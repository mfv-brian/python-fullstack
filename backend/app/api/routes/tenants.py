import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, delete, func, select

from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.models import (
    Message,
    Tenant,
    TenantCreate,
    TenantPublic,
    TenantsPublic,
    TenantUpdate,
)

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get(
    "/",
    response_model=TenantsPublic,
)
def read_tenants(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    search: str | None = Query(None, description="Search by name or code"),
    status: str | None = Query(None, description="Filter by status (active/inactive)"),
) -> Any:
    """
    Retrieve tenants with optional search and filtering (authenticated users).
    """
    # Build the base query
    statement = select(Tenant)
    
    # For non-superusers, only show their own tenant
    if not current_user.is_superuser:
        statement = statement.where(col(Tenant.id) == current_user.tenant_id)
    
    # Add search filter if provided
    if search:
        search_filter = (
            col(Tenant.name).ilike(f"%{search}%") | 
            col(Tenant.code).ilike(f"%{search}%")
        )
        statement = statement.where(search_filter)
    
    # Add status filter if provided
    if status:
        statement = statement.where(col(Tenant.status) == status)
    
    # Get count
    count_statement = select(func.count()).select_from(Tenant)
    if not current_user.is_superuser:
        count_statement = count_statement.where(col(Tenant.id) == current_user.tenant_id)
    if search:
        count_statement = count_statement.where(search_filter)
    if status:
        count_statement = count_statement.where(col(Tenant.status) == status)
    
    count = session.exec(count_statement).one()
    
    # Get paginated results
    tenants = session.exec(statement.offset(skip).limit(limit)).all()
    
    return TenantsPublic(
        data=[TenantPublic.model_validate(tenant) for tenant in tenants],
        count=count
    )


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TenantPublic,
)
def create_tenant(*, session: SessionDep, tenant_in: TenantCreate) -> Any:
    """
    Create new tenant.
    """
    # Check if tenant with same code already exists
    existing_tenant = session.exec(
        select(Tenant).where(col(Tenant.code) == tenant_in.code)
    ).first()
    
    if existing_tenant:
        raise HTTPException(
            status_code=400,
            detail="A tenant with this code already exists.",
        )
    
    tenant = Tenant.model_validate(tenant_in)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    
    return TenantPublic.model_validate(tenant)


@router.get("/{tenant_id}", response_model=TenantPublic)
def read_tenant(
    tenant_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get a specific tenant by id.
    """
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found",
        )
    
    return TenantPublic.model_validate(tenant)


@router.patch(
    "/{tenant_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=TenantPublic,
)
def update_tenant(
    *,
    session: SessionDep,
    tenant_id: uuid.UUID,
    tenant_in: TenantUpdate,
) -> Any:
    """
    Update a tenant.
    """
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found",
        )
    
    # Check if code is being updated and if it conflicts with existing tenant
    if tenant_in.code and tenant_in.code != tenant.code:
        existing_tenant = session.exec(
            select(Tenant).where(col(Tenant.code) == tenant_in.code)
        ).first()
        if existing_tenant:
            raise HTTPException(
                status_code=400,
                detail="A tenant with this code already exists.",
            )
    
    # Update tenant data
    update_data = tenant_in.model_dump(exclude_unset=True)
    if update_data:
        from datetime import datetime, timezone
        update_data["updated_at"] = datetime.now(timezone.utc)
        tenant.sqlmodel_update(update_data)
        session.add(tenant)
        session.commit()
        session.refresh(tenant)
    
    return TenantPublic.model_validate(tenant)


@router.delete(
    "/{tenant_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_tenant(
    *,
    session: SessionDep,
    tenant_id: uuid.UUID,
) -> Any:
    """
    Delete a tenant.
    """
    tenant = session.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found",
        )
    
    session.delete(tenant)
    session.commit()
    
    return Message(message="Tenant deleted successfully") 