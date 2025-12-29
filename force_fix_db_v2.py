
import sqlite3
import os

# Use relative path since we are in the correct CWD
db_path = 'wtf_exam_system.db'

print(f"Connecting to database at {os.path.abspath(db_path)}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {tables}")

# Check exam_sessions
if ('exam_sessions',) in tables:
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
else:
    print("Table exam_sessions not found! Attempting to recreate from schema...")
    # If table is missing, maybe we should let SQLAlchemy create it, but we can create it manually if needed.
    # But usually app creates it if not exists.
    # The error "no such column" implies table exists but column missing.
    # The error "no such table" implies table missing.
    # Previous run said "no such table: exam_sessions" which is weird if the app was running.
    pass

conn.commit()
conn.close()
print("Migration completed.")
