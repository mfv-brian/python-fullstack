import uuid
import logging
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item, 
    ItemCreate, 
    User, 
    UserCreate, 
    UserUpdate, 
    Tenant, 
    TenantCreate,
    TenantUpdate,
    AuditLog,
    AuditAction,
    AuditSeverity
)

logger = logging.getLogger(__name__)

def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID, tenant_id: uuid.UUID | None = None) -> Item:
    update_data = {"owner_id": owner_id}
    if tenant_id:
        update_data["tenant_id"] = tenant_id
    db_item = Item.model_validate(item_in, update=update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_tenant(*, session: Session, tenant_create: TenantCreate, user_id: uuid.UUID | None = None) -> Tenant:
    db_tenant = Tenant.model_validate(tenant_create)
    session.add(db_tenant)
    session.commit()
    session.refresh(db_tenant)
    
    # Create audit log for tenant creation if user_id is provided
    if user_id:
        audit_log = AuditLog(
            user_id=user_id,
            action=AuditAction.CREATE,
            resource_type="tenant",
            resource_id=str(db_tenant.id),
            after_state={
                "id": str(db_tenant.id),
                "name": db_tenant.name,
                "description": db_tenant.description,
                "code": db_tenant.code,
                "status": db_tenant.status,
                "max_users": db_tenant.max_users,
                "max_storage_gb": db_tenant.max_storage_gb,
                "features_enabled": db_tenant.features_enabled,
                "created_at": db_tenant.created_at.isoformat(),
                "updated_at": db_tenant.updated_at.isoformat()
            },
            metadata={
                "tenant_name": db_tenant.name,
                "tenant_code": db_tenant.code,
                "creator_user_id": str(user_id)
            },
            severity=AuditSeverity.INFO,
            tenant_id=db_tenant.id
        )
        session.add(audit_log)
        session.commit()
    
    return db_tenant


def update_tenant(*, session: Session, db_tenant: Tenant, tenant_in: TenantUpdate, user_id: uuid.UUID | None = None) -> Tenant:
    # Store before state for audit log
    before_state = {
        "id": str(db_tenant.id),
        "name": db_tenant.name,
        "description": db_tenant.description,
        "code": db_tenant.code,
        "status": db_tenant.status,
        "max_users": db_tenant.max_users,
        "max_storage_gb": db_tenant.max_storage_gb,
        "features_enabled": db_tenant.features_enabled,
        "created_at": db_tenant.created_at.isoformat(),
        "updated_at": db_tenant.updated_at.isoformat()
    }
    
    # Update tenant data
    update_data = tenant_in.model_dump(exclude_unset=True)
    if update_data:
        from datetime import datetime, timezone
        update_data["updated_at"] = datetime.now(timezone.utc)
        db_tenant.sqlmodel_update(update_data)
        session.add(db_tenant)
        session.commit()
        session.refresh(db_tenant)
        
        # Create audit log for tenant update if user_id is provided
        if user_id:
            audit_log = AuditLog(
                user_id=user_id,
                action=AuditAction.UPDATE,
                resource_type="tenant",
                resource_id=str(db_tenant.id),
                before_state=before_state,
                after_state={
                    "id": str(db_tenant.id),
                    "name": db_tenant.name,
                    "description": db_tenant.description,
                    "code": db_tenant.code,
                    "status": db_tenant.status,
                    "max_users": db_tenant.max_users,
                    "max_storage_gb": db_tenant.max_storage_gb,
                    "features_enabled": db_tenant.features_enabled,
                    "created_at": db_tenant.created_at.isoformat(),
                    "updated_at": db_tenant.updated_at.isoformat()
                },
                metadata={
                    "tenant_name": db_tenant.name,
                    "tenant_code": db_tenant.code,
                    "updater_user_id": str(user_id),
                    "updated_fields": list(update_data.keys())
                },
                severity=AuditSeverity.INFO,
                tenant_id=db_tenant.id
            )
            session.add(audit_log)
            session.commit()
    
    return db_tenant


def delete_tenant(*, session: Session, db_tenant: Tenant, user_id: uuid.UUID | None = None) -> bool:
    # Store before state for audit log
    before_state = {
        "id": str(db_tenant.id),
        "name": db_tenant.name,
        "description": db_tenant.description,
        "code": db_tenant.code,
        "status": db_tenant.status,
        "max_users": db_tenant.max_users,
        "max_storage_gb": db_tenant.max_storage_gb,
        "features_enabled": db_tenant.features_enabled,
        "created_at": db_tenant.created_at.isoformat(),
        "updated_at": db_tenant.updated_at.isoformat()
    }
    
    # Create audit log for tenant deletion BEFORE deleting the tenant
    if user_id:
        audit_log = AuditLog(
            user_id=user_id,
            action=AuditAction.DELETE,
            resource_type="tenant",
            resource_id=str(db_tenant.id),
            before_state=before_state,
            metadata={
                "tenant_name": db_tenant.name,
                "tenant_code": db_tenant.code,
                "deleter_user_id": str(user_id),
                "cascade_delete": True
            },
            severity=AuditSeverity.INFO,
            tenant_id=db_tenant.id
        )
        session.add(audit_log)
        session.commit()
    
    # Delete the tenant
    session.delete(db_tenant)
    session.commit()
    
    return True


def get_tenant_by_code(*, session: Session, code: str) -> Tenant | None:
    statement = select(Tenant).where(Tenant.code == code)
    return session.exec(statement).first()


def get_tenant_by_id(*, session: Session, tenant_id: uuid.UUID) -> Tenant | None:
    return session.get(Tenant, tenant_id)
