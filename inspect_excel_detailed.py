
import pandas as pd
import os

filepath = '/opt/Way To Future考试管理系统/Student_grade_system/基础数据/2025秋季第一学期WTF考卷登记表4.0.xlsx'
print(f"\nAnalyzing {filepath}...")
try:
    xls = pd.ExcelFile(filepath, engine='openpyxl')
    print(f"Sheet names: {xls.sheet_names}")
    
    # Check the first sheet specifically
    first_sheet = xls.sheet_names[0]
    print(f"\n  Sheet: {first_sheet}")
    df = pd.read_excel(filepath, sheet_name=first_sheet, nrows=5, engine='openpyxl')
    print(df.columns.tolist())
    print(df.head(5))
    
    # Check if any sheet name looks like 'Student', '考生', '名单', etc.
    for sheet_name in xls.sheet_names:
        if any(keyword in sheet_name for keyword in ['名单', '学生', '考生', 'Student', 'Registration']):
             print(f"\n  Potential Student Sheet: {sheet_name}")
             df = pd.read_excel(filepath, sheet_name=sheet_name, nrows=5, engine='openpyxl')
             print(df.columns.tolist())
             print(df.head(5))

except Exception as e:
    print(f"Error reading file: {e}")
