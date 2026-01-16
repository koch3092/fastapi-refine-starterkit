import uuid

from sqlmodel import Session

from app.models import ItemCreate, ItemUpdate
from app.services import item as item_service
from tests.utils.item import create_random_item
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def test_create_item(db: Session) -> None:
    """Test creating a new item.

    Verifies that item is created with correct title, description, and owner.
    """
    user = create_random_user(db)
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    item = item_service.create_item(session=db, item_in=item_in, owner_id=user.id)
    assert item.title == title
    assert item.description == description
    assert item.owner_id == user.id


def test_create_item_without_description(db: Session) -> None:
    """Test creating an item without description.

    Verifies that description is optional.
    """
    user = create_random_user(db)
    title = random_lower_string()
    item_in = ItemCreate(title=title)
    item = item_service.create_item(session=db, item_in=item_in, owner_id=user.id)
    assert item.title == title
    assert item.description is None
    assert item.owner_id == user.id


def test_get_item_by_id(db: Session) -> None:
    """Test retrieving an item by ID.

    Verifies that get_item_by_id returns the correct item.
    """
    item = create_random_item(db)
    fetched_item = item_service.get_item_by_id(session=db, item_id=item.id)
    assert fetched_item
    assert fetched_item.id == item.id
    assert fetched_item.title == item.title
    assert fetched_item.owner_id == item.owner_id


def test_get_item_by_id_not_found(db: Session) -> None:
    """Test get_item_by_id returns None for non-existent ID."""
    non_existent_id = uuid.uuid4()
    fetched_item = item_service.get_item_by_id(session=db, item_id=non_existent_id)
    assert fetched_item is None


def test_get_items_paginated_all(db: Session) -> None:
    """Test retrieving all items (superuser case).

    Verifies that passing owner_id=None returns all items.
    """
    # Create items for different users
    item1 = create_random_item(db)
    item2 = create_random_item(db)

    items, count = item_service.get_items_paginated(
        session=db, owner_id=None, skip=0, limit=100
    )
    assert count >= 2
    item_ids = [item.id for item in items]
    assert item1.id in item_ids
    assert item2.id in item_ids


def test_get_items_paginated_by_owner(db: Session) -> None:
    """Test retrieving items filtered by owner.

    Verifies that passing owner_id filters items correctly.
    """
    # Create a user with items
    user = create_random_user(db)
    title1 = random_lower_string()
    title2 = random_lower_string()
    item_in1 = ItemCreate(title=title1)
    item_in2 = ItemCreate(title=title2)
    item1 = item_service.create_item(session=db, item_in=item_in1, owner_id=user.id)
    item2 = item_service.create_item(session=db, item_in=item_in2, owner_id=user.id)

    # Create an item for another user
    other_item = create_random_item(db)

    # Get items for the first user only
    items, count = item_service.get_items_paginated(
        session=db, owner_id=user.id, skip=0, limit=100
    )
    assert count == 2
    item_ids = [item.id for item in items]
    assert item1.id in item_ids
    assert item2.id in item_ids
    assert other_item.id not in item_ids


def test_get_items_paginated_with_skip_limit(db: Session) -> None:
    """Test pagination with skip and limit parameters."""
    user = create_random_user(db)

    # Create multiple items
    for i in range(5):
        item_in = ItemCreate(title=f"Item {i}")
        item_service.create_item(session=db, item_in=item_in, owner_id=user.id)

    items_all, count = item_service.get_items_paginated(
        session=db, owner_id=user.id, skip=0, limit=100
    )
    items_limited, _ = item_service.get_items_paginated(
        session=db, owner_id=user.id, skip=0, limit=2
    )
    items_skipped, _ = item_service.get_items_paginated(
        session=db, owner_id=user.id, skip=2, limit=2
    )

    assert count == 5
    assert len(items_limited) == 2
    assert len(items_skipped) == 2
    # Verify skipped items are different from first batch
    limited_ids = {item.id for item in items_limited}
    skipped_ids = {item.id for item in items_skipped}
    assert limited_ids.isdisjoint(skipped_ids)


def test_get_items_paginated_empty(db: Session) -> None:
    """Test pagination returns empty list for user with no items."""
    user = create_random_user(db)
    items, count = item_service.get_items_paginated(
        session=db, owner_id=user.id, skip=0, limit=100
    )
    assert count == 0
    assert len(items) == 0


def test_update_item(db: Session) -> None:
    """Test updating an item.

    Verifies that update_item modifies the item correctly.
    """
    item = create_random_item(db)
    new_title = random_lower_string()
    new_description = random_lower_string()
    item_in_update = ItemUpdate(title=new_title, description=new_description)
    updated_item = item_service.update_item(
        session=db, db_item=item, item_in=item_in_update
    )
    assert updated_item.id == item.id
    assert updated_item.title == new_title
    assert updated_item.description == new_description
    assert updated_item.owner_id == item.owner_id


def test_update_item_partial(db: Session) -> None:
    """Test partial update of an item.

    Verifies that only specified fields are updated.
    """
    item = create_random_item(db)
    original_description = item.description
    new_title = random_lower_string()
    item_in_update = ItemUpdate(title=new_title)
    updated_item = item_service.update_item(
        session=db, db_item=item, item_in=item_in_update
    )
    assert updated_item.title == new_title
    assert updated_item.description == original_description


def test_delete_item(db: Session) -> None:
    """Test deleting an item.

    Verifies that delete_item removes item from database.
    """
    item = create_random_item(db)
    item_id = item.id
    item_service.delete_item(session=db, db_item=item)
    deleted_item = item_service.get_item_by_id(session=db, item_id=item_id)
    assert deleted_item is None


def test_delete_item_does_not_affect_other_items(db: Session) -> None:
    """Test deleting an item doesn't affect other items.

    Verifies that other items remain intact after deletion.
    """
    user = create_random_user(db)
    item_in1 = ItemCreate(title=random_lower_string())
    item_in2 = ItemCreate(title=random_lower_string())
    item1 = item_service.create_item(session=db, item_in=item_in1, owner_id=user.id)
    item2 = item_service.create_item(session=db, item_in=item_in2, owner_id=user.id)

    # Delete first item
    item_service.delete_item(session=db, db_item=item1)

    # Verify first item is deleted
    deleted_item = item_service.get_item_by_id(session=db, item_id=item1.id)
    assert deleted_item is None

    # Verify second item still exists
    remaining_item = item_service.get_item_by_id(session=db, item_id=item2.id)
    assert remaining_item is not None
    assert remaining_item.id == item2.id
