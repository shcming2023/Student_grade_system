import sqlite3
import pandas as pd

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def diagnose_exams():
    conn = sqlite3.connect(DB_PATH)
    
    target_exams = ['G4牛津英语', '袋鼠数学A', '袋鼠数学B', 'AMC8']
    
    results = []
    
    print(f"{'Exam Name':<20} | {'ID':<5} | {'Questions':<10} | {'Registrations':<15}")
    print("-" * 60)
    
    for exam_name in target_exams:
        # Find all templates with this name
        templates = pd.read_sql_query(f"SELECT id, name FROM exam_templates WHERE name LIKE '%{exam_name}%'", conn)
        
        for _, t in templates.iterrows():
            t_id = t['id']
            t_name = t['name']
            
            # Count questions
            q_count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM questions WHERE exam_template_id = {t_id}", conn).iloc[0]['count']
            
            # Count registrations
            r_count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM exam_registrations WHERE exam_template_id = {t_id}", conn).iloc[0]['count']
            
            print(f"{t_name:<20} | {t_id:<5} | {q_count:<10} | {r_count:<15}")
            
            results.append({
                'name': t_name,
                'id': t_id,
                'questions': q_count,
                'registrations': r_count
            })

    conn.close()

if __name__ == "__main__":
    diagnose_exams()
