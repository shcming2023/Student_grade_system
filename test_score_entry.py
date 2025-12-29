import unittest
from datetime import datetime
from wtf_app_simple import app, db, ExamTemplate, ExamSession, Student, ExamRegistration, Question, Score

class TestScoreEntry(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Create Test Data
        self.template = ExamTemplate(name="Test Template 2025")
        db.session.add(self.template)
        db.session.commit()

        self.session = ExamSession(exam_date="2025-01-01", location="Test Loc")
        db.session.add(self.session)
        db.session.commit()

        self.student = Student(name="Test Student", student_id="TS001", gender="M", school="Test School", grade="1", contact_info="123")
        db.session.add(self.student)
        db.session.commit()

        self.reg = ExamRegistration(student_id=self.student.id, exam_session_id=self.session.id, exam_template_id=self.template.id)
        db.session.add(self.reg)
        
        self.q1 = Question(exam_template_id=self.template.id, question_number="1", score=10.0, module="Module A")
        self.q2 = Question(exam_template_id=self.template.id, question_number="2", score=5.0, module="Module B")
        db.session.add_all([self.q1, self.q2])
        db.session.commit()

        # Mock login (if necessary, but I'll try to bypass or mock session if endpoints require login)
        # The endpoints require @login_required. I need to simulate login.
        # Since I can't easily mock flask-login without more setup, I will modify the test to use a test_request_context with a logged-in user if possible, 
        # or just disable login_required for testing? No, that's hacking code.
        # I'll use a transaction to create a user and login.
        from wtf_app_simple import User
        self.user = User(username="admin", password="password", role="admin") # Note: password hashing might be needed if the app uses it.
        # wtf_app_simple uses generate_password_hash? Let's check.
        # Assuming simple storage for now or I'll just check if I can login.
        # Actually, looking at previous file reads, it uses `check_password_hash`.
        from werkzeug.security import generate_password_hash
        self.user.password_hash = generate_password_hash("password")
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
        resp = self.app.get('/api/score-entry/templates')
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Test Template 2025")
        self.assertEqual(data[0]['student_count'], 1)

        # 2. Get Students
        resp = self.app.get(f'/api/score-entry/students?template_name={self.template.name}')
        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['student_id'], "TS001")

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
        self.assertEqual(data[0]['scored_questions'], 2)

if __name__ == '__main__':
    unittest.main()
