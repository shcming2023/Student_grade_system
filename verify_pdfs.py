import os
import sys
import io

# Add path to sys.path
sys.path.append('/opt/Way To Future考试管理系统/Student_grade_system')

from wtf_app_simple import app, db, generate_report_card_pdf

def verify():
    test_cases = [
        {'name': 'G4牛津英语', 'sid': 65, 'tid': 89, 'sess': 4},
        {'name': 'AMC8', 'sid': 63, 'tid': 109, 'sess': 4},
        {'name': '袋鼠数学A', 'sid': 62, 'tid': 110, 'sess': 4},
        {'name': 'G6朗文英语', 'sid': 52, 'tid': 118, 'sess': 4}
    ]
    
    with app.app_context():
        print(f"{'Exam':<15} | {'PDF Size':<10} | {'Status':<10}")
        print("-" * 40)
        
        for case in test_cases:
            try:
                pdf_bytes = generate_report_card_pdf(case['sid'], case['sess'], case['tid'])
                
                if pdf_bytes:
                    size = len(pdf_bytes.getvalue())
                    status = "OK" if size > 1000 else "Small/Empty"
                    print(f"{case['name']:<15} | {size:<10} | {status:<10}")
                    
                    # Save to file for inspection if needed
                    with open(f"verify_{case['name']}.pdf", "wb") as f:
                        f.write(pdf_bytes.getvalue())
                else:
                    print(f"{case['name']:<15} | {'None':<10} | {'Failed':<10}")
            except Exception as e:
                print(f"{case['name']:<15} | {'Error':<10} | {str(e):<10}")

if __name__ == "__main__":
    verify()
