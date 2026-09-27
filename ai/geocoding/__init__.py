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
    """Curated gazetteer lookup for demo districts and Indian administrative places (FR-026-028)."""

    name = "gazetteer"

    DEFAULT_ENTRIES = {
        "demo village 1": {
            "latitude": 19.876,
            "longitude": 75.343,
            "admin_hierarchy": {
                "state": "Demo State",
                "district": "Demo District 1",
                "block": "Demo Block A",
                "village_ward": "Demo Village 1",
            },
        },
        "डेमो गाँव 1": {
            "latitude": 19.876,
            "longitude": 75.343,
            "admin_hierarchy": {
                "state": "Demo State",
                "district": "Demo District 1",
                "block": "Demo Block A",
                "village_ward": "Demo Village 1",
            },
        },
        "डेमो गाव 1": {
            "latitude": 19.876,
            "longitude": 75.343,
            "admin_hierarchy": {
                "state": "Demo State",
                "district": "Demo District 1",
                "block": "Demo Block A",
                "village_ward": "Demo Village 1",
            },
        },
        "demo town 2": {
            "latitude": 19.990,
            "longitude": 75.180,
            "admin_hierarchy": {
                "state": "Demo State",
                "district": "Demo District 2",
                "block": "Demo Block B",
                "village_ward": "Demo Town 2",
            },
        },
        "डेमो टाउन 2": {
            "latitude": 19.990,
            "longitude": 75.180,
            "admin_hierarchy": {
                "state": "Demo State",
                "district": "Demo District 2",
                "block": "Demo Block B",
                "village_ward": "Demo Town 2",
            },
        },
        "aurangabad": {
            "latitude": 19.8762,
            "longitude": 75.3433,
            "admin_hierarchy": {
                "state": "Maharashtra",
                "district": "Chhatrapati Sambhajinagar",
                "block": "Aurangabad",
                "village_ward": "Aurangabad",
            },
        },
        "pune": {
            "latitude": 18.5204,
            "longitude": 73.8567,
            "admin_hierarchy": {
                "state": "Maharashtra",
                "district": "Pune",
                "block": "Haveli",
                "village_ward": "Pune",
            },
        },
    }

    def __init__(self, entries: Optional[dict] = None) -> None:
        self.entries = entries if entries is not None else self.DEFAULT_ENTRIES

    def geocode(self, location_text: str) -> GeocodeResult:
        if not location_text or not location_text.strip():
            return GeocodeResult(
                provider=self.name,
                confidence=None,
                resolved=False,
                uncertainty_notes=["No location string provided (FR-033 safe default)"],
            )

        cleaned = location_text.lower().strip()

        # Check exact or substring matches
        for place_key, data in self.entries.items():
            if place_key in cleaned or cleaned in place_key:
                is_exact = place_key == cleaned
                conf = 0.95 if is_exact else 0.82
                return GeocodeResult(
                    provider=self.name,
                    confidence=conf,
                    resolved=True,
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    admin_hierarchy=data["admin_hierarchy"],
                    uncertainty_notes=[] if is_exact else [f"Fuzzy match to '{place_key}' from input '{location_text}'"],
                )

        return GeocodeResult(
            provider=self.name,
            confidence=None,
            resolved=False,
            latitude=None,
            longitude=None,
            admin_hierarchy=None,
            uncertainty_notes=[f"Location '{location_text}' not in gazetteer — routed to needs-geocoding (FR-033)"],
        )


class NominatimGeocoder:
    """Placeholder — OSM Nominatim fallback; rate-limits must be respected."""

    name = "nominatim"

    def geocode(self, location_text: str) -> GeocodeResult:
        raise NotImplementedError("NominatimGeocoder is a placeholder — implement in Phase 2")
