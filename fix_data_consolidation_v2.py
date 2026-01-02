import sqlite3
import pandas as pd

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def migrate_scores_by_name(conn, student_name, src_template_id, dest_template_id):
    print(f"\n--- Migrating {student_name}: Template {src_template_id} -> {dest_template_id} ---")
    
    # 1. Find Source Student IDs (any student with this name having scores in src template)
    src_query = f"""
    SELECT DISTINCT s.id 
    FROM scores sc
    JOIN questions q ON sc.question_id = q.id
    JOIN students s ON sc.student_id = s.id
    WHERE q.exam_template_id = {src_template_id} AND s.name = '{student_name}'
    """
    src_student_ids = pd.read_sql_query(src_query, conn)['id'].tolist()
    
    if not src_student_ids:
        print(f"No scores found for any '{student_name}' in Template {src_template_id}")
        return

    print(f"Found source student IDs with scores: {src_student_ids}")
    
    # 2. Find Dest Student ID (the one registered in dest template)
    dest_query = f"""
    SELECT DISTINCT s.id
    FROM exam_registrations er
    JOIN students s ON er.student_id = s.id
    WHERE er.exam_template_id = {dest_template_id} AND s.name = '{student_name}'
    """
    dest_student_ids = pd.read_sql_query(dest_query, conn)['id'].tolist()
    
    if not dest_student_ids:
        print(f"No registration found for '{student_name}' in Template {dest_template_id}")
        # Optional: Create registration?
        return
        
    dest_student_id = dest_student_ids[0] # Assume one valid registration per template
    print(f"Targeting Dest Student ID: {dest_student_id}")
    
    # 3. Map Questions
    src_qs = pd.read_sql_query(f"SELECT id, question_number FROM questions WHERE exam_template_id={src_template_id}", conn)
    dest_qs = pd.read_sql_query(f"SELECT id, question_number FROM questions WHERE exam_template_id={dest_template_id}", conn)
    dest_map = dict(zip(dest_qs['question_number'], dest_qs['id']))
    
    # 4. Copy Scores
    cursor = conn.cursor()
    count = 0
    
    for s_id in src_student_ids:
        # Get scores for this source student
        scores = pd.read_sql_query(f"""
            SELECT sc.score, q.question_number 
            FROM scores sc
            JOIN questions q ON sc.question_id = q.id
            WHERE sc.student_id = {s_id} AND q.exam_template_id = {src_template_id}
        """, conn)
        
        for _, row in scores.iterrows():
            q_num = row['question_number']
            score_val = row['score']
            
            if q_num in dest_map:
                dest_q_id = dest_map[q_num]
                try:
                    cursor.execute("""
                        INSERT INTO scores (student_id, question_id, score)
                        VALUES (?, ?, ?)
                    """, (int(dest_student_id), int(dest_q_id), float(score_val)))
                    count += 1
                except sqlite3.IntegrityError:
                    pass # Already exists
                    
    print(f"Successfully migrated {count} scores to Student {dest_student_id}.")
    conn.commit()

def fix_nico_and_others():
    conn = sqlite3.connect(DB_PATH)
    
    # G4 Oxford
    migrate_scores_by_name(conn, 'Nico', 61, 89)
    
    # AMC8
    migrate_scores_by_name(conn, 'Nico', 53, 109)
    
    # Math A
    migrate_scores_by_name(conn, 'Nico', 54, 110)
    
    conn.close()

if __name__ == "__main__":
    fix_nico_and_others()
