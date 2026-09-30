"""Phase 4 Acceptance & Integration Tests — Gap Detection & Explainable Prioritisation.

Verifies:
1. Realistic synthetic datasets for 3 BRICS countries (India, Brazil, South Africa) with source_label="synthetic" (FR-057).
2. Spatial gap detection: calculates per-capita deficit against sector benchmarks.
3. Conflicting project check: catches sanctioned/ongoing projects to prevent duplicate funding (FR-042).
4. Explainable priority scoring: transparent formula score = w_d*demand + w_g*gap + w_i*impact + w_e*equity - w_f*funded_penalty.
5. Evidence panel dossier: links every recommendation directly to evidence request IDs and citizen reference codes.
6. Incomplete data safety (FR-048): flags is_incomplete=True without silent default substitution.
"""

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models import CitizenRequest, ClusterMember, NeedsCluster, Project

client = TestClient(app)


def get_token(email: str) -> str:
    res = client.post("/auth/login", json={"email": email, "password": "password"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_brics_synthetic_datasets_registered_and_labeled():
    """FR-038 & FR-057: 3 BRICS synthetic datasets must be present and labeled source_label='synthetic'."""
    admin_token = get_token("admin@civicpulse.dev")
    res = client.get("/datasets", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    dataset_names = {d["name"]: d for d in data["items"]}

    # Verify India, Brazil, South Africa datasets
    assert "india_census_infrastructure_synthetic" in dataset_names
    assert "brazil_ibge_censo_synthetic" in dataset_names
    assert "south_africa_statssa_synthetic" in dataset_names

    # Check synthetic provenance labels
    assert dataset_names["india_census_infrastructure_synthetic"]["source_label"] == "synthetic"
    assert dataset_names["brazil_ibge_censo_synthetic"]["source_label"] == "synthetic"
    assert dataset_names["south_africa_statssa_synthetic"]["source_label"] == "synthetic"


def test_brics_infrastructure_and_demographics_layer():
    """FR-030/031: Infrastructure layer returns assets across BRICS sectors and demographics."""
    analyst_token = get_token("analyst@civicpulse.dev")
    res = client.get("/infrastructure", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "infrastructure" in data
    assert "demographics" in data
    assert data["source_label"] == "synthetic"

    asset_types = {a["asset_type"] for a in data["infrastructure"]}
    assert "water_point" in asset_types
    assert "power_substation" in asset_types
    assert "clinic" in asset_types
    assert "school" in asset_types

    # Ensure demographics contain population and deprivation indices
    for demo in data["demographics"]:
        assert demo["population"] is not None
        assert demo["deprivation_index"] is not None
        assert 0.0 <= demo["deprivation_index"] <= 1.0


def test_spatial_gap_detection_with_evidence_traceability():
    """FR-040–044: Gap detection calculates deficit and exposes evidence request IDs."""
    analyst_token = get_token("analyst@civicpulse.dev")
    db = SessionLocal()
    try:
        # Find Khayelitsha water cluster (severe water standpipe deficit, no conflicting project)
        zaf_req = db.query(CitizenRequest).filter(CitizenRequest.reference_code == "CP-2026-ZAF002").first()
        assert zaf_req is not None
        m_zaf = db.query(ClusterMember).filter(ClusterMember.request_id == zaf_req.id).first()
        assert m_zaf is not None
        cluster_id = m_zaf.cluster_id
    finally:
        db.close()

    res = client.get(f"/clusters/{cluster_id}/gap-analysis", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res.status_code == 200
    gap_data = res.json()

    assert gap_data["cluster_id"] == cluster_id
    assert gap_data["gap_found"] is True
    assert "benchmark_used" in gap_data
    assert "demand_summary" in gap_data
    assert "gap_summary" in gap_data
    assert "recommendation_summary" in gap_data

    # Explainable AI: Evidence request IDs and reference codes
    assert "evidence_request_ids" in gap_data
    assert zaf_req.id in gap_data["evidence_request_ids"]
    assert "evidence_reference_codes" in gap_data
    assert "CP-2026-ZAF002" in gap_data["evidence_reference_codes"]


def test_conflicting_project_detection_avoids_duplicate_funding():
    """FR-042: If an active/ongoing project exists in the catchment, flag conflict and avoid duplicate allocation."""
    analyst_token = get_token("analyst@civicpulse.dev")
    db = SessionLocal()
    try:
        # Paithan water cluster has an active project: "Jal Jeevan Mission Paithan Piped Water Scheme"
        ind_req = db.query(CitizenRequest).filter(CitizenRequest.reference_code == "CP-2026-IND001").first()
        assert ind_req is not None
        m_ind = db.query(ClusterMember).filter(ClusterMember.request_id == ind_req.id).first()
        assert m_ind is not None
        cluster_id = m_ind.cluster_id

        proj = db.query(Project).filter(Project.name == "Jal Jeevan Mission Paithan Piped Water Scheme").first()
        assert proj is not None
        expected_proj_id = proj.id
    finally:
        db.close()

    res = client.get(f"/clusters/{cluster_id}/gap-analysis", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res.status_code == 200
    gap_data = res.json()

    assert gap_data["gap_found"] is False
    assert gap_data["conflicting_project"] is not None
    assert gap_data["conflicting_project"]["id"] == expected_proj_id
    assert "Jal Jeevan Mission" in gap_data["conflicting_project"]["name"]
    assert gap_data["conflicting_project"]["status"] == "ongoing"
    assert "duplicate" in gap_data["recommendation_summary"].lower()


def test_transparent_priority_scoring_formula():
    """FR-045–050: Priority score = w_d*demand + w_g*gap + w_i*impact + w_e*equity - w_f*funded_penalty."""
    analyst_token = get_token("analyst@civicpulse.dev")
    db = SessionLocal()
    try:
        # Compare Paithan (has conflicting ongoing project) vs Khayelitsha (no conflicting project)
        ind_req = db.query(CitizenRequest).filter(CitizenRequest.reference_code == "CP-2026-IND001").first()
        zaf_req = db.query(CitizenRequest).filter(CitizenRequest.reference_code == "CP-2026-ZAF002").first()
        m_ind = db.query(ClusterMember).filter(ClusterMember.request_id == ind_req.id).first()
        m_zaf = db.query(ClusterMember).filter(ClusterMember.request_id == zaf_req.id).first()
        id_ind, id_zaf = m_ind.cluster_id, m_zaf.cluster_id
    finally:
        db.close()

    # Query priority for unconflicted cluster (Khayelitsha)
    res_zaf = client.get(f"/clusters/{id_zaf}/priority", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res_zaf.status_code == 200
    p_zaf = res_zaf.json()

    assert p_zaf["demand"] is not None
    assert p_zaf["gap"] is not None
    assert p_zaf["impact"] is not None
    assert p_zaf["equity_adjustment"] is not None
    assert p_zaf["funded_penalty"] == 0.0
    assert p_zaf["priority_index"] > 0.3
    assert p_zaf["is_incomplete"] is False
    assert zaf_req.id in p_zaf["evidence_request_ids"]

    # Verify formula calculation
    w = p_zaf["weights"]
    expected_score = round(
        w["demand"] * p_zaf["demand"]
        + w["gap"] * p_zaf["gap"]
        + w["impact"] * p_zaf["impact"]
        + w["equity"] * p_zaf["equity_adjustment"]
        - w.get("funded_penalty", 0.5) * p_zaf["funded_penalty"],
        4,
    )
    assert p_zaf["priority_index"] == expected_score

    # Query priority for conflicted cluster (Paithan)
    res_ind = client.get(f"/clusters/{id_ind}/priority", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res_ind.status_code == 200
    p_ind = res_ind.json()

    # Conflicted cluster must receive funded penalty
    assert p_ind["funded_penalty"] > 0.0
    # Penalty lowers priority index
    w_ind = p_ind["weights"]
    expected_ind_score = max(
        0.0,
        round(
            w_ind["demand"] * p_ind["demand"]
            + w_ind["gap"] * p_ind["gap"]
            + w_ind["impact"] * p_ind["impact"]
            + w_ind["equity"] * p_ind["equity_adjustment"]
            - w_ind.get("funded_penalty", 0.5) * p_ind["funded_penalty"],
            4,
        ),
    )
    assert p_ind["priority_index"] == expected_ind_score


def test_evidence_panel_dossier_explainable_ai():
    """FR-051–052: Evidence panel provides comprehensive traceable breakdown for decision-makers."""
    analyst_token = get_token("analyst@civicpulse.dev")
    db = SessionLocal()
    try:
        bra_req = db.query(CitizenRequest).filter(CitizenRequest.reference_code == "CP-2026-BRA001").first()
        assert bra_req is not None
        m_bra = db.query(ClusterMember).filter(ClusterMember.request_id == bra_req.id).first()
        assert m_bra is not None
        cluster_id = m_bra.cluster_id
    finally:
        db.close()

    res = client.get(f"/clusters/{cluster_id}/evidence", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res.status_code == 200
    ev = res.json()

    assert ev["cluster_id"] == cluster_id
    assert ev["issue_type"] == "sanitation"
    assert ev["location"]["village"] == "Favela da Maré"
    assert ev["location"]["state"] == "Rio de Janeiro"

    # Infrastructure context
    assert "infrastructure_context" in ev
    assert ev["infrastructure_context"]["source_label"] == "SYNTHETIC"
    assert ev["infrastructure_context"]["population_estimate"] == 24000
    assert ev["infrastructure_context"]["deprivation_index"] == 0.82

    # Explainable AI: Priority factor breakdown
    assert "priority_factors" in ev
    assert "formula" in ev["priority_factors"]
    assert "score = w_d*demand" in ev["priority_factors"]["formula"]

    # Evidence links to citizen reports
    assert "evidence_request_ids" in ev
    assert bra_req.id in ev["evidence_request_ids"]
    assert "evidence_reference_codes" in ev
    assert "CP-2026-BRA001" in ev["evidence_reference_codes"]


def test_incomplete_location_sets_is_incomplete_flag():
    """FR-048: Missing or unresolved location marks is_incomplete=True without guessing."""
    analyst_token = get_token("analyst@civicpulse.dev")
    db = SessionLocal()
    try:
        # Cluster 4 is seeded with an unresolved location
        unresolved_cluster = db.query(NeedsCluster).filter(NeedsCluster.issue_type == "roads", NeedsCluster.status == "forming").first()
        assert unresolved_cluster is not None
        cluster_id = unresolved_cluster.id
    finally:
        db.close()

    res = client.get(f"/clusters/{cluster_id}/priority", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res.status_code == 200
    p = res.json()
    assert p["is_incomplete"] is True
