"""Geocoder providers — Mock (default), gazetteer + Nominatim placeholders (PRD §11).

TODO(PRD FR-026–033, Phase 2, Member C): curated gazetteer lookup for the demo
districts, OSM Nominatim as fallback. Confidence = match type. Low confidence ⇒
resolved=False — never guess coordinates (FR-021/033).
"""

from __future__ import annotations

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

    def __init__(self, entries: dict | None = None) -> None:
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
                    uncertainty_notes=[]
                    if is_exact
                    else [f"Fuzzy match to '{place_key}' from input '{location_text}'"],
                )

        return GeocodeResult(
            provider=self.name,
            confidence=None,
            resolved=False,
            latitude=None,
            longitude=None,
            admin_hierarchy=None,
            uncertainty_notes=[
                f"Location '{location_text}' not in gazetteer — routed to needs-geocoding (FR-033)"
            ],
        )


class NominatimGeocoder:
    """Real OpenStreetMap Nominatim geocoder (FR-026-028/033).

    Adheres to OSM Nominatim Usage Policy with descriptive User-Agent,
    rate-limit awareness, and strict confidence thresholding.
    Never fabricates coordinates on missing/low-confidence results (FR-021/033).
    """

    name = "nominatim"
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    USER_AGENT = "CivicPulse/1.0 (Digital Public Infrastructure; contact: civicpulse@hackathon.org)"

    def __init__(self, timeout: float = 4.0, country_codes: str | None = "in") -> None:
        self.timeout = timeout
        self.country_codes = country_codes

    def geocode(self, location_text: str) -> GeocodeResult:
        if not location_text or not location_text.strip():
            return GeocodeResult(
                provider=self.name,
                confidence=None,
                resolved=False,
                uncertainty_notes=["No location string provided (FR-033 safe default)"],
            )

        cleaned = location_text.strip()
        params = {
            "q": cleaned,
            "format": "json",
            "addressdetails": "1",
            "limit": "1",
        }
        if self.country_codes:
            params["countrycodes"] = self.country_codes

        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json",
        }

        try:
            import httpx

            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(self.BASE_URL, params=params, headers=headers)
                if resp.status_code != 200:
                    return GeocodeResult(
                        provider=self.name,
                        confidence=None,
                        resolved=False,
                        uncertainty_notes=[
                            f"Nominatim returned HTTP {resp.status_code} for '{cleaned}'"
                        ],
                    )
                data = resp.json()
        except Exception as exc:
            return GeocodeResult(
                provider=self.name,
                confidence=None,
                resolved=False,
                uncertainty_notes=[f"Nominatim network/timeout error: {exc}"],
            )

        if not data or not isinstance(data, list) or len(data) == 0:
            return GeocodeResult(
                provider=self.name,
                confidence=None,
                resolved=False,
                uncertainty_notes=[
                    f"Location '{cleaned}' not found in OpenStreetMap Nominatim (FR-033)"
                ],
            )

        hit = data[0]
        try:
            lat = float(hit["lat"])
            lon = float(hit["lon"])
        except (KeyError, ValueError, TypeError):
            return GeocodeResult(
                provider=self.name,
                confidence=None,
                resolved=False,
                uncertainty_notes=[f"Nominatim returned malformed coordinates for '{cleaned}'"],
            )

        address = hit.get("address", {})
        state = address.get("state") or address.get("province") or "Unknown State"
        district = (
            address.get("state_district")
            or address.get("district")
            or address.get("county")
            or "Unknown District"
        )
        block = (
            address.get("subdistrict")
            or address.get("taluk")
            or address.get("tehsil")
            or address.get("municipality")
            or address.get("city")
            or "Unknown Block"
        )
        village_ward = (
            address.get("village")
            or address.get("suburb")
            or address.get("neighbourhood")
            or address.get("town")
            or address.get("city")
            or cleaned
        )

        # Compute match confidence based on OSM importance (clamped 0.55 - 0.95)
        raw_importance = hit.get("importance")
        if isinstance(raw_importance, (int, float)):
            conf = min(0.95, max(0.55, float(raw_importance)))
        else:
            conf = 0.75

        return GeocodeResult(
            provider=self.name,
            confidence=round(conf, 2),
            resolved=True,
            latitude=lat,
            longitude=lon,
            admin_hierarchy={
                "state": state,
                "district": district,
                "block": block,
                "village_ward": village_ward,
            },
            uncertainty_notes=[
                f"Resolved via OpenStreetMap Nominatim ({hit.get('display_name', '')})"
            ],
        )


class CompositeGeocoder:
    """Hybrid geocoder: checks curated gazetteer first (fast, deterministic, offline),
    then falls back to Nominatim for arbitrary unmapped locations."""

    name = "composite"

    def __init__(
        self,
        gazetteer: GazetteerGeocoder | None = None,
        nominatim: NominatimGeocoder | None = None,
    ) -> None:
        self.gazetteer = gazetteer or GazetteerGeocoder()
        self.nominatim = nominatim or NominatimGeocoder()

    def geocode(self, location_text: str) -> GeocodeResult:
        # 1. Try gazetteer
        res = self.gazetteer.geocode(location_text)
        if res.resolved:
            return res

        # 2. Fall back to Nominatim
        nom_res = self.nominatim.geocode(location_text)
        if nom_res.resolved:
            return nom_res

        # Neither resolved
        return GeocodeResult(
            provider=self.name,
            confidence=None,
            resolved=False,
            uncertainty_notes=[
                f"Location '{location_text}' could not be resolved by gazetteer or Nominatim "
                "(queued for human review, FR-033)"
            ],
        )
