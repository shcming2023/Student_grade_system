import pandas as pd
import sqlite3
import os

DB_PATH = 'Student_grade_system/wtf_exam_system.db'
EXCEL_PATH = 'Student_grade_system/基础数据/2025秋季第一学期WTF考卷登记表4.0.xlsx'
SHEET_NAME = 'G6先锋英语'
TARGET_TEMPLATE_ID = 118 # G6朗文英语

def fix_g6_data():
    print(f"Connecting to DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Verify Target Template
    cursor.execute("SELECT id, name FROM exam_templates WHERE id = ?", (TARGET_TEMPLATE_ID,))
    tpl = cursor.fetchone()
    if not tpl:
        print(f"Template ID {TARGET_TEMPLATE_ID} not found!")
        return
    print(f"Found Target Template: {tpl}")

    # 2. Check existing questions
    cursor.execute("SELECT count(*) FROM questions WHERE exam_template_id = ?", (TARGET_TEMPLATE_ID,))
    count = cursor.fetchone()[0]
    print(f"Current question count: {count}")
    
    if count > 0:
        print("Questions already exist. Skipping import.")
        # return # Optional: force overwrite? For now safe skip.

    # 3. Read Excel
    print(f"Reading Excel: {EXCEL_PATH} Sheet: {SHEET_NAME}")
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, engine='openpyxl')
        print(f"Read {len(df)} rows.")
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    # 4. Import Questions
    # Expected columns in DB: exam_template_id, question_number, module, knowledge_point, question_type, score
    # Expected columns in Excel: 题号, 模块, 知识点, 题型, 分值 (based on previous check)
    
    # Map columns
    # Excel: '题号', '模块', '知识点', '题型', '分值'
    # Note: previous output showed columns: ['G6英语', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4']
    # And row 0 contains headers.
    
    # We need to handle the header row correctly.
    # Previous check_excel_data output:
    #   G6英语 Unnamed: 1                 Unnamed: 2 Unnamed: 3 Unnamed: 4
    # 0   题号         模块                        知识点         题型         分值
    # 1    1         词汇  音标认读与单词拼写 (名词:resolution)     看音标写单词          1
    
    # So we need to reload with header=1 (row 1 as header, 0-indexed) or just slice.
    
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, engine='openpyxl', header=1)
    print("Columns after header=1:", df.columns.tolist())
    
    # Standardize column names if needed
    # Expected: 题号, 模块, 知识点, 题型, 分值
    # Let's map based on position or name
    
    questions_to_insert = []
    for index, row in df.iterrows():
        try:
            q_num = row['题号']
            module = row['模块']
            kp = row['知识点']
            q_type = row['题型']
            score = row['分值']
            
            # Basic validation
            if pd.isna(q_num) or pd.isna(score):
                continue
                
            questions_to_insert.append((TARGET_TEMPLATE_ID, q_num, module, kp, score))
        except Exception as e:
            print(f"Skipping row {index}: {e}")

    print(f"Prepared {len(questions_to_insert)} questions for insertion.")
    
    if questions_to_insert:
        cursor.executemany("""
            INSERT INTO questions (exam_template_id, question_number, module, knowledge_point, score)
            VALUES (?, ?, ?, ?, ?)
        """, questions_to_insert)
        conn.commit()
        print("Successfully inserted questions.")
    
    conn.close()

if __name__ == "__main__":
    fix_g6_data()
