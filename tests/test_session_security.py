"""
Test script to verify session timeout and security enhancements
"""
import sys
import os
import time
from datetime import datetime, timedelta

# Add the parent directory (Hirely root) to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app, db
from app.utils.security import check_session_timeout, invalidate_session, get_session_info, SESSION_TIMEOUT_MINUTES

def test_session_security():
    """Test session security features"""
    print("=" * 50)
    print("SESSION SECURITY TEST")
    print("=" * 50)
    
    app = create_app()
    
    with app.test_client() as client:
        with app.test_request_context():
            # Test 1: Check session timeout with no user
            print("\n1. Testing session timeout with no user...")
            from flask import session
            
            # Clear session first
            session.clear()
            
            result = check_session_timeout()
            print(f"   No user session timeout check: {result}")
            assert result == False, "Should return False for no user session"
            
            # Test 2: Create a valid session
            print("\n2. Creating valid session...")
            session['user_id'] = 1
            session['is_admin'] = True
            session['last_activity'] = datetime.utcnow().isoformat()
            
            result = check_session_timeout()
            print(f"   Valid session check: {result}")
            assert result == True, "Should return True for valid session"
            
            # Test 3: Test session info
            print("\n3. Getting session info...")
            info = get_session_info()
            print(f"   Session info: {info}")
            assert info['user_id'] == 1, "Should have correct user_id"
            assert info['is_admin'] == True, "Should have correct admin status"
            
            # Test 4: Test expired session
            print("\n4. Testing expired session...")
            # Set last activity to more than timeout minutes ago
            expired_time = datetime.utcnow() - timedelta(minutes=SESSION_TIMEOUT_MINUTES + 1)
            session['last_activity'] = expired_time.isoformat()
            
            result = check_session_timeout()
            print(f"   Expired session check: {result}")
            assert result == False, "Should return False for expired session"
            
            # Test 5: Test session invalidation
            print("\n5. Testing session invalidation...")
            session['user_id'] = 2
            session['is_admin'] = False
            session['test_data'] = 'should_be_cleared'
            
            invalidate_session()
            print(f"   Session after invalidation: {dict(session)}")
            assert 'user_id' not in session, "Session should be cleared"
            assert 'test_data' not in session, "All session data should be cleared"
            
            # Test 6: Test invalid timestamp format
            print("\n6. Testing invalid timestamp...")
            session['user_id'] = 3
            session['last_activity'] = 'invalid_timestamp'
            
            result = check_session_timeout()
            print(f"   Invalid timestamp check: {result}")
            assert result == False, "Should return False for invalid timestamp"
            
    print("\n" + "=" * 50)
    print("✅ ALL SESSION SECURITY TESTS PASSED!")
    print("=" * 50)
    
    # Test configuration
    print(f"\nConfiguration:")
    print(f"  Session timeout: {SESSION_TIMEOUT_MINUTES} minutes")
    print(f"  Security features: Session timeout, audit logging, secure logout")

def test_login_logout_flow():
    """Test the enhanced login/logout flow"""
    print("\n" + "=" * 50)
    print("LOGIN/LOGOUT FLOW TEST")
    print("=" * 50)
    
    app = create_app()
    
    with app.test_client() as client:
        # Test login page access
        print("\n1. Testing login page access...")
        response = client.get('/login')
        print(f"   Login page status: {response.status_code}")
        assert response.status_code == 200, "Login page should be accessible"
        
        # Test logout with no session
        print("\n2. Testing logout with no session...")
        response = client.get('/logout')
        print(f"   Logout status: {response.status_code}")
        # Should redirect to login or home
        assert response.status_code in [302, 200], "Logout should handle no session gracefully"
        
        # Test dashboard access without login
        print("\n3. Testing dashboard access without login...")
        response = client.get('/user_dashboard')
        print(f"   Dashboard access status: {response.status_code}")
        # Should redirect to login
        assert response.status_code == 302, "Should redirect to login"
        
    print("\n✅ LOGIN/LOGOUT FLOW TESTS PASSED!")

if __name__ == '__main__':
    try:
        print("Starting Session Security Tests...")
        test_session_security()
        test_login_logout_flow()
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)