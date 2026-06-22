from botocore.exceptions import ClientError


class S3Error(Exception):
    """Base exception for storage operations."""


class S3ValidationError(S3Error):
    """Raised when storage input is invalid."""


class S3NoKeyError(S3Error):
    """Raised when an object key does not exist."""


class S3NoBucketError(S3Error):
    """Raised when the configured bucket does not exist."""


class S3AccessDeniedError(S3Error):
    """Raised when S3 rejects the request due to permissions."""


class S3UnknownError(S3Error):
    """Raised for unmapped S3 client errors."""


def raise_s3_error(error: ClientError) -> None:
    """Map botocore ClientError values to project storage errors."""
    code = error.response.get("Error", {}).get("Code")

    if code in {"NoSuchKey", "404", "NotFound"}:
        raise S3NoKeyError("Storage object not found") from error

    if code == "NoSuchBucket":
        raise S3NoBucketError("Storage bucket is not configured") from error

    if code in {"AccessDenied", "403"}:
        raise S3AccessDeniedError("Storage access denied") from error

    raise S3UnknownError("Storage service error") from error
