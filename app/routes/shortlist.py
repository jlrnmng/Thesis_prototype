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
    """
    explanation_parts = []
    
    # Calculate component scores using raw values
    cosine_points = cosine_raw * 70
    bm25_points = bm25_raw * 30
    
    # Scoring methodology breakdown
    explanation_parts.append("**Match Analysis Summary**")
    explanation_parts.append("")
    
    # Score-based interpretation using the calculated final score
    calculated_final_score = cosine_points + bm25_points
    
    if calculated_final_score > 80:
        explanation_parts.append(f"**{candidate_name}** demonstrates **excellent alignment** with the {job_role} position.")
        explanation_parts.append(f"**Total Score: {calculated_final_score:.1f} points** - Strong compatibility across both semantic understanding and keyword matching.")
    elif calculated_final_score > 60:
        explanation_parts.append(f"**{candidate_name}** shows **good compatibility** with the {job_role} requirements.")
        explanation_parts.append(f"**Total Score: {calculated_final_score:.1f} points** - Solid relevant experience.")
    elif calculated_final_score > 40:
        explanation_parts.append(f"**{candidate_name}** presents **moderate alignment** with the {job_role} position.")
        explanation_parts.append(f"**Total Score: {calculated_final_score:.1f} points** - Some relevant qualifications worth exploring.")
    elif calculated_final_score > 0:
        explanation_parts.append(f"**{candidate_name}** shows **limited alignment** with the {job_role} requirements.")
        explanation_parts.append(f"**Total Score: {calculated_final_score:.1f} points** - Minimal overlap with job requirements.")
    else:
        explanation_parts.append(f"**{candidate_name}** shows **very limited alignment** with the {job_role} requirements.")
        explanation_parts.append(f"**Total Score: {calculated_final_score:.1f} points** - Significant gaps in required qualifications.")
    
    explanation_parts.append("")
    
    # Simple score breakdown
    explanation_parts.append("**Score Breakdown:**")
    explanation_parts.append(f"• **Semantic Match:** {cosine_points:.1f} points (content similarity)")
    explanation_parts.append(f"• **Keyword Match:** {bm25_points:.1f} points (specific terms)")
    explanation_parts.append("")
    
    # Coverage explanation
    coverage_percent = coverage * 100
    if coverage_percent > 60:
        explanation_parts.append(f"**Coverage:** {coverage_percent:.1f}% of job requirements (comprehensive match)")
    elif coverage_percent > 40:
        explanation_parts.append(f"**Coverage:** {coverage_percent:.1f}% of job requirements (moderate match)")
    else:
        explanation_parts.append(f"**Coverage:** {coverage_percent:.1f}% of job requirements (limited match)")
    
    # Top matching terms
    if top_terms and len(top_terms) > 0:
        top_term_names = [term['term'] for term in top_terms[:3]]
        explanation_parts.append(f"**Key matching areas:** {', '.join(top_term_names)}")
    
    return "\n".join(explanation_parts)

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

        # Get all applications
        applications = Application.query.filter(
            Application.resume_text.isnot(None),
            Application.resume_text != '',
            ~Application.resume_text.like('Resume for %')
        ).all()

        if not applications:
            return jsonify({'message': 'No applications found with resume text'}), 404

        # Use matching service for improved hybrid scoring
        from matching_service import get_matching_service
        ms = get_matching_service(current_app.config.get('CHROMA_PATH', 'chroma_storage'))
        
        # Score applications against job using hybrid scoring (70% cosine + 30% BM25)
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

        # Calculate hybrid scores (semantic + keyword matching)
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Initialize SentenceTransformer model
        try:
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except Exception:
            model = None
            
        # Calculate semantic similarity score (cosine similarity)
        semantic_score = 0.5  # Default fallback
        if model:
            try:
                job_embedding = model.encode([job_text])
                resume_embedding = model.encode([resume_text])
                semantic_score = float(cosine_similarity(job_embedding, resume_embedding)[0][0])
            except Exception as e:
                print(f"Error calculating semantic similarity: {e}")

        # BM25 index on resume corpus for keyword matching (same as matching service)
        tokenized_resume_corpus = [tokenized_resume]  # Create corpus with one resume
        bm25 = BM25Okapi(tokenized_resume_corpus)

        # Calculate keyword matching score (BM25) using job tokens as query
        bm25_raw_scores = bm25.get_scores(tokenized_job)
        bm25_raw_score = float(bm25_raw_scores[0]) if len(bm25_raw_scores) > 0 else 0
        
        # Normalize BM25 score to 0-1 range to prevent negative final scores
        def normalize_bm25_score(score):
            # Based on observed BM25 scores, typical range is around -20 to +15
            bm25_min, bm25_max = -20.0, 15.0
            normalized = (score - bm25_min) / (bm25_max - bm25_min)
            return max(0, min(1, normalized))
        
        bm25_normalized = normalize_bm25_score(bm25_raw_score)
        
        # Calculate final score using the NEW scoring methodology:
        # Final Score = (Cosine Similarity × 70) + (BM25 Score × 30)
        cosine_points = semantic_score * 70          # Cosine score (0-1) × 70 = 0-70 points
        bm25_points = bm25_normalized * 30           # Normalized BM25 (0-1) × 30 = 0-30 points
        final_match_score = cosine_points + bm25_points
        
        print(f"DEBUG: Cosine score: {semantic_score} -> {cosine_points:.1f} points")
        print(f"DEBUG: BM25 raw: {bm25_raw_score} -> normalized: {bm25_normalized:.3f} -> {bm25_points:.1f} points")
        print(f"DEBUG: Final match score: {final_match_score:.1f}")
        
        # Use the final match score as the overall score for compatibility
        overall_score = final_match_score

        # Per-term contributions (using original BM25 instance for term analysis)
        term_bm25 = BM25Okapi([tokenized_resume])  # BM25 for individual term scoring
        term_scores = {}
        for term in set(tokenized_job):
            if len(term) < 2:
                continue
            try:
                score = float(term_bm25.get_scores([term])[0])
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

        # Enhanced recommendation logic using the new scoring methodology
        if final_match_score > 80:
            recommendation_status = 'Highly Recommended'
            score_interpretation = 'Excellent match with strong semantic and keyword alignment'
        elif final_match_score > 65:
            recommendation_status = 'Recommended'
            score_interpretation = 'Good match with solid relevant experience'
        elif final_match_score > 50:
            recommendation_status = 'Consider'
            score_interpretation = 'Moderate match with some relevant qualifications'
        elif final_match_score > 35:
            recommendation_status = 'Review Required'
            score_interpretation = 'Limited match, requires detailed evaluation'
        else:
            recommendation_status = 'Low Match'
            score_interpretation = 'Minimal alignment with job requirements'

        # Calculate detailed score breakdown components using the new methodology
        score_breakdown = {
            'final_match_score': round(final_match_score, 1),
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

        # Generate detailed explanation
        detailed_explanation = _generate_detailed_explanation(
            final_match_score, semantic_score, bm25_normalized, semantic_score, bm25_normalized, token_coverage, len(formatted_terms), 
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
            'score_breakdown': score_breakdown,
            'matching_analysis': {
                'final_match_score': round(final_match_score, 1),
                'cosine_raw_score': round(semantic_score, 3),
                'bm25_raw_score': round(bm25_raw_score, 3),
                'cosine_points': round(cosine_points, 1),
                'bm25_points': round(bm25_points, 1),
                'key_matching_terms': formatted_terms,
                'token_coverage': round(token_coverage, 3),
                'detailed_explanation': detailed_explanation,
                'explanation': f"Candidate {user.full_name} achieved {round(final_match_score, 1)} points total score based on the new scoring methodology: (Cosine Similarity × 70) + (BM25 Score × 30)."
            },
            'recommendation': {
                'status': recommendation_status,
                'reasoning': _generate_recommendation_reasoning(final_match_score, len(formatted_terms))
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
