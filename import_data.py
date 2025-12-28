
import pandas as pd
import os
from datetime import date
from wtf_app_simple import app, db, School, Student, ExamSession, Subject, ExamTemplate, Question, User
import sqlite3

from sqlalchemy import inspect

def migrate_db():
    """Add exam_template_id column to questions table if not exists"""
    with app.app_context():
        # Check if column exists
        inspector = inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('questions')]
        if 'exam_template_id' not in columns:
            print("Migrating database: Adding exam_template_id to questions table...")
            with db.engine.connect() as conn:
                conn.execute('ALTER TABLE questions ADD COLUMN exam_template_id INTEGER REFERENCES exam_templates(id)')
            print("Migration complete.")
        else:
            print("Database already migrated.")

def ensure_subjects():
    """Ensure all required subjects exist"""
    subjects_data = [
        {'name': '朗文英语', 'code': 'LANGFORD', 'type': 'langford', 'total_score': 100},
        {'name': '牛津英语', 'code': 'OXFORD', 'type': 'oxford', 'total_score': 100},
        {'name': '先锋英语', 'code': 'PIONEER', 'type': 'pioneer', 'total_score': 100},
        {'name': '中文数学', 'code': 'CHINESE_MATH', 'type': 'chinese_math', 'total_score': 100},
        {'name': '英语数学', 'code': 'ENGLISH_MATH', 'type': 'english_math', 'total_score': 100},
        {'name': '语文', 'code': 'CHINESE', 'type': 'chinese', 'total_score': 100},
        {'name': 'AMC数学', 'code': 'AMC', 'type': 'amc', 'total_score': 25},
        {'name': '袋鼠数学', 'code': 'KANGAROO', 'type': 'kangaroo', 'total_score': 150},
        {'name': '小托福', 'code': 'TOEFL_JUNIOR', 'type': 'toefl_junior', 'total_score': 900},
    ]
    
    for s_data in subjects_data:
        subject = Subject.query.filter_by(code=s_data['code']).first()
        if not subject:
            print(f"Creating subject: {s_data['name']}")
            new_subject = Subject(**s_data)
            db.session.add(new_subject)
    db.session.commit()

