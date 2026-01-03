#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
橡心国际WTF活动管理平台 - 简化版本
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash, make_response
import flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from datetime import datetime, date
import os
import io
import hashlib
import pandas as pd
import zipfile
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Frame, PageTemplate
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import requests

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'wtf-exam-system-secret-key-2023')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wtf_exam_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Email Config
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.example.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'user@example.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'password')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')

# 初始化数据库
db = SQLAlchemy(app)

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='teacher')  # admin, teacher
    english_name = db.Column(db.String(50))
    real_name = db.Column(db.String(50))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'english_name': self.english_name or self.username,
            'real_name': self.real_name or ''
        }

# 简化的数据模型
class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code
        }
    
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=True)  # Changed to nullable
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    grade_level = db.Column(db.String(10), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    class_name = db.Column(db.String(50), nullable=True) # Changed to nullable explicitly
    email = db.Column(db.String(100)) # Added email field
    
    school = db.relationship('School', backref='students')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id or '',
            'name': self.name,
            'gender': self.gender,
            'grade_level': self.grade_level,
            'school_id': self.school_id,
            'school_name': self.school.name if self.school else None,
            'class_name': self.class_name or ''
        }

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), default='Way To Future IV')
    company_name_zh = db.Column(db.String(100), default='橡心国际')
    logo_path = db.Column(db.String(255))  # Path relative to static folder
    
    # LLM Configuration
    llm_api_provider = db.Column(db.String(50), default='deepseek')
    llm_api_key = db.Column(db.String(255))
    llm_api_base_url = db.Column(db.String(255), default='https://api.deepseek.com')
    llm_model = db.Column(db.String(100), default='deepseek-chat')
    
    def to_dict(self):
        return {
            'company_name': self.company_name,
            'company_name_zh': self.company_name_zh,
            'logo_path': self.logo_path,
            'llm_api_provider': self.llm_api_provider,
            'llm_api_key': self.llm_api_key,
            'llm_api_base_url': self.llm_api_base_url,
            'llm_model': self.llm_model
        }

class ExamSession(db.Model):
    __tablename__ = 'exam_sessions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    session_type = db.Column(db.String(20), nullable=False)  # morning/afternoon
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='draft')
    location = db.Column(db.String(100))
    # New fields for PDF Header
    exam_name_en = db.Column(db.String(100)) # Left side, e.g. Way To Future VII
    company_brand = db.Column(db.String(100)) # Middle, e.g. 橡心国际 (can override system setting)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'exam_date': self.exam_date.strftime('%Y-%m-%d') if self.exam_date else None,
            'session_type': self.session_type,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'status': self.status,
            'location': self.location,
            'exam_name_en': self.exam_name_en,
            'company_brand': self.company_brand
        }

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # langford/oxford/amc等
    total_score = db.Column(db.Float, default=100.0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'type': self.type,
            'total_score': self.total_score
        }

exam_template_sessions = db.Table('exam_template_sessions',
    db.Column('exam_template_id', db.Integer, db.ForeignKey('exam_templates.id'), primary_key=True),
    db.Column('exam_session_id', db.Integer, db.ForeignKey('exam_sessions.id'), primary_key=True)
)

class ExamTemplate(db.Model):
    __tablename__ = 'exam_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    # exam_session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'))  # Deprecated
    exam_session_id = db.Column(db.Integer, nullable=True) # Keep for backward compatibility/DB schema matching but unused
    grade_level = db.Column(db.String(10), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    
    # Teachers
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    grader_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    subject = db.relationship('Subject', backref='templates')
    # exam_session = db.relationship('ExamSession', backref='templates') # Deprecated
    sessions = db.relationship('ExamSession', secondary=exam_template_sessions, lazy='subquery',
        backref=db.backref('templates', lazy=True))
    
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_templates')
    grader = db.relationship('User', foreign_keys=[grader_id], backref='graded_templates')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'session_ids': [s.id for s in self.sessions],
            'session_names': [s.name for s in self.sessions],
            'grade_level': self.grade_level,
            'total_questions': self.total_questions,
            'creator_id': self.creator_id,
            'creator_name': self.creator.username if self.creator else None,
            'grader_id': self.grader_id,
            'grader_name': self.grader.username if self.grader else None
        }

class ExamRegistration(db.Model):
    __tablename__ = 'exam_registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    exam_session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'))
    exam_template_id = db.Column(db.Integer, db.ForeignKey('exam_templates.id'))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    attendance_status = db.Column(db.String(20))  # present/absent
    score = db.Column(db.Float)
    status = db.Column(db.String(20))
    
    student = db.relationship('Student', backref='registrations')
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

    def to_dict(self):
        return {
            'id': self.id,
            'question_number': self.question_number,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'module': self.module,
            'knowledge_point': self.knowledge_point,
            'score': self.score,
            'exam_template_id': self.exam_template_id
        }

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

class AICommentHistory(db.Model):
    __tablename__ = 'ai_comment_history'
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('exam_registrations.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_ai_generated = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='draft')  # draft, confirmed
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    confirmed_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    registration = db.relationship('ExamRegistration', backref='ai_comments')
    confirmer = db.relationship('User', foreign_keys=[confirmed_by])

    __table_args__ = (
        db.UniqueConstraint('registration_id', 'version', name='uq_registration_version'),
    )

class ReportCard(db.Model):
    __tablename__ = 'report_cards'
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('exam_registrations.id'))
    ai_comment = db.Column(db.Text)
    teacher_comment = db.Column(db.Text)
    confirmed_comment_id = db.Column(db.Integer, db.ForeignKey('ai_comment_history.id'))
    pdf_url = db.Column(db.String(255))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    registration = db.relationship('ExamRegistration', backref=db.backref('report_card', uselist=False))
    confirmed_comment = db.relationship('AICommentHistory', foreign_keys=[confirmed_comment_id])

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# 管理员权限装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            if request.path.startswith('/api/') or request.is_json:
                return jsonify({'success': False, 'message': '权限不足'}), 403
            flash('需要管理员权限', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Global login requirement
@app.before_request
def require_login():
    # Allow static files, login page, and favicon
    if request.endpoint and 'static' not in request.endpoint and \
       request.endpoint != 'login' and request.endpoint != 'logout':
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))

# 路由定义
@app.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """系统设置"""
    setting = SystemSetting.query.first()
    if not setting:
        setting = SystemSetting()
        db.session.add(setting)
        db.session.commit()
        
    if request.method == 'POST':
        setting.company_name = request.form.get('company_name')
        setting.company_name_zh = request.form.get('company_name_zh')
        
        # LLM Settings
        setting.llm_api_provider = request.form.get('llm_api_provider')
        setting.llm_api_key = request.form.get('llm_api_key')
        setting.llm_api_base_url = request.form.get('llm_api_base_url')
        setting.llm_model = request.form.get('llm_model')
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename:
                from werkzeug.utils import secure_filename
                filename = secure_filename(file.filename)
                # Ensure static/img directory exists
                img_dir = os.path.join(app.static_folder, 'img')
                if not os.path.exists(img_dir):
                    os.makedirs(img_dir)
                
                logo_path = os.path.join(img_dir, filename)
                file.save(logo_path)
                setting.logo_path = f'img/{filename}'
                
        db.session.commit()
        flash('系统设置已保存', 'success')
        return redirect(url_for('settings'))
        
    return render_template('wtf_settings.html', setting=setting)

