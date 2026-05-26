import json
import models
from database import SessionLocal

def import_lesson_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    db = SessionLocal()
    for w_data in data['weeks']:
        # Tạo tuần
        week = models.Week(title=w_data['title'], order_num=w_data['order_num'])
        db.add(week)
        db.flush() # Lấy ID của tuần vừa tạo
        
        # Tạo bài tập
        for ex_data in w_data['exercises']:
            ex = models.Exercise(title=ex_data['title'], week_id=week.week_id, order_num=1)
            db.add(ex)
            db.flush()
            
            # Tạo hoạt động
            for act in ex_data['activities']:
                activity = models.Activity(
                    exercise_id=ex.exercise_id,
                    activity_type=act['type'],
                    content=act['content'],
                    order_num=act['order_num']
                )
                db.add(activity)
                
    db.commit()
    db.close()
    print("✅ Đã nạp thành công Week 1 và Week 2 vào Database!")

if __name__ == "__main__":
    import_lesson_data('data_lesson.json')