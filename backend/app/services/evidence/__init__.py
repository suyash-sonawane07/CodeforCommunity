"""Evidence generation boundary — PRD FR-051–052 (+ FR-064–067 outcome snapshots).

TODO(PRD FR-051–052, Phase 2, Member C): assemble the evidence panel purely
from stored fields + documented formulas — no invented numbers (FR-052).
Outcome part (Phase 3): baseline/followup snapshots with synthetic labelling
(FR-065/057) and the correlation-not-causation disclaimer (FR-067).
"""

from dataclasses import dataclass


@dataclass
class EvidenceInput:
    cluster_id: int


@dataclass
class EvidenceOutput:
    payload: dict  # matches schemas.EvidencePanel shape


def build_evidence_panel(payload: EvidenceInput) -> EvidenceOutput:
    raise NotImplementedError("Evidence generation is not implemented (scaffold)")


def build_outcome_snapshot(cluster_id: int) -> dict:
    """TODO(PRD FR-064–067, Phase 3): baseline vs synthetic followup + disclaimer."""
    raise NotImplementedError("Outcome snapshots are not implemented (scaffold)")
