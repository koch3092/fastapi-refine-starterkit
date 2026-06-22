import uuid
from typing import Any

from sqlalchemy import ColumnElement
from sqlmodel import Session, col, func, select

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
    *,
    session: Session,
    owner_id: uuid.UUID | None,
    skip: int = 0,
    limit: int = 100,
    conditions: list[ColumnElement[Any]] | None = None,
    order_by: list[Any] | None = None,
) -> tuple[list[Item], int]:
    """Retrieve a paginated list of items with total count.

    Args:
        session: Database session for the operation.
        owner_id: Filter by owner; if None, returns all items (for superusers).
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        conditions: Optional SQLAlchemy filter conditions from Refine query.
        order_by: Optional SQLAlchemy order_by clauses from Refine query.

    Returns:
        A tuple of (list of items, total count matching the filter).
    """
    # Build base query conditions
    base_conditions: list[ColumnElement[Any]] = []
    if owner_id is not None:
        base_conditions.append(col(Item.owner_id) == owner_id)
    if conditions:
        base_conditions.extend(conditions)

    # Count query
    count_statement = select(func.count()).select_from(Item)
    if base_conditions:
        count_statement = count_statement.where(*base_conditions)
    count = session.exec(count_statement).one()

    # Data query
    statement = select(Item)
    if base_conditions:
        statement = statement.where(*base_conditions)
    if order_by:
        statement = statement.order_by(*order_by)
    statement = statement.offset(skip).limit(limit)
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
