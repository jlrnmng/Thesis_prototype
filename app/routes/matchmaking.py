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

def _generate_recommendation_reasoning(score, term_count):
    """
    Generate recommendation reasoning based on score and matching terms
    (Same function as used in shortlisting for consistency)
    """
    if score > 80:
        return f"Excellent match with high relevance score ({score:.1f}) and {term_count} matching key terms. Highly recommended for application."
    elif score > 65:
        return f"Strong candidate match with good relevance score ({score:.1f}) and {term_count} relevant qualifications. Recommended for application."
    elif score > 50:
        return f"Good match with moderate relevance score ({score:.1f}) and {term_count} matching terms. Consider applying."
    elif score > 35:
        return f"Moderate match with some relevant experience (score: {score:.1f}). Review job requirements carefully before applying."
    else:
        return f"Limited match with position requirements (score: {score:.1f}). Consider improving resume alignment or exploring other opportunities."

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
        print(f"DEBUG: Explaining matchmaking for job_id: {job_id}")
        user_id = session['user_id']
        print(f"DEBUG: User ID: {user_id}")

        # Get user's most recent application
        latest_application = Application.query.filter_by(
            user_id=user_id
        ).order_by(Application.submission_date.desc()).first()

        if not latest_application:
            print(f"DEBUG: No applications found for user {user_id}")
            return jsonify({'error': 'No applications found for this user'}), 404

        user_resume_text = latest_application.resume_text or ""
        print(f"DEBUG: Resume text length: {len(user_resume_text)}")

        # Get the job
        job = Job.query.get_or_404(job_id)
        print(f"DEBUG: Found job: {job.role}")
        
        # Use matching service for improved hybrid scoring
        from matching_service import get_matching_service
        ms = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
        
        # Get similarity scores using both cosine and BM25 (same as shortlisting)
        job_desc = f"{job.role} {job.description}"
        cosine_scores = ms._get_cosine_similarity_scores(user_resume_text, [job_desc])
        bm25_scores = ms._get_bm25_scores(user_resume_text, [job_desc])
        
        # Get raw scores
        cosine_score = cosine_scores[0]  # Already 0-1 range
        bm25_raw_score = bm25_scores[0]
        
        # Normalize BM25 score to 0-1 range (same as shortlisting)
        bm25_normalized = ms._normalize_scores([bm25_raw_score])[0]
        
        # Calculate final hybrid score using EXACT same formula as shortlisting:
        # Final Score = (Cosine Similarity × 70) + (BM25 Score × 30)
        cosine_points = cosine_score * 70
        bm25_points = bm25_normalized * 30
        final_score = cosine_points + bm25_points

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
        
        # Generate summary insights using the same scoring as shortlisting
        if final_score > 80:
            level = "Excellent"
            recommendation = "Highly recommended - strong alignment with job requirements"
        elif final_score > 65:
            level = "Strong"
            recommendation = "Recommended - good match with solid relevant experience"
        elif final_score > 50:
            level = "Good"
            recommendation = "Consider applying - moderate match with relevant qualifications"
        elif final_score > 35:
            level = "Moderate"
            recommendation = "Review carefully - limited match, requires detailed evaluation"
        else:
            level = "Limited"
            recommendation = "Low match - minimal alignment with job requirements"
            
        insights = [
            f"{level} match with an overall score of {final_score:.1f} points",
            f"Semantic similarity contributes {cosine_points:.1f} points (content understanding)",
            f"Keyword matching contributes {bm25_points:.1f} points (specific terms)",
            f"Found {matching_token_count} matching terms between your resume and the job description",
            f"Your resume covers {coverage*100:.1f}% of the key terms in the job posting"
        ]

        return jsonify({
            'job_id': job.id,
            'job_role': job.role,
            'scores': {
                'overall': round(final_score, 1),
                'cosine_points': round(cosine_points, 1),
                'bm25_points': round(bm25_points, 1),
                'cosine_raw': round(cosine_score, 3),
                'bm25_raw': round(bm25_raw_score, 3),
                'bm25_normalized': round(bm25_normalized, 3),
                'semantic_weight': 70,
                'keyword_weight': 30
            },
            'matching_terms': formatted_terms[:10],  # Top 10 matching terms
            'coverage': {
                'matching_terms': matching_token_count,
                'resume_terms': resume_token_count,
                'percentage': round(coverage * 100, 1)
            },
            'insights': insights,
            'recommendation': recommendation,
            'recommendation_reasoning': _generate_recommendation_reasoning(final_score, matching_token_count),
            'scoring_explanation': f"Score calculated using: (Cosine Similarity × 70) + (BM25 Score × 30) = ({cosine_score:.3f} × 70) + ({bm25_normalized:.3f} × 30) = {final_score:.1f} points"
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
