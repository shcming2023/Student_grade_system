from wtf_app_simple import app, db, ExamTemplate, ExamRegistration, Student, User

def debug_data():
    with app.app_context():
        # 1. Check if template exists
        name = "G2中文数学模板"
        templates = ExamTemplate.query.filter_by(name=name).all()
        print(f"Templates found for '{name}': {len(templates)}")
        for t in templates:
            print(f"  ID: {t.id}, Name: {t.name}, GraderID: {t.grader_id}")
            
        if not templates:
            print("No templates found! Checking all template names...")
            all_templates = ExamTemplate.query.all()
            for t in all_templates:
                if "G2" in t.name and "数学" in t.name:
                    print(f"  Found similar: {t.name}")
            return

        template_ids = [t.id for t in templates]
        
        # 2. Check registrations
        regs = ExamRegistration.query.filter(ExamRegistration.exam_template_id.in_(template_ids)).all()
        print(f"Registrations found: {len(regs)}")
        for r in regs:
            s = Student.query.get(r.student_id)
            print(f"  RegID: {r.id}, Student: {s.name} ({s.student_id}), TemplateID: {r.exam_template_id}")

if __name__ == "__main__":
    debug_data()