import boto3
from botocore.config import Config
from mypy_boto3_s3.client import S3Client

from app.storage.config import StorageConfig


def create_s3_client(
    config: StorageConfig,
    *,
    endpoint_url: str | None = None,
) -> S3Client:
    """Create an S3-compatible storage client."""
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url or config.internal_endpoint_url,
        aws_access_key_id=config.access_key,
        aws_secret_access_key=config.secret_key,
        region_name=config.region,
        config=Config(
            signature_version="s3v4",
            s3={
                "addressing_style": config.addressing_style,
                "payload_signing_enabled": False,
            },
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        ),
    )
