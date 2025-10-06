import os
import sys
import sqlite3
from sqlalchemy import text
from flask import render_template, request, session, redirect, flash, url_for, make_response, send_file
from app import create_app, db
from app.utils.security import secure_route, session_security_check, log_security_event, check_session_timeout, invalidate_session

# Ensure parent dir is importable
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Create Flask app instance
app = create_app()

# Initialize database tables if not created
with app.app_context():
    db.create_all()


# -------------------------------
# Health check for DBs
# -------------------------------
def check_databases(app):
    """Check SQLAlchemy + ChromaDB connectivity status."""
    sql_ok = False
    chroma_ok = False
    ncols = 0

    # SQLAlchemy check
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
        sql_ok = True
        print('SQLAlchemy connection: OK')
    except Exception as e:
        print('SQLAlchemy connection: FAIL ->', e)

    # ChromaDB check
    try:
        # Try to get collections through the matching service
        from matching_service import get_matching_service
        ms = get_matching_service()
        
        # Check if collections are accessible
        resumes_count = ms.resumes_collection.count() if ms.resumes_collection else 0
        jobs_count = ms.jobs_collection.count() if ms.jobs_collection else 0
        total_docs = resumes_count + jobs_count
        
        print(f"ChromaDB connection: OK")
        print(f"ChromaDB collections:")
        print(f"- Resumes: {resumes_count} documents")
        print(f"- Jobs: {jobs_count} documents")
        chroma_ok = True
    except Exception as e:
        print(f'ChromaDB connection: FAIL -> {str(e)}')

    # Final status
    print('\nDatabase Status Summary:')
    print('------------------------')
    if sql_ok:
        print('✓ SQLite Database: Connected')
    else:
        print('✗ SQLite Database: NOT CONNECTED')
        
    if chroma_ok:
        print(f'✓ ChromaDB: Connected ({total_docs} total documents)')
    else:
        print('✗ ChromaDB: NOT CONNECTED')
    print('------------------------')


# -------------------------------
# Import models after app creation
# -------------------------------
from app.models import Job, User, Application

# Import matching service
try:
    from matching_service import get_matching_service
    MATCHING_ENABLED = True
    print("Matching service imported successfully")
except ImportError as e:
    print(f"WARNING: Matching service not available: {e}")
    MATCHING_ENABLED = False


# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def index():
    jobs = Job.query.filter_by(is_active=True).all()
    return render_template('index.html', jobs=jobs)


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/admin_register', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'GET':
        return render_template('admin_register.html')
    
    # POST request - handle admin registration
    print("DEBUG: Processing admin registration")
    
    username = request.form.get('username')
    email = request.form.get('email')
    company_name = request.form.get('company_name')
    company_address = request.form.get('company_address')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([username, email, company_name, company_address, password, confirm_password]):
        flash('All fields are required.', 'error')
        return render_template('admin_register.html')
    
    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return render_template('admin_register.html')
    
    if User.query.filter_by(email=email).first():
        flash('Email already registered.', 'error')
        return render_template('admin_register.html')
    
    try:
        new_admin = User(
            first_name=username,
            last_name='Admin',
            email=email,
            address=company_address,
            is_admin=True
        )
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"DEBUG: Admin created successfully - {email}")
        flash('Admin account created successfully! Please log in.', 'success')
        return redirect('/login')
        
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error creating admin: {e}")
        flash('An error occurred during registration. Please try again.', 'error')
        return render_template('admin_register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    print("DEBUG: Login route accessed")
    
    if request.method == 'GET':
        print("DEBUG: Rendering login form")
        return render_template('login.html')
    
    # POST request - handle login
    print("DEBUG: Processing POST login request")
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    print(f"DEBUG: Email: {email}")
    print(f"DEBUG: Password provided: {'Yes' if password else 'No'}")
    
    if not email or not password:
        flash('Please provide both email and password.', 'error')
        return render_template('login.html')
    
    user = User.query.filter_by(email=email).first()
    print(f"DEBUG: User found: {'Yes' if user else 'No'}")
    
    if user:
        print(f"DEBUG: User ID: {user.id}, Is Admin: {user.is_admin}")
        
        if user.check_password(password):
            print("DEBUG: Password correct, setting session")
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            
            print(f"DEBUG: Session set - user_id: {session.get('user_id')}, is_admin: {session.get('is_admin')}")
            
            if user.is_admin:
                print("DEBUG: Redirecting to admin dashboard")
                return redirect('/admin_dashboard')
            else:
                print("DEBUG: Redirecting to user dashboard")
                return redirect('/user_dashboard')
        else:
            print("DEBUG: Password incorrect")
            flash('Invalid email or password.', 'error')
    else:
        print("DEBUG: User not found")
        flash('Invalid email or password.', 'error')
    
    return render_template('login.html')


@app.route('/user_dashboard')
@secure_route
def user_dashboard():
    print("DEBUG: User dashboard route accessed")
    print(f"DEBUG: Session data: {dict(session)}")
    
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    if not user_id:
        print("DEBUG: No user_id in session, redirecting to login")
        flash('Please log in to access the dashboard.', 'error')
        return redirect('/login')
    
    if is_admin:
        print("DEBUG: User is admin, redirecting to admin dashboard")
        return redirect('/admin_dashboard')
    
    user = User.query.get(user_id)
    if not user:
        print("DEBUG: User not found in database, clearing session")
        session.clear()
        flash('User account not found. Please log in again.', 'error')
        return redirect('/login')
    
    # Get all active jobs
    jobs = Job.query.filter_by(is_active=True).all()
    
    # Calculate match scores for user if they have a resume
    if user.resume and MATCHING_ENABLED:
        try:
            # Get user's resume text (you'll need to extract from file)
            # For now using a placeholder - implement proper extraction
            from app.utils.resume_extractor import extract_resume_text
            
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
            resume_path = os.path.join(upload_folder, user.resume)
            
            if os.path.exists(resume_path):
                resume_text = extract_resume_text(resume_path)
                
                if resume_text:
                    # Get matching service and rank jobs
                    matching_service = get_matching_service(app.config.get('CHROMA_PATH', 'chroma_storage'))
                    job_rankings = matching_service.get_top_jobs_for_resume(
                        resume_text, 
                        jobs,
                        top_n=len(jobs)  # Get all jobs ranked
                    )
                    
                    # Create score dict
                    score_dict = {job_id: score for job_id, score in job_rankings}
                    
                    # Add match scores to jobs
                    for job in jobs:
                        job.match_score = round(score_dict.get(job.id, 0), 0)
                    
                    # Sort jobs by match score (highest first)
                    jobs.sort(key=lambda x: x.match_score, reverse=True)
                    
                    print(f"DEBUG: Calculated match scores for {len(jobs)} jobs")
                else:
                    print("WARNING: Could not extract resume text")
                    for job in jobs:
                        job.match_score = 0
            else:
                print(f"WARNING: Resume file not found at {resume_path}")
                for job in jobs:
                    job.match_score = 0
                    
        except Exception as e:
            print(f"ERROR: Failed to calculate job matches: {e}")
            import traceback
            traceback.print_exc()
            # Fallback - no match scores
            for job in jobs:
                job.match_score = 0
    else:
        # No resume or matching disabled
        for job in jobs:
            job.match_score = 0
    
    applied_job_ids = []

    response = make_response(
        render_template(
            'dashboard_user.html',
            user=user,
            jobs=jobs,
            applied_job_ids=applied_job_ids,
            applied_jobs_count=len(applied_job_ids),
            available_jobs_count=len(jobs),
            match_score=85
        )
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/admin_dashboard')
@secure_route
def admin_dashboard():
    print("DEBUG: Admin dashboard route accessed")
    
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    if not user_id:
        flash('Please log in to access the dashboard.', 'error')
        return redirect('/login')
    
    if not is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect('/user_dashboard')
    
    # Get current admin user
    user = User.query.get(user_id)
    if not user:
        session.clear()
        flash('User account not found. Please log in again.', 'error')
        return redirect('/login')
    
    # Get only jobs created by this admin
    jobs = Job.query.filter_by(created_by=user_id, is_active=True).all()
    
    response = make_response(
        render_template('dashboard_admin.html', user=user, jobs=jobs)
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    if not user_id or not is_admin:
        flash('Please log in as admin to post jobs.', 'error')
        return redirect('/login')
    
    if request.method == 'GET':
        return render_template('post_job.html')
    
    # POST request - create job
    role = request.form.get('role')
    responsibilities = request.form.get('responsibilities')
    requirements = request.form.get('requirements')
    qualifications = request.form.get('qualifications')
    
    if not all([role, responsibilities, requirements, qualifications]):
        flash('All fields are required.', 'error')
        return render_template('post_job.html')
    
    # Combine all fields into one description
    description = f"Responsibilities:\n{responsibilities}\n\nRequirements:\n{requirements}\n\nQualifications:\n{qualifications}"
    
    try:
        new_job = Job(
            role=role,
            description=description,
            is_active=True,
            created_by=user_id  # Associate with current admin
        )
        
        db.session.add(new_job)
        db.session.commit()
        
        # Add job to ChromaDB for vector search
        if MATCHING_ENABLED:
            try:
                matching_service = get_matching_service(app.config.get('CHROMA_PATH', 'chroma_storage'))
                matching_service.add_job_to_db(new_job.id, description, role)
                print(f"DEBUG: Job {new_job.id} added to ChromaDB")
            except Exception as e:
                print(f"WARNING: Failed to add job to ChromaDB: {e}")
        
        flash('Job posted successfully!', 'success')
        return redirect('/admin_dashboard')
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to post job - {e}")
        flash('An error occurred while posting the job.', 'error')
        return render_template('post_job.html')


@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@secure_route
def edit_job(job_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    if not user_id or not is_admin:
        flash('Please log in as admin to edit jobs.', 'error')
        return redirect('/login')
    
    job = Job.query.get_or_404(job_id)
    
    # Check if current admin owns this job
    if job.created_by != user_id:
        flash('Access denied. You can only edit jobs you created.', 'error')
        return redirect('/admin_dashboard')
    
    if request.method == 'GET':
        # Get all applications for this job
        applications = Application.query.filter_by(job_id=job_id).all()
        
        if applications and MATCHING_ENABLED:
            try:
                # Use matching service to rank applicants
                matching_service = get_matching_service(app.config.get('CHROMA_PATH', 'chroma_storage'))
                rankings = matching_service.rank_applicants_for_job(
                    job.description,
                    job.role,
                    applications
                )
                
                # Create a dict for quick score lookup
                score_dict = {app_id: score for app_id, score in rankings}
                
                # Add match scores to applications
                for app in applications:
                    app.match_score = round(score_dict.get(app.id, 0), 2)
                
                # Sort by match score
                applications.sort(key=lambda x: x.match_score, reverse=True)
                
                print(f"DEBUG: Ranked {len(applications)} applications for job {job_id}")
                
            except Exception as e:
                print(f"ERROR: Failed to rank applications: {e}")
                # Fallback to placeholder scores
                for app in applications:
                    app.match_score = 75
        else:
            # No applications or matching disabled
            for app in applications:
                app.match_score = 0
        
        return render_template('edit_job.html', job=job, applications=applications)
    
    # POST request - update job
    role = request.form.get('role')
    description = request.form.get('description')
    
    if not role or not description:
        flash('All fields are required.', 'error')
        return redirect(f'/edit_job/{job_id}')
    
    try:
        job.role = role
        job.description = description
        
        db.session.commit()
        
        # Update job in ChromaDB
        if MATCHING_ENABLED:
            try:
                matching_service = get_matching_service(app.config.get('CHROMA_PATH', 'chroma_storage'))
                matching_service.add_job_to_db(job.id, description, role)
                print(f"DEBUG: Job {job.id} updated in ChromaDB")
            except Exception as e:
                print(f"WARNING: Failed to update job in ChromaDB: {e}")
        
        flash('Job updated successfully!', 'success')
        return redirect(f'/edit_job/{job_id}')
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to update job - {e}")
        flash('An error occurred while updating the job.', 'error')
        return redirect(f'/edit_job/{job_id}')


@app.route('/delete_job/<int:job_id>', methods=['POST'])
@secure_route
def delete_job(job_id):
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    if not user_id or not is_admin:
        flash('Please log in as admin to delete jobs.', 'error')
        return redirect('/login')
    
    job = Job.query.get_or_404(job_id)
    
    # Check if current admin owns this job
    if job.created_by != user_id:
        flash('Access denied. You can only delete jobs you created.', 'error')
        return redirect('/admin_dashboard')
    
    try:
        # Delete associated applications first
        Application.query.filter_by(job_id=job_id).delete()
        
        # Delete the job
        db.session.delete(job)
        db.session.commit()
        
        flash('Job deleted successfully!', 'success')
        return redirect('/admin_dashboard')
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to delete job - {e}")
        flash('An error occurred while deleting the job.', 'error')
        return redirect('/admin_dashboard')


@app.route('/view_resume/<int:user_id>')
def view_resume(user_id):
    admin_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    if not admin_id or not is_admin:
        flash('Please log in as admin to view resumes.', 'error')
        return redirect('/login')
    
    user = User.query.get_or_404(user_id)
    
    # Check if this user has applied to any jobs created by the current admin
    user_applications = Application.query.filter_by(user_id=user_id).all()
    admin_job_ids = [job.id for job in Job.query.filter_by(created_by=admin_id).all()]
    
    has_access = any(app.job_id in admin_job_ids for app in user_applications)
    
    if not has_access:
        flash('Access denied. You can only view resumes of applicants to your own jobs.', 'error')
        return redirect('/admin_dashboard')
    
    if not user.resume:
        flash('No resume available for this user.', 'error')
        return redirect('/admin_dashboard')
    
    # Construct resume file path
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    resume_path = os.path.join(upload_folder, user.resume)
    
    if not os.path.exists(resume_path):
        flash('Resume file not found.', 'error')
        return redirect('/admin_dashboard')
    
    try:
        return send_file(resume_path, as_attachment=False)
    except Exception as e:
        print(f"ERROR: Failed to send resume - {e}")
        flash('An error occurred while viewing the resume.', 'error')
        return redirect('/admin_dashboard')


@app.route('/logout')
def logout():
    print("DEBUG: Logout route accessed")
    
    # Get user info for logging before clearing session
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    user_type = "Admin" if is_admin else "User"
    
    # Clear all session data
    session.clear()
    
    # Force session to be deleted on client
    session.permanent = False
    
    # Log the logout event for security audit
    if user_id:
        print(f"SECURITY LOG: {user_type} ID {user_id} logged out successfully")
    
    flash('You have been logged out successfully.', 'success')
    
    # Create response with security headers
    response = make_response(redirect(url_for('index')))
    
    # Add security headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # Clear any authentication cookies
    response.set_cookie('session', '', expires=0, secure=True, httponly=True, samesite='Strict')
    
    return response


@app.route('/api/job_matches', methods=['GET'])
def get_job_matches():
    """API endpoint to get job matches for current user"""
    user_id = session.get('user_id')
    
    if not user_id:
        return {'success': False, 'error': 'Not authenticated'}, 401
    
    user = User.query.get(user_id)
    if not user or not user.resume:
        return {'success': False, 'error': 'No resume found'}, 404
    
    if not MATCHING_ENABLED:
        return {'success': False, 'error': 'Matching service not available'}, 503
    
    try:
        from app.utils.resume_extractor import extract_resume_text
        
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        resume_path = os.path.join(upload_folder, user.resume)
        
        if not os.path.exists(resume_path):
            return {'success': False, 'error': 'Resume file not found'}, 404
        
        resume_text = extract_resume_text(resume_path)
        if not resume_text:
            return {'success': False, 'error': 'Could not extract resume text'}, 500
        
        # Get all active jobs
        jobs = Job.query.filter_by(is_active=True).all()
        
        # Get matching service and rank jobs
        matching_service = get_matching_service(app.config.get('CHROMA_PATH', 'chroma_storage'))
        job_rankings = matching_service.get_top_jobs_for_resume(
            resume_text, 
            jobs,
            top_n=10  # Top 10 matches
        )
        
        # Format results
        results = []
        for job_id, score in job_rankings:
            job = Job.query.get(job_id)
            if job:
                results.append({
                    'job_id': job.id,
                    'role': job.role,
                    'match_score': round(score, 2),
                    'description_preview': job.description[:150] + '...' if len(job.description) > 150 else job.description
                })
        
        return {'success': True, 'matches': results}, 200
        
    except Exception as e:
        print(f"ERROR: Failed to get job matches: {e}")
        return {'success': False, 'error': str(e)}, 500


@app.route('/apply/<int:job_id>', methods=['POST'])
def apply_to_job(job_id):
    """Handle job application submission"""
    user_id = session.get('user_id')
    
    if not user_id:
        return {'success': False, 'error': 'Please log in first'}, 401
    
    # Get user and job
    user = User.query.get(user_id)
    job = Job.query.get(job_id)
    
    if not user or not job:
        return {'success': False, 'error': 'Invalid user or job'}, 404
    
    # Check if already applied
    existing_app = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing_app:
        return {'success': False, 'error': 'You have already applied to this job'}, 400
    
    try:
        # Prefer extracting resume from saved user file if available
        resume_text = f"Resume for {user.full_name}"
        if user.resume:
            try:
                from app.utils.resume_extractor import extract_resume_text
                upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
                resume_path = os.path.join(upload_folder, user.resume)
                if os.path.exists(resume_path):
                    extracted = extract_resume_text(resume_path)
                    if extracted:
                        resume_text = extracted
                    else:
                        print(f"DEBUG: Extraction returned empty for {resume_path}")
                else:
                    print(f"DEBUG: Resume file not found at {resume_path}")
            except Exception as e:
                print(f"WARNING: Could not extract saved resume: {e}")
        
        # Create application
        new_application = Application(
            user_id=user_id,
            job_id=job_id,
            resume_text=resume_text
        )
        
        db.session.add(new_application)
        db.session.commit()
        
        # Add resume to ChromaDB
        if MATCHING_ENABLED:
            try:
                matching_service = get_matching_service(app.config.get('CHROMA_PATH', 'chroma_storage'))
                matching_service.add_resume_to_db(user_id, resume_text)
                print(f"DEBUG: Resume for user {user_id} added to ChromaDB")
            except Exception as e:
                print(f"WARNING: Failed to add resume to ChromaDB: {e}")
        
        return {'success': True, 'message': 'Application submitted successfully'}
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to submit application: {e}")
        return {'success': False, 'error': 'Failed to submit application'}, 500


# -------------------------------
# Error handlers
# -------------------------------
@app.errorhandler(404)
def not_found_error(error):
    print(f"DEBUG: 404 error for path: {request.path}")
    return render_template('login.html'), 404


@app.errorhandler(500)
def internal_error(error):
    print(f"DEBUG: 500 error: {error}")
    db.session.rollback()
    return render_template('login.html'), 500


# -------------------------------
# Main entry
# -------------------------------
if __name__ == '__main__':
    print("Template folder set to:", app.template_folder)

    with app.app_context():
        print("\n=== Registered Routes ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint:30s} -> {rule.rule}")

    # Ensure upload folder exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Run DB health check
    try:
        check_databases(app)
    except Exception:
        pass

    print("\n=== Starting Flask App ===")
    print("Access the application at: http://localhost:5000")
    print("Login page: http://localhost:5000/login")
    print("Register page: http://localhost:5000/register")
    print(f"Matching service: {'ENABLED' if MATCHING_ENABLED else 'DISABLED'}")
    
    # Start server
    app.run(debug=True, host='0.0.0.0', port=5000)