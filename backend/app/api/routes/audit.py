"""Audit trail routes (PRD §10.1 #17, FR-062)."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.deps import require_role
from app.schemas import AuditLogListResponse, NotImplementedResponse

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get(
    "",
    response_model=AuditLogListResponse,
    responses={501: {"model": NotImplementedResponse}},
    summary="Audit trail (admin)",
)
def list_audit_logs(user=Depends(require_role("admin"))) -> JSONResponse:
    """TODO(PRD FR-062): read audit_logs with filters."""
    payload = NotImplementedResponse().model_dump()
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=payload)