@app.route('/api/test-llm-connection', methods=['POST'])
@login_required
@admin_required
def test_llm_connection():
    """测试LLM连接"""
    data = request.get_json()
    api_key = data.get('api_key')
    base_url = data.get('base_url', 'https://api.deepseek.com')
    model = data.get('model', 'deepseek-chat')
    
    if not api_key:
        return jsonify({'success': False, 'message': 'API Key 不能为空'})
        
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': 'Ping'}],
            'max_tokens': 5
        }
        
        endpoint = f"{base_url.rstrip('/')}/chat/completions"
        
        import requests
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return jsonify({'success': True, 'message': '连接成功！LLM 响应正常。'})
        else:
            return jsonify({'success': False, 'message': f'连接失败 (HTTP {response.status_code}): {response.text[:100]}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'连接测试出错: {str(e)}'})

# Context processor to inject settings into all templates
@app.context_processor
def inject_settings():
    try:
        setting = SystemSetting.query.first()
        if not setting:
            return dict(system_setting={'company_name': 'Way To Future IV', 'company_name_zh': '橡心国际'})
        return dict(system_setting=setting.to_dict())
    except:
        return dict(system_setting={'company_name': 'Way To Future IV', 'company_name_zh': '橡心国际'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            next_page = request.args.get('next')
            # Redirect to index by default instead of dashboard
            return redirect(next_page or url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """用户注销"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """首页"""
    return render_template('wtf_index_simple.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """仪表板"""
    total_students = Student.query.count()
    total_exams = ExamSession.query.count()
    total_registrations = ExamRegistration.query.count()
    
    # 最近考试场次
    recent_exams = ExamSession.query.order_by(ExamSession.exam_date.desc()).limit(5).all()
    
    # 科目分布
    subjects = Subject.query.all()
    
    return render_template('wtf_dashboard.html', 
                         total_students=total_students,
                         total_exams=total_exams,
                         total_registrations=total_registrations,
                         recent_exams=recent_exams,
                         subjects=subjects)

@app.route('/exam-sessions')
def exam_sessions():
    """考试场次管理"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    
    query = ExamSession.query
    
    if search_query:
        query = query.filter(ExamSession.name.contains(search_query))
        
    pagination = query.order_by(ExamSession.exam_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    sessions = pagination.items
    
    return render_template('exam_sessions.html', 
                           sessions=sessions, 
                           pagination=pagination,
                           search_query=search_query)

@app.route('/students')
@login_required
def students():
    """考生管理"""
    students = Student.query.all()
    schools = School.query.all()
    return render_template('wtf_students.html', students=students, schools=schools)

@app.route('/teachers')
@login_required
@admin_required
def teachers_page():
    """教师管理页面"""
    return render_template('teachers.html')

@app.route('/api/teachers', methods=['GET'])
@login_required
@admin_required
def api_get_teachers():
    teachers = User.query.all()
    return jsonify([t.to_dict() for t in teachers])

@app.route('/api/teachers', methods=['POST'])
@login_required
@admin_required
def api_create_teacher():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
    new_user = User(
        username=data['username'],
        role=data.get('role', 'teacher'),
        english_name=data.get('english_name', data['username']),
        real_name=data.get('real_name', '')
    )
    new_user.set_password(data['password'])
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': '教师创建成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/teachers/<int:id>', methods=['PUT'])
@login_required
@admin_required
def api_update_teacher(id):
    # ... existing implementation ...
    pass # Placeholder, I won't replace this part, I will search for the end of api_update_teacher

# Let's search for something else to insert before.
# How about inserting before `if __name__ == '__main__':` or at the end of file?
# Or after `api_update_teacher`.

# Let's try to insert after `api_update_teacher` is defined.
# I need to see the content of api_update_teacher first to match correctly.

    user = User.query.get_or_404(id)
    data = request.get_json()
    
    try:
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        if 'role' in data:
            user.role = data['role']
            
        if 'english_name' in data:
            user.english_name = data['english_name']
            
        if 'real_name' in data:
            user.real_name = data['real_name']
            
        db.session.commit()
        return jsonify({'success': True, 'message': '教师信息更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/teachers/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_teacher(id):
    user = User.query.get_or_404(id)
    
    if user.username == 'admin':
        return jsonify({'success': False, 'message': '不能删除管理员账号'}), 400
        
    try:
        # Check dependencies (templates)
        if ExamTemplate.query.filter((ExamTemplate.creator_id == id) | (ExamTemplate.grader_id == id)).first():
             return jsonify({'success': False, 'message': '该教师已关联试卷，无法删除'}), 400
             
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': '教师删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# AI Comment APIs
@app.route('/api/ai-comment/generate', methods=['POST'])
@login_required
def generate_ai_comment():
    data = request.get_json()
    registration_id = data.get('registration_id')
    
    # Resolve registration_id if missing
    if not registration_id:
        student_id = data.get('student_id')
        template_name = data.get('template_name')
        if student_id and template_name:
            reg = db.session.query(ExamRegistration)\
                .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
                .filter(ExamRegistration.student_id == student_id)\
                .filter(ExamTemplate.name == template_name)\
                .first()
            if reg:
                registration_id = reg.id

    force = data.get('force', False)
    
    if not registration_id:
        return jsonify({'success': False, 'message': 'Missing registration_id'}), 400
        
    registration = ExamRegistration.query.get(registration_id)
    if not registration:
        return jsonify({'success': False, 'message': 'Registration not found'}), 404
        
    # 1. Check Quota
    MAX_GENERATIONS = 3
    used_count = AICommentHistory.query.filter_by(registration_id=registration_id).count()
    if used_count >= MAX_GENERATIONS:
        return jsonify({
            'success': False, 
            'error': 'quota_exceeded', 
            'message': f'已达到生成上限（{MAX_GENERATIONS}/{MAX_GENERATIONS}），无法继续生成。'
        }), 400
        
    # 2. Check Completeness
    questions = Question.query.filter_by(exam_template_id=registration.exam_template_id).all()
    question_ids = [q.id for q in questions]
    total_count = len(questions)
    
    if total_count > 0:
        scores = Score.query.filter(
            Score.student_id == registration.student_id,
            Score.question_id.in_(question_ids)
        ).all()
        filled_count = len(scores)
        missing_count = total_count - filled_count
    else:
        scores = []
        filled_count = 0
        missing_count = 0
    
    if missing_count > 0 and not force:
        return jsonify({
            'success': False,
            'error': 'incomplete_scores',
            'message': '检测到部分题目未填写成绩，请确认后重试。',
            'missing_count': missing_count,
            'total_count': total_count
        }), 400
        
    # 3. Call LLM
    setting = SystemSetting.query.first()
    if not setting or not setting.llm_api_key:
        return jsonify({'success': False, 'message': 'LLM API尚未配置，请联系管理员。'}), 500
        
    student = registration.student
    template = registration.exam_template
    
    score_details = []
    for s in scores:
        q = next((x for x in questions if x.id == s.question_id), None)
        if q:
            score_details.append(f"题目{q.question_number}({q.knowledge_point}): {s.score}/{q.score}")
            
    prompt = f"""
    请根据以下学生考试数据生成一段简短的评语（200字以内），包含优点和改进建议。
    
    学生姓名：{student.name}
    考试名称：{template.name}
    年级：{student.grade_level}
    总分：{registration.score}
    
    题目得分详情：
    {"; ".join(score_details)}
    """
    
    try:
        headers = {
            "Authorization": f"Bearer {setting.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": setting.llm_model,
            "messages": [
                {"role": "system", "content": "你是一位专业的老师，负责根据学生的考试成绩撰写评语。评语应客观、鼓励为主，指出具体知识点的掌握情况。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{setting.llm_api_base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            return jsonify({'success': False, 'message': f'LLM API Error: {response.text}'}), 500
            
        result = response.json()
        ai_content = result['choices'][0]['message']['content']
        
        # 4. Save to History
        new_version = used_count + 1
        history = AICommentHistory(
            registration_id=registration_id,
            version=new_version,
            content=ai_content,
            status='draft',
            confirmed_by=session['user_id']
        )
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'comment': {
                'id': history.id,
                'version': history.version,
                'content': history.content,
                'status': history.status,
                'generated_at': history.generated_at.isoformat()
            },
            'remaining_quota': MAX_GENERATIONS - new_version
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ai-comment/history', methods=['GET'])
@login_required
def get_ai_comment_history():
    registration_id = request.args.get('registration_id')
    
    # Resolve registration_id if missing
    if not registration_id:
        student_id = request.args.get('student_id')
        template_name = request.args.get('template_name')
        if student_id and template_name:
            reg = db.session.query(ExamRegistration)\
                .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
                .filter(ExamRegistration.student_id == student_id)\
                .filter(ExamTemplate.name == template_name)\
                .first()
            if reg:
                registration_id = reg.id
                
    if not registration_id:
        return jsonify({'success': False, 'message': 'Missing registration_id'}), 400
        
    history = AICommentHistory.query.filter_by(registration_id=registration_id).order_by(AICommentHistory.version.asc()).all()
    
    MAX_GENERATIONS = 3
    used_count = len(history)
    
    return jsonify({
        'success': True,
        'history': [{
            'id': h.id,
            'version': h.version,
            'content': h.content,
            'status': h.status,
            'generated_at': h.generated_at.isoformat(),
            'confirmed_at': h.confirmed_at.isoformat() if h.confirmed_at else None
        } for h in history],
        'quota': {
            'used': used_count,
            'total': MAX_GENERATIONS,
            'remaining': MAX_GENERATIONS - used_count
        }
    })

@app.route('/api/ai-comment/confirm', methods=['POST'])
@login_required
def confirm_ai_comment():
    data = request.get_json()
    comment_id = data.get('comment_id')
    content = data.get('content')
    
    if not comment_id:
        return jsonify({'success': False, 'message': 'Missing comment_id'}), 400
        
    comment = AICommentHistory.query.get(comment_id)
    if not comment:
        return jsonify({'success': False, 'message': 'Comment not found'}), 404
        
    # Update comment
    comment.content = content
    comment.status = 'confirmed'
    comment.confirmed_at = datetime.utcnow()
    comment.confirmed_by = session['user_id']
    
    # Update ReportCard (create if not exists)
    report_card = ReportCard.query.filter_by(registration_id=comment.registration_id).first()
    if not report_card:
        report_card = ReportCard(registration_id=comment.registration_id)
        db.session.add(report_card)
    
    report_card.confirmed_comment_id = comment.id
    report_card.teacher_comment = content 
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': '评语已确认'})

@app.route('/registration')
@login_required
def registration():
    """报考管理"""
    return render_template('registration.html')

@app.route('/report-cards')
@login_required
def report_cards():
    """成绩单管理"""
    return render_template('report_cards.html')

@app.route('/api/statistics')
def api_statistics():
    """统计分析API"""
    # 科目统计
    subject_stats = db.session.query(
        Subject.type,
        Subject.name,
        db.func.count(ExamTemplate.id).label('count')
    ).outerjoin(ExamTemplate).group_by(Subject.type, Subject.name).all()
    
    # 年级统计
    grade_stats = db.session.query(
        Student.grade_level,
        db.func.count(Student.id).label('count')
    ).group_by(Student.grade_level).all()
    
    return jsonify({
        'subject_stats': [{
            'type': stat.type,
            'name': stat.name,
            'count': stat.count
        } for stat in subject_stats],
        'grade_stats': [{
            'grade': stat.grade_level,
            'count': stat.count
        } for stat in grade_stats]
    })

@app.route('/question-templates')
def question_templates():
    """题目模板管理"""
    templates = db.session.query(
        ExamTemplate, Subject
    ).join(Subject).order_by(ExamTemplate.grade_level, Subject.name).all()
    return render_template('question_templates.html', templates=templates)

@app.route('/api/question-templates/<grade>')
def api_question_templates_by_grade(grade):
    """获取指定年级的题目模板"""
    templates = db.session.query(
        ExamTemplate, Subject
    ).join(Subject).filter(
        ExamTemplate.grade_level == grade
    ).all()
    
    return jsonify([{
        'id': template.id,
        'name': template.name,
        'subject': subject.name,
        'subject_code': subject.code,
        'grade': template.grade_level,
        'total_questions': template.total_questions
    } for template, subject in templates])

@app.route('/api/questions/<template_id>')
def api_questions_by_template(template_id):
    """获取指定模板的题目列表"""
    template = ExamTemplate.query.get(template_id)
    if not template:
        return jsonify({'error': '模板不存在'}), 404
    
    questions = Question.query.filter_by(subject_id=template.subject_id).all()
    
    return jsonify([{
        'id': question.id,
        'question_number': question.question_number,
        'module': question.module,
        'knowledge_point': question.knowledge_point,
        'score': float(question.score)
    } for question in questions])

@app.route('/api/exam-templates/<int:id>/assign-teachers', methods=['POST'])
@login_required
def api_assign_template_teachers(id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    template = ExamTemplate.query.get_or_404(id)
    data = request.get_json()
    
    try:
        # Update ALL templates with the same name to ensure consistency across sessions
        target_templates = ExamTemplate.query.filter_by(name=template.name).all()
        
        count = 0
        for t in target_templates:
            if 'creator_id' in data:
                t.creator_id = data['creator_id']
            if 'grader_id' in data:
                t.grader_id = data['grader_id']
            count += 1
            
        db.session.commit()
        return jsonify({'success': True, 'message': f'教师分配成功 (已同步至 {count} 个同名试卷)'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Score entry routes (Refactored v2.2)

@app.route('/score-entry')
@login_required
def score_entry_dashboard():
    """评分录入 - 仪表板 (选择试卷)"""
    return render_template('score_entry_dashboard.html')

@app.route('/score-entry/list')
@login_required
def score_entry_list():
    """评分录入 - 考生列表"""
    template_name = request.args.get('template_name')
    if not template_name:
        return redirect(url_for('score_entry_dashboard'))
    return render_template('score_entry_list.html', template_name=template_name)

@app.route('/score-entry/form')
@login_required
def score_entry_form():
    """评分录入 - 录入表单"""
    student_id = request.args.get('student_id')
    return render_template('score_entry_form.html', student_id=student_id)

# API Routes for Score Entry

@app.route('/api/score-entry/templates')
@login_required
def api_score_entry_templates():
    """获取唯一的试卷模板列表 (用于筛选)"""
    # Permission check
    user_id = session.get('user_id')
    role = session.get('role')
    
    query = db.session.query(
        ExamTemplate.name,
        ExamTemplate.grade_level,
        Subject.name.label('subject_name'),
        db.func.count(ExamTemplate.id).label('session_count')
    ).join(Subject)
    
    # If not admin, filter by grader_id
    if role != 'admin':
        query = query.filter(ExamTemplate.grader_id == user_id)

    # 聚合 unique name
    # Also count students for each unique template name
    # We need to sum up students for all template IDs matching the name
    
    # First get basic info
    templates = query.group_by(ExamTemplate.name, ExamTemplate.grade_level, Subject.name)\
     .order_by(ExamTemplate.grade_level, Subject.name).all()
    
    results = []
    for t in templates:
        # Get all template IDs for this name
        sub_query = ExamTemplate.query.filter_by(name=t.name)
        if role != 'admin':
            sub_query = sub_query.filter_by(grader_id=user_id)
        t_ids = [sub.id for sub in sub_query.all()]
        
        # Count students
        student_count = 0
        if t_ids:
            student_count = ExamRegistration.query.filter(ExamRegistration.exam_template_id.in_(t_ids)).count()
            
        results.append({
            'name': t.name,
            'grade': t.grade_level,
            'subject': t.subject_name,
            'session_count': t.session_count,
            'student_count': student_count
        })
    
    return jsonify(results)

@app.route('/api/score-entry/students')
@login_required
def api_score_entry_students():
    """获取指定试卷名称的所有考生 (跨场次)"""
    template_name = request.args.get('template_name')
    user_id = session.get('user_id')
    role = session.get('role')
    
    # Debug info removed
    if not template_name:
        return jsonify({'error': 'Missing template name'}), 400
        
    # 1. Find all template IDs with this name (and permission check)
    query_templates = ExamTemplate.query.filter_by(name=template_name)
    
    # If not admin, filter by grader_id
    if role != 'admin':
        query_templates = query_templates.filter_by(grader_id=user_id)
        
    templates = query_templates.all()
    template_ids = [t.id for t in templates]
    
    if not template_ids:
        return jsonify([])
        
    try:
        # 2. Find all students registered for these templates
        query = db.session.query(
            ExamRegistration, Student, ExamSession, ExamTemplate
        ).join(Student)\
         .join(ExamSession, ExamRegistration.exam_session_id == ExamSession.id)\
         .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
         .filter(ExamRegistration.exam_template_id.in_(template_ids))\
         .order_by(ExamSession.exam_date, Student.student_id)
         
        registrations = query.all()
         
        # 3. Check scoring status for each student
        results = []
        for reg, student, session_obj, template in registrations:
            # Get total questions count
            total_q = template.total_questions
            # Get scored count
            # Note: This is a bit expensive (N+1), but for <1000 students it's okay for now. 
            # Can be optimized with a group by query later if needed.
            # We need to find questions for this template
            q_ids = db.session.query(Question.id).filter_by(exam_template_id=template.id).all()
            q_ids = [q[0] for q in q_ids]
            
            scored_count = 0
            if q_ids:
                scored_count = Score.query.filter(
                    Score.student_id == student.id,
                    Score.question_id.in_(q_ids)
                ).count()
                
            status = 'completed' if scored_count >= total_q and total_q > 0 else \
                     'in_progress' if scored_count > 0 else 'pending'
                     
            results.append({
                'student_id': student.id,
                'student_code': student.student_id,
                'name': student.name,
                'session_name': session_obj.name,
                'status': status,
                'scored_count': scored_count,
                'total_questions': total_q
            })
            
        return jsonify(results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/score-entry/student-detail/<int:student_id>')
@login_required
def api_score_entry_student_detail(student_id):
    """获取单个考生的录入详情 (题目 + 已有分数)"""
    template_name = request.args.get('template_name')
    
    # 1. Get Registration and Template
    query = db.session.query(ExamRegistration, ExamTemplate)\
        .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
        .filter(ExamRegistration.student_id == student_id)
        
    if template_name:
        query = query.filter(ExamTemplate.name == template_name)
        
    reg_data = query.first()
    
    if not reg_data:
        return jsonify({'error': 'Registration not found'}), 404
        
    reg, template = reg_data
    
    # 2. Get Questions
    questions = Question.query.filter_by(exam_template_id=template.id).all()
    
    # Natural sort
    def natural_sort_key(q):
        import re
        parts = re.split(r'(\d+)', q.question_number)
        return [int(p) if p.isdigit() else p for p in parts]
    questions.sort(key=natural_sort_key)
    
    # 3. Get Scores
    q_ids = [q.id for q in questions]
    scores = []
    if q_ids:
        saved_scores = Score.query.filter(
            Score.student_id == student_id,
            Score.question_id.in_(q_ids)
        ).all()
        scores = {s.question_id: s.score for s in saved_scores}
        
    # 3.1 Get Report Card Comment
    report_card = ReportCard.query.filter_by(registration_id=reg.id).first()
    ai_comment = report_card.ai_comment if report_card else ""

    # Get AI Generation Count
    ai_gen_count = AICommentHistory.query.filter_by(registration_id=reg.id).count()
        
    # 4. Navigation (Prev/Next)
    prev_id = None
    next_id = None
    
    if template_name:
        # Find all template IDs with this name
        templates = ExamTemplate.query.filter_by(name=template_name).all()
        template_ids = [t.id for t in templates]
        
        # Get sorted list of student IDs
        # Order must match the list view: ExamSession.exam_date, Student.student_id
        student_ids_tuples = db.session.query(Student.id)\
            .join(ExamRegistration, Student.id == ExamRegistration.student_id)\
            .join(ExamSession, ExamRegistration.exam_session_id == ExamSession.id)\
            .filter(ExamRegistration.exam_template_id.in_(template_ids))\
            .order_by(ExamSession.exam_date, Student.student_id)\
            .all()
            
        all_ids = [s[0] for s in student_ids_tuples]
        
        try:
            curr_idx = all_ids.index(student_id)
            if curr_idx > 0:
                prev_id = all_ids[curr_idx - 1]
            if curr_idx < len(all_ids) - 1:
                next_id = all_ids[curr_idx + 1]
        except ValueError:
            pass
            
    # 5. Construct Response
    return jsonify({
        'student': {
            'id': student_id,
            'name': reg.student.name,
            'student_id': reg.student.student_id,
            'template_name': template.name
        },
        'questions': [{
            'id': q.id,
            'number': q.question_number,
            'score': q.score, # max score
            'module': q.module
        } for q in questions],
        'scores': scores,
        'ai_comment': ai_comment,
        'ai_gen_count': ai_gen_count,
        'navigation': {
            'prev_id': prev_id,
            'next_id': next_id
        }
    })


@app.route('/api/score-entry/save', methods=['POST'])
@login_required
def api_score_entry_save():
    """保存分数 (Upsert) - 支持单个分数或批量分数"""
    data = request.get_json()
    student_id = data.get('student_id')
    
    # Check if batch mode (scores dict)
    scores_dict = data.get('scores') # {question_id: score_value}
    ai_comment = data.get('ai_comment')
    template_name = data.get('template_name')
    
    if scores_dict is not None and isinstance(scores_dict, dict):
        if not student_id:
             return jsonify({'success': False, 'message': 'Missing student_id'}), 400
             
        try:
            # Save AI Comment if provided
            if ai_comment is not None:
                reg = None
                
                # 1. Try by template_name
                if template_name:
                    reg = db.session.query(ExamRegistration)\
                        .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
                        .filter(ExamRegistration.student_id == student_id)\
                        .filter(ExamTemplate.name == template_name)\
                        .first()
                        
                # 2. Fallback to question context
                if not reg and scores_dict:
                    first_q_id = next(iter(scores_dict.keys()), None)
                    if first_q_id:
                        q = Question.query.get(int(first_q_id))
                        if q:
                            reg = ExamRegistration.query.filter_by(
                                student_id=student_id, 
                                exam_template_id=q.exam_template_id
                            ).first()
                            
                if reg:
                    report_card = ReportCard.query.filter_by(registration_id=reg.id).first()
                    if not report_card:
                        report_card = ReportCard(registration_id=reg.id)
                        db.session.add(report_card)
                    report_card.ai_comment = ai_comment
                             
            for q_id_str, score_val in scores_dict.items():
                q_id = int(q_id_str)
                # Logic reused for each score
                # 1. Check Question
                question = Question.query.get(q_id)
                if not question:
                    continue # Skip invalid questions
                
                # 2. Validate
                try:
                    val = float(score_val)
                    if val < 0 or val > question.score:
                        return jsonify({'success': False, 'message': f'题目Q{question.question_number}分数必须在 0 - {question.score} 之间'}), 400
                except ValueError:
                    return jsonify({'success': False, 'message': f'题目Q{question.question_number}分数必须是数字'}), 400
                
                # 3. Upsert
                score = Score.query.filter_by(student_id=student_id, question_id=q_id).first()
                if score:
                    score.score = val
                    score.is_correct = (val == question.score)
                    score.scoring_time = datetime.utcnow()
                else:
                    score = Score(
                        student_id=student_id,
                        question_id=q_id,
                        score=val,
                        is_correct=(val == question.score)
                    )
                    db.session.add(score)
            
            db.session.commit()
            return jsonify({'success': True})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    # Legacy/Single mode (kept for compatibility if needed, but updated frontend sends batch)
    question_id = data.get('question_id')
    score_value = data.get('score')
    
    if not all([student_id, question_id]):
        return jsonify({'success': False, 'message': 'Missing parameters'}), 400
        
    try:
        # Check if score exists
        score = Score.query.filter_by(student_id=student_id, question_id=question_id).first()
        
        # Validation: check max score
        question = Question.query.get(question_id)
        if not question:
             return jsonify({'success': False, 'message': 'Question not found'}), 404
             
        if score_value is None or score_value == '':
             # If empty, maybe delete? Or ignore? 
             # Let's assume user wants to clear it if they send null, or if they send nothing don't update.
             # Current frontend usually sends value.
             pass
        else:
            try:
                val = float(score_value)
                if val < 0 or val > question.score:
                     return jsonify({'success': False, 'message': f'分数必须在 0 - {question.score} 之间'}), 400
            except ValueError:
                 return jsonify({'success': False, 'message': '分数必须是数字'}), 400
        
        if score:
            score.score = float(score_value)
            score.is_correct = (score.score == question.score)
            score.scoring_time = datetime.utcnow()
        else:
            score = Score(
                student_id=student_id,
                question_id=question_id,
                score=float(score_value),
                is_correct=(float(score_value) == question.score)
            )
            db.session.add(score)
            
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# API removed per user request (v2.2)

@login_required
def api_students_by_session(exam_session_id):
    """获取指定考试场次的学生列表"""
    grade = request.args.get('grade')
    subject = request.args.get('subject') # Optional subject filter
    
    # 获取当前用户
    current_user_id = session.get('user_id')
    current_user = User.query.get(current_user_id)
    
    # 查询注册学生
    query = db.session.query(
        Student, School, Subject, ExamTemplate, ExamRegistration
    ).join(School, Student.school_id == School.id)\
     .join(ExamRegistration, Student.id == ExamRegistration.student_id)\
     .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
     .join(Subject, ExamTemplate.subject_id == Subject.id)\
     .filter(ExamRegistration.exam_session_id == exam_session_id)
    
    # 权限过滤：如果是普通教师，只能看自己负责阅卷的试卷
    if current_user and current_user.role != 'admin':
        query = query.filter(ExamTemplate.grader_id == current_user_id)
    
    if grade:
        query = query.filter(Student.grade_level == grade)
        
    if subject:
        query = query.filter(Subject.name == subject)
    
    results = query.all()
    
    students = []
    # Collect all needed questions IDs to fetch scores efficiently
    student_ids = []
    
    for student, school, sub, template, reg in results:
        student_ids.append(student.id)
        students.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': student.name,
            'grade_level': student.grade_level,
            'school_name': school.name,
            'subject_name': sub.name,
            'template_id': template.id,
            'status': reg.attendance_status # Optional
        })
    
    # 获取题目列表 (优化：支持多套试卷)
    # 前端目前假设同一列表用同一套题。为了兼容，我们按 template_id 分组返回，或者前端处理
    # 简单起见，如果 students 列表包含多个 template_id，我们可能需要前端支持切换或分别加载
    # 暂时保持取第一个的逻辑，但加入 scores 回显
    
    questions = []
    scores_map = {} # student_id -> { question_id: score }
    
    if students:
        # 假设按筛选结果，通常是同一年级同一科目，所以 template 应该是一样的
        # 如果不一样（例如没选科目），前端可能显示有问题。
        # 增强逻辑：获取所有涉及的 unique template
        template_ids = list(set(s['template_id'] for s in students))
        
        # 为了前端兼容性，我们只返回第一个模板的题目
        # 并在前端提示如果存在多个模板的情况（或者建议用户筛选科目）
        primary_template_id = template_ids[0]
        
        # 获取题目
        q_objs = Question.query.filter_by(exam_template_id=primary_template_id).all()
        
        # Natural Sort for Questions (e.g. Q1, Q2, Q10 instead of Q1, Q10, Q2)
        def natural_sort_key(q):
            import re
            # Extract number from question_number string
            parts = re.split(r'(\d+)', q.question_number)
            return [int(p) if p.isdigit() else p for p in parts]
            
        q_objs.sort(key=natural_sort_key)
        
        questions = [{
            'id': q.id,
            'question_number': q.question_number,
            'module': q.module,
            'knowledge_point': q.knowledge_point,
            'score': float(q.score)
        } for q in q_objs]
        
        # 获取已保存的分数
        # 获取涉及的所有题目ID（不仅是第一个模板，而是所有学生的模板）
        # 但前端只能显示一套题，所以我们只获取 primary_template_id 相关的分数
        q_ids = [q.id for q in q_objs]
        
        if student_ids and q_ids:
            saved_scores = Score.query.filter(
                Score.student_id.in_(student_ids),
                Score.question_id.in_(q_ids)
            ).all()
            
            for s in saved_scores:
                if s.student_id not in scores_map:
                    scores_map[s.student_id] = {}
                scores_map[s.student_id][s.question_id] = s.score

    return jsonify({
        'students': students,
        'questions': questions,
        'saved_scores': scores_map,
        'multiple_templates': len(set(s['template_id'] for s in students)) > 1 if students else False
    })

@app.route('/statistics')
@login_required
def statistics():
    """统计报表页面"""
    sessions = ExamSession.query.order_by(ExamSession.exam_date.desc()).all()
    return render_template('statistics.html', sessions=sessions)

@app.route('/api/stats/session/<int:session_id>')
@login_required
def api_session_stats(session_id):
    """获取考试场次详细统计"""
    # 1. 获取基础信息
    session = ExamSession.query.get_or_404(session_id)
    
    # 2. 获取该场次所有成绩
    # 连接: Score -> Student -> ExamRegistration (check session)
    # 简化: 先找到该场次的所有学生ID
    registrations = ExamRegistration.query.filter_by(exam_session_id=session_id).all()
    student_ids = [r.student_id for r in registrations]
    
    if not student_ids:
        return jsonify({
            'overview': {'total_students': 0, 'avg_score': 0, 'pass_rate': 0},
            'distribution': [],
            'question_stats': []
        })
        
    # 3. 计算总分统计
    # 获取每个学生的总分
    student_scores = []
    for sid in student_ids:
        scores = Score.query.filter_by(student_id=sid).all()
        if scores:
            total = sum(s.score for s in scores)
            student_scores.append(total)
            
    if not student_scores:
        return jsonify({
            'overview': {'total_students': 0, 'avg_score': 0, 'pass_rate': 0},
            'distribution': [],
            'question_stats': []
        })
        
    avg_score = sum(student_scores) / len(student_scores)
    max_score = max(student_scores)
    min_score = min(student_scores)
    # 假设满分为100或根据模板计算，这里简单假设60分及格
    pass_count = sum(1 for s in student_scores if s >= 60)
    pass_rate = (pass_count / len(student_scores)) * 100
    
    # 4. 分数段分布
    distribution = {
        '90-100': 0,
        '80-89': 0,
        '70-79': 0,
        '60-69': 0,
        '<60': 0
    }
    
    for s in student_scores:
        if s >= 90: distribution['90-100'] += 1
        elif s >= 80: distribution['80-89'] += 1
        elif s >= 70: distribution['70-79'] += 1
        elif s >= 60: distribution['60-69'] += 1
        else: distribution['<60'] += 1
        
    # 5. 题目正确率分析
    # 获取该场次使用的模板（假设同场次模板相同或取第一个）
    reg = registrations[0]
    template = ExamTemplate.query.get(reg.exam_template_id)
    questions = Question.query.filter_by(subject_id=template.subject_id).all()
    
    question_stats = []
    for q in questions:
        q_scores = Score.query.filter(
            Score.question_id == q.id,
            Score.student_id.in_(student_ids)
        ).all()
        
        if q_scores:
            correct_count = sum(1 for s in q_scores if s.is_correct)
            q_accuracy = (correct_count / len(q_scores)) * 100
            avg_q_score = sum(s.score for s in q_scores) / len(q_scores)
        else:
            q_accuracy = 0
            avg_q_score = 0
            
        question_stats.append({
            'number': q.question_number,
            'module': q.module,
            'accuracy': round(q_accuracy, 1),
            'avg_score': round(avg_q_score, 1)
        })
        
    # 按题号排序
    # question_stats.sort(key=lambda x: x['number']) # 简单排序，可能需要更复杂的逻辑
    
    return jsonify({
        'overview': {
            'total_students': len(student_scores),
            'avg_score': round(avg_score, 1),
            'max_score': max_score,
            'min_score': min_score,
            'pass_rate': round(pass_rate, 1)
        },
        'distribution': distribution,
        'question_stats': question_stats
    })

@app.route('/api/stats/export/<int:session_id>')
@login_required
def api_export_stats(session_id):
    """导出统计报表Excel"""
    session_obj = ExamSession.query.get_or_404(session_id)
    
    # 1. 获取所有成绩数据
    registrations = ExamRegistration.query.filter_by(exam_session_id=session_id).all()
    student_ids = [r.student_id for r in registrations]
    
    if not student_ids:
        return "无数据", 404
        
    # 获取学生详细成绩
    student_data = []
    for reg in registrations:
        student = reg.student
        scores = Score.query.filter_by(student_id=student.id).all()
        total_score = sum(s.score for s in scores)
        
        student_info = {
            '学号': student.student_id,
            '姓名': student.name,
            '年级': student.grade_level,
            '总分': total_score
        }
        
        # 添加每题得分
        for s in scores:
            student_info[f'Q{s.question.question_number}'] = s.score
            
        student_data.append(student_info)
        
    df_students = pd.DataFrame(student_data)
    
    # 2. 题目统计
    # 获取题目列表
    reg = registrations[0]
    template = ExamTemplate.query.get(reg.exam_template_id)
    questions = Question.query.filter_by(subject_id=template.subject_id).all()
    
    question_stats = []
    for q in questions:
        q_scores = Score.query.filter(
            Score.question_id == q.id,
            Score.student_id.in_(student_ids)
        ).all()
        
        if q_scores:
            correct_count = sum(1 for s in q_scores if s.is_correct)
            q_accuracy = (correct_count / len(q_scores)) * 100
            avg_q_score = sum(s.score for s in q_scores) / len(q_scores)
        else:
            q_accuracy = 0
            avg_q_score = 0
            
        question_stats.append({
            '题号': q.question_number,
            '模块': q.module,
            '知识点': q.knowledge_point,
            '满分': q.score,
            '平均得分': round(avg_q_score, 1),
            '正确率(%)': round(q_accuracy, 1)
        })
    
    df_questions = pd.DataFrame(question_stats)
    
    # 3. 导出到内存
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_students.to_excel(writer, sheet_name='学生成绩明细', index=False)
        df_questions.to_excel(writer, sheet_name='题目统计分析', index=False)
        
    output.seek(0)
    
    filename = f"{session_obj.name}_统计报表.xlsx"
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

# --- Email Functionality ---

def send_email_with_attachment(to_email, subject, body, attachment_bytes, attachment_filename):
    """Sends an email with a PDF attachment."""
    msg = MIMEMultipart()
    msg['From'] = app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment_bytes:
        part = MIMEApplication(attachment_bytes.getvalue(), Name=attachment_filename)
        part['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
        msg.attach(part)

    try:
        # For development/demo, if MAIL_SERVER is 'smtp.example.com', we just log it
        if app.config['MAIL_SERVER'] == 'smtp.example.com':
            print(f"MOCK EMAIL SENT to {to_email} with subject '{subject}'")
            return True, "Mock email sent (Server not configured)"
            
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        if app.config['MAIL_USE_TLS']:
            server.starttls()
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully"
    except Exception as e:
        print(f"EMAIL ERROR: {str(e)}")
        return False, str(e)

@app.route('/api/email/send-report-card', methods=['POST'])
@login_required
def send_report_card_email():
    """发送成绩单邮件"""
    data = request.get_json()
    student_id = data.get('student_id')
    exam_session_id = data.get('exam_session_id')
    template_id = data.get('template_id')
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'success': False, 'message': 'Student not found'}), 404
        
    if not student.email:
         return jsonify({'success': False, 'message': 'Student has no email address'}), 400
         
    # Generate PDF
    # Note: generate_report_card_pdf might need to be imported or available in scope. 
    # It is defined in this file (or imported if refactored).
    # Assuming it is available as 'generate_report_card_pdf' in this module.
    pdf_buffer = generate_report_card_pdf(student_id, exam_session_id, template_id)
    if not pdf_buffer:
        return jsonify({'success': False, 'message': 'Failed to generate PDF'}), 500
        
    # Send Email
    exam_session = ExamSession.query.get(exam_session_id)
    session_name = exam_session.name if exam_session else "Exam"
    
    subject = f"Score Report: {student.name} - {session_name}"
    body = f"Dear {student.name},\n\nPlease find attached your score report for {session_name}.\n\nBest regards,\nWay To Future Team"
    filename = f"ReportCard_{student.name}_{session_name}.pdf"
    
    success, msg = send_email_with_attachment(student.email, subject, body, pdf_buffer, filename)
    
    if success:
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'success': False, 'message': msg}), 500

import zipfile

@app.route('/api/pdf/batch-generate-zip', methods=['POST'])
@login_required
def batch_generate_zip():
    """批量生成PDF压缩包"""
    data = request.get_json()
    items = data.get('items', [])
    
    if not items:
        return jsonify({'error': 'No items provided'}), 400
        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for item in items:
            s_id = item.get('student_id')
            sess_id = item.get('exam_session_id')
            tmpl_id = item.get('template_id')
            
            student = Student.query.get(s_id)
            if not student:
                continue
                
            try:
                pdf_buffer = generate_report_card_pdf(s_id, sess_id, tmpl_id)
                if pdf_buffer:
                    exam_session = ExamSession.query.get(sess_id)
                    session_name = exam_session.name if exam_session else "Exam"
                    filename = f"ReportCard_{student.name}_{session_name}.pdf"
                    zip_file.writestr(filename, pdf_buffer.getvalue())
            except Exception as e:
                print(f"Error generating PDF for {s_id}: {e}")
                
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name='ReportCards_Batch.zip',
        mimetype='application/zip'
    )

@app.route('/api/email/batch-send-report-card-items', methods=['POST'])
@login_required
def batch_send_report_card_items():
    """批量发送成绩单邮件 (按列表)"""
    data = request.get_json()
    items = data.get('items', [])
    
    success_count = 0
    fail_count = 0
    details = []
    processed_keys = set()
    
    for item in items:
        s_id = item.get('student_id')
        sess_id = item.get('exam_session_id')
        tmpl_id = item.get('template_id')
        
        key = f"{s_id}-{sess_id}"
        if key in processed_keys:
            continue
        processed_keys.add(key)
        
        student = Student.query.get(s_id)
        if not student:
            continue
            
        if not student.email:
            fail_count += 1
            details.append({'student': student.name, 'status': 'No Email'})
            continue
            
        try:
            pdf_buffer = generate_report_card_pdf(s_id, sess_id, tmpl_id)
            if not pdf_buffer:
                fail_count += 1
                details.append({'student': student.name, 'status': 'PDF Generation Failed'})
                continue
                
            exam_session = ExamSession.query.get(sess_id)
            session_name = exam_session.name if exam_session else "Exam"
            subject = f"Score Report: {student.name} - {session_name}"
            body = f"Dear {student.name},\n\nPlease find attached your score report for {session_name}.\n\nBest regards,\nWay To Future Team"
            filename = f"ReportCard_{student.name}_{session_name}.pdf"
            
            success, msg = send_email_with_attachment(student.email, subject, body, pdf_buffer, filename)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                details.append({'student': student.name, 'status': f'Email Error: {msg}'})
                
        except Exception as e:
            fail_count += 1
            details.append({'student': student.name, 'status': f'Error: {str(e)}'})

    return jsonify({
        'success': True, 
        'summary': f"Sent: {success_count}, Failed: {fail_count}",
        'details': details
    })

@app.route('/api/email/batch-send-report-card', methods=['POST'])
@login_required
def batch_send_report_card_email():
    """批量发送成绩单邮件"""
    data = request.get_json()
    exam_session_id = data.get('exam_session_id')
    template_id = data.get('template_id') # Optional
    
    # Logic: Get all students in session (and template if provided)
    query = db.session.query(ExamRegistration)\
        .filter(ExamRegistration.exam_session_id == exam_session_id)
        
    if template_id:
        query = query.filter(ExamRegistration.exam_template_id == template_id)
        
    registrations = query.all()
    
    success_count = 0
    fail_count = 0
    details = []
    
    processed_student_ids = set()
    
    for reg in registrations:
        if reg.student_id in processed_student_ids:
            continue
        processed_student_ids.add(reg.student_id)
        
        student = reg.student
        if not student.email:
            fail_count += 1
            details.append({'student': student.name, 'status': 'No Email'})
            continue
            
        try:
            pdf_buffer = generate_report_card_pdf(student.id, exam_session_id, template_id)
            if not pdf_buffer:
                fail_count += 1
                details.append({'student': student.name, 'status': 'PDF Generation Failed'})
                continue
                
            exam_session = ExamSession.query.get(exam_session_id)
            session_name = exam_session.name if exam_session else "Exam"
            subject = f"Score Report: {student.name} - {session_name}"
            body = f"Dear {student.name},\n\nPlease find attached your score report for {session_name}.\n\nBest regards,\nWay To Future Team"
            filename = f"ReportCard_{student.name}_{session_name}.pdf"
            
            success, msg = send_email_with_attachment(student.email, subject, body, pdf_buffer, filename)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                details.append({'student': student.name, 'status': f'Email Error: {msg}'})
                
        except Exception as e:
            fail_count += 1
            details.append({'student': student.name, 'status': f'Error: {str(e)}'})
            
    return jsonify({
        'success': True, 
        'summary': f"Sent: {success_count}, Failed: {fail_count}",
        'details': details
    })

# API removed per user request (v2.2)


# API removed per user request (v2.2)


@app.route('/api/init-templates', methods=['POST'])
def api_init_templates():
    """初始化题目模板 - Controlled by Environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return jsonify({'error': 'Forbidden: Functionality disabled in production.'}), 403
        
    # Development logic (simplified for placeholder)
    # logic ...
    return jsonify({'success': True, 'message': 'Development mode: init allowed (logic pending)'})
    # ... (rest of code removed/commented)

@app.route('/api/ai-comment/generate', methods=['POST'])
@login_required
def api_generate_ai_comment():
    """生成AI评语 (Mock AI)"""
    data = request.get_json()
    student_id = data.get('student_id')
    template_name = data.get('template_name') # Optional
    
    if not student_id:
        return jsonify({'error': 'Missing student_id'}), 400
        
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
        
    # Get scores
    # Logic similar to student-detail
    query = db.session.query(ExamRegistration, ExamTemplate)\
        .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
        .filter(ExamRegistration.student_id == student_id)
        
    if template_name:
        query = query.filter(ExamTemplate.name == template_name)
        
    reg_data = query.first()
    if not reg_data:
         return jsonify({'error': 'Registration not found'}), 404
         
    reg, template = reg_data
    
    questions = Question.query.filter_by(exam_template_id=template.id).all()
    q_ids = [q.id for q in questions]
    scores = Score.query.filter(
        Score.student_id == student_id,
        Score.question_id.in_(q_ids)
    ).all()
    
    # Calculate Module Performance
    module_stats = {}
    total_score = 0
    max_score = 0
    
    for q in questions:
        module = q.module or 'General'
        if module not in module_stats:
            module_stats[module] = {'got': 0, 'total': 0}
        
        module_stats[module]['total'] += q.score
        max_score += q.score
        
        # Find score
        s = next((x for x in scores if x.question_id == q.id), None)
        if s:
            module_stats[module]['got'] += s.score
            total_score += s.score
            
    # Generate Comment
    comment_parts = []
    
    # Part 1: Overall
    percentage = (total_score / max_score * 100) if max_score > 0 else 0
    if percentage >= 90:
        intro = f"{student.name}同学在本次{template.name}测评中表现卓越，总分达到了{total_score}分（满分{max_score}分）。"
    elif percentage >= 80:
        intro = f"{student.name}同学在本次{template.name}测评中表现优异，基础扎实，总分为{total_score}分。"
    elif percentage >= 60:
        intro = f"{student.name}同学在本次{template.name}测评中顺利完成考试，总分为{total_score}分，仍有进步空间。"
    else:
        intro = f"{student.name}同学在本次{template.name}测评中表现有待提高，总分为{total_score}分，建议加强基础练习。"
    comment_parts.append(intro)
    
    # Part 2: Module Analysis
    strong_modules = []
    weak_modules = []
    
    for mod, stats in module_stats.items():
        if stats['total'] > 0:
            mod_pct = (stats['got'] / stats['total']) * 100
            if mod_pct >= 85:
                strong_modules.append(mod)
            elif mod_pct < 60:
                weak_modules.append(mod)
                
    if strong_modules:
        comment_parts.append(f"在{', '.join(strong_modules)}模块上掌握得非常好，展现了深厚的理解能力。")
        
    if weak_modules:
        comment_parts.append(f"建议后续重点复习{', '.join(weak_modules)}相关知识点，通过针对性练习填补知识盲区。")
        
    # Part 3: Encouragement
    encourage = "希望在未来的学习中继续保持热情，取得更大的突破！"
    comment_parts.append(encourage)
    
    generated_comment = "".join(comment_parts)
    
    return jsonify({'comment': generated_comment})

def generate_report_card_pdf(student_id, exam_session_id, template_id=None):
    """生成学生成绩单PDF - Refactored v9 (Compact Layout)"""
    try:
        # 注册中文字体
        try:
            pdfmetrics.registerFont(TTFont('DroidSansFallback', '/usr/share/fonts/google-droid/DroidSansFallback.ttf'))
            font_name = 'DroidSansFallback'
        except Exception:
            font_name = 'Helvetica' # Fallback
            
        # 获取学生信息
        student = Student.query.get(student_id)
        if not student:
            student = Student.query.filter_by(student_id=str(student_id)).first()
            
        if not student:
            print(f"Student not found: {student_id}")
            return None
            
        # 获取考试场次信息
        exam_session = ExamSession.query.get(exam_session_id)
        
        # 获取该场次下该学生的所有报名信息
        query = db.session.query(ExamRegistration, ExamTemplate, Subject)\
            .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
            .join(Subject, ExamTemplate.subject_id == Subject.id)\
            .filter(ExamRegistration.student_id == student.id)\
            .filter(ExamRegistration.exam_session_id == exam_session_id)
            
        if template_id:
            query = query.filter(ExamTemplate.id == template_id)
            
        registrations = query.all()
        
        if not registrations:
            return None
            
        # 创建PDF
        buffer = io.BytesIO()
        # Reduce margins
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=15*mm, leftMargin=15*mm,
                              topMargin=15*mm, bottomMargin=15*mm)
        
        story = []
        styles = getSampleStyleSheet()
        
        # --- Styles v9 ---
        
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Title'],
            fontName=font_name,
            fontSize=22, # Slightly smaller
            leading=26,
            alignment=1, 
            spaceAfter=6 # Reduced
        )
        
        heading_style = ParagraphStyle(
            'ReportHeading',
            parent=styles['Heading3'],
            fontName=font_name,
            fontSize=13, # Slightly smaller
            textColor=colors.HexColor('#333333'),
            borderPadding=0,
            spaceBefore=10, # Reduced
            spaceAfter=5
        )
        
        normal_style = ParagraphStyle(
            'ReportNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leading=13
        )
        
        small_style = ParagraphStyle(
            'ReportSmall',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            leading=11
        )
        
        # Table Content - Keep small 8pt
        table_content_style = ParagraphStyle(
            'TableContent',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            leading=10,
            alignment=1 
        )
        
        # Header Left - Smaller
        header_left_style = ParagraphStyle(
            'HeaderLeft',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9, # Reduced from 11
            alignment=0 
        )
        
        # Header Center - Smaller
        header_center_style = ParagraphStyle(
            'HeaderCenter',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=14, # Reduced from 16
            alignment=1 
        )
        
        # Settings
        setting = SystemSetting.query.first()
        system_company_name_zh = setting.company_name_zh if setting else '橡心国际'
        system_logo_path = setting.logo_path if setting else None
        
        header_left_text = exam_session.exam_name_en or 'Way To Future'
        header_middle_text = exam_session.company_brand or system_company_name_zh
        
        # Logo - Smaller
        header_right_logo = ''
        if system_logo_path:
             abs_logo_path = os.path.join(app.static_folder, system_logo_path)
             if os.path.exists(abs_logo_path):
                 try:
                     img = Image(abs_logo_path)
                     img_height = 20*mm # Reduced from 25
                     img.drawHeight = img_height
                     img.drawWidth = img_height * (img.imageWidth / img.imageHeight)
                     header_right_logo = img
                 except:
                     pass

        for exam_reg, template, subject in registrations:
            if exam_reg != registrations[0][0]:
                story.append(PageBreak())
                
            # --- Header (Compact) ---
            header_data = [[
                Paragraph(header_left_text, header_left_style), 
                Paragraph(header_middle_text, header_center_style), 
                header_right_logo
            ]]
            
            # Reduce row height
            header_table = Table(header_data, colWidths=[55*mm, 70*mm, 55*mm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4), # Reduced padding
                ('TOPPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 8)) # Reduced spacer
            
            # --- Title (Simplified) ---
            story.append(Paragraph("测评报告", title_style))
            story.append(Spacer(1, 8))
            
            # --- Basic Info ---
            basic_info_data = [
                [
                    Paragraph(f"<b>考生姓名：</b> {student.name}", normal_style),
                    Paragraph(f"<b>测评名称：</b> {template.name}", normal_style),
                    Paragraph(f"<b>测评时间：</b> {exam_session.exam_date.strftime('%Y-%m-%d')}", normal_style)
                ]
            ]
            
            basic_info_table = Table(basic_info_data, colWidths=[60*mm, 60*mm, 60*mm])
            basic_info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(basic_info_table)
            
            # --- Analysis ---
            story.append(Paragraph("测评分析", heading_style))
            
            questions = Question.query.filter_by(exam_template_id=template.id).all()
            
            def natural_sort_key(q):
                import re
                parts = re.split(r'(\d+)', q.question_number)
                return [int(p) if p.isdigit() else p for p in parts]
            questions.sort(key=natural_sort_key)
            
            q_ids = [q.id for q in questions]
            scores_map = {} 
            if q_ids:
                found_scores = Score.query.filter(
                    Score.student_id == student.id,
                    Score.question_id.in_(q_ids)
                ).all()
                scores_map = {s.question_id: s for s in found_scores}
            
            detail_rows = []
            total_score = 0
            correct_count = 0
            
            for q in questions:
                score_obj = scores_map.get(q.id)
                if score_obj:
                    is_correct_text = '正确' if score_obj.is_correct else '错误'
                    color = colors.green if score_obj.is_correct else colors.red
                    if score_obj.is_correct:
                        correct_count += 1
                    total_score += float(score_obj.score)
                else:
                    # User requested empty value if not graded
                    is_correct_text = '' 
                    color = colors.black
                
                kp = q.knowledge_point or '' # User wants correct content, assuming empty if None
                module_text = q.module or ''
                
                detail_rows.append([
                    Paragraph(f"Q{q.question_number}", table_content_style),
                    Paragraph(module_text, table_content_style),
                    Paragraph(kp, table_content_style),
                    Paragraph(f'<font color="{color}">{is_correct_text}</font>', table_content_style)
                ])

            mid = (len(detail_rows) + 1) // 2
            left_data = detail_rows[:mid]
            right_data = detail_rows[mid:]
            
            while len(right_data) < len(left_data):
                right_data.append(['', '', '', ''])
                
            header_row = ['题号', '模块', '知识点', '结果', '', '题号', '模块', '知识点', '结果']
            
            table_data = [header_row]
            for l, r in zip(left_data, right_data):
                table_data.append(l + [''] + r)
                
            col_w = [10*mm, 18*mm, 47*mm, 12*mm]
            gap_w = 6*mm
            full_col_widths = col_w + [gap_w] + col_w
            
            detail_table = Table(table_data, colWidths=full_col_widths, repeatRows=1)
            detail_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#E8F4FC')),
                ('BACKGROUND', (5, 0), (8, 0), colors.HexColor('#E8F4FC')),
                ('GRID', (0, 0), (3, -1), 0.5, colors.grey),
                ('GRID', (5, 0), (8, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(detail_table)
            story.append(Spacer(1, 8))
            
            # --- Analysis Summary ---
            total_questions = len(questions)
            incorrect_count = total_questions - correct_count
            accuracy_pct = (correct_count / total_questions * 100) if total_questions > 0 else 0
            
            analysis_data = [
                ['测评总题数', '正确题数', '错误题数', '正确率'],
                [str(total_questions), str(correct_count), str(incorrect_count), f"{accuracy_pct:.1f}%"]
            ]
            
            analysis_table = Table(analysis_data, colWidths=[45*mm]*4)
            analysis_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8F4FC')), 
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(analysis_table)
            story.append(Spacer(1, 15))
            
            # --- Teacher Comment (Conditional Page Break) ---
            # Instead of forcing page break, we let it flow. 
            # But we want to ensure it doesn't break awkwardly.
            # KeepTogether might be complex here, so we'll just check if we want to force it?
            # User wants "Control within 2 pages (1 sheet duplex)".
            # If the table is long, it might push comment to 3rd page.
            # Let's try to keep it compact.
            
            # story.append(PageBreak()) # Removed forced break to save space if possible
            
            # Check if we need a break? Hard to know current position.
            # But "3. 测评评价区域缩小到页面三分之一" (approx 90-100mm)
            # If we just append, it might fit on page 2 bottom.
            
            story.append(Paragraph("测评评价", heading_style))
            
            report_card = ReportCard.query.filter_by(registration_id=exam_reg.id).first()
            comment_text = ""
            if report_card and (report_card.teacher_comment or report_card.ai_comment):
                comment_text = report_card.teacher_comment or report_card.ai_comment
            
            # Reduced height: 90mm (approx 1/3 page)
            comment_data = [[Paragraph(comment_text, normal_style)]]
            comment_table = Table(comment_data, colWidths=[180*mm], rowHeights=[90*mm])
            comment_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(comment_table)
            
            # Footer
            story.append(Spacer(1, 8))
            footer_text = f"{header_left_text} | {header_middle_text}"
            story.append(Paragraph(footer_text, small_style))
            
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"生成PDF错误: {e}")
        import traceback
        traceback.print_exc()
        return None
@app.route('/pdf/report-card/<student_id>/<exam_session_id>')
def pdf_report_card(student_id, exam_session_id):
    """生成并下载成绩单PDF"""
    template_id = request.args.get('template_id')
    pdf_buffer = generate_report_card_pdf(student_id, exam_session_id, template_id)
    
    if pdf_buffer:
        student = Student.query.get(student_id)
        if not student:
            student = Student.query.filter_by(student_id=str(student_id)).first()
            
        if student:
            filename = f"成绩单_{student.name}_{student.student_id}_{exam_session_id}.pdf"
        else:
            filename = f"成绩单_{student_id}_{exam_session_id}.pdf"
        
        # 检查是否为下载请求
        action = request.args.get('action', 'preview')
        as_attachment = (action == 'download')
        
        return send_file(
            pdf_buffer,
            as_attachment=as_attachment,
            download_name=filename,
            mimetype='application/pdf'
        )
    else:
        return "生成PDF失败", 500

def generate_batch_zip(tasks, zip_name):
    """
    Helper to generate ZIP with PDFs.
    tasks: list of dict {'student_id': int, 'session_id': int, 'template_id': int|None, 'filename': str}
    """
    import zipfile
    import tempfile
    
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, zip_name)
    
    error_log = []
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for task in tasks:
            try:
                pdf_buffer = generate_report_card_pdf(task['student_id'], task['session_id'], task.get('template_id'))
                if pdf_buffer:
                    # Sanitize filename
                    safe_filename = "".join([c for c in task['filename'] if c.isalnum() or c in (' ', '.', '_', '-')]).strip()
                    if not safe_filename.endswith('.pdf'):
                        safe_filename += '.pdf'
                        
                    pdf_path = os.path.join(temp_dir, safe_filename)
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    zipf.write(pdf_path, safe_filename)
                    os.remove(pdf_path)
                else:
                    error_log.append(f"Failed to generate (No Data): {task['filename']}")
            except Exception as e:
                error_log.append(f"Error generating {task['filename']}: {str(e)}")
                
        if error_log:
            error_path = os.path.join(temp_dir, "error_log.txt")
            with open(error_path, "w") as f:
                f.write("\n".join(error_log))
            zipf.write(error_path, "error_log.txt")
            os.remove(error_path)
            
    return zip_path

import shutil

def cleanup_temp_dir(path):
    try:
        # Check if it's a file, get parent dir
        if os.path.isfile(path):
            parent_dir = os.path.dirname(path)
            # Verify it is indeed a temp dir (simple check: name starts with tmp or inside /tmp)
            # But generate_batch_zip uses tempfile.mkdtemp() which creates unique random dirs.
            # We assume the parent dir contains ONLY this zip and error logs created by us.
            shutil.rmtree(parent_dir)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"Error cleaning up temp dir: {e}")

@app.route('/pdf/batch-report-cards/<exam_session_id>')
@login_required
def pdf_batch_report_cards(exam_session_id):
    """批量生成成绩单PDF (按场次)"""
    try:
        session = ExamSession.query.get_or_404(exam_session_id)
        # Get all students in this session (distinct)
        # We need to find students who have at least one registration in this session
        registrations = db.session.query(ExamRegistration.student_id).filter_by(exam_session_id=exam_session_id).distinct().all()
        student_ids = [r[0] for r in registrations]
        
        if not student_ids:
            return "没有找到学生记录", 404
            
        tasks = []
        students = Student.query.filter(Student.id.in_(student_ids)).all()
        student_map = {s.id: s for s in students}
        
        for s_id in student_ids:
            student = student_map.get(s_id)
            if student:
                tasks.append({
                    'student_id': s_id,
                    'session_id': exam_session_id,
                    'template_id': None, # All subjects
                    'filename': f"{student.name}_{student.student_id}.pdf"
                })
        
        zip_path = generate_batch_zip(tasks, f'Batch_Session_{session.name}.zip')
        
        @flask.after_this_request
        def remove_file(response):
            cleanup_temp_dir(zip_path)
            return response
            
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f'批量成绩单_{session.name}.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        return f"批量生成失败: {str(e)}", 500

@app.route('/pdf/batch-report-cards/template/<int:template_id>')
@login_required
def pdf_batch_report_cards_by_template(template_id):
    """批量生成成绩单PDF (按试卷)"""
    try:
        template = ExamTemplate.query.get_or_404(template_id)
        registrations = ExamRegistration.query.filter_by(exam_template_id=template_id).all()
        
        if not registrations:
            return "没有找到学生记录", 404
            
        tasks = []
        for reg in registrations:
            student = Student.query.get(reg.student_id)
            if student:
                tasks.append({
                    'student_id': student.id,
                    'session_id': reg.exam_session_id,
                    'template_id': template_id,
                    'filename': f"{student.name}_{student.student_id}_{template.name}.pdf"
                })
                
        zip_path = generate_batch_zip(tasks, f'Batch_Template_{template.name}.zip')
        
        @flask.after_this_request
        def remove_file(response):
            cleanup_temp_dir(zip_path)
            return response

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f'批量成绩单_试卷_{template.name}.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        return f"批量生成失败: {str(e)}", 500

@app.route('/pdf/batch-report-cards/student/<int:student_id>')
@login_required
def pdf_batch_report_cards_by_student(student_id):
    """批量生成成绩单PDF (按学生)"""
    try:
        student = Student.query.get_or_404(student_id)
        # Find all sessions the student participated in
        regs = ExamRegistration.query.filter_by(student_id=student_id).all()
        session_ids = list(set([r.exam_session_id for r in regs]))
        
        if not session_ids:
            return "该学生没有考试记录", 404
            
        tasks = []
        for sess_id in session_ids:
            session = ExamSession.query.get(sess_id)
            if session:
                tasks.append({
                    'student_id': student_id,
                    'session_id': sess_id,
                    'template_id': None, # All subjects in that session
                    'filename': f"{session.name}_{session.exam_date}.pdf"
                })
                
        zip_path = generate_batch_zip(tasks, f'Batch_Student_{student.name}.zip')
        
        @flask.after_this_request
        def remove_file(response):
            cleanup_temp_dir(zip_path)
            return response

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f'批量成绩单_{student.name}.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        return f"批量生成失败: {str(e)}", 500

@app.route('/api/pdf/batch-selected', methods=['POST'])
@login_required
def api_pdf_batch_selected():
    """批量生成选中的成绩单PDF"""
    data = request.get_json()
    items = data.get('items', [])
    
    if not items:
        return jsonify({'success': False, 'message': '未选择任何记录'}), 400
        
    try:
        tasks = []
        for item in items:
            student = Student.query.get(item['student_id'])
            template = ExamTemplate.query.get(item.get('template_id')) if item.get('template_id') else None
            
            if student:
                filename = f"{student.name}_{student.student_id}"
                if template:
                    filename += f"_{template.name}"
                filename += ".pdf"
                
                tasks.append({
                    'student_id': item['student_id'],
                    'session_id': item['session_session_id'] if 'session_session_id' in item else item['exam_session_id'], # Handle potential key naming
                    'template_id': item.get('template_id'),
                    'filename': filename
                })
        
        zip_path = generate_batch_zip(tasks, f'Batch_Selected_{len(tasks)}_Items.zip')
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f'批量导出_{len(tasks)}项.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        print(f"Batch generation error: {e}")
        return jsonify({'success': False, 'message': f'生成失败: {str(e)}'}), 500

@app.route('/api/pdf/batch-export-by-student/<int:student_id>', methods=['GET'])
@login_required
def api_batch_export_by_student(student_id):
    """B2.2: Export all report cards for a student"""
    student = Student.query.get_or_404(student_id)
    registrations = ExamRegistration.query.filter_by(student_id=student_id).all()
    
    if not registrations:
        return jsonify({'success': False, 'message': '该考生无报考记录'}), 404

    tasks = []
    for reg in registrations:
            template_name = reg.exam_template.name if reg.exam_template else 'Unknown'
            filename = f"{student.name}_{template_name}.pdf"
            tasks.append({
            'student_id': student.id,
            'session_id': reg.exam_session_id,
            'template_id': reg.exam_template_id,
            'filename': filename
            })
    
    zip_path = generate_batch_zip(tasks, f'{student.name}_All_ReportCards.zip')
    return send_file(zip_path, as_attachment=True, download_name=f'{student.name}_全部成绩单.zip', mimetype='application/zip')

@app.route('/api/pdf/batch-export-by-template/<int:template_id>', methods=['GET'])
@login_required
def api_batch_export_by_template(template_id):
    """B2.3: Export all report cards for a template"""
    template = ExamTemplate.query.get_or_404(template_id)
    registrations = ExamRegistration.query.filter_by(exam_template_id=template_id).all()
    
    if not registrations:
        return jsonify({'success': False, 'message': '该试卷无报考记录'}), 404
        
    tasks = []
    for reg in registrations:
            student = reg.student
            if student:
                filename = f"{student.name}_{student.student_id}.pdf"
                tasks.append({
                'student_id': student.id,
                'session_id': reg.exam_session_id,
                'template_id': template.id,
                'filename': filename
                })
                
    zip_path = generate_batch_zip(tasks, f'{template.name}_All_ReportCards.zip')
    return send_file(zip_path, as_attachment=True, download_name=f'{template.name}_全部成绩单.zip', mimetype='application/zip')

@app.route('/api/pdf/batch-export-all', methods=['GET'])
@login_required
def api_batch_export_all_pdfs():
    """B2.4: Export ALL report cards in system"""
    registrations = ExamRegistration.query.all()
    if not registrations:
            return jsonify({'success': False, 'message': '系统无任何报考记录'}), 404
            
    tasks = []
    for reg in registrations:
            student = reg.student
            template = reg.exam_template
            if student and template:
                filename = f"{student.name}_{template.name}.pdf"
                tasks.append({
                'student_id': student.id,
                'session_id': reg.exam_session_id,
                'template_id': template.id,
                'filename': filename
                })
                
    zip_path = generate_batch_zip(tasks, f'All_ReportCards_Full_Backup.zip')
    return send_file(zip_path, as_attachment=True, download_name=f'全量成绩单备份.zip', mimetype='application/zip')

@app.route('/api/report-cards')
def api_report_cards():
    """获取成绩单列表"""
    page = int(request.args.get('page', 1))
    pageSize = int(request.args.get('pageSize', 20))
    exam_session_id = request.args.get('examSessionId')
    grade = request.args.get('grade')
    subject = request.args.get('subject')
    status = request.args.get('status')
    template_id = request.args.get('templateId')
    
    # 构建查询
    query = db.session.query(
        Student.id.label('student_pk'),
        Student.student_id,
        Student.name.label('student_name'),
        Student.grade_level,
        School.name.label('school_name'),
        ExamSession.id.label('exam_session_id'),
        ExamSession.name.label('exam_session_name'),
        Subject.name.label('subject_name'),
        Subject.total_score.label('max_score'),
        ExamTemplate.id.label('template_id')
    ).join(School, Student.school_id == School.id)\
     .join(ExamRegistration, Student.id == ExamRegistration.student_id)\
     .join(ExamSession, ExamRegistration.exam_session_id == ExamSession.id)\
     .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
     .join(Subject, ExamTemplate.subject_id == Subject.id)
    
    # 应用筛选条件
    if template_id:
        query = query.filter(ExamTemplate.id == template_id)
    if exam_session_id:
        query = query.filter(ExamSession.id == exam_session_id)
    if grade:
        query = query.filter(Student.grade_level == grade)
    if subject:
        query = query.filter(Subject.name == subject)
    
    # 分页
    offset = (page - 1) * pageSize
    total = query.count()
    results = query.offset(offset).limit(pageSize).all()
    
    report_cards = []
    
    for result in results:
        # 获取分数统计
        scores = db.session.query(Score, Question)\
            .join(Question, Score.question_id == Question.id)\
            .join(Subject, Question.subject_id == Subject.id)\
            .filter(Score.student_id == result.student_pk)\
            .filter(Subject.id == Subject.query.filter_by(name=result.subject_name).first().id)\
            .all()
        
        total_score = sum(float(score.score) for score, question in scores)
        correct_count = sum(1 for score, question in scores if score.is_correct)
        total_count = len(scores)
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        
        # 确定状态
        if total_count == 0:
            status_result = 'pending'
        elif correct_count == total_count:
            status_result = 'completed'
        else:
            status_result = 'partial'
        
        # 应用状态筛选
        if status and status_result != status:
            continue
        
        report_cards.append({
            'studentId': result.student_pk,
            'studentName': result.student_name,
            'studentIdNum': result.student_id,
            'grade': result.grade_level,
            'schoolName': result.school_name,
            'examSessionId': result.exam_session_id,
            'examSessionName': result.exam_session_name,
            'subjectName': result.subject_name,
            'totalScore': round(total_score, 1),
            'maxScore': result.max_score,
            'accuracy': round(accuracy, 1),
            'status': status_result,
            'correctCount': correct_count,
            'totalCount': total_count,
            'templateId': result.template_id
        })
    
    return jsonify({
        'reportCards': report_cards,
        'currentPage': page,
        'totalPages': (total + pageSize - 1) // pageSize,
        'totalCount': total
    })

@app.route('/api/exam-sessions/create', methods=['POST'])
@login_required
def api_create_exam_session():
    data = request.get_json()
    try:
        new_session = ExamSession(
            name=data['name'],
            exam_date=datetime.strptime(data['exam_date'], '%Y-%m-%d').date(),
            session_type=data['session_type'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            location=data.get('location', ''),
            status=data.get('status', 'draft'),
            exam_name_en=data.get('exam_name_en'),
            company_brand=data.get('company_brand')
        )
        db.session.add(new_session)
        db.session.commit()
        return jsonify({'success': True, 'message': '考试场次创建成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/exam-sessions/<int:id>', methods=['PUT'])
@login_required
def api_update_exam_session(id):
    session = ExamSession.query.get_or_404(id)
    data = request.get_json()
    try:
        session.name = data['name']
        session.exam_date = datetime.strptime(data['exam_date'], '%Y-%m-%d').date()
        session.session_type = data['session_type']
        session.start_time = data['start_time']
        session.end_time = data['end_time']
        session.location = data.get('location', session.location)
        session.status = data.get('status', session.status)
        session.exam_name_en = data.get('exam_name_en', session.exam_name_en)
        session.company_brand = data.get('company_brand', session.company_brand)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '考试场次更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/exam-sessions/<int:id>', methods=['DELETE'])
@login_required
def api_delete_exam_session(id):
    session = ExamSession.query.get_or_404(id)
    try:
        # Check dependencies
        # 1. Check templates
        # Since ExamTemplate.sessions is M2M, we need to check if this session is associated with any template.
        # However, checking the ExamTemplate table directly might be tricky if it's M2M.
        # But wait, ExamTemplate has 'sessions' relationship.
        # Let's check the association table 'exam_template_sessions' indirectly via relationship.
        
        # Or simpler:
        template_count = 0
        # If using backref 'templates' on ExamSession (defined in ExamTemplate)
        if hasattr(session, 'templates'):
             template_count = len(session.templates)
        
        if template_count > 0:
             return jsonify({
                'success': False, 
                'message': f'无法删除：该场次关联了 {template_count} 个试卷模板，请先解除关联。'
            }), 400

        # 2. Check registrations
        reg_count = ExamRegistration.query.filter_by(exam_session_id=id).count()
        if reg_count > 0:
            return jsonify({
                'success': False, 
                'message': f'无法删除：该场次已有 {reg_count} 条报考记录，请先移除这些记录。'
            }), 400
            
        db.session.delete(session)
        db.session.commit()
        return jsonify({'success': True, 'message': '考试场次删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/students/create', methods=['POST'])
@login_required
def api_create_student():
    data = request.get_json()
    
    # Generate Student ID if empty
    student_id = data.get('student_id')
    if not student_id:
        import time
        import random
        # Simple generation logic: 'S' + timestamp last 8 digits + random 2
        student_id = f"S{int(time.time())}{random.randint(10,99)}"

    # Check if student ID exists (only if provided manually, but we auto-gen now if empty)
    if data.get('student_id') and Student.query.filter_by(student_id=student_id).first():
        return jsonify({'success': False, 'message': '学号已存在'}), 400

    # Handle School (Select or Create)
    school_name = data.get('school_name')
    if not school_name:
        return jsonify({'success': False, 'message': '必须填写学校名称'}), 400
        
    school = School.query.filter_by(name=school_name).first()
    if not school:
        # Auto create school
        import uuid
        code = f"SCH_{uuid.uuid4().hex[:6].upper()}"
        school = School(name=school_name, code=code)
        db.session.add(school)
        db.session.commit()

    try:
        new_student = Student(
            student_id=student_id,
            name=data['name'],
            gender=data['gender'],
            grade_level=data['grade_level'],
            school_id=school.id,
            class_name=data.get('class_name', '')
        )
        db.session.add(new_student)
        db.session.commit()
        return jsonify({'success': True, 'message': '学生创建成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/students/registration-options')
@login_required
def api_student_registration_options():
    sessions = ExamSession.query.order_by(ExamSession.exam_date.desc()).all()
    result = []
    
    for s in sessions:
        # Use the backref 'templates' from the M2M relationship
        s_templates = s.templates
        
        templates_data = [{
            'id': t.id,
            'name': t.name,
            'subject_name': t.subject.name if t.subject else ''
        } for t in s_templates]
        
        result.append({
            'id': s.id,
            'name': s.name,
            'templates': templates_data
        })
        
    return jsonify(result)

@app.route('/api/students/<int:id>', methods=['GET'])
@login_required
def api_get_student_detail(id):
    student = Student.query.get_or_404(id)
    regs = []
    for r in student.registrations:
        regs.append({
            'session_id': r.exam_session_id,
            'template_id': r.exam_template_id,
            'session_name': r.exam_session.name if r.exam_session else '',
            'template_name': r.exam_template.name if r.exam_template else ''
        })
    
    data = student.to_dict()
    data['registrations'] = regs
    return jsonify(data)

@app.route('/api/students/<int:id>', methods=['PUT'])
@login_required
def api_update_student(id):
    try:
        student = Student.query.get(id)
        if not student:
            return jsonify({'success': False, 'message': '学生不存在'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '无效的数据格式'}), 400

        # Update logic...
        # If student_id changed, check uniqueness
        new_sid = data.get('student_id')
        if new_sid and new_sid != student.student_id:
             if Student.query.filter_by(student_id=new_sid).first():
                 return jsonify({'success': False, 'message': '学号已存在'}), 400
             student.student_id = new_sid
        
        student.name = data['name']
        student.gender = data['gender']
        student.grade_level = data['grade_level']
        student.class_name = data.get('class_name', student.class_name)
        
        if 'school_name' in data:
            school = School.query.filter_by(name=data['school_name']).first()
            if not school:
                 # Auto create school if needed or handle error
                 import uuid
                 code = f"SCH_{uuid.uuid4().hex[:6].upper()}"
                 school = School(name=data['school_name'], code=code)
                 db.session.add(school)
                 db.session.commit()
            student.school_id = school.id
            
        # Handle Registrations
        if 'registrations' in data:
            # Expected format: [{'session_id': 1, 'template_ids': [1, 2]}, ...]
            new_regs = set()
            for item in data['registrations']:
                s_id = int(item['session_id'])
                for t_id in item.get('template_ids', []):
                    new_regs.add((s_id, int(t_id)))
            
            # Get current regs
            current_regs = ExamRegistration.query.filter_by(student_id=student.id).all()
            current_map = {(r.exam_session_id, r.exam_template_id): r for r in current_regs}
            current_keys = set(current_map.keys())
            
            to_add = new_regs - current_keys
            to_remove = current_keys - new_regs
            
            # Remove (only if no scores)
            for key in to_remove:
                reg = current_map[key]
                # Check for scores
                has_scores = Score.query.join(Question).filter(
                    Score.student_id == student.id,
                    Question.exam_template_id == reg.exam_template_id
                ).first()
                
                if not has_scores:
                    db.session.delete(reg)
            
            # Add
            for s_id, t_id in to_add:
                new_reg = ExamRegistration(
                    student_id=student.id,
                    exam_session_id=s_id,
                    exam_template_id=t_id,
                    attendance_status='present',
                    status='registered'
                )
                db.session.add(new_reg)
                
        db.session.commit()
        return jsonify({'success': True, 'message': '学生信息更新成功'})
    except Exception as e:
        import traceback
        import sys
        error_msg = f"Error in api_update_student: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        
        # Log to file in project root for persistence
        try:
            with open('error_log.txt', 'a') as f:
                f.write(f"[{datetime.now()}] {error_msg}\n")
                f.write(f"Payload: {data if 'data' in locals() else 'None'}\n")
                f.write("-" * 50 + "\n")
        except:
            pass # Fallback if file write fails
            
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/students/<int:id>', methods=['DELETE'])
@login_required
def api_delete_student(id):
    student = Student.query.get_or_404(id)
    try:
        # Check dependencies
        # 1. Check registrations
        registration_count = ExamRegistration.query.filter_by(student_id=id).count()
        if registration_count > 0:
            return jsonify({
                'success': False, 
                'message': f'无法删除：该考生存在 {registration_count} 条报考记录，请先移除这些记录。'
            }), 400
        
        # 2. Check scores
        score_count = Score.query.filter_by(student_id=id).count()
        if score_count > 0:
            return jsonify({
                'success': False, 
                'message': f'无法删除：该考生存在 {score_count} 条成绩记录，请先移除这些记录。'
            }), 400
        
        db.session.delete(student)
        db.session.commit()
        return jsonify({'success': True, 'message': '考生删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# A1: Import functions removed per security requirements
# @app.route('/api/students/import', methods=['POST'])
# def api_import_students():
#     pass

@app.route('/api/exam-sessions')
def api_exam_sessions():
    """获取考试场次列表"""
    sessions = ExamSession.query.order_by(ExamSession.exam_date.desc()).all()
    return jsonify({
        'sessions': [{
            'id': session.id,
            'name': session.name,
            'exam_date': session.exam_date.strftime('%Y-%m-%d'),
            'session_type': session.session_type,
            'status': session.status
        } for session in sessions]
    })

# A1: Import functions removed per security requirements
# @app.route('/api/templates/import', methods=['POST'])
# def api_import_templates():
#     pass

# --- Exam Template Management ---
@app.route('/exam_templates')
@login_required
def exam_templates():
    user_id = session.get('user_id')
    role = session.get('role')
    
    query = ExamTemplate.query
    if role != 'admin':
        query = query.filter(ExamTemplate.creator_id == user_id)
        
    templates = query.all()
    subjects = Subject.query.all()
    sessions = ExamSession.query.order_by(ExamSession.exam_date.desc()).all()
    teachers = User.query.filter((User.role == 'teacher') | (User.role == 'admin')).all()
    return render_template('exam_templates.html', templates=templates, subjects=subjects, sessions=sessions, teachers=teachers)

@app.route('/api/exam_templates', methods=['GET'])
@login_required
def api_get_exam_templates():
    """获取所有试卷模板 (包含场次信息和报名统计)"""
    # Join with Subject only
    results = db.session.query(ExamTemplate, Subject)\
        .join(Subject, ExamTemplate.subject_id == Subject.id)\
        .all()
    
    data = []
    for template, subject in results:
        # Get registration count
        reg_count = ExamRegistration.query.filter_by(exam_template_id=template.id).count()
        
        item = template.to_dict()
        # Enrich with extra info
        item['subject_name'] = subject.name
        item['reg_count'] = reg_count
        
        # Handle multiple sessions
        if template.sessions:
            item['session_name'] = ', '.join([s.name for s in template.sessions])
            # For date and type, we just show the first one or a summary to avoid clutter
            first_session = template.sessions[0]
            item['session_date'] = first_session.exam_date.strftime('%Y-%m-%d') if first_session.exam_date else ''
            item['session_type'] = first_session.session_type
            item['session_type_cn'] = '上午' if first_session.session_type == 'morning' else '下午'
            if len(template.sessions) > 1:
                item['session_date'] += ' 等'
        else:
            item['session_name'] = '未分配场次'
            item['session_date'] = ''
            item['session_type'] = ''
            item['session_type_cn'] = ''
            
        data.append(item)
        
    return jsonify(data)

@app.route('/api/students/quick-register', methods=['POST'])
@login_required
def api_student_quick_register():
    """快速录入学生并报名"""
    data = request.get_json()
    
    # Validation
    required_fields = ['name', 'gender', 'grade_level', 'school_name', 'template_id']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
            
    try:
        # 1. Find or Create School
        school_name = data['school_name']
        school = School.query.filter_by(name=school_name).first()
        if not school:
            # Generate code logic (simple)
            import random
            code = 'SCH' + str(random.randint(1000, 9999))
            school = School(name=school_name, code=code)
            db.session.add(school)
            db.session.flush()
            
        # 2. Find or Create Student
        # Check by Name + School + Grade (Assuming unique enough for quick entry)
        student = Student.query.filter_by(
            name=data['name'],
            school_id=school.id,
            grade_level=data['grade_level']
        ).first()
        
        if not student:
            # Generate student ID
            import time
            sid = 'S' + str(int(time.time()))[-8:] # Simple ID generation
            
            student = Student(
                student_id=sid,
                name=data['name'],
                gender=data['gender'],
                grade_level=data['grade_level'],
                school_id=school.id,
                class_name=data.get('class_name', '')
            )
            db.session.add(student)
            db.session.flush()
            
        # 3. Register
        template_id = data['template_id']
        template = ExamTemplate.query.get(template_id)
        if not template:
             return jsonify({'success': False, 'message': '试卷不存在'}), 404
             
        exists = ExamRegistration.query.filter_by(
            student_id=student.id,
            exam_template_id=template_id
        ).first()
        
        if not exists:
            new_reg = ExamRegistration(
                student_id=student.id,
                exam_template_id=template_id,
                exam_session_id=template.exam_session_id,
                attendance_status='pending'
            )
            db.session.add(new_reg)
            msg = '报名成功'
        else:
            msg = '该学生已报名此试卷'
            
        db.session.commit()
        return jsonify({'success': True, 'message': msg, 'student_id': student.id})
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/exam_templates', methods=['POST'])
@login_required
def api_create_exam_template():
    data = request.get_json()
    try:
        new_template = ExamTemplate(
            name=data['name'],
            subject_id=data['subject_id'],
            grade_level=data['grade_level'],
            total_questions=data.get('total_questions', 0),
            creator_id=data.get('creator_id'),
            grader_id=data.get('grader_id')
        )
        
        # Handle sessions (M2M)
        if 'session_ids' in data and data['session_ids']:
            sessions = ExamSession.query.filter(ExamSession.id.in_(data['session_ids'])).all()
            new_template.sessions = sessions
            # Backward compatibility
            if sessions:
                new_template.exam_session_id = sessions[0].id
        elif 'exam_session_id' in data and data['exam_session_id']:
            # Fallback for legacy single session
            session = ExamSession.query.get(data['exam_session_id'])
            if session:
                new_template.sessions = [session]
                new_template.exam_session_id = session.id
        
        db.session.add(new_template)
        db.session.commit()
        return jsonify({'success': True, 'message': '试卷模板创建成功', 'template': new_template.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/exam_templates/<int:id>', methods=['PUT'])
@login_required
def api_update_exam_template(id):
    template = ExamTemplate.query.get_or_404(id)
    data = request.get_json()
    try:
        template.name = data['name']
        template.subject_id = data['subject_id']
        template.grade_level = data['grade_level']
        
        # Handle sessions (M2M)
        if 'session_ids' in data:
            sessions = ExamSession.query.filter(ExamSession.id.in_(data['session_ids'])).all()
            template.sessions = sessions
            # Backward compatibility
            if sessions:
                template.exam_session_id = sessions[0].id
            else:
                template.exam_session_id = None
        elif 'exam_session_id' in data:
            # Fallback for legacy single session update
            if data['exam_session_id']:
                session = ExamSession.query.get(data['exam_session_id'])
                if session:
                    template.sessions = [session]
                    template.exam_session_id = session.id
            else:
                template.sessions = []
                template.exam_session_id = None

        # total_questions might be auto-calc, but allow edit
        if 'total_questions' in data:
            template.total_questions = data['total_questions']
        
        if 'creator_id' in data:
            template.creator_id = data['creator_id']
        if 'grader_id' in data:
            template.grader_id = data['grader_id']
        
        db.session.commit()
        return jsonify({'success': True, 'message': '试卷模板更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/exam_templates/<int:id>', methods=['DELETE'])
@login_required
def api_delete_exam_template(id):
    template = ExamTemplate.query.get_or_404(id)
    try:
        # Check dependencies (Questions, Registrations)
        # A2: Enhanced protection
        reg_count = ExamRegistration.query.filter_by(exam_template_id=id).count()
        if reg_count > 0:
            return jsonify({
                'success': False, 
                'message': f'无法删除：该试卷已有 {reg_count} 条考试记录，请先移除这些记录。'
            }), 400
            
        # Check scores
        score_count = Score.query.join(Question).filter(Question.exam_template_id == id).count()
        if score_count > 0:
             return jsonify({
                'success': False, 
                'message': f'无法删除：该试卷已有 {score_count} 条成绩记录，请先移除这些记录。'
            }), 400
        
        # Delete associated questions first
        Question.query.filter_by(exam_template_id=id).delete()
        
        db.session.delete(template)
        db.session.commit()
        return jsonify({'success': True, 'message': '试卷模板删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --- Question Management ---
@app.route('/api/exam_templates/<int:id>/questions', methods=['GET'])
@login_required
def api_get_template_questions(id):
    questions = Question.query.filter_by(exam_template_id=id).order_by(Question.id).all()
    return jsonify([q.to_dict() for q in questions])

@app.route('/api/exam_templates/<int:id>/questions', methods=['POST'])
@login_required
def api_add_question(id):
    data = request.get_json()
    try:
        new_question = Question(
            exam_template_id=id,
            question_number=data['question_number'],
            subject_id=data.get('subject_id'), # Optional, usually same as template
            module=data.get('module'),
            knowledge_point=data.get('knowledge_point'),
            score=data['score']
        )
        db.session.add(new_question)
        
        # Update template total questions count
        template = ExamTemplate.query.get(id)
        template.total_questions = Question.query.filter_by(exam_template_id=id).count() + 1
        
        db.session.commit()
        return jsonify({'success': True, 'message': '题目添加成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/questions/<int:id>', methods=['DELETE'])
@login_required
def api_delete_question(id):
    question = Question.query.get_or_404(id)
    template_id = question.exam_template_id
    try:
        db.session.delete(question)
        
        # Update template total questions count
        template = ExamTemplate.query.get(template_id)
        # We need to count again, but since we haven't committed the delete yet, 
        # the count will include the current one unless we commit first or flush.
        # Simplest: commit delete, then count, then update template.
        db.session.commit()
        
        template = ExamTemplate.query.get(template_id)
        template.total_questions = Question.query.filter_by(exam_template_id=template_id).count()
        db.session.commit()
        
        return jsonify({'success': True, 'message': '题目删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/questions/<int:id>', methods=['PUT'])
@login_required
def api_update_question(id):
    question = Question.query.get_or_404(id)
    data = request.get_json()
    try:
        question.question_number = data.get('question_number', question.question_number)
        question.module = data.get('module', question.module)
        question.knowledge_point = data.get('knowledge_point', question.knowledge_point)
        question.score = data.get('score', question.score)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '题目更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --- Registration Management ---

@app.route('/api/registrations', methods=['GET'])
@login_required
def api_get_registrations():
    session_id = request.args.get('session_id')
    template_id = request.args.get('template_id')
    
    query = db.session.query(ExamRegistration, Student, ExamTemplate)\
        .join(Student, ExamRegistration.student_id == Student.id)\
        .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)
        
    if session_id:
        query = query.filter(ExamRegistration.exam_session_id == session_id)
    if template_id:
        query = query.filter(ExamRegistration.exam_template_id == template_id)
        
    results = query.all()
    
    return jsonify([{
        'id': reg.id,
        'student_id': student.id,
        'student_code': student.student_id,
        'student_name': student.name,
        'grade_level': student.grade_level,
        'class_name': student.class_name,
        'template_name': template.name,
        'registration_date': reg.registration_date.strftime('%Y-%m-%d %H:%M')
    } for reg, student, template in results])

@app.route('/api/registrations', methods=['POST'])
@login_required
def api_register_students():
    data = request.get_json()
    template_id = data.get('template_id')
    student_ids = data.get('student_ids', [])
    
    if not template_id or not student_ids:
        return jsonify({'success': False, 'message': '参数缺失'}), 400
        
    template = ExamTemplate.query.get(template_id)
    if not template:
        return jsonify({'success': False, 'message': '试卷模板不存在'}), 404
        
    count = 0
    try:
        for sid in student_ids:
            # Check if already registered
            exists = ExamRegistration.query.filter_by(
                student_id=sid,
                exam_template_id=template_id
            ).first()
            
            if not exists:
                new_reg = ExamRegistration(
                    student_id=sid,
                    exam_template_id=template_id,
                    exam_session_id=template.exam_session_id,
                    attendance_status='pending'
                )
                db.session.add(new_reg)
                count += 1
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'成功报名 {count} 名学生'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/registrations/<int:id>', methods=['DELETE'])
@login_required
def api_delete_registration(id):
    reg = ExamRegistration.query.get_or_404(id)
    try:
        # Check if score exists
        if Score.query.filter_by(student_id=reg.student_id, question_id=Question.query.filter_by(exam_template_id=reg.exam_template_id).first().id if Question.query.filter_by(exam_template_id=reg.exam_template_id).first() else 0).first():
             # Simplistic check: if student has ANY score for questions in this template? 
             # Better: join Score and Question
             pass
             
        db.session.delete(reg)
        db.session.commit()
        return jsonify({'success': True, 'message': '取消报名成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/schools', methods=['GET'])
@login_required
def api_get_schools():
    """获取所有学校列表 (用于自动补全)"""
    schools = School.query.order_by(School.name).all()
    return jsonify([{
        'id': s.id,
        'name': s.name
    } for s in schools])

@app.route('/api/students/available', methods=['GET'])
@login_required
def api_get_available_students():
    """Get students NOT registered for a specific template"""
    template_id = request.args.get('template_id')
    grade_filter = request.args.get('grade')
    
    if not template_id:
        return jsonify([])
        
    # Get registered student IDs
    registered_ids = db.session.query(ExamRegistration.student_id)\
        .filter(ExamRegistration.exam_template_id == template_id)\
        .subquery()
        
    query = Student.query.filter(Student.id.notin_(registered_ids))
    
    if grade_filter:
        query = query.filter(Student.grade_level == grade_filter)
        
    students = query.all()
    
    return jsonify([s.to_dict() for s in students])

# 初始化数据库
@app.before_first_request
def create_tables():
    """创建数据库表"""
    db.create_all()
    
    # 检查并添加缺失的列 (Migration Logic)
    try:
        inspector = inspect(db.engine)
        
        # Check exam_templates columns
        columns_templates = [c['name'] for c in inspector.get_columns('exam_templates')]
        with db.engine.connect() as conn:
            if 'creator_id' not in columns_templates:
                print("Migrating: Adding creator_id to exam_templates")
                conn.execute('ALTER TABLE exam_templates ADD COLUMN creator_id INTEGER REFERENCES users(id)')
            if 'grader_id' not in columns_templates:
                print("Migrating: Adding grader_id to exam_templates")
                conn.execute('ALTER TABLE exam_templates ADD COLUMN grader_id INTEGER REFERENCES users(id)')
                
        # Check users columns
        columns_users = [c['name'] for c in inspector.get_columns('users')]
        with db.engine.connect() as conn:
            if 'english_name' not in columns_users:
                print("Migrating: Adding english_name to users")
                conn.execute('ALTER TABLE users ADD COLUMN english_name VARCHAR(50)')
            if 'real_name' not in columns_users:
                print("Migrating: Adding real_name to users")
                conn.execute('ALTER TABLE users ADD COLUMN real_name VARCHAR(50)')

        # Check exam_registrations columns
        columns_regs = [c['name'] for c in inspector.get_columns('exam_registrations')]
        with db.engine.connect() as conn:
            if 'score' not in columns_regs:
                print("Migrating: Adding score to exam_registrations")
                conn.execute('ALTER TABLE exam_registrations ADD COLUMN score FLOAT')
            if 'status' not in columns_regs:
                print("Migrating: Adding status to exam_registrations")
                conn.execute('ALTER TABLE exam_registrations ADD COLUMN status VARCHAR(20)')
                
    except Exception as e:
        print(f"Migration check failed: {e}")
    
    # 检查并创建默认用户
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("已创建默认管理员账号: admin / admin123")
    
    # 创建初始数据
    if not Subject.query.first():
        create_initial_data()

def create_initial_data():
    """创建初始数据"""
    
    # 创建学校
    schools = [
        School(name='橡心国际小学', code='OX001'),
        School(name='橡心国际初中', code='OX002'),
    ]
    
    for school in schools:
        db.session.add(school)
    
    # 创建科目
    subjects = [
        Subject(name='朗文英语', code='LANGFORD', type='langford', total_score=100),
        Subject(name='牛津英语', code='OXFORD', type='oxford', total_score=100),
        Subject(name='先锋英语', code='PIONEER', type='pioneer', total_score=100),
        Subject(name='中文数学', code='CHINESE_MATH', type='chinese_math', total_score=100),
        Subject(name='英语数学', code='ENGLISH_MATH', type='english_math', total_score=100),
        Subject(name='AMC数学', code='AMC', type='amc', total_score=150),
        Subject(name='袋鼠数学', code='KANGAROO', type='kangaroo', total_score=120),
        Subject(name='小托福', code='TOEFL_JUNIOR', type='toefl_junior', total_score=100),
    ]
    
    for subject in subjects:
        db.session.add(subject)
    db.session.flush()  # 获取科目ID
    
    # 创建G1-G6题目模板
    templates_g1_g6 = [
        # G1 年级模板
        {'name': 'G1朗文英语模板', 'subject_code': 'LANGFORD', 'grade': 'G1', 'questions': 60},
        {'name': 'G1牛津英语模板', 'subject_code': 'OXFORD', 'grade': 'G1', 'questions': 50},
        {'name': 'G1中文数学模板', 'subject_code': 'CHINESE_MATH', 'grade': 'G1', 'questions': 40},
        {'name': 'G1袋鼠数学模板', 'subject_code': 'KANGAROO', 'grade': 'G1', 'questions': 24},
        
        # G2 年级模板
        {'name': 'G2朗文英语模板', 'subject_code': 'LANGFORD', 'grade': 'G2', 'questions': 65},
        {'name': 'G2牛津英语模板', 'subject_code': 'OXFORD', 'grade': 'G2', 'questions': 55},
        {'name': 'G2中文数学模板', 'subject_code': 'CHINESE_MATH', 'grade': 'G2', 'questions': 45},
        {'name': 'G2袋鼠数学模板', 'subject_code': 'KANGAROO', 'grade': 'G2', 'questions': 26},
        
        # G3 年级模板
        {'name': 'G3朗文英语模板', 'subject_code': 'LANGFORD', 'grade': 'G3', 'questions': 70},
        {'name': 'G3牛津英语模板', 'subject_code': 'OXFORD', 'grade': 'G3', 'questions': 60},
        {'name': 'G3先锋英语模板', 'subject_code': 'PIONEER', 'grade': 'G3', 'questions': 65},
        {'name': 'G3中文数学模板', 'subject_code': 'CHINESE_MATH', 'grade': 'G3', 'questions': 50},
        {'name': 'G3英语数学模板', 'subject_code': 'ENGLISH_MATH', 'grade': 'G3', 'questions': 45},
        {'name': 'G3袋鼠数学模板', 'subject_code': 'KANGAROO', 'grade': 'G3', 'questions': 30},
        {'name': 'G3小托福模板', 'subject_code': 'TOEFL_JUNIOR', 'grade': 'G3', 'questions': 80},
        
        # G4 年级模板
        {'name': 'G4朗文英语模板', 'subject_code': 'LANGFORD', 'grade': 'G4', 'questions': 75},
        {'name': 'G4牛津英语模板', 'subject_code': 'OXFORD', 'grade': 'G4', 'questions': 65},
        {'name': 'G4先锋英语模板', 'subject_code': 'PIONEER', 'grade': 'G4', 'questions': 70},
        {'name': 'G4中文数学模板', 'subject_code': 'CHINESE_MATH', 'grade': 'G4', 'questions': 55},
        {'name': 'G4英语数学模板', 'subject_code': 'ENGLISH_MATH', 'grade': 'G4', 'questions': 50},
        {'name': 'G4AMC8模板', 'subject_code': 'AMC', 'grade': 'G4', 'questions': 25},
        {'name': 'G4袋鼠数学模板', 'subject_code': 'KANGAROO', 'grade': 'G4', 'questions': 32},
        {'name': 'G4小托福模板', 'subject_code': 'TOEFL_JUNIOR', 'grade': 'G4', 'questions': 85},
        
        # G5 年级模板
        {'name': 'G5朗文英语模板', 'subject_code': 'LANGFORD', 'grade': 'G5', 'questions': 80},
        {'name': 'G5牛津英语模板', 'subject_code': 'OXFORD', 'grade': 'G5', 'questions': 70},
        {'name': 'G5先锋英语模板', 'subject_code': 'PIONEER', 'grade': 'G5', 'questions': 75},
        {'name': 'G5中文数学模板', 'subject_code': 'CHINESE_MATH', 'grade': 'G5', 'questions': 60},
        {'name': 'G5英语数学模板', 'subject_code': 'ENGLISH_MATH', 'grade': 'G5', 'questions': 55},
        {'name': 'G5AMC8模板', 'subject_code': 'AMC', 'grade': 'G5', 'questions': 25},
        {'name': 'G5袋鼠数学模板', 'subject_code': 'KANGAROO', 'grade': 'G5', 'questions': 36},
        {'name': 'G5小托福模板', 'subject_code': 'TOEFL_JUNIOR', 'grade': 'G5', 'questions': 90},
        
        # G6 年级模板
        {'name': 'G6朗文英语模板', 'subject_code': 'LANGFORD', 'grade': 'G6', 'questions': 85},
        {'name': 'G6牛津英语模板', 'subject_code': 'OXFORD', 'grade': 'G6', 'questions': 75},
        {'name': 'G6先锋英语模板', 'subject_code': 'PIONEER', 'grade': 'G6', 'questions': 80},
        {'name': 'G6中文数学模板', 'subject_code': 'CHINESE_MATH', 'grade': 'G6', 'questions': 65},
        {'name': 'G6英语数学模板', 'subject_code': 'ENGLISH_MATH', 'grade': 'G6', 'questions': 60},
        {'name': 'G6AMC8模板', 'subject_code': 'AMC', 'grade': 'G6', 'questions': 25},
        {'name': 'G6袋鼠数学模板', 'subject_code': 'KANGAROO', 'grade': 'G6', 'questions': 40},
        {'name': 'G6小托福模板', 'subject_code': 'TOEFL_JUNIOR', 'grade': 'G6', 'questions': 95},
    ]
    
    # 创建考试模板
    for template_data in templates_g1_g6:
        subject = Subject.query.filter_by(code=template_data['subject_code']).first()
        if subject:
            template = ExamTemplate(
                name=template_data['name'],
                subject_id=subject.id,
                grade_level=template_data['grade'],
                total_questions=template_data['questions']
            )
            db.session.add(template)
    
    db.session.flush()  # 获取模板ID
    
    # 创建题目模板
    questions_data = []
    
    # 为每个模板生成题目
    for template_data in templates_g1_g6:
        subject = Subject.query.filter_by(code=template_data['subject_code']).first()
        template = ExamTemplate.query.filter_by(name=template_data['name']).first()
        
        if subject and template:
            # 根据科目类型生成不同的题目
            if 'LANGFORD' in template_data['subject_code'] or 'OXFORD' in template_data['subject_code']:
                # 英语题目
                modules = ['听力', '阅读', '语法', '词汇', '写作']
                knowledge_points = ['词汇理解', '语法运用', '阅读理解', '听力理解', '写作表达']
            elif 'CHINESE_MATH' in template_data['subject_code'] or 'ENGLISH_MATH' in template_data['subject_code']:
                # 数学题目
                modules = ['数与代数', '图形与几何', '统计与概率', '解决问题']
                knowledge_points = ['计算能力', '几何直观', '数据分析', '逻辑推理', '空间想象']
            elif 'AMC' in template_data['subject_code'] or 'KANGAROO' in template_data['subject_code']:
                # 竞赛数学
                modules = ['代数', '几何', '数论', '组合', '概率统计']
                knowledge_points = ['方程求解', '几何证明', '数论应用', '组合计数', '概率计算']
            else:
                # 其他科目
                modules = ['基础模块', '进阶模块', '综合应用']
                knowledge_points = ['基础知识', '应用能力', '综合分析']
            
            for i in range(1, template_data['questions'] + 1):
                module = modules[i % len(modules)]
                knowledge_point = knowledge_points[i % len(knowledge_points)]
                score = 100.0 / template_data['questions']  # 平均分配分数
                
                question = Question(
                    question_number=f"Q{i:02d}",
                    subject_id=subject.id,
                    module=module,
                    knowledge_point=knowledge_point,
                    score=round(score, 1)
                )
                questions_data.append(question)
    
    # 批量添加题目
    for question in questions_data:
        db.session.add(question)
    
    # 创建示例考试场次
    exam_session = ExamSession(
        name='2025秋季WTF测评',
        exam_date=date(2025, 12, 27),
        session_type='morning',
        start_time='09:40',
        end_time='11:50',
        status='in_progress',
        location='橡心国际校区'
    )
    
    db.session.add(exam_session)
    db.session.commit()


# --- Exam Session Form Handlers (PC View) ---
@app.route('/exam-sessions/add', methods=['POST'])
@login_required
def handle_exam_add():
    name = request.form.get('name')
    date_str = request.form.get('date')
    
    try:
        exam_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # Create with defaults
        new_session = ExamSession(
            name=name,
            exam_date=exam_date,
            session_type='morning', # Default
            start_time='09:00',
            end_time='11:00',
            status='draft'
        )
        db.session.add(new_session)
        db.session.commit()
        flash('考试场次创建成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'创建失败: {str(e)}', 'danger')
        
    return redirect(url_for('exam_sessions'))

@app.route('/exam-sessions/edit', methods=['POST'])
@login_required
def handle_exam_edit():
    exam_id = request.form.get('exam_id')
    name = request.form.get('name')
    date_str = request.form.get('date')
    
    session = ExamSession.query.get_or_404(exam_id)
    try:
        session.name = name
        session.exam_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        db.session.commit()
        flash('考试场次更新成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失败: {str(e)}', 'danger')
        
    return redirect(url_for('exam_sessions'))

@app.route('/exam-sessions/delete', methods=['POST'])
@login_required
def handle_exam_delete():
    exam_id = request.form.get('exam_id')
    session = ExamSession.query.get_or_404(exam_id)
    try:
        # Check registrations
        if ExamRegistration.query.filter_by(exam_session_id=exam_id).first():
            flash('无法删除：该考试已有学生报名', 'danger')
        else:
            db.session.delete(session)
            db.session.commit()
            flash('考试场次已删除', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')
        
    return redirect(url_for('exam_sessions'))

# --- Data Management & Import/Export ---

@app.route('/data/management')
@login_required
def data_management():
    """数据管理页面"""
    return render_template('data_management.html')

# A1: Import functions removed per security requirements
# @app.route('/data/import/exams', methods=['POST'])
# @login_required
# def import_exams():
#    flash('导入功能已禁用，请联系管理员', 'danger')
#    return redirect(url_for('data_management'))

# @app.route('/data/import/templates', methods=['POST'])
# @login_required
# # def import_templates():
# #     flash('导入功能已禁用，请联系管理员', 'danger')
# #     return redirect(url_for('data_management'))

# @app.route('/data/import/students', methods=['POST'])
# @login_required
# # def import_students():
# #     flash('导入功能已禁用，请联系管理员', 'danger')
# #     return redirect(url_for('data_management'))

# @app.route('/data/import/scores', methods=['POST'])
# @login_required
# def import_scores():
#    flash('导入功能已禁用，请联系管理员', 'danger')
#    return redirect(url_for('data_management'))

@app.route('/data/export/all')
@login_required
def export_all_data():
    """一键全量导出备份"""
    try:
        # 1. Exams
        sessions = ExamSession.query.all()
        df_exams = pd.DataFrame([{
            '名称': s.name, 
            '日期': s.exam_date, 
            '状态': s.status,
            '类型': s.session_type,
            '开始时间': s.start_time,
            '结束时间': s.end_time
        } for s in sessions])
        
        # 2. Templates
        templates = ExamTemplate.query.all()
        df_templates = pd.DataFrame([{
            '模板名称': t.name, 
            '科目': t.subject.name if t.subject else '', 
            '年级': t.grade_level, 
            '题目数': t.total_questions
        } for t in templates])

        # 2.1 Questions (Added)
        questions = Question.query.all()
        df_questions = pd.DataFrame([{
            '试卷名称': q.exam_template.name if q.exam_template else '',
            '题号': q.question_number,
            '模块': q.module,
            '知识点': q.knowledge_point,
            '题型': getattr(q, 'question_type', ''), # Handle potential missing attribute
            '分值': q.score
        } for q in questions])
        
        # 3. Students (Enhanced)
        students = Student.query.all()
        student_data = []
        for s in students:
            # Get registrations info
            regs = ExamRegistration.query.filter_by(student_id=s.id).all()
            reg_details = []
            for r in regs:
                t_name = r.exam_template.name if r.exam_template else 'Unknown'
                s_name = r.exam_session.name if r.exam_session else 'Unknown'
                reg_details.append(f"{s_name} ({t_name})")
            reg_str = "; ".join(reg_details)

            student_data.append({
                '姓名': s.name, 
                '学号': s.student_id, 
                '年级': s.grade_level, 
                '学校': s.school.name if s.school else '',
                '报考详情': reg_str
            })
        df_students = pd.DataFrame(student_data)
        
        # 4. Scores
        regs = ExamRegistration.query.filter(ExamRegistration.score != None).all()
        scores_data = []
        for r in regs:
            if r.student and r.exam_template:
                scores_data.append({
                    '学号': r.student.student_id,
                    '姓名': r.student.name,
                    '试卷名称': r.exam_template.name,
                    '得分': r.score
                })
        df_scores = pd.DataFrame(scores_data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if not df_exams.empty:
                df_exams.to_excel(writer, sheet_name='考试场次', index=False)
            if not df_templates.empty:
                df_templates.to_excel(writer, sheet_name='试卷模板', index=False)
            if not df_questions.empty:
                df_questions.to_excel(writer, sheet_name='题目明细', index=False)
            if not df_students.empty:
                df_students.to_excel(writer, sheet_name='考生信息', index=False)
            if not df_scores.empty:
                df_scores.to_excel(writer, sheet_name='评分记录', index=False)
            
        output.seek(0)
        filename = f"System_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(output, download_name=filename, as_attachment=True)
    except Exception as e:
        flash(f'备份失败: {str(e)}', 'danger')
        return redirect(url_for('data_management'))

@app.route('/data/export/exams')
@login_required
def export_exams():
    try:
        sessions = ExamSession.query.all()
        data = [{'名称': s.name, '日期': s.exam_date, '状态': s.status} for s in sessions]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(output, download_name='exams.xlsx', as_attachment=True)
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'danger')
        return redirect(url_for('data_management'))

@app.route('/data/export/templates')
@login_required
def export_templates():
    try:
        templates = ExamTemplate.query.all()
        # Sheet 1: Templates
        t_data = [{'模板名称': t.name, '科目': t.subject.name if t.subject else '', '年级': t.grade_level, '题目数': t.total_questions} for t in templates]
        df_templates = pd.DataFrame(t_data)

        # Sheet 2: Questions
        q_data = []
        for t in templates:
            questions = Question.query.filter_by(exam_template_id=t.id).order_by(Question.question_number).all()
            for q in questions:
                q_data.append({
                    '试卷名称': t.name,
                    '题号': q.question_number,
                    '模块': q.module,
                    '知识点': q.knowledge_point,
                    '分值': q.score
                })
        df_questions = pd.DataFrame(q_data)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_templates.to_excel(writer, sheet_name='试卷列表', index=False)
            df_questions.to_excel(writer, sheet_name='题目明细', index=False)
        output.seek(0)
        return send_file(output, download_name='templates_with_details.xlsx', as_attachment=True)
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'danger')
        return redirect(url_for('data_management'))

@app.route('/data/export/students')
@login_required
def export_students():
    try:
        students = Student.query.all()
        data = []
        for s in students:
            # Get registrations info
            regs = ExamRegistration.query.filter_by(student_id=s.id).all()
            reg_details = []
            for r in regs:
                t_name = r.exam_template.name if r.exam_template else 'Unknown'
                s_name = r.exam_session.name if r.exam_session else 'Unknown'
                reg_details.append(f"{s_name} ({t_name})")
            reg_str = "; ".join(reg_details)

            data.append({
                '姓名': s.name, 
                '学号': s.student_id, 
                '年级': s.grade_level, 
                '学校': s.school.name if s.school else '',
                '报考详情': reg_str
            })
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(output, download_name='students_with_details.xlsx', as_attachment=True)
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'danger')
        return redirect(url_for('data_management'))

@app.route('/data/export/scores')
@login_required
def export_scores():
    try:
        regs = ExamRegistration.query.filter(ExamRegistration.score != None).all()
        data = []
        for r in regs:
            if r.student and r.exam_template:
                data.append({
                    '学号': r.student.student_id,
                    '姓名': r.student.name,
                    '试卷名称': r.exam_template.name,
                    '得分': r.score
                })
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(output, download_name='scores.xlsx', as_attachment=True)
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'danger')
        return redirect(url_for('data_management'))

# Helper to create zip
def create_batch_zip(pdf_files, error_logs):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in pdf_files:
            # Ensure unique filenames
            if filename in zip_file.namelist():
                base, ext = os.path.splitext(filename)
                counter = 1
                while f"{base}_{counter}{ext}" in zip_file.namelist():
                    counter += 1
                filename = f"{base}_{counter}{ext}"
            zip_file.writestr(filename, content.getvalue())
        
        if error_logs:
            zip_file.writestr('error_log.txt', '\n'.join(error_logs))
            
    zip_buffer.seek(0)
    return zip_buffer

@app.route('/api/export/pdf/student/<int:student_id>')
@login_required
def export_student_pdfs(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Find all sessions the student participated in
    registrations = ExamRegistration.query.filter_by(student_id=student_id).all()
    session_ids = set(r.exam_session_id for r in registrations if r.exam_session_id)
    
    pdf_files = []
    error_logs = []
    
    for session_id in session_ids:
        session_obj = ExamSession.query.get(session_id)
        if not session_obj:
            continue
            
        try:
            pdf_buffer = generate_report_card_pdf(student_id, session_id)
            if pdf_buffer:
                filename = f"{student.name}_{session_obj.name}.pdf"
                pdf_files.append((filename, pdf_buffer))
            else:
                error_logs.append(f"Failed to generate PDF for session: {session_obj.name}")
        except Exception as e:
            error_logs.append(f"Error generating PDF for session {session_obj.name}: {str(e)}")
            
    if not pdf_files and not error_logs:
         return jsonify({'success': False, 'message': '没有找到该考生的考试记录'}), 404

    zip_buffer = create_batch_zip(pdf_files, error_logs)
    from urllib.parse import quote
    filename = f"{student.name}_ReportCards.zip"
    
    # Handle filename encoding for non-ascii
    response = make_response(send_file(
        zip_buffer, 
        as_attachment=True,
        download_name=filename,
        mimetype='application/zip'
    ))
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
    return response

@app.route('/api/export/pdf/template/<int:template_id>')
@login_required
def export_template_pdfs(template_id):
    template = ExamTemplate.query.get_or_404(template_id)
    
    # Find all registrations for this template
    registrations = ExamRegistration.query.filter_by(exam_template_id=template_id).all()
    
    pdf_files = []
    error_logs = []
    
    processed_students = set()
    
    for reg in registrations:
        if reg.student_id in processed_students:
            continue
        processed_students.add(reg.student_id)
        
        student = reg.student
        if not student:
            continue
            
        try:
            # We filter by template_id to get only this exam's result in the PDF
            pdf_buffer = generate_report_card_pdf(reg.student_id, reg.exam_session_id, template_id=template_id)
            if pdf_buffer:
                filename = f"{student.name}_{template.name}.pdf"
                pdf_files.append((filename, pdf_buffer))
            else:
                error_logs.append(f"Failed to generate PDF for student: {student.name}")
        except Exception as e:
            error_logs.append(f"Error generating PDF for student {student.name}: {str(e)}")
            
    if not pdf_files:
         return jsonify({'success': False, 'message': '没有可生成的成绩单'}), 404

    zip_buffer = create_batch_zip(pdf_files, error_logs)
    from urllib.parse import quote
    filename = f"{template.name}_ReportCards.zip"
    
    response = make_response(send_file(
        zip_buffer, 
        as_attachment=True,
        download_name=filename,
        mimetype='application/zip'
    ))
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
    return response

@app.route('/api/export/pdf/all')
@login_required
def export_all_pdfs():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    # Strategy: Group by (Student, Session)
    registrations = ExamRegistration.query.all()
    
    tasks = set()
    for reg in registrations:
        if reg.student_id and reg.exam_session_id:
            tasks.add((reg.student_id, reg.exam_session_id))
            
    pdf_files = []
    error_logs = []
    
    for student_id, session_id in tasks:
        student = Student.query.get(student_id)
        session_obj = ExamSession.query.get(session_id)
        
        if not student or not session_obj:
            continue
            
        try:
            pdf_buffer = generate_report_card_pdf(student_id, session_id)
            if pdf_buffer:
                filename = f"{student.name}_{session_obj.name}.pdf"
                pdf_files.append((filename, pdf_buffer))
            else:
                error_logs.append(f"Failed for {student.name} in {session_obj.name}")
        except Exception as e:
            error_logs.append(f"Error for {student.name} in {session_obj.name}: {str(e)}")

    if not pdf_files:
         return jsonify({'success': False, 'message': '没有可生成的成绩单'}), 404

    zip_buffer = create_batch_zip(pdf_files, error_logs)
    from urllib.parse import quote
    filename = f"All_ReportCards_{datetime.now().strftime('%Y%m%d')}.zip"
    
    response = make_response(send_file(
        zip_buffer, 
        as_attachment=True,
        download_name=filename,
        mimetype='application/zip'
    ))
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
    return response

if __name__ == '__main__':
    # 运行应用
    app.run(host='0.0.0.0', port=8083, debug=True)