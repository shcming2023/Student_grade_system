import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wtf_app_simple import app, db, Student, ExamRegistration, ExamTemplate

with app.app_context():
    count = Student.query.count()
    print(f"Total Students: {count}")
    
    # Check if '黄昱珩' exists
    s = Student.query.filter_by(name='黄昱珩').first()
    if s:
        print(f"Found 黄昱珩: {s.name}, Grade: {s.grade_level}, School: {s.school.name if s.school else 'None'}")
        regs = ExamRegistration.query.filter_by(student_id=s.id).all()
        for r in regs:
            print(f"  - Registered for: {r.exam_template.name} ({r.exam_session.name})")
    else:
        print("黄昱珩 NOT FOUND")

    # Check gender distribution
    males = Student.query.filter_by(gender='M').count()
    females = Student.query.filter_by(gender='F').count()
    print(f"Males: {males}, Females: {females}")
