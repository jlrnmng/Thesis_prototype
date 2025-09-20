from flask import Blueprint, request, jsonify, session
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.utils.decorators import login_required, admin_required
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


@auth_bp.route('/create-admin', methods=['POST'])
def create_admin():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    middle_name = data.get('middle_name')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    # Prevent duplicate emails
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_admin = User(
        email=email,
        password_hash=hashed_password,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        role='admin'
    )

    db.session.add(new_admin)
    db.session.commit()
    return jsonify({'message': f'Admin {email} created successfully'})


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict(),
                'is_admin': user.is_admin  # 👈 include admin status
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


@auth_bp.route('/admins', methods=['GET'])
def list_admins():
    admins = User.query.filter_by(is_admin=True).all()
    return jsonify([{
        'id': admin.id,
        'email': admin.email,
        'first_name': admin.first_name,
        'last_name': admin.last_name
    } for admin in admins]), 200
