import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests

url = 'http://localhost:8083'
login_url = f'{url}/login'
index_url = f'{url}/'

session = requests.Session()

# Login
response = session.post(login_url, data={'username': 'admin', 'password': 'admin123'})
print(f"Login Status: {response.status_code}")

# Get Index
response = session.get(index_url)
print(f"Index Status: {response.status_code}")
content = response.text

if "评分录入" in content:
    print("SUCCESS: Found '评分录入' in index page.")
else:
    print("FAILURE: '评分录入' NOT found in index page.")
    # Print a snippet to see what we got
    print("Content snippet:")
    print(content[:500])

if "(已更新)" in content:
    print("SUCCESS: Found '(已更新)' in title.")
else:
    print("FAILURE: '(已更新)' NOT found in title.")
