import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_admin_user,
    get_current_auditor_user,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    UserRole,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=UsersPublic,
)
def read_users(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users (authenticated users).
    """
    # Build the base query
    statement = select(User)
    
    # For non-admin users, only show users from their own tenant
    if current_user.role != UserRole.ADMIN:
        statement = statement.where(col(User.tenant_id) == current_user.tenant_id)
    
    # Get count
    count_statement = select(func.count()).select_from(User)
    if current_user.role != UserRole.ADMIN:
        count_statement = count_statement.where(col(User.tenant_id) == current_user.tenant_id)
    
    count = session.exec(count_statement).one()
    
    # Get paginated results
    statement = statement.offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=[UserPublic.model_validate(user) for user in users], count=count)


@router.post(
    "/", 
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def create_user(*, session: SessionDep, user_in: UserCreate, current_user: CurrentUser) -> Any:
    """
    Create new user.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # Non-admin users can only create users in their own tenant
    if current_user.role != UserRole.ADMIN and user_in.tenant_id and user_in.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to create users in other tenants",
        )

    # Set tenant_id from current user if not provided
    if not user_in.tenant_id:
        user_in.tenant_id = current_user.tenant_id

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Admin users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    # For signup, create a default tenant or use existing one
    tenant = crud.get_tenant_by_code(session=session, code="default")
    if not tenant:
        # Create default tenant if it doesn't exist
        from app.models import TenantCreate
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
    
    # Create UserCreate with tenant_id
    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        tenant_id=tenant.id
    )
    
    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: CurrentUser,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    # Check permissions - only admin users can update users from other tenants
    if current_user.role != UserRole.ADMIN and db_user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update users from other tenants",
        )
    
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    # Non-admin users cannot change tenant_id
    if current_user.role != UserRole.ADMIN and user_in.tenant_id and user_in.tenant_id != db_user.tenant_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to change a user's tenant",
        )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions - only admin users can delete users from other tenants
    if current_user.role != UserRole.ADMIN and user.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete users from other tenants",
        )
    
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Users are not allowed to delete themselves through this endpoint"
        )
    
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)  # type: ignore
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")


@router.get("/admin-only", dependencies=[Depends(get_current_active_superuser), Depends(get_current_admin_user)])
def admin_only_endpoint():
    return {"msg": "You are an admin"}

@router.get("/auditor-only", dependencies=[Depends(get_current_active_superuser), Depends(get_current_auditor_user)])
def auditor_only_endpoint():
    return {"msg": "You are an auditor"}
