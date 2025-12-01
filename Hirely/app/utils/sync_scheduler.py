#!/usr/bin/env python3
"""
Periodic ChromaDB Synchronization Scheduler

This module provides background scheduling for periodic ChromaDB synchronization checks.
It can be integrated into the main application to automatically detect and fix sync issues.
"""
import os
import sys
import time
import threading
import logging
from datetime import datetime, timedelta

# Add Hirely package to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

logger = logging.getLogger(__name__)

class SyncScheduler:
    """Scheduler for periodic ChromaDB synchronization checks"""
    
    def __init__(self, check_interval_minutes: int = 30):
        """
        Initialize the sync scheduler
        
        Args:
            check_interval_minutes: How often to run sync checks (default: 30 minutes)
        """
        self.check_interval = timedelta(minutes=check_interval_minutes)
        self.last_check = None
        self.scheduler_thread = None
        self.running = False
        
    def start(self):
        """Start the periodic sync scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
            self.scheduler_thread.start()
            logger.info(f"ChromaDB sync scheduler started (interval: {self.check_interval})")
    
    def stop(self):
        """Stop the periodic sync scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            logger.info("ChromaDB sync scheduler stopped")
    
    def _scheduler_worker(self):
        """Background worker that runs periodic sync checks"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check if it's time for a sync check
                if (self.last_check is None or 
                    current_time - self.last_check >= self.check_interval):
                    
                    self._run_sync_check()
                    self.last_check = current_time
                
                # Sleep for 1 minute before checking again
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in sync scheduler: {e}")
                time.sleep(60)  # Wait before retrying
    
    def _run_sync_check(self):
        """Run a synchronization check"""
        try:
            from app.utils.chroma_sync import schedule_sync_check
            schedule_sync_check()
            logger.debug("Periodic sync check completed")
        except Exception as e:
            logger.error(f"Error during periodic sync check: {e}")
    
    def force_check(self):
        """Force an immediate sync check"""
        logger.info("Forcing immediate sync check")
        self._run_sync_check()

# Global scheduler instance
_scheduler = None

def get_scheduler() -> SyncScheduler:
    """Get the global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = SyncScheduler()
    return _scheduler

def start_sync_scheduler(check_interval_minutes: int = 30):
    """Start the global sync scheduler"""
    scheduler = get_scheduler()
    scheduler.check_interval = timedelta(minutes=check_interval_minutes)
    scheduler.start()

def stop_sync_scheduler():
    """Stop the global sync scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None

def force_sync_check():
    """Force an immediate sync check"""
    scheduler = get_scheduler()
    scheduler.force_check()

if __name__ == '__main__':
    # Test the scheduler
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    print("Starting sync scheduler test...")
    start_sync_scheduler(check_interval_minutes=1)  # Check every minute for testing
    
    try:
        # Run for 5 minutes
        time.sleep(300)
    except KeyboardInterrupt:
        print("Stopping scheduler...")
    finally:
        stop_sync_scheduler()
        print("Scheduler stopped.")