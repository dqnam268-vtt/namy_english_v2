from pydantic import BaseModel

# ==========================================
# 1. DỮ LIỆU ĐĂNG NHẬP
# ==========================================
class UserLogin(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    status: str
    message: str
    user_id: int
    role: str
    username: str

# ==========================================
# 2. DỮ LIỆU TẠO TÀI KHOẢN (DÀNH CHO ADMIN)
# ==========================================
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "student"  # Mặc định tài khoản tạo ra là học sinh (student)

# ==========================================
# 3. DỮ LIỆU HỘP THƯ (FEEDBACK)
# ==========================================
class FeedbackCreate(BaseModel):
    message: str
    location: str
    user_id: int

# ==========================================
# 4. DỮ LIỆU TẠO LỘ TRÌNH (DÀNH CHO ADMIN)
# ==========================================
# Đây chính là khuôn mẫu WeekCreate mà hệ thống đang tìm kiếm
class WeekCreate(BaseModel):
    title: str
    order_num: int