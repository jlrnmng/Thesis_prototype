#!/usr/bin/env python3
"""
Script to update existing admin accounts with company names
"""
import os
import sys
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def update_admin_companies():
    """Update admin accounts to have company names"""
    db_path = os.path.join('instance', 'resume_matcher.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all admins without company names
        cursor.execute("SELECT id, first_name, last_name, email FROM users WHERE is_admin = 1 AND (company_name IS NULL OR company_name = '')")
        admins = cursor.fetchall()
        
        if not admins:
            print("✅ All admins already have company names!")
            conn.close()
            return True
        
        print(f"Found {len(admins)} admin(s) without company names:\n")
        
        for admin_id, first_name, last_name, email in admins:
            # Generate a default company name from their information
            # You can customize this logic as needed
            if first_name and first_name != 'Admin':
                company_name = f"{first_name}'s Company"
            else:
                # Extract username from email
                username = email.split('@')[0]
                company_name = f"{username.title()} Company"
            
            print(f"  Admin ID {admin_id} ({first_name} {last_name}, {email})")
            print(f"    → Setting company name to: {company_name}")
            
            cursor.execute(
                "UPDATE users SET company_name = ? WHERE id = ?",
                (company_name, admin_id)
            )
        
        conn.commit()
        print(f"\n✅ Updated {len(admins)} admin account(s) with company names!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during update: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Updating admin accounts with company names")
    print("=" * 60)
    print("Note: Existing admins will get default company names.")
    print("You can update these in the admin profile later.\n")
    
    success = update_admin_companies()
    
    if success:
        print("\n🎉 Update completed!")
    else:
        print("\n❌ Update failed!")
        sys.exit(1)
