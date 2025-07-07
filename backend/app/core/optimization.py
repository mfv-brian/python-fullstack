"""
Database optimization utilities for multi-tenant schema
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import text, create_engine, and_
from sqlmodel import Session, select, func
from sqlalchemy.exc import SQLAlchemyError

from app.core.db import engine
from app.models import Tenant, User, Item, AuditLog, TenantMetrics

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Database optimization utilities for multi-tenant applications."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_partitioned_tables(self) -> bool:
        """Create partitioned tables for audit logs and metrics."""
        try:
            # Create partitioned audit_log table
            self.session.execute(text("""
                CREATE TABLE IF NOT EXISTS audit_log_partitioned (
                    LIKE audit_log INCLUDING ALL
                ) PARTITION BY RANGE (timestamp);
            """))
            
            # Create monthly partitions for the last 12 months
            for i in range(12):
                start_date = datetime.now() - timedelta(days=30 * i)
                end_date = start_date + timedelta(days=30)
                partition_name = f"audit_log_{start_date.strftime('%Y_%m')}"
                
                self.session.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {partition_name} 
                    PARTITION OF audit_log_partitioned
                    FOR VALUES FROM ('{start_date.isoformat()}') 
                    TO ('{end_date.isoformat()}');
                """))
            
            # Create partitioned tenant_metrics table
            self.session.execute(text("""
                CREATE TABLE IF NOT EXISTS tenant_metrics_partitioned (
                    LIKE tenant_metrics INCLUDING ALL
                ) PARTITION BY RANGE (date);
            """))
            
            self.session.commit()
            logger.info("Partitioned tables created successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create partitioned tables: {e}")
            self.session.rollback()
            return False
    
    def create_tenant_based_indexes(self) -> bool:
        """Create tenant-specific indexes for better performance."""
        try:
            # Composite indexes for tenant-based queries
            indexes = [
                # User indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_tenant_email_active ON user (tenant_id, email, is_active)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_tenant_role_active ON user (tenant_id, role, is_active)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_tenant_last_login ON user (tenant_id, last_login_at DESC)",
                
                # Item indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_tenant_created_desc ON item (tenant_id, created_at DESC)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_tenant_owner_created ON item (tenant_id, owner_id, created_at DESC)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_tenant_title_search ON item (tenant_id, title) USING gin(to_tsvector('english', title))",
                
                # Audit log indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_tenant_timestamp_desc ON audit_log (tenant_id, timestamp DESC)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_tenant_action_timestamp ON audit_log (tenant_id, action, timestamp DESC)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_tenant_severity_timestamp ON audit_log (tenant_id, severity, timestamp DESC)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_tenant_user_timestamp ON audit_log (tenant_id, user_id, timestamp DESC)",
                
                # Full-text search indexes
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_metadata_search ON audit_log USING gin(custom_metadata)",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_item_description_search ON item USING gin(to_tsvector('english', description))",
            ]
            
            for index_sql in indexes:
                self.session.execute(text(index_sql))
            
            self.session.commit()
            logger.info("Tenant-based indexes created successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tenant-based indexes: {e}")
            self.session.rollback()
            return False
    
    def create_partial_indexes(self) -> bool:
        """Create partial indexes for active records only."""
        try:
            partial_indexes = [
                # Only active users
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_active_only ON user (tenant_id, email) WHERE is_active = true",
                
                # Only active tenants
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tenant_active_only ON tenant (id, name) WHERE status = 'active'",
                
                # Recent audit logs (last 30 days)
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_recent ON audit_log (tenant_id, timestamp) WHERE timestamp > NOW() - INTERVAL '30 days'",
                
                # High severity audit logs
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_high_severity ON audit_log (tenant_id, timestamp) WHERE severity IN ('ERROR', 'CRITICAL')",
            ]
            
            for index_sql in partial_indexes:
                self.session.execute(text(index_sql))
            
            self.session.commit()
            logger.info("Partial indexes created successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create partial indexes: {e}")
            self.session.rollback()
            return False
    
    def analyze_tables(self) -> bool:
        """Run ANALYZE on all tables to update statistics."""
        try:
            tables = ['tenant', 'user', 'item', 'audit_log', 'tenant_metrics']
            
            for table in tables:
                self.session.execute(text(f"ANALYZE {table}"))
            
            self.session.commit()
            logger.info("Table analysis completed successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to analyze tables: {e}")
            self.session.rollback()
            return False
    
    def vacuum_tables(self) -> bool:
        """Run VACUUM on all tables to reclaim storage."""
        try:
            tables = ['tenant', 'user', 'item', 'audit_log', 'tenant_metrics']
            
            for table in tables:
                self.session.execute(text(f"VACUUM ANALYZE {table}"))
            
            self.session.commit()
            logger.info("Table vacuum completed successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to vacuum tables: {e}")
            self.session.rollback()
            return False
    
    def get_table_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics for all tables."""
        try:
            stats = {}
            
            # Get table sizes and row counts
            result = self.session.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public'
                ORDER BY tablename, attname;
            """))
            
            stats['column_stats'] = [dict(row) for row in result]
            
            # Get index usage statistics
            result = self.session.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                ORDER BY idx_scan DESC;
            """))
            
            stats['index_usage'] = [dict(row) for row in result]
            
            # Get table sizes
            result = self.session.execute(text("""
                SELECT 
                    tablename,
                    pg_size_pretty(pg_total_relation_size(tablename::text)) as size,
                    pg_total_relation_size(tablename::text) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(tablename::text) DESC;
            """))
            
            stats['table_sizes'] = [dict(row) for row in result]
            
            return stats
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get table statistics: {e}")
            return {"error": str(e)}
    
    def optimize_tenant_queries(self, tenant_id: str) -> Dict[str, Any]:
        """Optimize queries for a specific tenant."""
        try:
            # Get tenant-specific statistics
            tenant_stats = {}
            
            # User count
            user_count = self.session.exec(
                select(func.count()).where(User.tenant_id == tenant_id)
            ).one()
            tenant_stats['user_count'] = user_count
            
            # Item count
            item_count = self.session.exec(
                select(func.count()).where(Item.tenant_id == tenant_id)
            ).one()
            tenant_stats['item_count'] = item_count
            
            # Recent audit logs
            recent_audits = self.session.exec(
                select(func.count())
                .where(AuditLog.tenant_id == tenant_id)
                .where(AuditLog.timestamp > datetime.now() - timedelta(days=7))
            ).one()
            tenant_stats['recent_audits'] = recent_audits
            
            # Storage usage estimation
            storage_estimate = (user_count * 0.1) + (item_count * 0.05) + (recent_audits * 0.01)
            tenant_stats['storage_mb'] = round(storage_estimate, 2)
            
            return tenant_stats
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to optimize tenant queries: {e}")
            return {"error": str(e)}
    
    def create_tenant_metrics(self) -> bool:
        """Create or update tenant metrics for monitoring."""
        try:
            tenants = self.session.exec(select(Tenant)).all()
            
            for tenant in tenants:
                # Calculate metrics
                user_count = self.session.exec(
                    select(func.count()).where(User.tenant_id == tenant.id)
                ).one()
                
                item_count = self.session.exec(
                    select(func.count()).where(Item.tenant_id == tenant.id)
                ).one()
                
                audit_count = self.session.exec(
                    select(func.count()).where(AuditLog.tenant_id == tenant.id)
                ).one()
                
                active_users = self.session.exec(
                    select(func.count())
                    .where(User.tenant_id == tenant.id)
                    .where(User.is_active == True)
                    .where(User.last_login_at > datetime.now() - timedelta(days=30))  # type: ignore
                ).one()
                
                # Create or update metrics
                metrics = self.session.exec(
                    select(TenantMetrics)
                    .where(TenantMetrics.tenant_id == tenant.id)
                    .where(TenantMetrics.date == datetime.now().date())
                ).first()
                
                if not metrics:
                    metrics = TenantMetrics(
                        tenant_id=tenant.id,
                        date=datetime.now(),
                        user_count=user_count,
                        item_count=item_count,
                        audit_log_count=audit_count,
                        active_users=active_users,
                        storage_used_mb=round((user_count * 0.1) + (item_count * 0.05), 2)
                    )
                    self.session.add(metrics)
                else:
                    metrics.user_count = user_count
                    metrics.item_count = item_count
                    metrics.audit_log_count = audit_count
                    metrics.active_users = active_users
                    metrics.storage_used_mb = round((user_count * 0.1) + (item_count * 0.05), 2)
            
            self.session.commit()
            logger.info("Tenant metrics updated successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tenant metrics: {e}")
            self.session.rollback()
            return False


def optimize_database() -> Dict[str, Any]:
    """Main function to optimize the entire database."""
    with Session(engine) as session:
        optimizer = DatabaseOptimizer(session)
        
        results = {
            "partitioned_tables": optimizer.create_partitioned_tables(),
            "tenant_indexes": optimizer.create_tenant_based_indexes(),
            "partial_indexes": optimizer.create_partial_indexes(),
            "table_analysis": optimizer.analyze_tables(),
            "table_vacuum": optimizer.vacuum_tables(),
            "tenant_metrics": optimizer.create_tenant_metrics(),
            "statistics": optimizer.get_table_statistics()
        }
        
        return results


def get_tenant_performance_report(tenant_id: str) -> Dict[str, Any]:
    """Get performance report for a specific tenant."""
    with Session(engine) as session:
        optimizer = DatabaseOptimizer(session)
        return optimizer.optimize_tenant_queries(tenant_id) 