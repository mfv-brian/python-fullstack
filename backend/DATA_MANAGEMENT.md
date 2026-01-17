# Audit Log Data Management

This document describes the comprehensive data management system for audit logs, including retention policies, archival, compression, backup, and automated scheduling.

## Features

### 1. Data Retention Policies
- **Configurable retention periods**: Set how long to keep audit logs (default: 90 days)
- **Automatic cleanup**: Remove logs older than the retention period
- **Policy management**: View and update retention settings via API

### 2. Data Archival
- **Cold storage**: Move old logs to compressed archive files
- **Configurable archival periods**: Archive logs after specified days (default: 30 days)
- **JSON format**: Archives are stored in compressed JSON format for easy access
- **Automatic cleanup**: Remove archived logs from the database

### 3. Data Compression
- **Efficient storage**: Compress archive files to save disk space
- **Configurable compression periods**: Compress archives after specified days (default: 7 days)
- **Gzip compression**: Uses standard gzip compression for compatibility

### 4. Backup and Recovery
- **Automated backups**: Create regular backups of current audit logs
- **SQLite format**: Backups stored in SQLite format for portability
- **Upload/restore**: Upload backup files and restore from them
- **Backup cleanup**: Automatically remove old backup files

### 5. Automated Scheduling
- **Background jobs**: Automated execution of maintenance tasks
- **Configurable schedules**: Set custom schedules for each operation
- **Monitoring**: Track job status and execution history

## API Endpoints

### Storage Statistics
```http
GET /api/v1/data-management/storage/stats
```
Get comprehensive storage statistics including database, archive, and backup information.

### Retention Management
```http
POST /api/v1/data-management/retention/apply?retention_days=90
```
Apply retention policy to delete logs older than specified days.

### Archival Management
```http
POST /api/v1/data-management/archive/create?archive_after_days=30
```
Create archive of logs older than specified days.

```http
POST /api/v1/data-management/archive/compress?compress_after_days=7
```
Compress archive files older than specified days.

### Backup Management
```http
POST /api/v1/data-management/backup/create
```
Create a backup of current audit logs.

```http
POST /api/v1/data-management/backup/restore?backup_file=path/to/backup.sqlite
```
Restore audit logs from a backup file.

```http
POST /api/v1/data-management/backup/upload
```
Upload a backup file and restore from it.

```http
DELETE /api/v1/data-management/backup/cleanup?keep_days=30
```
Clean up backup files older than specified days.

### Full Maintenance
```http
POST /api/v1/data-management/maintenance/full
```
Run complete maintenance including retention, archival, compression, backup, and cleanup.

### Policy Management
```http
GET /api/v1/data-management/policy/current
```
Get current data retention policy settings.

```http
PUT /api/v1/data-management/policy/update?retention_days=120&archive_after_days=60
```
Update data retention policy settings.

### Scheduler Management
```http
GET /api/v1/data-management/scheduler/status
```
Get scheduler status and job information.

```http
POST /api/v1/data-management/scheduler/start
```
Start the data management scheduler.

```http
POST /api/v1/data-management/scheduler/stop
```
Stop the data management scheduler.

## CLI Usage

The system includes a command-line interface for data management operations:

### Basic Commands
```bash
# Get storage statistics
python -m app.scripts.data_management stats

# Apply retention policy
python -m app.scripts.data_management retention --days 90

# Create archive
python -m app.scripts.data_management archive --days 30

# Create backup
python -m app.scripts.data_management backup

# Restore from backup
python -m app.scripts.data_management restore /path/to/backup.sqlite

# Compress archives
python -m app.scripts.data_management compress --days 7

# Clean up old backups
python -m app.scripts.data_management cleanup --days 30

# Run full maintenance
python -m app.scripts.data_management maintenance \
  --retention-days 90 \
  --archive-days 30 \
  --compress-days 7 \
  --backup-keep-days 30
```

## Automated Scheduling

The system includes automated scheduling with the following default schedule:

- **Daily Retention Policy**: 2:00 AM
- **Daily Compression**: 1:00 AM  
- **Daily Backup**: 4:00 AM
- **Weekly Archival**: Sunday 3:00 AM
- **Weekly Backup Cleanup**: Saturday 5:00 AM
- **Monthly Full Maintenance**: 1st of month 6:00 AM

### Starting the Scheduler
```python
from app.core.scheduler import start_scheduler

# Start the scheduler
start_scheduler()
```

### Stopping the Scheduler
```python
from app.core.scheduler import stop_scheduler

# Stop the scheduler
stop_scheduler()
```

## Configuration

### Default Policy Settings
```python
DataRetentionPolicy(
    retention_days=90,           # Keep logs for 90 days
    archive_after_days=30,       # Archive after 30 days
    compress_after_days=7,       # Compress after 7 days
    max_log_size_mb=1000,        # Max log size in MB
    backup_interval_hours=24,    # Backup every 24 hours
)
```

### Storage Locations
- **Archives**: `{BASE_DIR}/archives/audit_logs/`
- **Backups**: `{BASE_DIR}/backups/audit_logs/`

## Data Formats

### Archive Format
Archives are stored as compressed JSON files with one log entry per line:
```json
{
  "id": "log_id",
  "user_id": "user_id",
  "action": "CREATE",
  "resource_type": "user",
  "resource_id": "resource_id",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "before_state": null,
  "after_state": {"email": "user@example.com"},
  "custom_metadata": {"source": "api"},
  "severity": "INFO",
  "tenant_id": "tenant_id",
  "timestamp": "2024-01-01T12:00:00Z",
  "session_id": "session_id"
}
```

### Backup Format
Backups are stored as SQLite databases with the following schema:
```sql
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
);
```

## Security Considerations

1. **Authentication Required**: All data management endpoints require superuser authentication
2. **File Permissions**: Archive and backup files should have appropriate file permissions
3. **Backup Security**: Backup files contain sensitive data and should be stored securely
4. **Network Security**: When uploading backups, ensure secure transmission

## Monitoring and Logging

The system provides comprehensive logging for all operations:
- **Application logs**: All operations are logged with appropriate levels
- **Job status**: Track scheduled job execution and results
- **Storage metrics**: Monitor disk usage and file counts
- **Error handling**: Detailed error messages for troubleshooting

## Best Practices

1. **Regular Monitoring**: Check storage statistics regularly
2. **Test Restores**: Periodically test backup restoration procedures
3. **Policy Review**: Review retention policies based on business requirements
4. **Storage Planning**: Monitor disk usage and plan for growth
5. **Backup Verification**: Verify backup integrity regularly
6. **Documentation**: Document custom policies and procedures

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed (`apscheduler`)
2. **Permission Errors**: Check file permissions for archive and backup directories
3. **Disk Space**: Monitor available disk space for archives and backups
4. **Scheduler Issues**: Check scheduler status and job logs
5. **Backup Failures**: Verify backup file integrity and permissions

### Debug Mode
Enable debug logging for detailed troubleshooting:
```python
import logging
logging.getLogger('app.core.data_management').setLevel(logging.DEBUG)
logging.getLogger('app.core.scheduler').setLevel(logging.DEBUG)
```

## Performance Considerations

1. **Batch Operations**: Large operations are performed in batches
2. **Compression**: Archives are compressed to save space
3. **Indexing**: Database queries use appropriate indexes
4. **Background Processing**: Heavy operations run in background
5. **Resource Management**: Proper cleanup of database connections and file handles 