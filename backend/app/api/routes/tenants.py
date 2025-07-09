import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel import col, delete, func, select

from app import crud
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
    UserRole,
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
    
    # For non-admin users, only show their own tenant
    if current_user.role != UserRole.ADMIN:
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
    if current_user.role != UserRole.ADMIN:
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
def create_tenant(*, session: SessionDep, tenant_in: TenantCreate, request: Request, current_user: CurrentUser) -> Any:
    """
    Create new tenant.
    """
    # Check if tenant with same code already exists
    existing_tenant = crud.get_tenant_by_code(session=session, code=tenant_in.code)
    
    if existing_tenant:
        raise HTTPException(
            status_code=400,
            detail="A tenant with this code already exists.",
        )
    
    tenant = crud.create_tenant(session=session, tenant_create=tenant_in, user_id=current_user.id)
    
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
    tenant = crud.get_tenant_by_id(session=session, tenant_id=tenant_id)
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
    request: Request,
    current_user: CurrentUser,
) -> Any:
    """
    Update a tenant.
    """
    tenant = crud.get_tenant_by_id(session=session, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found",
        )
    
    # Check if code is being updated and if it conflicts with existing tenant
    if tenant_in.code and tenant_in.code != tenant.code:
        existing_tenant = crud.get_tenant_by_code(session=session, code=tenant_in.code)
        if existing_tenant:
            raise HTTPException(
                status_code=400,
                detail="A tenant with this code already exists.",
            )
    
    tenant = crud.update_tenant(session=session, db_tenant=tenant, tenant_in=tenant_in, user_id=current_user.id)
    
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
    request: Request,
    current_user: CurrentUser,
) -> Any:
    """
    Delete a tenant.
    """
    tenant = crud.get_tenant_by_id(session=session, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found",
        )
    
    crud.delete_tenant(session=session, db_tenant=tenant, user_id=current_user.id)
    
    return Message(message="Tenant deleted successfully") 