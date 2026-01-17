#!/usr/bin/env python3
"""
Data Management CLI Script

This script provides command-line interface for audit log data management operations.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from sqlmodel import Session

from app.core.config import settings
from app.core.data_management import (
    AuditLogDataManager,
    DataRetentionPolicy,
    apply_retention_policy,
    archive_old_logs,
    create_backup,
    get_storage_stats,
)
from app.core.db import get_db


def print_json(data: dict):
    """Print data as formatted JSON"""
    print(json.dumps(data, indent=2, default=str))


def get_storage_statistics():
    """Get and display storage statistics"""
    session = next(get_db())
    try:
        stats = get_storage_stats(session)
        print("=== Storage Statistics ===")
        print_json(stats)
    finally:
        session.close()


def apply_retention(retention_days: int):
    """Apply retention policy"""
    session = next(get_db())
    try:
        policy = DataRetentionPolicy(retention_days=retention_days)
        result = apply_retention_policy(session, policy)
        print("=== Retention Policy Applied ===")
        print_json(result)
    finally:
        session.close()


def create_archive(archive_after_days: int):
    """Create archive of old logs"""
    session = next(get_db())
    try:
        policy = DataRetentionPolicy(archive_after_days=archive_after_days)
        result = archive_old_logs(session, policy)
        print("=== Archive Created ===")
        print_json(result)
    finally:
        session.close()


def create_backup_operation():
    """Create backup of current logs"""
    session = next(get_db())
    try:
        result = create_backup(session)
        print("=== Backup Created ===")
        print_json(result)
    finally:
        session.close()


def restore_backup(backup_file: str):
    """Restore from backup file"""
    session = next(get_db())
    try:
        manager = AuditLogDataManager(session)
        result = manager.restore_from_backup(backup_file)
        print("=== Backup Restored ===")
        print_json(result)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        session.close()


def compress_archives(compress_after_days: int):
    """Compress old archives"""
    session = next(get_db())
    try:
        policy = DataRetentionPolicy(compress_after_days=compress_after_days)
        manager = AuditLogDataManager(session, policy)
        result = manager.compress_old_archives()
        print("=== Archives Compressed ===")
        print_json(result)
    finally:
        session.close()


def cleanup_backups(keep_days: int):
    """Clean up old backup files"""
    session = next(get_db())
    try:
        manager = AuditLogDataManager(session)
        result = manager.cleanup_old_backups(keep_days)
        print("=== Backups Cleaned Up ===")
        print_json(result)
    finally:
        session.close()


def run_full_maintenance(
    retention_days: int = 90,
    archive_after_days: int = 30,
    compress_after_days: int = 7,
    backup_keep_days: int = 30,
):
    """Run full maintenance operation"""
    session = next(get_db())
    try:
        policy = DataRetentionPolicy(
            retention_days=retention_days,
            archive_after_days=archive_after_days,
            compress_after_days=compress_after_days,
        )
        manager = AuditLogDataManager(session, policy)
        
        print("=== Starting Full Maintenance ===")
        
        # Run all maintenance tasks
        retention_result = manager.apply_retention_policy()
        print("✓ Retention policy applied")
        
        archive_result = manager.archive_old_logs()
        print("✓ Old logs archived")
        
        compress_result = manager.compress_old_archives()
        print("✓ Archives compressed")
        
        backup_result = manager.create_backup()
        print("✓ Backup created")
        
        cleanup_result = manager.cleanup_old_backups(backup_keep_days)
        print("✓ Old backups cleaned up")
        
        print("\n=== Full Maintenance Results ===")
        print_json({
            "retention": retention_result,
            "archival": archive_result,
            "compression": compress_result,
            "backup": backup_result,
            "cleanup": cleanup_result,
            "completed_at": datetime.utcnow().isoformat(),
        })
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Audit Log Data Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Stats command
    subparsers.add_parser("stats", help="Get storage statistics")
    
    # Retention command
    retention_parser = subparsers.add_parser("retention", help="Apply retention policy")
    retention_parser.add_argument(
        "--days", type=int, default=90, help="Retention period in days (default: 90)"
    )
    
    # Archive command
    archive_parser = subparsers.add_parser("archive", help="Create archive of old logs")
    archive_parser.add_argument(
        "--days", type=int, default=30, help="Archive logs older than days (default: 30)"
    )
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create backup")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("file", help="Backup file path")
    
    # Compress command
    compress_parser = subparsers.add_parser("compress", help="Compress old archives")
    compress_parser.add_argument(
        "--days", type=int, default=7, help="Compress archives older than days (default: 7)"
    )
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old backups")
    cleanup_parser.add_argument(
        "--days", type=int, default=30, help="Keep backups newer than days (default: 30)"
    )
    
    # Full maintenance command
    maintenance_parser = subparsers.add_parser("maintenance", help="Run full maintenance")
    maintenance_parser.add_argument(
        "--retention-days", type=int, default=90, help="Retention period in days (default: 90)"
    )
    maintenance_parser.add_argument(
        "--archive-days", type=int, default=30, help="Archive after days (default: 30)"
    )
    maintenance_parser.add_argument(
        "--compress-days", type=int, default=7, help="Compress after days (default: 7)"
    )
    maintenance_parser.add_argument(
        "--backup-keep-days", type=int, default=30, help="Keep backups newer than days (default: 30)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "stats":
            get_storage_statistics()
        elif args.command == "retention":
            apply_retention(args.days)
        elif args.command == "archive":
            create_archive(args.days)
        elif args.command == "backup":
            create_backup_operation()
        elif args.command == "restore":
            restore_backup(args.file)
        elif args.command == "compress":
            compress_archives(args.days)
        elif args.command == "cleanup":
            cleanup_backups(args.days)
        elif args.command == "maintenance":
            run_full_maintenance(
                retention_days=args.retention_days,
                archive_after_days=args.archive_days,
                compress_after_days=args.compress_days,
                backup_keep_days=args.backup_keep_days,
            )
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 