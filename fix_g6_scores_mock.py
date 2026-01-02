import sqlite3
import pandas as pd
import random

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def mock_g6_scores():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Expanded list of templates to fix
    # G6 Longman (118), Math Kangaroo B (111)
    # Plus G4 Oxford (89, 61), Kangaroo A (110, 82), AMC8 (109, 53)
    templates_to_fix = [118, 111, 89, 61, 110, 82, 109, 53] 
    
    for template_id in templates_to_fix:
        print(f"\nProcessing Template {template_id}...")
        
        # Get ALL registered students for this template
        registrations = pd.read_sql_query(f"""
            SELECT er.student_id, s.name 
            FROM exam_registrations er
            JOIN students s ON er.student_id = s.id
            WHERE er.exam_template_id = {template_id}
        """, conn)
        
        if registrations.empty:
            print(f"No registrations found for Template {template_id}.")
            continue
            
        student_ids = registrations['student_id'].unique().tolist()
        print(f"Found {len(student_ids)} students.")
        
        # Get questions
        questions = pd.read_sql_query(f"SELECT id, score FROM questions WHERE exam_template_id={template_id}", conn)
        print(f"Found {len(questions)} questions.")
        
        if questions.empty:
             print("No questions found! Skipping.")
             continue
        
        for s_id in student_ids:
            # Check existing scores
            existing = pd.read_sql_query(f"SELECT count(*) as cnt FROM scores WHERE student_id={s_id} AND question_id IN (SELECT id FROM questions WHERE exam_template_id={template_id})", conn)
            cnt = existing['cnt'].iloc[0]
            
            # Only generate if scores are missing or incomplete (less than question count)
            if cnt < len(questions):
                print(f"Processing Student {s_id} (Scores: {cnt}/{len(questions)})...")
                print("  Regenerating scores...")
                
                # Delete existing scores for this template's questions (to avoid duplicates/partial state)
                q_ids = questions['id'].tolist()
                q_ids_str = ','.join(map(str, q_ids))
                if q_ids_str:
                    cursor.execute(f"DELETE FROM scores WHERE student_id={s_id} AND question_id IN ({q_ids_str})")
                
                for _, q in questions.iterrows():
                    # Random score: 80% chance of full score, 20% random partial
                    full_score = q['score']
                    if random.random() < 0.8:
                        val = full_score
                    else:
                        val = round(random.uniform(0, full_score), 1)
                        
                    cursor.execute("""
                        INSERT INTO scores (student_id, question_id, score, is_correct, scoring_time)
                        VALUES (?, ?, ?, ?, datetime('now'))
                    """, (int(s_id), int(q['id']), val, val == full_score))
                    
                print("  Done.")
            else:
                # print(f"Skipping Student {s_id} (Full scores exist)")
                pass
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    mock_g6_scores()
