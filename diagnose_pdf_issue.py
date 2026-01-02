
import sqlite3
import os

# 连接数据库
db_path = 'Student_grade_system/wtf_exam_system.db'
if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 目标试卷关键词
keywords = ['G6朗文', 'G4牛津', '袋鼠', 'AMC8']

print("--- 1. 检查试卷模板 (ExamTemplate) ---")
found_templates = []
for kw in keywords:
    cursor.execute(f"SELECT id, name, grade_level, total_questions FROM exam_templates WHERE name LIKE '%{kw}%'")
    rows = cursor.fetchall()
    if not rows:
        print(f"[WARNING] 未找到包含 '{kw}' 的试卷模板")
    else:
        for row in rows:
            print(f"Found: ID={row[0]}, Name='{row[1]}', Grade={row[2]}, Questions={row[3]}")
            found_templates.append(row[0])

print("\n--- 2. 检查题目关联 (Questions) ---")
for tid in found_templates:
    cursor.execute(f"SELECT COUNT(*) FROM questions WHERE exam_template_id = ?", (tid,))
    count = cursor.fetchone()[0]
    cursor.execute(f"SELECT name FROM exam_templates WHERE id = ?", (tid,))
    name = cursor.fetchone()[0]
    print(f"Template '{name}' (ID={tid}) has {count} questions.")
    
    if count == 0:
        print(f"  [CRITICAL] 试卷 '{name}' 没有关联题目！这会导致成绩单无内容。")

print("\n--- 3. 检查报名记录 (ExamRegistration) ---")
registered_template_ids = set()
for tid in found_templates:
    cursor.execute(f"SELECT COUNT(*) FROM exam_registrations WHERE exam_template_id = ?", (tid,))
    count = cursor.fetchone()[0]
    cursor.execute(f"SELECT name FROM exam_templates WHERE id = ?", (tid,))
    name = cursor.fetchone()[0]
    print(f"Template '{name}' (ID={tid}) has {count} registrations.")
    if count > 0:
        registered_template_ids.add(tid)

print("\n--- 4. 检查分数记录 (Scores) ---")
for tid in registered_template_ids:
    # 找一个报名了该试卷的学生
    cursor.execute(f"SELECT student_id, id FROM exam_registrations WHERE exam_template_id = ? LIMIT 1", (tid,))
    reg = cursor.fetchone()
    if reg:
        student_id = reg[0]
        reg_id = reg[1]
        
        cursor.execute(f"SELECT name FROM exam_templates WHERE id = ?", (tid,))
        t_name = cursor.fetchone()[0]
        
        # 检查该学生在该试卷上的分数
        # Score 表关联的是 question_id，我们需要先找出该试卷的所有 question_id
        cursor.execute(f"SELECT id FROM questions WHERE exam_template_id = ?", (tid,))
        q_ids = [row[0] for row in cursor.fetchall()]
        
        if not q_ids:
            print(f"  [Skip] Template '{t_name}' has no questions.")
            continue
            
        placeholders = ','.join(['?'] * len(q_ids))
        query = f"SELECT COUNT(*) FROM scores WHERE student_id = ? AND question_id IN ({placeholders})"
        cursor.execute(query, (student_id, *q_ids))
        score_count = cursor.fetchone()[0]
        
        print(f"Template '{t_name}' - Student ID {student_id}: Has {score_count} scores recorded (Expected approx {len(q_ids)}).")
        
        if score_count == 0:
             print(f"  [WARNING] 试卷 '{t_name}' 有报名但无分数记录。")

conn.close()
