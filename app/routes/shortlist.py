from flask import Blueprint, request, jsonify
from app.models import db, Application, Job, User
from rank_bm25 import BM25Okapi
import numpy as np
import heapq
from datetime import datetime
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

def _generate_recommendation_reasoning(score, term_count):
    """
    Generate recommendation reasoning based on score and matching terms
    """
    if score > 1.5:
        return f"Strong candidate with high relevance score ({score}) and {term_count} matching key terms. Recommended for interview."
    elif score > 0.8:
        return f"Good candidate match with moderate relevance score ({score}) and {term_count} relevant qualifications. Consider for interview."
    elif score > 0.3:
        return f"Potential candidate with some relevant experience (score: {score}). May require further evaluation."
    else:
        return f"Limited match with position requirements (score: {score}). Consider only if candidate pool is limited."

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
        for rank, (app, score) in enumerate(zip(top_applications, top_scores), 1):
            user = User.query.get(app.user_id)

            candidate_info = {
                'rank': rank,
                'application_id': app.id,
                'candidate_id': app.user_id,
                'candidate_name': {
                    'first_name': user.first_name,
                    'middle_name': user.middle_name or '',
                    'last_name': user.last_name,
                    'full_name': user.full_name
                },
                'contact_email': user.email,
                'relevance_score': round(float(score), 3),
                'application_date': app.submission_date.strftime('%Y-%m-%d %H:%M'),
                'resume_summary': app.resume_text[:300] + '...' if len(app.resume_text) > 300 else app.resume_text,
                'cluster_category': app.cluster_id
            }
            results.append(candidate_info)

        response = {
            'job_details': {
                'job_id': target_job.id,
                'position': target_job.role,
                'job_description': target_job.description,
                'cluster_id': target_job.cluster_id
            },
            'shortlist_summary': {
                'total_candidates_reviewed': len(applications),
                'top_candidates_selected': len(results),
                'selection_method': 'BM25 relevance scoring',
                'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            },
            'candidates': results
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@shortlist_bp.route('/explain/<int:application_id>', methods=['GET'])
@admin_required
def explain_shortlist(application_id):
    try:
        application = Application.query.get_or_404(application_id)
        job = Job.query.get_or_404(application.job_id)
        user = User.query.get(application.user_id)

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

        recommendation_status = (
            'Recommended' if overall_score > 1.0
            else 'Consider' if overall_score > 0.5
            else 'Low Match'
        )

        response = {
            'candidate_details': {
                'application_id': application_id,
                'candidate_name': user.full_name,
                'candidate_email': user.email,
                'application_date': application.submission_date.strftime('%Y-%m-%d %H:%M')
            },
            'job_details': {
                'job_id': job.id,
                'position': job.role,
                'department_cluster': job.cluster_id
            },
            'matching_analysis': {
                'relevance_score': round(overall_score, 3),
                'key_matching_terms': formatted_terms,
                'token_coverage': round(token_coverage, 3),
                'explanation': f"Candidate {user.full_name} scored {round(overall_score, 3)} based on resume containing relevant terms. Top contributing terms and context snippets are provided for review."
            },
            'recommendation': {
                'status': recommendation_status,
                'reasoning': _generate_recommendation_reasoning(overall_score, len(formatted_terms))
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
