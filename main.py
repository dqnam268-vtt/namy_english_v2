import os  # Thêm thư viện hệ thống
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import bcrypt

import models
import schemas
from database import engine, get_db

# ==========================================
# KHẮC PHỤC TRIỆT ĐỂ LỖI SẬP SERVER TRÊN RENDER
# Đảm bảo các thư mục giao diện luôn tồn tại trước khi FastAPI khởi chạy
# ==========================================
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

# Tự động tạo các bảng trong Database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NamY English App V2")

# ==========================================
# CẤU HÌNH GIAO DIỆN (Tất cả trong một)
# ==========================================
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

# ==========================================
# CÁC ROUTE TRẢ VỀ TRANG WEB (HTML)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/student", response_class=HTMLResponse)
async def student_page(request: Request):
    return templates.TemplateResponse("student.html", {"request": request})


# ==========================================
# CÁC ROUTE XỬ LÝ LOGIC NGẦM (API)
# ==========================================
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

@app.post("/api/login", response_model=schemas.LoginResponse)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tên đăng nhập hoặc mật khẩu không chính xác")
    return {"status": "success", "message": "Đăng nhập thành công", "user_id": user.id, "role": user.role, "username": user.username}

@app.post("/api/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Tên đăng nhập này đã tồn tại. Vui lòng chọn tên khác!")
    
    hashed_password = hash_password(user.password)
    new_user = models.User(username=user.username, password_hash=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    return {"status": "success", "message": f"Đã tạo tài khoản '{user.username}' thành công!"}

@app.get("/api/get_syllabus")
def get_syllabus(db: Session = Depends(get_db)):
    weeks = db.query(models.Week).order_by(models.Week.order_num).all()
    result = []
    for week in weeks:
        week_data = {"week_id": week.id, "title": week.title, "exercises": []}
        for exc in week.exercises:
            activity_names = [act.activity_type for act in exc.activities]
            week_data["exercises"].append({"id": exc.id, "title": exc.title, "activities": activity_names})
        result.append(week_data)
    return result

@app.post("/api/send_feedback")
def receive_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    new_feedback = models.Feedback(user_id=feedback.user_id, message=f"[{feedback.location}] {feedback.message}")
    db.add(new_feedback)
    db.commit()
    return {"status": "success", "message": "Đã lưu phản hồi vào Database"}

@app.post("/api/seed_data")
def seed_data(db: Session = Depends(get_db)):
    if db.query(models.Week).first():
        return {"message": "Dữ liệu đã tồn tại, không cần tạo lại!"}
    
    hashed_pw = hash_password("123456")
    admin = models.User(username="admin", password_hash=hashed_pw, role="admin")
    student = models.User(username="namy_student", password_hash=hashed_pw, role="student")
    db.add_all([admin, student])
    db.commit()

    w1 = models.Week(title="WEEK 1", order_num=1)
    db.add(w1)
    db.commit()

    e1 = models.Exercise(title="EXERCISE 1", week_id=w1.id, order_num=1)
    db.add(e1)
    db.commit()

    a1 = models.Activity(exercise_id=e1.id, activity_type="Video watching", content={"url": "video.mp4"}, order_num=1)
    a2 = models.Activity(exercise_id=e1.id, activity_type="Answering questions", content={"q1": "What is..."}, order_num=2)
    a3 = models.Activity(exercise_id=e1.id, activity_type="Matching meaning test", content={"pairs": []}, order_num=3)
    db.add_all([a1, a2, a3])
    db.commit()
    
    return {"message": "Đã bơm dữ liệu mẫu (Kèm TK admin và student) vào Database thành công!"}