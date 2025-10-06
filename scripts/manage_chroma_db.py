#!/usr/bin/env python3
"""Direct ChromaDB SQLite management tool.

Usage:
  python tools/manage_chroma_db.py [--restore-backup] [--list-backups] [--list-collections]

This tool provides direct management of the ChromaDB SQLite database,
bypassing the ChromaDB Python API to avoid telemetry issues.
"""
import os
import sys
import argparse
import sqlite3
import shutil
from datetime import datetime
import json

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def connect_db(db_path):
    """Connect to ChromaDB sqlite database"""
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_tables(conn):
    """Create ChromaDB tables if they don't exist"""
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id TEXT PRIMARY KEY,
            embedding BLOB,
            document TEXT,
            metadata TEXT
        )
        """)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        return False

def import_jobs(conn, db_path, dry_run=False):
    """Import jobs into ChromaDB from Job records"""
    from app import create_app, db
    app = create_app()

    with app.app_context():
        from app.models import Job
        
        # Get all active jobs
        jobs = Job.query.filter_by(is_active=True).all()

        print(f'Found {len(jobs)} active jobs')
        
        if dry_run:
            print("Dry run - no changes will be made")
            return

        success = 0
        for job in jobs:
            try:
                # Store job in ChromaDB
                doc_id = f"job_{job.id}"
                metadata = {
                    "job_id": job.id,
                    "role": job.role
                }
                
                full_text = f"{job.role} {job.description}"
                
                conn.execute(
                    "INSERT OR REPLACE INTO embeddings (id, document, metadata) VALUES (?, ?, ?)",
                    (doc_id, full_text, json.dumps(metadata))
                )
                success += 1
                print(f"Added job {job.id}: {job.role}")
            except Exception as e:
                print(f"Error adding job {job.id}: {e}")
        
        conn.commit()
        print(f"\nSummary:")
        print(f"Total jobs processed: {len(jobs)}")
        print(f"Successfully added to ChromaDB: {success}")
        print(f"Failed to add: {len(jobs) - success}")

def import_resumes(conn, db_path, dry_run=False):
    """Import resumes into ChromaDB from Application records"""
    from app import create_app, db
    app = create_app()

    with app.app_context():
        from app.models import Application
        
        # Get all applications with non-empty resume text
        apps = Application.query.filter(
            Application.resume_text.isnot(None),
            Application.resume_text != '',
            ~Application.resume_text.like('Resume for %')  # Exclude placeholders
        ).all()

        print(f'Found {len(apps)} applications with resume text')
        
        if dry_run:
            print("Dry run - no changes will be made")
            return

        success = 0
        for app in apps:
            try:
                # Store resume in ChromaDB
                doc_id = f"user_{app.user_id}"
                metadata = {"user_id": app.user_id}
                
                conn.execute(
                    "INSERT OR REPLACE INTO embeddings (id, document, metadata) VALUES (?, ?, ?)",
                    (doc_id, app.resume_text, json.dumps(metadata))
                )
                success += 1
                print(f"Added resume for application {app.id}")
            except Exception as e:
                print(f"Error adding resume for application {app.id}: {e}")
        
        conn.commit()
        print(f"\nSummary:")
        print(f"Total applications processed: {len(apps)}")
        print(f"Successfully added to ChromaDB: {success}")
        print(f"Failed to add: {len(apps) - success}")

def verify_data(conn):
    """Verify resume and job data in ChromaDB"""
    print("\nVerifying ChromaDB contents:")
    print("----------------------------")
    
    # Check resumes
    cursor = conn.execute("SELECT id, document, metadata FROM embeddings WHERE id LIKE 'user_%'")
    resumes = cursor.fetchall()
    print(f"\nFound {len(resumes)} resumes in ChromaDB:")
    for i, (doc_id, document, metadata) in enumerate(resumes[:5], 1):
        meta = json.loads(metadata) if metadata else {}
        preview = document[:100] + "..." if document else "No content"
        print(f"{i}. ID: {doc_id}")
        print(f"   User ID: {meta.get('user_id', 'unknown')}")
        print(f"   Preview: {preview}")
    if len(resumes) > 5:
        print(f"...and {len(resumes) - 5} more resumes")
    
    # Check jobs
    cursor = conn.execute("SELECT id, document, metadata FROM embeddings WHERE id LIKE 'job_%'")
    jobs = cursor.fetchall()
    print(f"\nFound {len(jobs)} jobs in ChromaDB:")
    for i, (doc_id, document, metadata) in enumerate(jobs[:5], 1):
        meta = json.loads(metadata) if metadata else {}
        preview = document[:100] + "..." if document else "No content"
        print(f"{i}. ID: {doc_id}")
        print(f"   Job ID: {meta.get('job_id', 'unknown')}")
        print(f"   Role: {meta.get('role', 'unknown')}")
        print(f"   Preview: {preview}")
    if len(jobs) > 5:
        print(f"...and {len(jobs) - 5} more jobs")

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dry-run', action='store_true',
                       help="Don't save changes, just show what would be done")
    parser.add_argument('--verify', action='store_true',
                       help="Verify the contents of ChromaDB")
    args = parser.parse_args()

    from app import create_app
    app = create_app()
    
    chroma_path = app.config.get('CHROMA_PATH', 'chroma_storage')
    db_path = os.path.join(chroma_path, 'chroma.sqlite3')
    
    print(f"ChromaDB SQLite path: {db_path}")
    
    # Create chroma_storage directory if it doesn't exist
    os.makedirs(chroma_path, exist_ok=True)
    
    # Connect to or create database
    conn = connect_db(db_path)
    if not conn:
        return
    
    # Create tables if needed
    if not create_tables(conn):
        return
        
    if args.verify:
        verify_data(conn)
    elif not args.dry_run:
        # Import resumes
        import_resumes(conn, db_path, args.dry_run)
        print("\n")
        # Import jobs
        import_jobs(conn, db_path, args.dry_run)
    
    conn.close()

if __name__ == '__main__':
    main()