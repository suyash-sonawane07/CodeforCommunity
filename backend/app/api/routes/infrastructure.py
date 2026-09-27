"""Infrastructure & demographic layer routes (PRD §10.1 #14, FR-030–031).

SCAFFOLD: returns 501. Responses must include the dataset provenance label
(`source_label`) so the UI can show the SYNTHETIC badge (FR-057).
"""

from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.deps import require_role
from app.schemas import InfrastructureLayerResponse, NotImplementedResponse

router = APIRouter(prefix="/infrastructure", tags=["infrastructure"])


def _not_implemented() -> JSONResponse:
    payload = NotImplementedResponse().model_dump()
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=payload)


@router.get(
    "",
    response_model=InfrastructureLayerResponse,
    responses={501: {"model": NotImplementedResponse}},
    summary="Infrastructure/demographic layer query — FR-030/031 (analyst+)",
)
def infrastructure_layer(
    asset_type: Optional[str] = None,
    district: Optional[str] = None,
    user=Depends(require_role("analyst")),
) -> JSONResponse:
    """TODO(PRD FR-030–031, Phase 2): query curated tables with dataset_version."""
    return _not_implemented()
