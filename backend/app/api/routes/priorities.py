from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.schemas.api import PrioritiesResponse, PriorityItem
from app.core.security import require_supervisor

router = APIRouter(prefix="/priorities", tags=["priorities"])

@router.get("", response_model=PrioritiesResponse)
def get_priorities(
    country: Optional[str] = Query(None),
    issue: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_supervisor)
):
    items = [
        PriorityItem(cluster_id=1, issue="Potholes", country="India", date="2023-01-01", rank=1, score=0.9),
        PriorityItem(cluster_id=2, issue="Water Leak", country="Brazil", date="2023-01-02", rank=2, score=0.8),
    ]
    if country:
        items = [i for i in items if i.country.lower() == country.lower()]
    if issue:
        items = [i for i in items if issue.lower() in i.issue.lower()]
    return PrioritiesResponse(items=items)
