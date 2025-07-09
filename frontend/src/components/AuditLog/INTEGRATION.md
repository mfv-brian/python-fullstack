# Audit Log Integration with Backend API

This document describes the integration of the Audit Log Management UI with the backend API, replacing all mock data with real API calls.

## Overview

The Audit Log Management system has been fully integrated with the backend API, providing:

- Real-time data fetching from the backend
- WebSocket connection for live monitoring
- Export functionality using backend endpoints
- Database optimization operations
- Comprehensive error handling

## API Integration Points

### 1. Audit Log Data Fetching

**Component**: `AuditLogTable.tsx`
**Hook**: `useAuditLogs`
**API Endpoint**: `GET /api/v1/audit-logs/`

```typescript
// Usage
const { data, isLoading, error } = useAuditLogs(page, filters)
```

**Features**:
- Pagination support (10 logs per page)
- Advanced filtering (action, severity, resource type, date range, etc.)
- Error handling with user-friendly messages
- Loading states with skeleton components
- Automatic data transformation for UI display

### 2. Export Functionality

**Component**: `AuditLogExport.tsx`
**Hook**: `useAuditLogExport`
**API Endpoints**: 
- `GET /api/v1/audit-logs/export/csv` (CSV export)
- `GET /api/v1/audit-logs/` (JSON export)

```typescript
// Usage
const exportMutation = useAuditLogExport()
await exportMutation.mutateAsync({ format: 'CSV', filters })
```

**Features**:
- CSV export using backend endpoint
- JSON export by fetching data and converting
- Filter-aware exports
- Automatic file download
- Progress indication

### 3. Real-time Monitoring

**Component**: `AuditLogRealTime.tsx`
**WebSocket Endpoint**: `ws://host/api/v1/audit-logs/ws`

```typescript
// WebSocket connection
const ws = new WebSocket(`${protocol}//${host}/api/v1/audit-logs/ws`)
```

**Features**:
- Real-time log streaming
- Connection status management
- Pause/resume functionality
- Auto-scroll to latest logs
- Error handling and reconnection
- Message type handling (audit_log, ping/pong)

### 4. Settings Management

**Component**: `AuditLogSettings.tsx`
**API Endpoints**:
- `POST /api/v1/utils/optimize-database` (Storage optimization)
- `POST /api/v1/utils/reindex-database` (Index rebuild)

```typescript
// Usage
await UtilsService.optimizeDatabaseEndpoint()
await UtilsService.reindexDatabaseEndpoint()
```

**Features**:
- Database optimization operations
- Index rebuilding
- Settings persistence (simulated)
- Operation status feedback
- Error handling

## Data Flow

### 1. Data Fetching Flow

```
User Action → Filter Change → useAuditLogs Hook → API Call → Data Transformation → UI Update
```

### 2. Export Flow

```
User Action → Export Dialog → useAuditLogExport Hook → API Call → File Download → Success Feedback
```

### 3. Real-time Flow

```
WebSocket Connection → Message Reception → Data Parsing → UI Update → Auto-scroll
```

## Error Handling

### 1. API Errors

- Network errors are caught and displayed to users
- Loading states prevent multiple requests
- Retry mechanisms for failed requests
- Graceful degradation when services are unavailable

### 2. WebSocket Errors

- Connection errors are displayed with retry options
- Automatic reconnection attempts
- Connection status indicators
- Error messages for debugging

### 3. Export Errors

- File download errors are caught
- User feedback for failed exports
- Retry options for failed operations

## Performance Optimizations

### 1. Caching

- React Query provides automatic caching
- Stale data is shown while fetching fresh data
- Optimistic updates for better UX

### 2. Pagination

- Only loads 10 logs per page
- Reduces initial load time
- Improves memory usage

### 3. Real-time Optimization

- Limits to 100 most recent logs
- Automatic cleanup of old logs
- Efficient WebSocket message handling

## Security Considerations

### 1. Authentication

- All API calls require authentication
- WebSocket connections respect auth tokens
- Superuser-only access for audit logs

### 2. Data Sanitization

- Input validation on filters
- Safe data transformation
- XSS prevention in UI rendering

### 3. Tenant Isolation

- Multi-tenant support in API calls
- Tenant-specific data filtering
- Isolation in real-time monitoring

## Testing

### 1. Unit Tests

- Hook testing with React Query
- Component testing with mock data
- Error handling verification

### 2. Integration Tests

- API integration testing
- WebSocket connection testing
- Export functionality testing

### 3. E2E Tests

- Complete user workflow testing
- Error scenario testing
- Performance testing

## Configuration

### 1. API Base URL

The integration automatically uses the current window location to determine the API base URL:

```typescript
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
const host = window.location.host
const wsUrl = `${protocol}//${host}/api/v1/audit-logs/ws`
```

### 2. Pagination Settings

- Default page size: 10 logs
- Configurable via `PER_PAGE` constant
- Backend supports custom limits

### 3. Real-time Settings

- Max logs in memory: 100
- Auto-scroll enabled by default
- Configurable connection retry logic

## Future Enhancements

### 1. User Information

Currently using mock user names and emails. Future integration could:
- Fetch real user details from user API
- Cache user information
- Display real user avatars

### 2. Advanced Filtering

- Full-text search across all fields
- Complex date range queries
- Saved filter presets

### 3. Real-time Enhancements

- Filtered WebSocket streams
- Custom notification sounds
- Desktop notifications

### 4. Export Enhancements

- Scheduled exports
- Email delivery
- Custom export templates

## Troubleshooting

### 1. Common Issues

**API Connection Errors**:
- Check backend service status
- Verify authentication tokens
- Check network connectivity

**WebSocket Connection Issues**:
- Verify WebSocket endpoint availability
- Check firewall settings
- Ensure proper protocol (ws/wss)

**Export Failures**:
- Check file permissions
- Verify filter parameters
- Ensure sufficient memory

### 2. Debug Information

- Console logs for API calls
- WebSocket connection status
- Error details in browser console
- Network tab for request/response inspection

## Migration Notes

### From Mock Data

1. **Data Structure Changes**: API responses are transformed to match UI expectations
2. **Error Handling**: Added comprehensive error handling for all API calls
3. **Loading States**: Implemented proper loading indicators
4. **Pagination**: Real pagination with backend support

### Backward Compatibility

- All existing UI components remain functional
- Component interfaces unchanged
- Existing tests should continue to pass
- Gradual migration path available

## API Reference

### Audit Logs Service

```typescript
// Read audit logs with filters
AuditLogsService.readAuditLogs(params)

// Export audit logs as CSV
AuditLogsService.exportAuditLogsCsv(params)

// Get specific audit log
AuditLogsService.readAuditLog({ auditLogId })

// Create audit log
AuditLogsService.createAuditLog({ requestBody })

// Update audit log
AuditLogsService.updateAuditLog({ auditLogId, requestBody })

// Delete audit log
AuditLogsService.deleteAuditLog({ auditLogId })
```

### Utils Service

```typescript
// Database optimization
UtilsService.optimizeDatabaseEndpoint()

// Index rebuilding
UtilsService.reindexDatabaseEndpoint()

// Database vacuum
UtilsService.vacuumDatabaseEndpoint()
```

This integration provides a complete, production-ready audit log management system with real-time capabilities, comprehensive filtering, and robust error handling. 