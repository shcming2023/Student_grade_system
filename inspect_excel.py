
import pandas as pd
import os

base_dir = '/opt/Way To Future考试管理系统/Student_grade_system/基础数据'
files = [
    '2025秋季第一学期WTF考卷登记表4.0.xlsx',
    'WTF学术测评考卷登记表.xlsx'
]

for filename in files:
    filepath = os.path.join(base_dir, filename)
    print(f"\nAnalyzing {filename}...")
    try:
        # Use openpyxl for xlsx files
        xls = pd.ExcelFile(filepath, engine='openpyxl')
        print(f"Sheet names: {xls.sheet_names}")
        for sheet_name in xls.sheet_names:
            print(f"\n  Sheet: {sheet_name}")
            df = pd.read_excel(filepath, sheet_name=sheet_name, nrows=3, engine='openpyxl')
            print(df.columns.tolist())
            print(df.head(3))
    except Exception as e:
        print(f"Error reading {filename}: {e}")
