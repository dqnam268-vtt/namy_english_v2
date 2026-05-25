import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Lấy chuỗi kết nối từ biến môi trường (Environment Variable) nếu có
# Ở phiên bản V2, nếu không có mạng, hệ thống tự động tạo file namy_v2.db tại máy tính
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./namy_v2.db"
)

# Xử lý lỗi tương thích chuỗi kết nối của SQLAlchemy đối với một số cloud hosting
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 2. Khởi tạo Engine tương ứng với loại Cơ sở dữ liệu
if DATABASE_URL.startswith("sqlite"):
    # Cấu hình riêng cho SQLite (Chạy dưới local máy cá nhân)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Cấu hình tối ưu cho PostgreSQL Cloud (Khi đưa lên Render/Supabase)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()