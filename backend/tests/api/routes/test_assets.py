import uuid
from collections.abc import Generator
from typing import Any

import pytest
from botocore.exceptions import ClientError
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.api.deps.common import get_presigned_s3_client, get_s3_client
from app.core.config import settings
from app.main import app
from app.models import Asset, AssetPresignedUploadRequest
from app.services import asset as asset_service
from app.services import user as user_service
from tests.utils.user import create_random_user


class FakeS3Client:
    def __init__(self) -> None:
        self.deleted_keys: list[str] = []
        self.missing_keys: set[str] = set()

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: dict[str, Any],
        ExpiresIn: int,
        HttpMethod: str,
    ) -> str:
        key = Params["Key"]
        return f"https://storage.example.test/{ClientMethod}/{key}?expires={ExpiresIn}&method={HttpMethod}"

    def head_object(self, Bucket: str, Key: str) -> dict[str, Any]:
        if Key in self.missing_keys:
            raise ClientError(
                {"Error": {"Code": "NoSuchKey", "Message": "not found"}},
                "HeadObject",
            )
        return {"Bucket": Bucket, "Key": Key}

    def delete_object(self, Bucket: str, Key: str) -> dict[str, Any]:
        self.deleted_keys.append(Key)
        return {"Bucket": Bucket, "Key": Key}


@pytest.fixture()
def fake_s3_client() -> Generator[FakeS3Client, None, None]:
    fake_client = FakeS3Client()
    app.dependency_overrides[get_s3_client] = lambda: fake_client
    app.dependency_overrides[get_presigned_s3_client] = lambda: fake_client
    yield fake_client
    app.dependency_overrides.pop(get_s3_client, None)
    app.dependency_overrides.pop(get_presigned_s3_client, None)


def create_asset(
    db: Session,
    *,
    owner_id: uuid.UUID,
    file_name: str = "asset.txt",
) -> Asset:
    asset_in = AssetPresignedUploadRequest(
        file_name=file_name,
        content_type="text/plain",
        size=12,
    )
    asset = asset_service.create_asset_record(
        owner_id=owner_id,
        asset_in=asset_in,
    )
    return asset_service.save_asset_record(session=db, db_asset=asset)


def test_create_asset_presigned_upload(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    fake_s3_client: FakeS3Client,
) -> None:
    data = {"file_name": "example.txt", "content_type": "text/plain", "size": 12}

    response = client.post(
        f"{settings.API_V1_STR}/assets/presigned-upload",
        headers=normal_user_token_headers,
        json=data,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["method"] == "PUT"
    assert content["required_headers"] == {"Content-Type": "text/plain"}
    assert content["asset"]["file_name"] == data["file_name"]
    assert content["asset"]["object_key"].startswith("assets/")
    assert "put_object" in content["upload_url"]
    assert fake_s3_client.deleted_keys == []


def test_read_assets_regular_user_only_sees_own_assets(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
    db: Session,
    fake_s3_client: FakeS3Client,
) -> None:
    normal_user = user_service.get_user_by_email(
        session=db,
        email=settings.EMAIL_TEST_USER,
    )
    assert normal_user
    other_user = create_random_user(db)
    marker = f"visibility-{uuid.uuid4()}.txt"
    own_asset = create_asset(db, owner_id=normal_user.id, file_name=marker)
    other_asset = create_asset(db, owner_id=other_user.id, file_name=marker)

    user_response = client.get(
        f"{settings.API_V1_STR}/assets/",
        headers=normal_user_token_headers,
        params={"file_name_like": "visibility-"},
    )
    assert user_response.status_code == 200
    user_content = user_response.json()
    assert user_response.headers["x-total-count"] == "1"
    assert [asset["id"] for asset in user_content] == [str(own_asset.id)]

    admin_response = client.get(
        f"{settings.API_V1_STR}/assets/",
        headers=superuser_token_headers,
        params={"file_name_like": "visibility-"},
    )
    assert admin_response.status_code == 200
    admin_ids = {asset["id"] for asset in admin_response.json()}
    assert str(own_asset.id) in admin_ids
    assert str(other_asset.id) in admin_ids
    assert int(admin_response.headers["x-total-count"]) >= 2
    assert fake_s3_client.deleted_keys == []


def test_read_asset_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    other_user = create_random_user(db)
    asset = create_asset(db, owner_id=other_user.id)

    response = client.get(
        f"{settings.API_V1_STR}/assets/{asset.id}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 403
    content = response.json()
    assert content["message"] == "Not enough permissions"
    assert content["statusCode"] == 403


def test_read_asset_download_url(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    fake_s3_client: FakeS3Client,
) -> None:
    owner = create_random_user(db)
    asset = create_asset(db, owner_id=owner.id)

    response = client.get(
        f"{settings.API_V1_STR}/assets/{asset.id}/download-url",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["asset"]["id"] == str(asset.id)
    assert "get_object" in content["download_url"]
    assert fake_s3_client.deleted_keys == []


def test_delete_asset_deletes_object_and_record(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    fake_s3_client: FakeS3Client,
) -> None:
    owner = create_random_user(db)
    asset = create_asset(db, owner_id=owner.id)
    asset_id = asset.id
    object_key = asset.object_key

    response = client.delete(
        f"{settings.API_V1_STR}/assets/{asset_id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Asset deleted successfully"
    assert fake_s3_client.deleted_keys == [object_key]
    db.expire_all()
    assert db.get(Asset, asset_id) is None
