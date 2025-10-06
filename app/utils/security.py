"""
Security utilities for session management and authentication
"""
from flask import session, current_app, make_response
from datetime import datetime, timedelta
import functools

# Session timeout in minutes
SESSION_TIMEOUT_MINUTES = 30

def check_session_timeout():
    """
    Check if the current session has timed out
    Returns True if session is valid, False if timed out
    """
    if 'user_id' not in session:
        return False
    
    last_activity = session.get('last_activity')
    if not last_activity:
        # No last activity recorded, set it now
        session['last_activity'] = datetime.utcnow().isoformat()
        return True
    
    try:
        last_activity_time = datetime.fromisoformat(last_activity)
        current_time = datetime.utcnow()
        
        # Check if session has timed out
        if current_time - last_activity_time > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            return False
        
        # Update last activity time
        session['last_activity'] = current_time.isoformat()
        return True
        
    except (ValueError, TypeError):
        # Invalid timestamp format, clear session
        return False

def invalidate_session():
    """
    Completely invalidate the current session
    """
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    # Log session invalidation
    if user_id:
        user_type = "Admin" if is_admin else "User"
        print(f"SECURITY LOG: Session invalidated for {user_type} ID {user_id}")
    
    # Clear all session data
    session.clear()
    session.permanent = False

def no_cache(f):
    """
    Decorator to prevent browser caching of protected pages
    This prevents users from accessing protected content via browser back button after logout
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        
        # Add headers to prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Additional security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    return decorated_function

def session_security_check(f):
    """
    Decorator to check session timeout and validity
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if 'user_id' not in session:
            return f(*args, **kwargs)  # Let the route handle unauthenticated users
        
        # Check session timeout
        if not check_session_timeout():
            invalidate_session()
            # The route will detect the cleared session and redirect to login
        
        return f(*args, **kwargs)
    
    return decorated_function

def secure_route(f):
    """
    Combined decorator for session security and cache prevention
    Use this on all protected routes that require authentication
    """
    @functools.wraps(f)
    @no_cache
    @session_security_check
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated_function

def log_security_event(event_type, user_id=None, details=None):
    """
    Log security-related events for audit purposes
    """
    timestamp = datetime.utcnow().isoformat()
    user_info = f"User ID {user_id}" if user_id else "Unknown user"
    details_str = f" - {details}" if details else ""
    
    print(f"SECURITY LOG [{timestamp}]: {event_type} - {user_info}{details_str}")

def get_session_info():
    """
    Get information about the current session for debugging/monitoring
    """
    if 'user_id' not in session:
        return None
    
    last_activity = session.get('last_activity')
    if last_activity:
        try:
            last_activity_time = datetime.fromisoformat(last_activity)
            time_since_activity = datetime.utcnow() - last_activity_time
            minutes_since_activity = time_since_activity.total_seconds() / 60
        except (ValueError, TypeError):
            minutes_since_activity = None
    else:
        minutes_since_activity = None
    
    return {
        'user_id': session.get('user_id'),
        'is_admin': session.get('is_admin'),
        'last_activity': last_activity,
        'minutes_since_activity': minutes_since_activity,
        'timeout_minutes': SESSION_TIMEOUT_MINUTES
    }