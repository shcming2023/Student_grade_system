from wtf_app_simple import app, db, ExamTemplate, ExamSession, School

with app.app_context():
    print("Schools:")
    for s in School.query.all():
        print(f" - {s.name}")

    print("\nExamTemplates:")
    for t in ExamTemplate.query.all():
        print(f" - {t.name}")

    print("\nExamSessions:")
    for s in ExamSession.query.all():
        print(f" - {s.name} ({s.date})")
