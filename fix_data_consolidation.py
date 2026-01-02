import sqlite3
import pandas as pd

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def copy_scores(conn, student_name, src_template_id, dest_template_id):
    print(f"Processing {student_name}: Template {src_template_id} -> {dest_template_id}")
    
    # Get Student ID
    s_df = pd.read_sql_query(f"SELECT id FROM students WHERE name='{student_name}'", conn)
    if s_df.empty:
        print(f"Student {student_name} not found!")
        return
    s_id = s_df.iloc[0]['id']
    
    # Get Questions Mapping (Question Number -> ID)
    src_qs = pd.read_sql_query(f"SELECT id, question_number FROM questions WHERE exam_template_id={src_template_id}", conn)
    dest_qs = pd.read_sql_query(f"SELECT id, question_number FROM questions WHERE exam_template_id={dest_template_id}", conn)
    
    print(f"Debug: Src T={src_template_id} Qs={len(src_qs)}, Dest T={dest_template_id} Qs={len(dest_qs)}")
    
    if src_qs.empty or dest_qs.empty:
        print("Source or Dest questions empty!")
        return

    # Create map: Q_Num -> Dest_Q_ID
    dest_map = dict(zip(dest_qs['question_number'], dest_qs['id']))
    
    # Get Source Scores
    q_ids_str = ','.join(map(str, src_qs['id'].tolist()))
    scores_query = f"SELECT * FROM scores WHERE student_id={s_id} AND question_id IN ({q_ids_str})"
    # print(f"Debug Query: {scores_query}")
    scores = pd.read_sql_query(scores_query, conn)
    print(f"Found {len(scores)} scores in source for Student ID {s_id}.")
    
    cursor = conn.cursor()
    count = 0
    for _, score in scores.iterrows():
        # Find corresponding source question number
        src_q_row = src_qs[src_qs['id'] == score['question_id']]
        if src_q_row.empty:
            continue
        q_num = src_q_row.iloc[0]['question_number']
        
        # Find corresponding dest question id
        if q_num in dest_map:
            dest_q_id = dest_map[q_num]
            score_val = score['score']
            
            # Insert or Update
            try:
                cursor.execute("""
                    INSERT INTO scores (student_id, question_id, score)
                    VALUES (?, ?, ?)
                """, (int(s_id), int(dest_q_id), float(score_val)))
                count += 1
            except sqlite3.IntegrityError:
                # Already exists? Update?
                pass
                
    print(f"Copied {count} scores.")
    conn.commit()

def consolidate_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. G4 Oxford: Nico 61 -> 89
    copy_scores(conn, 'Nico', 61, 89)
    # Remove duplicate reg? No, just ensure 89 is used.
    
    # 2. AMC8: Nico 53 -> 109
    copy_scores(conn, 'Nico', 53, 109)
    # Cleanup regs: Delete 53, 81. Keep 109.
    s_id_nico = pd.read_sql_query("SELECT id FROM students WHERE name='Nico'", conn).iloc[0]['id']
    cursor.execute(f"DELETE FROM exam_registrations WHERE student_id={s_id_nico} AND exam_template_id IN (53, 81)")
    print("Cleaned AMC8 regs for Nico.")

    # 3. Math A: Nico 54 -> 110
    copy_scores(conn, 'Nico', 54, 110)
    # Move Wei Ruixi (82 -> 110)
    wei_df = pd.read_sql_query("SELECT id FROM students WHERE name='魏睿希'", conn)
    if not wei_df.empty:
        wei_id = wei_df.iloc[0]['id']
        cursor.execute(f"UPDATE exam_registrations SET exam_template_id=110 WHERE student_id={wei_id} AND exam_template_id=82")
        print("Moved Wei Ruixi to Template 110")
    
    # Move Lin Junhan (110 -> 110) - Already there.
    
    # Cleanup Nico Math A regs: Delete 54, 82. Keep 110.
    cursor.execute(f"DELETE FROM exam_registrations WHERE student_id={s_id_nico} AND exam_template_id IN (54, 82)")
    print("Cleaned Math A regs for Nico.")
    
    # 4. Math B: Nico (Keep 111, Delete 55, 83)
    cursor.execute(f"DELETE FROM exam_registrations WHERE student_id={s_id_nico} AND exam_template_id IN (55, 83)")
    print("Cleaned Math B regs for Nico.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    consolidate_data()
