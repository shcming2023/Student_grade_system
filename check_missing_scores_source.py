import pandas as pd
import os

EXCEL_PATH = 'Student_grade_system/基础数据/2025秋季第一学期WTF考卷登记表4.0.xlsx'

def check_excel_source():
    if not os.path.exists(EXCEL_PATH):
        print(f"File not found: {EXCEL_PATH}")
        return

    print(f"Reading {EXCEL_PATH}...")
    xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    
    target_sheets = [s for s in xls.sheet_names if '袋鼠' in s or 'AMC' in s]
    print(f"Found sheets: {target_sheets}")
    
    for sheet in target_sheets:
        df = pd.read_excel(xls, sheet_name=sheet)
        print(f"\n--- Sheet: {sheet} ---")
        print(f"Columns: {df.columns.tolist()}")
        
        # Check for specific students
        students = ['魏睿希', '林钧瀚', 'Nico']
        for s in students:
            # Assuming '姓名' or 'Name' column exists
            name_col = next((c for c in df.columns if '姓名' in str(c) or 'Name' in str(c)), None)
            if name_col:
                found = df[df[name_col].astype(str).str.contains(s, na=False)]
                if not found.empty:
                    print(f"Found {s}: {len(found)} rows")
                    # Check if they have scores (columns usually start with numbers or 'Q')
                    # Just print the first row found
                    print(found.iloc[0].to_dict())
                else:
                    print(f"Student {s} NOT found in {sheet}")
            else:
                print(f"No name column found in {sheet}")

if __name__ == "__main__":
    check_excel_source()
