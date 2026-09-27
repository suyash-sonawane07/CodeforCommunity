"""Equity-aware prioritisation boundary — PRD FR-045–050.

Illustrative model: Priority Index = Demand × Gap × Impact × Equity Adjustment
(PRD §6.7 — explicitly NOT a validated formula). TODO(PRD FR-045–050, Phase 2,
Member C): implement with per-factor normalisation (FR-047), configurable
weights (FR-046) and missing-data handling (FR-048: excluded + flagged, never
silently defaulted).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PrioritisationInput:
    cluster_id: int
    weights: dict[str, float] | None = None  # injected; defaults equal (FR-046)


@dataclass
class PrioritisationOutput:
    demand: float | None
    gap: float | None
    impact: float | None
    equity_adjustment: float | None
    priority_index: float | None
    is_incomplete: bool


def compute_priority(payload: PrioritisationInput) -> PrioritisationOutput:
    raise NotImplementedError("Prioritisation is not implemented (scaffold)")
