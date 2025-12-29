
import sqlite3
import os

db_path = '/opt/Way To Future考试管理系统/wtf_exam_system.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Create system_settings table
cursor.execute('''
CREATE TABLE IF NOT EXISTS system_settings (
    id INTEGER PRIMARY KEY,
    company_name VARCHAR(100),
    company_name_zh VARCHAR(100),
    logo_path VARCHAR(255)
)
''')

# 2. Insert default setting if not exists
cursor.execute('SELECT count(*) FROM system_settings')
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO system_settings (company_name, company_name_zh) VALUES ('Way To Future IV', '橡心国际')")

# 3. Modify Student table (allow nullable student_id and class_name)
# SQLite doesn't support ALTER TABLE ALTER COLUMN. We have to rename, create new, copy, drop.
# Or we can just try to insert NULLs and see if it fails (it will if created with NOT NULL).
# Let's inspect the schema first.
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='students'")
create_sql = cursor.fetchone()[0]
print(f"Original Schema: {create_sql}")

if "student_id VARCHAR(20) NOT NULL" in create_sql or "class_name VARCHAR(50)" in create_sql:
    print("Migrating students table...")
    
    # Rename old table
    cursor.execute("ALTER TABLE students RENAME TO students_old")
    
    # Create new table (nullable student_id and class_name)
    # Note: We must recreate foreign keys correctly.
    # Original:
    # student_id = db.Column(db.String(20), unique=True, nullable=False) -> nullable=True
    # class_name = db.Column(db.String(50)) -> It was nullable by default in previous SQL code? 
    # Wait, in the code I read earlier: class_name = db.Column(db.String(50)) (default nullable=True in SQLAlchemy?)
    # But student_id was nullable=False.
    
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
    cursor.execute("INSERT INTO students SELECT id, student_id, name, gender, grade_level, school_id, class_name FROM students_old")
    
    # Drop old table
    cursor.execute("DROP TABLE students_old")
    print("Migration done.")

conn.commit()
conn.close()
