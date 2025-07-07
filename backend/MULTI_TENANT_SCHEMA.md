# Multi-Tenant Schema Implementation

## Overview

This document describes the comprehensive multi-tenant schema implementation with optimization strategies for high-volume writes and complex queries.

## Schema Design

### 1. Multi-Tenant Architecture

#### Tenant Model
```python
class Tenant(TenantBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(min_length=1, max_length=255, index=True)
    code: str = Field(unique=True, index=True, min_length=1, max_length=50)
    status: TenantStatus = Field(default=TenantStatus.ACTIVE, index=True)
    max_users: int = Field(default=100)
    max_storage_gb: int = Field(default=10)
    features_enabled: dict = Field(default_factory=dict, sa_type=JSON)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

#### Tenant-Aware Models
All models include `tenant_id` for proper isolation:
- User
- Item
- AuditLog
- TenantMetrics

### 2. Indexing Strategy

#### Composite Indexes
```sql
-- User indexes
CREATE INDEX idx_user_tenant_email_active ON user (tenant_id, email, is_active);
CREATE INDEX idx_user_tenant_role_active ON user (tenant_id, role, is_active);
CREATE INDEX idx_user_tenant_last_login ON user (tenant_id, last_login_at DESC);

-- Item indexes
CREATE INDEX idx_item_tenant_created_desc ON item (tenant_id, created_at DESC);
CREATE INDEX idx_item_tenant_owner_created ON item (tenant_id, owner_id, created_at DESC);
CREATE INDEX idx_item_title_tenant ON item (title, tenant_id);

-- Audit log indexes
CREATE INDEX idx_audit_tenant_timestamp ON audit_log (tenant_id, timestamp);
CREATE INDEX idx_audit_tenant_action ON audit_log (tenant_id, action);
CREATE INDEX idx_audit_tenant_severity ON audit_log (tenant_id, severity);
```

#### Partial Indexes
```sql
-- Only active users
CREATE INDEX idx_user_active_only ON user (tenant_id, email) WHERE is_active = true;

-- Recent audit logs (last 30 days)
CREATE INDEX idx_audit_recent ON audit_log (tenant_id, timestamp) 
WHERE timestamp > NOW() - INTERVAL '30 days';

-- High severity audit logs
CREATE INDEX idx_audit_high_severity ON audit_log (tenant_id, timestamp) 
WHERE severity IN ('ERROR', 'CRITICAL');
```

#### Full-Text Search Indexes
```sql
-- Item title search
CREATE INDEX idx_item_tenant_title_search ON item (tenant_id, title) 
USING gin(to_tsvector('english', title));

-- Item description search
CREATE INDEX idx_item_description_search ON item 
USING gin(to_tsvector('english', description));

