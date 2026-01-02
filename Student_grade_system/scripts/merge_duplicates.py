import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wtf_app_simple import app, db, Student, ExamRegistration

def merge_duplicates():
    with app.app_context():
        # Duplicate pairs (Keep ID, Delete ID) based on analysis
        # Keep the one that matches User's list (Grade)
        # User List: 侯敏恩(5), 程芸熙(4), 舒仁洛(3), 陶申涛(4), 黄昱珩(4)
        
        # From check_duplicates.py:
        # 侯敏恩: ID 18 (Grade 5) - KEEP, ID 75 (Grade 4) - DELETE
        # 程芸熙: ID 13 (Grade 4) - KEEP, ID 73 (Grade 2) - DELETE
        # 舒仁洛: ID 20 (Grade 3) - KEEP, ID 76 (Grade 4) - DELETE
        # 陶申涛: ID 15 (Grade 4) - KEEP, ID 74 (Grade 3) - DELETE
        # 黄昱珩: ID 1 (Grade 4) - KEEP, ID 72 (Grade 6) - DELETE
        
        pairs = [
            (18, 75),
            (13, 73),
            (20, 76),
            (15, 74),
            (1, 72)
        ]
        
        for keep_id, delete_id in pairs:
            keep_s = Student.query.get(keep_id)
            delete_s = Student.query.get(delete_id)
            
            if not keep_s or not delete_s:
                print(f"Skipping pair {keep_id}, {delete_id} - not found")
                continue
                
            print(f"Merging {delete_s.name} (ID {delete_id}, G{delete_s.grade_level}) into {keep_s.name} (ID {keep_id}, G{keep_s.grade_level})")
            
            # Move registrations
            regs = ExamRegistration.query.filter_by(student_id=delete_id).all()
            for r in regs:
                # Check if target already has this registration
                exists = ExamRegistration.query.filter_by(
                    student_id=keep_id, 
                    exam_session_id=r.exam_session_id,
                    exam_template_id=r.exam_template_id
                ).first()
                
                if not exists:
                    r.student_id = keep_id
                    print(f"  Moved registration: {r.exam_template.name}")
                else:
                    db.session.delete(r)
                    print(f"  Duplicate registration deleted: {r.exam_template.name}")
            
            # Delete the student
            db.session.delete(delete_s)
            
        db.session.commit()
        print("Merge complete.")

if __name__ == '__main__':
    merge_duplicates()
