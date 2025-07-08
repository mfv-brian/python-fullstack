# Audit Log Management UI

This directory contains the complete UI implementation for the Audit Log Management system. The system provides comprehensive audit logging capabilities with advanced search, real-time monitoring, export functionality, and data management features.

## Components Overview

### 1. AuditLogManagement.tsx
**Main container component with tabbed interface:**
- **Audit Logs Tab**: Historical log browsing with advanced filters
- **Real-time Monitor Tab**: Live log streaming with WebSocket simulation
- **Settings Tab**: Data retention, archival, and backup configuration

### 2. AuditLogTable.tsx
**Primary log viewing interface with:**
- Paginated table display (10 logs per page)
- Advanced filtering integration
- Export functionality
- Detailed log entry modal
- Responsive design for mobile/desktop
- Mock data with realistic audit log entries

### 3. AuditLogFilters.tsx
**Comprehensive search and filtering system:**
- **Quick Search**: Full-text search across all log fields
- **Advanced Filters** (collapsible):
  - Date/time range picker (start/end dates)
  - Action type filter (CREATE, UPDATE, DELETE, VIEW, LOGIN, LOGOUT, EXPORT, IMPORT)
  - Resource type filter (user, item, order, product, setting)
  - Severity level filter (INFO, WARNING, ERROR, CRITICAL)
  - User ID search
  - Tenant ID filter for multi-tenant support
- Real-time filter application
- Filter reset functionality

### 4. AuditLogDetails.tsx
**Detailed log entry modal with structured display:**
- **Basic Information**: Timestamp, Log ID, Action, Severity
- **User Information**: Name, Email, User ID, Session ID
- **Resource Information**: Type, Resource ID
- **Technical Information**: IP Address, User Agent, Tenant ID
- **Message**: Descriptive log message
- **State Changes**: Before/After state comparison (JSON formatted)
- **Metadata**: Additional custom fields (JSON formatted)
- Color-coded badges for severity and actions

### 5. AuditLogExport.tsx
**Flexible export functionality:**
- **Format Selection**: JSON or CSV export
- **Filter Integration**: Exports respect current filter criteria
- **Format Descriptions**: User-friendly explanations
- **Active Filter Summary**: Shows what will be exported
- **Download Implementation**: Browser-based file download
- Progress indication during export

### 6. AuditLogRealTime.tsx
**Live log monitoring with:**
- **WebSocket Simulation**: Real-time log generation (2-5 second intervals)
- **Connection Management**: Connect/Disconnect controls
- **Pause/Resume**: Temporary monitoring suspension
- **Auto-scroll**: Automatic scrolling to latest logs
- **Log Limit**: Maintains last 100 logs for performance
- **Live Indicators**: Visual status indicators
- **Clear Functionality**: Manual log clearing
- **Responsive Feed**: Mobile-optimized log display

### 7. AuditLogSettings.tsx
**Comprehensive data management configuration:**

#### Data Retention
- Configurable retention period (1-3650 days)
- Warning notifications for data deletion
- Automatic cleanup scheduling

#### Data Archival
- Enable/disable automatic archival
- Configurable archival threshold (days)
- Cold storage migration
- Manual archival trigger

#### Storage Optimization
- Data compression toggle (up to 70% space savings)
- Performance impact information

#### Backup & Recovery
- Automated backup scheduling (Daily/Weekly/Monthly)
- Geographic distribution information
- Encryption details

#### Data Management Actions
- **Cleanup Old Logs**: Manual retention enforcement
- **Optimize Storage**: Storage defragmentation
- **Rebuild Indexes**: Performance optimization
- Safety warnings for maintenance operations

## Data Structure

### AuditLogEntry Type
```typescript
{
  id: string                    // Unique log identifier
  user_id?: string             // User who performed action
  session_id?: string          // Session identifier
  action: AuditLogAction       // Action type enum
  resource_type: string        // Type of resource affected
  resource_id?: string         // Specific resource identifier
  timestamp: string            // ISO timestamp with timezone
  ip_address?: string          // Client IP address
  user_agent?: string          // Browser/client information
  before_state?: object        // State before change
  after_state?: object         // State after change
  metadata?: object            // Custom additional data
  severity: AuditLogSeverity   // Log severity level
  tenant_id?: string           // Multi-tenant identifier
  message?: string             // Human-readable description
  user_email?: string          // User email for display
  user_name?: string           // User name for display
}
```

### Supported Actions
- **CREATE**: Resource creation
- **UPDATE**: Resource modification
- **DELETE**: Resource deletion
- **VIEW**: Resource access/viewing
- **LOGIN**: User authentication
- **LOGOUT**: User session termination
- **EXPORT**: Data export operations
- **IMPORT**: Data import operations

### Severity Levels
- **INFO**: Normal operations (blue)
- **WARNING**: Attention required (yellow)
- **ERROR**: Error conditions (red)
- **CRITICAL**: Critical failures (purple)

## Features Implemented

### ✅ Search and Retrieval
- Advanced multi-field filtering
- Full-text search capability
- Date range filtering
- Pagination for large datasets
- Export functionality (JSON/CSV)
- Real-time log streaming
- Complete tenant isolation

### ✅ Data Management
- Configurable retention policies
- Automated data archival
- Data compression options
- Automated backup procedures
- Manual maintenance operations

### ✅ User Experience
- Responsive design (mobile/desktop)
- Intuitive tabbed interface
- Color-coded severity indicators
- Detailed log inspection
- Real-time status updates
- Progress indicators
- Comprehensive tooltips and help text

### ✅ Technical Features
- Mock WebSocket implementation
- Browser-based file downloads
- Local storage simulation
- Performance-optimized rendering
- Error handling and loading states
- TypeScript type safety

## Integration

### Routing
- Route: `/audit-logs` (superuser only)
- Integrated with existing router configuration
- Added to sidebar navigation

### Permissions
- Restricted to superuser accounts only
- Integrated with existing authentication system
- Respects current user permissions

### Styling
- Consistent with existing Chakra UI theme
- Responsive design patterns
- Accessible color schemes
- Loading and error states

## Mock Data
The implementation includes realistic mock data for demonstration:
- Varied action types and severities
- Realistic timestamps and user information
- Sample before/after state changes
- Multi-tenant scenarios
- IP addresses and user agents

## Future API Integration
The components are designed for easy API integration:
- Standardized data types
- Consistent error handling
- Loading state management
- Filter parameter serialization
- Export endpoint preparation
- WebSocket connection framework

## Usage

### For Superusers
1. Navigate to "Audit Logs" in the sidebar
2. Use the Audit Logs tab to browse historical data
3. Apply filters to narrow down results
4. Click on log entries to view detailed information
5. Export filtered data using the export functionality
6. Monitor real-time activity in the Real-time Monitor tab
7. Configure system settings in the Settings tab

### For Developers
- All components accept props for customization
- Types are exported for API integration
- Mock data can be easily replaced with API calls
- WebSocket connection can be substituted with real implementation
- Settings can be connected to backend configuration endpoints 