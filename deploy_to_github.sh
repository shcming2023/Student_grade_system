#!/bin/bash

# Initialize git if not exists
if [ ! -d ".git" ]; then
    git init
    git branch -M main
fi

# Add all files
git add .

# Commit
git commit -m "Update: Apply local changes (Mobile/PC optimization, Login, PDF, etc.) - $(date)"

# Add remote if not exists
if ! git remote | grep -q "origin"; then
    git remote add origin https://github.com/shcming2023/Student_grade_system.git
else
    git remote set-url origin https://github.com/shcming2023/Student_grade_system.git
fi

# Push (Force to overwrite remote as requested)
echo "Pushing to GitHub..."
git push -u origin main --force
