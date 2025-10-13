"""
Test script to verify cache prevention headers on protected routes
"""
import sys
import os
import requests

# Add the parent directory (Hirely root) to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app, db

def test_cache_headers():
    """Test that protected routes have proper cache prevention headers"""
    print("=" * 60)
    print("CACHE PREVENTION TEST")
    print("=" * 60)
    
    app = create_app()
    
    with app.test_client() as client:
        # Test protected routes that should have no-cache headers
        protected_routes = [
            '/user_dashboard',
            '/admin_dashboard',
            '/edit_job/1',  # This will 404 but should still have headers
            '/view_resume/1'  # This will 404 but should still have headers
        ]
        
        for route in protected_routes:
            print(f"\n📍 Testing route: {route}")
            
            try:
                response = client.get(route, follow_redirects=False)
                
                # Check for cache prevention headers
                cache_control = response.headers.get('Cache-Control', '')
                pragma = response.headers.get('Pragma', '')
                expires = response.headers.get('Expires', '')
                last_modified = response.headers.get('Last-Modified', '')
                
                print(f"   Status Code: {response.status_code}")
                print(f"   Cache-Control: {cache_control}")
                print(f"   Pragma: {pragma}")
                print(f"   Expires: {expires}")
                print(f"   Last-Modified: {last_modified}")
                
                # Verify cache prevention headers
                expected_cache_control = 'no-cache, no-store, must-revalidate, private'
                has_cache_prevention = (
                    'no-cache' in cache_control and 
                    'no-store' in cache_control and
                    'must-revalidate' in cache_control
                )
                
                if has_cache_prevention:
                    print("   ✅ Cache prevention headers present")
                else:
                    print("   ❌ Cache prevention headers missing or incomplete")
                
                # Check security headers
                security_headers = {
                    'X-Content-Type-Options': response.headers.get('X-Content-Type-Options', ''),
                    'X-Frame-Options': response.headers.get('X-Frame-Options', ''),
                    'X-XSS-Protection': response.headers.get('X-XSS-Protection', '')
                }
                
                print(f"   Security Headers: {security_headers}")
                
            except Exception as e:
                print(f"   ❌ Error testing route: {e}")
        
        # Test non-protected routes (should not have cache prevention)
        print(f"\n📍 Testing non-protected route: /")
        response = client.get('/')
        cache_control = response.headers.get('Cache-Control', '')
        print(f"   Status Code: {response.status_code}")
        print(f"   Cache-Control: {cache_control}")
        
        if 'no-cache' not in cache_control:
            print("   ✅ Non-protected route properly allows caching")
        else:
            print("   ⚠️  Non-protected route has cache prevention (may be intentional)")
    
    print("\n" + "=" * 60)
    print("✅ CACHE PREVENTION TEST COMPLETED")
    print("=" * 60)
    
    print("\n📋 Expected Behavior After Logout:")
    print("  • Browser back button should show 'Page Expired' or reload from server")
    print("  • Protected content should not be accessible from browser cache")
    print("  • Users should be redirected to login when accessing protected routes")
    print("  • Cache-Control headers prevent browser from storing sensitive pages")

def test_logout_redirect():
    """Test logout functionality and redirection"""
    print("\n" + "=" * 60)
    print("LOGOUT FLOW TEST")
    print("=" * 60)
    
    app = create_app()
    
    with app.test_client() as client:
        # Test logout route
        print("\n📍 Testing logout route")
        response = client.get('/logout', follow_redirects=False)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Location Header: {response.headers.get('Location', 'Not set')}")
        
        # Check logout response headers
        cache_control = response.headers.get('Cache-Control', '')
        print(f"   Cache-Control: {cache_control}")
        
        if response.status_code == 302:
            print("   ✅ Logout properly redirects")
        else:
            print(f"   ⚠️  Unexpected logout response: {response.status_code}")
        
        # Test accessing protected route after logout simulation
        print("\n📍 Testing dashboard access after logout")
        response = client.get('/user_dashboard', follow_redirects=False)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Protected route properly redirects when not logged in")
        else:
            print(f"   ❌ Protected route should redirect: {response.status_code}")
    
    print("\n✅ LOGOUT FLOW TEST COMPLETED")

if __name__ == '__main__':
    try:
        print("Starting Cache Prevention and Logout Tests...")
        test_cache_headers()
        test_logout_redirect()
        print("\n🎉 ALL TESTS COMPLETED!")
        
        print("\n" + "=" * 60)
        print("MANUAL TESTING INSTRUCTIONS")
        print("=" * 60)
        print("1. Start the web application: python main.py")
        print("2. Login to your account (user or admin)")
        print("3. Navigate to dashboard")
        print("4. Logout using the logout button")
        print("5. Try clicking browser's back button")
        print("6. Expected: Page should reload and redirect to login")
        print("7. Should NOT show cached dashboard content")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)