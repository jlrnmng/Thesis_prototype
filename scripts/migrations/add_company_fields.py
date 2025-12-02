#!/usr/bin/env python3
"""
Migration script to add company_name and company_address fields to users table
"""
import os
import sys
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def migrate():
    """Add company_name and company_address columns to users table"""
    db_path = os.path.join('instance', 'resume_matcher.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        changes_made = False
        
        # Add company_name if it doesn't exist
        if 'company_name' not in columns:
            print("Adding company_name column...")
            cursor.execute("ALTER TABLE users ADD COLUMN company_name VARCHAR(200)")
            print("✅ Added company_name column")
            changes_made = True
        else:
            print("ℹ️ company_name column already exists")
        
        # Add company_address if it doesn't exist
        if 'company_address' not in columns:
            print("Adding company_address column...")
            cursor.execute("ALTER TABLE users ADD COLUMN company_address TEXT")
            print("✅ Added company_address column")
            changes_made = True
        else:
            print("ℹ️ company_address column already exists")
        
        if changes_made:
            conn.commit()
            print("\n✅ Migration completed successfully!")
        else:
            print("\n✅ No migration needed - columns already exist")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Running migration: Add company fields to users table")
    print("=" * 60)
    
    success = migrate()
    
    if success:
        print("\n🎉 Migration completed!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
