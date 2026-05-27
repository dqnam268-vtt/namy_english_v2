import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import bcrypt

import models
import schemas
from database import engine, get_db

os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

try:
    models.Base.metadata.create_all(bind=engine)
    print("🚀 TÌNH TRẠNG: KẾT NỐI DATABASE THÀNH CÔNG!")
except Exception as e:
    print(f"❌ LỖI DATABASE: {e}")

app = FastAPI(title="NamY English App V2")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home_page():
    return FileResponse("static/index.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    return FileResponse("static/admin.html")

@app.get("/student", response_class=HTMLResponse)
async def student_page():
    return FileResponse("static/student.html")

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tài khoản hoặc mật khẩu không đúng")
    return {"status": "success", "message": "Thành công", "user_id": user.user_id, "role": user.role, "username": user.username}

@app.post("/api/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại!")
    new_user = models.User(username=user.username, password_hash=hash_password(user.password), role=user.role)
    db.add(new_user)
    db.commit()
    return {"status": "success", "message": "Đã tạo tài khoản"}

@app.get("/api/get_syllabus")
def get_syllabus(db: Session = Depends(get_db)):
    weeks = db.query(models.Week).order_by(models.Week.order_num).all()
    result = []
    for week in weeks:
        week_data = {"week_id": week.week_id, "title": week.title, "order_num": week.order_num, "exercises": []}
        for exc in week.exercises:
            act_list = [{"id": a.activity_id, "type": a.activity_type, "content": a.content} for a in exc.activities]
            week_data["exercises"].append({"id": exc.exercise_id, "title": exc.title, "activities": act_list})
        result.append(week_data)
    return result

@app.post("/api/send_feedback")
def receive_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    new_feedback = models.Feedback(user_id=feedback.user_id, message=f"[{feedback.location}] {feedback.message}")
    db.add(new_feedback)
    db.commit()
    return {"status": "success"}

@app.post("/api/add_week")
def add_week(week: schemas.WeekCreate, db: Session = Depends(get_db)):
    new_week = models.Week(title=week.title, order_num=week.order_num)
    db.add(new_week)
    db.commit()
    return {"status": "success", "message": f"Đã thêm tuần: {week.title}"}

@app.post("/api/add_exercise")
def add_exercise(exe: schemas.ExerciseCreate, db: Session = Depends(get_db)):
    new_exe = models.Exercise(title=exe.title, week_id=exe.week_id, order_num=exe.order_num)
    db.add(new_exe)
    db.commit()
    return {"status": "success", "message": f"Đã thêm bài tập: {exe.title}"}

@app.post("/api/add_activity")
def add_activity(act: schemas.ActivityCreate, db: Session = Depends(get_db)):
    new_act = models.Activity(exercise_id=act.exercise_id, activity_type=act.activity_type, content=act.content, order_num=act.order_num)
    db.add(new_act)
    db.commit()
    return {"status": "success", "message": "Đã thêm hoạt động thành công"}

@app.get("/api/get_feedbacks")
def get_feedbacks(db: Session = Depends(get_db)):
    feedbacks = db.query(models.Feedback, models.User.username).join(models.User, models.Feedback.user_id == models.User.user_id).all()
    return [{"id": fb.feedback_id, "username": uname, "message": fb.message, "location": fb.location} for fb, uname in feedbacks]

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_students": db.query(models.User).filter(models.User.role == "student").count(),
        "total_weeks": db.query(models.Week).count(),
        "total_feedbacks": db.query(models.Feedback).count()
    }

@app.get("/api/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.role == "student").all()
    result = []
    for u in users:
        done_count = db.query(models.Progress).filter(models.Progress.user_id == u.user_id, models.Progress.is_completed == True).count()
        result.append({"id": u.user_id, "username": u.username, "role": u.role, "done_count": done_count})
    return result

@app.post("/api/register_bulk")
def register_bulk(users_data: List[schemas.UserCreate], db: Session = Depends(get_db)):
    created = 0
    for user in users_data:
        if not db.query(models.User).filter(models.User.username == user.username).first():
            db.add(models.User(username=user.username, password_hash=hash_password(user.password), role="student"))
            created += 1
    db.commit()
    return {"status": "success", "message": f"Đã tạo nhanh {created} tài khoản."}

@app.post("/api/seed_data")
def seed_data(db: Session = Depends(get_db)):
    if db.query(models.Week).first():
        return {"message": "Dữ liệu mẫu đã có sẵn từ trước"}
    pw = hash_password("123456")
    db.add_all([models.User(username="admin", password_hash=pw, role="admin"), models.User(username="namy_student", password_hash=pw, role="student")])
    db.commit()
    w1 = models.Week(title="WEEK 1: INTRODUCTION & PHONETICS", order_num=1)
    db.add(w1); db.commit()
    e1 = models.Exercise(title="Exercise 1: Vowel Pronunciation Analysing", week_id=w1.week_id, order_num=1)
    db.add(e1); db.commit()
    db.add_all([
        models.Activity(exercise_id=e1.exercise_id, activity_type="Học Từ Vựng (Vocabulary)", content={"word": "Phonetics", "meaning": "Acoustic formants"}, order_num=1),
        models.Activity(exercise_id=e1.exercise_id, activity_type="Phat Âm & Nghe (Phonetics)", content={"url": "praat_analysis.mp4"}, order_num=2)
    ])
    db.commit()
    return {"message": "Đã tạo dữ liệu cấu trúc tuần mẫu thành công!"}