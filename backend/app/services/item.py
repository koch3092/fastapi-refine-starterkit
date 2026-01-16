import uuid

from sqlmodel import Session, func, select

from app.models import Item, ItemCreate, ItemUpdate


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """Create a new item in the database.

    Args:
        session: Database session for the operation.
        item_in: Item creation data including title and description.
        owner_id: The UUID of the user who owns this item.

    Returns:
        The newly created item entity with generated ID.
    """
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_items_paginated(
    *, session: Session, owner_id: uuid.UUID | None, skip: int = 0, limit: int = 100
) -> tuple[list[Item], int]:
    """Retrieve a paginated list of items with total count.

    Args:
        session: Database session for the operation.
        owner_id: Filter by owner; if None, returns all items (for superusers).
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.

    Returns:
        A tuple of (list of items, total count matching the filter).
    """
    if owner_id is None:
        # Superuser: get all items
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        statement = select(Item).offset(skip).limit(limit)
        items = list(session.exec(statement).all())
    else:
        # Regular user: get only their items
        count_statement = (
            select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
        )
        items = list(session.exec(statement).all())

    return items, count


def get_item_by_id(*, session: Session, item_id: uuid.UUID) -> Item | None:
    """Retrieve an item by its unique identifier.

    Args:
        session: Database session for the operation.
        item_id: The UUID of the item to retrieve.

    Returns:
        The item entity if found, None otherwise.
    """
    return session.get(Item, item_id)


def update_item(*, session: Session, db_item: Item, item_in: ItemUpdate) -> Item:
    """Update an existing item.

    Args:
        session: Database session for the operation.
        db_item: The existing item entity to update.
        item_in: Update data with fields to modify.

    Returns:
        The updated item entity.
    """
    update_dict = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update_dict)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_item(*, session: Session, db_item: Item) -> None:
    """Delete an item from the database.

    Args:
        session: Database session for the operation.
        db_item: The item entity to delete.
    """
    session.delete(db_item)
    session.commit()
