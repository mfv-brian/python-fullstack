import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, JSON
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    AUDITOR = "auditor"
    USER = "user"


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    role: UserRole = Field(default=UserRole.USER)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    tenant_id: uuid.UUID | None = Field(default=None)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)
    tenant_id: uuid.UUID | None = Field(default=None)
    role: UserRole | None = None


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    tenant_id: uuid.UUID | None = Field(foreign_key="tenant.id", default=None)
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    tenant_id: uuid.UUID | None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


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


# Tenant models
from datetime import datetime, timezone
from enum import Enum


class TenantStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


# Shared properties for tenants
class TenantBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    code: str = Field(unique=True, index=True, min_length=1, max_length=50)
    status: TenantStatus = Field(default=TenantStatus.ACTIVE)


# Properties to receive via API on creation
class TenantCreate(TenantBase):
    pass


# Properties to receive via API on update
class TenantUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    status: TenantStatus | None = None


# Database model, database table inferred from class name
class Tenant(TenantBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Properties to return via API, id is always required
class TenantPublic(TenantBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TenantsPublic(SQLModel):
    data: list[TenantPublic]
    count: int


# Audit Log models
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


# Shared properties for audit logs
class AuditLogBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    action: AuditAction
    resource_type: str = Field(max_length=100)
    resource_id: str = Field(max_length=255)
    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=500)
    before_state: dict | None = Field(default=None, sa_type=JSON)
    after_state: dict | None = Field(default=None, sa_type=JSON)
    custom_metadata: dict | None = Field(default=None, sa_type=JSON)
    severity: AuditSeverity = Field(default=AuditSeverity.INFO)
    tenant_id: uuid.UUID | None = Field(foreign_key="tenant.id", default=None)


# Properties to receive via API on creation
class AuditLogCreate(AuditLogBase):
    pass


# Properties to receive via API on update
class AuditLogUpdate(SQLModel):
    custom_metadata: dict | None = None
    severity: AuditSeverity | None = None


# Database model, database table inferred from class name
class AuditLog(AuditLogBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str | None = Field(default=None, max_length=255)


# Properties to return via API, id is always required
class AuditLogPublic(AuditLogBase):
    id: uuid.UUID
    timestamp: datetime
    session_id: str | None


class AuditLogsPublic(SQLModel):
    data: list[AuditLogPublic]
    count: int


# Export response
class AuditLogExport(SQLModel):
    csv_data: str
    filename: str
