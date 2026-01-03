import requests
import sys
import os

# Add path to import app
sys.path.append('/opt/Way To Future考试管理系统/Student_grade_system')
from wtf_app_simple import app, db, Student, ExamSession, ExamTemplate

# Configuration
BASE_URL = 'http://localhost:8083'
USERNAME = 'admin'
PASSWORD = 'password'

# 1. Login
session = requests.Session()
try:
    login_data = {'username': USERNAME, 'password': PASSWORD}
    r = session.post(f'{BASE_URL}/login', data=login_data)
    if 'user_id' not in session.cookies and 'session' not in session.cookies:
        print("Login failed")
        sys.exit(1)
    print("Login successful")
except Exception as e:
    print(f"Connection error: {e}")
    sys.exit(1)

# 2. Get resources
with app.app_context():
    # Find a session and template
    exam_session = ExamSession.query.first()
    template = ExamTemplate.query.first()
    
    if not exam_session or not template:
        print("No session or template found to test registrations")
        # Just create dummy ones if needed, but let's assume they exist
        sys.exit(1)
        
    session_id = exam_session.id
    template_id = template.id
    print(f"Using Session ID: {session_id}, Template ID: {template_id}")

    # Create a student
    student_data = {
        'name': 'Test Reg Student',
        'gender': 'M',
        'grade_level': 'G1',
        'school_name': 'Test School',
        'class_name': 'Class 1',
        'registrations': []
    }
    
    # We can use API or DB. Let's use DB to be faster and sure about ID.
    import time
    import random
    sid = f"S{int(time.time())}{random.randint(10,99)}"
    
    # Check if school exists
    from wtf_app_simple import School
    school = School.query.filter_by(name='Test School').first()
    if not school:
        school = School(name='Test School', code='SCH_TEST')
        db.session.add(school)
        db.session.commit()
        
    student = Student(
        student_id=sid,
        name='Test Reg Student',
        gender='M',
        grade_level='G1',
        school_id=school.id,
        class_name='Class 1'
    )
    db.session.add(student)
    db.session.commit()
    student_db_id = student.id
    print(f"Created Student DB ID: {student_db_id}")

# 3. Update with NEW School and NEW Registration
update_data = {
    'student_id': sid,
    'name': 'Test Reg Student',
    'gender': 'F', 
    'grade_level': 'G1',
    'school_name': 'New School ' + sid, # New school
    'class_name': 'Class 1',
    'registrations': [
        {
            'session_id': str(session_id), # Frontend sends string often
            'template_ids': [str(template_id)]
        }
    ]
}

print(f"Sending update payload: {update_data}")
r = session.put(f'{BASE_URL}/api/students/{student_db_id}', json=update_data)
print(f"Update response: {r.status_code} {r.text}")
