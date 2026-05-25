from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext

import models
import schemas
from database import engine, get_db

# Tự động tạo các bảng trong Database dựa trên file models.py nếu chưa tồn tại
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NamY English App V2")

# ==========================================
# CẤU HÌNH GIAO DIỆN (Tất cả trong một)
# ==========================================
# 1. Gắn thư mục static để FastAPI đọc được file CSS, JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Gắn thư mục chứa các trang giao diện HTML
templates = Jinja2Templates(directory="static")

# ==========================================
# CÁC ROUTE TRẢ VỀ TRANG WEB (HTML)
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Trang chủ (Cổng đăng nhập)"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Trang bảng điều khiển dành cho Thầy"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/student", response_class=HTMLResponse)
async def student_page(request: Request):
    """Trang tổng hợp công cụ học tập cho Học sinh"""
    return templates.TemplateResponse("student.html", {"request": request})


# ==========================================
# CÁC ROUTE XỬ LÝ LOGIC NGẦM (API)
# ==========================================

# Cấu hình mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

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
        "user_id": user.id, # Đã đồng bộ với V2
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
    
    hashed_password = pwd_context.hash(user.password)
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
            "week_id": week.id, # Đã đồng bộ với V2
            "title": week.title,
            "exercises": []
        }
        for exc in week.exercises:
            activity_names = [act.activity_type for act in exc.activities]
            week_data["exercises"].append({
                "id": exc.id, # Đã đồng bộ với V2
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
    
    hashed_pw = pwd_context.hash("123456")
    
    # TẠO 2 TÀI KHOẢN MẪU ĐỂ TEST PHÂN QUYỀN V2
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

    # Tạo 3 Hoạt động cho Bài tập 1
    a1 = models.Activity(exercise_id=e1.id, activity_type="Video watching", content={"url": "video.mp4"}, order_num=1)
    a2 = models.Activity(exercise_id=e1.id, activity_type="Answering questions", content={"q1": "What is..."}, order_num=2)
    a3 = models.Activity(exercise_id=e1.id, activity_type="Matching meaning test", content={"pairs": []}, order_num=3)
    
    db.add_all([a1, a2, a3])
    db.commit()
    
    return {"message": "Đã bơm dữ liệu mẫu (Kèm TK admin và student) vào Database thành công!"}