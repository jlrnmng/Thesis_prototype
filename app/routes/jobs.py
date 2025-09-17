from flask import Blueprint, request, jsonify, current_app
from app.models import db, Job
from app import model, kmeans_model, jobs_collection
from app.utils.decorators import admin_required

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/', methods=['GET'])
def get_jobs():
    try:
        # Get only active jobs (available to all authenticated users)
        jobs = Job.query.filter_by(is_active=True).all()
        return jsonify([job.to_dict() for job in jobs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/', methods=['POST'])
@admin_required
def add_job():
    try:
        # Check if models are loaded
        if not all([model, kmeans_model, jobs_collection]):
            return jsonify({'error': 'System not fully initialized'}), 503
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        role = data.get('role')
        description = data.get('description')
        
        if not all([role, description]):
            return jsonify({'error': 'Missing role or description'}), 400
        
        # Combine role and description for vectorization
        role_jobdesc = f"{role} {description}"
        
        # Vectorize
        job_vector = model.encode([role_jobdesc])
        
        # Predict cluster
        cluster_id = int(kmeans_model.predict(job_vector)[0])
        
        # Save to database
        new_job = Job(role=role, description=description, cluster_id=cluster_id)
        db.session.add(new_job)
        db.session.commit()
        
        # Save to ChromaDB
        jobs_collection.add(
            ids=[str(new_job.id)],
            embeddings=job_vector.tolist(),
            metadatas=[{"role": role, "cluster_id": cluster_id}]
        )
        
        return jsonify({
            'message': 'Job added successfully',
            'job': new_job.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@admin_required
def delete_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        job.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Job deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500