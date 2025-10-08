"""
Main routes for HTML pages with AI matching integration
"""
from flask import Blueprint, render_template, request, session, redirect, flash, jsonify, send_file, current_app, make_response
from app.models import Job, User, Application, db
from app.utils.security import secure_route, session_security_check, log_security_event
from datetime import datetime
import os

try:
    from matching_service import get_matching_service
    MATCHING_ENABLED = True
except ImportError:
    MATCHING_ENABLED = False
    print("WARNING: Matching service not available")

try:
    from app.utils.resume_extractor import extract_resume_text
    RESUME_EXTRACTION_ENABLED = True
except Exception as e:
    RESUME_EXTRACTION_ENABLED = False
    print("WARNING: Resume extractor not available:", repr(e))

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page"""
    jobs = Job.query.filter_by(is_active=True).all()
    return render_template('index.html', jobs=jobs)


@main_bp.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')


@main_bp.route('/register')
def register_page():
    """User registration page"""
    return render_template('register.html')


@main_bp.route('/admin_register')
def admin_register_page():
    """Admin registration page"""
    return render_template('admin_register.html')


@main_bp.route('/dashboard')
@secure_route
def dashboard():
    """Main dashboard route - redirects to appropriate dashboard based on user type"""
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access the dashboard.', 'error')
        return redirect('/')
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        session.clear()
        return redirect('/')
    
    # Redirect to appropriate dashboard
    if user.is_admin:
        return redirect('/admin_dashboard')
    else:
        return redirect('/user_dashboard')


@main_bp.route('/logout')
def logout():
    """Handle logout with proper session clearing and security"""
    from app.utils.security import invalidate_session, log_security_event
    
    # Get user info for logging before clearing session
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    # Log security event
    if user_id:
        user_type = "Admin" if is_admin else "User"
        log_security_event(
            event_type="logout",
            user_id=user_id,
            details=f"{user_type} logged out successfully"
        )
    
    # Clear session using security utility
    invalidate_session()
    
    # Clear all session data
    session.clear()
    
    # Add success message
    flash('You have been successfully logged out.', 'success')
    
    # Redirect to home page
    response = make_response(redirect('/'))
    
    # Add security headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


@main_bp.route('/user_dashboard')
@secure_route
def user_dashboard():
    """User dashboard with AI job recommendations"""
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    if not user_id:
        flash('Please log in to access the dashboard.', 'error')
        return redirect('/login')
    
    if is_admin:
        return redirect('/admin_dashboard')
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        flash('User account not found. Please log in again.', 'error')
        return redirect('/login')
    
    jobs = Job.query.filter_by(is_active=True).all()
    
    print(f"DEBUG: MATCHING_ENABLED: {MATCHING_ENABLED}")
    
    if MATCHING_ENABLED:
        try:
            resume_text = None
            
            # First, try to get resume text from the user's most recent application
            latest_application = Application.query.filter_by(
                user_id=user_id
            ).order_by(Application.submission_date.desc()).first()
            
            print(f"DEBUG: Latest application found: {latest_application is not None}")
            
            if latest_application and latest_application.resume_text:
                resume_text = latest_application.resume_text
                print(f"DEBUG: Resume text from application: {len(resume_text)} chars")
            
            # If no application resume text, try to extract from uploaded resume file
            elif user.resume and RESUME_EXTRACTION_ENABLED:
                print(f"DEBUG: Trying to extract from uploaded resume: {user.resume}")
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                resume_path = os.path.join(upload_folder, user.resume)
                if os.path.exists(resume_path):
                    try:
                        resume_text = extract_resume_text(resume_path, preprocess=True)
                        print(f"DEBUG: Extracted resume text: {len(resume_text)} chars")
                    except Exception as e:
                        print(f"DEBUG: Failed to extract resume text: {e}")
            
            if resume_text and len(resume_text.strip()) > 0:
                matching_service = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
                job_rankings = matching_service.get_top_jobs_for_resume(
                    resume_text, 
                    jobs,
                    top_n=len(jobs)
                )
                
                print(f"DEBUG: Job rankings: {job_rankings[:3]}")  # Show first 3 rankings
                
                score_dict = {job_id: score for job_id, score in job_rankings}
                for job in jobs:
                    job.match_score = round(score_dict.get(job.id, 0), 0)
                
                jobs.sort(key=lambda x: x.match_score, reverse=True)
                print(f"DEBUG: Calculated match scores for {len(jobs)} jobs")
                print(f"DEBUG: Top 3 job scores: {[(job.role, job.match_score) for job in jobs[:3]]}")
            else:
                print("DEBUG: No resume text available - user needs to upload resume or apply to a job")
                for job in jobs:
                    job.match_score = 0
                    
        except Exception as e:
            print(f"ERROR: Failed to calculate job matches: {e}")
            import traceback
            traceback.print_exc()
            for job in jobs:
                job.match_score = 0
    else:
        print("DEBUG: Matching not enabled - setting all scores to 0")
        for job in jobs:
            job.match_score = 0
    
    applied_job_ids = []
    
    return render_template(
        'dashboard_user.html',
        user=user,
        jobs=jobs,
        applied_job_ids=applied_job_ids,
        applied_jobs_count=len(applied_job_ids),
        available_jobs_count=len(jobs),
        match_score=85
    )


@main_bp.route('/admin_dashboard')
@secure_route
def admin_dashboard():
    """Admin dashboard"""
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    if not user_id:
        flash('Please log in to access the dashboard.', 'error')
        return redirect('/login')
    
    if not is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect('/user_dashboard')
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        flash('User account not found. Please log in again.', 'error')
        return redirect('/login')
    
    # Get only jobs created by this admin
    jobs = Job.query.filter_by(created_by=user_id, is_active=True).all()
    
    return render_template('dashboard_admin.html', user=user, jobs=jobs)


@main_bp.route('/post_job', methods=['GET', 'POST'])
@secure_route
def post_job():
    """Post new job"""
    user_id = session.get('user_id')
    is_admin = session.get('is_admin')
    
    if not user_id or not is_admin:
        flash('Please log in as admin to post jobs.', 'error')
        return redirect('/login')
    
    if request.method == 'GET':
        return render_template('post_job.html')
    
    role = request.form.get('role')
    responsibilities = request.form.get('responsibilities')
    requirements = request.form.get('requirements')
    qualifications = request.form.get('qualifications')
    
    if not all([role, responsibilities, requirements, qualifications]):
        flash('All fields are required.', 'error')
        return render_template('post_job.html')
    
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
        
        if MATCHING_ENABLED:
            try:
                matching_service = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
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


@main_bp.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@secure_route
def edit_job(job_id):
    """Edit job and view ranked applicants"""
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
        applications = Application.query.filter_by(job_id=job_id).all()
        
        if applications and MATCHING_ENABLED:
            try:
                matching_service = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
                rankings = matching_service.rank_applicants_for_job(
                    job.description,
                    job.role,
                    applications
                )
                
                score_dict = {app_id: score for app_id, score in rankings}
                for app in applications:
                    app.match_score = round(score_dict.get(app.id, 0), 1)
                
                applications.sort(key=lambda x: x.match_score, reverse=True)
                print(f"DEBUG: Ranked {len(applications)} applications for job {job_id}")
                
            except Exception as e:
                print(f"ERROR: Failed to rank applications: {e}")
                for app in applications:
                    app.match_score = 75
        else:
            for app in applications:
                app.match_score = 0
        
        return render_template('edit_job.html', job=job, applications=applications)
    
    role = request.form.get('role')
    description = request.form.get('description')
    
    if not role or not description:
        flash('All fields are required.', 'error')
        return redirect(f'/edit_job/{job_id}')
    
    try:
        job.role = role
        job.description = description
        db.session.commit()
        
        if MATCHING_ENABLED:
            try:
                matching_service = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
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


@main_bp.route('/delete_job/<int:job_id>', methods=['POST'])
@secure_route
def delete_job(job_id):
    """Delete job"""
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
        Application.query.filter_by(job_id=job_id).delete()
        db.session.delete(job)
        db.session.commit()
        
        flash('Job deleted successfully!', 'success')
        return redirect('/admin_dashboard')
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to delete job - {e}")
        flash('An error occurred while deleting the job.', 'error')
        return redirect('/admin_dashboard')


@main_bp.route('/view_resume/<int:user_id>')
@secure_route
def view_resume(user_id):
    """View resume"""
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
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
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


@main_bp.route('/apply/<int:job_id>', methods=['POST'])
@secure_route
def apply_to_job(job_id):
    """Apply to job"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'Please log in first'}), 401
    
    user = User.query.get(user_id)
    job = Job.query.get(job_id)
    
    if not user or not job:
        return jsonify({'success': False, 'error': 'Invalid user or job'}), 404
    
    existing_app = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
    if existing_app:
        return jsonify({'success': False, 'error': 'You have already applied to this job'}), 400
    
    try:
        resume_text = ""
        if user.resume and RESUME_EXTRACTION_ENABLED:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            resume_path = os.path.join(upload_folder, user.resume)
            if os.path.exists(resume_path):
                # Extract resume text with NLP preprocessing enabled
                resume_text = extract_resume_text(resume_path, preprocess=True)
        
        if not resume_text:
            resume_text = f"Resume for {user.full_name}"
        
        new_application = Application(
            user_id=user_id,
            job_id=job_id,
            resume_text=resume_text
        )
        
        db.session.add(new_application)
        db.session.commit()
        
        if MATCHING_ENABLED and resume_text:
            try:
                matching_service = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
                matching_service.add_resume_to_db(user_id, resume_text)
                print(f"DEBUG: Resume for user {user_id} added to ChromaDB")
            except Exception as e:
                print(f"WARNING: Failed to add resume to ChromaDB: {e}")
        
        return jsonify({'success': True, 'message': 'Application submitted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to submit application: {e}")
        return jsonify({'success': False, 'error': 'Failed to submit application'}), 500


@main_bp.route('/profile')
def profile():
    """User profile page"""
    # Basic session check without timeout enforcement
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access your profile.', 'error')
        return redirect('/')
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'error')
        session.clear()
        return redirect('/')
    
    # Update last activity for session management
    session['last_activity'] = datetime.utcnow().isoformat()
    
    # Apply cache prevention
    response = make_response(render_template('profile.html', user=user))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


@main_bp.route('/update_profile', methods=['POST'])
def update_profile():
    """Update user profile information"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Please log in to update your profile'}), 401
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Update last activity
    session['last_activity'] = datetime.utcnow().isoformat()
    
    try:
        # Update personal information
        user.first_name = request.form.get('first_name', '').strip()
        user.last_name = request.form.get('last_name', '').strip()
        user.middle_name = request.form.get('middle_name', '').strip()
        user.email = request.form.get('email', '').strip()
        user.phone = request.form.get('phone', '').strip()
        user.address = request.form.get('address', '').strip()
        
        # Validate required fields
        if not user.first_name or not user.last_name or not user.email:
            return jsonify({'success': False, 'error': 'First name, last name, and email are required'}), 400
        
        # Check email uniqueness (if changed)
        existing_user = User.query.filter(User.email == user.email, User.id != user.id).first()
        if existing_user:
            return jsonify({'success': False, 'error': 'Email already exists'}), 400
        
        # Handle resume upload if provided
        if 'resume' in request.files:
            resume_file = request.files['resume']
            if resume_file and resume_file.filename:
                if resume_file.filename.lower().endswith('.pdf'):
                    # Generate secure filename
                    import time
                    timestamp = str(int(time.time()))
                    filename = f"{user.first_name}_{user.last_name}_Resume_{timestamp}.pdf"
                    
                    # Save file
                    upload_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), filename)
                    resume_file.save(upload_path)
                    
                    # Delete old resume if exists
                    if user.resume:
                        old_resume_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), user.resume)
                        if os.path.exists(old_resume_path):
                            os.remove(old_resume_path)
                    
                    user.resume = filename
                else:
                    return jsonify({'success': False, 'error': 'Only PDF files are allowed for resume'}), 400
        
        db.session.commit()
        
        # Log security event
        log_security_event(
            event_type="profile_update",
            user_id=user_id,
            details=f"User {user.email} updated profile information"
        )
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to update profile: {e}")
        return jsonify({'success': False, 'error': 'Failed to update profile'}), 500


@main_bp.route('/download_resume/<int:user_id>')
@secure_route
def download_resume(user_id):
    """Download user's resume"""
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Please log in to download resumes.', 'error')
        return redirect('/')
    
    current_user = User.query.get(current_user_id)
    if not current_user:
        flash('Session expired. Please log in again.', 'error')
        session.clear()
        return redirect('/')
    
    target_user = User.query.get(user_id)
    if not target_user:
        flash('User not found', 'error')
        return redirect('/profile' if current_user_id == user_id else '/dashboard')
    
    # Users can only download their own resume, admins can download any
    if not current_user.is_admin and current_user_id != user_id:
        flash('Access denied', 'error')
        return redirect('/dashboard')
    
    if not target_user.resume:
        flash('Resume not found', 'error')
        return redirect('/profile' if current_user_id == user_id else '/dashboard')
    
    resume_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), target_user.resume)
    
    if not os.path.exists(resume_path):
        flash('Resume file not found', 'error')
        return redirect('/profile' if current_user_id == user_id else '/dashboard')
    
    # Log download for security audit
    log_security_event(
        event_type="resume_download",
        user_id=current_user_id,
        details=f"User {current_user.email} downloaded resume for user {target_user.email}"
    )
    
    return send_file(resume_path, as_attachment=True, download_name=target_user.resume)