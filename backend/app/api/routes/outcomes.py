"""Outcome measurement routes (PRD §10.1 #12, FR-064–067).

SCAFFOLD: returns 501. Outcome views must carry the correlation-not-causation
disclaimer (FR-067) and synthetic labelling (FR-057).
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.deps import require_role
from app.schemas import NotImplementedResponse, OutcomeResponse

router = APIRouter(prefix="/clusters", tags=["outcomes"])


@router.get(
    "/{cluster_id}/outcome",
    response_model=OutcomeResponse,
    responses={501: {"model": NotImplementedResponse}},
    summary="Outcome measurement view — FR-064–067 (analyst+)",
)
def get_outcome(cluster_id: int, user=Depends(require_role("analyst"))) -> JSONResponse:
    """TODO(PRD FR-064–067, Phase 3): baseline vs synthetic followup snapshot."""
    payload = NotImplementedResponse().model_dump()
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=payload)
