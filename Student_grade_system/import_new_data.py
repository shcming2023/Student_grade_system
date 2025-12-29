import sys
from wtf_app_simple import app, db, ExamTemplate, ExamRegistration, Student, ExamSession, Subject, School

# Define Sessions
SESSION_MAP = {
    '2026-01-04_AM': 3,
    '2026-01-04_PM': 4,
    '2026-01-11_AM': 1,
    '2026-01-11_PM': 2
}

# Define Data
# Format: [Name, Grade, School, [Subjects...]]
# Subjects: '数学', '语文', '英语新课标', '朗文', '国际数学', 'Map', '袋鼠', '小托福', 'AMC'

DATA = {
    '2026-01-04_AM': [
        ['黄昱珩', 'G4', '协和国际', ['语文', '国际数学', 'Map']],
        ['王姿文', 'G6', '协和国际', ['国际数学', 'Map']],
        ['徐泽涵', 'G2', '协和先锋', ['数学', '语文', '朗文']],
        ['乔哲宇', 'G4', '协和国际', ['语文', '朗文', 'Map']],
        ['陈韬宇', 'G6', '协和先锋', ['语文', '国际数学']],
        ['金时萱', 'G3', '协和国际', ['语文', '国际数学', 'Map']],
        ['李茗浩', 'G3', '协和国际', ['语文', '国际数学', 'Map']],
        ['魏睿希', 'G3', '协和先锋', ['数学', '语文', '朗文', '袋鼠']],
        ['汤舒博', 'G4', '协和国际', ['语文', '国际数学', 'Map']],
        ['詹谦屹', 'G4', '协和先锋', ['数学', '语文', '朗文']],
        ['武恒旭', 'G5', '协和先锋', ['数学', '语文', '朗文']],
        ['金晨宇', 'G5', '协和先锋', ['数学', '语文', '朗文']],
        ['胡律铭', 'G4', '协和先锋', ['数学', '语文', '朗文']],
        ['赵振贤', 'G3', '协和先锋', ['数学', '语文', '朗文']],
        ['严一宁', 'G3', '协和先锋', ['数学', '语文', '朗文']],
        ['蒋植阳', 'G2', '协和先锋', ['数学', '语文', '朗文']],
        ['何林泽', 'G4', '协和先锋', ['数学', '语文', '朗文']],
        ['化艺霖', 'G3', '协和先锋', ['数学', '语文', '朗文']],
        ['金诺一', 'G4', '协和国际', ['Map']],
        ['仲若溪', 'G1', '协和国际', ['语文', '国际数学', 'Map']],
    ],
    '2026-01-04_PM': [
        ['朱亚伦', 'G3', '协和国际', ['语文', '国际数学', 'Map']],
        ['陶申涛', 'G4', '协和国际', ['语文', '国际数学', 'Map']],
        ['张凌尚', 'G4', '协和先锋', ['数学', '语文', '朗文']],
        ['朱陈筱', 'G3', '协和国际', ['语文', '国际数学', 'Map']],
        ['侯敏恩', 'G5', '协和先锋', ['数学', '语文', '朗文']],
        ['顾情鸾', 'G4', '协和先锋', ['数学', '语文', '朗文']],
        ['舒仁洛', 'G3', '协和先锋', ['数学', '语文', '朗文']],
        ['陈星汝', 'G4', '协和先锋', ['数学', '语文', '朗文']],
        ['王雯仪', 'G3', '协和先锋', ['数学', '语文', '朗文']],
        ['国来', 'G2', '协和先锋', ['数学', '语文', '朗文']],
        ['袁彧珩', 'G3', '协和国际', ['语文', '国际数学', 'Map']],
        ['张清怡', 'G5', '徐汇东二小学', ['数学', '语文', '英语新课标']],
        ['赵可欣', 'G4', '协和国际', ['语文', '国际数学', 'Map']],
        ['金宇轩', 'G2', '万源协和', ['数学', '语文', '英语新课标']],
        ['李子墨', 'G3', '协和国际', ['语文', '国际数学', 'Map']],
        ['徐熙宸', 'G3', '协和国际', ['语文', '国际数学', 'Map']],
        ['卢艺晗', 'G6', '协和双语', ['数学', '语文', '朗文']],
        ['彭温珺', 'G2', '协和先锋', ['数学', '语文', '朗文']],
        ['蔡卓尔', 'G3', '协和国际', ['语文', '国际数学', 'Map']],
        ['林钧瀚', 'G2', '协和先锋', ['数学', '语文', '朗文', '袋鼠']],
    ],
    '2026-01-11_AM': [
        ['吴舒然', 'G1', '协和先锋', ['数学', '语文', '朗文']],
        ['孙悦雯', 'G5', '协和先锋', ['数学', '语文', '朗文']],
        ['山川', 'G4', '协和先锋', ['数学', '语文', '朗文']],
        ['顾家玮', 'G5', '燎原双语', ['数学', '语文', '英语新课标']],
    ],
    '2026-01-11_PM': [
        ['任禾', 'G2', '协和先锋', ['数学', '语文', '朗文']],
        ['程芸熙', 'G4', '协和先锋', ['数学', '语文', '朗文']],
        ['刘张屹', 'G2', '协和先锋', ['数学', '语文', '朗文', '小托福', 'AMC']],
        ['朴智耀', 'G2', '万科双语', ['数学', '语文']],
        ['金果馨', 'G4', '华东师范附属小学', ['数学', '语文', '英语新课标']],
        ['白沅亨', 'G1', '星河湾', ['语文', '国际数学', 'Map']],
    ]
}

