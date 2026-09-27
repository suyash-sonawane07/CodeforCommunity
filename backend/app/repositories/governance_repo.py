"""Repository for ReviewAction and AuditLog entities."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import AuditLog, ReviewAction


class GovernanceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record_review_action(
        self,
        cluster_id: int,
        action: str,
        note: str,
        reviewer_id: Optional[int] = None,
        before_value: Optional[dict] = None,
        after_value: Optional[dict] = None,
    ) -> ReviewAction:
        review = ReviewAction(
            cluster_id=cluster_id,
            reviewer_id=reviewer_id,
            action=action,
            note=note,
            before_value=before_value,
            after_value=after_value,
        )
        self.db.add(review)
        self.db.flush()
        return review

    def create_audit_log(
        self,
        action: str,
        actor_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        before_value: Optional[dict] = None,
        after_value: Optional[dict] = None,
        detail: Optional[dict] = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_value=before_value,
            after_value=after_value,
            detail=detail,
        )
        self.db.add(log_entry)
        self.db.flush()
        return log_entry

    def list_audit_logs(
        self, entity_type: Optional[str] = None, limit: int = 100
    ) -> list[AuditLog]:
        query = self.db.query(AuditLog)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        return query.order_by(AuditLog.id.desc()).limit(limit).all()
