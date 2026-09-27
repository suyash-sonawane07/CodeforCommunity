"""Geocoder — FR-026–028/033.

Implementations return `resolved=False` (no coordinates) when confidence is
below threshold — never guess (FR-021/033). Curated gazetteer first, OSM
Nominatim fallback per PRD §11.
"""

from typing import Protocol, runtime_checkable

from ai.interfaces.schemas import GeocodeResult


@runtime_checkable
class Geocoder(Protocol):
    name: str

    def geocode(self, location_text: str) -> GeocodeResult: ...
