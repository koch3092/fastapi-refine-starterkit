import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Response
from fastapi_refine import (
    FilterConfig,
    FilterField,
    RefineQuery,
    RefineResponse,
    SortConfig,
)

from app.api.deps.common import CurrentUser, SessionDep
from app.api.deps.refine import refine_query_dep
from app.models import Item, ItemCreate, ItemPublic, ItemUpdate, Message
from app.services import item as item_service

router = APIRouter(prefix="/items", tags=["items"])

# Get table columns for Refine config (SQLModel provides __table__ at runtime)
_item_c = Item.__table__.c  # type: ignore[attr-defined]

# Configure Refine query parameters for items
item_filter_config = FilterConfig(
    fields={
        "id": FilterField(column=_item_c.id, cast=uuid.UUID),
        "title": FilterField(column=_item_c.title, cast=str),
        "description": FilterField(column=_item_c.description, cast=str),
        "owner_id": FilterField(column=_item_c.owner_id, cast=uuid.UUID),
    },
    search_fields=[_item_c.title, _item_c.description],
)

item_sort_config = SortConfig(
    fields={
        "title": _item_c.title,
        "id": _item_c.id,
    }
)

ItemQuery = Annotated[
    RefineQuery,
    refine_query_dep(
        Item,
        item_filter_config,
        item_sort_config,
    ),
]


def get_item_with_permission(
    session: SessionDep,
    current_user: CurrentUser,
    id: Annotated[uuid.UUID, Path(description="The item ID")],
) -> Item:
    """Get an item by ID and verify user has permission.

    Args:
        session: Database session.
        current_user: The authenticated user.
        id: The item UUID from path.

    Returns:
        The item if found and user has permission.

    Raises:
        HTTPException: 404 if not found, 403 if no permission.
    """
    item = item_service.get_item_by_id(session=session, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item


CurrentItem = Annotated[Item, Depends(get_item_with_permission)]


@router.get("/", response_model=list[ItemPublic])
def read_items(
    response: Response,
    session: SessionDep,
    current_user: CurrentUser,
    query: ItemQuery,
) -> Any:
    """Retrieve a paginated list of items.

    Superusers can see all items; regular users only see their own.
    Supports Refine's simple-rest pagination, sorting, and filtering.

    Args:
        response: FastAPI response object for setting headers.
        session: Database session dependency.
        current_user: The authenticated user making the request.
        query: Refine query parameters (pagination, sort, filter).

    Returns:
        List of items with x-total-count header.
    """
    owner_id = None if current_user.is_superuser else current_user.id
    items, count = item_service.get_items_paginated(
        session=session,
        owner_id=owner_id,
        skip=query.offset,
        limit=query.limit,
        conditions=query.conditions,
        order_by=query.order_by,
    )
    RefineResponse(response).set_total_count(count)
    return items


@router.get("/{id}", response_model=ItemPublic)
def read_item(item: CurrentItem) -> Any:
    """Retrieve a single item by its ID.

    Args:
        item: The item retrieved via dependency with permission check.

    Returns:
        The requested item.
    """
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
@router.patch("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    item: CurrentItem,
    item_in: ItemUpdate,
) -> Any:
    """Update an existing item.

    Supports both PUT and PATCH methods for Refine compatibility.

    Args:
        session: Database session dependency.
        item: The item retrieved via dependency with permission check.
        item_in: The updated item data.

    Returns:
        The updated item.
    """
    item = item_service.update_item(session=session, db_item=item, item_in=item_in)
    return item


@router.delete("/{id}")
def delete_item(session: SessionDep, item: CurrentItem) -> Message:
    """Delete an item by its ID.

    Args:
        session: Database session dependency.
        item: The item retrieved via dependency with permission check.

    Returns:
        Success message confirming deletion.
    """
    item_service.delete_item(session=session, db_item=item)
    return Message(message="Item deleted successfully")
