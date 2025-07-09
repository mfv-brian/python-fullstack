import uuid
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, JSON, Index
from enum import Enum
from sqlalchemy import text


class UserRole(str, Enum):
    ADMIN = "admin"
    AUDITOR = "auditor"
    USER = "user"


class TenantStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    SEARCH = "SEARCH"


class AuditSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Base class for all tenant-aware models
class TenantAwareBase(SQLModel):
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", nullable=False, index=True)


# Tenant model with enhanced features
class TenantBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, index=True)
    description: str | None = Field(default=None, max_length=500)
    code: str = Field(unique=True, index=True, min_length=1, max_length=50)
    status: TenantStatus = Field(default=TenantStatus.ACTIVE, index=True)
    # Multi-tenant configuration
    max_users: int = Field(default=100)
    max_storage_gb: int = Field(default=10)
    features_enabled: dict = Field(default_factory=dict, sa_type=JSON)
    # Performance tracking
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TenantCreate(TenantBase):
    pass


class TenantUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    status: TenantStatus | None = None
    max_users: int | None = None
    max_storage_gb: int | None = None
    features_enabled: dict | None = None


class Tenant(TenantBase, table=True):  # type: ignore
    __tablename__ = "tenant" # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Relationships
    users: List["User"] = Relationship(back_populates="tenant", cascade_delete=True)
    items: List["Item"] = Relationship(back_populates="tenant", cascade_delete=True)
    audit_logs: List["AuditLog"] = Relationship(back_populates="tenant", cascade_delete=True)
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_tenant_status_created", "status", "created_at"),
        Index("idx_tenant_code_status", "code", "status"),
    )


class TenantPublic(TenantBase):
    id: uuid.UUID


class TenantsPublic(SQLModel):
    data: list[TenantPublic]
    count: int


# Enhanced User model with tenant isolation
class UserBase(SQLModel):
    email: EmailStr = Field(max_length=255)
    is_active: bool = Field(default=True, index=True)
    is_superuser: bool = Field(default=False, index=True)
    full_name: str | None = Field(default=None, max_length=255, index=True)
    role: UserRole = Field(default=UserRole.USER, index=True)
    # Performance tracking
    last_login_at: datetime | None = Field(default=None, index=True)
    login_count: int = Field(default=0)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    tenant_id: uuid.UUID


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)
    tenant_id: uuid.UUID | None = Field(default=None)
    role: UserRole | None = None
    last_login_at: datetime | None = None


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):  # type: ignore
    __tablename__ = "user" # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", nullable=False, index=True)
    
    # Relationships
    tenant: Tenant = Relationship(back_populates="users")
    items: List["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    audit_logs: List["AuditLog"] = Relationship(back_populates="user", cascade_delete=True)
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_user_tenant_email", "tenant_id", "email"),
        Index("idx_user_tenant_active", "tenant_id", "is_active"),
        Index("idx_user_tenant_role", "tenant_id", "role"),
        Index("idx_user_last_login", "last_login_at"),
    )


class UserPublic(UserBase):
    id: uuid.UUID
    tenant_id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Enhanced Item model with tenant isolation
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255, index=True)
    description: str | None = Field(default=None, max_length=1000)
    # Performance tracking
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class Item(ItemBase, table=True):  # type: ignore
    __tablename__ = "item" # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", nullable=False, index=True)
    
    # Relationships
    owner: User = Relationship(back_populates="items")
    tenant: Tenant = Relationship(back_populates="items")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_item_tenant_created", "tenant_id", "created_at"),
        Index("idx_item_tenant_owner", "tenant_id", "owner_id"),
        Index("idx_item_title_tenant", "title", "tenant_id"),
    )


class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    tenant_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Enhanced Audit Log model with tenant isolation and partitioning support
class AuditLogBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    action: AuditAction = Field(index=True)
    resource_type: str = Field(max_length=100, index=True)
    resource_id: str = Field(max_length=255, index=True)
    ip_address: str | None = Field(default=None, max_length=45, index=True)
    user_agent: str | None = Field(default=None, max_length=500)
    before_state: dict | None = Field(default=None, sa_type=JSON)
    after_state: dict | None = Field(default=None, sa_type=JSON)
    custom_metadata: dict | None = Field(default=None, sa_type=JSON)
    severity: AuditSeverity = Field(default=AuditSeverity.INFO, index=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", nullable=False, index=True)
    # Performance tracking
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    session_id: str | None = Field(default=None, max_length=255, index=True)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogUpdate(SQLModel):
    custom_metadata: dict | None = None
    severity: AuditSeverity | None = None


class AuditLog(AuditLogBase, table=True):  # type: ignore
    __tablename__ = "audit_log" # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Relationships
    user: User = Relationship(back_populates="audit_logs")
    tenant: Tenant = Relationship(back_populates="audit_logs")
    
    # Indexes for performance and partitioning
    __table_args__ = (
        # Composite indexes for common queries
        Index("idx_audit_tenant_timestamp", "tenant_id", "timestamp"),
        Index("idx_audit_tenant_action", "tenant_id", "action"),
        Index("idx_audit_tenant_severity", "tenant_id", "severity"),
        Index("idx_audit_tenant_user", "tenant_id", "user_id"),
        Index("idx_audit_tenant_resource", "tenant_id", "resource_type", "resource_id"),
        # Time-based indexes for partitioning
        Index("idx_audit_timestamp_partition", "timestamp"),
        Index("idx_audit_tenant_timestamp_partition", "tenant_id", "timestamp"),
    )


class AuditLogPublic(AuditLogBase):
    id: uuid.UUID


class AuditLogsPublic(SQLModel):
    data: list[AuditLogPublic]
    count: int


class AuditLogExport(SQLModel):
    csv_data: str
    filename: str


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Performance monitoring models
class TenantMetrics(SQLModel, table=True):  # type: ignore
    __tablename__ = "tenant_metrics" # type: ignore
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", nullable=False, index=True)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    user_count: int = Field(default=0)
    item_count: int = Field(default=0)
    audit_log_count: int = Field(default=0)
    storage_used_mb: float = Field(default=0.0)
    active_users: int = Field(default=0)
    
    __table_args__ = (
        Index("idx_tenant_metrics_date", "tenant_id", "date"),
    )
