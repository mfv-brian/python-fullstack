"""update_existing_users_to_use_roles

Revision ID: d198aa5166a7
Revises: 00ca649b4bd9
Create Date: 2025-07-09 15:49:58.454257

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'd198aa5166a7'
down_revision = '00ca649b4bd9'
branch_labels = None
depends_on = None


def upgrade():
    # Update existing users to have the correct roles based on is_superuser field
    # Users with is_superuser=True should have role='ADMIN'
    # Users with is_superuser=False should have role='USER' (default)
    
    # Update superusers to have admin role
    op.execute("""
        UPDATE "user" 
        SET role = 'ADMIN' 
        WHERE is_superuser = true AND (role IS NULL OR role != 'ADMIN')
    """)
    
    # Update regular users to have user role (if not already set)
    op.execute("""
        UPDATE "user" 
        SET role = 'USER' 
        WHERE is_superuser = false AND (role IS NULL OR role != 'USER')
    """)
    
    # Ensure admin@example.com has admin role
    op.execute("""
        UPDATE "user" 
        SET role = 'ADMIN', is_superuser = true 
        WHERE email = 'admin@example.com'
    """)


def downgrade():
    # Revert roles back to default user role
    op.execute("""
        UPDATE "user" 
        SET role = 'USER' 
        WHERE role = 'ADMIN'
    """)
