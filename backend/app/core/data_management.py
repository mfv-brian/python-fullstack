import gzip
import json
import os
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from sqlmodel import Session, select, delete
from sqlalchemy import text

from app.core.config import settings
from app.models import AuditLog

logger = logging.getLogger(__name__)


class DataRetentionPolicy:
    """Configurable retention policy for audit logs"""
    
    def __init__(
        self,
        retention_days: int = 90,
        archive_after_days: int = 30,
        compress_after_days: int = 7,
        max_log_size_mb: int = 1000,
        backup_interval_hours: int = 24,
    ):
        self.retention_days = retention_days
        self.archive_after_days = archive_after_days
        self.compress_after_days = compress_after_days
        self.max_log_size_mb = max_log_size_mb
        self.backup_interval_hours = backup_interval_hours


class AuditLogDataManager:
    """Manages audit log data retention, archival, compression, and backup"""
    
    def __init__(self, session: Session, policy: Optional[DataRetentionPolicy] = None):
        self.session = session
        self.policy = policy or DataRetentionPolicy()
        self.archive_dir = Path(settings.BASE_DIR) / "archives" / "audit_logs"
        self.backup_dir = Path(settings.BASE_DIR) / "backups" / "audit_logs"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure archive and backup directories exist"""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def apply_retention_policy(self) -> Dict[str, int]:
        """
        Apply retention policy to audit logs
        Returns: Dict with counts of processed logs
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.policy.retention_days)
        
        # Delete logs older than retention period
        statement = delete(AuditLog).where(AuditLog.timestamp < cutoff_date)
        result = self.session.execute(statement)
        deleted_count = result.rowcount
        
        self.session.commit()
        
        logger.info(f"Deleted {deleted_count} audit logs older than {self.policy.retention_days} days")
        
        return {
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
    
    def archive_old_logs(self) -> Dict[str, Any]:
        """
        Archive logs older than archive_after_days to cold storage
        Returns: Dict with archive information
        """
        archive_cutoff = datetime.now(timezone.utc) - timedelta(days=self.policy.archive_after_days)
        
        # Get logs to archive
        statement = select(AuditLog).where(AuditLog.timestamp < archive_cutoff)
        logs_to_archive = self.session.exec(statement).all()
        
        if not logs_to_archive:
            return {"archived_count": 0, "archive_file": None}
        
        # Create archive file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"audit_logs_{timestamp}.json.gz"
        
        # Write logs to compressed archive
        with gzip.open(archive_file, 'wt', encoding='utf-8') as f:
            for log in logs_to_archive:
                log_data = {
                    "id": str(log.id),
                    "user_id": str(log.user_id),
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "before_state": log.before_state,
                    "after_state": log.after_state,
                    "custom_metadata": log.custom_metadata,
                    "severity": log.severity,
                    "tenant_id": str(log.tenant_id) if log.tenant_id else None,
                    "timestamp": log.timestamp.isoformat(),
                    "session_id": log.session_id,
                }
                f.write(json.dumps(log_data) + '\n')
        
        # Delete archived logs from database
        statement = delete(AuditLog).where(AuditLog.timestamp < archive_cutoff)
        result = self.session.execute(statement)
        deleted_count = result.rowcount
        
        self.session.commit()
        
        archive_size_mb = archive_file.stat().st_size / (1024 * 1024)
        
        logger.info(f"Archived {deleted_count} logs to {archive_file} ({archive_size_mb:.2f} MB)")
        
        return {
            "archived_count": deleted_count,
            "archive_file": str(archive_file),
            "archive_size_mb": archive_size_mb,
            "archive_cutoff": archive_cutoff.isoformat()
        }
    
    def compress_old_archives(self) -> Dict[str, Any]:
        """
        Compress archive files older than compress_after_days
        Returns: Dict with compression information
        """
        compress_cutoff = datetime.now() - timedelta(days=self.policy.compress_after_days)
        compressed_count = 0
        total_saved_mb = 0
        
        for archive_file in self.archive_dir.glob("audit_logs_*.json"):
            if archive_file.stat().st_mtime < compress_cutoff.timestamp():
                # Already compressed
                if archive_file.suffix == '.gz':
                    continue
                
                # Compress the file
                compressed_file = archive_file.with_suffix('.json.gz')
                with open(archive_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Calculate space saved
                original_size = archive_file.stat().st_size
                compressed_size = compressed_file.stat().st_size
                saved_mb = (original_size - compressed_size) / (1024 * 1024)
                
                # Remove original file
                archive_file.unlink()
                
                compressed_count += 1
                total_saved_mb += saved_mb
        
        logger.info(f"Compressed {compressed_count} archive files, saved {total_saved_mb:.2f} MB")
        
        return {
            "compressed_count": compressed_count,
            "total_saved_mb": total_saved_mb
        }
    
    def create_backup(self) -> Dict[str, Any]:
        """
        Create a backup of current audit logs
        Returns: Dict with backup information
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"audit_logs_backup_{timestamp}.sqlite"
        
        # Get all current logs
        statement = select(AuditLog)
        logs = self.session.exec(statement).all()
        
        # Create SQLite backup
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE audit_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                before_state TEXT,
                after_state TEXT,
                custom_metadata TEXT,
                severity TEXT NOT NULL,
                tenant_id TEXT,
                timestamp TEXT NOT NULL,
                session_id TEXT
            )
        ''')
        
        # Insert data
        for log in logs:
            cursor.execute('''
                INSERT INTO audit_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(log.id),
                str(log.user_id),
                log.action,
                log.resource_type,
                log.resource_id,
                log.ip_address,
                log.user_agent,
                json.dumps(log.before_state) if log.before_state else None,
                json.dumps(log.after_state) if log.after_state else None,
                json.dumps(log.custom_metadata) if log.custom_metadata else None,
                log.severity,
                str(log.tenant_id) if log.tenant_id else None,
                log.timestamp.isoformat(),
                log.session_id,
            ))
        
        conn.commit()
        conn.close()
        
        backup_size_mb = backup_file.stat().st_size / (1024 * 1024)
        
        logger.info(f"Created backup: {backup_file} ({backup_size_mb:.2f} MB, {len(logs)} logs)")
        
        return {
            "backup_file": str(backup_file),
            "backup_size_mb": backup_size_mb,
            "log_count": len(logs),
            "timestamp": timestamp
        }
    
    def restore_from_backup(self, backup_file: str) -> Dict[str, Any]:
        """
        Restore audit logs from a backup file
        Returns: Dict with restore information
        """
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Connect to backup database
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        
        # Get all logs from backup
        cursor.execute('SELECT * FROM audit_logs')
        backup_logs = cursor.fetchall()
        conn.close()
        
        # Clear current logs (optional - you might want to merge instead)
        # statement = delete(AuditLog)
        # self.session.execute(statement)
        
        # Restore logs
        restored_count = 0
        for log_data in backup_logs:
            try:
                audit_log = AuditLog(
                    id=log_data[0],
                    user_id=log_data[1],
                    action=log_data[2],
                    resource_type=log_data[3],
                    resource_id=log_data[4],
                    ip_address=log_data[5],
                    user_agent=log_data[6],
                    before_state=json.loads(log_data[7]) if log_data[7] else None,
                    after_state=json.loads(log_data[8]) if log_data[8] else None,
                    custom_metadata=json.loads(log_data[9]) if log_data[9] else None,
                    severity=log_data[10],
                    tenant_id=log_data[11],
                    timestamp=datetime.fromisoformat(log_data[12]),
                    session_id=log_data[13],
                )
                self.session.add(audit_log)
                restored_count += 1
            except Exception as e:
                logger.error(f"Failed to restore log {log_data[0]}: {e}")
        
        self.session.commit()
        
        logger.info(f"Restored {restored_count} logs from backup: {backup_file}")
        
        return {
            "restored_count": restored_count,
            "backup_file": backup_file,
            "total_in_backup": len(backup_logs)
        }
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics for audit logs
        Returns: Dict with storage information
        """
        # Database stats
        statement = select(AuditLog)
        logs = self.session.exec(statement).all()
        
        # Archive stats
        archive_files = list(self.archive_dir.glob("audit_logs_*.json.gz"))
        archive_size_mb = sum(f.stat().st_size for f in archive_files) / (1024 * 1024)
        
        # Backup stats
        backup_files = list(self.backup_dir.glob("audit_logs_backup_*.sqlite"))
        backup_size_mb = sum(f.stat().st_size for f in backup_files) / (1024 * 1024)
        
        # Calculate oldest and newest logs
        if logs:
            oldest_log = min(logs, key=lambda x: x.timestamp)
            newest_log = max(logs, key=lambda x: x.timestamp)
        else:
            oldest_log = newest_log = None
        
        return {
            "database": {
                "log_count": len(logs),
                "oldest_log": oldest_log.timestamp.isoformat() if oldest_log else None,
                "newest_log": newest_log.timestamp.isoformat() if newest_log else None,
            },
            "archives": {
                "file_count": len(archive_files),
                "total_size_mb": archive_size_mb,
            },
            "backups": {
                "file_count": len(backup_files),
                "total_size_mb": backup_size_mb,
            },
            "policy": {
                "retention_days": self.policy.retention_days,
                "archive_after_days": self.policy.archive_after_days,
                "compress_after_days": self.policy.compress_after_days,
                "backup_interval_hours": self.policy.backup_interval_hours,
            }
        }
    
    def cleanup_old_backups(self, keep_days: int = 30) -> Dict[str, Any]:
        """
        Clean up old backup files
        Returns: Dict with cleanup information
        """
        cutoff_time = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0
        freed_mb = 0
        
        for backup_file in self.backup_dir.glob("audit_logs_backup_*.sqlite"):
            if backup_file.stat().st_mtime < cutoff_time.timestamp():
                file_size_mb = backup_file.stat().st_size / (1024 * 1024)
                backup_file.unlink()
                deleted_count += 1
                freed_mb += file_size_mb
        
        logger.info(f"Cleaned up {deleted_count} old backup files, freed {freed_mb:.2f} MB")
        
        return {
            "deleted_count": deleted_count,
            "freed_mb": freed_mb,
            "cutoff_days": keep_days
        }


# Convenience functions for common operations
def apply_retention_policy(session: Session, policy: Optional[DataRetentionPolicy] = None) -> Dict[str, int]:
    """Apply retention policy to audit logs"""
    manager = AuditLogDataManager(session, policy)
    return manager.apply_retention_policy()


def archive_old_logs(session: Session, policy: Optional[DataRetentionPolicy] = None) -> Dict[str, Any]:
    """Archive old audit logs"""
    manager = AuditLogDataManager(session, policy)
    return manager.archive_old_logs()


def create_backup(session: Session, policy: Optional[DataRetentionPolicy] = None) -> Dict[str, Any]:
    """Create backup of audit logs"""
    manager = AuditLogDataManager(session, policy)
    return manager.create_backup()


def get_storage_stats(session: Session, policy: Optional[DataRetentionPolicy] = None) -> Dict[str, Any]:
    """Get storage statistics"""
    manager = AuditLogDataManager(session, policy)
    return manager.get_storage_stats() 