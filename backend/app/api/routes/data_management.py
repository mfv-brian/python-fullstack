from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session

from app.api.deps import get_current_active_superuser, get_db
from app.core.data_management import (
    AuditLogDataManager,
    DataRetentionPolicy,
    apply_retention_policy,
    archive_old_logs,
    create_backup,
    get_storage_stats,
)
from app.core.scheduler import get_scheduler_status, start_scheduler, stop_scheduler
from app.models import User

router = APIRouter()


@router.get("/storage/stats", response_model=Dict[str, Any])
def get_storage_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Get storage statistics for audit logs
    """
    return get_storage_stats(db)


@router.post("/retention/apply", response_model=Dict[str, Any])
def apply_data_retention(
    retention_days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Apply retention policy to audit logs
    """
    policy = DataRetentionPolicy(retention_days=retention_days)
    result = apply_retention_policy(db, policy)
    return {
        "message": "Retention policy applied successfully",
        "deleted_count": result["deleted_count"],
        "cutoff_date": result["cutoff_date"],
        "applied_by": current_user.email,
        "applied_at": datetime.utcnow().isoformat(),
    }


@router.post("/archive/create", response_model=Dict[str, Any])
def create_archive(
    archive_after_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Archive old audit logs to cold storage
    """
    policy = DataRetentionPolicy(archive_after_days=archive_after_days)
    result = archive_old_logs(db, policy)
    return {
        "message": "Archive created successfully",
        "archived_count": result["archived_count"],
        "archive_file": result["archive_file"],
        "archive_size_mb": result["archive_size_mb"],
        "created_by": current_user.email,
        "created_at": datetime.utcnow().isoformat(),
    }


@router.post("/archive/compress", response_model=Dict[str, Any])
def compress_archives(
    compress_after_days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Compress old archive files
    """
    policy = DataRetentionPolicy(compress_after_days=compress_after_days)
    manager = AuditLogDataManager(db, policy)
    result = manager.compress_old_archives()
    return {
        "message": "Archives compressed successfully",
        "compressed_count": result["compressed_count"],
        "total_saved_mb": result["total_saved_mb"],
        "compressed_by": current_user.email,
        "compressed_at": datetime.utcnow().isoformat(),
    }


@router.post("/backup/create", response_model=Dict[str, Any])
def create_data_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Create a backup of current audit logs
    """
    result = create_backup(db)
    return {
        "message": "Backup created successfully",
        "backup_file": result["backup_file"],
        "backup_size_mb": result["backup_size_mb"],
        "log_count": result["log_count"],
        "created_by": current_user.email,
        "created_at": datetime.utcnow().isoformat(),
    }


@router.post("/backup/restore", response_model=Dict[str, Any])
def restore_from_backup(
    backup_file: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Restore audit logs from a backup file
    """
    manager = AuditLogDataManager(db)
    try:
        result = manager.restore_from_backup(backup_file)
        return {
            "message": "Backup restored successfully",
            "restored_count": result["restored_count"],
            "backup_file": result["backup_file"],
            "total_in_backup": result["total_in_backup"],
            "restored_by": current_user.email,
            "restored_at": datetime.utcnow().isoformat(),
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@router.post("/backup/upload", response_model=Dict[str, Any])
def upload_backup_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Upload a backup file and restore from it
    """
    if not file.filename.endswith('.sqlite'):
        raise HTTPException(status_code=400, detail="Only SQLite backup files are supported")
    
    # Save uploaded file
    manager = AuditLogDataManager(db)
    backup_path = manager.backup_dir / f"uploaded_{file.filename}"
    
    try:
        with open(backup_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        # Restore from uploaded backup
        result = manager.restore_from_backup(str(backup_path))
        
        return {
            "message": "Backup uploaded and restored successfully",
            "uploaded_file": file.filename,
            "restored_count": result["restored_count"],
            "total_in_backup": result["total_in_backup"],
            "uploaded_by": current_user.email,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        # Clean up uploaded file on error
        if backup_path.exists():
            backup_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload and restore failed: {str(e)}")


@router.delete("/backup/cleanup", response_model=Dict[str, Any])
def cleanup_old_backups(
    keep_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Clean up old backup files
    """
    manager = AuditLogDataManager(db)
    result = manager.cleanup_old_backups(keep_days)
    return {
        "message": "Old backups cleaned up successfully",
        "deleted_count": result["deleted_count"],
        "freed_mb": result["freed_mb"],
        "keep_days": result["cutoff_days"],
        "cleaned_by": current_user.email,
        "cleaned_at": datetime.utcnow().isoformat(),
    }


@router.post("/maintenance/full", response_model=Dict[str, Any])
def run_full_maintenance(
    retention_days: int = 90,
    archive_after_days: int = 30,
    compress_after_days: int = 7,
    backup_keep_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Run full data maintenance including retention, archival, compression, and backup cleanup
    """
    policy = DataRetentionPolicy(
        retention_days=retention_days,
        archive_after_days=archive_after_days,
        compress_after_days=compress_after_days,
    )
    
    manager = AuditLogDataManager(db, policy)
    
    # Run all maintenance tasks
    retention_result = manager.apply_retention_policy()
    archive_result = manager.archive_old_logs()
    compress_result = manager.compress_old_archives()
    backup_result = manager.create_backup()
    cleanup_result = manager.cleanup_old_backups(backup_keep_days)
    
    return {
        "message": "Full maintenance completed successfully",
        "maintenance_tasks": {
            "retention": retention_result,
            "archival": archive_result,
            "compression": compress_result,
            "backup": backup_result,
            "cleanup": cleanup_result,
        },
        "executed_by": current_user.email,
        "executed_at": datetime.utcnow().isoformat(),
    }


@router.get("/policy/current", response_model=Dict[str, Any])
def get_current_policy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Get current data retention policy settings
    """
    manager = AuditLogDataManager(db)
    return {
        "policy": {
            "retention_days": manager.policy.retention_days,
            "archive_after_days": manager.policy.archive_after_days,
            "compress_after_days": manager.policy.compress_after_days,
            "max_log_size_mb": manager.policy.max_log_size_mb,
            "backup_interval_hours": manager.policy.backup_interval_hours,
        },
        "retrieved_by": current_user.email,
        "retrieved_at": datetime.utcnow().isoformat(),
    }


@router.put("/policy/update", response_model=Dict[str, Any])
def update_policy(
    retention_days: Optional[int] = None,
    archive_after_days: Optional[int] = None,
    compress_after_days: Optional[int] = None,
    max_log_size_mb: Optional[int] = None,
    backup_interval_hours: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Update data retention policy settings
    """
    # Get current policy
    manager = AuditLogDataManager(db)
    current_policy = manager.policy
    
    # Update only provided values
    new_policy = DataRetentionPolicy(
        retention_days=retention_days or current_policy.retention_days,
        archive_after_days=archive_after_days or current_policy.archive_after_days,
        compress_after_days=compress_after_days or current_policy.compress_after_days,
        max_log_size_mb=max_log_size_mb or current_policy.max_log_size_mb,
        backup_interval_hours=backup_interval_hours or current_policy.backup_interval_hours,
    )
    
    # Create new manager with updated policy
    updated_manager = AuditLogDataManager(db, new_policy)
    
    return {
        "message": "Policy updated successfully",
        "old_policy": {
            "retention_days": current_policy.retention_days,
            "archive_after_days": current_policy.archive_after_days,
            "compress_after_days": current_policy.compress_after_days,
            "max_log_size_mb": current_policy.max_log_size_mb,
            "backup_interval_hours": current_policy.backup_interval_hours,
        },
        "new_policy": {
            "retention_days": new_policy.retention_days,
            "archive_after_days": new_policy.archive_after_days,
            "compress_after_days": new_policy.compress_after_days,
            "max_log_size_mb": new_policy.max_log_size_mb,
            "backup_interval_hours": new_policy.backup_interval_hours,
        },
        "updated_by": current_user.email,
        "updated_at": datetime.utcnow().isoformat(),
    }


@router.get("/scheduler/status", response_model=Dict[str, Any])
def get_scheduler_status_endpoint(
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Get scheduler status and job information
    """
    return get_scheduler_status()


@router.post("/scheduler/start", response_model=Dict[str, Any])
def start_scheduler_endpoint(
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Start the data management scheduler
    """
    start_scheduler()
    return {
        "message": "Scheduler started successfully",
        "started_by": current_user.email,
        "started_at": datetime.utcnow().isoformat(),
    }


@router.post("/scheduler/stop", response_model=Dict[str, Any])
def stop_scheduler_endpoint(
    current_user: User = Depends(get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Stop the data management scheduler
    """
    stop_scheduler()
    return {
        "message": "Scheduler stopped successfully",
        "stopped_by": current_user.email,
        "stopped_at": datetime.utcnow().isoformat(),
    } 