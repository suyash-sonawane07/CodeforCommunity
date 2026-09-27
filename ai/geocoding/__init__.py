"""Geocoder providers — Mock (default), gazetteer + Nominatim placeholders (PRD §11).

TODO(PRD FR-026–033, Phase 2, Member C): curated gazetteer lookup for the demo
districts, OSM Nominatim as fallback. Confidence = match type. Low confidence ⇒
resolved=False — never guess coordinates (FR-021/033).
"""

from __future__ import annotations

from typing import Optional

from ai.interfaces.schemas import GeocodeResult


class MockGeocoder:
    name = "mock"

    def geocode(self, location_text: str) -> GeocodeResult:
        """Offline default: never resolves, never fabricates coordinates."""
        return GeocodeResult(
            provider=self.name,
            confidence=None,
            resolved=False,
            admin_hierarchy=None,
            uncertainty_notes=["Mock geocoder — resolves nothing (FR-033 safe default)"],
        )


class GazetteerGeocoder:
    """Placeholder — curated gazetteer for 1 state / 2–3 demo districts."""

    name = "gazetteer"

    def __init__(self, entries: Optional[dict] = None) -> None:
        self.entries = entries or {}

    def geocode(self, location_text: str) -> GeocodeResult:
        raise NotImplementedError("GazetteerGeocoder is a placeholder — implement in Phase 2")


class NominatimGeocoder:
    """Placeholder — OSM Nominatim fallback; rate-limits must be respected."""

    name = "nominatim"

    def geocode(self, location_text: str) -> GeocodeResult:
        raise NotImplementedError("NominatimGeocoder is a placeholder — implement in Phase 2")
