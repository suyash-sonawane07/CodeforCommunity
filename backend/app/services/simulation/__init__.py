"""Policy simulation service — PRD FR-053–056.

Deterministic scenario planning modeling cluster coverage based on sector allocations.
Cost benchmarks are configurable and clearly disclosed as synthetic (FR-056).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional


@dataclass
class SimulationInput:
    sector_allocations: dict[str, float]  # roads|water|health|education (₹)
    config: Optional[dict] = None  # cost data injected at runtime


@dataclass
class SimulationOutput:
    scenario_id: str
    coverable_clusters_before: Optional[int]
    coverable_clusters_after: Optional[int]
    disclaimer: str  # FR-056 synthetic-cost disclosure


SECTOR_BENCHMARK_COSTS = {
    "roads": 2500000.0,  # ₹25 Lakhs per km / upgrade
    "transport": 1500000.0,  # ₹15 Lakhs per route feeder/stop
    "water": 1000000.0,  # ₹10 Lakhs per borewell/distribution
    "education": 1200000.0,  # ₹12 Lakhs per toilet block/classroom
    "health": 2000000.0,  # ₹20 Lakhs per sub-centre enhancement
}


def run_scenario(payload: SimulationInput, db=None) -> SimulationOutput:
    """Simulates how many citizen demand clusters can be addressed given sector budgets."""
    allocations = payload.sector_allocations
    scenario_id = f"sim_{uuid.uuid4().hex[:8]}"

    total_clusters = 1
    if db is not None:
        from app.models import NeedsCluster

        total_clusters = db.query(NeedsCluster).count() or 1

    # Baseline coverable clusters before new allocation
    before = max(1, int(total_clusters * 0.25))

    additional_covered = 0
    for sector, budget in allocations.items():
        cost = SECTOR_BENCHMARK_COSTS.get(sector, 1500000.0)
        if budget > 0:
            additional_covered += int(budget // cost)

    after = min(total_clusters + 5, before + additional_covered)

    return SimulationOutput(
        scenario_id=scenario_id,
        coverable_clusters_before=before,
        coverable_clusters_after=after,
        disclaimer=(
            "Estimates use synthetic/curated cost data — not official budget figures (FR-056)"
        ),
    )
