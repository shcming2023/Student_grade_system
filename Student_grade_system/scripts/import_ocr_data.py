import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from wtf_app_simple import app, db, User, School, Student, ExamSession, ExamTemplate, ExamRegistration, Subject, Score, Question
from datetime import datetime
import random

# OCR Data extracted from images
OCR_DATA = [
    # Image 1: 2026.1.4 上午场 9:40-11:50
    {"姓名": "黄昱珩", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "汤乐行", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "张辰汐", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "俞悦", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "徐子恒", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "徐子杰", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "张屹然", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "王姿文", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "张雅涵", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "钱宇辰", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "宋佳泽", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},
    {"姓名": "黄诗涵", "学校": "协和国际", "年级": "6", "数学新课标": 1, "语文新课标": 1, "英语新课标": 1, "日期": "2026-01-04", "时间": "上午场", "开始": "09:40", "结束": "11:50"},

    # Image 2: 2026.1.4 下午场 13:30-15:10
    {"姓名": "程芸熙", "学校": "协和先锋", "年级": "2", "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},
    {"姓名": "朱亚伦", "学校": "协和先锋", "年级": "3", "语文新课标": 1, "国际数学": 1, "Map测评": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},
    {"姓名": "陶申涛", "学校": "协和先锋", "年级": "3", "语文新课标": 1, "国际数学": 1, "Map测评": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},
    {"姓名": "张凌尚", "学校": "协和先锋", "年级": "4", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"}, # G4
    {"姓名": "朱陈筱", "学校": "协和先锋", "年级": "3", "语文新课标": 1, "国际数学": 1, "Map测评": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},
    {"姓名": "侯敏恩", "学校": "协和先锋", "年级": "4", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},
    {"姓名": "顾情鸾", "学校": "协和先锋", "年级": "4", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},
    {"姓名": "舒仁洛", "学校": "协和先锋", "年级": "4", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},
    {"姓名": "陈星汝", "学校": "协和先锋", "年级": "4", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},
    {"姓名": "王雯仪", "学校": "协和先锋", "年级": "3", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},
    {"姓名": "国来", "学校": "协和先锋", "年级": "2", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},

    # Image 4: 2026.1.11 上午场 9:30-11:55
    {"姓名": "何林泽", "学校": "协和先锋", "年级": "4", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-11", "时间": "上午场", "开始": "09:30", "结束": "11:55"},
    {"姓名": "吴舒然", "学校": "协和先锋", "年级": "1", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-11", "时间": "上午场", "开始": "09:30", "结束": "11:55"},
    {"姓名": "孙悦雯", "学校": "协和先锋", "年级": "5", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-11", "时间": "上午场", "开始": "09:30", "结束": "11:55"},
]

def generate_student_id():
    return f"2026{random.randint(1000, 9999)}"

def main():
    print("Starting import process...", flush=True)
    
    # 1. Save to Excel
    try:
        df = pd.DataFrame(OCR_DATA)
        df = df.fillna(0)
        output_path = '/opt/Way To Future考试管理系统/Student_grade_system/基础数据/registration_data_ocr.xlsx'
        df.to_excel(output_path, index=False)
        print(f"Excel file created at: {output_path}", flush=True)
    except Exception as e:
        print(f"Error creating Excel: {e}", flush=True)

    # 2. Import to DB
    with app.app_context():
        # Get Admin User for creator_id (or use first user)
        admin = User.query.first()
        admin_id = admin.id if admin else 1

        # Mappings
        SUBJECT_MAP = {
            "数学新课标": {"subject_name": "中文数学", "template_suffix": "中文数学"},
            "语文新课标": {"subject_name": "语文", "template_suffix": "语文"},
            "英语新课标": {"subject_name": "先锋英语", "template_suffix": "先锋英语"},
            "朗文英语": {"subject_name": "朗文英语", "template_suffix": "朗文英语"}, # Fixed G1 issue
            "国际数学": {"subject_name": "英语数学", "template_suffix": "英语数学"},
            "Map测评": {"subject_name": "Map测评", "template_suffix": "Map测评"},
            "袋鼠数学": {"subject_name": "袋鼠数学", "template_suffix": "袋鼠数学"}, # Fixed A issue
            "小托福": {"subject_name": "小托福", "template_suffix": "小托福"},
            "AMC": {"subject_name": "AMC数学", "template_suffix": "AMC8"},
        }

        # 1. Ensure Subjects Exist
        for ocr_key, config in SUBJECT_MAP.items():
            subj_name = config['subject_name']
            subject = Subject.query.filter_by(name=subj_name).first()
            if not subject:
                subject = Subject(name=subj_name, code=f"SUBJ{random.randint(100,999)}", type="standard")
                db.session.add(subject)
                db.session.commit()
                print(f"Created Subject: {subj_name}", flush=True)

        for row in OCR_DATA:
            # A. School
            school_name = row['学校']
            school = School.query.filter_by(name=school_name).first()
            if not school:
                school = School(name=school_name, code=f"SCH{random.randint(100,999)}")
                db.session.add(school)
                db.session.commit()
            
            # B. Student
            student_name = row['姓名']
            student = Student.query.filter_by(name=student_name, school_id=school.id).first()
            if not student:
                student = Student(
                    student_id=generate_student_id(),
                    name=student_name,
                    gender="女", # Default
                    grade_level=row['年级'],
                    school_id=school.id,
                    class_name="1班"
                )
                db.session.add(student)
                db.session.commit()
            else:
                if student.grade_level != row['年级']:
                    student.grade_level = row['年级']
                    db.session.commit()

            # C. Exam Session
            session_name = f"{row['日期']} {row['时间']}"
            exam_session = ExamSession.query.filter_by(name=session_name).first()
            if not exam_session:
                exam_session = ExamSession(
                    name=session_name,
                    exam_date=datetime.strptime(row['日期'], '%Y-%m-%d').date(),
                    session_type=row['时间'],
                    start_time=row['开始'],
                    end_time=row['结束'],
                    status='published'
                )
                db.session.add(exam_session)
                db.session.commit()

            # **CRITICAL: Cleanup existing registrations for this student in this session**
            # This prevents duplicates and clears incorrect "old" data
            existing_regs = ExamRegistration.query.filter_by(student_id=student.id, exam_session_id=exam_session.id).all()
            if existing_regs:
                print(f"Clearing {len(existing_regs)} existing registrations for {student.name} in {session_name}", flush=True)
                for reg in existing_regs:
                    db.session.delete(reg)
                db.session.commit()

            # D. Registration
            for ocr_subj, config in SUBJECT_MAP.items():
                if row.get(ocr_subj) == 1:
                    subject = Subject.query.filter_by(name=config['subject_name']).first()
                    
                    # Create template specific to the grade
                    # Format: "橡心国际Way To Future 2025-2026学年S2 - {BaseSuffix} G{Grade}"
                    grade = row['年级']
                    grade_display = f"G{grade}" if str(grade).isdigit() else grade
                    
                    t_name = f"橡心国际Way To Future 2025-2026学年S2 - {config['template_suffix']} {grade_display}"
                    
                    # Find or Create Template
                    template = ExamTemplate.query.filter_by(name=t_name).first()
                    if not template:
                        # Try to copy total_questions from a similar template or default to 1
                        existing_t = ExamTemplate.query.filter(ExamTemplate.name.like(f"%{config['template_suffix']}%")).first()
                        total_q = existing_t.total_questions if existing_t else 1
                        
                        template = ExamTemplate(
                            name=t_name,
                            subject_id=subject.id,
                            exam_session_id=exam_session.id,
                            grade_level=str(grade),
                            total_questions=total_q,
                            creator_id=admin_id,
                            grader_id=admin_id
                        )
                        db.session.add(template)
                        db.session.commit()
                        print(f"Created Template: {template.name} for Session {session_name}", flush=True)

                    # Register
                    registration = ExamRegistration(
                        student_id=student.id,
                        exam_session_id=exam_session.id,
                        exam_template_id=template.id
                    )
                    db.session.add(registration)
                    db.session.commit()
                    print(f"Registered {student.name} for {template.name}", flush=True)

    print("Import completed successfully!", flush=True)

if __name__ == "__main__":
    main()
