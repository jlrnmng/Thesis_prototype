from app import create_app  # Import your factory function from app/__init__.py
from flask import Flask, render_template, request, redirect
import os

# Create the Flask app instance
app = create_app()

from flask import render_template

@app.route('/')
def index():
    # Default page → login
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')  # Make sure this file exists in /templates

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # For now just print to console and redirect
        print(f"User tried to login: {username} | {password}")
        return redirect('/apply')
    return render_template('login.html')

@app.route('/apply')
def apply_page():
    return "<h1>Welcome! You are logged in.</h1>"


if __name__ == '__main__':
    # Print all routes for debugging
    with app.app_context():
        print("\n=== Registered Routes ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint:30s} -> {rule}")

    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Run Flask server
    app.run(debug=True, host='0.0.0.0', port=5000)
