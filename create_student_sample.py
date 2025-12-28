import pandas as pd
import os

# Create directory if not exists
os.makedirs('基础数据', exist_ok=True)

data = [
    {'姓名': '张三', '年级': 'G1', '班级': '1班', '学号': '2025001'},
    {'姓名': '李四', '年级': 'G2', '班级': '1班', '学号': '2025002'},
    {'姓名': '王五', '年级': 'G3', '班级': '2班', '学号': '2025003'},
    {'姓名': '赵六', '年级': 'G4', '班级': '1班', '学号': '2025004'},
    {'姓名': '钱七', '年级': 'G5', '班级': '3班', '学号': '2025005'},
    {'姓名': '孙八', '年级': 'G6', '班级': '1班', '学号': '2025006'},
    {'姓名': '周九', '年级': 'G1', '班级': '2班', '学号': '2025007'},
    {'姓名': '吴十', '年级': 'G3', '班级': '1班', '学号': '2025008'},
]
df = pd.DataFrame(data)
output_path = '/opt/Way To Future考试管理系统/Student_grade_system/基础数据/students_sample.xlsx'
df.to_excel(output_path, index=False)
print(f"Created {output_path}")
