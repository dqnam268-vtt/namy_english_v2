from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ==========================================
# 1. BẢNG NGƯỜI DÙNG (Tài khoản Admin và Học sinh)
# ==========================================
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student") # Phân quyền: "admin" hoặc "student"
    
    # Mối quan hệ: 1 User có nhiều Tiến độ học và nhiều Tin nhắn phản hồi
    progresses = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

# ==========================================
# 2. BẢNG CẤU TRÚC BÀI HỌC
# ==========================================
class Week(Base):
    __tablename__ = "weeks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    order_num = Column(Integer, nullable=False)
    
    # Mối quan hệ: 1 Tuần có nhiều Bài tập
    exercises = relationship("Exercise", back_populates="week", cascade="all, delete-orphan")

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("weeks.id"))
    title = Column(String(100), nullable=False)
    order_num = Column(Integer, nullable=False)
    
    week = relationship("Week", back_populates="exercises")
    activities = relationship("Activity", back_populates="exercise", cascade="all, delete-orphan")

# ==========================================
# 3. BẢNG CÔNG CỤ HỌC TẬP (Vocab, Grammar, Reading...)
# ==========================================
class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    activity_type = Column(String(50), nullable=False) # VD: 'vocab', 'grammar', 'reading'
    
    # Dùng JSON chuẩn để tương thích hoàn hảo cả SQLite (Local) và Postgres (Cloud)
    content = Column(JSON, nullable=False) 
    order_num = Column(Integer, nullable=False)
    
    exercise = relationship("Exercise", back_populates="activities")
    progresses = relationship("Progress", back_populates="activity")

# ==========================================
# 4. BẢNG LƯU TRỮ DỮ LIỆU CỦA HỌC SINH
# ==========================================
class Progress(Base):
    """Bảng lưu điểm số để hiển thị lên Dashboard cho Thầy Nam"""
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_id = Column(Integer, ForeignKey("activities.id"))
    score = Column(Integer, default=0) # Điểm số đạt được
    is_completed = Column(Boolean, default=False) # Đánh dấu hoàn thành
    
    user = relationship("User", back_populates="progresses")
    activity = relationship("Activity", back_populates="progresses")

class Feedback(Base):
    """Bảng lưu tin nhắn thắc mắc của học sinh"""
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    location = Column(String(100)) # Ghi nhận học sinh thắc mắc ở bài nào
    
    user = relationship("User", back_populates="feedbacks")