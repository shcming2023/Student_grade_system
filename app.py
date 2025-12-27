#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学生成绩管理系统主应用
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# 创建Flask应用
app = Flask(__name__)

# 配置数据库
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 数据模型
class Student(db.Model):
    """学生模型"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    class_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    grades = db.relationship('Grade', backref='student', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'gender': self.gender,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'class_name': self.class_name,
            'phone': self.phone,
            'email': self.email
        }

class Course(db.Model):
    """课程模型"""
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Float, nullable=False, default=3.0)
    teacher = db.Column(db.String(50), nullable=False)
    grades = db.relationship('Grade', backref='course', lazy=True)

class Grade(db.Model):
    """成绩模型"""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    exam_type = db.Column(db.String(20), nullable=False)  # 期中、期末、平时
    exam_date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    semester = db.Column(db.String(20), nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'student_name': self.student.name if self.student else '',
            'student_id': self.student.student_id if self.student else '',
            'course_name': self.course.course_name if self.course else '',
            'course_code': self.course.course_code if self.course else '',
            'score': self.score,
            'exam_type': self.exam_type,
            'exam_date': self.exam_date.strftime('%Y-%m-%d'),
            'semester': self.semester,
            'academic_year': self.academic_year
        }

# 路由定义
@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """仪表板"""
    student_count = Student.query.count()
    course_count = Course.query.count()
    grade_count = Grade.query.count()
    
    # 获取最近的成绩记录
    recent_grades = Grade.query.order_by(Grade.exam_date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         student_count=student_count,
                         course_count=course_count,
                         grade_count=grade_count,
                         recent_grades=recent_grades)

@app.route('/students')
def students():
    """学生列表"""
    students = Student.query.all()
    return render_template('students.html', students=students)

@app.route('/courses')
def courses():
    """课程列表"""
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/grades')
def grades():
    """成绩列表"""
    grades = Grade.query.order_by(Grade.exam_date.desc()).all()
    return render_template('grades.html', grades=grades)

# API路由
@app.route('/api/students', methods=['GET'])
def api_students():
    """获取学生列表API"""
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

@app.route('/api/students', methods=['POST'])
def api_add_student():
    """添加学生API"""
    data = request.json
    
    student = Student(
        student_id=data['student_id'],
        name=data['name'],
        gender=data['gender'],
        class_name=data['class_name'],
        phone=data.get('phone', ''),
        email=data.get('email', '')
    )
    
    db.session.add(student)
    db.session.commit()
    
    return jsonify({'success': True, 'student': student.to_dict()})

@app.route('/api/grades', methods=['GET'])
def api_grades():
    """获取成绩列表API"""
    grades = Grade.query.order_by(Grade.exam_date.desc()).all()
    return jsonify([grade.to_dict() for grade in grades])

@app.route('/api/grades', methods=['POST'])
def api_add_grade():
    """添加成绩API"""
    data = request.json
    
    grade = Grade(
        student_id=data['student_id'],
        course_id=data['course_id'],
        score=data['score'],
        exam_type=data['exam_type'],
        semester=data['semester'],
        academic_year=data['academic_year']
    )
    
    db.session.add(grade)
    db.session.commit()
    
    return jsonify({'success': True, 'grade': grade.to_dict()})

@app.route('/api/statistics')
def api_statistics():
    """成绩统计API"""
    # 平均成绩统计
    avg_scores = db.session.query(
        Course.course_name,
        db.func.avg(Grade.score).label('avg_score')
    ).join(Grade).group_by(Course.course_name).all()
    
    # 成绩分布统计
    grade_dist = db.session.query(
        db.func.case(
            (Grade.score >= 90, '优秀'),
            (Grade.score >= 80, '良好'),
            (Grade.score >= 70, '中等'),
            (Grade.score >= 60, '及格'),
            else_='不及格'
        ).label('grade_level'),
        db.func.count(Grade.id).label('count')
    ).group_by('grade_level').all()
    
    return jsonify({
        'avg_scores': [{'course': row.course_name, 'avg_score': float(row.avg_score)} for row in avg_scores],
        'grade_distribution': [{'level': row.grade_level, 'count': row.count} for row in grade_dist]
    })

# 初始化数据库
@app.before_first_request
def create_tables():
    """创建数据库表"""
    db.create_all()
    
    # 添加测试数据
    if not Student.query.first():
        # 添加测试学生
        test_student = Student(
            student_id='2023001',
            name='张三',
            gender='男',
            class_name='计算机科学1班',
            phone='13800138000',
            email='zhangsan@example.com'
        )
        db.session.add(test_student)
        
        # 添加测试课程
        test_course = Course(
            course_code='CS101',
            course_name='计算机基础',
            credits=3.0,
            teacher='李老师'
        )
        db.session.add(test_course)
        
        db.session.commit()
        
        # 添加测试成绩
        test_grade = Grade(
            student_id=test_student.id,
            course_id=test_course.id,
            score=85.5,
            exam_type='期末',
            semester='第一学期',
            academic_year='2023-2024'
        )
        db.session.add(test_grade)
        db.session.commit()

if __name__ == '__main__':
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), exist_ok=True)
    
    # 运行应用
    app.run(host='0.0.0.0', port=5000, debug=True)