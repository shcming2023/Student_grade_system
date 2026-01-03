
import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import zipfile
import io

# Add project path
sys.path.append('/opt/Way To Future考试管理系统/Student_grade_system')

from wtf_app_simple import generate_batch_zip

class TestBatchPDF(unittest.TestCase):
    def test_fault_tolerance(self):
        print("Testing PDF Batch Generation Fault Tolerance...")
        
        # Mock data
        tasks = [
            {'student_id': 1, 'session_id': 1, 'template_id': 1, 'filename': 'Success1.pdf'},
            {'student_id': 2, 'session_id': 1, 'template_id': 1, 'filename': 'Fail_This.pdf'},
            {'student_id': 3, 'session_id': 1, 'template_id': 1, 'filename': 'Success2.pdf'},
        ]
        
        # Mock generate_report_card_pdf
        def side_effect(student_id, session_id, template_id):
            if student_id == 2:
                raise ValueError("Simulated PDF Generation Failure")
            return io.BytesIO(b"dummy pdf content")
            
        with patch('wtf_app_simple.generate_report_card_pdf', side_effect=side_effect):
            zip_path = generate_batch_zip(tasks, 'test_batch.zip')
            
            print(f"Zip generated at: {zip_path}")
            
            # Verify zip content
            with zipfile.ZipFile(zip_path, 'r') as z:
                namelist = z.namelist()
                print(f"Zip contents: {namelist}")
                
                self.assertIn('Success1.pdf', namelist)
                self.assertIn('Success2.pdf', namelist)
                self.assertNotIn('Fail_This.pdf', namelist)
                self.assertIn('error_log.txt', namelist)
                
                # Verify error log content
                with z.open('error_log.txt') as f:
                    log_content = f.read().decode('utf-8')
                    print(f"Error Log Content:\n{log_content}")
                    self.assertIn("Simulated PDF Generation Failure", log_content)
                    self.assertIn("Fail_This.pdf", log_content)
            
            # Cleanup
            os.remove(zip_path)
            # Note: The temp dir containing zip_path is NOT removed by generate_batch_zip, 
            # which confirms the resource leak I suspected.
            
if __name__ == '__main__':
    unittest.main()
