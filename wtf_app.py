#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
橡心国际WTF活动管理平台
基于Node.js+React+MySQL技术栈，实现数字化考试管理
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
import json
import tempfile
from decimal import Decimal

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'wtf-exam-system-secret-key-2023'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///wtf_exam_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 初始化数据库
db = SQLAlchemy(app)

# 导入模型到SQLAlchemy上下文

# 路由定义
@app.route('/')
def index():
    """首页 - WTF考试管理平台"""
    return render_template('wtf_index.html')

@app.route('/dashboard')
def dashboard():
    """仪表板"""
    # 统计数据
    total_students = Student.query.count()
    total_exams = ExamSession.query.count()
    total_registrations = ExamRegistration.query.count()
    total_scores = Score.query.count()
    
    # 最近考试场次
    recent_exams = ExamSession.query.order_by(ExamSession.exam_date.desc()).limit(5).all()
    
    # 科目分布
    subject_stats = db.session.query(
        Subject.type,
        db.func.count(ExamTemplate.id).label('count')
    ).join(ExamTemplate).group_by(Subject.type).all()
    
    return render_template('wtf_dashboard.html', 
                         total_students=total_students,
                         total_exams=total_exams,
                         total_registrations=total_registrations,
                         total_scores=total_scores,
                         recent_exams=recent_exams,
                         subject_stats=subject_stats)

# 考试管理
@app.route('/exam-sessions')
def exam_sessions():
    """考试场次管理"""
    sessions = ExamSession.query.order_by(ExamSession.exam_date.desc()).all()
    return render_template('exam_sessions.html', sessions=sessions)

