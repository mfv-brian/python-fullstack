import logging

from sqlmodel import Session, select

from app.core.db import engine, init_db
from app.core.config import settings
from app import crud
from app.models import TenantCreate, UserCreate, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        # Create superuser first
        user = session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()
        if not user:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user = crud.create_user(session=session, user_create=user_in)
            logger.info(f"Created superuser: {user.email}")
        
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
                )
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
                )
            )
            logger.info(f"Created tenant: {tenant2.name}")
        
        tenant3 = crud.get_tenant_by_code(session=session, code="STARTUP")
        if not tenant3:
            tenant3 = crud.create_tenant(
                session=session,
                tenant_create=TenantCreate(
                    name="Startup Inc",
                    description="A growing startup company",
                    code="STARTUP",
                    status="active"
                )
            )
            logger.info(f"Created tenant: {tenant3.name}")
        
        # Create sample users
        logger.info("Creating sample users")
        
        # Sample users for ACME
        user1 = crud.get_user_by_email(session=session, email="john.doe@acme.com")
        if not user1:
            user1 = crud.create_user(
                session=session,
                user_create=UserCreate(
                    email="john.doe@acme.com",
                    password="password123",
                    full_name="John Doe",
                    is_superuser=False,
                    tenant_id=tenant1.id
                )
            )
            logger.info(f"Created user: {user1.full_name}")
        
        user2 = crud.get_user_by_email(session=session, email="jane.smith@acme.com")
        if not user2:
            user2 = crud.create_user(
                session=session,
                user_create=UserCreate(
                    email="jane.smith@acme.com",
                    password="password123",
                    full_name="Jane Smith",
                    is_superuser=False,
                    tenant_id=tenant1.id
                )
            )
            logger.info(f"Created user: {user2.full_name}")
        
        # Sample users for TECHCO
        user3 = crud.get_user_by_email(session=session, email="bob.wilson@techco.com")
        if not user3:
            user3 = crud.create_user(
                session=session,
                user_create=UserCreate(
                    email="bob.wilson@techco.com",
                    password="password123",
                    full_name="Bob Wilson",
                    is_superuser=False,
                    tenant_id=tenant2.id
                )
            )
            logger.info(f"Created user: {user3.full_name}")
        
        user4 = crud.get_user_by_email(session=session, email="alice.brown@techco.com")
        if not user4:
            user4 = crud.create_user(
                session=session,
                user_create=UserCreate(
                    email="alice.brown@techco.com",
                    password="password123",
                    full_name="Alice Brown",
                    is_superuser=False,
                    tenant_id=tenant2.id
                )
            )
            logger.info(f"Created user: {user4.full_name}")
        
        # Sample users for STARTUP
        user5 = crud.get_user_by_email(session=session, email="mike.jones@startup.com")
        if not user5:
            user5 = crud.create_user(
                session=session,
                user_create=UserCreate(
                    email="mike.jones@startup.com",
                    password="password123",
                    full_name="Mike Jones",
                    is_superuser=False,
                    tenant_id=tenant3.id
                )
            )
            logger.info(f"Created user: {user5.full_name}")
        
        user6 = crud.get_user_by_email(session=session, email="sarah.davis@startup.com")
        if not user6:
            user6 = crud.create_user(
                session=session,
                user_create=UserCreate(
                    email="sarah.davis@startup.com",
                    password="password123",
                    full_name="Sarah Davis",
                    is_superuser=False,
                    tenant_id=tenant3.id
                )
            )
            logger.info(f"Created user: {user6.full_name}")


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
