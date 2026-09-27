"""Clustering service — PRD FR-019–025.

Groups related citizen requests by semantic similarity and geographic proximity.
Two-band thresholds (auto-merge / review) come from configuration.
Unresolved locations are excluded from spatial clustering (FR-021).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClusteringInput:
    """Typed input bundle for request clustering."""

    request_embeddings: list = field(default_factory=list)
    coordinates: list = field(default_factory=list)  # (lat, lon) | None entries
    timestamps: list = field(default_factory=list)
    config: Optional[dict] = None  # thresholds/time-window injected at runtime


@dataclass
class ClusteringOutput:
    assignments: list[Optional[int]] = field(default_factory=list)  # cluster id per request
    needs_review: list[int] = field(default_factory=list)  # uncertain-band requests (FR-025)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def cluster_requests(payload: ClusteringInput) -> ClusteringOutput:
    """Clusters requests based on embedding similarity and optional geospatial distance."""
    embeddings = payload.request_embeddings
    coords = payload.coordinates
    config = payload.config or {}

    auto_merge_threshold = config.get("auto_merge_threshold", 0.70)
    review_threshold = config.get("review_threshold", 0.45)
    max_distance_km = config.get("max_distance_km", 10.0)

    n = len(embeddings)
    if n == 0:
        return ClusteringOutput(assignments=[], needs_review=[])

    assignments: list[Optional[int]] = [None] * n
    needs_review: list[int] = []
    current_cluster_id = 1

    for i in range(n):
        if assignments[i] is not None:
            continue

        assignments[i] = current_cluster_id
        for j in range(i + 1, n):
            if assignments[j] is not None:
                continue

            # Semantic similarity check
            sim = _cosine_similarity(embeddings[i], embeddings[j])

            # Spatial distance check if both have coordinates
            within_geo = True
            c1 = coords[i] if i < len(coords) else None
            c2 = coords[j] if j < len(coords) else None
            if c1 and c2 and c1[0] is not None and c2[0] is not None:
                dist = _haversine_km(c1[0], c1[1], c2[0], c2[1])
                if dist > max_distance_km:
                    within_geo = False

            if within_geo and sim >= auto_merge_threshold:
                assignments[j] = current_cluster_id
            elif within_geo and sim >= review_threshold:
                if j not in needs_review:
                    needs_review.append(j)

        current_cluster_id += 1

    return ClusteringOutput(assignments=assignments, needs_review=needs_review)
