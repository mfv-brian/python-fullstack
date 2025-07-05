import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from app.core.config import settings
from app.models import AuditAction, AuditSeverity
from app.tests.utils.user import create_random_user

@pytest.fixture
def normal_user(db):
    return create_random_user(db)

@pytest.fixture
def audit_log_data(superuser_token_headers, db, normal_user):
    return [
        {
            "user_id": str(normal_user.id),
            "action": "CREATE",
            "resource_type": "tenant",
            "resource_id": str(uuid.uuid4()),
            "ip_address": "127.0.0.1",
            "user_agent": "pytest-agent",
            "before_state": {"foo": "bar"},
            "after_state": {"foo": "baz"},
            "custom_metadata": {"meta": "data"},
            "severity": "INFO",
            "tenant_id": None,
        },
        {
            "user_id": superuser_token_headers["user_id"] if "user_id" in superuser_token_headers else str(normal_user.id),
            "action": "UPDATE",
            "resource_type": "item",
            "resource_id": str(uuid.uuid4()),
            "ip_address": "127.0.0.2",
            "user_agent": "pytest-agent-2",
            "before_state": {"foo": "baz"},
            "after_state": {"foo": "qux"},
            "custom_metadata": {"meta": "data2"},
            "severity": "WARNING",
            "tenant_id": None,
        },
    ]

@pytest.fixture
def created_audit_log_ids(client: TestClient, superuser_token_headers: dict, audit_log_data: list):
    ids = []
    for entry in audit_log_data:
        response = client.post(
            f"{settings.API_V1_STR}/audit-logs/",
            headers=superuser_token_headers,
            json=entry,
        )
        assert response.status_code == 200
        ids.append(response.json()["id"])
    return ids

def test_create_audit_log(client: TestClient, superuser_token_headers: dict, audit_log_data: list):
    for entry in audit_log_data:
        response = client.post(
            f"{settings.API_V1_STR}/audit-logs/",
            headers=superuser_token_headers,
            json=entry,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == entry["action"]
        assert data["resource_type"] == entry["resource_type"]
        assert data["custom_metadata"] == entry["custom_metadata"]
        assert "id" in data
        assert "timestamp" in data

def test_get_audit_log(client: TestClient, superuser_token_headers: dict, created_audit_log_ids):
    for audit_log_id in created_audit_log_ids:
        response = client.get(
            f"{settings.API_V1_STR}/audit-logs/{audit_log_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == audit_log_id

def test_update_audit_log(client: TestClient, superuser_token_headers: dict, created_audit_log_ids):
    for audit_log_id in created_audit_log_ids:
        update_data = {"custom_metadata": {"meta": "updated"}, "severity": "WARNING"}
        response = client.patch(
            f"{settings.API_V1_STR}/audit-logs/{audit_log_id}",
            headers=superuser_token_headers,
            json=update_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["custom_metadata"] == update_data["custom_metadata"]
        assert data["severity"] == update_data["severity"]

def test_search_audit_logs(client: TestClient, superuser_token_headers: dict, created_audit_log_ids, audit_log_data: list):
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=1)).replace(tzinfo=None).isoformat()
    end = (now + timedelta(days=1)).replace(tzinfo=None).isoformat()
    # Search by action
    response = client.get(
        f"{settings.API_V1_STR}/audit-logs/?start_date={start}&end_date={end}&action=CREATE",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    # Search by user_id
    user_id = audit_log_data[0]["user_id"]
    response = client.get(
        f"{settings.API_V1_STR}/audit-logs/?user_id={user_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert any(log["user_id"] == user_id for log in data["data"])

def test_export_audit_logs_csv(client: TestClient, superuser_token_headers: dict):
    response = client.get(
        f"{settings.API_V1_STR}/audit-logs/export/csv",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["csv_data"].startswith("ID,Timestamp,User ID,Action,Resource Type,Resource ID")
    assert data["filename"].endswith(".csv")

def test_delete_audit_log(client: TestClient, superuser_token_headers: dict, created_audit_log_ids):
    for audit_log_id in created_audit_log_ids:
        response = client.delete(
            f"{settings.API_V1_STR}/audit-logs/{audit_log_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Audit log deleted successfully"
        # Verify deletion
        get_response = client.get(
            f"{settings.API_V1_STR}/audit-logs/{audit_log_id}",
            headers=superuser_token_headers,
        )
        assert get_response.status_code == 404

def test_websocket_audit_log():
    from starlette.testclient import TestClient as StarletteTestClient
    from app.main import app
    with StarletteTestClient(app) as client:
        with client.websocket_connect(f"{settings.API_V1_STR}/audit-logs/ws") as ws:
            msg = ws.receive_text()
            assert msg == "ping" 