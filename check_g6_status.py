import sqlite3
import pandas as pd

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def check_g6():
    conn = sqlite3.connect(DB_PATH)
    t_id = 118
    print(f"Checking G6 (Template {t_id})...")
    
    # Check questions
    q_count = pd.read_sql_query(f"SELECT COUNT(*) as c FROM questions WHERE exam_template_id={t_id}", conn).iloc[0]['c']
    print(f"Questions: {q_count}")
    
    # Check registrations
    regs = pd.read_sql_query(f"SELECT s.name, s.id FROM exam_registrations er JOIN students s ON er.student_id=s.id WHERE er.exam_template_id={t_id}", conn)
    print(f"Registrations: {len(regs)}")
    if not regs.empty:
        print(regs.head())
        
        # Check scores for first student
        s_id = regs.iloc[0]['id']
        s_name = regs.iloc[0]['name']
        score_count = pd.read_sql_query(f"SELECT COUNT(*) as c FROM scores s JOIN questions q ON s.question_id=q.id WHERE s.student_id={s_id} AND q.exam_template_id={t_id}", conn).iloc[0]['c']
        print(f"Scores for {s_name}: {score_count}")
        
    conn.close()

if __name__ == "__main__":
    check_g6()
