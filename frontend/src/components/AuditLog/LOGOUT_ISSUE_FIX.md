# Logout Issue Fix

## Vấn đề

Khi thực hiện các action (tạo, sửa, xóa user/tenant), ứng dụng bị logout và redirect về trang login.

## Nguyên nhân

Vấn đề xảy ra do endpoint `GET /audit-logs/` yêu cầu superuser privileges, trong khi endpoint `POST /audit-logs/` cho phép authenticated users. Điều này gây ra xung đột khi:

1. Frontend cố gắng fetch audit logs (GET request)
2. Backend trả về lỗi 403 Forbidden vì user không phải superuser
3. Frontend xử lý lỗi 403 bằng cách logout user

## Giải pháp

### Backend Changes

1. **Modified `GET /audit-logs/` endpoint**:
   - Bỏ dependency `get_current_active_superuser`
   - Thêm `current_user: CurrentUser` parameter
   - Thêm logic để non-superusers chỉ có thể xem audit logs của tenant của họ
   - Thêm validation để đảm bảo security

2. **Security Features**:
   - Non-superusers chỉ có thể xem audit logs từ tenant của họ
   - Superusers có thể xem tất cả audit logs
   - Validation tenant_id để tránh unauthorized access

### Frontend Changes

1. **Added Debug Logging**:
   - Console logs để track audit log creation
   - Error handling với detailed error information
   - Test buttons để debug

2. **Error Handling**:
   - Audit log creation failures không làm break main operations
   - Detailed error logging để debug

## Testing

1. **Test Simple Action**: Button để test action không liên quan đến audit log
2. **Test Audit Log**: Button để test audit log creation
3. **Console Logs**: Detailed logging để track issues

## Security Considerations

1. **Tenant Isolation**: Users chỉ có thể xem audit logs của tenant của họ
2. **User Validation**: Users chỉ có thể tạo audit logs cho actions của họ
3. **Superuser Access**: Superusers vẫn có full access

## Code Changes

### Backend (`backend/app/api/routes/audit_logs.py`)

```python
@router.get(
    "/",
    response_model=AuditLogsPublic,
)
def read_audit_logs(
    session: SessionDep,
    current_user: CurrentUser,  # Added
    skip: int = 0,
    limit: int = 100,
    # ... other parameters
) -> Any:
    """
    Retrieve audit logs with filtering options (authenticated users).
    """
    # For non-superusers, only show logs from their own tenant
    if not current_user.is_superuser:
        statement = statement.where(col(AuditLog.tenant_id) == current_user.tenant_id)
    
    # ... rest of the logic with tenant validation
```

### Frontend (`frontend/src/utils/auditLog.ts`)

```typescript
const logAction = async (data: AuditLogData) => {
  try {
    console.log("Creating audit log:", data)
    // ... audit log creation logic
    console.log("Audit log created successfully:", result)
  } catch (error) {
    console.error("Failed to create audit log:", error)
    // Don't throw error to avoid breaking the main operation
  }
}
```

## Verification

1. Login với user thường (không phải superuser)
2. Thực hiện các action (tạo/sửa/xóa user/tenant)
3. Kiểm tra console logs để đảm bảo audit logs được tạo thành công
4. Kiểm tra audit logs page để đảm bảo logs được hiển thị
5. Đảm bảo không bị logout

## Future Improvements

1. **Better Error Handling**: More specific error messages
2. **Retry Logic**: Retry failed audit log creations
3. **Offline Support**: Queue audit logs when offline
4. **Performance**: Optimize audit log queries 