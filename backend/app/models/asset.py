import uuid
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


def get_datetime_utc() -> datetime:
    """Return the current UTC datetime for timestamp defaults."""
    return datetime.now(timezone.utc)


class AssetBase(SQLModel):
    file_name: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=255)
    size: int = Field(ge=0)


class AssetPresignedUploadRequest(AssetBase):
    pass


class AssetUpdate(SQLModel):
    file_name: str | None = Field(default=None, min_length=1, max_length=255)


class Asset(AssetBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    object_key: str = Field(unique=True, index=True, max_length=1024)
    created_at: datetime = Field(default_factory=get_datetime_utc, nullable=False)
    owner: User | None = Relationship(back_populates="assets")


class AssetPublic(AssetBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    object_key: str
    created_at: datetime


class AssetPresignedUploadResponse(SQLModel):
    asset: AssetPublic
    upload_url: str
    method: str = "PUT"
    expires_in: int
    required_headers: dict[str, str]


class AssetPresignedDownloadResponse(SQLModel):
    asset: AssetPublic
    download_url: str
    expires_in: int
