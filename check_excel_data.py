
import pandas as pd
import os
import sys

print("Starting script...", flush=True)

file_path = 'Student_grade_system/基础数据/students_sample.xlsx'
if not os.path.exists(file_path):
    print(f"File not found: {file_path}", flush=True)
    exit(1)

print(f"File found at {file_path}", flush=True)

try:
    print("Opening Excel file...", flush=True)
    xl = pd.ExcelFile(file_path, engine='openpyxl')
    print("Excel file opened.", flush=True)
    print("Sheet names:", xl.sheet_names, flush=True)
    
    target_sheets = xl.sheet_names
    print("\nTarget Sheets found:", target_sheets, flush=True)
    
    for sheet in target_sheets:
        print(f"Reading sheet: {sheet}", flush=True)
        df = pd.read_excel(file_path, sheet_name=sheet, engine='openpyxl')
        print(f"\n--- {sheet} ---", flush=True)
        print("Columns:", df.columns.tolist(), flush=True)
        print("Row count:", len(df), flush=True)
        print(df.head(3), flush=True)
        
except Exception as e:
    print(f"Error reading excel: {e}", flush=True)
    import traceback
    traceback.print_exc()
