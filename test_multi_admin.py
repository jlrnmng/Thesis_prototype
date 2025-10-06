#!/usr/bin/env python3
"""
Test script to verify multi-admin functionality
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models import Job, User

def test_admin_isolation():
    """Test that each admin only sees their own jobs"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Multi-Admin Functionality")
        print("=" * 50)
        
        # Get all admins
        admins = User.query.filter_by(is_admin=True).all()
        print(f"📊 Found {len(admins)} admin users:")
        for admin in admins:
            print(f"   - {admin.full_name} (ID: {admin.id})")
        
        print("\n📋 Testing job visibility per admin:")
        print("-" * 40)
        
        for admin in admins:
            # Simulate what the admin dashboard does
            admin_jobs = Job.query.filter_by(created_by=admin.id, is_active=True).all()
            print(f"\n👤 Admin: {admin.full_name} (ID: {admin.id})")
            print(f"   Jobs visible: {len(admin_jobs)}")
            
            if admin_jobs:
                for job in admin_jobs:
                    print(f"   - {job.role} (Job ID: {job.id})")
            else:
                print("   - No jobs found")
        
        print("\n🔍 All jobs in database:")
        print("-" * 30)
        all_jobs = Job.query.all()
        for job in all_jobs:
            creator = User.query.get(job.created_by) if job.created_by else None
            print(f"Job {job.id}: '{job.role}' → Owner: {creator.full_name if creator else 'NULL'}")
        
        print("\n✅ Test completed!")

if __name__ == "__main__":
    test_admin_isolation()