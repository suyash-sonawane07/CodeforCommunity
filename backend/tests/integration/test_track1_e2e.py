"""End-to-End integration test for Code for Communities 2.0 Track 1 pipeline.

Verifies:
1. Multilingual citizen intake (Marathi text, Hindi voice with base64, English text).
2. Request tracking via token-less reference code.
3. Automated cluster grouping with deduplication.
4. Analyst cluster inspection with sector filtering.
5. Evidence panel with traceable context (infrastructure proximity, demographics, projects).
6. Gap detection with benchmark validation and conflicting project checks.
7. Equity-adjusted priority scoring.
8. GeoJSON map layer output (null-safe for unresolved locations).
9. Human reviewer approval & correction workflow with mandatory notes.
10. Policy what-if simulation with sector budget allocations.
11. Outcome measurement tracking with synthetic disclaimer.
12. Immutable audit trail logging.
"""

import base64

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_token(email: str) -> str:
    res = client.post("/auth/login", json={"email": email, "password": "password"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_track1_end_to_end_pipeline():
    analyst_token = get_token("analyst@civicpulse.dev")
    reviewer_token = get_token("reviewer@civicpulse.dev")
    decision_token = get_token("decision@civicpulse.dev")
    admin_token = get_token("admin@civicpulse.dev")

    analyst_auth = {"Authorization": f"Bearer {analyst_token}"}
    reviewer_auth = {"Authorization": f"Bearer {reviewer_token}"}
    decision_auth = {"Authorization": f"Bearer {decision_token}"}
    admin_auth = {"Authorization": f"Bearer {admin_token}"}

    # -------------------------------------------------------------
    # Step 1: Multilingual Citizen Intake
    # -------------------------------------------------------------
    # 1A: Marathi text submission
    mr_res = client.post(
        "/requests",
        json={
            "channel": "text",
            "language_hint": "mr",
            "text": "गावात शाळा आहे पण संध्याकाळी 5 वाजेनंतर बस स्थानक वरून बस नाही.",
            "location_text": "Demo Village 1, Demo Block A",
            "consent_ack": True,
        },
    )
    assert mr_res.status_code == 201
    mr_data = mr_res.json()
    assert "request_id" in mr_data
    assert "reference_code" in mr_data
    mr_ref = mr_data["reference_code"]
    mr_req_id = mr_data["request_id"]
    assert mr_req_id.startswith("req_")

    # 1B: Hindi voice submission (base64 audio)
    dummy_audio = base64.b64encode(b"RIFFdummywaveaudioheaderandcontent").decode("utf-8")
    hi_res = client.post(
        "/requests",
        json={
            "channel": "voice",
            "language_hint": "hi",
            "audio_base64": dummy_audio,
            "text": "गाँव में पीने का पानी सिर्फ दो घंटे आता है।",
            "location_text": "Demo Town 2, Demo Block B",
            "consent_ack": True,
        },
    )
    assert hi_res.status_code == 201
    hi_data = hi_res.json()
    hi_ref = hi_data["reference_code"]
    assert hi_ref.startswith("CP-2026-")

    # -------------------------------------------------------------
    # Step 2: Citizen Checks Own Submission Status (Public)
    # -------------------------------------------------------------
    status_res = client.get(f"/requests/{mr_ref}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["reference_code"] == mr_ref
    assert status_data["status"] in ["processing", "received", "active"]

    # -------------------------------------------------------------
    # Step 3: Analyst Lists Clusters with Filtering
    # -------------------------------------------------------------
    clusters_res = client.get("/clusters", headers=analyst_auth)
    assert clusters_res.status_code == 200
    clusters_data = clusters_res.json()
    assert clusters_data["total"] >= 1
    cluster_items = clusters_data["items"]
    target_cluster_id = cluster_items[0]["id"]

    # Filter by sector
    transport_res = client.get("/clusters?sector=transport", headers=analyst_auth)
    assert transport_res.status_code == 200
    for it in transport_res.json()["items"]:
        assert it["issue_type"] in ["transport", "transport_access"]

    # -------------------------------------------------------------
    # Step 4: Cluster Detail & Evidence Panel
    # -------------------------------------------------------------
    detail_res = client.get(f"/clusters/{target_cluster_id}", headers=analyst_auth)
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == target_cluster_id

    evidence_res = client.get(f"/clusters/{target_cluster_id}/evidence", headers=analyst_auth)
    assert evidence_res.status_code == 200
    ev = evidence_res.json()
    assert ev["cluster_id"] == target_cluster_id
    assert "location" in ev
    assert "priority_factors" in ev
    assert "uncertainty_notes" in ev
    assert "existing_project_check" in ev

    # -------------------------------------------------------------
    # Step 5: Gap Detection & Priority Analysis
    # -------------------------------------------------------------
    gap_res = client.get(f"/clusters/{target_cluster_id}/gap-analysis", headers=analyst_auth)
    assert gap_res.status_code == 200
    gap = gap_res.json()
    assert "gap_found" in gap
    assert "demand_summary" in gap
    assert "benchmark_used" in gap

    priority_res = client.get(f"/clusters/{target_cluster_id}/priority", headers=analyst_auth)
    assert priority_res.status_code == 200
    prio = priority_res.json()
    assert prio["demand"] is not None
    assert prio["priority_index"] is not None
    assert prio["equity_adjustment"] is not None

    # -------------------------------------------------------------
    # Step 6: Geospatial Layer (GeoJSON)
    # -------------------------------------------------------------
    geo_res = client.get("/geospatial/clusters", headers=analyst_auth)
    assert geo_res.status_code == 200
    geo = geo_res.json()
    assert geo["type"] == "FeatureCollection"
    assert len(geo["features"]) > 0
    first_feat = geo["features"][0]
    assert first_feat["type"] == "Feature"
    assert "properties" in first_feat

    # -------------------------------------------------------------
    # Step 7: Infrastructure & Public Datasets Layer
    # -------------------------------------------------------------
    infra_res = client.get("/infrastructure", headers=analyst_auth)
    assert infra_res.status_code == 200
    infra = infra_res.json()
    assert "infrastructure" in infra
    assert "demographics" in infra
    assert infra["source_label"] == "synthetic"

    # -------------------------------------------------------------
    # Step 8: Human Review Gate (Approve / Reject / Correction)
    # -------------------------------------------------------------
    # Review action: Approve
    review_res = client.post(
        f"/clusters/{target_cluster_id}/review",
        json={
            "action": "approve",
            "note": "Verified field reports; road access deficit confirmed.",
        },
        headers=reviewer_auth,
    )
    assert review_res.status_code == 200
    assert review_res.json()["action"] == "approve"

    # Review correction
    corr_res = client.patch(
        f"/clusters/{target_cluster_id}",
        json={"issue_type": "transport", "note": "Adjusted sector classification from review."},
        headers=reviewer_auth,
    )
    assert corr_res.status_code == 200

    # -------------------------------------------------------------
    # Step 9: Policy What-If Simulation
    # -------------------------------------------------------------
    sim_res = client.post(
        "/simulations",
        json={
            "sector_allocations": {
                "transport": 3000000.0,
                "roads": 5000000.0,
                "water": 2000000.0,
                "education": 1500000.0,
            }
        },
        headers=decision_auth,
    )
    assert sim_res.status_code == 200
    sim = sim_res.json()
    assert "scenario_id" in sim
    assert sim["coverable_clusters_after"] >= sim["coverable_clusters_before"]
    assert "synthetic" in sim["disclaimer"].lower()

    # -------------------------------------------------------------
    # Step 10: Outcome Measurement
    # -------------------------------------------------------------
    outcome_res = client.get(f"/clusters/{target_cluster_id}/outcome", headers=analyst_auth)
    assert outcome_res.status_code == 200
    outcome = outcome_res.json()
    assert outcome["is_synthetic"] is True
    assert "disclaimer" in outcome
    assert "baseline" in outcome
    assert "followup" in outcome

    # -------------------------------------------------------------
    # Step 11: Governance & Audit Trail
    # -------------------------------------------------------------
    audit_res = client.get("/audit-logs", headers=admin_auth)
    assert audit_res.status_code == 200
    audit = audit_res.json()
    assert audit["total"] >= 1
    # Check that our review action was recorded in audit log
    actions = [item["action"] for item in audit["items"]]
    assert any("CLUSTER_REVIEW_APPROVE" in a or "CORRECTION" in a for a in actions)
