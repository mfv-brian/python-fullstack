from sqlmodel import Session, create_engine, select
from sqlalchemy import event, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
from contextlib import contextmanager
from typing import Generator, Optional
import logging

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, Tenant, UserRole

# Configure logging
logger = logging.getLogger(__name__)

# Enhanced engine with connection pooling and optimization
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    # Connection pooling configuration
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections when pool is full
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Timeout for getting connection from pool
    
    # Performance optimizations
    echo=settings.SQL_ECHO,  # Log SQL queries in development
    echo_pool=settings.SQL_ECHO,  # Log pool events in development
    
    # PostgreSQL specific optimizations
    connect_args={
        "application_name": "fastapi_app",
        "options": "-c timezone=utc -c statement_timeout=30000",  # 30s timeout
    }
)

# Database event listeners for performance monitoring
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(logger.info(f"Executing: {statement[:50]}..."))

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = logger.info(f"Total Time: {statement[:50]}...")

# Multi-tenant session management
class TenantSession:
    def __init__(self, tenant_id: Optional[str] = None):
        self.tenant_id = tenant_id
    
    def __enter__(self):
        self.session = Session(engine)
        if self.tenant_id:
            # Set tenant context for the session
            self.session.execute(text(f"SET app.tenant_id = '{self.tenant_id}'"))
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

@contextmanager
def get_session(tenant_id: Optional[str] = None) -> Generator[Session, None, None]:
    """Get a database session with optional tenant context."""
    session = Session(engine)
    try:
        if tenant_id:
            # Set tenant context for the session
            session.execute(text(f"SET app.tenant_id = '{tenant_id}'"))
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def get_tenant_session(tenant_id: str) -> Session:
    """Get a database session with tenant context."""
    session = Session(engine)
    session.execute(text(f"SET app.tenant_id = '{tenant_id}'"))
    return session

# Database initialization with tenant setup
def init_db(session: Session) -> None:
    """Initialize database with default data."""
    # Create default tenant if it doesn't exist
    default_tenant = session.exec(
        select(Tenant).where(Tenant.code == "default")
    ).first()
    
    if not default_tenant:
        from app.models import TenantCreate
        tenant_in = TenantCreate(
            name="Default Tenant",
            code="default",
            description="Default tenant for the application",
            max_users=1000,
            max_storage_gb=100,
            features_enabled={
                "audit_logs": True,
                "user_management": True,
                "item_management": True
            }
        )
        default_tenant = crud.create_tenant(session=session, tenant_create=tenant_in, user_id=None)
        logger.info(f"Created default tenant: {default_tenant.id}")

    # Create superuser if it doesn't exist
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            role=UserRole.ADMIN,
            tenant_id=default_tenant.id,
            full_name="System Administrator"
        )
        user = crud.create_user(session=session, user_create=user_in)
        logger.info(f"Created superuser: {user.email}")

# Database health check
def check_db_health() -> bool:
    """Check database connectivity and health."""
    try:
        with Session(engine) as session:
            session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Database statistics
def get_db_stats() -> dict:
    """Get database statistics for monitoring."""
    try:
        with Session(engine) as session:
            # Get connection pool stats
            pool = engine.pool
            stats = {
                "pool_size": getattr(pool, 'size', lambda: 0)(),
                "checked_in": getattr(pool, 'checkedin', lambda: 0)(),
                "checked_out": getattr(pool, 'checkedout', lambda: 0)(),
                "overflow": getattr(pool, 'overflow', lambda: 0)(),
                "invalid": getattr(pool, 'invalid', lambda: 0)(),
            }
            
            # Get table row counts
            tenant_count = session.exec(select(Tenant)).all()
            user_count = session.exec(select(User)).all()
            
            stats.update({
                "tenants": len(tenant_count),
                "users": len(user_count),
            })
            
            return stats
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return {"error": str(e)}

# Database maintenance functions
def vacuum_database() -> bool:
    """Run VACUUM on the database to reclaim storage."""
    try:
        with Session(engine) as session:
            session.execute(text("VACUUM ANALYZE"))
            session.commit()
            logger.info("Database VACUUM completed successfully")
            return True
    except Exception as e:
        logger.error(f"Database VACUUM failed: {e}")
        return False

def reindex_database() -> bool:
    """Reindex the database for better performance."""
    try:
        with Session(engine) as session:
            session.execute(text("REINDEX DATABASE"))
            session.commit()
            logger.info("Database reindex completed successfully")
            return True
    except Exception as e:
        logger.error(f"Database reindex failed: {e}")
        return False
