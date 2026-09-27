"""Governance entities: `review_actions`, `audit_logs` (PRD §9.1, §6.10).

Human decisions are separate from AI suggestions (FR-063); every state change
must produce an audit row (FR-062).
"""

from typing import Optional

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._mixins import TimestampMixin


class ReviewAction(Base, TimestampMixin):
    __tablename__ = "review_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("needs_clusters.id"), index=True)
    reviewer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(30))  # approve|reject|request_more_evidence
    note: Mapped[str] = mapped_column(Text)  # required (FR-059)
    before_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    after_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    reviewer: Mapped[Optional["User"]] = relationship("User")


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100))
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    before_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # FR-062
    after_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    detail: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
