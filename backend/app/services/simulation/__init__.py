"""Policy simulation boundary — PRD FR-053–056.

TODO(PRD FR-053–056, Phase 3, Member C): deterministic, repeatable scenario
runs (identical inputs ⇒ identical outputs — PRD §14). Cost-per-intervention
assumptions come from the curated dataset (synthetic, labelled), never literals
(FR-054/056, brief §26).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimulationInput:
    sector_allocations: dict[str, float]  # roads|water|health|education (₹)
    config: dict | None = None  # cost data injected at runtime


@dataclass
class SimulationOutput:
    scenario_id: str
    coverable_clusters_before: int | None
    coverable_clusters_after: int | None
    disclaimer: str  # FR-056 synthetic-cost disclosure


def run_scenario(payload: SimulationInput) -> SimulationOutput:
    raise NotImplementedError("Policy simulation is not implemented (scaffold)")
