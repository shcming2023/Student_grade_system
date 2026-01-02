import pandas as pd
EXCEL_PATH = 'Student_grade_system/基础数据/2025秋季第一学期WTF考卷登记表4.0.xlsx'

def check_g6_scores():
    xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    df = pd.read_excel(xls, sheet_name='G6先锋英语')
    print(df.head())
    
    # Check for Nico
    # Assuming column '姓名' or similar
    cols = df.columns.tolist()
    print(cols)
    
    # Try to find Nico
    nico = df[df.astype(str).apply(lambda x: x.str.contains('Nico', case=False, na=False)).any(axis=1)]
    print(f"Found Nico: {len(nico)}")
    if not nico.empty:
        print(nico.iloc[0].to_dict())

if __name__ == "__main__":
    check_g6_scores()
