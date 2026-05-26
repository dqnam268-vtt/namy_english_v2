import json
from database import SessionLocal
import models

def import_weeks(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    db = SessionLocal()
    for w_data in data['weeks']:
        # Kiểm tra xem tuần đã tồn tại chưa để tránh trùng lặp
        existing_week = db.query(models.Week).filter_by(title=w_data['title']).first()
        if not existing_week:
            new_week = models.Week(title=w_data['title'], order_num=w_data['order_num'])
            db.add(new_week)
            db.commit()
            print(f"✅ Đã tạo: {w_data['title']}")
        else:
            print(f"ℹ️ {w_data['title']} đã có sẵn.")
    db.close()

if __name__ == "__main__":
    import_weeks('data_lesson.json')