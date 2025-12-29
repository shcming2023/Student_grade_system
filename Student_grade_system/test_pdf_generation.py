from wtf_app_simple import app, db, Student, ExamSession, generate_report_card_pdf
import os

def test_pdf():
    with app.app_context():
        # Find Wang Wenyi
        student = Student.query.filter_by(name='王雯仪').first()
        if not student:
            print("Error: Student Wang Wenyi not found")
            return

        print(f"Found student: {student.name} (ID: {student.id})")

        # Find 1.4 Afternoon session
        # We look for session with date 2026-01-04 and type afternoon
        # Note: In rebuild_system, dates were set as 2026-01-04
        session = ExamSession.query.filter(
            ExamSession.name.like('%2026-01-04 下午场%')
        ).first()
        
        if not session:
            print("Error: Session 1.4 Afternoon not found")
            return
            
        print(f"Found session: {session.name} (ID: {session.id})")

        # Generate PDF
        print("Generating PDF...")
        pdf_buffer = generate_report_card_pdf(student.id, session.id)
        
        if pdf_buffer:
            output_path = f"report_card_{student.name}.pdf"
            with open(output_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            print(f"Success! PDF saved to {output_path}")
            print(f"File size: {os.path.getsize(output_path)} bytes")
        else:
            print("Error: PDF generation failed (returned None)")

if __name__ == "__main__":
    test_pdf()
