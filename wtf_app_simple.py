#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
橡心国际WTF活动管理平台 - 简化版本
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
import io
import hashlib
import pandas as pd
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'wtf-exam-system-secret-key-2023')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wtf_exam_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='teacher')  # admin, teacher

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    grade_level = db.Column(db.String(10), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    class_name = db.Column(db.String(50))
    
    school = db.relationship('School', backref='students')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'gender': self.gender,
            'grade_level': self.grade_level,
            'school_id': self.school_id,
            'school_name': self.school.name if self.school else None,
            'class_name': self.class_name
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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'exam_date': self.exam_date.strftime('%Y-%m-%d') if self.exam_date else None,
            'session_type': self.session_type,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'status': self.status,
            'location': self.location
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

class ExamTemplate(db.Model):
    __tablename__ = 'exam_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    exam_session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'))  # Added link to session
    grade_level = db.Column(db.String(10), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    
    subject = db.relationship('Subject', backref='templates')
    exam_session = db.relationship('ExamSession', backref='templates')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'exam_session_id': self.exam_session_id,
            'exam_session_name': self.exam_session.name if self.exam_session else None,
            'grade_level': self.grade_level,
            'total_questions': self.total_questions
        }

class ExamRegistration(db.Model):
    __tablename__ = 'exam_registrations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    exam_session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'))
    exam_template_id = db.Column(db.Integer, db.ForeignKey('exam_templates.id'))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    attendance_status = db.Column(db.String(20))  # present/absent
    
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

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# 路由定义
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
            return redirect(next_page or url_for('dashboard'))
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
    sessions = ExamSession.query.order_by(ExamSession.exam_date.desc()).all()
    return render_template('exam_sessions.html', sessions=sessions)

@app.route('/students')
@login_required
def students():
    """考生管理"""
    students = db.session.query(Student, School).join(School).all()
    schools = School.query.all()
    return render_template('wtf_students.html', students=students, schools=schools)

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

@app.route('/score-entry')
@login_required
def score_entry():
    """评分录入界面"""
    exam_sessions = ExamSession.query.order_by(ExamSession.exam_date.desc()).all()
    return render_template('score_entry.html', exam_sessions=exam_sessions)

