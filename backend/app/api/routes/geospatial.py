"""Geospatial routes (PRD §10.1 #13) — map layer output.

SCAFFOLD: returns 501. Unresolved locations must never appear with fabricated
coordinates (FR-021/033) — the eventual GeoJSON will carry null-geometry entries
for the "needs geocoding" list instead.
"""

from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.deps import require_role
from app.schemas import GeoJSONFeatureCollection, NotImplementedResponse

router = APIRouter(prefix="/geospatial", tags=["geospatial"])


def _not_implemented() -> JSONResponse:
    payload = NotImplementedResponse().model_dump()
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=payload)


@router.get(
    "/clusters",
    response_model=GeoJSONFeatureCollection,
    responses={501: {"model": NotImplementedResponse}},
    summary="GeoJSON for map rendering — FR-029 (analyst+)",
)
def cluster_geojson(
    sector: Optional[str] = None,
    district: Optional[str] = None,
    user=Depends(require_role("analyst")),
) -> JSONResponse:
    """TODO(PRD FR-029, FR-032, FR-033, Phase 2): PostGIS query → FeatureCollection."""
    return _not_implemented()
