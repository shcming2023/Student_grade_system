from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'wtf-exam-system-secret-key-2023')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wtf_exam_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='teacher')

class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    grade_level = db.Column(db.String(10), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    class_name = db.Column(db.String(50))
    school = db.relationship('School', backref='students')

class ExamSession(db.Model):
    __tablename__ = 'exam_sessions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    session_type = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='draft')
    location = db.Column(db.String(100))

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    total_score = db.Column(db.Float, default=100.0)

class ExamTemplate(db.Model):
    __tablename__ = 'exam_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    exam_session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'))
    grade_level = db.Column(db.String(10), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    grader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subject = db.relationship('Subject', backref='templates')
    exam_session = db.relationship('ExamSession', backref='templates')

class ExamRegistration(db.Model):
    __tablename__ = 'exam_registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    exam_session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'))
    exam_template_id = db.Column(db.Integer, db.ForeignKey('exam_templates.id'))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    attendance_status = db.Column(db.String(20))
    student = db.relationship('Student')
    exam_session = db.relationship('ExamSession')
    exam_template = db.relationship('ExamTemplate')

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_number = db.Column(db.String(20), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    module = db.Column(db.String(50))
    knowledge_point = db.Column(db.String(100))
    score = db.Column(db.Float, nullable=False)
    exam_template_id = db.Column(db.Integer, db.ForeignKey('exam_templates.id'))
    subject = db.relationship('Subject')
    exam_template = db.relationship('ExamTemplate', backref='questions')

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    score = db.Column(db.Float, nullable=False)
    is_correct = db.Column(db.Boolean)
    scoring_time = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student')
    question = db.relationship('Question')
