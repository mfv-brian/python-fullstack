import uuid
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Tenant, TenantStatus, User
from app.tests.utils.user import create_random_user


@pytest.fixture
def tenant_data() -> dict:
    return {
        "name": "Test Tenant",
        "description": "A test tenant for testing purposes",
        "code": f"TEST-{uuid.uuid4()}",
        "status": "active"
    }


@pytest.fixture
def tenant_data_2() -> dict:
    return {
        "name": "Another Tenant",
        "description": "Another test tenant",
        "code": f"ANOTHER-{uuid.uuid4()}",
        "status": "active"
    }


def test_create_tenant(
    client: TestClient, superuser_token_headers: dict, tenant_data: dict
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data,
    )
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == tenant_data["name"]
    assert data["description"] == tenant_data["description"]
    assert data["code"] == tenant_data["code"]
    assert data["status"] == tenant_data["status"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_tenant_duplicate_code(
    client: TestClient, superuser_token_headers: dict, tenant_data: dict
) -> None:
    # Create first tenant
    response = client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data,
    )
    assert response.status_code == 200
    
    # Try to create second tenant with same code
    response = client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data,
    )
    assert response.status_code == 400
    assert "code already exists" in response.json()["detail"]


def test_create_tenant_normal_user(
    client: TestClient, normal_user_token_headers: dict, tenant_data: dict
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=normal_user_token_headers,
        json=tenant_data,
    )
    assert response.status_code == 403


def test_read_tenants(
    client: TestClient, superuser_token_headers: dict, tenant_data: dict, tenant_data_2: dict
) -> None:
    # Create two tenants
    client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data,
    )
    client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data_2,
    )
    
    response = client.get(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 2
    assert data["count"] >= 2


def test_read_tenants_with_search(
    client: TestClient, superuser_token_headers: dict, tenant_data: dict, tenant_data_2: dict
) -> None:
    # Create two tenants
    client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data,
    )
    client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data_2,
    )
    
    # Search by name
    response = client.get(
        f"{settings.API_V1_STR}/tenants/?search=Test",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1
    assert any("Test" in tenant["name"] for tenant in data["data"])


def test_read_tenants_with_status_filter(
    client: TestClient, superuser_token_headers: dict, tenant_data: dict
) -> None:
    # Create tenant
    client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data,
    )
    
    # Filter by active status
    response = client.get(
        f"{settings.API_V1_STR}/tenants/?status=active",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 1
    assert all(tenant["status"] == "active" for tenant in data["data"])


def test_read_tenant(
    client: TestClient, superuser_token_headers: dict, tenant_data: dict
) -> None:
    # Create tenant
    create_response = client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data,
    )
    tenant_id = create_response.json()["id"]
    
    # Read tenant
    response = client.get(
        f"{settings.API_V1_STR}/tenants/{tenant_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tenant_id
    assert data["name"] == tenant_data["name"]


def test_read_tenant_not_found(
    client: TestClient, superuser_token_headers: dict
) -> None:
    fake_id = str(uuid.uuid4())
    response = client.get(
        f"{settings.API_V1_STR}/tenants/{fake_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_update_tenant(
    client: TestClient, superuser_token_headers: dict, tenant_data: dict
) -> None:
    # Create tenant
    create_response = client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data,
    )
    tenant_id = create_response.json()["id"]
    
    # Update tenant
    update_data = {
        "name": "Updated Tenant Name",
        "description": "Updated description",
        "status": "inactive"
    }
    response = client.patch(
        f"{settings.API_V1_STR}/tenants/{tenant_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["status"] == update_data["status"]


def test_update_tenant_duplicate_code(
    client: TestClient, superuser_token_headers: dict, tenant_data: dict, tenant_data_2: dict
) -> None:
    # Create two tenants
    tenant1_response = client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data,
    )
    tenant2_response = client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data_2,
    )
    
    tenant1_id = tenant1_response.json()["id"]
    
    # Try to update first tenant with second tenant's code
    update_data = {"code": tenant_data_2["code"]}
    response = client.patch(
        f"{settings.API_V1_STR}/tenants/{tenant1_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 400
    assert "code already exists" in response.json()["detail"]


def test_update_tenant_not_found(
    client: TestClient, superuser_token_headers: dict
) -> None:
    fake_id = str(uuid.uuid4())
    update_data = {"name": "Updated Name"}
    response = client.patch(
        f"{settings.API_V1_STR}/tenants/{fake_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 404


def test_delete_tenant(
    client: TestClient, superuser_token_headers: dict, tenant_data: dict
) -> None:
    # Create tenant
    create_response = client.post(
        f"{settings.API_V1_STR}/tenants/",
        headers=superuser_token_headers,
        json=tenant_data,
    )
    tenant_id = create_response.json()["id"]
    
    # Delete tenant
    response = client.delete(
        f"{settings.API_V1_STR}/tenants/{tenant_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Tenant deleted successfully"
    
    # Verify tenant is deleted
    get_response = client.get(
        f"{settings.API_V1_STR}/tenants/{tenant_id}",
        headers=superuser_token_headers,
    )
    assert get_response.status_code == 404


def test_delete_tenant_not_found(
    client: TestClient, superuser_token_headers: dict
) -> None:
    fake_id = str(uuid.uuid4())
    response = client.delete(
        f"{settings.API_V1_STR}/tenants/{fake_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404 