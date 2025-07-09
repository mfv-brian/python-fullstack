import asyncio
import csv
import io
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from sqlmodel import col, func, select
from starlette.responses import StreamingResponse

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    AuditAction,
    AuditLog,
    AuditLogCreate,
    AuditLogExport,
    AuditLogPublic,
    AuditLogsPublic,
    AuditLogUpdate,
    AuditSeverity,
    Message,
)

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get(
    "/",
    response_model=AuditLogsPublic,
)
def read_audit_logs(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    user_id: uuid.UUID | None = Query(None, description="Filter by user ID"),
    action: AuditAction | None = Query(None, description="Filter by action type"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    resource_id: str | None = Query(None, description="Filter by resource ID"),
    severity: AuditSeverity | None = Query(None, description="Filter by severity level"),
    tenant_id: uuid.UUID | None = Query(None, description="Filter by tenant ID"),
    start_date: datetime | None = Query(None, description="Start date for filtering"),
    end_date: datetime | None = Query(None, description="End date for filtering"),
) -> Any:
    """
    Retrieve audit logs with filtering options (authenticated users).
    """
    # Build the base query
    statement = select(AuditLog)
    
    # For non-superusers, only show logs from their own tenant
    if not current_user.is_superuser:
        statement = statement.where(col(AuditLog.tenant_id) == current_user.tenant_id)
    
    # Add filters
    if user_id:
        statement = statement.where(col(AuditLog.user_id) == user_id)
    if action:
        statement = statement.where(col(AuditLog.action) == action)
    if resource_type:
        statement = statement.where(col(AuditLog.resource_type) == resource_type)
    if resource_id:
        statement = statement.where(col(AuditLog.resource_id) == resource_id)
    if severity:
        statement = statement.where(col(AuditLog.severity) == severity)
    if tenant_id:
        # For non-superusers, ensure they can only filter by their own tenant
        if not current_user.is_superuser and tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view audit logs from your own tenant",
            )
        statement = statement.where(col(AuditLog.tenant_id) == tenant_id)
    if start_date:
        statement = statement.where(col(AuditLog.timestamp) >= start_date)
    if end_date:
        statement = statement.where(col(AuditLog.timestamp) <= end_date)
    
    # Order by timestamp descending (newest first)
    statement = statement.order_by(col(AuditLog.timestamp).desc())
    
    # Get count
    count_statement = select(func.count()).select_from(AuditLog)
    if not current_user.is_superuser:
        count_statement = count_statement.where(col(AuditLog.tenant_id) == current_user.tenant_id)
    if user_id:
        count_statement = count_statement.where(col(AuditLog.user_id) == user_id)
    if action:
        count_statement = count_statement.where(col(AuditLog.action) == action)
    if resource_type:
        count_statement = count_statement.where(col(AuditLog.resource_type) == resource_type)
    if resource_id:
        count_statement = count_statement.where(col(AuditLog.resource_id) == resource_id)
    if severity:
        count_statement = count_statement.where(col(AuditLog.severity) == severity)
    if tenant_id:
        if not current_user.is_superuser and tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view audit logs from your own tenant",
            )
        count_statement = count_statement.where(col(AuditLog.tenant_id) == tenant_id)
    if start_date:
        count_statement = count_statement.where(col(AuditLog.timestamp) >= start_date)
    if end_date:
        count_statement = count_statement.where(col(AuditLog.timestamp) <= end_date)
    
    count = session.exec(count_statement).one()
    
    # Get paginated results
    audit_logs = session.exec(statement.offset(skip).limit(limit)).all()
    
    return AuditLogsPublic(
        data=[AuditLogPublic.model_validate(log) for log in audit_logs],
        count=count
    )


@router.post(
    "/",
    response_model=AuditLogPublic,
)
def create_audit_log(
    *,
    session: SessionDep,
    request: Request,
    audit_log_in: AuditLogCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Create new audit log entry (authenticated users).
    """
    # Ensure the user can only create audit logs for their own actions
    if str(audit_log_in.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You can only create audit logs for your own actions",
        )
    
    # Ensure the tenant_id matches the current user's tenant
    if str(audit_log_in.tenant_id) != str(current_user.tenant_id):
        raise HTTPException(
            status_code=403,
            detail="You can only create audit logs for your own tenant",
        )
    
    # Get client IP and user agent
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Update audit log with client information
    audit_log_data = audit_log_in.model_dump()
    if not audit_log_data.get("ip_address") and client_ip:
        audit_log_data["ip_address"] = client_ip
    if not audit_log_data.get("user_agent") and user_agent:
        audit_log_data["user_agent"] = user_agent
    
    audit_log = AuditLog.model_validate(audit_log_data)
    session.add(audit_log)
    session.commit()
    session.refresh(audit_log)
    
    return AuditLogPublic.model_validate(audit_log)


@router.get("/{audit_log_id}", response_model=AuditLogPublic)
def read_audit_log(
    audit_log_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get a specific audit log by id.
    """
    audit_log = session.get(AuditLog, audit_log_id)
    if not audit_log:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found",
        )
    
    return AuditLogPublic.model_validate(audit_log)


