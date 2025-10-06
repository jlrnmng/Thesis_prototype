#!/usr/bin/env python3
"""Check Application records in the database.

This script will print out details about all Application records
to help understand why there are more records than resume files.
"""
import os
import sys

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    from app import create_app, db
    app = create_app()
    
    with app.app_context():
        from app.models import Application, User, Job
        
        apps = Application.query.all()
        print(f"\nFound {len(apps)} total applications")
        
        # Group by user
        user_apps = {}
        for app in apps:
            if app.user_id not in user_apps:
                user_apps[app.user_id] = []
            user_apps[app.user_id].append(app)
        
        print(f"Applications are from {len(user_apps)} unique users\n")
        
        for user_id, apps in user_apps.items():
            user = User.query.get(user_id)
            if not user:
                print(f"User {user_id}: Not found in database")
                continue
                
            print(f"User {user_id}: {user.full_name}")
            print(f"Number of applications: {len(apps)}")
            for app in apps:
                job = Job.query.get(app.job_id)
                job_title = job.role if job else "Unknown job"
                resume_preview = app.resume_text[:50] + "..." if app.resume_text else "No resume text"
                print(f"  - Applied to: {job_title}")
                print(f"    Resume text: {resume_preview}")
            print()

if __name__ == '__main__':
    main()