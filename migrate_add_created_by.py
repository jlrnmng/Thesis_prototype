#!/usr/bin/env python3
"""
Migration script to add created_by column to jobs table
Run this script ONCE to update the database schema
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models import Job, User
from sqlalchemy import text

def migrate_database():
    """Add created_by column to jobs table and update existing records"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get the first admin user to assign existing jobs to
            first_admin = User.query.filter_by(is_admin=True).first()
            
            if not first_admin:
                print("❌ No admin users found. Please create an admin user first.")
                return
            
            print(f"� Assigning all existing jobs to admin: {first_admin.full_name} (ID: {first_admin.id})")
            
            # Check current job status
            jobs_without_creator = Job.query.filter(
                (Job.created_by == None) | (Job.created_by == 0)
            ).all()
            
            print(f"📊 Found {len(jobs_without_creator)} jobs without a creator")
            
            if jobs_without_creator:
                # Update all jobs without a creator
                for job in jobs_without_creator:
                    job.created_by = first_admin.id
                    print(f"   ✓ Assigned job '{job.role}' (ID: {job.id}) to {first_admin.full_name}")
                
                db.session.commit()
                print(f"✅ Successfully updated {len(jobs_without_creator)} jobs")
            else:
                print("✅ All jobs already have creators assigned")
            
            # Verify the update
            print("\n=== VERIFICATION ===")
            all_jobs = Job.query.all()
            for job in all_jobs:
                creator = User.query.get(job.created_by) if job.created_by else None
                print(f"Job {job.id}: '{job.role}' → Created by: {creator.full_name if creator else 'STILL NULL'}")
            
            print("✅ Migration completed successfully!")
            print("🎉 Each admin can now only see and manage their own job posts")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    migrate_database()
    print("✨ Migration script completed")