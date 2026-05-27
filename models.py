from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student")
    
    progresses = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

class Week(Base):
    __tablename__ = "weeks"
    
    week_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    order_num = Column(Integer, nullable=False)
    
    exercises = relationship("Exercise", back_populates="week", cascade="all, delete-orphan")

class Exercise(Base):
    __tablename__ = "exercises"
    
    exercise_id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("weeks.week_id"))
    title = Column(String(100), nullable=False)
    order_num = Column(Integer, nullable=False)
    
    week = relationship("Week", back_populates="exercises")
    activities = relationship("Activity", back_populates="exercise", cascade="all, delete-orphan")

class Activity(Base):
    __tablename__ = "activities"
    
    activity_id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.exercise_id"))
    activity_type = Column(String(50), nullable=False) 
    content = Column(JSON, nullable=False) 
    order_num = Column(Integer, nullable=False)
    
    exercise = relationship("Exercise", back_populates="activities")
    progresses = relationship("Progress", back_populates="activity")

class Progress(Base):
    __tablename__ = "progress"
    
    progress_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    activity_id = Column(Integer, ForeignKey("activities.activity_id"))
    score = Column(Integer, default=0) 
    is_completed = Column(Boolean, default=False) 
    
    user = relationship("User", back_populates="progresses")
    activity = relationship("Activity", back_populates="progresses")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    feedback_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    message = Column(Text, nullable=False)
    location = Column(String(100)) 
    
    user = relationship("User", back_populates="feedbacks")