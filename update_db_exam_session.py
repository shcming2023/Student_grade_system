
import sqlite3
import os

db_path = '/opt/Way To Future考试管理系统/wtf_exam_system.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check and update ExamSession table
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exam_sessions'")
    if cursor.fetchone():
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='exam_sessions'")
        create_sql = cursor.fetchone()[0]
        
        # Check if columns exist
        columns_to_add = []
        if 'exam_name_en' not in create_sql:
            columns_to_add.append("ADD COLUMN exam_name_en VARCHAR(100)")
        if 'company_brand' not in create_sql:
            columns_to_add.append("ADD COLUMN company_brand VARCHAR(100)")
            
        for col_def in columns_to_add:
            try:
                # SQLite supports ADD COLUMN
                sql = f"ALTER TABLE exam_sessions {col_def}"
                cursor.execute(sql)
                print(f"Executed: {sql}")
            except Exception as e:
                print(f"Failed to add column: {e}")
                
    else:
        print("ExamSessions table not found.")

except Exception as e:
    print(f"Error updating ExamSession: {e}")

conn.commit()
conn.close()
