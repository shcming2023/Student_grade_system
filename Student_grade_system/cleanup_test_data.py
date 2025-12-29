import os
import sys
from wtf_app_simple import app, db, Student, ExamRegistration, Score, ExamSession, ExamTemplate, Question

def cleanup():
    print("Starting cleanup of test data...", flush=True)
    test_names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十"]
    
    with app.app_context():
        # 1. Delete test students
        students_to_delete = Student.query.filter(Student.name.in_(test_names)).all()
        for student in students_to_delete:
            print(f"Deleting student: {student.name} (ID: {student.student_id})", flush=True)
            registrations = ExamRegistration.query.filter_by(student_id=student.id).all()
            for reg in registrations:
                db.session.delete(reg)
            scores = Score.query.filter_by(student_id=student.id).all()
            for score in scores:
                db.session.delete(score)
            db.session.delete(student)
        
        # 2. Delete malformed session
        malformed_session_name = "橡心国际Way To Future 2025-2026学年S22026-01-04 下午场"
        bad_session = ExamSession.query.filter_by(name=malformed_session_name).first()
        if bad_session:
            print(f"Deleting malformed session: {bad_session.name}", flush=True)
            # Delete all registrations for this session
            regs = ExamRegistration.query.filter_by(exam_session_id=bad_session.id).all()
            for reg in regs:
                db.session.delete(reg)
            # Delete all templates for this session
            templates = ExamTemplate.query.filter_by(exam_session_id=bad_session.id).all()
            for temp in templates:
                # Delete questions for this template
                questions = Question.query.filter_by(exam_template_id=temp.id).all()
                for q in questions:
                    db.session.delete(q)
                db.session.delete(temp)
            db.session.delete(bad_session)

        db.session.commit()
        print("Cleanup completed successfully.", flush=True)

if __name__ == "__main__":
    cleanup()
