from pydantic import BaseModel

# ==========================================
# 1. DỮ LIỆU ĐĂNG NHẬP
# ==========================================
# Dữ liệu người dùng gửi lên khi gõ vào form đăng nhập
class UserLogin(BaseModel):
    username: str
    password: str

# Dữ liệu hệ thống trả về sau khi đăng nhập thành công
class LoginResponse(BaseModel):
    status: str
    message: str
    user_id: int
    role: str
    username: str

# ==========================================
# 2. DỮ LIỆU TẠO TÀI KHOẢN (DÀNH CHO ADMIN)
# ==========================================
# Dữ liệu khi thầy điền form cấp tài khoản cho học sinh
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "student"  # Mặc định tài khoản tạo ra là học sinh (student)

# ==========================================
# 3. DỮ LIỆU HỘP THƯ (FEEDBACK)
# ==========================================
# Dữ liệu nhận form tin nhắn thắc mắc từ học sinh
class FeedbackCreate(BaseModel):
    message: str
    location: str
    user_id: int