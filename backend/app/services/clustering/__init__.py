"""Clustering service boundary — PRD FR-019–025.

TODO(PRD FR-019–025, Phase 2, Member C): implement embedding-based similarity
+ geo/time-windowed clustering. Two-band thresholds (auto-merge / review) must
come from configuration, not literals. Unresolved locations are excluded from
spatial clustering and kept in a "needs location" queue (FR-021).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClusteringInput:
    """Typed input bundle. Populated by the intake pipeline later."""

    request_embeddings: list = field(default_factory=list)
    coordinates: list = field(default_factory=list)  # (lat, lon) | None entries
    timestamps: list = field(default_factory=list)
    config: Optional[dict] = None  # thresholds/time-window injected at runtime


@dataclass
class ClusteringOutput:
    assignments: list[int | None] = field(default_factory=list)  # cluster id per request
    needs_review: list[int] = field(default_factory=list)  # uncertain-band requests (FR-025)


def cluster_requests(payload: ClusteringInput) -> ClusteringOutput:
    """Placeholder — raises until Member C implements it."""
    raise NotImplementedError("Clustering is not implemented (scaffold)")