@app.route('/api/students/<exam_session_id>')
def api_students_by_session(exam_session_id):
    """获取指定考试场次的学生列表"""
    grade = request.args.get('grade')
    
    # 查询注册学生
    query = db.session.query(
        Student, School, Subject, ExamTemplate
    ).join(School, Student.school_id == School.id)\
     .join(ExamRegistration, Student.id == ExamRegistration.student_id)\
     .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
     .join(Subject, ExamTemplate.subject_id == Subject.id)\
     .filter(ExamRegistration.exam_session_id == exam_session_id)
    
    if grade:
        query = query.filter(Student.grade_level == grade)
    
    results = query.all()
    
    students = []
    for student, school, subject, template in results:
        students.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': student.name,
            'grade_level': student.grade_level,
            'school_name': school.name,
            'subject_name': subject.name,
            'template_id': template.id
        })
    
    # 获取题目列表（使用第一个学生的模板）
    questions = []
    if students:
        template_id = students[0]['template_id']
        template = ExamTemplate.query.get(template_id)
        if template:
            questions = Question.query.filter_by(subject_id=template.subject_id).all()
            questions = [{
                'id': q.id,
                'question_number': q.question_number,
                'module': q.module,
                'knowledge_point': q.knowledge_point,
                'score': float(q.score)
            } for q in questions]
    
    return jsonify({
        'students': students,
        'questions': questions
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

@app.route('/api/scores/import', methods=['POST'])
@login_required
def api_import_scores():
    """从Excel导入成绩"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '请上传Excel文件'}), 400
        
        file = request.files['file']
        session_id = request.form.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'message': '请选择考试场次'}), 400
            
        try:
            df = pd.read_excel(file, engine='openpyxl')
        except Exception as e:
            return jsonify({'success': False, 'message': f'文件解析失败: {str(e)}'}), 400
        
        # Check required columns
        id_col = None
        for col in df.columns:
            if '学号' in str(col) or 'student_id' in str(col).lower():
                id_col = col
                break
        
        if not id_col:
            return jsonify({'success': False, 'message': '未找到"学号"列 (需包含"学号"或"student_id")'}), 400
            
        success_count = 0
        errors = []
        
        # Pre-fetch questions for this session to avoid repeated queries
        # Assuming all students in session use templates that share questions (or we query per student)
        # To be safe and robust, we query per student's template
        
        for index, row in df.iterrows():
            student_id = str(row[id_col]).strip()
            if not student_id or student_id == 'nan':
                continue

            # Find student
            student = Student.query.filter_by(student_id=student_id).first()
            if not student:
                errors.append(f"行 {index+2}: 找不到学号 {student_id}")
                continue
                
            # Find registration
            reg = ExamRegistration.query.filter_by(
                student_id=student.id,
                exam_session_id=session_id
            ).first()
            
            if not reg:
                errors.append(f"行 {index+2}: 学生 {student.name} ({student_id}) 未报名该场次")
                continue
                
            # Get template and questions
            template = ExamTemplate.query.get(reg.exam_template_id)
            if not template:
                continue
                
            questions = Question.query.filter_by(subject_id=template.subject_id).all()
            q_map = {str(q.question_number): q for q in questions}
            # Also map "Q1" -> "1"
            
            student_scores_added = False
            for col in df.columns:
                col_str = str(col).strip()
                # Try raw, try without Q, try without .0
                keys_to_try = [col_str, col_str.replace('Q', ''), col_str.replace('.0', '')]
                
                q = None
                for k in keys_to_try:
                    if k in q_map:
                        q = q_map[k]
                        break
                
                if q:
                    try:
                        val = row[col]
                        if pd.isna(val): continue
                        
                        score_val = float(val)
                        if 0 <= score_val <= q.score:
                            # Delete existing score for this question
                            Score.query.filter_by(student_id=student.id, question_id=q.id).delete()
                            
                            new_score = Score(
                                student_id=student.id,
                                question_id=q.id,
                                score=score_val,
                                is_correct=(score_val == q.score)
                            )
                            db.session.add(new_score)
                            student_scores_added = True
                    except (ValueError, TypeError):
                        pass
            
            if student_scores_added:
                success_count += 1
                
        db.session.commit()
        
        msg = f"成功导入 {success_count} 名学生的成绩。"
        if errors:
            msg += f" <br>警告 ({len(errors)}条):<br>" + "<br>".join(errors[:5])
            if len(errors) > 5: msg += f"<br>...等共{len(errors)}条"
            
        return jsonify({'success': True, 'message': msg})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f"系统错误: {str(e)}"}), 500

@app.route('/api/scores/save', methods=['POST'])
def api_save_scores():
    """保存学生分数"""
    data = request.get_json()
    student_id = data.get('student_id')
    scores_data = data.get('scores', {})
    
    try:
        # 删除该学生之前的分数记录
        Score.query.filter_by(student_id=student_id).delete()
        
        # 添加新的分数记录
        for question_id, score_value in scores_data.items():
            score = Score(
                student_id=student_id,
                question_id=int(question_id),
                score=float(score_value),
                is_correct=score_value > 0
            )
            db.session.add(score)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/scores/batch-save', methods=['POST'])
def api_batch_save_scores():
    """批量保存学生分数"""
    data = request.get_json()
    scores_data = data.get('scores', [])
    
    try:
        for student_score in scores_data:
            student_id = student_score['student_id']
            scores = student_score['scores']
            
            # 删除之前的分数记录
            Score.query.filter_by(student_id=student_id).delete()
            
            # 添加新的分数记录
            for question_id, score_value in scores.items():
                score = Score(
                    student_id=student_id,
                    question_id=int(question_id),
                    score=float(score_value),
                    is_correct=score_value > 0
                )
                db.session.add(score)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/init-templates', methods=['POST'])
def api_init_templates():
    """初始化题目模板"""
    try:
        # 删除现有模板和题目
        ExamTemplate.query.delete()
        Question.query.delete()
        
        # 重新创建模板和题目
        create_initial_data()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

def generate_report_card_pdf(student_id, exam_session_id):
    """生成学生成绩单PDF"""
    try:
        # 获取学生信息
        student = Student.query.get(student_id)
        if not student:
            return None
            
        # 获取考试场次信息
        exam_session = ExamSession.query.get(exam_session_id)
        
        # 获取注册信息和成绩
        registration = db.session.query(ExamRegistration, ExamTemplate, Subject)\
            .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
            .join(Subject, ExamTemplate.subject_id == Subject.id)\
            .filter(ExamRegistration.student_id == student_id)\
            .filter(ExamRegistration.exam_session_id == exam_session_id)\
            .first()
        
        if not registration:
            return None
            
        exam_reg, template, subject = registration
        
        # 获取分数详情
        scores = db.session.query(Score, Question)\
            .join(Question, Score.question_id == Question.id)\
            .filter(Score.student_id == student_id)\
            .all()
        
        # 创建PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=20*mm, leftMargin=20*mm,
                              topMargin=20*mm, bottomMargin=20*mm)
        
        story = []
        styles = getSampleStyleSheet()
        
        # 标题
        title = Paragraph("橡心国际WTF活动成绩单", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # 学生信息表格
        student_data = [
            ['学生姓名', student.name],
            ['学号', student.student_id],
            ['年级', student.grade_level],
            ['学校', student.school.name if student.school else '-'],
            ['考试场次', exam_session.name if exam_session else '-'],
            ['考试日期', exam_session.exam_date.strftime('%Y-%m-%d') if exam_session else '-'],
            ['考试科目', subject.name],
            ['题目总数', str(template.total_questions)]
        ]
        
        student_table = Table(student_data, colWidths=[60*mm, 80*mm])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(student_table)
        story.append(Spacer(1, 20))
        
        # 成绩详情
        if scores:
            score_title = Paragraph("成绩详情", styles['Heading2'])
            story.append(score_title)
            story.append(Spacer(1, 12))
            
            score_data = [['题号', '模块', '知识点', '得分', '满分', '是否正确']]
            
            total_score = 0
            total_possible = 0
            
            for score, question in scores:
                is_correct = '是' if score.is_correct else '否'
                score_data.append([
                    question.question_number,
                    question.module or '-',
                    question.knowledge_point or '-',
                    str(float(score.score)),
                    str(float(question.score)),
                    is_correct
                ])
                total_score += float(score.score)
                total_possible += float(question.score)
            
            # 添加总分
            score_data.append(['', '', '总分', str(total_score), str(total_possible), f'{(total_score/total_possible*100):.1f}%'])
            
            score_table = Table(score_data, colWidths=[30*mm, 40*mm, 50*mm, 25*mm, 25*mm, 30*mm])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(score_table)
            story.append(Spacer(1, 20))
        
        # 统计信息
        stats_title = Paragraph("统计信息", styles['Heading2'])
        story.append(stats_title)
        story.append(Spacer(1, 12))
        
        # 计算统计数据
        correct_count = sum(1 for score, question in scores if score.is_correct)
        total_count = len(scores)
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        
        stats_data = [
            ['总题数', str(total_count)],
            ['正确题数', str(correct_count)],
            ['错误题数', str(total_count - correct_count)],
            ['正确率', f'{accuracy:.1f}%'],
            ['总分', str(sum(float(score.score) for score, question in scores))],
            ['平均分', f'{sum(float(score.score) for score, question in scores) / total_count:.1f}' if total_count > 0 else '0']
        ]
        
        stats_table = Table(stats_data, colWidths=[60*mm, 40*mm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        print(f"生成PDF错误: {e}")
        return None

@app.route('/pdf/report-card/<student_id>/<exam_session_id>')
def pdf_report_card(student_id, exam_session_id):
    """生成并下载成绩单PDF"""
    pdf_buffer = generate_report_card_pdf(student_id, exam_session_id)
    
    if pdf_buffer:
        student = Student.query.get(student_id)
        filename = f"成绩单_{student.name}_{student_id}_{exam_session_id}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    else:
        return "生成PDF失败", 500

@app.route('/pdf/batch-report-cards/<exam_session_id>')
def pdf_batch_report_cards(exam_session_id):
    """批量生成成绩单PDF"""
    try:
        # 获取考试场次的所有学生
        registrations = db.session.query(ExamRegistration)\
            .filter(ExamRegistration.exam_session_id == exam_session_id)\
            .all()
        
        if not registrations:
            return "没有找到学生记录", 404
        
        # 创建临时ZIP文件
        import zipfile
        import tempfile
        
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f'batch_report_cards_{exam_session_id}.zip')
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for reg in registrations:
                pdf_buffer = generate_report_card_pdf(reg.student_id, exam_session_id)
                if pdf_buffer:
                    student = Student.query.get(reg.student_id)
                    filename = f"成绩单_{student.name}_{student.student_id}.pdf"
                    
                    # 将PDF写入临时文件
                    pdf_path = os.path.join(temp_dir, filename)
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    
                    # 添加到ZIP
                    zipf.write(pdf_path, filename)
                    
                    # 删除临时PDF文件
                    os.remove(pdf_path)
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f'批量成绩单_{exam_session_id}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        print(f"批量生成PDF错误: {e}")
        return "批量生成PDF失败", 500

@app.route('/api/report-cards')
def api_report_cards():
    """获取成绩单列表"""
    page = int(request.args.get('page', 1))
    pageSize = int(request.args.get('pageSize', 20))
    exam_session_id = request.args.get('examSessionId')
    grade = request.args.get('grade')
    subject = request.args.get('subject')
    status = request.args.get('status')
    
    # 构建查询
    query = db.session.query(
        Student.id.label('student_id'),
        Student.student_id,
        Student.name.label('student_name'),
        Student.grade_level,
        School.name.label('school_name'),
        ExamSession.id.label('exam_session_id'),
        ExamSession.name.label('exam_session_name'),
        Subject.name.label('subject_name'),
        Subject.total_score.label('max_score')
    ).join(School, Student.school_id == School.id)\
     .join(ExamRegistration, Student.id == ExamRegistration.student_id)\
     .join(ExamSession, ExamRegistration.exam_session_id == ExamSession.id)\
     .join(ExamTemplate, ExamRegistration.exam_template_id == ExamTemplate.id)\
     .join(Subject, ExamTemplate.subject_id == Subject.id)
    
    # 应用筛选条件
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
            .filter(Score.student_id == result.student_id)\
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
            'studentId': result.student_id,
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
            'totalCount': total_count
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
            status=data.get('status', 'draft')
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
        # Check if there are related registrations
        if ExamRegistration.query.filter_by(exam_session_id=id).first():
            return jsonify({'success': False, 'message': '该场次已有学生报名，无法删除'}), 400
            
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
    try:
        # Check if school exists or create logic
        school_name = data.get('school_name')
        school = None
        if school_name:
            school = School.query.filter_by(name=school_name).first()
            if not school:
                # If school doesn't exist, use the first one as default or handle accordingly
                school = School.query.first()
        
        new_student = Student(
            student_id=data['student_id'],
            name=data['name'],
            gender=data['gender'],
            grade_level=data['grade_level'],
            school_id=school.id if school else None,
            class_name=data.get('class_name', '')
        )
        db.session.add(new_student)
        db.session.commit()
        return jsonify({'success': True, 'message': '学生创建成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/students/<int:id>', methods=['PUT'])
@login_required
def api_update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    try:
        student.name = data['name']
        student.gender = data['gender']
        student.grade_level = data['grade_level']
        student.student_id = data['student_id']
        student.class_name = data.get('class_name', student.class_name)
        
        if 'school_name' in data:
            school = School.query.filter_by(name=data['school_name']).first()
            if school:
                student.school_id = school.id
                
        db.session.commit()
        return jsonify({'success': True, 'message': '学生信息更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/students/<int:id>', methods=['DELETE'])
@login_required
def api_delete_student(id):
    student = Student.query.get_or_404(id)
    try:
        # Check dependencies
        if ExamRegistration.query.filter_by(student_id=id).first():
            return jsonify({'success': False, 'message': '该考生已有考试记录，无法删除'}), 400
        
        db.session.delete(student)
        db.session.commit()
        return jsonify({'success': True, 'message': '考生删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/students/import', methods=['POST'])
@login_required
def api_import_students():
    try:
        df = None
        # 1. Check for uploaded file
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                try:
                    df = pd.read_excel(file, engine='openpyxl')
                except Exception as e:
                    return jsonify({'success': False, 'message': f'文件解析失败: {str(e)}'}), 400
        
        # 2. Fallback to default file
        if df is None:
            file_path = '/opt/Way To Future考试管理系统/Student_grade_system/基础数据/students_sample.xlsx'
            if os.path.exists(file_path):
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                return jsonify({'success': False, 'message': '请上传Excel文件'}), 400
        
        # 3. Get session
        session_id = request.form.get('session_id')
        if session_id:
            exam_session = ExamSession.query.get(session_id)
        else:
            # Fallback to default session name
            session_name = "橡心国际Way To Future 2025-2026学年S2"
            exam_session = ExamSession.query.filter_by(name=session_name).first()
            
        if not exam_session:
             return jsonify({'success': False, 'message': '找不到有效的考试场次'}), 404
             
        count_new = 0
        count_updated = 0
        count_reg = 0
        
        for index, row in df.iterrows():
            name = row.get('姓名')
            grade = row.get('年级')
            classroom = row.get('班级')
            student_id_code = str(row.get('学号'))
            
            if pd.isna(name) or pd.isna(grade):
                continue
                
            student = Student.query.filter_by(student_id=student_id_code).first()
            if not student:
                student = Student(
                    name=name,
                    grade_level=grade,
                    class_name=classroom,
                    student_id=student_id_code,
                    gender='Unknown',
                    school_id=1
                )
                db.session.add(student)
                db.session.flush()
                count_new += 1
            else:
                student.grade_level = grade
                student.class_name = classroom
                count_updated += 1
            
            # Auto Register
            templates = ExamTemplate.query.filter_by(exam_session_id=exam_session.id).all()
            for template in templates:
                should_register = False
                if template.grade_level == grade:
                    should_register = True
                elif template.grade_level == 'Mixed':
                    should_register = True
                
                if should_register:
                    reg = ExamRegistration.query.filter_by(
                        student_id=student.id,
                        exam_template_id=template.id
                    ).first()
                    if not reg:
                        reg = ExamRegistration(
                            student_id=student.id,
                            exam_session_id=exam_session.id,
                            exam_template_id=template.id,
                            attendance_status='pending'
                        )
                        db.session.add(reg)
                        count_reg += 1
        
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': f'导入完成! 新增: {count_new}, 更新: {count_updated}, 新注册考试: {count_reg}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

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

@app.route('/api/templates/import', methods=['POST'])
@login_required
def api_import_templates():
    try:
        # Check for uploaded file
        if 'file' not in request.files:
             return jsonify({'success': False, 'message': '请上传Excel文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
             return jsonify({'success': False, 'message': '未选择文件'}), 400

        # Get session
        session_id = request.form.get('session_id')
        if not session_id:
             return jsonify({'success': False, 'message': '请选择考试场次'}), 400
        
        exam_session = ExamSession.query.get(session_id)
        if not exam_session:
             return jsonify({'success': False, 'message': '无效的考试场次'}), 400

        # Process file
        xls = pd.ExcelFile(file, engine='openpyxl')
        
        imported_count = 0
        
        # Mapping (Copied from import_data.py)
        subject_map = {
            '朗文英语': 'LANGFORD',
            '牛津英语': 'OXFORD',
            '先锋英语': 'PIONEER',
            '中数': 'CHINESE_MATH',
            '英数': 'ENGLISH_MATH',
            '语文': 'CHINESE',
            'AMC8': 'AMC',
            '袋鼠数学': 'KANGAROO',
            '小托福': 'TOEFL_JUNIOR'
        }

        for sheet_name in xls.sheet_names:
            # Determine Subject and Grade
            grade = 'Mixed'
            subject_code = None
            
            # Simple heuristic
            if '语文' in sheet_name:
                subject_code = 'CHINESE'
                if 'G' in sheet_name:
                     grade = sheet_name.split('语文')[0] 
            elif 'AMC' in sheet_name:
                subject_code = 'AMC'
            elif '袋鼠' in sheet_name:
                subject_code = 'KANGAROO'
            elif '托福' in sheet_name:
                subject_code = 'TOEFL_JUNIOR'
            elif '英数' in sheet_name:
                subject_code = 'ENGLISH_MATH'
            elif '中数' in sheet_name:
                subject_code = 'CHINESE_MATH'
            elif '朗文' in sheet_name:
                subject_code = 'LANGFORD'
            elif '牛津' in sheet_name:
                subject_code = 'OXFORD'
            elif '先锋' in sheet_name:
                subject_code = 'PIONEER'
            
            if not subject_code:
                 for k, v in subject_map.items():
                     if k in sheet_name:
                         subject_code = v
                         break
            
            if not subject_code:
                continue 
            
            subject = Subject.query.filter_by(code=subject_code).first()
            if not subject:
                continue

            # Read data
            try:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=1, engine='openpyxl')
                df.columns = df.columns.str.strip()
                if '题号' not in df.columns:
                     df = pd.read_excel(xls, sheet_name=sheet_name, header=0, engine='openpyxl')
                     df.columns = df.columns.str.strip()
                
                if '题号' not in df.columns:
                    continue
            except:
                continue

            # Create/Update Template
            template_name = f"{exam_session.name} - {sheet_name}"
            template = ExamTemplate.query.filter_by(name=template_name).first()
            if not template:
                template = ExamTemplate(
                    name=template_name,
                    subject_id=subject.id,
                    exam_session_id=exam_session.id,
                    grade_level=grade,
                    total_questions=len(df)
                )
                db.session.add(template)
                db.session.flush()
            else:
                template.exam_session_id = exam_session.id
                template.total_questions = len(df)
            
            # Clear old questions
            Question.query.filter_by(exam_template_id=template.id).delete()
            
            # Import Questions
            for idx, row in df.iterrows():
                try:
                    row_data = row.to_dict()
                    q_num = str(row_data.get('题号', idx+1))
                    module = row_data.get('模块', '')
                    kp = row_data.get('知识点', '') or row_data.get('核心知识点/技能', '')
                    score_val = row_data.get('分值', 1)
                    try:
                        score_val = float(score_val)
                    except:
                        score_val = 1.0
                        
                    q = Question(
                        exam_template_id=template.id,
                        question_number=q_num,
                        subject_id=subject.id,
                        score=float(score_val),
                        module=str(module),
                        knowledge_point=str(kp)
                    )
                    db.session.add(q)
                except:
                    pass
            
            imported_count += 1
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'成功导入 {imported_count} 个试卷模板'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# --- Exam Template Management ---
@app.route('/exam_templates')
@login_required
def exam_templates():
    templates = ExamTemplate.query.all()
    subjects = Subject.query.all()
    sessions = ExamSession.query.order_by(ExamSession.exam_date.desc()).all()
    return render_template('exam_templates.html', templates=templates, subjects=subjects, sessions=sessions)

@app.route('/api/exam_templates', methods=['GET'])
@login_required
def api_get_exam_templates():
    templates = ExamTemplate.query.all()
    return jsonify([t.to_dict() for t in templates])

@app.route('/api/exam_templates', methods=['POST'])
@login_required
def api_create_exam_template():
    data = request.get_json()
    try:
        new_template = ExamTemplate(
            name=data['name'],
            subject_id=data['subject_id'],
            exam_session_id=data.get('exam_session_id'),
            grade_level=data['grade_level'],
            total_questions=data.get('total_questions', 0)
        )
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
        if 'exam_session_id' in data:
            template.exam_session_id = data['exam_session_id']
        # total_questions might be auto-calc, but allow edit
        if 'total_questions' in data:
            template.total_questions = data['total_questions']
        
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
        if ExamRegistration.query.filter_by(exam_template_id=id).first():
            return jsonify({'success': False, 'message': '该试卷已有考试记录，无法删除'}), 400
        
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

# 初始化数据库
@app.before_first_request
def create_tables():
    """创建数据库表"""
    db.create_all()
    
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

if __name__ == '__main__':
    # 运行应用
    app.run(host='0.0.0.0', port=8083, debug=True)