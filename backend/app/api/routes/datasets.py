"""Dataset registry routes (PRD §10.1 #16, FR-038, FR-073)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models import PublicDataset
from app.schemas import DatasetInfo, DatasetListResponse

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get(
    "",
    response_model=DatasetListResponse,
    summary="Dataset registry + versions (admin)",
)
def list_datasets(
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
) -> DatasetListResponse:
    """Lists registered public datasets with versions and source labels (FR-038)."""
    datasets = db.query(PublicDataset).all()
    items = [
        DatasetInfo(
            id=d.id,
            name=d.name,
            source_label=d.source_label,
            version=d.version,
            ingested_at=d.ingested_at or (d.created_at.isoformat() if d.created_at else None),
        )
        for d in datasets
    ]
    return DatasetListResponse(items=items)
