
import sqlite3
import os

db_path = '/opt/Way To Future考试管理系统/wtf_exam_system.db'

# Force migration script
print(f"Connecting to database at {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current columns
cursor.execute("PRAGMA table_info(exam_sessions)")
columns = [info[1] for info in cursor.fetchall()]
print(f"Current columns in exam_sessions: {columns}")

# Add columns if missing
if 'exam_name_en' not in columns:
    print("Adding column: exam_name_en")
    try:
        cursor.execute("ALTER TABLE exam_sessions ADD COLUMN exam_name_en VARCHAR(100)")
        print("Success.")
    except Exception as e:
        print(f"Error adding exam_name_en: {e}")

if 'company_brand' not in columns:
    print("Adding column: company_brand")
    try:
        cursor.execute("ALTER TABLE exam_sessions ADD COLUMN company_brand VARCHAR(100)")
        print("Success.")
    except Exception as e:
        print(f"Error adding company_brand: {e}")

conn.commit()
conn.close()
print("Migration completed.")
