#!/usr/bin/env python3
"""
Automatic ChromaDB Synchronization Module

This module provides automatic synchronization between SQLite and ChromaDB
with retry mechanisms, error recovery, and background sync processes.
"""
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
import threading
import queue

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logger = logging.getLogger(__name__)

class ChromaSyncQueue:
    """Thread-safe queue for ChromaDB synchronization tasks"""
    
    def __init__(self):
        self.queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        
    def start_worker(self):
        """Start the background sync worker"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
            logger.info("ChromaDB sync worker started")
    
    def stop_worker(self):
        """Stop the background sync worker"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
            logger.info("ChromaDB sync worker stopped")
    
    def add_job_sync(self, job_id: int, job_description: str, job_role: str, priority: int = 1):
        """Add a job synchronization task to the queue"""
        task = {
            'type': 'job',
            'job_id': job_id,
            'job_description': job_description,
            'job_role': job_role,
            'priority': priority,
            'timestamp': datetime.now(),
            'retry_count': 0
        }
        self.queue.put(task)
        logger.debug(f"Added job sync task for job_id={job_id}")
    
    def add_resume_sync(self, user_id: int, resume_text: str, priority: int = 1):
        """Add a resume synchronization task to the queue"""
        task = {
            'type': 'resume',
            'user_id': user_id,
            'resume_text': resume_text,
            'priority': priority,
            'timestamp': datetime.now(),
            'retry_count': 0
        }
        self.queue.put(task)
        logger.debug(f"Added resume sync task for user_id={user_id}")
    
    def _worker(self):
        """Background worker that processes sync tasks"""
        from matching_service import get_matching_service
        
        while self.running:
            try:
                # Get task with timeout
                task = self.queue.get(timeout=1)
                
                # Process the task
                success = self._process_task(task)
                
                # If failed and retries available, re-queue with delay
                if not success and task['retry_count'] < 3:
                    task['retry_count'] += 1
                    # Exponential backoff: 1s, 2s, 4s
                    delay = 2 ** (task['retry_count'] - 1)
                    time.sleep(delay)
                    self.queue.put(task)
                    logger.warning(f"Re-queued {task['type']} sync task (retry {task['retry_count']}/3)")
                elif not success:
                    logger.error(f"Failed to sync {task['type']} after 3 retries: {task}")
                
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in sync worker: {e}")
    
    def _process_task(self, task: dict) -> bool:
        """Process a single synchronization task"""
        try:
            from matching_service import get_matching_service
            
            matching_service = get_matching_service()
            
            if task['type'] == 'job':
                success = matching_service.add_job_to_db(
                    task['job_id'], 
                    task['job_description'], 
                    task['job_role']
                )
                if success:
                    logger.info(f"Successfully synced job {task['job_id']} to ChromaDB")
                return success
                
            elif task['type'] == 'resume':
                success, cluster = matching_service.add_resume_to_db(
                    task['user_id'], 
                    task['resume_text']
                )
                if success:
                    logger.info(f"Successfully synced resume for user {task['user_id']} to ChromaDB")
                return success
                
            return False
            
        except Exception as e:
            logger.error(f"Error processing sync task: {e}")
            return False

# Global sync queue instance
_sync_queue = None

def get_sync_queue() -> ChromaSyncQueue:
    """Get the global sync queue instance"""
    global _sync_queue
    if _sync_queue is None:
        _sync_queue = ChromaSyncQueue()
        _sync_queue.start_worker()
    return _sync_queue

