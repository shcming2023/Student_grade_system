import pandas as pd
import os
from datetime import datetime
from wtf_app_simple import app, db, Student, ExamSession, ExamTemplate, ExamRegistration

def import_students_and_register():
    file_path = '/opt/Way To Future考试管理系统/Student_grade_system/基础数据/students_sample.xlsx'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Reading {file_path}...")
    df = pd.read_excel(file_path, engine='openpyxl')
    
    # Get active session
    session_name = "橡心国际Way To Future 2025-2026学年S2"
    exam_session = ExamSession.query.filter_by(name=session_name).first()
    if not exam_session:
        print(f"Session {session_name} not found!")
        return

    count_new = 0
    count_reg = 0
    
    for index, row in df.iterrows():
        name = row.get('姓名')
        grade = row.get('年级')
        classroom = row.get('班级')
        student_id_code = str(row.get('学号'))
        
        if pd.isna(name) or pd.isna(grade):
            continue
            
        # 1. Create/Update Student
        student = Student.query.filter_by(student_id=student_id_code).first()
        if not student:
            student = Student(
                name=name,
                grade_level=grade,
                class_name=classroom,
                student_id=student_id_code,
                gender='Unknown', # Default
                school_id=1 # Default to first school
            )
            db.session.add(student)
            db.session.flush() # Get ID
            count_new += 1
            print(f"Created student: {name} ({grade})")
        else:
            student.grade_level = grade
            student.class_name = classroom
            # db.session.add(student) # Update
        
        # 2. Register for Exams
        # Find all templates for this grade in this session
        # Logic: Template grade_level matches student grade OR 'Mixed' (e.g. AMC8)
        # Actually AMC8/Kangaroo might be for specific grades or all.
        # My import logic set grade_level for subject exams to Gx.
        # For Mixed/Competition exams, I might need custom logic.
        
        templates = ExamTemplate.query.filter_by(exam_session_id=exam_session.id).all()
        
        for template in templates:
            should_register = False
            
            # Match Grade
            if template.grade_level == grade:
                should_register = True
            elif template.grade_level == 'Mixed':
                # Register all? Or specific?
                # For now, let's register all Mixed exams to G3-G6?
                # User said "All students must correspond to exams".
                # Let's assume Mixed exams are open to all for now.
                should_register = True
            
            if should_register:
                # Check if already registered
                reg = ExamRegistration.query.filter_by(
                    student_id=student.id,
                    exam_template_id=template.id
                ).first()
                
                if not reg:
                    reg = ExamRegistration(
                        student_id=student.id,
                        exam_session_id=exam_session.id,
                        exam_template_id=template.id,
                        attendance_status='pending'
                    )
                    db.session.add(reg)
                    count_reg += 1
                    # print(f"  Registered {name} for {template.name}")
    
    db.session.commit()
    print(f"Import Complete.")
    print(f"New Students: {count_new}")
    print(f"New Registrations: {count_reg}")

if __name__ == '__main__':
    with app.app_context():
        import_students_and_register()
