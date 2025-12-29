from wtf_app_simple import app, db, Student, ExamRegistration, ExamSession

with app.app_context():
    with open('data_check.txt', 'w') as f:
        f.write("Checking Data...\n")
        
        students = Student.query.all()
        f.write(f"Total Students: {len(students)}\n")
        for s in students:
            f.write(f"Student: {s.name} ({s.student_id})\n")
            
        sessions = ExamSession.query.all()
        f.write(f"\nTotal Sessions: {len(sessions)}\n")
        for s in sessions:
            f.write(f"Session: {s.name}\n")
            
        regs = ExamRegistration.query.all()
        f.write(f"\nTotal Registrations: {len(regs)}\n")
        for r in regs:
            f.write(f"Reg: Student {r.student_id} -> Template {r.exam_template_id} in Session {r.exam_session_id}\n")
