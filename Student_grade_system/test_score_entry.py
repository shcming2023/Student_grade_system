import unittest
import sys
import os
from datetime import datetime

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from wtf_app_simple import app, db, ExamTemplate, ExamSession, Student, ExamRegistration, Question, Score, User, School
from werkzeug.security import generate_password_hash

class TestScoreEntry(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Create Test Data
        self.template = ExamTemplate(name="Test Template 2025", grade_level="1", subject_id=1, total_questions=2)
        db.session.add(self.template)
        db.session.commit()

        self.session_obj = ExamSession(name="Test Session", exam_date=datetime(2025, 1, 1).date(), location="Test Loc", session_type="standard", start_time="09:00", end_time="11:00")
        db.session.add(self.session_obj)
        db.session.commit()

        self.school_obj = School(name="Test School", code="TS001")
        db.session.add(self.school_obj)
        db.session.commit()

        self.student = Student(name="Test Student", student_id="TS001", gender="M", school_id=self.school_obj.id, grade_level="1")
        db.session.add(self.student)
        db.session.commit()

        self.reg = ExamRegistration(student_id=self.student.id, exam_session_id=self.session_obj.id, exam_template_id=self.template.id)
        db.session.add(self.reg)
        
        self.q1 = Question(exam_template_id=self.template.id, question_number="1", score=10.0, module="Module A")
        self.q2 = Question(exam_template_id=self.template.id, question_number="2", score=5.0, module="Module B")
        db.session.add_all([self.q1, self.q2])
        db.session.commit()

        # Create User
        self.user = User(username="admin", role="admin")
        self.user.set_password("password")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        return self.app.post('/login', data=dict(
            username='admin',
            password='password'
        ), follow_redirects=True)

    def test_flow(self):
        self.login()

        # 1. Get Templates
        # The template creation logic in wtf_app_simple.py creates templates dynamically based on subjects and grades.
        # But in our setUp, we created a template manually.
        # However, api_score_entry_templates filters by joining Question? 
        # Let's check api_score_entry_templates logic.
        
        resp = self.app.get('/api/score-entry/templates')
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        
        # Verify our test template is present
        # If the API requires questions to be linked to the template, make sure we have questions.
        # We added q1 and q2 linked to self.template.id.
        
        test_template = next((t for t in data if t['name'] == "Test Template 2025"), None)
        
        # If test_template is None, it might be because the API query has some filter we missed.
        # api_score_entry_templates query:
        # db.session.query(ExamTemplate.name, ...)
        # .join(Question, ExamTemplate.id == Question.exam_template_id)
        # .group_by(ExamTemplate.id)
        
        self.assertIsNotNone(test_template, f"Template not found in response: {data}")
        # self.assertEqual(test_template['student_count'], 1) 

        # 2. Get Students
        # self.template.name matches what we set
        
        # NOTE: api_score_entry_students uses this query:
        # registrations = db.session.query(...)
        # .join(Student).join(ExamSession).join(ExamTemplate)
        # .filter(ExamRegistration.exam_template_id.in_(template_ids))
        
        # We need to ensure ExamRegistration is set up correctly in setUp.
        # We did: self.reg = ExamRegistration(student_id=self.student.id, exam_session_id=self.session_obj.id, exam_template_id=self.template.id)
        
        resp = self.app.get(f'/api/score-entry/students?template_name={self.template.name}')
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['student_code'], "TS001") # API returns student_code not student_id

        # 3. Get Student Detail
        resp = self.app.get(f'/api/score-entry/student-detail/{self.student.id}?template_name={self.template.name}')
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(len(data['questions']), 2)
        self.assertEqual(data['student']['name'], "Test Student")

        # 4. Save Scores
        scores = {
            str(self.q1.id): 9.5,
            str(self.q2.id): 4.0
        }
        resp = self.app.post('/api/score-entry/save', json={
            'student_id': self.student.id,
            'scores': scores
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json['success'])

        # 5. Verify DB
        saved_scores = Score.query.filter_by(student_id=self.student.id).all()
        self.assertEqual(len(saved_scores), 2)
        score_map = {s.question_id: s.score for s in saved_scores}
        self.assertEqual(score_map[self.q1.id], 9.5)
        self.assertEqual(score_map[self.q2.id], 4.0)

        # 6. Verify Progress in Student List
        resp = self.app.get(f'/api/score-entry/students?template_name={self.template.name}')
        data = resp.json
        self.assertEqual(data[0]['scored_count'], 2)
        print("Test Passed!")

if __name__ == '__main__':
    unittest.main()
