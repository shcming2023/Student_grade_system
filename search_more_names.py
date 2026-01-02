import pandas as pd

def search_names():
    # 1. Check G6 sheet for other names
    path1 = 'Student_grade_system/基础数据/2025秋季第一学期WTF考卷登记表4.0.xlsx'
    print(f"Checking {path1} - G6先锋英语")
    xls = pd.ExcelFile(path1, engine='openpyxl')
    df = pd.read_excel(xls, sheet_name='G6先锋英语')
    
    # Search for Wei Ruixi
    found = False
    for r_idx, row in df.iterrows():
        for c_idx, val in enumerate(row):
            if isinstance(val, str) and '魏睿希' in val:
                print(f"Found '魏睿希' at {r_idx}, {c_idx}")
                found = True
    if not found:
        print("'魏睿希' not found.")

    # 2. Check OCR file
    path2 = 'Student_grade_system/基础数据/registration_data_ocr.xlsx'
    print(f"\nChecking {path2} - Sheet1")
    df2 = pd.read_excel(path2, engine='openpyxl')
    print("Columns:", df2.columns.tolist())
    print(df2.head())
    
    # Search for Nico or Wei Ruixi in OCR file
    print("\nSearching in OCR file...")
    for name in ['Nico', '魏睿希']:
        res = df2[df2.astype(str).apply(lambda x: x.str.contains(name, case=False, na=False)).any(axis=1)]
        if not res.empty:
            print(f"Found {name} in OCR file:")
            print(res.iloc[0].to_dict())
        else:
            print(f"{name} not found in OCR file.")

if __name__ == "__main__":
    search_names()
