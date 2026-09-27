"""Policy simulator routes (PRD §10.1 #15, FR-053–056).

SCAFFOLD: returns 501. No budget/cost assumptions are hard-coded anywhere (brief §26);
the service will consume configurable cost data from the curated dataset.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.deps import require_role
from app.schemas import NotImplementedResponse, SimulationCreate, SimulationResult

router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.post(
    "",
    response_model=SimulationResult,
    responses={501: {"model": NotImplementedResponse}},
    summary="Run a policy what-if scenario — FR-053–056 (decision_maker+)",
)
def run_simulation(
    body: SimulationCreate, user=Depends(require_role("decision_maker"))
) -> JSONResponse:
    """TODO(PRD FR-053–056, Phase 3, Member C logic + B API): deterministic scenario run."""
    payload = NotImplementedResponse().model_dump()
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=payload)
