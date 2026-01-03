
import sys
import os
import json

# Add project root to path
sys.path.append('/opt/Way To Future考试管理系统/Student_grade_system')

from wtf_app_simple import app, db, Student, User, ExamRegistration, ExamSession, ExamTemplate

def debug_update():
    with app.app_context():
        # Find a student
        student = Student.query.first()
        if not student:
            print("No students found.")
            return

        # Ensure student has a registration
        if not student.registrations:
            print("Adding a dummy registration...")
            session = ExamSession.query.first()
            template = ExamTemplate.query.first()
            if session and template:
                reg = ExamRegistration(
                    student_id=student.id,
                    exam_session_id=session.id,
                    exam_template_id=template.id,
                    status='registered'
                )
                db.session.add(reg)
                db.session.commit()
                print("Registration added.")
                # Refresh student
                student = Student.query.get(student.id)

        print(f"Testing update for student ID: {student.id}, Name: {student.name}")
        print(f"Existing registrations: {len(student.registrations)}")

        # Simulate update payload
        # Try to break it
        data = {
            'student_id': student.student_id,
            'name': student.name,
            'gender': 'M',
            'grade_level': student.grade_level,
            'school_name': '', # Empty school name
            'class_name': None, # None class name
            'registrations': [] 
        }
        
        # We need to simulate a request or just call the logic?
        # Better to use test client.
        
        client = app.test_client()
        
        # Login first
        # Need a user.
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("No admin user found.")
            return
            
        with client.session_transaction() as sess:
            sess['user_id'] = admin.id
            sess['role'] = admin.role
            
        print(f"Logged in as {admin.username}")
        
        # Send PUT request
        response = client.put(
            f'/api/students/{student.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {response.data.decode('utf-8')}")
        
        if response.status_code != 200:
            print("Update failed.")
        else:
            print("Update successful.")

if __name__ == '__main__':
    debug_update()
