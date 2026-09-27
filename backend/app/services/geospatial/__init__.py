"""Geospatial service boundary — PRD FR-026–033.

TODO(PRD FR-026–033, Phase 2, Member C): geocoding with confidence,
infrastructure proximity, population estimates, spatial aggregation.
Never fabricate coordinates (FR-021/033) — low-confidence results must map to
`location_unresolved`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GeoResolutionInput:
    location_text: str
    config: dict | None = None  # confidence threshold injected at runtime


@dataclass
class GeoResolutionOutput:
    latitude: float | None
    longitude: float | None
    confidence: float | None
    admin_hierarchy: dict | None  # {state, district, block, village_ward}
    resolved: bool


def resolve_location(payload: GeoResolutionInput) -> GeoResolutionOutput:
    raise NotImplementedError("Geospatial resolution is not implemented (scaffold)")


def nearest_infrastructure(latitude: float, longitude: float, asset_type: str) -> dict:
    """TODO(PRD FR-030): PostGIS nearest-match query over infrastructure_assets."""
    raise NotImplementedError("Infrastructure proximity is not implemented (scaffold)")
