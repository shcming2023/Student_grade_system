import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Before import")
try:
    from wtf_app_simple import app
    print("Import success")
except Exception as e:
    print(f"Import failed: {e}")
