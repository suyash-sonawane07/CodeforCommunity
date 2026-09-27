"""Deterministic service boundaries must be present but unimplemented (scaffold rule)."""

import pytest

from app.services.clustering import ClusteringInput, cluster_requests
from app.services.evidence import EvidenceInput, build_evidence_panel
from app.services.gap_detection import GapDetectionInput, detect_gap
from app.services.geospatial import GeoResolutionInput, resolve_location
from app.services.prioritisation import PrioritisationInput, compute_priority
from app.services.simulation import SimulationInput, run_scenario


@pytest.mark.parametrize(
    "call,payload",
    [
        (cluster_requests, ClusteringInput()),
        (resolve_location, GeoResolutionInput(location_text="somewhere")),
        (detect_gap, GapDetectionInput(cluster_id=1)),
        (compute_priority, PrioritisationInput(cluster_id=1)),
        (build_evidence_panel, EvidenceInput(cluster_id=1)),
        (run_scenario, SimulationInput(sector_allocations={"roads": 1.0})),
    ],
)
def test_service_boundaries_raise_not_implemented(call, payload):
    with pytest.raises(NotImplementedError):
        call(payload)


def test_no_hardcoded_weights_in_boundaries():
    """Brief §26: config objects in, no baked-in algorithm values."""
    from dataclasses import fields

    from app.services.prioritisation import PrioritisationInput

    names = {f.name for f in fields(PrioritisationInput)}
    assert "weights" in names  # weights are injected, not module constants
