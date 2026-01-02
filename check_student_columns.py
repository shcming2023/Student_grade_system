import pandas as pd
try:
    df = pd.read_excel('Student_grade_system/基础数据/students_sample.xlsx')
    print(df.columns.tolist())
    print(df.head(1))
except Exception as e:
    print(e)
