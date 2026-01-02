import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlite3
import os

DB_PATH = 'wtf_exam_system.db'

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create association table
    print("Creating exam_template_sessions table...")
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exam_template_sessions (
        exam_template_id INTEGER NOT NULL,
        exam_session_id INTEGER NOT NULL,
        PRIMARY KEY (exam_template_id, exam_session_id),
        FOREIGN KEY(exam_template_id) REFERENCES exam_templates(id),
        FOREIGN KEY(exam_session_id) REFERENCES exam_sessions(id)
    )
    ''')

    # 2. Migrate existing data
    print("Migrating data...")
    # Check if exam_session_id column exists in exam_templates (it might not if this is re-run after model change, but we are accessing DB directly)
    try:
        cursor.execute('SELECT id, exam_session_id FROM exam_templates WHERE exam_session_id IS NOT NULL')
        templates = cursor.fetchall()
        
        count = 0
        for t_id, s_id in templates:
            # Check if exists
            cursor.execute('SELECT 1 FROM exam_template_sessions WHERE exam_template_id=? AND exam_session_id=?', (t_id, s_id))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO exam_template_sessions (exam_template_id, exam_session_id) VALUES (?, ?)', (t_id, s_id))
                count += 1
        
        print(f"Migrated {count} relationships.")
    except Exception as e:
        print(f"Migration warning: {e}")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        migrate()
    else:
        print(f"Database {DB_PATH} not found.")
