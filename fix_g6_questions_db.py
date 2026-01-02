import sqlite3
import pandas as pd

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def fix_g6_questions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get questions for Template 118
    df = pd.read_sql_query("SELECT id, question_number FROM questions WHERE exam_template_id=118", conn)
    
    print(f"Found {len(df)} questions for Template 118.")
    
    updated_count = 0
    for _, row in df.iterrows():
        q_id = row['id']
        q_num = str(row['question_number'])
        
        new_num = q_num
        if q_num.endswith('.0'):
            new_num = str(int(float(q_num)))
            
        if new_num != q_num:
            cursor.execute("UPDATE questions SET question_number = ? WHERE id = ?", (new_num, q_id))
            updated_count += 1
            
    conn.commit()
    conn.close()
    print(f"Updated {updated_count} questions.")

if __name__ == "__main__":
    fix_g6_questions()
