import pandas as pd
EXCEL_PATH = 'Student_grade_system/基础数据/2025秋季第一学期WTF考卷登记表4.0.xlsx'

def inspect_g6_columns():
    xls = pd.ExcelFile(EXCEL_PATH, engine='openpyxl')
    df = pd.read_excel(xls, sheet_name='G6先锋英语', header=None)
    
    # Print shape
    print(f"Shape: {df.shape}")
    
    # Print row 1 (header)
    print("Row 1 (Header candidates):")
    print(df.iloc[1].tolist())
    
    # Check if we can find 'Nico' anywhere in the dataframe
    print("\nSearching for 'Nico'...")
    locations = []
    for r_idx, row in df.iterrows():
        for c_idx, val in enumerate(row):
            if isinstance(val, str) and 'Nico' in val:
                locations.append((r_idx, c_idx))
    
    if locations:
        print(f"Found 'Nico' at: {locations}")
        # If found, print that column
        col_idx = locations[0][1]
        print(f"\nColumn {col_idx} data (first 10 rows):")
        print(df.iloc[:10, col_idx])
    else:
        print("'Nico' not found in this sheet.")

if __name__ == "__main__":
    inspect_g6_columns()
