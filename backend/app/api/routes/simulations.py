"""Policy simulator routes (PRD §10.1 #15, FR-053–056)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models import SimulationScenario, User
from app.schemas import SimulationCreate, SimulationResult
from app.services.simulation import SimulationInput, run_scenario

router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.post(
    "",
    response_model=SimulationResult,
    summary="Run a policy what-if scenario — FR-053–056 (decision_maker+)",
)
def run_simulation(
    body: SimulationCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("decision_maker")),
) -> SimulationResult:
    """Executes deterministic scenario planning and returns coverage outcomes."""
    out = run_scenario(SimulationInput(sector_allocations=body.sector_allocations), db=db)

    # Persist scenario run
    user_email = user.email if hasattr(user, "email") else user.get("subject")
    u = db.query(User).filter(User.email == user_email).first()
    user_id = u.id if u else None

    scenario = SimulationScenario(
        user_id=user_id,
        sector_allocations=body.sector_allocations,
        result_payload={
            "coverable_clusters_before": out.coverable_clusters_before,
            "coverable_clusters_after": out.coverable_clusters_after,
        },
        dataset_version="synthetic_v0.1",
    )
    db.add(scenario)
    db.commit()

    return SimulationResult(
        scenario_id=out.scenario_id,
        sector_allocations=body.sector_allocations,
        coverable_clusters_before=out.coverable_clusters_before,
        coverable_clusters_after=out.coverable_clusters_after,
        disclaimer=out.disclaimer,
    )
