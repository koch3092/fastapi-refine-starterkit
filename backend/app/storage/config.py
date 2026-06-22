from typing import Literal

from pydantic import BaseModel

from app.core.config import settings


class StorageConfig(BaseModel):
    internal_endpoint_url: str
    public_endpoint_url: str
    access_key: str
    secret_key: str
    region: str
    bucket: str
    addressing_style: Literal["auto", "virtual", "path"]
    upload_expires_seconds: int
    download_expires_seconds: int


def get_storage_config() -> StorageConfig:
    """Build object storage configuration from app settings."""
    return StorageConfig(
        internal_endpoint_url=settings.S3_INTERNAL_ENDPOINT_URL,
        public_endpoint_url=settings.S3_PUBLIC_ENDPOINT_URL,
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        region=settings.S3_REGION,
        bucket=settings.S3_BUCKET,
        addressing_style=settings.S3_ADDRESSING_STYLE,
        upload_expires_seconds=settings.S3_PRESIGNED_UPLOAD_EXPIRES_SECONDS,
        download_expires_seconds=settings.S3_PRESIGNED_DOWNLOAD_EXPIRES_SECONDS,
    )
