import sqlite3
import pandas as pd

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def diagnose():
    conn = sqlite3.connect(DB_PATH)
    
    targets = [
        {'name': 'G4 Oxford', 'template_id': 89, 'student_id': 65},
        {'name': 'Kangaroo A', 'template_id': 110, 'student_id': 62},
        {'name': 'AMC8', 'template_id': 109, 'student_id': 63},
        # Secondary targets
        {'name': 'G4 Oxford (Old)', 'template_id': 61, 'student_id': 57},
        {'name': 'Kangaroo A (Old)', 'template_id': 82, 'student_id': 61},
        {'name': 'AMC8 (Old)', 'template_id': 53, 'student_id': 63},
    ]
    
    print(f"{'Exam':<20} | {'Tmpl':<5} | {'Stud':<5} | {'Questions':<10} | {'Scores':<10}")
    print("-" * 60)
    
    for t in targets:
        # Check Questions
        q_count = pd.read_sql_query(f"SELECT count(*) as cnt FROM questions WHERE exam_template_id={t['template_id']}", conn)['cnt'].iloc[0]
        
        # Check Scores
        s_count = pd.read_sql_query(f"""
            SELECT count(*) as cnt 
            FROM scores s
            JOIN questions q ON s.question_id = q.id
            WHERE s.student_id={t['student_id']} AND q.exam_template_id={t['template_id']}
        """, conn)['cnt'].iloc[0]
        
        print(f"{t['name']:<20} | {t['template_id']:<5} | {t['student_id']:<5} | {q_count:<10} | {s_count:<10}")

if __name__ == "__main__":
    diagnose()