@router.patch(
    "/{audit_log_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=AuditLogPublic,
)
def update_audit_log(
    *,
    session: SessionDep,
    audit_log_id: uuid.UUID,
    audit_log_in: AuditLogUpdate,
) -> Any:
    """
    Update an audit log entry.
    """
    audit_log = session.get(AuditLog, audit_log_id)
    if not audit_log:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found",
        )
    
    update_data = audit_log_in.model_dump(exclude_unset=True)
    if update_data:
        audit_log.sqlmodel_update(update_data)
        session.add(audit_log)
        session.commit()
        session.refresh(audit_log)
    
    return AuditLogPublic.model_validate(audit_log)


@router.delete(
    "/{audit_log_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_audit_log(
    *,
    session: SessionDep,
    audit_log_id: uuid.UUID,
) -> Any:
    """
    Delete an audit log entry.
    """
    audit_log = session.get(AuditLog, audit_log_id)
    if not audit_log:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found",
        )
    
    session.delete(audit_log)
    session.commit()
    
    return Message(message="Audit log deleted successfully")


@router.get(
    "/export/csv",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=AuditLogExport,
)
def export_audit_logs_csv(
    session: SessionDep,
    user_id: uuid.UUID | None = Query(None, description="Filter by user ID"),
    action: AuditAction | None = Query(None, description="Filter by action type"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    resource_id: str | None = Query(None, description="Filter by resource ID"),
    severity: AuditSeverity | None = Query(None, description="Filter by severity level"),
    tenant_id: uuid.UUID | None = Query(None, description="Filter by tenant ID"),
    start_date: datetime | None = Query(None, description="Start date for filtering"),
    end_date: datetime | None = Query(None, description="End date for filtering"),
) -> Any:
    """
    Export audit logs to CSV format.
    """
    # Build the query (same as read_audit_logs but without pagination)
    statement = select(AuditLog)
    
    if user_id:
        statement = statement.where(col(AuditLog.user_id) == user_id)
    if action:
        statement = statement.where(col(AuditLog.action) == action)
    if resource_type:
        statement = statement.where(col(AuditLog.resource_type) == resource_type)
    if resource_id:
        statement = statement.where(col(AuditLog.resource_id) == resource_id)
    if severity:
        statement = statement.where(col(AuditLog.severity) == severity)
    if tenant_id:
        statement = statement.where(col(AuditLog.tenant_id) == tenant_id)
    if start_date:
        statement = statement.where(col(AuditLog.timestamp) >= start_date)
    if end_date:
        statement = statement.where(col(AuditLog.timestamp) <= end_date)
    
    statement = statement.order_by(col(AuditLog.timestamp).desc())
    
    audit_logs = session.exec(statement).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "ID", "Timestamp", "User ID", "Action", "Resource Type", "Resource ID",
        "IP Address", "User Agent", "Severity", "Tenant ID", "Session ID",
        "Before State", "After State", "Custom Metadata"
    ])
    
    # Write data
    for log in audit_logs:
        writer.writerow([
            str(log.id),
            log.timestamp.isoformat(),
            str(log.user_id),
            log.action,
            log.resource_type,
            log.resource_id,
            log.ip_address or "",
            log.user_agent or "",
            log.severity,
            str(log.tenant_id) if log.tenant_id else "",
            log.session_id or "",
            str(log.before_state) if log.before_state else "",
            str(log.after_state) if log.after_state else "",
            str(log.custom_metadata) if log.custom_metadata else "",
        ])
    
    csv_data = output.getvalue()
    output.close()
    
    # Generate filename with timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"audit_logs_{timestamp}.csv"
    
    return AuditLogExport(csv_data=csv_data, filename=filename)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audit log monitoring.
    """
    await websocket.accept()
    try:
        while True:
            # Keep connection alive and send periodic updates
            # In a real implementation, you might want to use Redis pub/sub
            # or a message queue for real-time updates
            await websocket.send_text("ping")
            await asyncio.sleep(30)  # Send ping every 30 seconds
    except WebSocketDisconnect:
        pass


# Utility function to create audit log entries
def create_audit_log_entry(
    session: SessionDep,
    user_id: uuid.UUID,
    action: AuditAction,
    resource_type: str,
    resource_id: str,
    request: Request,
    before_state: dict | None = None,
    after_state: dict | None = None,
    metadata: dict | None = None,
    severity: AuditSeverity = AuditSeverity.INFO,
    tenant_id: uuid.UUID | None = None,
    session_id: str | None = None,
) -> AuditLog:
    """
    Utility function to create audit log entries from other parts of the application.
    """
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=client_ip,
        user_agent=user_agent,
        before_state=before_state,
        after_state=after_state,
        custom_metadata=metadata,
        severity=severity,
        tenant_id=tenant_id,
        session_id=session_id,
    )
    
    session.add(audit_log)
    session.commit()
    session.refresh(audit_log)
    
    return audit_log 