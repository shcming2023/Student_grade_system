"""
橡心国际WTF活动管理平台 - 数据模型
"""

from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Decimal, Date, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

# 枚举类型定义
class ExamSessionType(enum.Enum):
    MORNING = "morning"      # 上午场 9:40-11:50
    AFTERNOON = "afternoon"    # 下午场 13:30-15:10

class ExamStatus(enum.Enum):
    DRAFT = "draft"           # 草稿
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"     # 已完成
    ARCHIVED = "archived"       # 已归档

class AttendanceStatus(enum.Enum):
    PRESENT = "present"       # 到场
    ABSENT = "absent"         # 缺考

class SubjectType(enum.Enum):
    LANGFORD = "langford"     # 朗文英语
    OXFORD = "oxford"         # 牛津英语
    PIONEER = "pioneer"       # 先锋英语
    CHINESE_MATH = "chinese_math"  # 中数
    ENGLISH_MATH = "english_math"  # 英数
    AMC = "amc"              # AMC数学
    KANGAROO = "kangaroo"     # 袋鼠数学
    TOEFL_JUNIOR = "toefl_junior"  # 小托福

class GradeLevel(enum.Enum):
    G1 = "G1"
    G2 = "G2"
    G3 = "G3"
    G4 = "G4"
    G5 = "G5"
    G6 = "G6"

class SchoolSystem(enum.Enum):
    PUBLIC = "public"         # 公立体系
    INTERNATIONAL = "international"  # 国际体系
    BILINGUAL = "bilingual"   # 双语体系

