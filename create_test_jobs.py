#!/usr/bin/env python3
"""
Create test jobs for different admins to verify isolation
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app import create_app, db
from app.models import Job, User

def create_test_jobs():
    """Create test jobs for different admins"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Creating test jobs for different admins")
        print("=" * 50)
        
        # Get admins
        admin_jude = User.query.filter_by(id=2).first()  # Admin Jude
        admin_jlrnmng = User.query.filter_by(id=4).first()  # jlrnmng Admin
        admin_rmlle = User.query.filter_by(id=11).first()  # rmlle Admin
        
        print(f"Found admins:")
        print(f"  - Admin ID 2: {admin_jude.full_name if admin_jude else 'NOT FOUND'}")
        print(f"  - Admin ID 4: {admin_jlrnmng.full_name if admin_jlrnmng else 'NOT FOUND'}")
        print(f"  - Admin ID 11: {admin_rmlle.full_name if admin_rmlle else 'NOT FOUND'}")
        
        # Create job for jlrnmng Admin
        if admin_jlrnmng:
            print(f"👤 Creating job for {admin_jlrnmng.full_name}")
            job1 = Job(
                role="Senior Python Developer",
                description="Looking for an experienced Python developer to join our team.",
                created_by=admin_jlrnmng.id,
                cluster_id=1,
                is_active=True
            )
            db.session.add(job1)
            print("   ✓ Created: Senior Python Developer")
        
        # Create job for rmlle Admin
        if admin_rmlle:
            print(f"👤 Creating job for {admin_rmlle.full_name}")
            job2 = Job(
                role="UX/UI Designer",
                description="Creative designer needed for web and mobile applications.",
                created_by=admin_rmlle.id,
                cluster_id=2,
                is_active=True
            )
            db.session.add(job2)
            print("   ✓ Created: UX/UI Designer")
        
        # Create another job for jlrnmng Admin
        if admin_jlrnmng:
            job3 = Job(
                role="DevOps Engineer",
                description="Infrastructure and deployment specialist required.",
                created_by=admin_jlrnmng.id,
                cluster_id=3,
                is_active=True
            )
            db.session.add(job3)
            print("   ✓ Created: DevOps Engineer")
        
        db.session.commit()
        print("\n✅ Test jobs created successfully!")
        
        # Show final state
        print("\n📊 Final job distribution:")
        print("-" * 30)
        
        admins = [admin_jude, admin_jlrnmng, admin_rmlle]
        for admin in admins:
            if admin:
                admin_jobs = Job.query.filter_by(created_by=admin.id, is_active=True).all()
                print(f"\n👤 {admin.full_name} (ID: {admin.id})")
                print(f"   Total jobs: {len(admin_jobs)}")
                for job in admin_jobs:
                    print(f"   - {job.role}")

if __name__ == "__main__":
    create_test_jobs()