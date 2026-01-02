import pandas as pd
import sqlite3
import os

DB_PATH = 'Student_grade_system/wtf_exam_system.db'
EXCEL_PATH_1 = 'Student_grade_system/基础数据/WTF学术测评考卷登记表.xlsx'
EXCEL_PATH_2 = 'Student_grade_system/基础数据/2025秋季第一学期WTF考卷登记表4.0.xlsx'

# Mapping: Sheet Name -> (Excel Path, List of Exam Template Names)
# We will find all template IDs for the given names and import questions if count is 0.
TASKS = [
    {
        'sheet': 'AMC8',
        'excel': EXCEL_PATH_1,
        'template_names': ['AMC8']
    },
    {
        'sheet': '袋鼠数学A',
        'excel': EXCEL_PATH_1,
        'template_names': ['袋鼠数学A']
    },
    {
        'sheet': '袋鼠数学B',
        'excel': EXCEL_PATH_1,
        'template_names': ['袋鼠数学B']
    },
    {
        'sheet': 'G4牛津英语',
        'excel': EXCEL_PATH_2,
        'template_names': ['G4牛津英语']
    }
]

def run_import():
    print(f"Connecting to DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for task in TASKS:
        sheet = task['sheet']
        excel_path = task['excel']
        names = task['template_names']
        
        print(f"\nProcessing Task: {sheet} -> {names}")
        
        if not os.path.exists(excel_path):
            print(f"  Error: Excel file not found: {excel_path}")
            continue

        # 1. Find target template IDs
        placeholders = ','.join(['?'] * len(names))
        cursor.execute(f"SELECT id, name FROM exam_templates WHERE name IN ({placeholders})", names)
        templates = cursor.fetchall()
        
        if not templates:
            print(f"  No templates found for names: {names}")
            continue
            
        print(f"  Found templates: {templates}")
        
        # 2. Read Excel Data
        try:
            # Try reading with header=1 first (common format in this project)
            # But let's check columns first to be safe or try/catch logic
            # Based on previous checks:
            # AMC8/Kangaroo: row 0 is header? 
            #   AMC8 Unnamed: 1 ...
            #   0 题号 模块 ...
            # So header is row 1 (index 1).
            
            # G4 Oxford:
            #   G4牛津英语 Unnamed: 1 ...
            #   0 题号 模块 ...
            # So header is also row 1.
            
            df = pd.read_excel(excel_path, sheet_name=sheet, engine='openpyxl', header=1)
            print(f"  Read {len(df)} rows from Excel.")
            # print("  Columns:", df.columns.tolist())
        except Exception as e:
            print(f"  Error reading Excel sheet '{sheet}': {e}")
            continue

        # 3. Process each template
        for t_id, t_name in templates:
            # Check if questions exist
            cursor.execute("SELECT count(*) FROM questions WHERE exam_template_id = ?", (t_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"  [Skipping] Template {t_id} ({t_name}) already has {count} questions.")
                continue
                
            print(f"  [Importing] Template {t_id} ({t_name})...")
            
            questions_to_insert = []
            for index, row in df.iterrows():
                try:
                    # Flexible column mapping
                    q_num = row.get('题号')
                    module = row.get('模块')
                    kp = row.get('知识点') or row.get('核心知识点/技能')
                    # q_type = row.get('题型') # Removed from schema
                    score = row.get('分值')
                    
                    if pd.isna(q_num) or pd.isna(score):
                        continue
                        
                    questions_to_insert.append((t_id, q_num, module, kp, score))
                except Exception as e:
                    pass # Skip bad rows

            if questions_to_insert:
                cursor.executemany("""
                    INSERT INTO questions (exam_template_id, question_number, module, knowledge_point, score)
                    VALUES (?, ?, ?, ?, ?)
                """, questions_to_insert)
                print(f"    Inserted {len(questions_to_insert)} questions.")
            else:
                print("    No valid questions found to insert.")
                
    conn.commit()
    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    run_import()
