import pandas as pd
EXCEL_PATH = 'Student_grade_system/基础数据/WTF学术测评考卷登记表.xlsx'

def check_shape():
    xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    df = pd.read_excel(xls, sheet_name='袋鼠数学A', header=None)
    print(f"Shape: {df.shape}")
    print(df.iloc[:5, :10])

if __name__ == "__main__":
    check_shape()
