#!/usr/bin/env python3
"""Import resumes and jobs into ChromaDB.

This script will import all resume texts and job descriptions into
the newly initialized ChromaDB collections.
"""
import os
import sys

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    from app import create_app, db
    import chromadb
    from chromadb.utils import embedding_functions
    
    app = create_app()
    
    with app.app_context():
        from app.models import Application, Job, User
        
        # Initialize ChromaDB client
        chroma_path = app.config.get('CHROMA_PATH', 'new_chroma_storage')
        client = chromadb.Client(chromadb.config.Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=chroma_path
        ))
        
        # Set up embedding function
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get collections
        resumes = client.get_or_create_collection("resumes", embedding_function=embedding_fn)
        jobs = client.get_or_create_collection("jobs", embedding_function=embedding_fn)
        
        # Import resumes
        applications = Application.query.filter(
            Application.resume_text.isnot(None),
            Application.resume_text != '',
            ~Application.resume_text.like('Resume for %')
        ).all()
        
        print(f"\nProcessing {len(applications)} resumes:")
        resume_success = 0
        for app in applications:
            try:
                resumes.add(
                    documents=[app.resume_text],
                    ids=[f"user_{app.user_id}"],
                    metadatas=[{"user_id": app.user_id}]
                )
                resume_success += 1
                print(f"Added resume for user {app.user_id}")
            except Exception as e:
                print(f"Error adding resume for user {app.user_id}: {e}")
        
        # Import jobs
        active_jobs = Job.query.filter_by(is_active=True).all()
        
        print(f"\nProcessing {len(active_jobs)} jobs:")
        job_success = 0
        for job in active_jobs:
            try:
                full_text = f"{job.role} {job.description}"
                jobs.add(
                    documents=[full_text],
                    ids=[f"job_{job.id}"],
                    metadatas=[{"job_id": job.id, "role": job.role}]
                )
                job_success += 1
                print(f"Added job {job.id}: {job.role}")
            except Exception as e:
                print(f"Error adding job {job.id}: {e}")
        
        print(f"\nSummary:")
        print(f"Resumes processed: {len(applications)}")
        print(f"Resumes added successfully: {resume_success}")
        print(f"Jobs processed: {len(active_jobs)}")
        print(f"Jobs added successfully: {job_success}")

if __name__ == '__main__':
    main()