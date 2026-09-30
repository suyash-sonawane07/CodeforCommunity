"""Outcome measurement routes (PRD §10.1 #12, FR-064–067)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_supervisor
from app.schemas import OutcomeResponse
from app.services.evidence import build_outcome_snapshot

router = APIRouter(prefix="/clusters", tags=["outcomes"])


@router.get(
    "/{cluster_id}/outcome",
    response_model=OutcomeResponse,
    summary="Outcome measurement view — FR-064–067 (analyst+)",
)
def get_outcome(
    cluster_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_supervisor),
) -> OutcomeResponse:
    """Returns baseline vs synthetic followup indicators with correlation disclaimer (FR-067)."""
    snapshot = build_outcome_snapshot(cluster_id=cluster_id, db=db)
    return OutcomeResponse(**snapshot)