-- Audit metadata search
CREATE INDEX idx_audit_metadata_search ON audit_log USING gin(custom_metadata);
```

### 3. Data Partitioning

#### Time-Based Partitioning
```sql
-- Audit log partitioning by month
CREATE TABLE audit_log_partitioned (
    LIKE audit_log INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Monthly partitions
CREATE TABLE audit_log_2024_01 PARTITION OF audit_log_partitioned
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

#### Tenant-Based Partitioning
```sql
-- Tenant metrics partitioning by date
CREATE TABLE tenant_metrics_partitioned (
    LIKE tenant_metrics INCLUDING ALL
) PARTITION BY RANGE (date);
```

### 4. Connection Pooling

#### Configuration
```python
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    poolclass=QueuePool,
    pool_size=20,           # Number of connections to maintain
    max_overflow=30,        # Additional connections when pool is full
    pool_pre_ping=True,     # Validate connections before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_timeout=30,        # Timeout for getting connection from pool
)
```

#### PostgreSQL Optimizations
```python
connect_args={
    "application_name": "fastapi_app",
    "options": "-c timezone=utc -c statement_timeout=30000",  # 30s timeout
}
```

### 5. Performance Monitoring

#### Tenant Metrics
```python
class TenantMetrics(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", nullable=False, index=True)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    user_count: int = Field(default=0)
    item_count: int = Field(default=0)
    audit_log_count: int = Field(default=0)
    storage_used_mb: float = Field(default=0.0)
    active_users: int = Field(default=0)
```

#### Database Statistics
- Connection pool statistics
- Table sizes and row counts
- Index usage statistics
- Query performance metrics

### 6. Optimization Utilities

#### Database Optimizer Class
```python
class DatabaseOptimizer:
    def create_partitioned_tables(self) -> bool
    def create_tenant_based_indexes(self) -> bool
    def create_partial_indexes(self) -> bool
    def analyze_tables(self) -> bool
    def vacuum_tables(self) -> bool
    def get_table_statistics(self) -> Dict[str, Any]
    def optimize_tenant_queries(self, tenant_id: str) -> Dict[str, Any]
    def create_tenant_metrics(self) -> bool
```

#### API Endpoints
```
GET  /utils/db/health                    # Database health check
GET  /utils/db/stats                     # Database statistics
POST /utils/db/optimize                  # Run optimization tasks
POST /utils/db/vacuum                    # Run VACUUM
POST /utils/db/reindex                   # Reindex database
GET  /utils/db/tenant/{id}/performance   # Tenant performance report
```

## Usage Examples

### 1. Tenant Isolation
```python
# All queries automatically filter by tenant_id
def get_tenant_users(tenant_id: str, session: Session):
    return session.exec(
        select(User).where(User.tenant_id == tenant_id)
    ).all()
```

### 2. Performance Monitoring
```python
# Get tenant performance report
report = get_tenant_performance_report(tenant_id)
# Returns: user_count, item_count, recent_audits, storage_mb
```

### 3. Database Optimization
```python
# Run full optimization
results = optimize_database()
# Creates indexes, partitions, analyzes tables, updates metrics
```

## Best Practices

### 1. Query Optimization
- Always include `tenant_id` in WHERE clauses
- Use composite indexes for common query patterns
- Leverage partial indexes for filtered queries
- Use full-text search for text-based queries

### 2. Data Management
- Regular VACUUM and ANALYZE operations
- Monitor table sizes and growth
- Archive old audit logs to partitioned tables
- Update tenant metrics regularly

### 3. Connection Management
- Use connection pooling for concurrent requests
- Monitor pool statistics
- Set appropriate timeouts
- Recycle connections periodically

### 4. Monitoring
- Track query performance
- Monitor index usage
- Watch for slow queries
- Alert on connection pool exhaustion

## Migration Strategy

### 1. Schema Migration
```bash
# Generate migration
alembic revision --autogenerate -m "enhance_multi_tenant_schema"

# Apply migration
alembic upgrade head
```

### 2. Data Migration
- Existing data gets default tenant_id
- Indexes created concurrently to avoid locks
- Partitioned tables created separately

### 3. Performance Tuning
- Run optimization utilities after migration
- Monitor query performance
- Adjust indexes based on usage patterns

## Security Considerations

### 1. Tenant Isolation
- All queries must include tenant_id filter
- Row-level security (RLS) can be implemented
- Audit logging for all tenant operations

### 2. Access Control
- Role-based access control (RBAC)
- Tenant-specific permissions
- API-level tenant validation

### 3. Data Protection
- Encrypted connections
- Secure connection pooling
- Regular security audits

## Monitoring and Alerting

### 1. Key Metrics
- Query response times
- Connection pool utilization
- Table growth rates
- Index usage statistics

### 2. Alerts
- Slow query detection
- Connection pool exhaustion
- Storage usage thresholds
- Tenant performance degradation

### 3. Dashboards
- Database performance overview
- Tenant-specific metrics
- Query performance trends
- Resource utilization

## Conclusion

This multi-tenant schema implementation provides:
- Proper tenant isolation
- Optimized query performance
- Scalable architecture
- Comprehensive monitoring
- Easy maintenance and optimization

The design supports high-volume writes and complex queries while maintaining data integrity and performance across multiple tenants. 