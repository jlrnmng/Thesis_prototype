#!/usr/bin/env python3
"""
ChromaDB Synchronization Utility

This script ensures that ChromaDB is synchronized with the SQLite database.
It checks for missing documents and adds them to maintain consistency.

Usage:
    python scripts/sync_chroma_db.py [--dry-run] [--force-resync]
    
Options:
    --dry-run       : Show what would be done without making changes
    --force-resync  : Force complete resynchronization (slower but thorough)
"""
import os
import sys
import argparse
from datetime import datetime

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_chroma_sync():
    """Check synchronization status between SQLite and ChromaDB"""
    import chromadb
    from chromadb.config import Settings
    
    try:
        # Set environment variables to disable telemetry
        os.environ['CHROMA_DISABLE_TELEMETRY'] = '1'
        os.environ['ANONYMIZED_TELEMETRY'] = 'False'
        
        # Get ChromaDB path
        chroma_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'chroma_storage'
        ))
        
        # Initialize ChromaDB client
        try:
            client = chromadb.PersistentClient(path=chroma_path)
        except AttributeError:
            client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=chroma_path
            ))
        
        # Get ChromaDB data
        resumes_collection = client.get_collection("resumes")
        jobs_collection = client.get_collection("jobs")
        
        chroma_resumes = resumes_collection.get()
        chroma_jobs = jobs_collection.get()
        
        chroma_resume_users = set()
        chroma_job_ids = set()
        
        # Extract user IDs from resume collection
        for metadata in chroma_resumes.get('metadatas', []):
            if metadata and 'user_id' in metadata:
                chroma_resume_users.add(metadata['user_id'])
        
        # Extract job IDs from jobs collection
        for metadata in chroma_jobs.get('metadatas', []):
            if metadata and 'job_id' in metadata:
                chroma_job_ids.add(metadata['job_id'])
        
        return chroma_resume_users, chroma_job_ids, len(chroma_resumes.get('ids', [])), len(chroma_jobs.get('ids', []))
        
    except Exception as e:
        print(f"Error checking ChromaDB: {e}")
        return set(), set(), 0, 0

def check_sqlite_data():
    """Check what data exists in SQLite database"""
    from app import create_app, db
    from app.models import Application, Job
    
    try:
        app = create_app()
        with app.app_context():
            # Get applications with resume text
            applications = Application.query.filter(
                Application.resume_text.isnot(None),
                Application.resume_text != '',
                ~Application.resume_text.like('Resume for %')
            ).all()
            
            # Get active jobs
            jobs = Job.query.filter_by(is_active=True).all()
            
            sqlite_resume_users = {app.user_id for app in applications}
            sqlite_job_ids = {job.id for job in jobs}
            
            return sqlite_resume_users, sqlite_job_ids, len(applications), len(jobs)
            
    except Exception as e:
        print(f"Error checking SQLite: {e}")
        return set(), set(), 0, 0

def sync_missing_resumes(missing_users, dry_run=False):
    """Sync missing resumes to ChromaDB"""
    if not missing_users:
        return 0
    
    print(f"\n📝 Syncing {len(missing_users)} missing resumes...")
    
    if dry_run:
        print("DRY RUN - would sync the following users:")
        for user_id in sorted(missing_users):
            print(f"  - user_{user_id}")
        return len(missing_users)
    
    from app import create_app, db
    from app.models import Application
    from matching_service import get_matching_service
    
    try:
        app = create_app()
        with app.app_context():
            matching_service = get_matching_service()
            success = 0
            
            for user_id in missing_users:
                try:
                    # Get the most recent application for this user
                    app = Application.query.filter(
                        Application.user_id == user_id,
                        Application.resume_text.isnot(None),
                        Application.resume_text != '',
                        ~Application.resume_text.like('Resume for %')
                    ).order_by(Application.id.desc()).first()
                    
                    if app:
                        result, cluster = matching_service.add_resume_to_db(user_id, app.resume_text)
                        if result:
                            print(f"  ✅ Synced user_{user_id}")
                            success += 1
                        else:
                            print(f"  ❌ Failed to sync user_{user_id}")
                    else:
                        print(f"  ⚠️  No valid resume found for user_{user_id}")
                        
                except Exception as e:
                    print(f"  ❌ Error syncing user_{user_id}: {e}")
            
            return success
            
    except Exception as e:
        print(f"Error during resume sync: {e}")
        return 0

