from flask import Blueprint, request, jsonify
from app.models import db, Application, Job, User
from rank_bm25 import BM25Okapi
import numpy as np
import heapq
from app.utils.decorators import admin_required

shortlist_bp = Blueprint('shortlist', __name__)

def _get_snippet(text, term, radius=40):
    text_lower = text.lower()
    idx = text_lower.find(term)
    if idx == -1:
        return ''
    start = max(0, idx - radius)
    end = min(len(text), idx + len(term) + radius)
    return text[start:end].strip()

@shortlist_bp.route('/<int:job_id>', methods=['GET'])
@admin_required
def get_shortlist(job_id):
    try:
        # Get target job
        target_job = Job.query.get_or_404(job_id)

        # Get all applications in same cluster
        applications = Application.query.filter_by(cluster_id=target_job.cluster_id).all()

        if not applications:
            return jsonify({'message': 'No applications found for this job cluster'}), 404

        # Prepare corpus of resumes
        corpus = [app.resume_text or "" for app in applications]
        tokenized_corpus = [doc.lower().split() for doc in corpus]

        # Build BM25 index on resumes
        bm25 = BM25Okapi(tokenized_corpus)

        # Query = job description
        tokenized_query = (target_job.description or "").lower().split()

        # Score resumes against job description
        doc_scores = bm25.get_scores(tokenized_query)

        # Top 5 applications
        top_indices = np.argsort(doc_scores)[::-1][:5]
        top_applications = [applications[i] for i in top_indices]
        top_scores = [doc_scores[i] for i in top_indices]

        # Build response
        results = []
        for app, score in zip(top_applications, top_scores):
            user = User.query.get(app.user_id)
            results.append({
                'application_id': app.id,
                'user_id': app.user_id,
                'username': user.username,
                'email': user.email,
                'score': float(score),
                'resume_preview': app.resume_text[:200] + '...' if len(app.resume_text) > 200 else app.resume_text
            })

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@shortlist_bp.route('/explain/<int:application_id>', methods=['GET'])
@admin_required
def explain_shortlist(application_id):
    try:
        application = Application.query.get_or_404(application_id)
        job = Job.query.get_or_404(application.job_id)

        resume_text = application.resume_text or ""
        job_text = f"{job.role} {job.description}" or ""

        tokenized_resume = resume_text.lower().split()
        tokenized_job = job_text.lower().split()

        # BM25 index on resume
        bm25 = BM25Okapi([tokenized_resume])

        # Overall score
        overall_score = float(bm25.get_scores(tokenized_job)[0])

        # Per-term contributions
        term_scores = {}
        for term in set(tokenized_job):
            if len(term) < 2:
                continue
            try:
                score = float(bm25.get_scores([term])[0])
            except Exception:
                score = 0.0
            if score > 0 and term in " ".join(tokenized_resume):
                term_scores[term] = score

        # Top 10 contributing terms
        top_terms = heapq.nlargest(10, term_scores.items(), key=lambda x: x[1])
        formatted_terms = []
        for term, score in top_terms:
            job_count = tokenized_job.count(term)
            resume_count = tokenized_resume.count(term)
            snippet = _get_snippet(resume_text, term)
            formatted_terms.append({
                'term': term,
                'contribution': float(score),
                'job_count': job_count,
                'resume_count': resume_count,
                'resume_snippet': snippet
            })

        # Coverage: how much of the job description is represented in the resume
        matched_tokens = sum(1 for t in set(tokenized_job) if t in tokenized_resume)
        token_coverage = matched_tokens / max(1, len(set(tokenized_job)))

        return jsonify({
            'application_id': application_id,
            'job_id': job.id,
            'job_role': job.role,
            'overall_score': overall_score,
            'top_contributing_terms': formatted_terms,
            'token_coverage': round(token_coverage, 3),
            'explanation': (
                "Top job terms that made this resume rank highly are listed in "
                "'top_contributing_terms' with contribution scores, counts, and snippets from the resume."
            )
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
