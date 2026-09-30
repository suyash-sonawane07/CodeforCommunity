"""Deterministic service boundaries tests — verifying typed inputs, outputs, and behaviors."""

from app.services.clustering import ClusteringInput, ClusteringOutput, cluster_requests
from app.services.evidence import EvidenceInput, EvidenceOutput, build_evidence_panel
from app.services.gap_detection import GapDetectionInput, GapDetectionOutput, detect_gap
from app.services.geospatial import GeoResolutionInput, GeoResolutionOutput, resolve_location
from app.services.prioritisation import PrioritisationInput, PrioritisationOutput, compute_priority
from app.services.simulation import SimulationInput, SimulationOutput, run_scenario


def test_clustering_service_execution():
    res = cluster_requests(
        ClusteringInput(
            request_embeddings=[[1.0, 0.0], [0.95, 0.05], [0.0, 1.0]],
            coordinates=[(19.87, 75.34), (19.88, 75.35), (20.50, 76.00)],
        )
    )
    assert isinstance(res, ClusteringOutput)
    assert len(res.assignments) == 3
    assert res.assignments[0] == res.assignments[1]  # Similar + nearby grouped together
    assert res.assignments[0] != res.assignments[2]  # Distant / dissimilar separate


def test_geospatial_resolution_service():
    res = resolve_location(GeoResolutionInput(location_text="Demo Village 1, Demo Block A"))
    assert isinstance(res, GeoResolutionOutput)
    assert res.resolved is True
    assert res.latitude == 19.876
    assert res.longitude == 75.343


def test_gap_detection_service():
    res = detect_gap(GapDetectionInput(cluster_id=1))
    assert isinstance(res, GapDetectionOutput)
    assert res.gap_found is not None
    assert res.demand_summary is not None
    assert res.gap_summary is not None
    assert res.recommendation_summary is not None


def test_prioritisation_service():
    res = compute_priority(PrioritisationInput(cluster_id=1))
    assert isinstance(res, PrioritisationOutput)
    assert res.demand is not None
    assert res.gap is not None
    assert res.impact is not None
    assert res.equity_adjustment is not None
    assert res.priority_index is not None
    assert res.is_incomplete is False


def test_evidence_service():
    res = build_evidence_panel(EvidenceInput(cluster_id=1))
    assert isinstance(res, EvidenceOutput)
    payload = res.payload
    assert payload["cluster_id"] == 1
    assert "independent_demand_count" in payload
    assert "priority_factors" in payload
    assert "uncertainty_notes" in payload


def test_simulation_service():
    res = run_scenario(SimulationInput(sector_allocations={"roads": 5000000.0, "water": 2000000.0}))
    assert isinstance(res, SimulationOutput)
    assert res.coverable_clusters_before is not None
    assert res.coverable_clusters_after is not None
    assert res.coverable_clusters_after >= res.coverable_clusters_before
    assert "synthetic" in res.disclaimer.lower()


def test_no_hardcoded_weights_in_boundaries():
    """Brief §26: config objects in, no baked-in algorithm values."""
    from dataclasses import fields

    names = {f.name for f in fields(PrioritisationInput)}
    assert "weights" in names  # weights are injected, not module constants
