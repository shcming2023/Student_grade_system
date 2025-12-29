
import sqlite3
import os

# Correct DB Path: Student_grade_system/wtf_exam_system.db
db_path = 'Student_grade_system/wtf_exam_system.db'

print(f"Connecting to database at {os.path.abspath(db_path)}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check exam_sessions
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

# Also check SystemSetting table
cursor.execute("PRAGMA table_info(system_settings)")
sys_cols = [info[1] for info in cursor.fetchall()]
if not sys_cols:
    print("system_settings table missing, creating...")
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY,
            company_name VARCHAR(100),
            company_name_zh VARCHAR(100),
            logo_path VARCHAR(255)
        )
        ''')
        cursor.execute("INSERT INTO system_settings (company_name, company_name_zh) VALUES ('Way To Future IV', '橡心国际')")
        print("Created system_settings.")
    except Exception as e:
        print(f"Error creating system_settings: {e}")

# Check Students table (migration needed?)
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='students'")
res = cursor.fetchone()
if res:
    create_sql = res[0]
    print(f"Student Schema: {create_sql}")
    # If we need to fix students (nullable), we should do it here too if needed.
    # But user said Student Archives works, so maybe it's fine or already compatible.
    
conn.commit()
conn.close()
print("Migration completed on CORRECT database.")
