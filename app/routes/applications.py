from flask import Blueprint, request, jsonify, session
from app.models import db, Application, Job
from app.utils.pdf_processor import extract_text_from_pdf
from app.utils.decorators import login_required

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/', methods=['POST'])
@login_required
def apply_for_job():
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user_id = session['user_id']
        job_id = request.form.get('job_id')
        
        if not job_id:
            return jsonify({'error': 'Job ID is required'}), 400
            
        # Get the job to retrieve its cluster_id
        job = Job.query.get_or_404(job_id)
        
        # Check if resume file is provided
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
            
        resume_file = request.files['resume']
        if resume_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(resume_file)
        
        # Create application
        application = Application(
            user_id=user_id,
            job_id=job_id,
            cluster_id=job.cluster_id,
            resume_text=resume_text
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@applications_bp.route('/user', methods=['GET'])
@login_required
def get_user_applications():
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
            
        user_id = session['user_id']
        applications = Application.query.filter_by(user_id=user_id).all()
        
        result = []
        for app in applications:
            app_data = app.to_dict()
            app_data['job'] = app.job.to_dict()
            result.append(app_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500