from flask import Blueprint, request, jsonify, session
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
        job_descriptions = [f"{job.role} {job.description}" for job in jobs]

        # Create BM25 index for jobs
        tokenized_corpus = [desc.lower().split() for desc in job_descriptions]
        bm25 = BM25Okapi(tokenized_corpus)

        # Tokenize resume
        tokenized_resume = user_resume_text.lower().split()

        # Get scores for all jobs
        doc_scores = bm25.get_scores(tokenized_resume)

        # Get top 3 job matches
        top_indices = np.argsort(doc_scores)[::-1][:3]
        top_jobs = [jobs[i] for i in top_indices]
        top_scores = [doc_scores[i] for i in top_indices]

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
        job_description = f"{job.role} {job.description}" or ""

        # Lowercase tokenization
        tokenized_job = job_description.lower().split()
        tokenized_resume = user_resume_text.lower().split()

        # Use BM25 on single job doc
        bm25 = BM25Okapi([tokenized_job])

        # Overall score of resume vs job
        overall_score = float(bm25.get_scores(tokenized_resume)[0])

        # Compute per-term contributions
        term_scores = {}
        for term in set(tokenized_resume):
            if len(term) < 2:
                continue
            try:
                score = float(bm25.get_scores([term])[0])
            except Exception:
                score = 0.0
            if score > 0 and term in " ".join(tokenized_job):
                term_scores[term] = score

        # Pick top 10 terms
        top_n = 10
        top_terms = heapq.nlargest(top_n, term_scores.items(), key=lambda x: x[1])
        formatted_terms = []
        for term, score in top_terms:
            resume_count = tokenized_resume.count(term)
            job_count = tokenized_job.count(term)
            snippet = _get_snippet(job_description, term)
            formatted_terms.append({
                'term': term,
                'contribution': float(score),
                'resume_count': resume_count,
                'job_count': job_count,
                'job_snippet': snippet
            })

        # Coverage: percent of unique resume tokens found in job doc
        matched_tokens = sum(1 for t in set(tokenized_resume) if t in tokenized_job)
        token_coverage = matched_tokens / max(1, len(set(tokenized_resume)))

        return jsonify({
            'job_id': job.id,
            'job_role': job.role,
            'overall_score': overall_score,
            'top_contributing_terms': formatted_terms,
            'token_coverage': round(token_coverage, 3),
            'explanation': (
                "Top terms from your resume that contribute most to the match are listed in "
                "'top_contributing_terms' with per-term contribution, counts, and a short job snippet "
                "showing context."
            )
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
