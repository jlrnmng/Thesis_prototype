#!/usr/bin/env python3
"""
Test the automatic ChromaDB synchronization system

This script tests the new automatic synchronization features to ensure
jobs and resumes are properly synchronized between SQLite and ChromaDB.
"""
import os
import sys
import time

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_job_sync():
    """Test automatic job synchronization"""
    print("Testing automatic job synchronization...")
    
    from app import create_app, db
    from app.models import Job
    from app.utils.chroma_sync import ensure_job_synced
    
    app = create_app()
    
    with app.app_context():
        # Create a test job
        test_job = Job(
            role="Test Automatic Sync Job",
            description="This is a test job to verify automatic synchronization works correctly.",
            is_active=True,
            created_by=1  # Assuming admin user with ID 1 exists
        )
        
        try:
            # Add to SQLite
            db.session.add(test_job)
            db.session.commit()
            print(f"✅ Test job {test_job.id} created in SQLite")
            
            # Test automatic sync
            sync_success = ensure_job_synced(
                test_job.id, 
                test_job.description, 
                test_job.role
            )
            
            if sync_success:
                print(f"✅ Test job {test_job.id} successfully synced to ChromaDB")
            else:
                print(f"⚠️  Test job {test_job.id} queued for background sync")
            
            # Verify it's in ChromaDB
            time.sleep(2)  # Give background sync time to work
            
            from scripts.sync_chroma_db import check_chroma_sync
            chroma_resume_users, chroma_job_ids, _, _ = check_chroma_sync()
            
            if test_job.id in chroma_job_ids:
                print(f"✅ Test job {test_job.id} found in ChromaDB")
            else:
                print(f"❌ Test job {test_job.id} NOT found in ChromaDB")
            
            # Clean up
            db.session.delete(test_job)
            db.session.commit()
            print(f"🧹 Test job {test_job.id} cleaned up from SQLite")
            
        except Exception as e:
            print(f"❌ Error during job sync test: {e}")
            db.session.rollback()

def test_sync_queue():
    """Test the background sync queue"""
    print("\nTesting background sync queue...")
    
    try:
        from app.utils.chroma_sync import get_sync_queue
        
        sync_queue = get_sync_queue()
        
        # Add a test job to the queue
        sync_queue.add_job_sync(
            job_id=999,  # Non-existent ID for testing
            job_description="Test queue job description",
            job_role="Test Queue Job",
            priority=1
        )
        
        print("✅ Test job added to sync queue")
        
        # Wait a moment for processing
        time.sleep(3)
        
        print("✅ Background sync queue test completed")
        
    except Exception as e:
        print(f"❌ Error during sync queue test: {e}")

def test_sync_check():
    """Test the automatic sync check functionality"""
    print("\nTesting automatic sync check...")
    
    try:
        from app.utils.chroma_sync import get_sync_manager
        
        sync_manager = get_sync_manager()
        missing_jobs, missing_resumes = sync_manager.check_and_repair_sync()
        
        print(f"✅ Sync check completed")
        print(f"   Missing jobs detected and queued: {missing_jobs}")
        print(f"   Missing resumes detected and queued: {missing_resumes}")
        
    except Exception as e:
        print(f"❌ Error during sync check test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("Automatic ChromaDB Synchronization Test Suite")
    print("=" * 50)
    
    try:
        test_job_sync()
        test_sync_queue()
        test_sync_check()
        
        print("\n" + "=" * 50)
        print("✅ All synchronization tests completed!")
        print("\nThe automatic sync system should now:")
        print("  1. Immediately sync new jobs/resumes to ChromaDB")
        print("  2. Retry failed syncs with exponential backoff")
        print("  3. Queue items for background sync if immediate sync fails")
        print("  4. Periodically check and repair sync issues")
        print("  5. No longer require manual import script execution")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()