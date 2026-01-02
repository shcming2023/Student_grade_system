import sys
import os
import io
sys.path.append(os.path.join(os.getcwd(), 'Student_grade_system'))

from wtf_app_simple import app, generate_report_card_pdf

def test_pdfs():
    with app.app_context():
        cases = [
        {'name': 'G4 Oxford', 'template_id': 89, 'student_id': 65, 'session_id': 4},
        {'name': 'Kangaroo A', 'template_id': 110, 'student_id': 62, 'session_id': 4},
        {'name': 'AMC8', 'template_id': 109, 'student_id': 63, 'session_id': 4},
        {'name': 'G6 Longman', 'template_id': 118, 'student_id': 52, 'session_id': 4},
        {'name': 'Kangaroo B', 'template_id': 111, 'student_id': 70, 'session_id': 4},
        # Old
        {'name': 'G4 Oxford (Old)', 'template_id': 61, 'student_id': 57, 'session_id': 4},
        {'name': 'Kangaroo A (Old)', 'template_id': 82, 'student_id': 61, 'session_id': 4},
        {'name': 'AMC8 (Old)', 'template_id': 53, 'student_id': 63, 'session_id': 4},
        # MAP Assessment (New)
        {'name': 'MAP Assessment', 'template_id': 113, 'student_id': 1, 'session_id': 3},
    ]
        
        for case in cases:
            print(f"Testing {case['name']} (S{case['student_id']} T{case['template_id']})...")
            try:
                # We need to find the correct session_id. 
                # In previous steps we saw session 4 is likely the active one.
                # Let's verify registration first.
                from wtf_app_simple import ExamRegistration
                reg = ExamRegistration.query.filter_by(
                    student_id=case['student_id'], 
                    exam_template_id=case['template_id']
                ).first()
                
                if not reg:
                    print(f"  No registration found!")
                    continue
                    
                print(f"  Found registration: Session {reg.exam_session_id}")
                
                pdf_buffer = generate_report_card_pdf(
                    case['student_id'], 
                    reg.exam_session_id, 
                    case['template_id']
                )
                
                if pdf_buffer:
                    filename = f"verify_final_T{case['template_id']}_S{case['student_id']}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    print(f"  SUCCESS: Generated {filename} ({len(pdf_buffer.getvalue())} bytes)")
                else:
                    print(f"  FAILED: generate_report_card_pdf returned None")
                    
            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_pdfs()
