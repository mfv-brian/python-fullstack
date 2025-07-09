import logging

from sqlmodel import Session, select

from app.core.db import engine, init_db
from app.core.config import settings
from app import crud
from app.models import TenantCreate, UserCreate, User, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        # Create or get default tenant for superuser
        default_tenant_code = "DEFAULT"
        default_tenant = crud.get_tenant_by_code(session=session, code=default_tenant_code)
        if not default_tenant:
            default_tenant = crud.create_tenant(
                session=session,
                tenant_create=TenantCreate(
                    name="Default Tenant",
                    description="Default tenant for superuser",
                    code=default_tenant_code,
                    status="active"
                ),
                user_id=None  # No user_id for initial data creation
            )
            logger.info(f"Created default tenant: {default_tenant.name}")
        # Always ensure default_tenant is set
        assert default_tenant is not None, "Default tenant must exist before creating superuser"

        # Create superuser first
        user = session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()
        if user:
            # Remove existing superuser to recreate it
            session.delete(user)
            session.commit()
            logger.info(f"Removed existing superuser: {settings.FIRST_SUPERUSER}")
        
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            role=UserRole.ADMIN,
            tenant_id=default_tenant.id
        )
        user = crud.create_user(session=session, user_create=user_in)
        logger.info(f"Created superuser: {user.email}")
        
        # Create or update admin@example.com user
        admin_user = session.exec(
            select(User).where(User.email == "admin@example.com")
        ).first()
        if admin_user:
            # Update existing admin user to have ADMIN role
            admin_user.role = UserRole.ADMIN
            session.add(admin_user)
            session.commit()
            logger.info(f"Updated existing admin user: {admin_user.email}")
        else:
            # Create new admin user
            admin_user_in = UserCreate(
                email="admin@example.com",
                password="admin123",  # You should change this password
                role=UserRole.ADMIN,
                tenant_id=default_tenant.id,
                full_name="System Administrator"
            )
            admin_user = crud.create_user(session=session, user_create=admin_user_in)
            logger.info(f"Created admin user: {admin_user.email}")
        
        # Call the original init_db function
        init_db(session)
        
        # Create sample tenants
        logger.info("Creating sample tenants")
        
        # Check if tenants already exist
        tenant1 = crud.get_tenant_by_code(session=session, code="ACME")
        if not tenant1:
            tenant1 = crud.create_tenant(
                session=session,
                tenant_create=TenantCreate(
                    name="Acme Corporation",
                    description="A leading technology company",
                    code="ACME",
                    status="active"
                ),
                user_id=admin_user.id if admin_user else None
            )
            logger.info(f"Created tenant: {tenant1.name}")
        
        tenant2 = crud.get_tenant_by_code(session=session, code="TECHCO")
        if not tenant2:
            tenant2 = crud.create_tenant(
                session=session,
                tenant_create=TenantCreate(
                    name="TechCo Solutions",
                    description="Innovative software solutions provider",
                    code="TECHCO",
                    status="active"
                ),
                user_id=admin_user.id if admin_user else None
            )
            logger.info(f"Created tenant: {tenant2.name}")
        
        tenant3 = crud.get_tenant_by_code(session=session, code="STARTUP")
        if not tenant3:
            tenant3 = crud.create_tenant(
                session=session,
                tenant_create=TenantCreate(
                    name="Startup Inc",
                    description="A fast-growing startup company",
                    code="STARTUP",
                    status="active"
                ),
                user_id=admin_user.id if admin_user else None
            )
            logger.info(f"Created tenant: {tenant3.name}")
        
        # Create sample users
        logger.info("Creating sample users")
        
        # Create users for different tenants
        users_data = [
            {
                "email": "john.doe@acme.com",
                "password": "password123",
                "full_name": "John Doe",
                "tenant_id": tenant1.id if tenant1 else default_tenant.id
            },
            {
                "email": "jane.smith@techco.com",
                "password": "password123",
                "full_name": "Jane Smith",
                "tenant_id": tenant2.id if tenant2 else default_tenant.id
            },
            {
                "email": "bob.wilson@startup.com",
                "password": "password123",
                "full_name": "Bob Wilson",
                "tenant_id": tenant3.id if tenant3 else default_tenant.id
            },
            {
                "email": "alice.brown@acme.com",
                "password": "password123",
                "full_name": "Alice Brown",
                "tenant_id": tenant1.id if tenant1 else default_tenant.id
            },
            {
                "email": "mike.jones@techco.com",
                "password": "password123",
                "full_name": "Mike Jones",
                "tenant_id": tenant2.id if tenant2 else default_tenant.id
            },
            {
                "email": "sarah.davis@startup.com",
                "password": "password123",
                "full_name": "Sarah Davis",
                "tenant_id": tenant3.id if tenant3 else default_tenant.id
            }
        ]
        
        for user_data in users_data:
            existing_user = session.exec(
                select(User).where(User.email == user_data["email"])
            ).first()
            if not existing_user:
                user_in = UserCreate(**user_data)
                user = crud.create_user(session=session, user_create=user_in)
                logger.info(f"Created user: {user.full_name}")
        
        logger.info("Initial data created")


if __name__ == "__main__":
    init()
