import sys
import os
from werkzeug.security import generate_password_hash

# Add the directory to sys.path so we can import app
sys.path.append('/opt/Way To Future考试管理系统/Student_grade_system')

from wtf_app_simple import app, db, User

def setup_user():
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        if not user:
            print("Creating admin user...")
            user = User(username='admin', role='admin')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists. Resetting password...")
            user.set_password('password')
            db.session.commit()
            print("Password reset to 'password'.")

if __name__ == '__main__':
    setup_user()
