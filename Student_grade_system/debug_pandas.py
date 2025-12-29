import sys
print("Start script", flush=True)
import pandas as pd
print("Pandas imported", flush=True)

data = [
    {"Name": "Test", "Value": 1}
]
print("Data defined", flush=True)

df = pd.DataFrame(data)
print("DataFrame created", flush=True)

output_path = '/opt/Way To Future考试管理系统/Student_grade_system/基础数据/debug_test.xlsx'
try:
    df.to_excel(output_path, index=False)
    print(f"File saved to {output_path}", flush=True)
except Exception as e:
    print(f"Error saving file: {e}", flush=True)
