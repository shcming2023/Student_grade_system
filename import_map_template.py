import sys
import os
import pandas as pd
from datetime import datetime

# Add application path
sys.path.append('/opt/Way To Future考试管理系统/Student_grade_system')
from wtf_app_simple import app, db, ExamTemplate, Question, Subject

def import_map_templates():
    excel_path = '/opt/Way To Future考试管理系统/Student_grade_system/基础数据/MAP登记表.xlsx'
    if not os.path.exists(excel_path):
        print(f"Error: File not found at {excel_path}")
        return

    print(f"Reading Excel: {excel_path}")
    try:
        xl = pd.ExcelFile(excel_path, engine='openpyxl')
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    # Sheets
    sheets = xl.sheet_names
    print(f"Found sheets: {sheets}")

    # Target Templates (MAP Assessment)
    # IDs identified: 113, 114, 124
    target_template_ids = [113, 114, 124]
    
    with app.app_context():
        # Verify templates exist
        templates = ExamTemplate.query.filter(ExamTemplate.id.in_(target_template_ids)).all()
        if not templates:
            print("No target templates found!")
            return
            
        print(f"Found {len(templates)} templates to update: {[t.id for t in templates]}")
        
        # Get 'Map测评' Subject
        map_subject = Subject.query.filter(Subject.name.like('%Map%')).first()
        if not map_subject:
            print("Warning: 'Map测评' subject not found. Using ID 10 default or creating.")
            map_subject = Subject.query.get(10)
            if not map_subject:
                 # Create if missing (unlikely based on previous check)
                 map_subject = Subject(name='Map测评')
                 db.session.add(map_subject)
                 db.session.commit()
        
        subject_id = map_subject.id
        print(f"Using Subject ID: {subject_id} ({map_subject.name})")

        # Prepare Data from Excel
        # Expected structure: '模块' column
        
        questions_data = []
        
        # Process MAP-Math
        if 'MAP-Math' in sheets:
            df_math = xl.parse('MAP-Math', header=1)
            print(f"Processing MAP-Math: {len(df_math)} rows")
            print(f"Columns: {df_math.columns}")
            for idx, row in df_math.iterrows():
                module_name = str(row.get('模块', '')).strip()
                if not module_name or module_name == 'nan':
                    continue
                questions_data.append({
                    'module': module_name,
                    'q_num': f"M-{idx+1}",
                    'score': 300.0, # Max RIT
                    'type': 'Math'
                })
        else:
            print("Warning: MAP-Math sheet not found")

        # Process MAP-English
        if 'MAP-English' in sheets:
            df_eng = xl.parse('MAP-English', header=1)
            print(f"Processing MAP-English: {len(df_eng)} rows")
            print(f"Columns: {df_eng.columns}")
            for idx, row in df_eng.iterrows():
                module_name = str(row.get('模块', '')).strip()
                if not module_name or module_name == 'nan':
                    continue
                questions_data.append({
                    'module': module_name,
                    'q_num': f"E-{idx+1}",
                    'score': 300.0, # Max RIT
                    'type': 'English'
                })
        else:
            print("Warning: MAP-English sheet not found")

        print(f"Total questions extracted: {len(questions_data)}")

        # Update Templates
        for template in templates:
            print(f"Updating Template {template.id} ({template.name})...")
            
            # Delete existing questions
            deleted = Question.query.filter_by(exam_template_id=template.id).delete()
            print(f"  Deleted {deleted} existing questions.")
            
            # Insert new questions
            new_questions = []
            for q_data in questions_data:
                q = Question(
                    exam_template_id=template.id,
                    question_number=q_data['q_num'],
                    subject_id=subject_id,
                    module=q_data['module'],
                    score=q_data['score'],
                    knowledge_point=q_data['type'] # Storing Type in knowledge_point for reference
                )
                new_questions.append(q)
            
            db.session.add_all(new_questions)
            
            # Update Template Stats
            template.total_questions = len(new_questions)
            template.total_score = sum(q['score'] for q in questions_data)
            
            print(f"  Added {len(new_questions)} questions. Total Score: {template.total_score}")
        
        db.session.commit()
        print("Import completed successfully.")

if __name__ == "__main__":
    import_map_templates()
