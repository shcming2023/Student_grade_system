from wtf_app_simple import app, db, ExamTemplate, ExamRegistration, Student, ExamSession, Subject

def check_registrations():
    with app.app_context():
        # Find Template for G2 Chinese Math
        # Assuming '中数' maps to 'CHINESE_MATH' or similar subject, or just look by name
        # User said "G2中数", let's search templates with this name
        
        templates = ExamTemplate.query.all()
        target_template = None
        
        print("Searching for 'G2中数' templates...")
        for t in templates:
            # Check subject name or template name
            session_info = ""
            if t.exam_session_id:
                sess = ExamSession.query.get(t.exam_session_id)
                if sess:
                    session_info = f"{sess.exam_date} {sess.session_type}"
            
            print(f"ID: {t.id}, Name: {t.name}, Grade: {t.grade_level}, Session: {session_info}")
            
            if "G2" in t.grade_level and ("中数" in t.name or "CHINESE_MATH" in str(t.subject_id)):
                # Just fuzzy match user description
                pass

        # Let's try to match exactly what user said: "G2中数1月4日上午场"
        # Find 1/4 Morning Session first
        sessions = ExamSession.query.filter(ExamSession.exam_date.like('2025-01-04%')).all()
        morning_session = None
        for s in sessions:
            if s.session_type == 'morning':
                morning_session = s
                break
        
        if not morning_session:
            print("No 1/4 Morning session found.")
            return

        print(f"Found Session: {morning_session.id} {morning_session.name} {morning_session.exam_date}")

        # Find Template in this session with G2 and Math
        # Look for templates in this session
        tmps = ExamTemplate.query.filter_by(exam_session_id=morning_session.id).all()
        target = None
        for t in tmps:
            if t.grade_level == 'G2' and ('中数' in t.name or 'Math' in t.name):
                target = t
                print(f"Candidate Template: {t.id} {t.name}")
                
        if not target:
            # Fallback: maybe name is just '中数'
            for t in tmps:
                 if '中数' in t.name:
                     target = t
                     print(f"Candidate Template: {t.id} {t.name}")

        if target:
            print(f"Checking Registrations for Template {target.id}...")
            regs = ExamRegistration.query.filter_by(exam_template_id=target.id).all()
            print(f"Total Registrations in DB: {len(regs)}")
            for r in regs:
                stu = Student.query.get(r.student_id)
                print(f" - RegID: {r.id}, Student: {stu.name} ({stu.student_id})")
        else:
            print("Target template not found.")

if __name__ == "__main__":
    check_registrations()
