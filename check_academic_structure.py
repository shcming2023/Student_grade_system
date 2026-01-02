import pandas as pd
EXCEL_PATH = 'Student_grade_system/基础数据/WTF学术测评考卷登记表.xlsx'

def check_structure():
    xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    for sheet in ['AMC8', '袋鼠数学A', '袋鼠数学B']:
        df = pd.read_excel(xls, sheet_name=sheet)
        print(f"\n--- {sheet} ---")
        print(df.columns.tolist()[:10]) # First 10 cols
        print(df.iloc[0].to_dict())

if __name__ == "__main__":
    check_structure()
