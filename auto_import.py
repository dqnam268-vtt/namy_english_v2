import csv
import models
from database import SessionLocal

def run_auto_import(csv_file_path):
    db = SessionLocal()
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                week_num = int(row['Week_Num'].strip())
                week_title = row['Week_Title'].strip()
                exe_title = row['Exe_Title'].strip()
                act_type_raw = row['Act_Type'].strip()
                
                # 1. Tự động tìm hoặc tạo Tuần (Không bao giờ tạo trùng)
                week = db.query(models.Week).filter_by(order_num=week_num).first()
                if not week:
                    week = models.Week(title=week_title, order_num=week_num)
                    db.add(week)
                    db.commit()

                # 2. Tự động tìm hoặc tạo Bài tập
                exe = db.query(models.Exercise).filter_by(title=exe_title, week_id=week.week_id).first()
                if not exe:
                    exe = models.Exercise(title=exe_title, week_id=week.week_id, order_num=1)
                    db.add(exe)
                    db.commit()

                # 3. Đóng gói Hoạt động thông minh
                content = {}
                display_type = ""
                
                if act_type_raw == 'vocab':
                    display_type = "Học Từ Vựng (Vocabulary)"
                    content = {"word": row['Question_Word'], "meaning": row['Options_Meaning']}
                
                elif act_type_raw == 'quiz':
                    display_type = "Luyện Ngữ Pháp (Grammar)"
                    options_list = [opt.strip() for opt in row['Options_Meaning'].split(',')]
                    content = {
                        "question": row['Question_Word'],
                        "options": options_list,
                        "answer": row['Answer'].strip()
                    }
                    
                elif act_type_raw == 'video':
                    display_type = "Phát Âm & Nghe (Phonetics)"
                    content = {"url": row['Question_Word']}

                # Đưa vào Database
                act = models.Activity(exercise_id=exe.exercise_id, activity_type=display_type, content=content, order_num=1)
                db.add(act)
                
        db.commit()
        print("🚀 QUÁ TUYỆT VỜI! Đã nạp thành công toàn bộ khóa học từ file CSV!")
        
    except Exception as e:
        print(f"❌ Lỗi nạp dữ liệu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Đặt file course_data.csv vào cùng thư mục và chạy file này
    run_auto_import("course_data.csv")