import sqlite3
import os

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def check_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    target_names = ['%G6朗文%', '%G4牛津%', '%袋鼠%', '%AMC8%']
    
    print(f"{'Template ID':<12} {'Template Name':<20} {'Reg Count':<10}")
    print("-" * 50)
    
    for name_pattern in target_names:
        cursor.execute("SELECT id, name FROM exam_templates WHERE name LIKE ?", (name_pattern,))
        templates = cursor.fetchall()
        
        for t_id, t_name in templates:
            cursor.execute("SELECT count(*) FROM exam_registrations WHERE exam_template_id = ?", (t_id,))
            reg_count = cursor.fetchone()[0]
            
            if reg_count > 0:
                print(f"{t_id:<12} {t_name:<20} {reg_count:<10}")
                
                # Check registrations detail
                cursor.execute("""
                    SELECT r.id, s.name, es.id, es.name,
                           (SELECT count(*) FROM scores WHERE student_id = r.student_id AND question_id IN (SELECT id FROM questions WHERE exam_template_id = ?)) as score_count,
                           (SELECT sum(score) FROM scores WHERE student_id = r.student_id AND question_id IN (SELECT id FROM questions WHERE exam_template_id = ?)) as total_score
                    FROM exam_registrations r
                    JOIN students s ON r.student_id = s.id
                    JOIN exam_sessions es ON r.exam_session_id = es.id
                    WHERE r.exam_template_id = ?
                """, (t_id, t_id, t_id))
                
                regs = cursor.fetchall()
                for r_id, s_name, es_id, es_name, s_count, s_total in regs:
                    print(f"    RegID: {r_id}, Student: {s_name}, Session: {es_id} ({es_name}), Scores: {s_count}, Total: {s_total}")
            # else:
            #     print(f"{t_id:<12} {t_name:<20} 0 (No regs)")

    conn.close()

if __name__ == "__main__":
    check_data()
