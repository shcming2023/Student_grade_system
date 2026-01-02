import pandas as pd
import os

EXCEL_PATH = 'Student_grade_system/基础数据/students_sample.xlsx'

def list_sheets():
    xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    print(f"All sheets: {xls.sheet_names}")

if __name__ == "__main__":
    list_sheets()
