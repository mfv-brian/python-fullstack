#!/usr/bin/env python3
"""
Data Management Demo Script

This script demonstrates the various data management features for audit logs.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlmodel import Session

from app.core.config import settings
from app.core.data_management import AuditLogDataManager, DataRetentionPolicy
from app.core.db import engine
from app.models import AuditLog, User


def create_sample_data(session: Session):
    """Create sample audit logs for demonstration"""
    print("Creating sample audit logs...")
    
    # Create a sample user
    user = User(
        email="demo@example.com",
        hashed_password="demo_hash",
        is_active=True,
        is_superuser=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create audit logs with different timestamps
    now = datetime.now(timezone.utc)
    
    # Recent logs (within retention period)
    for i in range(5):
        audit_log = AuditLog(
            user_id=user.id,
            action="CREATE",
            resource_type="item",
            resource_id=f"item_{i}",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Demo Browser)",
            before_state=None,
            after_state={"name": f"Item {i}", "description": f"Demo item {i}"},
            custom_metadata={"source": "demo", "batch": "recent"},
            severity="INFO",
            timestamp=now - timedelta(days=i),
        )
        session.add(audit_log)
    
    # Old logs (outside retention period)
    for i in range(10):
        audit_log = AuditLog(
            user_id=user.id,
            action="UPDATE",
            resource_type="user",
            resource_id=f"user_{i}",
            ip_address="192.168.1.200",
            user_agent="Mozilla/5.0 (Demo Browser)",
            before_state={"email": f"old{i}@example.com"},
            after_state={"email": f"new{i}@example.com"},
            custom_metadata={"source": "demo", "batch": "old"},
            severity="INFO",
            timestamp=now - timedelta(days=100 + i),
        )
        session.add(audit_log)
    
    # Very old logs (for archival)
    for i in range(8):
        audit_log = AuditLog(
            user_id=user.id,
            action="DELETE",
            resource_type="document",
            resource_id=f"doc_{i}",
            ip_address="192.168.1.300",
            user_agent="Mozilla/5.0 (Demo Browser)",
            before_state={"title": f"Document {i}", "content": f"Content {i}"},
            after_state=None,
            custom_metadata={"source": "demo", "batch": "archival"},
            severity="WARNING",
            timestamp=now - timedelta(days=50 + i),
        )
        session.add(audit_log)
    
    session.commit()
    print(f"Created {23} sample audit logs")


def demonstrate_retention_policy(session: Session):
    """Demonstrate retention policy application"""
    print("\n=== Retention Policy Demo ===")
    
    # Get initial count
    initial_count = session.query(AuditLog).count()
    print(f"Initial audit log count: {initial_count}")
    
    # Apply retention policy (keep logs for 90 days)
    manager = AuditLogDataManager(session, DataRetentionPolicy(retention_days=90))
    result = manager.apply_retention_policy()
    
    print(f"Retention policy applied:")
    print(f"  - Deleted {result['deleted_count']} logs")
    print(f"  - Cutoff date: {result['cutoff_date']}")
    
    # Get final count
    final_count = session.query(AuditLog).count()
    print(f"Final audit log count: {final_count}")


def demonstrate_archival(session: Session):
    """Demonstrate archival functionality"""
    print("\n=== Archival Demo ===")
    
    # Get initial count
    initial_count = session.query(AuditLog).count()
    print(f"Initial audit log count: {initial_count}")
    
    # Create archive (archive logs older than 30 days)
    manager = AuditLogDataManager(session, DataRetentionPolicy(archive_after_days=30))
    result = manager.archive_old_logs()
    
    print(f"Archive created:")
    print(f"  - Archived {result['archived_count']} logs")
    print(f"  - Archive file: {result['archive_file']}")
    print(f"  - Archive size: {result['archive_size_mb']:.2f} MB")
    
    # Get final count
    final_count = session.query(AuditLog).count()
    print(f"Final audit log count: {final_count}")


def demonstrate_backup(session: Session):
    """Demonstrate backup functionality"""
    print("\n=== Backup Demo ===")
    
    # Create backup
    manager = AuditLogDataManager(session)
    result = manager.create_backup()
    
    print(f"Backup created:")
    print(f"  - Backup file: {result['backup_file']}")
    print(f"  - Backup size: {result['backup_size_mb']:.2f} MB")
    print(f"  - Log count: {result['log_count']}")
    
    return result['backup_file']


def demonstrate_restore(session: Session, backup_file: str):
    """Demonstrate restore functionality"""
    print("\n=== Restore Demo ===")
    
    # Get initial count
    initial_count = session.query(AuditLog).count()
    print(f"Initial audit log count: {initial_count}")
    
    # Restore from backup
    manager = AuditLogDataManager(session)
    result = manager.restore_from_backup(backup_file)
    
    print(f"Backup restored:")
    print(f"  - Restored {result['restored_count']} logs")
    print(f"  - Total in backup: {result['total_in_backup']}")
    
    # Get final count
    final_count = session.query(AuditLog).count()
    print(f"Final audit log count: {final_count}")


def demonstrate_storage_stats(session: Session):
    """Demonstrate storage statistics"""
    print("\n=== Storage Statistics Demo ===")
    
    manager = AuditLogDataManager(session)
    stats = manager.get_storage_stats()
    
    print("Storage Statistics:")
    print(f"  Database:")
    print(f"    - Log count: {stats['database']['log_count']}")
    print(f"    - Oldest log: {stats['database']['oldest_log']}")
    print(f"    - Newest log: {stats['database']['newest_log']}")
    print(f"  Archives:")
    print(f"    - File count: {stats['archives']['file_count']}")
    print(f"    - Total size: {stats['archives']['total_size_mb']:.2f} MB")
    print(f"  Backups:")
    print(f"    - File count: {stats['backups']['file_count']}")
    print(f"    - Total size: {stats['backups']['total_size_mb']:.2f} MB")
    print(f"  Policy:")
    print(f"    - Retention days: {stats['policy']['retention_days']}")
    print(f"    - Archive after days: {stats['policy']['archive_after_days']}")
    print(f"    - Compress after days: {stats['policy']['compress_after_days']}")


def demonstrate_full_maintenance(session: Session):
    """Demonstrate full maintenance operation"""
    print("\n=== Full Maintenance Demo ===")
    
    manager = AuditLogDataManager(session, DataRetentionPolicy(
        retention_days=90,
        archive_after_days=30,
        compress_after_days=7,
    ))
    
    print("Running full maintenance...")
    
    # Run all maintenance tasks
    retention_result = manager.apply_retention_policy()
    print(f"✓ Retention: {retention_result['deleted_count']} logs deleted")
    
    archive_result = manager.archive_old_logs()
    print(f"✓ Archival: {archive_result['archived_count']} logs archived")
    
    compress_result = manager.compress_old_archives()
    print(f"✓ Compression: {compress_result['compressed_count']} files compressed")
    
    backup_result = manager.create_backup()
    print(f"✓ Backup: {backup_result['log_count']} logs backed up")
    
    cleanup_result = manager.cleanup_old_backups(keep_days=30)
    print(f"✓ Cleanup: {cleanup_result['deleted_count']} backup files deleted")
    
    print("Full maintenance completed!")


def main():
    """Main demonstration function"""
    print("=== Audit Log Data Management Demo ===\n")
    
    # Create database session
    session = Session(engine)
    
    try:
        # Create sample data
        create_sample_data(session)
        
        # Demonstrate storage statistics
        demonstrate_storage_stats(session)
        
        # Demonstrate retention policy
        demonstrate_retention_policy(session)
        
        # Demonstrate archival
        demonstrate_archival(session)
        
        # Demonstrate backup
        backup_file = demonstrate_backup(session)
        
        # Demonstrate restore
        demonstrate_restore(session, backup_file)
        
        # Demonstrate full maintenance
        demonstrate_full_maintenance(session)
        
        # Final storage statistics
        demonstrate_storage_stats(session)
        
        print("\n=== Demo Completed Successfully! ===")
        print("\nCheck the following directories for generated files:")
        print(f"  - Archives: {Path(settings.BASE_DIR) / 'archives' / 'audit_logs'}")
        print(f"  - Backups: {Path(settings.BASE_DIR) / 'backups' / 'audit_logs'}")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main() 