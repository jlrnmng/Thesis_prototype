from flask import Blueprint, request, jsonify, session, current_app, redirect, flash, render_template
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # Get form data with correct field names
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        resume = request.files.get('resume')

        # Basic validation
        if not last_name or not first_name or not email or not password:
            flash('Please fill in all required fields.', 'error')
            return redirect('/register')

        # Resume is required for regular users
        if not resume:
            flash('Resume is required for registration.', 'error')
            return redirect('/register')

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please use a different email.', 'error')
            return redirect('/register')

        # Save resume file
        resume_filename = None
        if resume:
            filename = secure_filename(resume.filename)
            # Add timestamp to avoid conflicts
            import time
            timestamp = str(int(time.time()))
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            resume.save(upload_path)
            resume_filename = filename

        # Create user
        user = User(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            email=email,
            phone=phone,
            address=address,
            resume=resume_filename,
            is_admin=False
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect('/login')

    except Exception as e:
        db.session.rollback()
        flash(f'Registration failed: {str(e)}', 'error')
        return redirect('/register')


@auth_bp.route('/admin_register', methods=['POST'])
def admin_register():
    try:
        # Check if any admin already exists
        if User.query.filter_by(is_admin=True).first():
            flash('An admin already exists in the system.', 'error')
            return redirect('/login')
            
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        company_name = request.form.get('company_name')
        company_address = request.form.get('company_address')
        
        # Basic validation
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all required fields.', 'error')
            return redirect('/admin_register')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect('/admin_register')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return redirect('/admin_register')
            
        # Create admin user
        user = User(
            last_name=username,  # Using username as last_name for admin
            first_name='Admin',
            middle_name=None,
            email=email,
            phone=None,
            address=company_address,
            resume=None,
            is_admin=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Admin account created successfully! Please log in.', 'success')
        return redirect('/login')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Admin registration failed: {str(e)}', 'error')
        return redirect('/admin_register')


# Keep the API endpoints for potential future use
@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract data
        last_name = data.get('last_name')
        first_name = data.get('first_name')
        middle_name = data.get('middle_name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        address = data.get('address')

        # Basic validation
        if not last_name or not first_name or not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400

        # Check duplicates
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409

        # Create user
        user = User(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            email=email,
            phone=phone,
            address=address,
            is_admin=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/create-first-admin', methods=['POST'])
def create_first_admin():
    try:
        # Check if any admin already exists
        if User.query.filter_by(is_admin=True).first():
            return jsonify({'error': 'An admin already exists'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409
            
        user = User(
            last_name=username,
            first_name='Admin',
            email=email,
            is_admin=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'First admin created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400
        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=email).first()
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = 'admin' if user.is_admin else 'user'
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict(),
                'is_admin': user.is_admin  # 👈 include admin status
            }), 200
            
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/api/check', methods=['GET'])
def check_auth():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({'authenticated': True, 'user': user.to_dict()}), 200
    
    return jsonify({'authenticated': False}), 200


@auth_bp.route('/admins', methods=['GET'])
def list_admins():
    admins = User.query.filter_by(is_admin=True).all()
    return jsonify([{
        'id': admin.id,
        'email': admin.email,
        'first_name': admin.first_name,
        'last_name': admin.last_name
    } for admin in admins]), 200
