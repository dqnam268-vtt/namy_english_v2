from pydantic import BaseModel
from typing import Dict, Any

class UserLogin(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    status: str
    message: str
    user_id: int
    role: str
    username: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "student"

class FeedbackCreate(BaseModel):
    message: str
    location: str
    user_id: int

class WeekCreate(BaseModel):
    title: str
    order_num: int

class ExerciseCreate(BaseModel):
    title: str
    week_id: int
    order_num: int

class ActivityCreate(BaseModel):
    exercise_id: int
    activity_type: str
    content: Dict[str, Any]
    order_num: int