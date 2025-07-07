from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.core.security import get_password_hash
from app.models import (
    User,
    UserPublic,
)

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserPublic)
def create_user(user_in: PrivateUserCreate, session: SessionDep) -> Any:
    """
    Create a new user.
    """
    # Get or create default tenant
    from app import crud
    from app.models import TenantCreate
    tenant = crud.get_tenant_by_code(session=session, code="default")
    if not tenant:
        tenant_create = TenantCreate(
            name="Default Tenant",
            code="default",
            description="Default tenant for new users",
            max_users=1000,
            max_storage_gb=100,
            features_enabled={
                "audit_logs": True,
                "user_management": True,
                "item_management": True
            }
        )
        tenant = crud.create_tenant(session=session, tenant_create=tenant_create)

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        tenant_id=tenant.id,
    )

    session.add(user)
    session.commit()

    return user
