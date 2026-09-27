"""Infrastructure & demographic layer routes (PRD §10.1 #14, FR-030–031)."""

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models import DemographicIndicator, InfrastructureAsset, Location, PublicDataset
from app.schemas import InfrastructureLayerResponse

router = APIRouter(prefix="/infrastructure", tags=["infrastructure"])


@router.get(
    "",
    response_model=InfrastructureLayerResponse,
    summary="Infrastructure/demographic layer query — FR-030/031 (analyst+)",
)
def infrastructure_layer(
    asset_type: Optional[str] = None,
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(require_role("analyst")),
) -> InfrastructureLayerResponse:
    """Returns infrastructure assets and demographic indicators alongside dataset provenance (FR-057)."""
    # Assets query
    asset_q = db.query(InfrastructureAsset, Location).join(
        Location, InfrastructureAsset.location_id == Location.id, isouter=True
    )
    if asset_type:
        asset_q = asset_q.filter(InfrastructureAsset.asset_type == asset_type)
    if district:
        asset_q = asset_q.filter(Location.district.ilike(f"%{district}%"))

    assets = []
    for a, loc in asset_q.all():
        assets.append(
            {
                "id": a.id,
                "asset_type": a.asset_type,
                "name": a.name,
                "district": loc.district if loc else None,
                "village": loc.village_ward if loc else None,
                "latitude": loc.latitude if loc else None,
                "longitude": loc.longitude if loc else None,
                "dataset_version": a.dataset_version,
            }
        )

    # Demographics query
    demo_q = db.query(DemographicIndicator, Location).join(
        Location, DemographicIndicator.location_id == Location.id, isouter=True
    )
    if district:
        demo_q = demo_q.filter(Location.district.ilike(f"%{district}%"))

    demos = []
    for d, loc in demo_q.all():
        demos.append(
            {
                "id": d.id,
                "population": d.population,
                "deprivation_index": d.deprivation_index,
                "district": loc.district if loc else None,
                "village": loc.village_ward if loc else None,
                "dataset_version": d.dataset_version,
            }
        )

    dataset = db.query(PublicDataset).first()
    version = dataset.version if dataset else "synthetic_v0.1"
    source_label = dataset.source_label if dataset else "synthetic"

    return InfrastructureLayerResponse(
        infrastructure=assets,
        demographics=demos,
        dataset_version=version,
        source_label=source_label,
    )
