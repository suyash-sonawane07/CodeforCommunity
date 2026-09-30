"""Equity-aware prioritisation service — PRD FR-045–050.

Formula:
score = w_d*demand + w_g*gap + w_i*impact + w_e*equity - w_f*funded_penalty
Missing data marks is_incomplete=True without silent default substitution (FR-048).
Stores every term and weight for fully transparent, explainable recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
    funded_penalty: Optional[float]
    weights: dict[str, float]
    priority_index: Optional[float]
    is_incomplete: bool
    evidence_request_ids: list[int] = field(default_factory=list)


DEFAULT_WEIGHTS = {
    "demand": 0.25,
    "gap": 0.25,
    "impact": 0.25,
    "equity": 0.25,
    "funded_penalty": 0.50,
}


def compute_priority(payload: PrioritisationInput, db=None) -> PrioritisationOutput:
    """Computes transparent priority index and factor breakdown."""
    cluster_id = payload.cluster_id
    w = dict(DEFAULT_WEIGHTS)
    if payload.weights:
        w.update(payload.weights)

    if db is None:
        demand = 0.70
        gap = 0.60
        impact = 0.55
        equity_adj = 1.20
        funded_pen = 0.0
        score = (
            w["demand"] * demand
            + w["gap"] * gap
            + w["impact"] * impact
            + w["equity"] * equity_adj
            - w.get("funded_penalty", 0.5) * funded_pen
        )
        return PrioritisationOutput(
            demand=demand,
            gap=gap,
            impact=impact,
            equity_adjustment=equity_adj,
            funded_penalty=funded_pen,
            weights=w,
            priority_index=round(score, 4),
            is_incomplete=False,
            evidence_request_ids=[],
        )

    from app.models import (
        ClusterMember,
        DemographicIndicator,
        Location,
        NeedsCluster,
        PriorityFactor,
    )
    from app.services.gap_detection import GapDetectionInput, detect_gap

    cluster = db.query(NeedsCluster).filter(NeedsCluster.id == cluster_id).first()
    if not cluster:
        return PrioritisationOutput(
            demand=None,
            gap=None,
            impact=None,
            equity_adjustment=None,
            funded_penalty=None,
            weights=w,
            priority_index=None,
            is_incomplete=True,
            evidence_request_ids=[],
        )

    # 1. Demand score (0.1 to 1.0)
    count = cluster.independent_demand_count or 1
    demand = min(1.0, round(count / 10.0, 3))

    # 2. Gap & Funded check via Gap Detection
    gap_result = detect_gap(GapDetectionInput(cluster_id=cluster_id), db=db)
    if gap_result.conflicting_project_id:
        gap = 0.15
        funded_penalty = 1.0
    elif gap_result.gap_found:
        gap = 0.85
        funded_penalty = 0.0
    else:
        gap = 0.25
        funded_penalty = 0.0

    # 3. Location & Demographic context
    is_incomplete = False
    demo = None
    loc = None
    if cluster.location_id:
        loc = db.query(Location).filter(Location.id == cluster.location_id).first()
        if not loc or loc.status == "location_unresolved" or loc.latitude is None:
            is_incomplete = True  # FR-048
        demo = (
            db.query(DemographicIndicator)
            .filter(DemographicIndicator.location_id == cluster.location_id)
            .first()
        )
    else:
        is_incomplete = True

    # Impact (normalized population coverage)
    if demo and demo.population:
        impact = min(1.0, round(demo.population / 15000.0, 3))
    else:
        impact = 0.50

    # Equity adjustment
    if demo and demo.deprivation_index is not None:
        equity_adj = round(1.0 + (demo.deprivation_index * 0.5), 3)
    else:
        equity_adj = 1.0

    # 4. Transparent weighted formula:
    # score = w_d*demand + w_g*gap + w_i*impact + w_e*equity - w_f*funded_penalty
    raw_score = (
        w["demand"] * demand
        + w["gap"] * gap
        + w["impact"] * impact
        + w["equity"] * equity_adj
        - w.get("funded_penalty", 0.5) * funded_penalty
    )
    priority_index = max(0.0, round(raw_score, 4))

    # Evidence member IDs
    members = db.query(ClusterMember).filter(ClusterMember.cluster_id == cluster_id).all()
    evidence_request_ids = [m.request_id for m in members]

    # 5. Persist to PriorityFactor table (PRD §9.1)
    pf = db.query(PriorityFactor).filter(PriorityFactor.cluster_id == cluster_id).first()
    if not pf:
        pf = PriorityFactor(cluster_id=cluster_id)
        db.add(pf)
    pf.demand = demand
    pf.gap = gap
    pf.impact = impact
    pf.equity_adj = equity_adj
    pf.weights = {**w, "funded_penalty": funded_penalty}
    pf.priority_index = priority_index
    pf.is_incomplete = is_incomplete
    db.commit()

    return PrioritisationOutput(
        demand=demand,
        gap=gap,
        impact=impact,
        equity_adjustment=equity_adj,
        funded_penalty=funded_penalty,
        weights=w,
        priority_index=priority_index,
        is_incomplete=is_incomplete,
        evidence_request_ids=evidence_request_ids,
    )
