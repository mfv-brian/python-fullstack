import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.data_management import AuditLogDataManager, DataRetentionPolicy
from app.models import AuditLog, User
from app.tests.utils.user import create_random_user


class TestDataManagementAPI:
    """Test data management API endpoints"""

    def test_get_storage_stats(self, client: TestClient, superuser_headers: dict):
        """Test getting storage statistics"""
        response = client.get("/api/v1/data-management/storage/stats", headers=superuser_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "database" in data
        assert "archives" in data
        assert "backups" in data
        assert "policy" in data

    def test_apply_retention_policy(self, client: TestClient, superuser_headers: dict, db: Session):
        """Test applying retention policy"""
        # Create some old audit logs
        old_date = datetime.now(timezone.utc) - timedelta(days=100)
        user = create_random_user(db)
        
        for i in range(5):
            audit_log = AuditLog(
                user_id=user.id,
                action="test_action",
                resource_type="test_resource",
                resource_id=f"test_id_{i}",
                severity="INFO",
                timestamp=old_date,
            )
            db.add(audit_log)
        db.commit()
        
        response = client.post(
            "/api/v1/data-management/retention/apply?retention_days=90",
            headers=superuser_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["deleted_count"] == 5
        assert "cutoff_date" in data
        assert data["applied_by"] == "admin@example.com"

    def test_create_archive(self, client: TestClient, superuser_headers: dict, db: Session):
        """Test creating archive of old logs"""
        # Create some old audit logs
        old_date = datetime.now(timezone.utc) - timedelta(days=40)
        user = create_random_user(db)
        
        for i in range(3):
            audit_log = AuditLog(
                user_id=user.id,
                action="test_action",
                resource_type="test_resource",
                resource_id=f"test_id_{i}",
                severity="INFO",
                timestamp=old_date,
            )
            db.add(audit_log)
        db.commit()
        
        response = client.post(
            "/api/v1/data-management/archive/create?archive_after_days=30",
            headers=superuser_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["archived_count"] == 3
        assert data["archive_file"] is not None
        assert data["archive_size_mb"] > 0

    def test_compress_archives(self, client: TestClient, superuser_headers: dict):
        """Test compressing archives"""
        response = client.post(
            "/api/v1/data-management/archive/compress?compress_after_days=7",
            headers=superuser_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "compressed_count" in data
        assert "total_saved_mb" in data

    def test_create_backup(self, client: TestClient, superuser_headers: dict, db: Session):
        """Test creating backup"""
        # Create some audit logs
        user = create_random_user(db)
        for i in range(3):
            audit_log = AuditLog(
                user_id=user.id,
                action="test_action",
                resource_type="test_resource",
                resource_id=f"test_id_{i}",
                severity="INFO",
            )
            db.add(audit_log)
        db.commit()
        
        response = client.post("/api/v1/data-management/backup/create", headers=superuser_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["backup_file"] is not None
        assert data["backup_size_mb"] > 0
        assert data["log_count"] == 3

    def test_restore_from_backup(self, client: TestClient, superuser_headers: dict, db: Session):
        """Test restoring from backup"""
        # Create a backup first
        manager = AuditLogDataManager(db)
        backup_result = manager.create_backup()
        
        response = client.post(
            f"/api/v1/data-management/backup/restore?backup_file={backup_result['backup_file']}",
            headers=superuser_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["restored_count"] >= 0
        assert data["backup_file"] == backup_result["backup_file"]

    def test_restore_from_nonexistent_backup(self, client: TestClient, superuser_headers: dict):
        """Test restoring from non-existent backup"""
        response = client.post(
            "/api/v1/data-management/backup/restore?backup_file=nonexistent.sqlite",
            headers=superuser_headers
        )
        assert response.status_code == 404

    def test_upload_backup_file(self, client: TestClient, superuser_headers: dict, db: Session):
        """Test uploading backup file"""
        # Create a backup file
        manager = AuditLogDataManager(db)
        backup_result = manager.create_backup()
        
        with open(backup_result["backup_file"], "rb") as f:
            files = {"file": ("test_backup.sqlite", f, "application/octet-stream")}
            response = client.post(
                "/api/v1/data-management/backup/upload",
                headers=superuser_headers,
                files=files
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["uploaded_file"] == "test_backup.sqlite"
        assert data["restored_count"] >= 0

    def test_upload_invalid_file(self, client: TestClient, superuser_headers: dict):
        """Test uploading invalid file"""
        files = {"file": ("test.txt", b"invalid content", "text/plain")}
        response = client.post(
            "/api/v1/data-management/backup/upload",
            headers=superuser_headers,
            files=files
        )
        assert response.status_code == 400

    def test_cleanup_backups(self, client: TestClient, superuser_headers: dict):
        """Test cleaning up old backups"""
        response = client.delete(
            "/api/v1/data-management/backup/cleanup?keep_days=30",
            headers=superuser_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "deleted_count" in data
        assert "freed_mb" in data

    def test_run_full_maintenance(self, client: TestClient, superuser_headers: dict, db: Session):
        """Test running full maintenance"""
        # Create some test data
        user = create_random_user(db)
        for i in range(3):
            audit_log = AuditLog(
                user_id=user.id,
                action="test_action",
                resource_type="test_resource",
                resource_id=f"test_id_{i}",
                severity="INFO",
            )
            db.add(audit_log)
        db.commit()
        
        response = client.post(
            "/api/v1/data-management/maintenance/full",
            headers=superuser_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "maintenance_tasks" in data
        assert "retention" in data["maintenance_tasks"]
        assert "archival" in data["maintenance_tasks"]
        assert "compression" in data["maintenance_tasks"]
        assert "backup" in data["maintenance_tasks"]
        assert "cleanup" in data["maintenance_tasks"]

    def test_get_current_policy(self, client: TestClient, superuser_headers: dict):
        """Test getting current policy"""
        response = client.get("/api/v1/data-management/policy/current", headers=superuser_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "policy" in data
        policy = data["policy"]
        assert "retention_days" in policy
        assert "archive_after_days" in policy
        assert "compress_after_days" in policy
        assert "max_log_size_mb" in policy
        assert "backup_interval_hours" in policy

    def test_update_policy(self, client: TestClient, superuser_headers: dict):
        """Test updating policy"""
        response = client.put(
            "/api/v1/data-management/policy/update?retention_days=120&archive_after_days=60",
            headers=superuser_headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "old_policy" in data
        assert "new_policy" in data
        assert data["new_policy"]["retention_days"] == 120
        assert data["new_policy"]["archive_after_days"] == 60

    def test_scheduler_status(self, client: TestClient, superuser_headers: dict):
        """Test getting scheduler status"""
        response = client.get("/api/v1/data-management/scheduler/status", headers=superuser_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "scheduler_running" in data
        assert "jobs" in data
        assert "job_count" in data

    def test_start_scheduler(self, client: TestClient, superuser_headers: dict):
        """Test starting scheduler"""
        response = client.post("/api/v1/data-management/scheduler/start", headers=superuser_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Scheduler started successfully"
        assert data["started_by"] == "admin@example.com"

    def test_stop_scheduler(self, client: TestClient, superuser_headers: dict):
        """Test stopping scheduler"""
        response = client.post("/api/v1/data-management/scheduler/stop", headers=superuser_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Scheduler stopped successfully"
        assert data["stopped_by"] == "admin@example.com"

    def test_unauthorized_access(self, client: TestClient, db: Session):
        """Test unauthorized access to data management endpoints"""
        # Create regular user
        user = create_random_user(db)
        headers = {"Authorization": f"Bearer {user.id}"}
        
        response = client.get("/api/v1/data-management/storage/stats", headers=headers)
        assert response.status_code == 401

    def test_missing_authentication(self, client: TestClient):
        """Test missing authentication"""
        response = client.get("/api/v1/data-management/storage/stats")
        assert response.status_code == 401


class TestDataRetentionPolicy:
    """Test DataRetentionPolicy class"""

    def test_default_policy(self):
        """Test default policy values"""
        policy = DataRetentionPolicy()
        assert policy.retention_days == 90
        assert policy.archive_after_days == 30
        assert policy.compress_after_days == 7
        assert policy.max_log_size_mb == 1000
        assert policy.backup_interval_hours == 24

    def test_custom_policy(self):
        """Test custom policy values"""
        policy = DataRetentionPolicy(
            retention_days=180,
            archive_after_days=60,
            compress_after_days=14,
            max_log_size_mb=2000,
            backup_interval_hours=48,
        )
        assert policy.retention_days == 180
        assert policy.archive_after_days == 60
        assert policy.compress_after_days == 14
        assert policy.max_log_size_mb == 2000
        assert policy.backup_interval_hours == 48


class TestAuditLogDataManager:
    """Test AuditLogDataManager class"""

    def test_initialization(self, db: Session):
        """Test manager initialization"""
        manager = AuditLogDataManager(db)
        assert manager.session == db
        assert isinstance(manager.policy, DataRetentionPolicy)
        assert manager.archive_dir.exists()
        assert manager.backup_dir.exists()

    def test_apply_retention_policy_empty(self, db: Session):
        """Test applying retention policy with no logs"""
        manager = AuditLogDataManager(db)
        result = manager.apply_retention_policy()
        assert result["deleted_count"] == 0
        assert "cutoff_date" in result

    def test_archive_old_logs_empty(self, db: Session):
        """Test archiving with no old logs"""
        manager = AuditLogDataManager(db)
        result = manager.archive_old_logs()
        assert result["archived_count"] == 0
        assert result["archive_file"] is None

    def test_create_backup_empty(self, db: Session):
        """Test creating backup with no logs"""
        manager = AuditLogDataManager(db)
        result = manager.create_backup()
        assert result["log_count"] == 0
        assert result["backup_file"] is not None
        assert result["backup_size_mb"] > 0

    def test_get_storage_stats_empty(self, db: Session):
        """Test getting storage stats with no data"""
        manager = AuditLogDataManager(db)
        stats = manager.get_storage_stats()
        assert stats["database"]["log_count"] == 0
        assert stats["database"]["oldest_log"] is None
        assert stats["database"]["newest_log"] is None
        assert stats["archives"]["file_count"] == 0
        assert stats["backups"]["file_count"] == 0

    def test_cleanup_old_backups_empty(self, db: Session):
        """Test cleaning up backups with no old files"""
        manager = AuditLogDataManager(db)
        result = manager.cleanup_old_backups()
        assert result["deleted_count"] == 0
        assert result["freed_mb"] == 0

    def test_restore_from_nonexistent_backup(self, db: Session):
        """Test restoring from non-existent backup"""
        manager = AuditLogDataManager(db)
        with pytest.raises(FileNotFoundError):
            manager.restore_from_backup("nonexistent.sqlite") 