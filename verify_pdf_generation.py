import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'Student_grade_system'))

from wtf_app_simple import app, db, generate_report_card_pdf, ExamRegistration, Student, ExamSession, ExamTemplate

def test_pdf():
    with app.app_context():
        # Test Case 1: G4 Oxford (ID 89), Student ID 65 (Reg 170), Session 4
        student_id = 65
        student = Student.query.get(student_id)
        if not student:
            print(f"Error: Student {student_id} not found")
            return

        print(f"Testing for Student: {student.name} (ID: {student.id})")
        session_id = 4
        
        # 1. G4 Oxford (ID 89)
        print("\n--- Test 1: G4 Oxford (ID 89) ---")
        pdf_buffer = generate_report_card_pdf(student.id, session_id, template_id=89)
        if pdf_buffer:
            print(f"Success! PDF generated, size: {len(pdf_buffer.getvalue())} bytes")
            with open("test_g4_oxford_no_scores.pdf", "wb") as f:
                f.write(pdf_buffer.getvalue())
        else:
            print("Failed to generate PDF.")

        # 2. Kangaroo A (ID 110)
        # Check Reg for Kangaroo A ID 110 in Session 4
        # From prev log: RegID: 180, Student: Nico, Session: 4...
        # Let's find student ID for Reg 180
        reg180 = ExamRegistration.query.get(180)
        if reg180:
            print(f"\n--- Test 2: Kangaroo A (ID 110) Student {reg180.student_id} ---")
            pdf_buffer = generate_report_card_pdf(reg180.student_id, session_id, template_id=110)
            if pdf_buffer:
                print(f"Success! PDF generated, size: {len(pdf_buffer.getvalue())} bytes")
                with open("test_kangaroo_a_no_scores.pdf", "wb") as f:
                    f.write(pdf_buffer.getvalue())
            else:
                print("Failed to generate PDF.")
        else:
            print("Reg 180 not found")

        # 3. G6 Longman (ID 118) - Create Registration first
        print("\n--- Test 3: G6 Longman (ID 118) ---")
        # Check if reg exists
        reg = ExamRegistration.query.filter_by(
            student_id=student.id, 
            exam_session_id=session_id,
            exam_template_id=118
        ).first()
        
        if not reg:
            print("Creating new registration for G6 Longman...")
            reg = ExamRegistration(
                student_id=student.id,
                exam_session_id=session_id,
                exam_template_id=118
            )
            db.session.add(reg)
            db.session.commit()
            print(f"Created Reg ID: {reg.id}")
        else:
            print(f"Registration already exists: {reg.id}")
            
        pdf_buffer = generate_report_card_pdf(student.id, session_id, template_id=118)
        if pdf_buffer:
            print(f"Success! PDF generated, size: {len(pdf_buffer.getvalue())} bytes")
            with open("test_g6_longman.pdf", "wb") as f:
                f.write(pdf_buffer.getvalue())
        else:
            print("Failed to generate PDF.")

if __name__ == "__main__":
    test_pdf()
