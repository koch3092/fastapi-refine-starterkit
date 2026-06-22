import uuid
from typing import Annotated, Any, NoReturn

from fastapi import APIRouter, Depends, HTTPException, Path, Response
from fastapi_refine import (
    FilterConfig,
    FilterField,
    RefineQuery,
    RefineResponse,
    SortConfig,
)

from app.api.deps.common import (
    CurrentUser,
    PresignedS3ClientDep,
    S3ClientDep,
    SessionDep,
    StorageConfigDep,
)
from app.api.deps.refine import refine_query_dep
from app.models import (
    Asset,
    AssetPresignedDownloadResponse,
    AssetPresignedUploadRequest,
    AssetPresignedUploadResponse,
    AssetPublic,
    AssetUpdate,
    Message,
)
from app.services import asset as asset_service
from app.storage.errors import S3Error, S3NoKeyError, S3ValidationError
from app.storage.storage import (
    create_presigned_download_url,
    create_presigned_upload_url,
    delete_object,
)

router = APIRouter(prefix="/assets", tags=["assets"])

_asset_c = Asset.__table__.c  # type: ignore[attr-defined]

asset_filter_config = FilterConfig(
    fields={
        "id": FilterField(column=_asset_c.id, cast=uuid.UUID),
        "owner_id": FilterField(column=_asset_c.owner_id, cast=uuid.UUID),
        "file_name": FilterField(column=_asset_c.file_name, cast=str),
        "content_type": FilterField(column=_asset_c.content_type, cast=str),
    },
    search_fields=[_asset_c.file_name, _asset_c.content_type],
)

asset_sort_config = SortConfig(
    fields={
        "id": _asset_c.id,
        "file_name": _asset_c.file_name,
        "content_type": _asset_c.content_type,
        "size": _asset_c.size,
        "created_at": _asset_c.created_at,
    }
)

AssetQuery = Annotated[
    RefineQuery,
    refine_query_dep(Asset, asset_filter_config, asset_sort_config),
]


def get_asset_with_permission(
    session: SessionDep,
    current_user: CurrentUser,
    id: Annotated[uuid.UUID, Path(description="The asset ID")],
) -> Asset:
    """Load an asset and verify the current user can access it."""
    asset = asset_service.get_asset_by_id(session=session, asset_id=id)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    if not current_user.is_superuser and asset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return asset


CurrentAsset = Annotated[Asset, Depends(get_asset_with_permission)]


def raise_storage_http_error(error: S3Error) -> NoReturn:
    """Translate storage errors into API errors."""
    if isinstance(error, S3NoKeyError):
        raise HTTPException(status_code=404, detail="Storage object not found")
    if isinstance(error, S3ValidationError):
        raise HTTPException(status_code=400, detail=str(error))
    raise HTTPException(status_code=503, detail="Storage service unavailable")


@router.get("/", response_model=list[AssetPublic])
def read_assets(
    response: Response,
    session: SessionDep,
    current_user: CurrentUser,
    query: AssetQuery,
) -> Any:
    """Retrieve a paginated list of assets visible to the current user."""
    owner_id = None if current_user.is_superuser else current_user.id
    assets, count = asset_service.get_assets_paginated(
        session=session,
        owner_id=owner_id,
        skip=query.offset,
        limit=query.limit,
        conditions=query.conditions,
        order_by=query.order_by,
    )
    RefineResponse(response).set_total_count(count)
    return assets


@router.post("/presigned-upload", response_model=AssetPresignedUploadResponse)
def create_asset_upload_url(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    storage_config: StorageConfigDep,
    presigned_client: PresignedS3ClientDep,
    asset_in: AssetPresignedUploadRequest,
) -> AssetPresignedUploadResponse:
    """Create asset metadata and return a presigned PUT URL."""
    asset = asset_service.create_asset_record(
        owner_id=current_user.id,
        asset_in=asset_in,
    )
    try:
        upload_url, required_headers = create_presigned_upload_url(
            config=storage_config,
            presigned_client=presigned_client,
            object_key=asset.object_key,
            content_type=asset.content_type,
        )
    except S3Error as error:
        raise_storage_http_error(error)

    asset = asset_service.save_asset_record(session=session, db_asset=asset)

    return AssetPresignedUploadResponse(
        asset=AssetPublic.model_validate(asset),
        upload_url=upload_url,
        method="PUT",
        expires_in=storage_config.upload_expires_seconds,
        required_headers=required_headers,
    )


@router.get("/{id}", response_model=AssetPublic)
def read_asset(asset: CurrentAsset) -> Any:
    """Retrieve a single asset by id."""
    return asset


@router.patch("/{id}", response_model=AssetPublic)
def update_asset(
    *,
    session: SessionDep,
    asset: CurrentAsset,
    asset_in: AssetUpdate,
) -> Any:
    """Update mutable asset metadata."""
    return asset_service.update_asset(
        session=session,
        db_asset=asset,
        asset_in=asset_in,
    )


@router.get("/{id}/download-url", response_model=AssetPresignedDownloadResponse)
def read_asset_download_url(
    *,
    asset: CurrentAsset,
    storage_config: StorageConfigDep,
    s3_client: S3ClientDep,
    presigned_client: PresignedS3ClientDep,
) -> AssetPresignedDownloadResponse:
    """Return a presigned GET URL for an uploaded asset."""
    try:
        download_url = create_presigned_download_url(
            config=storage_config,
            client=s3_client,
            presigned_client=presigned_client,
            object_key=asset.object_key,
        )
    except S3Error as error:
        raise_storage_http_error(error)

    return AssetPresignedDownloadResponse(
        asset=AssetPublic.model_validate(asset),
        download_url=download_url,
        expires_in=storage_config.download_expires_seconds,
    )


@router.delete("/{id}", response_model=Message)
def delete_asset(
    *,
    session: SessionDep,
    asset: CurrentAsset,
    storage_config: StorageConfigDep,
    s3_client: S3ClientDep,
) -> Message:
    """Delete asset metadata and the corresponding object."""
    try:
        delete_object(
            config=storage_config,
            client=s3_client,
            object_key=asset.object_key,
        )
    except S3NoKeyError:
        pass
    except S3Error as error:
        raise_storage_http_error(error)

    asset_service.delete_asset_record(session=session, db_asset=asset)
    return Message(message="Asset deleted successfully")
