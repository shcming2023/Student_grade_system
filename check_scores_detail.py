import sqlite3
import pandas as pd

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def check_scores():
    conn = sqlite3.connect(DB_PATH)
    
    target_exams = ['G4牛津英语', '袋鼠数学A', '袋鼠数学B', 'AMC8']
    
    print(f"{'Student':<15} | {'Exam':<15} | {'T_ID':<5} | {'Scores (Current)':<16} | {'Scores (Other IDs)':<18}")
    print("-" * 80)
    
    for exam_name in target_exams:
        # Get all registrations for this exam name
        query = f"""
        SELECT s.name as student_name, s.id as student_id, et.id as template_id, et.name as template_name
        FROM exam_registrations er
        JOIN students s ON er.student_id = s.id
        JOIN exam_templates et ON er.exam_template_id = et.id
        WHERE et.name LIKE '%{exam_name}%'
        """
        regs = pd.read_sql_query(query, conn)
        
        for _, reg in regs.iterrows():
            s_id = reg['student_id']
            t_id = reg['template_id']
            s_name = reg['student_name']
            t_name = reg['template_name']
            
            # Count scores for this student linked to questions in THIS template
            score_query = f"""
            SELECT COUNT(*) as count 
            FROM scores s
            JOIN questions q ON s.question_id = q.id
            WHERE s.student_id = {s_id} AND q.exam_template_id = {t_id}
            """
            current_count = pd.read_sql_query(score_query, conn).iloc[0]['count']
            
            # Count scores for this student linked to questions in OTHER templates with SAME name
            other_score_query = f"""
            SELECT COUNT(*) as count 
            FROM scores s
            JOIN questions q ON s.question_id = q.id
            JOIN exam_templates et ON q.exam_template_id = et.id
            WHERE s.student_id = {s_id} 
            AND et.name = '{t_name}'
            AND et.id != {t_id}
            """
            other_count = pd.read_sql_query(other_score_query, conn).iloc[0]['count']
            
            print(f"{s_name:<15} | {t_name:<15} | {t_id:<5} | {current_count:<16} | {other_count:<18}")

    conn.close()

if __name__ == "__main__":
    check_scores()
