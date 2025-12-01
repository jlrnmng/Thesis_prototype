#!/usr/bin/env python3
"""
WSGI entry point for Render deployment.
This file allows Render to find and run the Flask app correctly.
"""
import sys
import os

# Get the absolute path to the Hirely directory
hirely_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Hirely')

print(f"WSGI: Setting up path to: {hirely_path}")

# Add the Hirely directory to Python path FIRST
sys.path.insert(0, hirely_path)

# Change working directory to Hirely so relative paths work
os.chdir(hirely_path)

print(f"WSGI: Changed to directory: {os.getcwd()}")
print(f"WSGI: Files in directory: {os.listdir('.')}")

# Now import the main module which will handle the app creation
try:
    import main
    app = main.app  # Get the app instance from main.py
    print("WSGI: Successfully imported app from main.py")
except Exception as main_error:
    print(f"WSGI: Failed to import main.py: {main_error}")
    try:
        # Fallback to simple app for testing
        import simple_app
        app = simple_app.create_app()
        print("WSGI: Using simple_app as fallback")
    except Exception as fallback_error:
        print(f"WSGI: Fallback also failed: {fallback_error}")
        raise main_error  # Raise the original error
        
except Exception as e:
    print(f"WSGI Error: {e}")
    print(f"WSGI: Current working directory: {os.getcwd()}")
    print(f"WSGI: Python path: {sys.path[:3]}")  # Show first 3 entries
    print(f"WSGI: Files in current directory: {os.listdir('.')}")
    if os.path.exists('app'):
        print(f"WSGI: Files in app directory: {os.listdir('app')}")
    raise

if __name__ == "__main__":
    app.run()