def import_data():
    base_dir = '/opt/Way To Future考试管理系统/Student_grade_system/基础数据'
    files = [
        '2025秋季第一学期WTF考卷登记表4.0.xlsx',
        'WTF学术测评考卷登记表.xlsx'
    ]
    
    # 1. Create Exam Session
    session_name = "橡心国际Way To Future 2025-2026学年S2"
    exam_session = ExamSession.query.filter_by(name=session_name).first()
    if not exam_session:
        print(f"Creating Exam Session: {session_name}")
        exam_session = ExamSession(
            name=session_name,
            exam_date=date(2026, 1, 15), # Future date
            session_type='morning',
            start_time='09:00',
            end_time='11:00',
            status='draft',
            location='橡心国际校区'
        )
        db.session.add(exam_session)
        db.session.commit()
    else:
        print(f"Exam Session exists: {session_name}")

    # Subject Mapping
    subject_map = {
        '朗文英语': 'LANGFORD',
        '牛津英语': 'OXFORD',
        '先锋英语': 'PIONEER',
        '中数': 'CHINESE_MATH',
        '英数': 'ENGLISH_MATH',
        '语文': 'CHINESE',
        'AMC8': 'AMC',
        '袋鼠数学': 'KANGAROO',
        '小托福': 'TOEFL_JUNIOR'
    }

    # 2. Process Files
    for filename in files:
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
            
        print(f"Processing {filename}...")
        try:
            xls = pd.ExcelFile(filepath, engine='openpyxl')
            for sheet_name in xls.sheet_names:
                print(f"  Processing sheet: {sheet_name}")
                
                # Determine Grade and Subject from sheet name (e.g., "G1语文", "AMC8")
                grade = 'Mixed'
                subject_code = None
                
                # Simple heuristic for Subject and Grade
                if '语文' in sheet_name:
                    subject_code = 'CHINESE'
                    if 'G' in sheet_name:
                         grade = sheet_name.split('语文')[0] # e.g., G1
                elif 'AMC' in sheet_name:
                    subject_code = 'AMC'
                elif '袋鼠' in sheet_name:
                    subject_code = 'KANGAROO'
                elif '托福' in sheet_name:
                    subject_code = 'TOEFL_JUNIOR'
                elif '英数' in sheet_name:
                    subject_code = 'ENGLISH_MATH'
                elif '中数' in sheet_name:
                    subject_code = 'CHINESE_MATH'
                elif '朗文' in sheet_name:
                    subject_code = 'LANGFORD'
                elif '牛津' in sheet_name:
                    subject_code = 'OXFORD'
                elif '先锋' in sheet_name:
                    subject_code = 'PIONEER'
                
                # Default to parsing subject if not found in specific logic
                if not subject_code:
                     # Try to match with subject_map keys
                     for k, v in subject_map.items():
                         if k in sheet_name:
                             subject_code = v
                             break
                
                if not subject_code:
                    print(f"    Skipping sheet {sheet_name}: Unknown subject")
                    continue
                    
                subject = Subject.query.filter_by(code=subject_code).first()
                if not subject:
                    print(f"    Skipping sheet {sheet_name}: Subject {subject_code} not found in DB")
                    continue

                # Read data - Try header=1 first (assuming title row)
                df = pd.read_excel(filepath, sheet_name=sheet_name, header=1, engine='openpyxl')
                
                # Clean columns
                df.columns = df.columns.str.strip()
                print(f"    Columns found: {df.columns.tolist()}")

                # Verify columns - if '题号' not in columns, try header=0
                if '题号' not in df.columns:
                     df = pd.read_excel(filepath, sheet_name=sheet_name, header=0, engine='openpyxl')
                     df.columns = df.columns.str.strip()
                
                if '题号' not in df.columns:
                    print(f"    Skipping sheet {sheet_name}: Could not find '题号' column")
                    continue

                # Create or Update Exam Template
                # Naming convention: Session Name - Sheet Name (Subject)
                template_name = f"{session_name} - {sheet_name}"
                template = ExamTemplate.query.filter_by(name=template_name).first()
                if not template:
                    template = ExamTemplate(
                        name=template_name,
                        subject_id=subject.id,
                        exam_session_id=exam_session.id,
                        grade_level=grade,
                        total_questions=len(df)
                    )
                    db.session.add(template)
                    db.session.flush() # Get ID
                    print(f"    Created Template: {template_name}")
                else:
                    template.exam_session_id = exam_session.id # Ensure session link
                    template.total_questions = len(df)
                    print(f"    Updated Template: {template_name}")

                # Clear existing questions for this template to avoid duplicates/conflicts
                Question.query.filter_by(exam_template_id=template.id).delete()

                # Import Questions
                for idx, row in df.iterrows():
                    try:
                        # Convert row to dict to safely use get
                        row_data = row.to_dict()
                        
                        q_num = str(row_data.get('题号', idx+1))
                        
                        module = row_data.get('模块', '')
                        kp = row_data.get('知识点', '') or row_data.get('核心知识点/技能', '')
                        score_val = row_data.get('分值', 1)
                        try:
                            score_val = float(score_val)
                        except:
                            score_val = 1.0
                            
                        q = Question(
                            exam_template_id=template.id,
                            question_number=q_num,
                            subject_id=subject.id,
                            score=float(score_val),
                            module=str(module),
                            knowledge_point=str(kp)
                        )
                        db.session.add(q)
                    except Exception as e:
                        print(f"      Error row {idx}: {e}")
                
                db.session.commit()
                print(f"    Imported {len(df)} questions for {sheet_name}")

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    with app.app_context():
        migrate_db()
        ensure_subjects()
        import_data()
