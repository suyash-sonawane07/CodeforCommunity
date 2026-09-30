"""Clustering service — PRD FR-019–025.

Groups related citizen requests by semantic similarity and geographic proximity.
Two-band thresholds (auto-merge / review) come from configuration.
Unresolved locations are excluded from spatial clustering (FR-021).
Deduplicates independent demand from spam/duplicate messages (FR-024).
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
    issue_types: list[str] = field(default_factory=list)
    raw_texts: list[str] = field(default_factory=list)
    channels: list[str] = field(default_factory=list)
    user_identifiers: list[str] = field(default_factory=list)
    config: Optional[dict] = None  # thresholds/time-window injected at runtime


@dataclass
class ClusterSummaryInfo:
    cluster_id: int
    issue_type: str
    member_indices: list[int]
    similarity_scores: dict[int, float]
    independent_demand_count: int
    raw_message_count: int


@dataclass
class ClusteringOutput:
    assignments: list[Optional[int]] = field(default_factory=list)  # cluster id per request
    needs_review: list[int] = field(default_factory=list)  # uncertain-band requests (FR-025)
    cluster_details: list[ClusterSummaryInfo] = field(default_factory=list)


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


def compute_independent_demand_count(
    indices: list[int],
    raw_texts: list[str],
    channels: list[str],
    user_identifiers: list[str],
    embeddings: list[list[float]],
) -> int:
    """Deduplicates requests to prevent spam or near-duplicate messages

    from inflating demand (FR-024).
    """
    if not indices:
        return 0

    unique_groups: list[list[int]] = []

    for idx in indices:
        is_dup = False
        text_curr = raw_texts[idx].strip().lower() if idx < len(raw_texts) else ""
        chan_curr = channels[idx] if idx < len(channels) else ""
        user_curr = user_identifiers[idx] if idx < len(user_identifiers) else ""
        emb_curr = embeddings[idx] if idx < len(embeddings) else []

        for grp in unique_groups:
            rep = grp[0]
            text_rep = raw_texts[rep].strip().lower() if rep < len(raw_texts) else ""
            chan_rep = channels[rep] if rep < len(channels) else ""
            user_rep = user_identifiers[rep] if rep < len(user_identifiers) else ""
            emb_rep = embeddings[rep] if rep < len(embeddings) else []

            # Exact text match
            if text_curr and text_rep and text_curr == text_rep:
                is_dup = True
                grp.append(idx)
                break

            # Same user
            if user_curr and user_rep and user_curr == user_rep:
                is_dup = True
                grp.append(idx)
                break

            # Near-duplicate text from same channel (similarity >= 0.88)
            if chan_curr and chan_rep and chan_curr == chan_rep and emb_curr and emb_rep:
                sim = _cosine_similarity(emb_curr, emb_rep)
                if sim >= 0.88:
                    is_dup = True
                    grp.append(idx)
                    break

        if not is_dup:
            unique_groups.append([idx])

    return len(unique_groups)


def cluster_requests(payload: ClusteringInput) -> ClusteringOutput:
    """Clusters requests based on embedding similarity, sector type, and optional geospatial distance."""
    embeddings = payload.request_embeddings
    coords = payload.coordinates
    issue_types = payload.issue_types
    raw_texts = payload.raw_texts
    channels = payload.channels
    user_identifiers = payload.user_identifiers
    config = payload.config or {}

    auto_merge_threshold = config.get("auto_merge_threshold", 0.70)
    review_threshold = config.get("review_threshold", 0.45)
    max_distance_km = config.get("max_distance_km", 10.0)

    n = len(embeddings)
    if n == 0:
        return ClusteringOutput(assignments=[], needs_review=[], cluster_details=[])

    assignments: list[Optional[int]] = [None] * n
    needs_review: list[int] = []
    cluster_members_map: dict[int, list[int]] = {}
    similarity_map: dict[int, dict[int, float]] = {}
    current_cluster_id = 1

    for i in range(n):
        if assignments[i] is not None:
            continue

        assignments[i] = current_cluster_id
        cluster_members_map[current_cluster_id] = [i]
        similarity_map[current_cluster_id] = {i: 1.0}

        i_sector = issue_types[i] if i < len(issue_types) else None

        for j in range(i + 1, n):
            if assignments[j] is not None:
                continue

            j_sector = issue_types[j] if j < len(issue_types) else None
            if i_sector and j_sector and i_sector != j_sector:
                continue  # Different civic sectors never cluster together

            # Semantic similarity
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
                cluster_members_map[current_cluster_id].append(j)
                similarity_map[current_cluster_id][j] = round(sim, 3)
            elif within_geo and sim >= review_threshold:
                if j not in needs_review:
                    needs_review.append(j)

        current_cluster_id += 1

    # Build cluster summaries with independent demand count
    cluster_details = []
    for cid, members in cluster_members_map.items():
        primary_sector = (
            issue_types[members[0]] if (members and members[0] < len(issue_types)) else "other"
        )
        indep_count = compute_independent_demand_count(
            members, raw_texts, channels, user_identifiers, embeddings
        )
        cluster_details.append(
            ClusterSummaryInfo(
                cluster_id=cid,
                issue_type=primary_sector,
                member_indices=members,
                similarity_scores=similarity_map.get(cid, {}),
                independent_demand_count=max(1, indep_count),
                raw_message_count=len(members),
            )
        )

    return ClusteringOutput(
        assignments=assignments,
        needs_review=needs_review,
        cluster_details=cluster_details,
    )
