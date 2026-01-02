import sys
import os
import io
import zipfile
sys.path.append(os.path.join(os.getcwd(), 'Student_grade_system'))

from wtf_app_simple import app, db, Student, ExamRegistration

def test_batch_email_and_zip():
    with app.app_context():
        # Find Nico
        student = Student.query.filter_by(name='Nico').first()
        if not student:
            print("Nico not found")
            return
            
        # Ensure Nico has email
        if not student.email:
            student.email = 'nico@example.com'
            db.session.commit()
            print("Set mock email for Nico")
            
        # Find a registration
        reg = ExamRegistration.query.filter_by(student_id=student.id).first()
        if not reg:
            print("No registration for Nico")
            return
            
        print(f"Testing for Student {student.id} (Nico), Session {reg.exam_session_id}, Template {reg.exam_template_id}")
        
        # Test client
        client = app.test_client()
        
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            
        # 1. Test Batch Email Items
        print("\n--- Testing Batch Email ---")
        items = [{
            'student_id': student.id,
            'exam_session_id': reg.exam_session_id,
            'template_id': reg.exam_template_id
        }]
        
        resp = client.post('/api/email/batch-send-report-card-items', json={'items': items})
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.get_json()}")
        
        # 2. Test Batch PDF Zip
        print("\n--- Testing Batch PDF Zip ---")
        resp_zip = client.post('/api/pdf/batch-generate-zip', json={'items': items})
        print(f"Status: {resp_zip.status_code}")
        print(f"Content-Type: {resp_zip.content_type}")
        
        if resp_zip.status_code == 200:
            zip_content = io.BytesIO(resp_zip.data)
            try:
                with zipfile.ZipFile(zip_content, 'r') as z:
                    print(f"Zip contains files: {z.namelist()}")
            except Exception as e:
                print(f"Failed to read zip: {e}")

if __name__ == "__main__":
    test_batch_email_and_zip()
