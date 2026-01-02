import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from wtf_app_simple import app

def simulate_frontend():
    with app.test_client() as client:
        # 1. Login first to get session
        # Assuming there is a login route or we can mock session
        # But wait, I can just use app.test_client() which handles cookies if I login.
        # Let's bypass login by using `with app.test_request_context` or just mocking the route?
        # No, `wtf_app_simple` has `login_required`.
        
        # Let's try to login. I need a valid user.
        # Default user usually admin/123456 or something.
        # Let's check `wtf_app_simple.py` for user model or creating a dummy user.
        pass

# Actually, I can just run a script that imports the logic of the API directly
# avoiding the HTTP layer for now to verify the LOGIC first.
# If logic works, then it's an HTTP/Auth issue or Frontend JS issue.

from wtf_app_simple import db, ExamTemplate, Student, ExamRegistration, School, ExamSession, Question
from flask import jsonify

def test_api_logic(template_id):
    with app.app_context():
        print(f"Testing API logic for Template ID: {template_id}")
        
        # --- Logic from api_students_by_template ---
        template = ExamTemplate.query.get(template_id)
        if not template:
            print("Template not found")
            return

        print(f"Found Template: {template.name}")

        # 1. Find related templates
        related_templates = ExamTemplate.query.filter_by(
            name=template.name,
            subject_id=template.subject_id,
            grade_level=template.grade_level
        ).all()
        
        related_ids = [t.id for t in related_templates]
        print(f"Related IDs: {related_ids}")

        # 2. Query Students (The updated Outer Join Logic)
        query = db.session.query(
            Student, School, ExamRegistration, ExamTemplate, ExamSession
        ).outerjoin(School, Student.school_id == School.id)\
         .join(ExamRegistration, Student.id == ExamRegistration.student_id)\
         .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
         .outerjoin(ExamSession, ExamRegistration.exam_session_id == ExamSession.id)\
         .filter(ExamRegistration.exam_template_id.in_(related_ids))
        
        results = query.all()
        print(f"Query returned {len(results)} rows.")

        students_data = []
        for student, school, reg, tmpl, session_obj in results:
             students_data.append({
                'id': student.id,
                'name': student.name,
                'status': reg.attendance_status
            })
        
        print(f"Processed {len(students_data)} students.")
        if len(students_data) > 0:
            print("Sample Student:", students_data[0])
        else:
            print("❌ No students found!")

if __name__ == "__main__":
    # Test with G3 Chinese (ID 21)
    test_api_logic(21)
