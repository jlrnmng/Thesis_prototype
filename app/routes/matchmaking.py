from flask import Blueprint, request, jsonify, session, current_app
from app.models import db, Application, Job
from rank_bm25 import BM25Okapi
import numpy as np
import heapq
from app.utils.decorators import login_required

matchmaking_bp = Blueprint('matchmaking', __name__)

def _get_snippet(text, term, radius=40):
    text_lower = text.lower()
    idx = text_lower.find(term)
    if idx == -1:
        return ''
    start = max(0, idx - radius)
    end = min(len(text), idx + len(term) + radius)
    return text[start:end].strip()

@matchmaking_bp.route('/', methods=['GET'])
@login_required
def get_job_matches():
    try:
        user_id = session['user_id']

        # Get user's most recent application
        latest_application = Application.query.filter_by(
            user_id=user_id
        ).order_by(Application.submission_date.desc()).first()

        if not latest_application:
            return jsonify({'error': 'No applications found for this user'}), 404

        user_resume_text = latest_application.resume_text or ""

        # Get all active jobs
        jobs = Job.query.filter_by(is_active=True).all()
        
        # Use matching service for improved hybrid scoring
        from matching_service import get_matching_service
        ms = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
        
        # Get top 3 job matches using hybrid scoring (70% cosine + 30% BM25)
        top_matches = ms.get_top_jobs_for_resume(user_resume_text, jobs, top_n=3)
        
        # Map job IDs to full job objects
        job_map = {job.id: job for job in jobs}
        top_jobs = [job_map[job_id] for job_id, _ in top_matches]
        top_scores = [score for _, score in top_matches]

        # Prepare response
        results = []
        for job, score in zip(top_jobs, top_scores):
            results.append({
                'job_id': job.id,
                'role': job.role,
                'score': float(score),
                'description_preview': (
                    job.description[:100] + '...'
                    if len(job.description) > 100
                    else job.description
                )
            })

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@matchmaking_bp.route('/explain/<int:job_id>', methods=['GET'])
@login_required
def explain_matchmaking(job_id):
    try:
        user_id = session['user_id']

        # Get user's most recent application
        latest_application = Application.query.filter_by(
            user_id=user_id
        ).order_by(Application.submission_date.desc()).first()

        if not latest_application:
            return jsonify({'error': 'No applications found for this user'}), 404

        user_resume_text = latest_application.resume_text or ""

        # Get the job
        job = Job.query.get_or_404(job_id)
        
        # Use matching service for improved hybrid scoring
        from matching_service import get_matching_service
        ms = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
        
        # Get similarity scores using both cosine and BM25
        job_desc = f"{job.role} {job.description}"
        cosine_score = ms._get_cosine_similarity_scores(user_resume_text, [job_desc])[0]
        bm25_score = ms._get_bm25_scores(user_resume_text, [job_desc])[0]
        
        # Normalize scores
        cosine_norm = ms._normalize_scores([cosine_score])[0]
        bm25_norm = ms._normalize_scores([bm25_score])[0]
        
        # Calculate final hybrid score (70% cosine + 30% BM25)
        final_score = (0.7 * cosine_norm + 0.3 * bm25_norm) * 100

        # Get key terms from both documents
        resume_terms = set(user_resume_text.lower().split())
        job_terms = set(job_desc.lower().split())
        
        # Find matching terms
        matching_terms = resume_terms.intersection(job_terms)
        formatted_terms = []
        
        # Analyze each matching term
        for term in matching_terms:
            if len(term) < 2:
                continue
                
            # Get term context
            resume_snippet = _get_snippet(user_resume_text, term)
            job_snippet = _get_snippet(job_desc, term)
            
            # Count occurrences
            resume_count = user_resume_text.lower().count(term)
            job_count = job_desc.lower().count(term)
            
            formatted_terms.append({
                'term': term,
                'resume_context': resume_snippet,
                'job_context': job_snippet,
                'resume_count': resume_count,
                'job_count': job_count
            })

        # Calculate coverage metrics
        resume_token_count = len(resume_terms)
        matching_token_count = len(matching_terms)
        coverage = matching_token_count / max(1, resume_token_count)
        
        # Generate summary insights
        level = "Strong" if final_score > 75 else "Good" if final_score > 50 else "Moderate" if final_score > 25 else "Limited"
        insights = [
            f"{level} match with an overall score of {final_score:.1f}%",
            f"Found {matching_token_count} matching terms between your resume and the job description",
            f"Your resume covers {coverage*100:.1f}% of the key terms in the job posting",
            f"Semantic similarity score: {cosine_norm*100:.1f}%",
            f"Keyword matching score: {bm25_norm*100:.1f}%"
        ]

        return jsonify({
            'job_id': job.id,
            'job_role': job.role,
            'scores': {
                'overall': round(final_score, 1),
                'semantic_similarity': round(cosine_norm * 100, 1),
                'keyword_matching': round(bm25_norm * 100, 1)
            },
            'matching_terms': formatted_terms[:10],  # Top 10 matching terms
            'coverage': {
                'matching_terms': matching_token_count,
                'resume_terms': resume_token_count,
                'percentage': round(coverage * 100, 1)
            },
            'insights': insights,
            'recommendation': _generate_recommendation_reasoning(final_score/100, matching_token_count)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
