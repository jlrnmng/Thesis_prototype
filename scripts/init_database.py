"""
Database initialization script for development setup
Run this script when setting up the project for the first time or to reset the database
"""
import os
import sys
import sqlite3

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app, db
from app.models import User, Job, Application

def init_development_database():
    """Initialize database with basic structure and sample data"""
    print("🔧 Initializing Development Database...")
    
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("📋 Creating database tables...")
        db.create_all()
        
        # Check if we already have users (avoid duplicates)
        existing_users = User.query.count()
        
        if existing_users == 0:
            print("👥 Creating sample admin and user accounts...")
            
            # Create a sample admin user
            sample_admin = User(
                email='admin@hirely.dev',
                username='admin',
                is_admin=True
            )
            sample_admin.set_password('admin123')  # Change this in production!
            
            # Create a sample regular user
            sample_user = User(
                email='user@hirely.dev',
                username='user',
                is_admin=False
            )
            sample_user.set_password('user123')  # Change this in production!
            
            db.session.add(sample_admin)
            db.session.add(sample_user)
            db.session.commit()
            
            print("✅ Sample accounts created:")
            print("   Admin: admin@hirely.dev / admin123")
            print("   User:  user@hirely.dev / user123")
        else:
            print(f"📊 Database already has {existing_users} users - skipping sample data creation")
        
        print("✅ Database initialization complete!")
        
        # Display current database status
        users_count = User.query.count()
        jobs_count = Job.query.count()
        applications_count = Application.query.count()
        
        print(f"\n📈 Current Database Status:")
        print(f"   Users: {users_count}")
        print(f"   Jobs: {jobs_count}")
        print(f"   Applications: {applications_count}")

def reset_database():
    """Reset database (WARNING: This will delete all data!)"""
    print("⚠️  WARNING: This will delete ALL database data!")
    confirm = input("Are you sure you want to reset the database? (type 'yes' to confirm): ")
    
    if confirm.lower() == 'yes':
        app = create_app()
        
        with app.app_context():
            print("🗑️  Dropping all tables...")
            db.drop_all()
            
            print("📋 Recreating tables...")
            db.create_all()
            
            print("✅ Database reset complete!")
            init_development_database()
    else:
        print("❌ Database reset cancelled")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        init_development_database()

if __name__ == '__main__':
    main()