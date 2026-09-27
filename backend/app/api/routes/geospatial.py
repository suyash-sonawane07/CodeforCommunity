"""Geospatial routes (PRD §10.1 #13) — map layer output."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models import Location, NeedsCluster
from app.schemas import GeoJSONFeature, GeoJSONFeatureCollection

router = APIRouter(prefix="/geospatial", tags=["geospatial"])


@router.get(
    "/clusters",
    response_model=GeoJSONFeatureCollection,
    summary="GeoJSON for map rendering — FR-029 (analyst+)",
)
def cluster_geojson(
    sector: Optional[str] = Query(default=None, alias="sector"),
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(require_role("analyst")),
) -> GeoJSONFeatureCollection:
    """Returns valid GeoJSON points for clusters. Unresolved locations have geometry: None (FR-021/033)."""
    query = db.query(NeedsCluster)
    if sector:
        query = query.filter(NeedsCluster.issue_type == sector)
    if district:
        query = query.join(Location, NeedsCluster.location_id == Location.id, isouter=True).filter(
            Location.district.ilike(f"%{district}%")
        )

    clusters = query.all()
    features: list[GeoJSONFeature] = []

    for c in clusters:
        geom = None
        loc_props = {}
        if c.location_id:
            loc = db.query(Location).filter(Location.id == c.location_id).first()
            if loc:
                loc_props = {
                    "village": loc.village_ward or loc.source_text,
                    "district": loc.district,
                    "block": loc.block,
                    "confidence": loc.confidence,
                }
                if loc.latitude is not None and loc.longitude is not None:
                    geom = {
                        "type": "Point",
                        "coordinates": [loc.longitude, loc.latitude],
                    }

        props = {
            "cluster_id": c.id,
            "issue_type": c.issue_type,
            "status": c.status,
            "review_status": c.review_status,
            "independent_demand_count": c.independent_demand_count,
            "raw_message_count": c.raw_message_count,
            "location_resolved": geom is not None,
            **loc_props,
        }

        features.append(GeoJSONFeature(type="Feature", geometry=geom, properties=props))

    return GeoJSONFeatureCollection(type="FeatureCollection", features=features)
