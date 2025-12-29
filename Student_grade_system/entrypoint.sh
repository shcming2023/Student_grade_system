#!/bin/bash
set -e

# Initialize database if needed
python -c "from wtf_app_simple import app, db, create_initial_data; 
with app.app_context():
    db.create_all()
    # Try to init data if tables are empty (basic check)
    try:
        from wtf_app_simple import Subject
        if not Subject.query.first():
            print('Initializing data...')
            create_initial_data()
    except Exception as e:
        print(f'Init check failed: {e}')
"

# Start Gunicorn
exec gunicorn -w 4 -b 0.0.0.0:5000 wtf_app_simple:app
