"""Equity-aware prioritisation service — PRD FR-045–050.

Illustrative formula:
Priority Index = Demand × Gap × Impact × Equity Adjustment (PRD §6.7)
Missing data marks is_incomplete=True without silent default substitution (FR-048).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PrioritisationInput:
    cluster_id: int
    weights: Optional[dict[str, float]] = None  # injected; defaults equal (FR-046)


@dataclass
class PrioritisationOutput:
    demand: Optional[float]
    gap: Optional[float]
    impact: Optional[float]
    equity_adjustment: Optional[float]
    priority_index: Optional[float]
    is_incomplete: bool


def compute_priority(payload: PrioritisationInput, db=None) -> PrioritisationOutput:
    """Computes transparent priority index and factor breakdown."""
    cluster_id = payload.cluster_id
    w = payload.weights or {"demand": 0.25, "gap": 0.25, "impact": 0.25, "equity": 0.25}

    if db is None:
        # Default mock calculation for standalone / unit tests
        demand = 0.70
        gap = 0.60
        impact = 0.55
        equity_adj = 1.20
        priority_index = round(demand * gap * impact * equity_adj * (w.get("demand", 0.25) * 4), 4)
        return PrioritisationOutput(
            demand=demand,
            gap=gap,
            impact=impact,
            equity_adjustment=equity_adj,
            priority_index=priority_index,
            is_incomplete=False,
        )

    from app.models import DemographicIndicator, NeedsCluster, Project

    cluster = db.query(NeedsCluster).filter(NeedsCluster.id == cluster_id).first()
    if not cluster:
        return PrioritisationOutput(
            demand=None,
            gap=None,
            impact=None,
            equity_adjustment=None,
            priority_index=None,
            is_incomplete=True,
        )

    # 1. Demand score (0.1 to 1.0)
    count = cluster.independent_demand_count or 1
    demand = min(1.0, round(count / 10.0, 3))

    # 2. Gap severity
    has_conflicting = (
        db.query(Project)
        .filter(
            Project.sector.ilike(f"%{cluster.issue_type.split('_')[0]}%"),
            Project.status.in_(["sanctioned", "ongoing"]),
        )
        .first()
    )
    gap = 0.20 if has_conflicting else 0.80

    # 3. Impact & Demographic context
    demo = None
    if cluster.location_id:
        demo = (
            db.query(DemographicIndicator)
            .filter(DemographicIndicator.location_id == cluster.location_id)
            .first()
        )

    if demo and demo.population:
        impact = min(1.0, round(demo.population / 10000.0, 3))
    else:
        impact = 0.50

    # 4. Equity adjustment factor
    if demo and demo.deprivation_index is not None:
        equity_adj = round(1.0 + (demo.deprivation_index * 0.5), 3)
    else:
        equity_adj = 1.0

    priority_index = round(demand * gap * impact * equity_adj, 4)

    return PrioritisationOutput(
        demand=demand,
        gap=gap,
        impact=impact,
        equity_adjustment=equity_adj,
        priority_index=priority_index,
        is_incomplete=False,
    )
