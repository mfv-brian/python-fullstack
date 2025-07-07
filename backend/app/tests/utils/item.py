from sqlmodel import Session
from app.models import Item

from app import crud
from app.models import Item, ItemCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.tenant import get_or_create_default_tenant
from app.tests.utils.utils import random_lower_string


def create_random_item(db: Session) -> Item:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    # Get or create default tenant
    tenant = get_or_create_default_tenant(db)
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    # Create item with tenant_id
    return crud.create_item(session=db, item_in=item_in, owner_id=owner_id, tenant_id=tenant.id)
