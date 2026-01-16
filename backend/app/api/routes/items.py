import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message
from app.services import item as item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """Retrieve a paginated list of items.

    Superusers can see all items; regular users only see their own.

    Args:
        session: Database session dependency.
        current_user: The authenticated user making the request.
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.

    Returns:
        Paginated list of items with total count.
    """
    owner_id = None if current_user.is_superuser else current_user.id
    items, count = item_service.get_items_paginated(
        session=session, owner_id=owner_id, skip=skip, limit=limit
    )
    return ItemsPublic(data=items, count=count)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """Retrieve a single item by its ID.

    Args:
        session: Database session dependency.
        current_user: The authenticated user making the request.
        id: The UUID of the item to retrieve.

    Returns:
        The requested item.

    Raises:
        HTTPException: 404 if item not found, 400 if insufficient permissions.
    """
    item = item_service.get_item_by_id(session=session, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """Create a new item for the current user.

    Args:
        session: Database session dependency.
        current_user: The authenticated user who will own the item.
        item_in: The item data to create.

    Returns:
        The newly created item.
    """
    item = item_service.create_item(
        session=session, item_in=item_in, owner_id=current_user.id
    )
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """Update an existing item.

    Args:
        session: Database session dependency.
        current_user: The authenticated user making the request.
        id: The UUID of the item to update.
        item_in: The updated item data.

    Returns:
        The updated item.

    Raises:
        HTTPException: 404 if item not found, 400 if insufficient permissions.
    """
    item = item_service.get_item_by_id(session=session, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = item_service.update_item(session=session, db_item=item, item_in=item_in)
    return item


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """Delete an item by its ID.

    Args:
        session: Database session dependency.
        current_user: The authenticated user making the request.
        id: The UUID of the item to delete.

    Returns:
        Success message confirming deletion.

    Raises:
        HTTPException: 404 if item not found, 400 if insufficient permissions.
    """
    item = item_service.get_item_by_id(session=session, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item_service.delete_item(session=session, db_item=item)
    return Message(message="Item deleted successfully")
