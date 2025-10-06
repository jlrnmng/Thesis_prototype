"""
Main routes for HTML pages with AI matching integration
"""
from flask import Blueprint, render_template, request, session, redirect, flash, jsonify, send_file, current_app
from app.models import Job, User, Application, db
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


@main_bp.route('/user_dashboard')
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
    
    if user.resume and MATCHING_ENABLED and RESUME_EXTRACTION_ENABLED:
        try:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            resume_path = os.path.join(upload_folder, user.resume)
            
            if os.path.exists(resume_path):
                resume_text = extract_resume_text(resume_path)
                
                if resume_text:
                    matching_service = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
                    job_rankings = matching_service.get_top_jobs_for_resume(
                        resume_text, 
                        jobs,
                        top_n=len(jobs)
                    )
                    
                    score_dict = {job_id: score for job_id, score in job_rankings}
                    for job in jobs:
                        job.match_score = round(score_dict.get(job.id, 0), 0)
                    
                    jobs.sort(key=lambda x: x.match_score, reverse=True)
                    print(f"DEBUG: Calculated match scores for {len(jobs)} jobs")
                else:
                    for job in jobs:
                        job.match_score = 0
            else:
                for job in jobs:
                    job.match_score = 0
                    
        except Exception as e:
            print(f"ERROR: Failed to calculate job matches: {e}")
            import traceback
            traceback.print_exc()
            for job in jobs:
                job.match_score = 0
    else:
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
                    app.match_score = round(score_dict.get(app.id, 0), 2)
                
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


@main_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect('/')


@main_bp.route('/apply/<int:job_id>', methods=['POST'])
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
                resume_text = extract_resume_text(resume_path)
        
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