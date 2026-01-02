import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from wtf_app_simple import app, db, Student, School, ExamSession, ExamTemplate, ExamRegistration
from datetime import datetime

def import_ocr_data():
    df = pd.read_excel('/opt/Way To Future考试管理系统/Student_grade_system/基础数据/registration_data_ocr.xlsx', engine='openpyxl')
    
    with app.app_context():
        # Cache sessions
        sessions = ExamSession.query.all()
        session_map = {} # Key: (date_str, time_str) -> session_obj
        for s in sessions:
            # s.exam_date is Date object, s.session_type/start_time/end_time
            # Session Name format: "橡心国际Way To Future 2025-2026学年S22026-01-04 上午场"
            # We can parse date/time from name or use attributes if reliable
            # Use name for matching as per previous logic
            if '上午场' in s.name:
                time_key = '上午场'
            elif '下午场' in s.name:
                time_key = '下午场'
            else:
                continue
            
            # Extract date from name or use exam_date
            date_str = str(s.exam_date)
            session_map[(date_str, time_key)] = s
            
        print(f"Loaded {len(session_map)} sessions.")

        for index, row in df.iterrows():
            name = row['姓名']
            if pd.isna(name): continue
            
            school_name = row['学校']
            grade = str(row['年级']).replace('G', '').strip()
            
            # Find or Create School
            school = School.query.filter_by(name=school_name).first()
            if not school and not pd.isna(school_name):
                school = School(name=school_name, code=school_name[:3].upper()) # Simple code
                db.session.add(school)
                db.session.commit()
            
            # Find or Create Student
            student = Student.query.filter_by(name=name, grade_level=grade).first()
            if not student:
                # Create new student
                import random
                student_id = f"S{datetime.now().strftime('%Y%m')}{random.randint(1000,9999)}"
                student = Student(
                    name=name,
                    student_id=student_id,
                    gender='Unknown', # Default
                    grade_level=grade,
                    school_id=school.id if school else None
                )
                db.session.add(student)
                db.session.commit()
                print(f"Created Student: {name}")
            
            # Determine Session
            date_val = row['日期'] # Timestamp or str
            if isinstance(date_val, pd.Timestamp):
                date_str = date_val.strftime('%Y-%m-%d')
            else:
                date_str = str(date_val)
                
            time_str = row['时间'] # '上午场'
            
            session = session_map.get((date_str, time_str))
            if not session:
                print(f"Warning: No session found for {date_str} {time_str}")
                continue
                
            # Map Checks to Templates
            templates_to_add = []
            
            def find_template(pattern):
                # pattern e.g. "G4中数"
                # Need to match strictly or loosely?
                # Template names are like "G4中数" exactly.
                return ExamTemplate.query.filter_by(name=pattern, exam_session_id=session.id).first()

            # 1. Math New (数学新课标)
            if row.get('数学新课标') == 1:
                t = find_template(f"G{grade}中数")
                if t: templates_to_add.append(t)
                
            # 2. Chinese New (语文新课标)
            if row.get('语文新课标') == 1:
                t = find_template(f"G{grade}语文")
                if t: templates_to_add.append(t)
                
            # 3. English New (英语新课标)
            if row.get('英语新课标') == 1:
                t_name = None
                if grade == '4': t_name = "G4牛津英语"
                elif grade == '6': t_name = "G6先锋英语"
                
                if t_name:
                    t = find_template(t_name)
                    if t: templates_to_add.append(t)
                else:
                    print(f"Warning: No English New template for Grade {grade}")

            # 4. Longman (朗文英语)
            if row.get('朗文英语') == 1:
                t = find_template(f"G{grade}朗文英语")
                if t: templates_to_add.append(t)
                
            # 5. Int Math (国际数学)
            if row.get('国际数学') == 1:
                t = find_template(f"G{grade}英数")
                if t: templates_to_add.append(t)
                
            # 6. MAP
            if row.get('Map测评') == 1:
                t1 = find_template("MAP-Math")
                t2 = find_template("MAP-English")
                if t1: templates_to_add.append(t1)
                if t2: templates_to_add.append(t2)
                
            # Register
            for t in templates_to_add:
                exists = ExamRegistration.query.filter_by(
                    student_id=student.id,
                    exam_session_id=session.id,
                    exam_template_id=t.id
                ).first()
                
                if not exists:
                    reg = ExamRegistration(
                        student_id=student.id,
                        exam_session_id=session.id,
                        exam_template_id=t.id
                    )
                    db.session.add(reg)
                    print(f"Registered {name} for {t.name}")
                    
            db.session.commit()
            
if __name__ == '__main__':
    import_ocr_data()
