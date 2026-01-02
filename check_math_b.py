import pandas as pd
EXCEL_PATH = 'Student_grade_system/基础数据/WTF学术测评考卷登记表.xlsx'

def check_math_b():
    xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    df = pd.read_excel(xls, sheet_name='袋鼠数学B')
    
    print("Checking '袋鼠数学B' for Nico...")
    nico = df[df.astype(str).apply(lambda x: x.str.contains('Nico', case=False, na=False)).any(axis=1)]
    if not nico.empty:
        print(f"Found Nico: {len(nico)}")
        print(nico.iloc[0].to_dict())
    else:
        print("Nico not found in '袋鼠数学B'.")

if __name__ == "__main__":
    check_math_b()
