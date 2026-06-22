from fastapi.testclient import TestClient

from app.core.config import settings


def test_openapi_declares_refine_error_envelope(client: TestClient) -> None:
    """Confirm OpenAPI exposes the fastapi-refine error envelope."""
    response = client.get(f"{settings.API_V1_STR}/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    operation = schema["paths"][f"{settings.API_V1_STR}/users/"]["post"]

    assert "RefineErrorResponse" in schema["components"]["schemas"]
    assert operation["responses"]["409"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/RefineErrorResponse"
    }
    assert operation["responses"]["422"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/RefineErrorResponse"
    }
    assert operation["responses"]["503"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/RefineErrorResponse"
    }
