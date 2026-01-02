import pandas as pd
import sqlite3

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def find_all_scores_nico():
    conn = sqlite3.connect(DB_PATH)
    
    # Get student ID for Nico
    s_df = pd.read_sql_query("SELECT id FROM students WHERE name='Nico'", conn)
    if s_df.empty:
        print("Nico not found")
        return
    s_ids = s_df['id'].tolist()
    print(f"Nico IDs: {s_ids}")
    
    for s_id in s_ids:
        print(f"\nChecking scores for Student ID {s_id}...")
        query = f"""
        SELECT et.name, et.id as template_id, COUNT(*) as score_count
        FROM scores s
        JOIN questions q ON s.question_id = q.id
        JOIN exam_templates et ON q.exam_template_id = et.id
        WHERE s.student_id = {s_id}
        GROUP BY et.id
        """
        res = pd.read_sql_query(query, conn)
        print(res)

    conn.close()

if __name__ == "__main__":
    find_all_scores_nico()
