"""Infrastructure gap detection boundary — PRD FR-040–044.

TODO(PRD FR-040–044, Phase 2, Member C): rule engine comparing cluster demand
vs infrastructure coverage vs existing projects (FR-042 mandatory pre-flag
check). Benchmarks must be documented configuration, never literals (FR-041).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GapDetectionInput:
    cluster_id: int
    config: dict | None = None  # benchmark definitions injected at runtime


@dataclass
class GapDetectionOutput:
    gap_found: bool | None
    demand_summary: str | None
    gap_summary: str | None
    recommendation_summary: str | None
    conflicting_project_id: int | None
    uncertainty_notes: list[str]


def detect_gap(payload: GapDetectionInput) -> GapDetectionOutput:
    raise NotImplementedError("Gap detection is not implemented (scaffold)")
