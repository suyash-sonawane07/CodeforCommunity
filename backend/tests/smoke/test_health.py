"""Smoke tests for the FastAPI scaffold — verify the shell itself, not features."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_responds():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["app"] == "CivicPulse"
    assert body["database"] in {"ok", "unavailable", "unknown"}


def test_root_and_version():
    for path in ("/", "/version"):
        res = client.get(path)
        assert res.status_code == 200
        assert res.json()["name"] == "CivicPulse"
        assert res.json()["scaffold"] is True


def test_openapi_and_docs_served():
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200


def test_protected_endpoint_requires_token():
    res = client.get("/clusters")
    assert res.status_code == 401
    assert res.json()["detail"]["error"]["code"] == "UNAUTHORIZED"


def test_demo_login_issues_role_scoped_token():
    res = client.post("/auth/login", json={"email": "analyst@civicpulse.dev", "password": "x"})
    assert res.status_code == 200
    body = res.json()
    assert body["role"] == "analyst"
    assert body["token_type"] == "bearer"

    # token unlocks the route → 200 OK with real cluster items
    auth = {"Authorization": f"Bearer {body['access_token']}"}
    res = client.get("/clusters", headers=auth)
    assert res.status_code == 200
    assert "items" in res.json()
    assert "total" in res.json()


def test_demo_login_rejects_unknown_user():
    res = client.post("/auth/login", json={"email": "nobody@x.dev", "password": "x"})
    assert res.status_code == 401


def test_role_hierarchy_enforced():
    token = client.post(
        "/auth/login", json={"email": "analyst@civicpulse.dev", "password": "x"}
    ).json()["access_token"]
    # analyst cannot reach admin-only endpoints
    res = client.get("/datasets", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert res.json()["detail"]["error"]["code"] == "FORBIDDEN"


def test_request_creation_requires_consent():
    res = client.post("/requests", json={"channel": "text", "text": "no bus", "consent_ack": False})
    assert res.status_code == 422  # FR-005: rejected before any business logic


def test_business_endpoints_return_valid_evidence_panel():
    token = client.post(
        "/auth/login", json={"email": "reviewer@civicpulse.dev", "password": "x"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/clusters/1/evidence", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["cluster_id"] == 1
    assert "issue_type" in body
    assert "independent_demand_count" in body
    assert "priority_factors" in body
    assert "uncertainty_notes" in body
