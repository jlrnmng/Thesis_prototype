from flask import Blueprint, request, jsonify, session
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.utils.decorators import login_required, admin_required
import os

auth_bp = Blueprint('auth', __name__)

from flask import Blueprint, request, jsonify, session, current_app
from app.models import db, User
from werkzeug.utils import secure_filename
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # 📝 Get form data
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('number')
        address = request.form.get('address')
        role_admin = request.form.get('role_admin')  # "on" if checked
        resume = request.files.get('resume')

        # ✅ Basic validation
        if not last_name or not first_name or not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400

        # ✅ Resume is required if NOT admin
        if not role_admin and not resume:
            return jsonify({'error': 'Resume is required for non-admin users'}), 400

        # ✅ Check duplicates (email only, since names can repeat)
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409

        # ✅ Save resume file if uploaded
        resume_filename = None
        if resume:
            filename = secure_filename(resume.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            resume.save(upload_path)
            resume_filename = filename  # store in DB if needed

        # ✅ Create and store the user
        user = User(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            email=email,
            phone=phone,
            address=address,
            is_admin=bool(role_admin),
            resume=resume_filename
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@auth_bp.route('/create-first-admin', methods=['POST'])
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
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
            
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409
            
        user = User(username=username, email=email, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'First admin created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'Missing username or password'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict()
            }), 200
            
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({'authenticated': True, 'user': user.to_dict()}), 200
    
    return jsonify({'authenticated': False}), 200