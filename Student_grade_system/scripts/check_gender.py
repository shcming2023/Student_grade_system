import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wtf_app_simple import app, db, Student

with app.app_context():
    genders = db.session.query(Student.gender).distinct().all()
    print(f"Distinct genders: {genders}")
    
    # Check a few students' gender
    students = Student.query.limit(5).all()
    for s in students:
        print(f"{s.name}: '{s.gender}'")
