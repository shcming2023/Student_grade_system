
import sqlite3
import random
from datetime import datetime

db_path = 'Student_grade_system/wtf_exam_system.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def migrate_registration(old_tid, new_tid, label):
    print(f"\n--- Migrating {label} ---")
    cursor.execute("SELECT id, student_id FROM exam_registrations WHERE exam_template_id = ?", (old_tid,))
    regs = cursor.fetchall()
    
    if not regs:
        print(f"No registrations found for {label} (ID={old_tid})")
        return

    for reg_id, student_id in regs:
        # Check if already registered for new template
        cursor.execute("SELECT id FROM exam_registrations WHERE exam_template_id = ? AND student_id = ?", (new_tid, student_id))
        existing = cursor.fetchone()
        
        if existing:
            print(f"Student {student_id} already registered for target template {new_tid}. Deleting old registration {reg_id}.")
            cursor.execute("DELETE FROM exam_registrations WHERE id = ?", (reg_id,))
        else:
            print(f"Migrating Student {student_id} from {old_tid} to {new_tid}.")
            cursor.execute("UPDATE exam_registrations SET exam_template_id = ? WHERE id = ?", (new_tid, reg_id))

def inject_scores(template_id, student_id, label):
    print(f"\n--- Injecting Scores for {label} (Template {template_id}, Student {student_id}) ---")
    
    # Check if scores exist
    cursor.execute("SELECT COUNT(*) FROM scores s JOIN questions q ON s.question_id = q.id WHERE s.student_id = ? AND q.exam_template_id = ?", (student_id, template_id))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Scores already exist ({count}). Skipping.")
        return

    # Get questions
    cursor.execute("SELECT id, score FROM questions WHERE exam_template_id = ?", (template_id,))
    questions = cursor.fetchall()
    
    if not questions:
        print(f"No questions found for template {template_id}!")
        return
        
    print(f"Found {len(questions)} questions. Injecting scores...")
    
    scores_data = []
    for q_id, max_score in questions:
        # Random score: either full score or 0 (simple test)
        earned = max_score if random.random() > 0.3 else 0
        is_correct = (earned == max_score)
        scores_data.append((student_id, q_id, earned, is_correct, datetime.utcnow()))
        
    cursor.executemany("INSERT INTO scores (student_id, question_id, score, is_correct, scoring_time) VALUES (?, ?, ?, ?, ?)", scores_data)
    print("Scores injected.")

# 1. Migrate G6 Longman -> G6 Pioneer
migrate_registration(118, 91, "G6 Langwen -> G6 Pioneer")

# 2. Migrate Kangaroo -> Kangaroo A
migrate_registration(115, 82, "Kangaroo (Morning) -> Kangaroo A")
migrate_registration(119, 110, "Kangaroo (Afternoon) -> Kangaroo A")

# 3. Inject Scores for G4 Oxford (ID 61, Student 57)
inject_scores(61, 57, "G4 Oxford")

# 4. Inject Scores for AMC8 (ID 53, Student 63)
inject_scores(53, 63, "AMC8")

conn.commit()
conn.close()
print("\nDone.")