# 数据模型定义
class School(db.Model):
    """学校信息"""
    __tablename__ = 'schools'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, comment='学校名称')
    code = Column(String(20), unique=True, nullable=False, comment='学校代码')
    system = Column(SQLEnum(SchoolSystem), nullable=False, comment='学校体系')
    address = Column(Text, comment='学校地址')
    phone = Column(String(20), comment='联系电话')
    contact_person = Column(String(50), comment='联系人')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关联关系
    students = relationship("Student", back_populates="school")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'system': self.system.value if self.system else None,
            'address': self.address,
            'phone': self.phone,
            'contact_person': self.contact_person,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Student(db.Model):
    """考生信息"""
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(20), unique=True, nullable=False, comment='学号')
    name = Column(String(50), nullable=False, comment='姓名')
    english_name = Column(String(50), comment='英文名')
    gender = Column(String(10), nullable=False, comment='性别')
    birth_date = Column(Date, comment='出生日期')
    grade_level = Column(SQLEnum(GradeLevel), nullable=False, comment='年级')
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False, comment='学校ID')
    class_name = Column(String(50), comment='班级')
    parent_phone = Column(String(20), comment='家长电话')
    parent_email = Column(String(100), comment='家长邮箱')
    photo_url = Column(String(255), comment='照片URL')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    school = relationship("School", back_populates="students")
    exam_registrations = relationship("ExamRegistration", back_populates="student")
    scores = relationship("Score", back_populates="student")
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'english_name': self.english_name,
            'gender': self.gender,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'grade_level': self.grade_level.value if self.grade_level else None,
            'school_id': self.school_id,
            'class_name': self.class_name,
            'parent_phone': self.parent_phone,
            'parent_email': self.parent_email,
            'photo_url': self.photo_url,
            'school_name': self.school.name if self.school else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ExamSession(db.Model):
    """考试场次"""
    __tablename__ = 'exam_sessions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, comment='考试名称')
    description = Column(Text, comment='考试描述')
    exam_date = Column(Date, nullable=False, comment='考试日期')
    session_type = Column(SQLEnum(ExamSessionType), nullable=False, comment='场次类型')
    start_time = Column(String(10), nullable=False, comment='开始时间')
    end_time = Column(String(10), nullable=False, comment='结束时间')
    status = Column(SQLEnum(ExamStatus), default=ExamStatus.DRAFT, comment='状态')
    location = Column(String(100), comment='考试地点')
    max_capacity = Column(Integer, comment='最大容量')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    exam_registrations = relationship("ExamRegistration", back_populates="exam_session")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'exam_date': self.exam_date.strftime('%Y-%m-%d') if self.exam_date else None,
            'session_type': self.session_type.value if self.session_type else None,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'status': self.status.value if self.status else None,
            'location': self.location,
            'max_capacity': self.max_capacity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Subject(db.Model):
    """科目管理"""
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, comment='科目名称')
    code = Column(String(20), unique=True, nullable=False, comment='科目代码')
    type = Column(SQLEnum(SubjectType), nullable=False, comment='科目类型')
    description = Column(Text, comment='科目描述')
    total_score = Column(Decimal(10, 2), nullable=False, default=100.00, comment='总分')
    duration = Column(Integer, comment='考试时长(分钟)')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关联关系
    exam_templates = relationship("ExamTemplate", back_populates="subject")
    questions = relationship("Question", back_populates="subject")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'type': self.type.value if self.type else None,
            'description': self.description,
            'total_score': float(self.total_score) if self.total_score else None,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ExamTemplate(db.Model):
    """试卷模板"""
    __tablename__ = 'exam_templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, comment='试卷名称')
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False, comment='科目ID')
    grade_level = Column(SQLEnum(GradeLevel), nullable=False, comment='适用年级')
    version = Column(String(20), default='1.0', comment='版本号')
    description = Column(Text, comment='试卷描述')
    total_questions = Column(Integer, nullable=False, comment='总题数')
    total_score = Column(Decimal(10, 2), nullable=False, comment='总分')
    time_limit = Column(Integer, comment='时限(分钟)')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    subject = relationship("Subject", back_populates="exam_templates")
    questions = relationship("Question", back_populates="exam_template")
    exam_registrations = relationship("ExamRegistration", back_populates="exam_template")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'grade_level': self.grade_level.value if self.grade_level else None,
            'version': self.version,
            'description': self.description,
            'total_questions': self.total_questions,
            'total_score': float(self.total_score) if self.total_score else None,
            'time_limit': self.time_limit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Question(db.Model):
    """题目信息"""
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    question_number = Column(String(20), nullable=False, comment='题号')
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False, comment='科目ID')
    exam_template_id = Column(Integer, ForeignKey('exam_templates.id'), nullable=False, comment='试卷模板ID')
    module = Column(String(50), comment='知识点模块')
    knowledge_point = Column(String(100), comment='知识点')
    score = Column(Decimal(5, 1), nullable=False, comment='分值')
    difficulty_level = Column(String(20), comment='难度等级')
    question_type = Column(String(20), comment='题型')
    content = Column(Text, comment='题目内容')
    answer = Column(Text, comment='答案')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    subject = relationship("Subject", back_populates="questions")
    exam_template = relationship("ExamTemplate", back_populates="questions")
    scores = relationship("Score", back_populates="question")
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_number': self.question_number,
            'subject_id': self.subject_id,
            'exam_template_id': self.exam_template_id,
            'module': self.module,
            'knowledge_point': self.knowledge_point,
            'score': float(self.score) if self.score else None,
            'difficulty_level': self.difficulty_level,
            'question_type': self.question_type,
            'content': self.content,
            'answer': self.answer,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ExamRegistration(db.Model):
    """报考信息"""
    __tablename__ = 'exam_registrations'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, comment='学生ID')
    exam_session_id = Column(Integer, ForeignKey('exam_sessions.id'), nullable=False, comment='考试场次ID')
    exam_template_id = Column(Integer, ForeignKey('exam_templates.id'), nullable=False, comment='试卷模板ID')
    registration_date = Column(DateTime, default=datetime.utcnow, comment='报考日期')
    status = Column(SQLEnum(ExamStatus), default=ExamStatus.DRAFT, comment='报考状态')
    attendance_status = Column(SQLEnum(AttendanceStatus), comment='考勤状态')
    seat_number = Column(String(10), comment='座位号')
    notes = Column(Text, comment='备注')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    student = relationship("Student", back_populates="exam_registrations")
    exam_session = relationship("ExamSession", back_populates="exam_registrations")
    exam_template = relationship("ExamTemplate", back_populates="exam_registrations")
    scores = relationship("Score", back_populates="exam_registration")
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'exam_session_id': self.exam_session_id,
            'exam_session_name': self.exam_session.name if self.exam_session else None,
            'exam_template_id': self.exam_template_id,
            'exam_template_name': self.exam_template.name if self.exam_template else None,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'status': self.status.value if self.status else None,
            'attendance_status': self.attendance_status.value if self.attendance_status else None,
            'seat_number': self.seat_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Score(db.Model):
    """成绩信息"""
    __tablename__ = 'scores'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, comment='学生ID')
    exam_registration_id = Column(Integer, ForeignKey('exam_registrations.id'), nullable=False, comment='报考ID')
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False, comment='题目ID')
    score = Column(Decimal(5, 1), nullable=False, comment='得分')
    is_correct = Column(Boolean, comment='是否正确')
    scoring_time = Column(DateTime, default=datetime.utcnow, comment='阅卷时间')
    scorer_name = Column(String(50), comment='阅卷人')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    student = relationship("Student", back_populates="scores")
    exam_registration = relationship("ExamRegistration", back_populates="scores")
    question = relationship("Question", back_populates="scores")
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'exam_registration_id': self.exam_registration_id,
            'question_id': self.question_id,
            'question_number': self.question.question_number if self.question else None,
            'score': float(self.score) if self.score else None,
            'is_correct': self.is_correct,
            'scoring_time': self.scoring_time.isoformat() if self.scoring_time else None,
            'scorer_name': self.scorer_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ReportCard(db.Model):
    """成绩单"""
    __tablename__ = 'report_cards'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False, comment='学生ID')
    exam_session_id = Column(Integer, ForeignKey('exam_sessions.id'), nullable=False, comment='考试场次ID')
    total_score = Column(Decimal(10, 2), nullable=False, comment='总分')
    rank_in_class = Column(Integer, comment='班级排名')
    rank_in_grade = Column(Integer, comment='年级排名')
    radar_data = Column(Text, comment='雷达图数据(JSON格式)')
    analysis_notes = Column(Text, comment='能力分析备注')
    pdf_url = Column(String(255), comment='PDF文件URL')
    generated_at = Column(DateTime, default=datetime.utcnow, comment='生成时间')
    
    # 关联关系
    student = relationship("Student")
    exam_session = relationship("ExamSession")
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'exam_session_id': self.exam_session_id,
            'total_score': float(self.total_score) if self.total_score else None,
            'rank_in_class': self.rank_in_class,
            'rank_in_grade': self.rank_in_grade,
            'radar_data': self.radar_data,
            'analysis_notes': self.analysis_notes,
            'pdf_url': self.pdf_url,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }