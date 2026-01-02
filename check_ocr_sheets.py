import pandas as pd
EXCEL_PATH = 'Student_grade_system/基础数据/registration_data_ocr.xlsx'

def check_ocr_sheets():
    xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    print(xls.sheet_names)

if __name__ == "__main__":
    check_ocr_sheets()