class ChromaDBSyncManager:
    """Manager for automatic ChromaDB synchronization"""
    
    def __init__(self):
        self.sync_queue = get_sync_queue()
        
    def sync_job_immediately(self, job_id: int, job_description: str, job_role: str, 
                           max_retries: int = 3) -> bool:
        """
        Immediately synchronize a job to ChromaDB with retries
        
        Returns:
            bool: True if successful, False if failed after all retries
        """
        from matching_service import get_matching_service
        
        for attempt in range(max_retries):
            try:
                matching_service = get_matching_service()
                success = matching_service.add_job_to_db(job_id, job_description, job_role)
                
                if success:
                    logger.info(f"Job {job_id} successfully synced to ChromaDB (attempt {attempt + 1})")
                    return True
                else:
                    logger.warning(f"Job {job_id} sync failed (attempt {attempt + 1})")
                    
            except Exception as e:
                logger.error(f"Error syncing job {job_id} (attempt {attempt + 1}): {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        # If immediate sync failed, add to background queue
        logger.warning(f"Immediate sync failed for job {job_id}, adding to background queue")
        self.sync_queue.add_job_sync(job_id, job_description, job_role, priority=2)
        return False
    
    def sync_resume_immediately(self, user_id: int, resume_text: str, 
                              max_retries: int = 3) -> bool:
        """
        Immediately synchronize a resume to ChromaDB with retries
        
        Returns:
            bool: True if successful, False if failed after all retries
        """
        from matching_service import get_matching_service
        
        for attempt in range(max_retries):
            try:
                matching_service = get_matching_service()
                success, cluster = matching_service.add_resume_to_db(user_id, resume_text)
                
                if success:
                    logger.info(f"Resume for user {user_id} successfully synced to ChromaDB (attempt {attempt + 1})")
                    return True
                else:
                    logger.warning(f"Resume sync failed for user {user_id} (attempt {attempt + 1})")
                    
            except Exception as e:
                logger.error(f"Error syncing resume for user {user_id} (attempt {attempt + 1}): {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        
        # If immediate sync failed, add to background queue
        logger.warning(f"Immediate sync failed for user {user_id}, adding to background queue")
        self.sync_queue.add_resume_sync(user_id, resume_text, priority=2)
        return False
    
    def check_and_repair_sync(self) -> Tuple[int, int]:
        """
        Check for synchronization issues and repair them automatically
        
        Returns:
            Tuple[int, int]: (missing_jobs_count, missing_resumes_count)
        """
        try:
            from scripts.sync_chroma_db import check_chroma_sync, check_sqlite_data
            
            # Get current sync status
            sqlite_resume_users, sqlite_job_ids, _, _ = check_sqlite_data()
            chroma_resume_users, chroma_job_ids, _, _ = check_chroma_sync()
            
            # Find missing items
            missing_resume_users = sqlite_resume_users - chroma_resume_users
            missing_job_ids = sqlite_job_ids - chroma_job_ids
            
            # Queue missing items for sync
            if missing_job_ids:
                from app import create_app, db
                from app.models import Job
                
                app = create_app()
                with app.app_context():
                    for job_id in missing_job_ids:
                        job = Job.query.filter_by(id=job_id, is_active=True).first()
                        if job:
                            self.sync_queue.add_job_sync(job.id, job.description, job.role, priority=3)
            
            if missing_resume_users:
                from app import create_app, db
                from app.models import Application
                
                app = create_app()
                with app.app_context():
                    for user_id in missing_resume_users:
                        app = Application.query.filter(
                            Application.user_id == user_id,
                            Application.resume_text.isnot(None),
                            Application.resume_text != '',
                            ~Application.resume_text.like('Resume for %')
                        ).order_by(Application.id.desc()).first()
                        
                        if app:
                            self.sync_queue.add_resume_sync(user_id, app.resume_text, priority=3)
            
            if missing_job_ids or missing_resume_users:
                logger.info(f"Queued {len(missing_job_ids)} jobs and {len(missing_resume_users)} resumes for automatic sync")
            
            return len(missing_job_ids), len(missing_resume_users)
            
        except Exception as e:
            logger.error(f"Error during sync check and repair: {e}")
            return 0, 0

# Global sync manager instance
_sync_manager = None

def get_sync_manager() -> ChromaDBSyncManager:
    """Get the global sync manager instance"""
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = ChromaDBSyncManager()
    return _sync_manager

def ensure_job_synced(job_id: int, job_description: str, job_role: str) -> bool:
    """
    Ensure a job is synchronized to ChromaDB with automatic retries
    
    This function should be called after successfully creating a job in SQLite.
    It will attempt immediate synchronization and fall back to background sync if needed.
    
    Args:
        job_id: The job ID
        job_description: The job description
        job_role: The job role/title
        
    Returns:
        bool: True if immediately synced, False if queued for background sync
    """
    sync_manager = get_sync_manager()
    return sync_manager.sync_job_immediately(job_id, job_description, job_role)

def ensure_resume_synced(user_id: int, resume_text: str) -> bool:
    """
    Ensure a resume is synchronized to ChromaDB with automatic retries
    
    This function should be called after successfully creating a resume/application in SQLite.
    It will attempt immediate synchronization and fall back to background sync if needed.
    
    Args:
        user_id: The user ID
        resume_text: The resume text content
        
    Returns:
        bool: True if immediately synced, False if queued for background sync
    """
    sync_manager = get_sync_manager()
    return sync_manager.sync_resume_immediately(user_id, resume_text)

def schedule_sync_check():
    """
    Schedule a periodic sync check (to be called periodically by the application)
    """
    sync_manager = get_sync_manager()
    missing_jobs, missing_resumes = sync_manager.check_and_repair_sync()
    
    if missing_jobs > 0 or missing_resumes > 0:
        logger.warning(f"Found and queued {missing_jobs} missing jobs and {missing_resumes} missing resumes for sync")
    else:
        logger.debug("Sync check completed - no missing items found")

def cleanup_sync_resources():
    """Clean up sync resources (call on application shutdown)"""
    global _sync_queue
    if _sync_queue:
        _sync_queue.stop_worker()
        _sync_queue = None