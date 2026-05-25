from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import bcrypt  # Sử dụng trực tiếp bộ thư viện bcrypt chính chủ

import models
import schemas
from database import engine, get_db

# Tự động tạo các bảng trong Database dựa trên file models.py nếu chưa tồn tại
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NamY English App V2")

# ==========================================
# CẤU HÌNH GIAO DIỆN (Tất cả trong một)
# ==========================================
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

# ==========================================
# CÁ C ROUTE TRẢ VỀ TRANG WEB (HTML)
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

# --- BỘ MÃ HÓA MẬT KHẨU BCRYPT CHÍNH CHỦ MỚI ---
def hash_password(password: str) -> str:
    """Hàm băm mật khẩu thô thành chuỗi bảo mật"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Hàm so sánh mật khẩu đăng nhập với mật khẩu trong DB"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


# 1. API Đăng nhập
@app.post("/api/login", response_model=schemas.LoginResponse)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác"
        )
        
    return {
        "status": "success",
        "message": "Đăng nhập thành công",
        "user_id": user.id,
        "role": user.role,
        "username": user.username
    }

# 2. API Tạo tài khoản mới
@app.post("/api/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Tên đăng nhập này đã tồn tại. Vui lòng chọn tên khác!"
        )
    
    # Mã hóa mật khẩu bằng hàm chính chủ mới
    hashed_password = hash_password(user.password)
    
    new_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    
    return {"status": "success", "message": f"Đã tạo tài khoản '{user.username}' thành công!"}

# 3. API Lấy danh sách bài học
@app.get("/api/get_syllabus")
def get_syllabus(db: Session = Depends(get_db)):
    weeks = db.query(models.Week).order_by(models.Week.order_num).all()
    
    result = []
    for week in weeks:
        week_data = {
            "week_id": week.id,
            "title": week.title,
            "exercises": []
        }
        for exc in week.exercises:
            activity_names = [act.activity_type for act in exc.activities]
            week_data["exercises"].append({
                "id": exc.id,
                "title": exc.title,
                "activities": activity_names
            })
        result.append(week_data)
        
    return result

# 4. API Nhận Feedback từ học sinh
@app.post("/api/send_feedback")
def receive_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    new_feedback = models.Feedback(
        user_id=feedback.user_id,
        message=f"[{feedback.location}] {feedback.message}"
    )
    db.add(new_feedback)
    db.commit()
    return {"status": "success", "message": "Đã lưu phản hồi vào Database"}

# 5. API Tạo Dữ Liệu Mẫu (Chạy 1 lần)
@app.post("/api/seed_data")
def seed_data(db: Session = Depends(get_db)):
    if db.query(models.Week).first():
        return {"message": "Dữ liệu đã tồn tại, không cần tạo lại!"}
    
    # Mã hóa bằng hàm brypt mới
    hashed_pw = hash_password("123456")
    
    # Tạo 2 tài khoản mẫu phân quyền V2
    admin = models.User(username="admin", password_hash=hashed_pw, role="admin")
    student = models.User(username="namy_student", password_hash=hashed_pw, role="student")
    db.add_all([admin, student])
    db.commit()

    # Tạo Tuần 1
    w1 = models.Week(title="WEEK 1", order_num=1)
    db.add(w1)
    db.commit()

    # Tạo Bài tập 1 cho Tuần 1
    e1 = models.Exercise(title="EXERCISE 1", week_id=w1.id, order_num=1)
    db.add(e1)
    db.commit()

    # Tạo 3 Hoạt động mẫu
    a1 = models.Activity(exercise_id=e1.id, activity_type="Video watching", content={"url": "video.mp4"}, order_num=1)
    a2 = models.Activity(exercise_id=e1.id, activity_type="Answering questions", content={"q1": "What is..."}, order_num=2)
    a3 = models.Activity(exercise_id=e1.id, activity_type="Matching meaning test", content={"pairs": []}, order_num=3)
    
    db.add_all([a1, a2, a3])
    db.commit()
    
    return {"message": "Đã bơm dữ liệu mẫu (Kèm TK admin và student) vào Database thành công!"}