def get_or_create_school(name):
    s = School.query.filter_by(name=name).first()
    if not s:
        s = School(name=name, code=f'SCH_{hash(name)%10000}')
        db.session.add(s)
        db.session.flush()
    return s

def get_or_create_student(name, grade, school_id):
    # Simple check by name (and school/grade if possible, but name is primary here)
    # To avoid duplicates, we first check by Name + School
    s = Student.query.filter_by(name=name, school_id=school_id).first()
    if not s:
        # Check by name only? Might be risky if same name. But assume unique for now.
        s = Student.query.filter_by(name=name).first()
    
    if not s:
        import time
        import random
        # Retry loop for ID generation
        for _ in range(5):
            sid = str(int(time.time()))[-6:] + str(random.randint(10,99))
            if not Student.query.filter_by(student_id=sid).first():
                break
        else:
             # Fallback if loop fails
             sid = str(int(time.time()))[-5:] + str(random.randint(100,999))
             
        s = Student(student_id=sid, name=name, gender='M', grade_level=grade, school_id=school_id)
        db.session.add(s)
        db.session.flush()
    else:
        # Update info
        s.grade_level = grade
        s.school_id = school_id
    return s

def get_or_create_template(session_id, grade, subject_key):
    # Mapping
    # '数学' -> 中数
    # '语文' -> 语文
    # '英语新课标' -> 英语新课标 (New Subject)
    # '朗文' -> 朗文英语
    # '国际数学' -> 英数
    # 'Map' -> Map测评
    # '袋鼠' -> 袋鼠数学
    # '小托福' -> 小托福
    # 'AMC' -> AMC数学
    
    subj_map = {
        '数学': '中数',
        '语文': '语文',
        '朗文': '朗文英语',
        '国际数学': '英数',
        'Map': 'Map测评',
        '袋鼠': '袋鼠数学',
        '小托福': '小托福',
        'AMC': 'AMC数学',
        '英语新课标': '英语新课标'
    }
    
    subj_name = subj_map.get(subject_key, subject_key)
    
    # Special Handling: Mixed Grades for some subjects
    target_grade = grade
    if subj_name in ['Map测评', '袋鼠数学', '小托福', 'AMC数学']:
        target_grade = 'Mixed'
        
    # Find Subject ID
    subject = Subject.query.filter_by(name=subj_name).first()
    if not subject:
        print(f"Creating Subject: {subj_name}")
        subject = Subject(name=subj_name, code=f'SUB_{hash(subj_name)%10000}', type='standard')
        db.session.add(subject)
        db.session.flush()
        
    # Find Template
    # Name pattern: "G{grade}{subj_name}" or just "{subj_name}" for Mixed
    if target_grade == 'Mixed':
        t_name = f"{subj_name}"
        # Fix: Map name might be "Map测评"
        if subj_name == '袋鼠数学' and grade in ['G1','G2']: # Assuming A/B levels? 
             # Just use generic "袋鼠数学" or "袋鼠数学A/B"?
             # DB has "袋鼠数学A", "袋鼠数学B". Let's try to match or create generic.
             # Let's create generic for now to match data.
             pass
    else:
        t_name = f"{target_grade}{subj_name}"
        
    # Try find by name and session
    t = ExamTemplate.query.filter_by(name=t_name, exam_session_id=session_id).first()
    
    # If not found, try finding by name only (maybe session not linked yet, but we want new ones)
    if not t:
        # Create new template for this session
        print(f"Creating Template: {t_name} for Session {session_id}")
        t = ExamTemplate(
            name=t_name,
            subject_id=subject.id,
            exam_session_id=session_id,
            grade_level=target_grade,
            total_questions=0
        )
        # Note: total_score might not be in model definition if removed earlier, or defaults to 100
        # Let's check model definition if needed. Assuming total_score is not in __init__ or was removed.
        # But wait, previous logs showed total_score in API.
        # Ah, the error says "total_score is an invalid keyword argument".
        # Maybe it was removed from the model but still in the table? Or I am mistaken.
        # Let's remove total_score from init.
        
        db.session.add(t)
        db.session.flush()
        
    return t

def main():
    with app.app_context():
        print("Clearing existing registrations...")
        db.session.query(ExamRegistration).delete()
        db.session.commit()
        
        count = 0
        for session_key, students in DATA.items():
            session_id = SESSION_MAP[session_key]
            print(f"Processing {session_key} (Session {session_id})...")
            
            for item in students:
                name, grade, school_name, subjects = item
                
                school = get_or_create_school(school_name)
                student = get_or_create_student(name, grade, school.id)
                
                for subj in subjects:
                    template = get_or_create_template(session_id, grade, subj)
                    
                    reg = ExamRegistration(
                        student_id=student.id,
                        exam_template_id=template.id,
                        exam_session_id=session_id,
                        attendance_status='pending'
                    )
                    db.session.add(reg)
                    count += 1
                    
        db.session.commit()
        print(f"Done! Imported {count} registrations.")

if __name__ == '__main__':
    main()
