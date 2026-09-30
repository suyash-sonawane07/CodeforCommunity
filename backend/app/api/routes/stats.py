from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.api import StatsResponse
from app.core.security import require_supervisor

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db), current_user = Depends(require_supervisor)):
    return StatsResponse(
        totals=100,
        hotspots=["Pune", "Mumbai"],
        critical_gaps=5,
        approved=20
    )
