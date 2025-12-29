import sys
from wtf_app_simple import app, db, Student, ExamRegistration, ExamTemplate, ExamSession, Subject

def verify():
    print("Verifying data for 王雯仪...", flush=True)
    with app.app_context():
        # 1. Find Student
        # Wang Wenyi is in Image 1: 2026.1.4 Morning?
        # Wait, the user said "2026年1.4下午场".
        # Let's check my OCR data in import_ocr_data.py
        # Image 1: 2026.1.4 上午场 9:40-11:50
        # Line 16: {"姓名": "王姿文", "学校": "协和国际", "年级": "6", ...}
        # Line 41: {"姓名": "王雯仪", "学校": "协和先锋", "年级": "3", ...}
        # Let's find where Wang Wenyi is in the OCR data.
        # Line 41: {"姓名": "王雯仪", "学校": "协和先锋", "年级": "3", "数学新课标": 1, "语文新课标": 1, "朗文英语": 1, "日期": "2026-01-04", "时间": "下午场", "开始": "13:30", "结束": "15:10"},
        # Okay, she is in 2026-01-04 Afternoon (下午场). The user is correct.
        
        student = Student.query.filter_by(name="王雯仪").first()
        if not student:
            print("ERROR: Student 王雯仪 not found!", flush=True)
            return

        print(f"Student: {student.name}, ID: {student.student_id}, Grade: {student.grade_level}")
        
        # 2. Find Registrations
        regs = ExamRegistration.query.filter_by(student_id=student.id).all()
        if not regs:
            print("ERROR: No exam registrations found for student.", flush=True)
            return
            
        print(f"Found {len(regs)} exam registrations:")
        
        for reg in regs:
            session = ExamSession.query.get(reg.exam_session_id)
            template = ExamTemplate.query.get(reg.exam_template_id)
            subject = Subject.query.get(template.subject_id)
            
            print(f" - Session: {session.name}")
            print(f"   Template: {template.name}")
            print(f"   Subject: {subject.name}")
            print("---")

        # Check against expectation
        # Expect: 2026-01-04 下午场
        # Expect 3 templates: 
        # 1. 数学新课标 (中文数学)
        # 2. 语文新课标 (语文)
        # 3. 朗文英语 (朗文英语)
        # All should be Grade 3 (G3)
        
if __name__ == "__main__":
    verify()
