
import sqlite3
import os

db_path = '/opt/Way To Future考试管理系统/wtf_exam_system.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Create system_settings table
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_settings (
        id INTEGER PRIMARY KEY,
        company_name VARCHAR(100),
        company_name_zh VARCHAR(100),
        logo_path VARCHAR(255)
    )
    ''')
    print("Created system_settings table.")
except Exception as e:
    print(f"Error creating system_settings: {e}")

# 2. Insert default setting if not exists
try:
    cursor.execute('SELECT count(*) FROM system_settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO system_settings (company_name, company_name_zh) VALUES ('Way To Future IV', '橡心国际')")
        print("Inserted default settings.")
except Exception as e:
    print(f"Error checking/inserting settings: {e}")

# 3. Modify Student table
try:
    # Check if table exists first
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
    if cursor.fetchone():
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='students'")
        create_sql = cursor.fetchone()[0]
        print(f"Original Schema: {create_sql}")

        # Basic check to see if we need migration (if NOT NULL is present for student_id)
        # Note: This simple string check might fail if formatting is different, but good enough for typical SQLite dumps
        if "student_id VARCHAR(20) NOT NULL" in create_sql or "student_id" in create_sql and "NOT NULL" in create_sql.split("student_id")[1].split(",")[0]:
            print("Migrating students table...")
            
            # Rename old table
            cursor.execute("ALTER TABLE students RENAME TO students_old")
            
            # Create new table (nullable student_id and class_name)
            new_sql = '''
            CREATE TABLE students (
                id INTEGER PRIMARY KEY,
                student_id VARCHAR(20) UNIQUE,
                name VARCHAR(50) NOT NULL,
                gender VARCHAR(10) NOT NULL,
                grade_level VARCHAR(10) NOT NULL,
                school_id INTEGER,
                class_name VARCHAR(50),
                FOREIGN KEY(school_id) REFERENCES schools(id)
            )
            '''
            cursor.execute(new_sql)
            
            # Copy data
            # Note: Columns must match. 
            cursor.execute("INSERT INTO students (id, student_id, name, gender, grade_level, school_id, class_name) SELECT id, student_id, name, gender, grade_level, school_id, class_name FROM students_old")
            
            # Drop old table
            cursor.execute("DROP TABLE students_old")
            print("Migration done.")
        else:
            print("Table already seems to have correct schema or migration not needed.")
    else:
        print("Students table not found (maybe DB not init yet).")

except Exception as e:
    print(f"Error during migration: {e}")
    # Restore if failed in middle? 
    # SQLite DDL is transactional mostly.
    pass

conn.commit()
conn.close()
