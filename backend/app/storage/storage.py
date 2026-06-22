from typing import Any

from botocore.exceptions import ClientError
from mypy_boto3_s3.client import S3Client

from app.storage.config import StorageConfig
from app.storage.errors import raise_s3_error


def create_presigned_upload_url(
    *,
    config: StorageConfig,
    presigned_client: S3Client,
    object_key: str,
    content_type: str,
) -> tuple[str, dict[str, str]]:
    """Create a presigned PUT URL and required headers."""
    params: dict[str, Any] = {
        "Bucket": config.bucket,
        "Key": object_key,
        "ContentType": content_type,
    }
    required_headers = {"Content-Type": content_type}
    upload_url = presigned_client.generate_presigned_url(
        ClientMethod="put_object",
        Params=params,
        ExpiresIn=config.upload_expires_seconds,
        HttpMethod="PUT",
    )
    return upload_url, required_headers


def create_presigned_download_url(
    *,
    config: StorageConfig,
    client: S3Client,
    presigned_client: S3Client,
    object_key: str,
) -> str:
    """Create a presigned GET URL for an existing object."""
    get_object_info(config=config, client=client, object_key=object_key)
    return presigned_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": config.bucket, "Key": object_key},
        ExpiresIn=config.download_expires_seconds,
        HttpMethod="GET",
    )


def get_object_info(
    *,
    config: StorageConfig,
    client: S3Client,
    object_key: str,
) -> None:
    """Validate that an object exists in storage."""
    try:
        client.head_object(Bucket=config.bucket, Key=object_key)
    except ClientError as error:
        raise_s3_error(error)


def delete_object(
    *,
    config: StorageConfig,
    client: S3Client,
    object_key: str,
) -> None:
    """Delete an object from storage after validating it exists."""
    get_object_info(config=config, client=client, object_key=object_key)
    try:
        client.delete_object(Bucket=config.bucket, Key=object_key)
    except ClientError as error:
        raise_s3_error(error)
