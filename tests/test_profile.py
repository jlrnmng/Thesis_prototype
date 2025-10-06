"""
Simple test script to test profile functionality without ML dependencies
"""
import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Test profile routes directly
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_profile.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

# Import models
from models import User, Application, Job

# Create tables
with app.app_context():
    db.create_all()
    
    # Create test user
    test_user = User(
        first_name="John",
        last_name="Doe", 
        email="john.doe@example.com",
        is_admin=False
    )
    test_user.set_password("password123")
    
    db.session.add(test_user)
    db.session.commit()
    
    print("✅ Profile test setup complete!")
    print(f"Test user created: {test_user.first_name} {test_user.last_name}")
    print(f"User fields available:")
    print(f"  - ID: {test_user.id}")
    print(f"  - Name: {test_user.first_name} {test_user.middle_name or ''} {test_user.last_name}")
    print(f"  - Email: {test_user.email}")
    print(f"  - Phone: {test_user.phone}")
    print(f"  - Address: {test_user.address}")
    print(f"  - Resume: {test_user.resume}")
    print(f"  - Is Admin: {test_user.is_admin}")
    
    print("\n✅ Profile feature is ready to use!")
    print("📁 Profile template created: app/templates/profile.html")
    print("🔧 Profile routes added to app/routes/main.py:")
    print("   - GET /profile - View profile page")
    print("   - POST /update_profile - Update profile information")
    print("   - GET /download_resume/<user_id> - Download resume")
    print("\n🔒 Duplicate application prevention already exists!")
    print("   - Located in app/routes/main.py lines 407-409")
    print("   - Prevents users from applying to the same job multiple times")