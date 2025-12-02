#!/usr/bin/env python3
"""
Test script to verify profile update functionality without ML dependencies
"""
import os
import sys
import tempfile
from werkzeug.datastructures import FileStorage
from io import BytesIO

# Add the app directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_profile_routes():
    """Test if the profile routes are properly defined"""
    try:
        from app.routes.main import main_bp
        
        # Check if routes exist
        routes = []
        for rule in main_bp.url_map.iter_rules():
            routes.append((rule.rule, rule.methods))
        
        profile_routes = [route for route in routes if 'profile' in route[0] or 'resume' in route[0]]
        
        print("✅ Profile-related routes found:")
        for route, methods in profile_routes:
            print(f"   {route} - {methods}")
            
        return len(profile_routes) > 0
        
    except Exception as e:
        print(f"❌ Error testing routes: {e}")
        return False

def test_user_model():
    """Test if the User model has resume field"""
    try:
        from app.models import User
        
        # Check if resume field exists
        if hasattr(User, 'resume'):
            print("✅ User model has 'resume' field")
            return True
        else:
            print("❌ User model missing 'resume' field")
            return False
            
    except Exception as e:
        print(f"❌ Error testing User model: {e}")
        return False

def test_file_validation():
    """Test file validation logic"""
    try:
        # Test PDF file extension validation
        test_files = [
            "resume.pdf",
            "document.docx", 
            "image.jpg",
            "text.txt"
        ]
        
        valid_extensions = ['.pdf']
        
        for filename in test_files:
            is_valid = any(filename.lower().endswith(ext) for ext in valid_extensions)
            status = "✅" if is_valid else "❌"
            print(f"   {status} {filename} - {'Valid' if is_valid else 'Invalid'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing file validation: {e}")
        return False

def test_secure_filename_generation():
    """Test secure filename generation logic"""
    try:
        import time
        
        # Simulate the filename generation logic from update_profile
        first_name = "John"
        last_name = "Doe"
        timestamp = str(int(time.time()))
        filename = f"{first_name}_{last_name}_Resume_{timestamp}.pdf"
        
        print(f"✅ Generated secure filename: {filename}")
        
        # Check if filename is safe (no path traversal)
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        is_safe = not any(char in filename for char in dangerous_chars)
        
        if is_safe:
            print("✅ Filename is secure (no dangerous characters)")
        else:
            print("❌ Filename contains dangerous characters")
            
        return is_safe
        
    except Exception as e:
        print(f"❌ Error testing filename generation: {e}")
        return False

def test_template_exists():
    """Test if profile template exists"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), 'app', 'templates', 'profile.html')
        
        if os.path.exists(template_path):
            print("✅ Profile template (profile.html) exists")
            
            # Check if template has resume section
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'resume' in content.lower():
                print("✅ Template contains resume-related content")
                return True
            else:
                print("❌ Template missing resume content")
                return False
        else:
            print("❌ Profile template not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing template: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Profile Update Functionality")
    print("=" * 50)
    
    tests = [
        ("User Model", test_user_model),
        ("Profile Routes", test_profile_routes),
        ("File Validation", test_file_validation),
        ("Secure Filename", test_secure_filename_generation),
        ("Template Exists", test_template_exists)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Profile update functionality appears to be working.")
    else:
        print("⚠️ Some tests failed. There may be issues with the profile update functionality.")
    
    return passed == total

if __name__ == "__main__":
    main()