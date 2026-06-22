from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from mypy_boto3_s3.client import S3Client
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from app.storage.client import create_s3_client
from app.storage.config import StorageConfig, get_storage_config

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_storage_config_dep() -> StorageConfig:
    """Return storage configuration for request-scoped dependencies."""
    return get_storage_config()


StorageConfigDep = Annotated[StorageConfig, Depends(get_storage_config_dep)]


def get_s3_client(config: StorageConfigDep) -> S3Client:
    """Return an internal S3 client for server-to-storage operations."""
    return create_s3_client(config)


S3ClientDep = Annotated[S3Client, Depends(get_s3_client)]


def get_presigned_s3_client(config: StorageConfigDep) -> S3Client:
    """Return a public-endpoint S3 client for browser-facing presigned URLs."""
    return create_s3_client(config, endpoint_url=config.public_endpoint_url)


PresignedS3ClientDep = Annotated[S3Client, Depends(get_presigned_s3_client)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Verify current user is a superuser.

    Args:
        current_user: The authenticated user.

    Returns:
        The superuser if verified.

    Raises:
        HTTPException: 403 if user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
