"""Audit trail routes (PRD §10.1 #17, FR-062)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_supervisor
from app.models import AuditLog
from app.schemas import AuditLogEntry, AuditLogListResponse

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get(
    "",
    response_model=AuditLogListResponse,
    summary="Audit trail (admin)",
)
def list_audit_logs(
    db: Session = Depends(get_db),
    user=Depends(require_supervisor),
) -> AuditLogListResponse:
    """Returns an immutable audit log trail for governance and review actions (FR-062)."""
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(100).all()
    items = [
        AuditLogEntry(
            id=entry.id,
            actor_id=entry.actor_id,
            action=entry.action,
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            before_value=entry.before_value,
            after_value=entry.after_value,
            created_at=entry.created_at.isoformat() if entry.created_at else None,
        )
        for entry in logs
    ]
    return AuditLogListResponse(items=items, total=len(items))
