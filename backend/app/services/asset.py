import uuid
from typing import Any

from sqlalchemy import ColumnElement
from sqlmodel import Session, col, func, select

from app.models import Asset, AssetPresignedUploadRequest, AssetUpdate
from app.storage.key import build_asset_object_key


def create_asset_record(
    *,
    owner_id: uuid.UUID,
    asset_in: AssetPresignedUploadRequest,
) -> Asset:
    """Build an asset metadata record before direct browser upload."""
    asset_id = uuid.uuid4()
    object_key = build_asset_object_key(
        owner_id=owner_id,
        asset_id=asset_id,
        file_name=asset_in.file_name,
    )
    db_asset = Asset(
        id=asset_id,
        owner_id=owner_id,
        file_name=asset_in.file_name,
        content_type=asset_in.content_type,
        size=asset_in.size,
        object_key=object_key,
    )
    return db_asset


def save_asset_record(*, session: Session, db_asset: Asset) -> Asset:
    """Persist an asset metadata record."""
    session.add(db_asset)
    session.commit()
    session.refresh(db_asset)
    return db_asset


def get_asset_by_id(*, session: Session, asset_id: uuid.UUID) -> Asset | None:
    """Retrieve an asset by id."""
    return session.get(Asset, asset_id)


def get_assets_paginated(
    *,
    session: Session,
    owner_id: uuid.UUID | None,
    skip: int = 0,
    limit: int = 100,
    conditions: list[ColumnElement[Any]] | None = None,
    order_by: list[Any] | None = None,
) -> tuple[list[Asset], int]:
    """Retrieve a paginated asset list with total count."""
    base_conditions: list[ColumnElement[Any]] = []
    if owner_id is not None:
        base_conditions.append(col(Asset.owner_id) == owner_id)
    if conditions:
        base_conditions.extend(conditions)

    count_statement = select(func.count()).select_from(Asset)
    if base_conditions:
        count_statement = count_statement.where(*base_conditions)
    count = session.exec(count_statement).one()

    statement = select(Asset)
    if base_conditions:
        statement = statement.where(*base_conditions)
    if order_by:
        statement = statement.order_by(*order_by)
    else:
        statement = statement.order_by(col(Asset.created_at).desc())
    statement = statement.offset(skip).limit(limit)
    assets = list(session.exec(statement).all())

    return assets, count


def update_asset(
    *,
    session: Session,
    db_asset: Asset,
    asset_in: AssetUpdate,
) -> Asset:
    """Update mutable asset metadata."""
    update_dict = asset_in.model_dump(exclude_unset=True)
    db_asset.sqlmodel_update(update_dict)
    session.add(db_asset)
    session.commit()
    session.refresh(db_asset)
    return db_asset


def delete_asset_record(*, session: Session, db_asset: Asset) -> None:
    """Delete an asset metadata record."""
    session.delete(db_asset)
    session.commit()
