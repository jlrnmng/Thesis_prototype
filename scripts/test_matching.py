#!/usr/bin/env python3
"""Test ChromaDB matching functionality.

This script will:
1. Test job recommendations for each resume
2. Test candidate matching for each job
3. Verify scoring and ranking functionality
"""
import os
import sys
from pprint import pprint

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def format_score(score):
    """Format score as points (0-100 scale)"""
    return f"{score:.1f} pts"

def main():
    from app import create_app, db
    from matching_service import get_matching_service
    
    app = create_app()
    
    with app.app_context():
        from app.models import Application, Job, User
        
        # Get matching service with new ChromaDB path
        ms = get_matching_service(app.config.get('CHROMA_PATH', 'new_chroma_storage'))
        
        # Get all unique users who have applied
        users = User.query.join(Application).distinct().all()
        active_jobs = Job.query.filter_by(is_active=True).all()
        
        print("\nTesting Job Recommendations for Each Candidate:")
        print("=============================================")
        
        for user in users:
            # Get user's most recent application for their resume
            app = Application.query.filter_by(user_id=user.id).order_by(
                Application.submission_date.desc()
            ).first()
            
            if not app or not app.resume_text:
                continue
                
            print(f"\nCandidate: {user.full_name}")
            print(f"Background: {app.resume_text[:200]}...")
            
            # Get top 3 job matches
            matches = ms.get_top_jobs_for_resume(app.resume_text, active_jobs, top_n=3)
            print("\nTop Job Matches:")
            for job_id, score in matches:
                job = next(j for j in active_jobs if j.id == job_id)
                print(f"- {job.role}: {format_score(score)}")
        
        print("\n\nTesting Candidate Matching for Each Job:")
        print("======================================")
        
        for job in active_jobs:
            print(f"\nJob: {job.role}")
            print(f"Description: {job.description[:200]}...")
            
            # Get most recent application for each user
            # First get all user IDs who have applied
            user_ids = db.session.query(Application.user_id).distinct().all()
            user_ids = [uid[0] for uid in user_ids]
            
            # Then get the most recent application for each user
            applications = []
            for user_id in user_ids:
                latest_app = Application.query.filter(
                    Application.user_id == user_id,
                    Application.resume_text.isnot(None),
                    Application.resume_text != ''
                ).order_by(Application.submission_date.desc()).first()
                if latest_app:
                    applications.append(latest_app)
            
            # Rank candidates
            rankings = ms.rank_applicants_for_job(
                job_description=job.description,
                job_role=job.role,
                applications=applications
            )
            
            print("\nTop Candidates:")
            for app_id, score in rankings[:3]:  # Top 3 candidates
                app = next(a for a in applications if a.id == app_id)
                user = db.session.get(User, app.user_id)
                print(f"- {user.full_name}: {format_score(score)}")
        
        # Test specific matches we expect to be good
        print("\n\nTesting Specific Role Matches:")
        print("============================")
        
        test_cases = [
            ("Machine Learning Engineer (Junior)", "Carla Dizon"),
            ("Cybersecurity Analyst (Associate Level)", "Rafael Santiago"),
            ("Data Analyst (Junior Level)", "Angela Torres"),
            ("Front-End Web Developer (Entry-Level)", "Maria Elenor Cruz"),
            ("Junior Software engineer", "Juan B dela cruz")
        ]
        
        print("\nMatching service state:")
        for job in active_jobs:
            print(f"Job in active_jobs: {job.role}")
        
        for role, candidate in test_cases:
            print(f"\nLooking for role: {role}")
            # Use exact role name matching
            job = next((j for j in active_jobs if j.role == role), None)
            if not job:
                print(f"Warning: Could not find job with exact title: {role}")
                # Try case-insensitive match for debugging
                job = next((j for j in active_jobs if j.role.lower() == role.lower()), None)
                if job:
                    print(f"Found job with case-insensitive match: {job.role}")
            user = next((u for u in users if candidate.lower() in u.full_name.lower()), None)
            
            if not job or not user:
                continue
                
            app = Application.query.filter_by(user_id=user.id).first()
            if not app or not app.resume_text:
                continue
            
            # Use get_top_jobs_for_resume for consistent scoring
            matches = ms.get_top_jobs_for_resume(
                resume_text=app.resume_text,
                all_jobs=active_jobs,
                top_n=len(active_jobs)
            )
            
            # Find the score for our specific job
            score = next((score for job_id, score in matches if job_id == job.id), None)
            
            if score is not None:
                print(f"\nTesting {candidate} for {role}:")
                print(f"Match Score: {format_score(score)}")
                
                if score > 75:
                    print("✓ Strong match as expected")
                elif score > 50:
                    print("~ Moderate match")
                else:
                    print("⨯ Weaker match than expected")

if __name__ == '__main__':
    main()