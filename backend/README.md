# FastAPI Backend - Multi-Tenant Application

A high-performance, multi-tenant FastAPI backend with comprehensive optimization strategies for handling high-volume writes and complex queries.

## 🚀 Features

### Multi-Tenant Architecture
- **Tenant Isolation**: Complete data separation between tenants
- **Role-Based Access Control**: Admin, Auditor, and User roles
- **Tenant Configuration**: Customizable limits and features per tenant
- **Audit Logging**: Comprehensive activity tracking per tenant

### Database Optimization
- **Advanced Indexing**: Composite, partial, and full-text search indexes
- **Data Partitioning**: Time-based and tenant-based partitioning
- **Connection Pooling**: Optimized for high concurrency
- **Performance Monitoring**: Real-time metrics and statistics

### High-Performance Features
- **Query Optimization**: Tenant-aware query patterns
- **Caching Strategy**: Efficient data retrieval
- **Storage Management**: Automatic cleanup and maintenance
- **Scalability**: Designed for horizontal scaling

## 🏗️ Architecture

### Database Schema
```
Tenant (1) ←→ (N) User
Tenant (1) ←→ (N) Item  
Tenant (1) ←→ (N) AuditLog
Tenant (1) ←→ (N) TenantMetrics
```

### Key Models
- **Tenant**: Multi-tenant configuration and limits
- **User**: Role-based user management with tenant isolation
- **Item**: Tenant-specific data with ownership tracking
- **AuditLog**: Comprehensive activity logging with partitioning
- **TenantMetrics**: Performance monitoring and usage tracking

## 📊 Performance Optimizations

### Indexing Strategy
```sql
-- Composite indexes for tenant-based queries
idx_user_tenant_email_active ON user (tenant_id, email, is_active)
idx_item_tenant_created_desc ON item (tenant_id, created_at DESC)
idx_audit_tenant_timestamp ON audit_log (tenant_id, timestamp)

-- Partial indexes for performance
idx_user_active_only ON user (tenant_id, email) WHERE is_active = true
idx_audit_recent ON audit_log (tenant_id, timestamp) WHERE timestamp > NOW() - INTERVAL '30 days'
```

### Data Partitioning
- **Audit Logs**: Monthly partitions for efficient querying
- **Metrics**: Date-based partitioning for historical data
- **Automatic Management**: Self-maintaining partition strategy

### Connection Pooling
```python
pool_size=20, max_overflow=30, pool_pre_ping=True
pool_recycle=3600, pool_timeout=30
```

## 🔧 Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --reload
```

### Environment Variables
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis
```

## 📈 API Endpoints

### Authentication
```
POST /login/access-token     # User login
GET  /login/test-token       # Test authentication
POST /login/recover-password # Password recovery
POST /login/reset-password   # Password reset
```

### User Management
```
GET    /users/               # List users (admin only)
POST   /users/               # Create user (admin only)
GET    /users/me             # Get current user
PATCH  /users/me             # Update current user
POST   /users/signup         # User registration
```

### Tenant Management
```
GET    /tenants/             # List tenants
POST   /tenants/             # Create tenant
GET    /tenants/{id}         # Get tenant details
PATCH  /tenants/{id}         # Update tenant
DELETE /tenants/{id}         # Delete tenant
```

### Item Management
```
GET    /items/               # List items (tenant-scoped)
POST   /items/               # Create item
GET    /items/{id}           # Get item details
PATCH  /items/{id}           # Update item
DELETE /items/{id}           # Delete item
```

### Audit Logs
```
GET    /audit-logs/          # List audit logs (tenant-scoped)
POST   /audit-logs/          # Create audit log
GET    /audit-logs/{id}      # Get audit log details
PATCH  /audit-logs/{id}      # Update audit log
DELETE /audit-logs/{id}      # Delete audit log
GET    /audit-logs/export/csv # Export audit logs
```

### Database Management
```
GET    /utils/db/health                    # Database health check
GET    /utils/db/stats                     # Database statistics
POST   /utils/db/optimize                  # Run optimization tasks
POST   /utils/db/vacuum                    # Run VACUUM
POST   /utils/db/reindex                   # Reindex database
GET    /utils/db/tenant/{id}/performance   # Tenant performance report
```

## 🔍 Database Optimization

### Automatic Optimization
```python
from app.core.optimization import optimize_database

# Run comprehensive optimization
results = optimize_database()
```

### Manual Optimization
```python
from app.core.optimization import DatabaseOptimizer

with Session(engine) as session:
    optimizer = DatabaseOptimizer(session)
    
    # Create indexes
    optimizer.create_tenant_based_indexes()
    optimizer.create_partial_indexes()
    
    # Analyze tables
    optimizer.analyze_tables()
    
    # Vacuum tables
    optimizer.vacuum_tables()
```

### Performance Monitoring
```python
from app.core.db import get_db_stats, check_db_health

# Check database health
health = check_db_health()

# Get detailed statistics
stats = get_db_stats()
```

## 🛡️ Security Features

### Multi-Tenant Security
- **Data Isolation**: Complete separation between tenants
- **Row-Level Security**: Database-level tenant filtering
- **API-Level Validation**: Request-level tenant verification

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication
- **Role-Based Access**: Admin, Auditor, User permissions
- **Password Security**: Bcrypt hashing with salt

### Audit Trail
- **Comprehensive Logging**: All user actions tracked
- **Tenant-Scoped**: Audit logs isolated per tenant
- **Performance Optimized**: Partitioned for efficient querying

## 📊 Monitoring & Analytics

### Tenant Metrics
- User count and activity
- Item count and storage usage
- Audit log volume
- Performance indicators

### Database Performance
- Query response times
- Index usage statistics
- Connection pool utilization
- Table growth monitoring

### Health Checks
- Database connectivity
- API endpoint availability
- System resource usage
- Error rate monitoring

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Production Considerations
- **Environment Variables**: Secure configuration management
- **Database Backups**: Regular automated backups
- **Monitoring**: Application and database monitoring
- **Scaling**: Horizontal scaling with load balancers

## 📚 Documentation

### API Documentation
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI Schema**: Available at `/openapi.json`

### Database Schema
- **Migration Files**: `app/alembic/versions/`
- **Model Definitions**: `app/models.py`
- **Schema Documentation**: `MULTI_TENANT_SCHEMA.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API documentation at `/docs`

---

**Built with FastAPI, SQLModel, and PostgreSQL for high-performance multi-tenant applications.**
