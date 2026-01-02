import sqlite3
import pandas as pd

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def fix_g6_scores():
    conn = sqlite3.connect(DB_PATH)
    
    src_template_id = 91  # G6先锋英语
    dest_template_id = 118 # G6朗文英语
    student_name = 'Nico'
    
    print(f"Migrating {student_name}: {src_template_id} -> {dest_template_id}")
    
    # 1. Get Source Scores (Student 58)
    # Find student ID for Nico in Source Template
    src_query = f"""
    SELECT DISTINCT s.id 
    FROM scores sc
    JOIN questions q ON sc.question_id = q.id
    JOIN students s ON sc.student_id = s.id
    WHERE q.exam_template_id = {src_template_id} AND s.name = '{student_name}'
    """
    src_s_ids = pd.read_sql_query(src_query, conn)['id'].tolist()
    print(f"Source Student IDs: {src_s_ids}")
    
    if not src_s_ids:
        print("No source scores found.")
        return

    # 2. Get Dest Student ID (Student 52 or 65)
    dest_query = f"""
    SELECT DISTINCT s.id
    FROM exam_registrations er
    JOIN students s ON er.student_id = s.id
    WHERE er.exam_template_id = {dest_template_id} AND s.name = '{student_name}'
    """
    dest_s_ids = pd.read_sql_query(dest_query, conn)['id'].tolist()
    print(f"Dest Student IDs: {dest_s_ids}")
    
    if not dest_s_ids:
        print("No dest registration found.")
        return
    
    dest_s_id = dest_s_ids[0] # Use first one
    
    # 3. Map Questions
    src_qs = pd.read_sql_query(f"SELECT id, question_number FROM questions WHERE exam_template_id={src_template_id}", conn)
    dest_qs = pd.read_sql_query(f"SELECT id, question_number FROM questions WHERE exam_template_id={dest_template_id}", conn)
    
    # Normalize dest question numbers (remove .0 if present)
    def normalize(x):
        try:
            return str(int(float(x)))
        except:
            return str(x)
            
    dest_qs['normalized_num'] = dest_qs['question_number'].apply(normalize)
    dest_map = dict(zip(dest_qs['normalized_num'], dest_qs['id']))
    
    print(f"Mapped {len(dest_map)} dest questions.")
    
    cursor = conn.cursor()
    count = 0
    
    for s_id in src_s_ids:
        scores = pd.read_sql_query(f"""
            SELECT sc.score, q.question_number 
            FROM scores sc
            JOIN questions q ON sc.question_id = q.id
            WHERE sc.student_id = {s_id} AND q.exam_template_id = {src_template_id}
        """, conn)
        
        for _, row in scores.iterrows():
            q_num = normalize(row['question_number']) # Normalize source too
            score_val = row['score']
            
            if q_num in dest_map:
                dest_q_id = dest_map[q_num]
                try:
                    cursor.execute("""
                        INSERT INTO scores (student_id, question_id, score)
                        VALUES (?, ?, ?)
                    """, (int(dest_s_id), int(dest_q_id), float(score_val)))
                    count += 1
                except sqlite3.IntegrityError:
                    pass
                    
    print(f"Migrated {count} scores.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_g6_scores()
