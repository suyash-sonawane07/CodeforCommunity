"""Analysis & decision-support entities: `gap_analyses`, `priority_factors`,
`evidence_records`, `simulation_scenarios`, `interventions` (PRD §9.1).

No algorithm values are hard-coded here — the services (Member C) populate them.
"""

from typing import Optional

from sqlalchemy import JSON, Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._mixins import TimestampMixin


class GapAnalysis(Base, TimestampMixin):
    __tablename__ = "gap_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("needs_clusters.id"), index=True)
    gap_found: Mapped[bool] = mapped_column(Boolean, default=False)
    benchmark_used: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # FR-041
    conflicting_project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id"), nullable=True
    )  # FR-042
    demand_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # FR-044
    gap_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # FR-044
    recommendation_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # FR-044
    uncertainty_notes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)


class PriorityFactor(Base, TimestampMixin):
    __tablename__ = "priority_factors"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("needs_clusters.id"), index=True)
    demand: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    equity_adj: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weights: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # FR-046 config
    priority_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # computed
    is_incomplete: Mapped[bool] = mapped_column(Boolean, default=False)  # FR-048


class EvidenceRecord(Base, TimestampMixin):
    __tablename__ = "evidence_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("needs_clusters.id"), index=True)
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # FR-051 snapshot
    generated_at: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    generator_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(30), default="system")


class SimulationScenario(Base, TimestampMixin):
    __tablename__ = "simulation_scenarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    sector_allocations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # FR-053
    result_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    dataset_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class Intervention(Base, TimestampMixin):
    __tablename__ = "interventions"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("needs_clusters.id"), index=True)
    baseline_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # FR-064
    followup_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # FR-065
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True)  # FR-057 labelling
    status: Mapped[str] = mapped_column(String(30), default="planned")
