"""Demand clustering entities: `needs_clusters`, `cluster_members` (PRD §9.1, §6.3).

Cluster lifecycle (FR-022): forming → active → under_review → approved/rejected → archived.
`independent_demand_count` is the deduplicated count; `raw_message_count` shown alongside
it always (FR-024). `review_status` is deliberately separate from `status` (FR-063).
"""

from typing import List, Optional

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._mixins import TimestampMixin


class NeedsCluster(Base, TimestampMixin):
    __tablename__ = "needs_clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    issue_type: Mapped[str] = mapped_column(String(50), index=True)  # FR-014 taxonomy
    status: Mapped[str] = mapped_column(String(30), default="forming", index=True)  # FR-022
    review_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # FR-063
    independent_demand_count: Mapped[int] = mapped_column(Integer, default=0)  # FR-024
    raw_message_count: Mapped[int] = mapped_column(Integer, default=0)
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"), nullable=True, index=True
    )
    time_window_start: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    time_window_end: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    uncertainty_notes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # §25
    dataset_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    members: Mapped[List["ClusterMember"]] = relationship("ClusterMember", back_populates="cluster")


class ClusterMember(Base, TimestampMixin):
    __tablename__ = "cluster_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("needs_clusters.id"), index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("citizen_requests.id"), index=True)
    similarity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # FR-019
    assignment: Mapped[str] = mapped_column(String(20), default="auto")  # auto | review | human

    cluster: Mapped["NeedsCluster"] = relationship("NeedsCluster", back_populates="members")
    request: Mapped["CitizenRequest"] = relationship("CitizenRequest")
