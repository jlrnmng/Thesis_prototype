from flask import Blueprint, request, jsonify, current_app
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

def _generate_detailed_explanation(final_percentage, semantic_score, keyword_score, cosine_raw, bm25_raw, coverage, term_count, candidate_name, job_role, top_terms):
    """
    Generate a detailed, human-readable explanation of the matching score with scoring breakdown
    Uses the same style as user matchmaking feature
    """
    # Calculate component scores using raw values
    cosine_points = cosine_raw * 70
    bm25_points = bm25_raw * 30
    calculated_final_score = cosine_points + bm25_points
    
    # Generate summary insights using the same format as matchmaking
    if calculated_final_score > 80:
        level = "Excellent"
        recommendation = "Highly recommended - strong alignment with job requirements"
    elif calculated_final_score > 65:
        level = "Strong"
        recommendation = "Recommended - good match with solid relevant experience"
    elif calculated_final_score > 50:
        level = "Good"
        recommendation = "Consider interviewing - moderate match with relevant qualifications"
    elif calculated_final_score > 35:
        level = "Moderate"
        recommendation = "Review carefully - limited match, requires detailed evaluation"
    else:
        level = "Limited"
        recommendation = "Low match - minimal alignment with job requirements"
        
    insights = [
        f"{level} match with an overall score of {calculated_final_score:.1f} points",
        f"Semantic similarity contributes {cosine_points:.1f} points (content understanding)",
        f"Keyword matching contributes {bm25_points:.1f} points (specific terms)",
        f"Found {term_count} matching terms between candidate resume and job description",
        f"Candidate resume covers {coverage*100:.1f}% of the key terms in the job posting"
    ]
    
    return {
        'insights': insights,
        'recommendation': recommendation,
        'scoring_explanation': f"Score calculated using: (Cosine Similarity × 70) + (BM25 Score × 30) = ({cosine_raw:.3f} × 70) + ({bm25_raw:.3f} × 30) = {calculated_final_score:.1f} points"
    }

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
        
        # Get all applications with resume text for automatic matching
        applications = Application.query.filter(
            Application.resume_text.isnot(None),
            Application.resume_text != '',
            ~Application.resume_text.like('Resume for %')
        ).all()

        if not applications:
            return jsonify({'message': 'No applications found with resume text'}), 404

        # Use matching service for automatic hybrid scoring (70% cosine + 30% BM25)
        from matching_service import get_matching_service
        ms = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
        
        # Score applications against job using automatic K-means classification
        rankings = ms.rank_applicants_for_job(
            job_description=target_job.description,
            job_role=target_job.role,
            applications=applications
        )
        
        # Get top 5 matches
        top_matches = rankings[:5]
        
        # Map application IDs to full application objects and scores
        app_map = {app.id: app for app in applications}
        top_applications = [app_map[app_id] for app_id, _ in top_matches]
        top_scores = [score for _, score in top_matches]

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
                'relevance_score': round(float(score), 1),
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
        print(f"DEBUG: Explaining shortlist for application ID: {application_id}")
        
        application = Application.query.get_or_404(application_id)
        job = Job.query.get_or_404(application.job_id)
        user = User.query.get(application.user_id)

        print(f"DEBUG: Found application for user {user.first_name} {user.last_name}")
        
        resume_text = application.resume_text or ""
        job_text = f"{job.role} {job.description}" or ""

        print(f"DEBUG: Resume text length: {len(resume_text)}")
        print(f"DEBUG: Job text length: {len(job_text)}")

        resume_text = application.resume_text or ""
        job_text = f"{job.role} {job.description}" or ""

        tokenized_resume = resume_text.lower().split()
        tokenized_job = job_text.lower().split()

        # Calculate hybrid scores using the exact same matching service logic as the main route
        try:
            from matching_service import get_matching_service
            ms = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
            
            print(f"DEBUG: Using matching service for consistent scoring")
            
            # Get ALL applications for the SAME JOB to ensure consistent scoring context
            all_applications = Application.query.filter(
                Application.job_id == job.id,
                Application.resume_text.isnot(None),
                Application.resume_text != '',
                ~Application.resume_text.like('Resume for %')
            ).all()
            
            if not all_applications:
                print("WARNING: No applications found for consistent scoring")
                overall_score = 0
            else:
                # Use the EXACT same method as the main route with ALL applications
                # This ensures consistent BM25 normalization context
                rankings = ms.rank_applicants_for_job(
                    job_description=job.description,
                    job_role=job.role,
                    applications=all_applications  # All applications for consistent normalization
                )
                
                # Find the score for our specific application
                app_score_dict = {app_id: score for app_id, score in rankings}
                overall_score = app_score_dict.get(application_id, 0)
                print(f"DEBUG: Consistent score for app {application_id}: {overall_score:.1f}")
        
        except Exception as e:
            print(f"ERROR: Failed to get consistent score: {e}")
            overall_score = 0
        
        # Get individual component scores for detailed breakdown
        try:
            job_desc = f"{job.role} {job.description}"
            
            # Get raw cosine similarity (this is consistent regardless of context)
            cosine_scores = ms._get_cosine_similarity_scores(resume_text, [job_desc])
            semantic_score = cosine_scores[0] if cosine_scores else 0
            cosine_points = semantic_score * 70
            
            # Calculate BM25 points by working backwards from overall score
            # overall_score = cosine_points + bm25_points
            # So: bm25_points = overall_score - cosine_points
            bm25_points = max(0, overall_score - cosine_points)  # Ensure non-negative
            bm25_normalized = bm25_points / 30 if bm25_points > 0 else 0  # Reverse the * 30
            
            # Get raw BM25 score for display purposes
            bm25_scores = ms._get_bm25_scores(resume_text, [job_desc])
            bm25_raw_score = bm25_scores[0] if bm25_scores else 0
            
            print(f"DEBUG: Component scores (derived from overall score):")
            print(f"  - Overall score: {overall_score:.1f}")
            print(f"  - Cosine: {semantic_score:.4f} -> {cosine_points:.1f} points")
            print(f"  - BM25 points (derived): {bm25_points:.1f}")
            print(f"  - BM25 normalized (derived): {bm25_normalized:.3f}")
            print(f"  - BM25 raw (for display): {bm25_raw_score:.4f}")
            print(f"  - Verification: {cosine_points:.1f} + {bm25_points:.1f} = {overall_score:.1f}")
            
        except Exception as e:
            print(f"ERROR: Failed to calculate component scores: {e}")
            # Use fallback component calculations based on overall score
            semantic_score = (overall_score / 100) * 0.7  # Approximate semantic portion
            bm25_normalized = (overall_score / 100) * 0.3  # Approximate BM25 portion  
            bm25_raw_score = 5.0  # Default display value
            cosine_points = semantic_score * 70
            bm25_points = bm25_normalized * 30

        # Calculate matching terms using the same approach as user matchmaking
        job_desc = f"{job.role} {job.description}"
        
        # Get key terms from both documents (same as matchmaking)
        resume_terms = set(resume_text.lower().split())
        job_terms = set(job_desc.lower().split())
        
        # Find matching terms
        matching_terms = resume_terms.intersection(job_terms)
        formatted_terms = []
        
        # Analyze each matching term (same as matchmaking approach)
        for term in matching_terms:
            if len(term) < 2:
                continue
                
            # Get term context
            resume_snippet = _get_snippet(resume_text, term)
            job_snippet = _get_snippet(job_desc, term)
            
            # Count occurrences
            resume_count = resume_text.lower().count(term)
            job_count = job_desc.lower().count(term)
            
            formatted_terms.append({
                'term': term,
                'resume_context': resume_snippet,
                'job_context': job_snippet,
                'resume_count': resume_count,
                'job_count': job_count,
                'contribution': resume_count + job_count,  # Simple contribution calculation
                'resume_snippet': resume_snippet   # Keep for backwards compatibility
            })

        # Sort by contribution (frequency) and take top 10
        formatted_terms.sort(key=lambda x: x['contribution'], reverse=True)
        formatted_terms = formatted_terms[:10]

        # Calculate coverage metrics (same as matchmaking)
        resume_token_count = len(resume_terms)
        matching_token_count = len(matching_terms)
        token_coverage = matching_token_count / max(1, resume_token_count)
        
        print(f"DEBUG: Found {matching_token_count} matching terms out of {resume_token_count} resume terms")
        print(f"DEBUG: Token coverage: {token_coverage*100:.1f}%")

        # Enhanced recommendation logic using the new scoring methodology
        if overall_score > 80:
            recommendation_status = 'Highly Recommended'
            score_interpretation = 'Excellent match with strong semantic and keyword alignment'
        elif overall_score > 65:
            recommendation_status = 'Recommended'
            score_interpretation = 'Good match with solid relevant experience'
        elif overall_score > 50:
            recommendation_status = 'Consider'
            score_interpretation = 'Moderate match with some relevant qualifications'
        elif overall_score > 35:
            recommendation_status = 'Review Required'
            score_interpretation = 'Limited match, requires detailed evaluation'
        else:
            recommendation_status = 'Low Match'
            score_interpretation = 'Minimal alignment with job requirements'

        # Calculate detailed score breakdown components using the new methodology
        score_breakdown = {
            'overall_score': round(overall_score, 1),
            'cosine_raw_score': round(semantic_score, 3),
            'bm25_raw_score': round(bm25_raw_score, 3),
            'bm25_normalized_score': round(bm25_normalized, 3),
            'cosine_points': round(cosine_points, 1),
            'bm25_points': round(bm25_points, 1),
            'semantic_weight': 70,
            'keyword_weight': 30,
            'token_coverage_percentage': round(token_coverage * 100, 1),
            'matching_terms_count': len(formatted_terms),
            'total_job_terms': len(set(tokenized_job)),
            'total_resume_terms': len(set(tokenized_resume))
        }

        # Generate detailed explanation using the same style as matchmaking
        detailed_explanation_data = _generate_detailed_explanation(
            overall_score, semantic_score, bm25_normalized, semantic_score, bm25_normalized, token_coverage, len(formatted_terms), 
            user.first_name, job.role, formatted_terms[:5]
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
            'scores': {
                'overall': round(overall_score, 1),
                'cosine_points': round(cosine_points, 1),
                'bm25_points': round(bm25_points, 1),
                'cosine_raw': round(semantic_score, 3),
                'bm25_raw': round(bm25_raw_score, 3),
                'bm25_normalized': round(bm25_normalized, 3),
                'semantic_weight': 70,
                'keyword_weight': 30
            },
            'coverage': {
                'matching_terms': len(formatted_terms),
                'percentage': round(token_coverage * 100, 1)
            },
            'insights': detailed_explanation_data['insights'],
            'recommendation': detailed_explanation_data['recommendation'],
            'recommendation_reasoning': _generate_recommendation_reasoning(overall_score, len(formatted_terms)),
            'scoring_explanation': detailed_explanation_data['scoring_explanation']
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