@app.route('/exam-sessions/new', methods=['GET', 'POST'])
def new_exam_session():
    """创建考试场次"""
    if request.method == 'POST':
        data = request.json
        
        session = ExamSession(
            name=data['name'],
            description=data.get('description'),
            exam_date=datetime.strptime(data['exam_date'], '%Y-%m-%d').date(),
            session_type=data['session_type'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            location=data.get('location'),
            max_capacity=data.get('max_capacity')
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({'success': True, 'session': session.to_dict()})
    
    return render_template('exam_session_form.html')

@app.route('/exam-templates')
def exam_templates():
    """试卷模板管理"""
    templates = db.session.query(ExamTemplate, Subject).join(Subject).all()
    return render_template('exam_templates.html', templates=templates)

@app.route('/students')
def students():
    """考生管理"""
    students = db.session.query(Student, School).join(School).all()
    return render_template('wtf_students.html', students=students)

@app.route('/students/new', methods=['GET', 'POST'])
def new_student():
    """添加考生"""
    if request.method == 'POST':
        data = request.json
        
        student = Student(
            student_id=data['student_id'],
            name=data['name'],
            english_name=data.get('english_name'),
            gender=data['gender'],
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
            grade_level=data['grade_level'],
            school_id=data['school_id'],
            class_name=data.get('class_name'),
            parent_phone=data.get('parent_phone'),
            parent_email=data.get('parent_email')
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({'success': True, 'student': student.to_dict()})
    
    schools = School.query.all()
    return render_template('student_form.html', schools=schools, grade_levels=list(GradeLevel))

@app.route('/registration')
def registration():
    """报考管理"""
    registrations = db.session.query(
        ExamRegistration, Student, ExamSession, ExamTemplate
    ).join(Student).join(ExamSession).join(ExamTemplate).all()
    
    return render_template('registration.html', registrations=registrations)

@app.route('/score-entry/<int:exam_registration_id>')
def score_entry(exam_registration_id):
    """阅卷登分界面"""
    registration = db.session.query(
        ExamRegistration, Student, ExamTemplate
    ).join(Student).join(ExamTemplate).filter(
        ExamRegistration.id == exam_registration_id
    ).first()
    
    if not registration:
        flash('报考记录不存在', 'error')
        return redirect(url_for('registration'))
    
    # 获取题目列表
    questions = db.session.query(
        Question, Score
    ).outerjoin(Score, and_(
        Score.question_id == Question.id,
        Score.student_id == registration.Student.id
    )).filter(
        Question.exam_template_id == registration.ExamTemplate.id
    ).order_by(Question.question_number).all()
    
    return render_template('score_entry.html', 
                         registration=registration,
                         questions=questions)

@app.route('/api/scores/batch', methods=['POST'])
def batch_score_update():
    """批量更新分数 - tRPC upsert接口"""
    data = request.json
    
    try:
        for score_data in data['scores']:
            # 查找现有记录
            existing_score = Score.query.filter_by(
                student_id=score_data['student_id'],
                question_id=score_data['question_id']
            ).first()
            
            if existing_score:
                # 更新记录
                existing_score.score = score_data['score']
                existing_score.is_correct = score_data.get('is_correct', score_data['score'] > 0)
                existing_score.scoring_time = datetime.utcnow()
                existing_score.scorer_name = score_data.get('scorer_name', 'System')
            else:
                # 创建新记录
                new_score = Score(
                    student_id=score_data['student_id'],
                    exam_registration_id=score_data['exam_registration_id'],
                    question_id=score_data['question_id'],
                    score=score_data['score'],
                    is_correct=score_data.get('is_correct', score_data['score'] > 0),
                    scorer_name=score_data.get('scorer_name', 'System')
                )
                db.session.add(new_score)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '分数更新成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/report-cards')
def report_cards():
    """成绩单管理"""
    report_cards = db.session.query(
        ReportCard, Student, ExamSession
    ).join(Student).join(ExamSession).all()
    
    return render_template('report_cards.html', report_cards=report_cards)

@app.route('/report-cards/generate/<int:student_id>/<int:exam_session_id>')
def generate_report_card(student_id, exam_session_id):
    """生成成绩单PDF"""
    try:
        # 获取学生信息
        student = Student.query.get(student_id)
        exam_session = ExamSession.query.get(exam_session_id)
        
        if not student or not exam_session:
            return jsonify({'success': False, 'error': '学生或考试场次不存在'})
        
        # 计算总分和排名
        total_score = db.session.query(
            db.func.sum(Score.score)
        ).join(ExamRegistration).filter(
            ExamRegistration.student_id == student_id,
            ExamRegistration.exam_session_id == exam_session_id
        ).scalar() or Decimal('0.0')
        
        # 生成雷达图数据
        radar_data = generate_radar_data(student_id, exam_session_id)
        
        # 创建成绩单记录
        report_card = ReportCard(
            student_id=student_id,
            exam_session_id=exam_session_id,
            total_score=total_score,
            radar_data=json.dumps(radar_data),
            generated_at=datetime.utcnow()
        )
        
        db.session.add(report_card)
        db.session.commit()
        
        # 生成PDF (这里简化实现，实际需要Puppeteer)
        pdf_content = generate_pdf_report(student, exam_session, total_score, radar_data)
        
        # 保存PDF文件
        pdf_filename = f"report_card_{student_id}_{exam_session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        # 更新PDF URL
        report_card.pdf_url = f"/uploads/{pdf_filename}"
        db.session.commit()
        
        return jsonify({
            'success': True,
            'report_card_id': report_card.id,
            'pdf_url': report_card.pdf_url,
            'total_score': float(total_score)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件下载"""
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# API路由
@app.route('/api/exam-sessions', methods=['GET'])
def api_exam_sessions():
    """获取考试场次列表"""
    sessions = ExamSession.query.order_by(ExamSession.exam_date.desc()).all()
    return jsonify([session.to_dict() for session in sessions])

@app.route('/api/students', methods=['GET'])
def api_students():
    """获取学生列表"""
    students = db.session.query(Student, School).join(School).all()
    return jsonify([{
        **student.Student.to_dict(),
        'school_name': student.School.name if student.School else None
    } for student in students])

@app.route('/api/exam-registrations', methods=['GET'])
def api_exam_registrations():
    """获取报考记录"""
    registrations = db.session.query(
        ExamRegistration, Student, ExamSession
    ).join(Student).join(ExamSession).all()
    
    return jsonify([{
        **registration.ExamRegistration.to_dict(),
        'student_name': registration.Student.name if registration.Student else None,
        'exam_session_name': registration.ExamSession.name if registration.ExamSession else None
    } for registration in registrations])

@app.route('/api/statistics')
def api_statistics():
    """统计分析API"""
    # 科目分布统计
    subject_stats = db.session.query(
        Subject.type,
        Subject.name,
        db.func.count(ExamRegistration.id).label('count')
    ).join(ExamTemplate).join(ExamRegistration).group_by(Subject.type, Subject.name).all()
    
    # 年级分布统计
    grade_stats = db.session.query(
        Student.grade_level,
        db.func.count(Student.id).label('count')
    ).group_by(Student.grade_level).all()
    
    # 成绩分布统计
    score_distribution = db.session.query(
        db.func.case([
            (Score.score >= 90, '优秀'),
            (Score.score >= 80, '良好'),
            (Score.score >= 70, '中等'),
            (Score.score >= 60, '及格'),
        ], else_='不及格').label('grade_level'),
        db.func.count(Score.id).label('count')
    ).group_by('grade_level').all()
    
    return jsonify({
        'subject_stats': [{
            'type': stat.type.value if stat.type else None,
            'name': stat.name,
            'count': stat.count
        } for stat in subject_stats],
        'grade_stats': [{
            'grade': stat.grade_level.value if stat.grade_level else None,
            'count': stat.count
        } for stat in grade_stats],
        'score_distribution': [{
            'level': stat.grade_level,
            'count': stat.count
        } for stat in score_distribution]
    })

# 工具函数
def generate_radar_data(student_id, exam_session_id):
    """生成雷达图能力分析数据"""
    # 按知识点模块统计得分率
    module_scores = db.session.query(
        Question.module,
        db.func.sum(Score.score).label('total_score'),
        db.func.sum(Question.score).label('max_score')
    ).join(Score).join(Question).filter(
        Score.student_id == student_id
    ).group_by(Question.module).all()
    
    radar_data = []
    for module in module_scores:
        if module.module and module.max_score and module.max_score > 0:
            score_rate = float(module.total_score) / float(module.max_score) * 100
            radar_data.append({
                'module': module.module,
                'score': float(module.total_score),
                'max_score': float(module.max_score),
                'rate': round(score_rate, 1)
            })
    
    return radar_data

def generate_pdf_report(student, exam_session, total_score, radar_data):
    """生成PDF报告 (简化版本，实际应使用Puppeteer)"""
    # 这里返回一个简单的HTML转PDF的占位符
    # 实际实现需要集成Puppeteer或类似工具
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>成绩单 - {student.name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .info {{ margin-bottom: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>橡心国际WTF考试成绩单</h1>
            <p>学生姓名: {student.name}</p>
            <p>考试场次: {exam_session.name}</p>
            <p>考试日期: {exam_session.exam_date}</p>
        </div>
        <div class="info">
            <h3>成绩信息</h3>
            <p>总分: {total_score}</p>
        </div>
        <div class="analysis">
            <h3>能力分析</h3>
            {json.dumps(radar_data, indent=2, ensure_ascii=False)}
        </div>
    </body>
    </html>
    """
    
    # 简化返回，实际应使用HTML转PDF工具
    return html_content.encode('utf-8')

# 初始化数据库
@app.before_first_request
def create_tables():
    """创建数据库表"""
    db.create_all()
    
    # 创建初始数据
    if not Subject.query.first():
        create_initial_data()

def create_initial_data():
    """创建初始数据"""
    
    # 创建学校
    schools = [
        School(name='橡心国际小学', code='OX001', system=SchoolSystem.INTERNATIONAL),
        School(name='橡心国际初中', code='OX002', system=SchoolSystem.INTERNATIONAL),
    ]
    
    for school in schools:
        db.session.add(school)
    
    # 创建科目
    subjects = [
        Subject(name='朗文英语', code='LANGFORD', type=SubjectType.LANGFORD, total_score=100),
        Subject(name='牛津英语', code='OXFORD', type=SubjectType.OXFORD, total_score=100),
        Subject(name='先锋英语', code='PIONEER', type=SubjectType.PIONEER, total_score=100),
        Subject(name='中文数学', code='CHINESE_MATH', type=SubjectType.CHINESE_MATH, total_score=100),
        Subject(name='英语数学', code='ENGLISH_MATH', type=SubjectType.ENGLISH_MATH, total_score=100),
        Subject(name='AMC数学', code='AMC', type=SubjectType.AMC, total_score=150),
        Subject(name='袋鼠数学', code='KANGAROO', type=SubjectType.KANGAROO, total_score=120),
        Subject(name='小托福', code='TOEFL_JUNIOR', type=SubjectType.TOEFL_JUNIOR, total_score=100),
    ]
    
    for subject in subjects:
        db.session.add(subject)
    
    db.session.commit()
    
    # 创建示例考试场次
    exam_session = ExamSession(
        name='2025秋季WTF测评',
        description='2025年秋季学期橡心国际WTF综合测评',
        exam_date=date(2025, 12, 27),
        session_type=ExamSessionType.MORNING,
        start_time='09:40',
        end_time='11:50',
        status=ExamStatus.IN_PROGRESS,
        location='橡心国际校区'
    )
    
    db.session.add(exam_session)
    db.session.commit()

if __name__ == '__main__':
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 运行应用
    app.run(host='0.0.0.0', port=8083, debug=True)