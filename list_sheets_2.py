import pandas as pd
import os

EXCEL_PATH = 'Student_grade_system/基础数据/WTF学术测评考卷登记表.xlsx'

def list_sheets_2():
    if not os.path.exists(EXCEL_PATH):
        print("File not found")
        return
    xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    print(f"All sheets: {xls.sheet_names}")

if __name__ == "__main__":
    list_sheets_2()
