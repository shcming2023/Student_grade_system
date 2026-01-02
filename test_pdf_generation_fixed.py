
import os
import sys

print("Start script...", flush=True)

# Add path to sys.path to import wtf_app_simple
sys.path.append(os.path.join(os.getcwd(), 'Student_grade_system'))
print("Path added.", flush=True)

try:
    from wtf_app_simple import app, db, generate_report_card_pdf, ExamRegistration
    print("Import successful.", flush=True)
except ImportError as e:
    print(f"Import failed: {e}", flush=True)
    sys.exit(1)
except Exception as e:
    print(f"Import error: {e}", flush=True)
    sys.exit(1)

def test_pdf(reg_id, output_name):
    print(f"\nGenerating PDF for Registration ID {reg_id} -> {output_name}", flush=True)
    with app.app_context():
        reg = ExamRegistration.query.get(reg_id)
        if not reg:
            print(f"Registration {reg_id} not found!", flush=True)
            return
            
        print(f"Student: {reg.student.name}, Template: {reg.exam_template.name}", flush=True)
        
        try:
            pdf_buffer = generate_report_card_pdf(reg.student_id, reg.exam_session_id, reg.exam_template_id)
            if pdf_buffer:
                with open(output_name, 'wb') as f:
                    f.write(pdf_buffer.read())
                print(f"Success! PDF saved to {output_name}", flush=True)
            else:
                print("Failed! PDF buffer is None.", flush=True)
        except Exception as e:
            print(f"Error generating PDF: {e}", flush=True)
            import traceback
            traceback.print_exc()

# 1. G6 Pioneer (was Longman) - Student 41
print("Checking G6 Pioneer...", flush=True)
with app.app_context():
    reg = ExamRegistration.query.filter_by(student_id=41, exam_template_id=91).first()
    if reg:
        test_pdf(reg.id, "report_G6_Pioneer.pdf")
    else:
        print("Reg not found for G6 Pioneer", flush=True)

# 2. Kangaroo A - Student 8
print("Checking Kangaroo A...", flush=True)
with app.app_context():
    reg = ExamRegistration.query.filter_by(student_id=8, exam_template_id=82).first()
    if reg:
        test_pdf(reg.id, "report_Kangaroo_A.pdf")
    else:
         print("Reg not found for Kangaroo A", flush=True)

# 3. G4 Oxford - Student 57 (Template 61)
print("Checking G4 Oxford...", flush=True)
with app.app_context():
    reg = ExamRegistration.query.filter_by(student_id=57, exam_template_id=61).first()
    if reg:
        test_pdf(reg.id, "report_G4_Oxford.pdf")

# 4. AMC8 - Student 63 (Template 53)
print("Checking AMC8...", flush=True)
with app.app_context():
    reg = ExamRegistration.query.filter_by(student_id=63, exam_template_id=53).first()
    if reg:
        test_pdf(reg.id, "report_AMC8.pdf")
