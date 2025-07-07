import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session

from app.core.config import settings
from app.core.data_management import AuditLogDataManager, DataRetentionPolicy
from app.api.deps import get_db

logger = logging.getLogger(__name__)


class DataManagementScheduler:
    """Scheduler for automated data management tasks"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.policy = DataRetentionPolicy()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs"""
        # Daily retention policy application (2 AM)
        self.scheduler.add_job(
            func=self._apply_retention_policy,
            trigger=CronTrigger(hour=2, minute=0),
            id="retention_policy",
            name="Apply Retention Policy",
            replace_existing=True
        )
        
        # Weekly archival (Sunday 3 AM)
        self.scheduler.add_job(
            func=self._archive_old_logs,
            trigger=CronTrigger(day_of_week="sun", hour=3, minute=0),
            id="archive_logs",
            name="Archive Old Logs",
            replace_existing=True
        )
        
        # Daily compression (1 AM)
        self.scheduler.add_job(
            func=self._compress_archives,
            trigger=CronTrigger(hour=1, minute=0),
            id="compress_archives",
            name="Compress Archives",
            replace_existing=True
        )
        
        # Daily backup (4 AM)
        self.scheduler.add_job(
            func=self._create_backup,
            trigger=CronTrigger(hour=4, minute=0),
            id="create_backup",
            name="Create Backup",
            replace_existing=True
        )
        
        # Weekly backup cleanup (Saturday 5 AM)
        self.scheduler.add_job(
            func=self._cleanup_backups,
            trigger=CronTrigger(day_of_week="sat", hour=5, minute=0),
            id="cleanup_backups",
            name="Cleanup Old Backups",
            replace_existing=True
        )
        
        # Monthly full maintenance (1st of month at 6 AM)
        self.scheduler.add_job(
            func=self._full_maintenance,
            trigger=CronTrigger(day=1, hour=6, minute=0),
            id="full_maintenance",
            name="Full Maintenance",
            replace_existing=True
        )
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Data management scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Data management scheduler stopped")
    
    def _get_db_session(self) -> Session:
        """Get database session"""
        return next(get_db())
    
    def _apply_retention_policy(self):
        """Apply retention policy (scheduled job)"""
        try:
            session = self._get_db_session()
            manager = AuditLogDataManager(session, self.policy)
            result = manager.apply_retention_policy()
            logger.info(f"Scheduled retention policy applied: {result['deleted_count']} logs deleted")
        except Exception as e:
            logger.error(f"Failed to apply retention policy: {e}")
        finally:
            session.close()
    
    def _archive_old_logs(self):
        """Archive old logs (scheduled job)"""
        try:
            session = self._get_db_session()
            manager = AuditLogDataManager(session, self.policy)
            result = manager.archive_old_logs()
            logger.info(f"Scheduled archival completed: {result['archived_count']} logs archived")
        except Exception as e:
            logger.error(f"Failed to archive old logs: {e}")
        finally:
            session.close()
    
    def _compress_archives(self):
        """Compress archives (scheduled job)"""
        try:
            session = self._get_db_session()
            manager = AuditLogDataManager(session, self.policy)
            result = manager.compress_old_archives()
            logger.info(f"Scheduled compression completed: {result['compressed_count']} files compressed")
        except Exception as e:
            logger.error(f"Failed to compress archives: {e}")
        finally:
            session.close()
    
    def _create_backup(self):
        """Create backup (scheduled job)"""
        try:
            session = self._get_db_session()
            manager = AuditLogDataManager(session, self.policy)
            result = manager.create_backup()
            logger.info(f"Scheduled backup created: {result['backup_file']}")
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
        finally:
            session.close()
    
    def _cleanup_backups(self):
        """Cleanup old backups (scheduled job)"""
        try:
            session = self._get_db_session()
            manager = AuditLogDataManager(session, self.policy)
            result = manager.cleanup_old_backups()
            logger.info(f"Scheduled backup cleanup completed: {result['deleted_count']} files deleted")
        except Exception as e:
            logger.error(f"Failed to cleanup backups: {e}")
        finally:
            session.close()
    
    def _full_maintenance(self):
        """Full maintenance (scheduled job)"""
        try:
            session = self._get_db_session()
            manager = AuditLogDataManager(session, self.policy)
            
            # Run all maintenance tasks
            retention_result = manager.apply_retention_policy()
            archive_result = manager.archive_old_logs()
            compress_result = manager.compress_old_archives()
            backup_result = manager.create_backup()
            cleanup_result = manager.cleanup_old_backups()
            
            logger.info(f"Scheduled full maintenance completed: "
                       f"retention={retention_result['deleted_count']}, "
                       f"archive={archive_result['archived_count']}, "
                       f"compress={compress_result['compressed_count']}, "
                       f"backup={backup_result['log_count']}, "
                       f"cleanup={cleanup_result['deleted_count']}")
        except Exception as e:
            logger.error(f"Failed to run full maintenance: {e}")
        finally:
            session.close()
    
    def get_job_status(self) -> dict:
        """Get status of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        
        return {
            "scheduler_running": self.scheduler.running,
            "jobs": jobs,
            "job_count": len(jobs)
        }
    
    def update_policy(self, policy: DataRetentionPolicy):
        """Update the policy used by scheduled jobs"""
        self.policy = policy
        logger.info("Data management policy updated")


# Global scheduler instance
scheduler = DataManagementScheduler()


def start_scheduler():
    """Start the data management scheduler"""
    scheduler.start()


def stop_scheduler():
    """Stop the data management scheduler"""
    scheduler.stop()


def get_scheduler_status() -> dict:
    """Get scheduler status"""
    return scheduler.get_job_status() 