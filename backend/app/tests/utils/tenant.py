from sqlmodel import Session
from app import crud
from app.models import Tenant, TenantCreate
from app.tests.utils.utils import random_lower_string


def create_random_tenant(db: Session) -> Tenant:
    """Create a random tenant for testing."""
    name = random_lower_string()
    code = random_lower_string()
    description = random_lower_string()
    tenant_in = TenantCreate(
        name=name,
        code=code,
        description=description,
        max_users=100,
        max_storage_gb=10,
        features_enabled={
            "audit_logs": True,
            "user_management": True,
            "item_management": True
        }
    )
    tenant = crud.create_tenant(session=db, tenant_create=tenant_in, user_id=None)
    return tenant


def get_or_create_default_tenant(db: Session) -> Tenant:
    """Get the default tenant or create it if it doesn't exist."""
    tenant = crud.get_tenant_by_code(session=db, code="default")
    if not tenant:
        tenant_in = TenantCreate(
            name="Default Tenant",
            code="default",
            description="Default tenant for testing",
            max_users=1000,
            max_storage_gb=100,
            features_enabled={
                "audit_logs": True,
                "user_management": True,
                "item_management": True
            }
        )
        tenant = crud.create_tenant(session=db, tenant_create=tenant_in, user_id=None)
    return tenant 