def sync_missing_jobs(missing_jobs, dry_run=False):
    """Sync missing jobs to ChromaDB"""
    if not missing_jobs:
        return 0
    
    print(f"\n💼 Syncing {len(missing_jobs)} missing jobs...")
    
    if dry_run:
        print("DRY RUN - would sync the following jobs:")
        for job_id in sorted(missing_jobs):
            print(f"  - job_{job_id}")
        return len(missing_jobs)
    
    from app import create_app, db
    from app.models import Job
    from matching_service import get_matching_service
    
    try:
        app = create_app()
        with app.app_context():
            matching_service = get_matching_service()
            success = 0
            
            for job_id in missing_jobs:
                try:
                    job = Job.query.filter_by(id=job_id, is_active=True).first()
                    
                    if job:
                        result = matching_service.add_job_to_db(job.id, job.description, job.role)
                        if result:
                            print(f"  ✅ Synced job_{job_id} ({job.role})")
                            success += 1
                        else:
                            print(f"  ❌ Failed to sync job_{job_id}")
                    else:
                        print(f"  ⚠️  Job {job_id} not found or inactive")
                        
                except Exception as e:
                    print(f"  ❌ Error syncing job_{job_id}: {e}")
            
            return success
            
    except Exception as e:
        print(f"Error during job sync: {e}")
        return 0

def main():
    """Main synchronization function"""
    parser = argparse.ArgumentParser(description=__doc__,
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dry-run', action='store_true',
                       help="Show what would be done without making changes")
    parser.add_argument('--force-resync', action='store_true',
                       help="Force complete resynchronization")
    args = parser.parse_args()
    
    print("ChromaDB Synchronization Utility")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    print()
    
    # Check current state
    print("📊 Checking current synchronization status...")
    
    # Get SQLite data
    sqlite_resume_users, sqlite_job_ids, sqlite_resume_count, sqlite_job_count = check_sqlite_data()
    print(f"SQLite Database:")
    print(f"  - Resumes: {sqlite_resume_count} (users: {len(sqlite_resume_users)})")
    print(f"  - Jobs: {sqlite_job_count}")
    
    # Get ChromaDB data
    chroma_resume_users, chroma_job_ids, chroma_resume_count, chroma_job_count = check_chroma_sync()
    print(f"ChromaDB:")
    print(f"  - Resumes: {chroma_resume_count} (users: {len(chroma_resume_users)})")
    print(f"  - Jobs: {chroma_job_count}")
    
    # Find missing items
    if args.force_resync:
        missing_resume_users = sqlite_resume_users
        missing_job_ids = sqlite_job_ids
        print(f"\n🔄 FORCE RESYNC MODE - will resync all data")
    else:
        missing_resume_users = sqlite_resume_users - chroma_resume_users
        missing_job_ids = sqlite_job_ids - chroma_job_ids
    
    # Report synchronization status
    print(f"\n📋 Synchronization Status:")
    print(f"  - Missing resumes: {len(missing_resume_users)}")
    print(f"  - Missing jobs: {len(missing_job_ids)}")
    
    if not missing_resume_users and not missing_job_ids and not args.force_resync:
        print("\n✅ Database is already synchronized!")
        return True
    
    # Perform synchronization
    total_synced = 0
    
    if missing_resume_users:
        synced_resumes = sync_missing_resumes(missing_resume_users, args.dry_run)
        total_synced += synced_resumes
    
    if missing_job_ids:
        synced_jobs = sync_missing_jobs(missing_job_ids, args.dry_run)
        total_synced += synced_jobs
    
    # Final status
    print(f"\n" + "=" * 40)
    if args.dry_run:
        print(f"DRY RUN COMPLETE")
        print(f"Would sync {total_synced} items")
    else:
        print(f"SYNCHRONIZATION COMPLETE")
        print(f"Successfully synced {total_synced} items")
        
        # Re-check status
        new_chroma_resume_users, new_chroma_job_ids, new_chroma_resume_count, new_chroma_job_count = check_chroma_sync()
        print(f"\nUpdated ChromaDB Status:")
        print(f"  - Resumes: {new_chroma_resume_count} (users: {len(new_chroma_resume_users)})")
        print(f"  - Jobs: {new_chroma_job_count}")
        
        remaining_missing_resumes = sqlite_resume_users - new_chroma_resume_users
        remaining_missing_jobs = sqlite_job_ids - new_chroma_job_ids
        
        if not remaining_missing_resumes and not remaining_missing_jobs:
            print("✅ Databases are now fully synchronized!")
        else:
            print(f"⚠️  Still missing: {len(remaining_missing_resumes)} resumes, {len(remaining_missing_jobs)} jobs")
    
    return True

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Synchronization cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during synchronization: {e}")
        import traceback
        traceback.print_exc()
        exit(1)