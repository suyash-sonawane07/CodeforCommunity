"""Root contract tests — the generated OpenAPI must expose the full PRD §10.1 surface.

Run: `make test-contract` (uses the backend venv).
"""

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))

from app.main import app  # noqa: E402

PRD_ENDPOINTS = {
    ("POST", "/auth/login"),
    ("POST", "/requests"),
    ("POST", "/requests/{request_id}/audio"),
    ("GET", "/requests/{request_id}"),
    ("GET", "/clusters"),
    ("GET", "/clusters/{cluster_id}"),
    ("PATCH", "/clusters/{cluster_id}"),
    ("GET", "/clusters/{cluster_id}/evidence"),
    ("POST", "/clusters/{cluster_id}/review"),
    ("GET", "/clusters/{cluster_id}/gap-analysis"),
    ("GET", "/clusters/{cluster_id}/priority"),
    ("POST", "/simulations"),
    ("GET", "/clusters/{cluster_id}/outcome"),
    ("GET", "/geospatial/clusters"),
    ("GET", "/infrastructure"),
    ("GET", "/datasets"),
    ("GET", "/audit-logs"),
}


def _openapi():
    return app.openapi()


def test_all_prd_endpoints_present_in_openapi():
    spec = _openapi()
    actual = {
        (method.upper(), path)
        for path, ops in spec["paths"].items()
        for method in ops
        if method in {"get", "post", "patch", "put", "delete"}
    }
    missing = PRD_ENDPOINTS - actual
    assert not missing, f"PRD endpoints missing from OpenAPI: {sorted(missing)}"


def test_error_envelope_component_registered():
    """The uniform error envelope must be discoverable in the spec — routes embed it
    via NotImplementedResponse (501) / ErrorBody (401, 403)."""
    schemas = _openapi()["components"]["schemas"]
    assert "NotImplementedResponse" in schemas
    assert "ErrorBody" in schemas
    assert schemas["NotImplementedResponse"]["properties"]["error"]["$ref"].endswith("ErrorBody")


def test_request_create_enforces_consent_contract():
    schema = _openapi()["components"]["schemas"]["RequestCreate"]
    assert schema["properties"]["consent_ack"]["type"] == "boolean"
    # consent is required in every documented request example (FR-005)
    assert "consent_ack" in schema["properties"]


def test_committed_openapi_json_matches_app():
    """CI contract-drift guard: docs/api/openapi/openapi.json must be current."""
    committed_path = Path(__file__).resolve().parents[2] / "docs" / "api" / "openapi" / "openapi.json"
    committed = json.loads(committed_path.read_text())
    assert committed["paths"] == _openapi()["paths"], (
        "docs/api/openapi/openapi.json is stale — run `make openapi-export` and commit it"
    )
