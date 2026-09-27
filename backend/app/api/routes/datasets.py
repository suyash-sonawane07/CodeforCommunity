"""Dataset registry routes (PRD §10.1 #16, FR-038, FR-073).

SCAFFOLD: returns 501. Registry rows carry `source_label` ∈
{confirmed, candidate, synthetic} + `version` (FR-038).
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.deps import require_role
from app.schemas import DatasetListResponse, NotImplementedResponse

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get(
    "",
    response_model=DatasetListResponse,
    responses={501: {"model": NotImplementedResponse}},
    summary="Dataset registry + versions (admin)",
)
def list_datasets(user=Depends(require_role("admin"))) -> JSONResponse:
    """TODO(PRD FR-038/FR-073): read public_datasets."""
    payload = NotImplementedResponse().model_dump()
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=payload)
