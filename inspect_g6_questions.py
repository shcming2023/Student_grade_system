import sqlite3
import pandas as pd

DB_PATH = 'Student_grade_system/wtf_exam_system.db'

def inspect_questions():
    conn = sqlite3.connect(DB_PATH)
    
    # Template 91
    q91 = pd.read_sql_query("SELECT id, question_number FROM questions WHERE exam_template_id=91", conn)
    print("Template 91 Questions (first 5):")
    print(q91.head())
    
    # Template 118
    q118 = pd.read_sql_query("SELECT id, question_number FROM questions WHERE exam_template_id=118", conn)
    print("\nTemplate 118 Questions (first 5):")
    print(q118.head())
    
    # Check intersection
    common = set(q91['question_number']).intersection(set(q118['question_number']))
    print(f"\nCommon Question Numbers: {len(common)}")
    
    conn.close()

if __name__ == "__main__":
    inspect_questions()
