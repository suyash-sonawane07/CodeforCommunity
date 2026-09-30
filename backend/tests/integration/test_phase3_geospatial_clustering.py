"""Phase 3 Acceptance & Integration Tests: Geospatial resolution & Demand Clustering.

Verifies:
1. Geocoder seeded gazetteer first, fallback, caching, and Location table lat/lng population.
2. cluster_requests() groups by issue_type + spatial proximity and computes deduplicated independent_demand_count.
3. GET /clusters, GET /clusters/{id}, and POST /clusters/{id}/review human review workflow.
"""

from ai.geocoding import CompositeGeocoder
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models import AuditLog, Location, ReviewAction
from app.services.clustering import ClusteringInput, cluster_requests

client = TestClient(app)


def get_token(email: str) -> str:
    res = client.post("/auth/login", json={"email": email, "password": "password"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_geocoder_resolution_and_caching():
    """Verify gazetteer resolution, lat/lon accuracy, and geocoder caching."""
    geocoder = CompositeGeocoder()

    # 1. Resolve seeded location
    res1 = geocoder.geocode("Demo Village 1, Demo Block A")
    assert res1.resolved is True
    assert res1.latitude is not None
    assert res1.longitude is not None
    assert round(res1.latitude, 2) == 19.88
    assert round(res1.longitude, 2) == 75.34

    # 2. Verify in-memory cache hit
    res2 = geocoder.geocode("Demo Village 1, Demo Block A")
    assert res2.resolved is True
    assert res2.latitude == res1.latitude
    assert res2.longitude == res1.longitude

    # 3. Verify location populated in DB from citizen intake
    submit_res = client.post(
        "/requests",
        json={
            "channel": "text",
            "text": "Deep potholes on the main highway.",
            "location_text": "Demo Village 1, Demo Block A",
            "consent_ack": True,
        },
    )
    assert submit_res.status_code == 201
    db = SessionLocal()
    try:
        loc = (
            db.query(Location)
            .filter(Location.village_ward.ilike("%Demo Village 1%"))
            .order_by(Location.id.desc())
            .first()
        )
        assert loc is not None
        assert loc.latitude is not None
        assert loc.longitude is not None
        assert loc.status == "resolved"
    finally:
        db.close()


def test_cluster_requests_algorithm_with_deduplication():
    """Verify cluster_requests groups by issue_type + space and deduplicates independent demand."""
    payload = ClusteringInput(
        request_embeddings=[
            [1.0, 0.0, 0.0],  # Item 0: water complaint A
            [1.0, 0.0, 0.0],  # Item 1: duplicate water complaint A (identical text)
            [0.92, 0.08, 0.0],  # Item 2: similar water complaint B (same village)
            [0.0, 1.0, 0.0],  # Item 3: road complaint C (different sector & distance)
        ],
        coordinates=[
            (19.876, 75.343),
            (19.876, 75.343),
            (19.880, 75.345),
            (20.500, 76.100),
        ],
        issue_types=["water", "water", "water", "roads"],
        raw_texts=[
            "No drinking water in sector 1",
            "No drinking water in sector 1",  # exact duplicate
            "Water supply pipe broken in sector 1",
            "Broken road near bus stand",
        ],
        channels=["telegram", "telegram", "web", "web"],
        user_identifiers=["user_1", "user_1", "user_2", "user_3"],
    )

    out = cluster_requests(payload)
    assert len(out.assignments) == 4
    # Items 0, 1, 2 cluster together
    assert out.assignments[0] == out.assignments[1] == out.assignments[2]
    # Item 3 in separate cluster
    assert out.assignments[3] != out.assignments[0]

    # Check cluster details & deduplication
    assert len(out.cluster_details) == 2
    water_cluster = next(c for c in out.cluster_details if c.issue_type == "water")
    assert water_cluster.raw_message_count == 3
    # Independent demand deduplicated to 2 because item 1 is a duplicate of item 0
    assert water_cluster.independent_demand_count == 2


def test_api_cluster_routes_and_review_workflow():
    """Verify GET /clusters, GET /clusters/{id}, and POST /clusters/{id}/review."""
    analyst_token = get_token("analyst@civicpulse.dev")
    reviewer_token = get_token("reviewer@civicpulse.dev")

    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}
    reviewer_headers = {"Authorization": f"Bearer {reviewer_token}"}

    # 1. Submit requests to ensure at least one water cluster exists
    client.post(
        "/requests",
        json={
            "channel": "text",
            "text": "Drinking water tap is broken in Demo Village 1",
            "location_text": "Demo Village 1, Demo Block A",
            "consent_ack": True,
        },
    )

    # 2. GET /clusters (analyst)
    list_res = client.get("/clusters", headers=analyst_headers)
    assert list_res.status_code == 200, list_res.text
    clusters_data = list_res.json()
    assert clusters_data["total"] >= 1
    assert len(clusters_data["items"]) >= 1

    target_cluster = clusters_data["items"][0]
    target_id = target_cluster["id"]

    # Test sector filter
    filtered_res = client.get(
        f"/clusters?sector={target_cluster['issue_type']}", headers=analyst_headers
    )
    assert filtered_res.status_code == 200
    for it in filtered_res.json()["items"]:
        assert it["issue_type"] == target_cluster["issue_type"]

    # 3. GET /clusters/{id} (analyst)
    detail_res = client.get(f"/clusters/{target_id}", headers=analyst_headers)
    assert detail_res.status_code == 200, detail_res.text
    detail_data = detail_res.json()
    assert detail_data["id"] == target_id
    assert "independent_demand_count" in detail_data
    assert "raw_message_count" in detail_data

    # 4. POST /clusters/{id}/review (reviewer) — Approve action
    review_res = client.post(
        f"/clusters/{target_id}/review",
        headers=reviewer_headers,
        json={
            "action": "approve",
            "note": "Community field visit verified persistent water supply outage.",
        },
    )
    assert review_res.status_code == 200, review_res.text
    review_data = review_res.json()
    assert review_data["cluster_id"] == target_id
    assert review_data["action"] == "approve"
    assert review_data["review_status"] == "approve"
    assert review_data["audit_log_id"] is not None

    # 5. Verify review status updated in GET /clusters/{id}
    updated_detail = client.get(f"/clusters/{target_id}", headers=analyst_headers).json()
    assert updated_detail["review_status"] == "approve"
    assert updated_detail["status"] == "approved"

    # 6. Verify audit trail and review action in DB
    db = SessionLocal()
    try:
        action_rec = (
            db.query(ReviewAction)
            .filter(ReviewAction.cluster_id == target_id)
            .order_by(ReviewAction.id.desc())
            .first()
        )
        assert action_rec is not None
        assert action_rec.action == "approve"

        audit_rec = (
            db.query(AuditLog)
            .filter(AuditLog.entity_id == target_id, AuditLog.action == "CLUSTER_REVIEW_APPROVE")
            .first()
        )
        assert audit_rec is not None
    finally:
        db.close()
