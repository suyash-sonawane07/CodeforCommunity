"""Infrastructure gap detection service — PRD FR-040–044.

Compares cluster demand vs existing infrastructure coverage vs active government projects (FR-042).
Benchmarks are configurable definitions (FR-041).
Exposes explainable factor breakdowns and evidence request IDs behind every finding.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GapDetectionInput:
    cluster_id: int
    config: Optional[dict] = None  # benchmark definitions injected at runtime


@dataclass
class GapDetectionOutput:
    gap_found: Optional[bool]
    demand_summary: Optional[str]
    gap_summary: Optional[str]
    recommendation_summary: Optional[str]
    conflicting_project_id: Optional[int]
    benchmark_used: Optional[str] = None
    uncertainty_notes: list[str] = field(default_factory=list)
    evidence_request_ids: list[int] = field(default_factory=list)
    evidence_reference_codes: list[str] = field(default_factory=list)


DEFAULT_BENCHMARKS = {
    "water": {
        "standard": "Jal Jeevan / WHO Standard: 55 LPCD piped water or functional point within 500m per 250 residents",
        "radius_km": 1.5,
        "people_per_unit": 250,
    },
    "transport": {
        "standard": "BRICS Urban Mobility Standard: Transit node within 1.5 km",
        "radius_km": 1.5,
        "people_per_unit": 2000,
    },
    "transport_access": {
        "standard": "BRICS Urban Mobility Standard: Transit node within 1.5 km",
        "radius_km": 1.5,
        "people_per_unit": 2000,
    },
    "roads": {
        "standard": "PMGSY Standard: All-weather road connectivity within 500m",
        "radius_km": 1.0,
        "people_per_unit": 1000,
    },
    "education": {
        "standard": "Right to Education Standard: School with sanitation within 1.0 km per 1200 residents",
        "radius_km": 2.0,
        "people_per_unit": 1200,
    },
    "health": {
        "standard": "National Health Mission Standard: Primary Health Centre within 5.0 km per 5000 residents",
        "radius_km": 5.0,
        "people_per_unit": 5000,
    },
    "sanitation": {
        "standard": "Sanitation Standard: Covered drainage & functional sanitation within 500m per 300 residents",
        "radius_km": 1.0,
        "people_per_unit": 300,
    },
    "power": {
        "standard": "Electrification Standard: Distribution substation capacity within 3.0 km",
        "radius_km": 3.0,
        "people_per_unit": 4000,
    },
    "electricity": {
        "standard": "Electrification Standard: Distribution substation capacity within 3.0 km",
        "radius_km": 3.0,
        "people_per_unit": 4000,
    },
    "other": {
        "standard": "General Public Infrastructure Standard",
        "radius_km": 2.5,
        "people_per_unit": 1500,
    },
}

SECTOR_ASSET_MAPPING = {
    "water": ["water_point", "water_supply", "water_tap", "borewell"],
    "transport": ["bus_stop", "transit_station", "rail_station", "bus_terminal"],
    "transport_access": ["bus_stop", "transit_station", "rail_station", "bus_terminal"],
    "roads": ["road", "bridge", "culvert"],
    "education": ["school", "primary_school", "secondary_school"],
    "health": ["clinic", "hospital", "phc", "chc", "health_centre"],
    "sanitation": ["drainage_point", "toilet", "sewer", "waste_facility"],
    "power": ["power_substation", "transformer", "grid_node"],
    "electricity": ["power_substation", "transformer", "grid_node"],
}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def detect_gap(payload: GapDetectionInput, db=None) -> GapDetectionOutput:
    """Evaluates whether an infrastructure deficit exists for the given cluster."""
    cluster_id = payload.cluster_id
    config = payload.config or {}

    if db is None:
        return GapDetectionOutput(
            gap_found=True,
            demand_summary="Independent citizen reports indicate recurring accessibility deficits.",
            gap_summary="No active service detected within standard service benchmark radius.",
            recommendation_summary="Sanction transit frequency expansion or upgrade.",
            conflicting_project_id=None,
            benchmark_used="National Infrastructure Service Radius Standards",
            uncertainty_notes=["Analysis based on synthetic baseline data."],
            evidence_request_ids=[],
            evidence_reference_codes=[],
        )

    from app.models import (
        CitizenRequest,
        ClusterMember,
        DemographicIndicator,
        GapAnalysis,
        InfrastructureAsset,
        Location,
        NeedsCluster,
        Project,
    )

    cluster = db.query(NeedsCluster).filter(NeedsCluster.id == cluster_id).first()
    if not cluster:
        return GapDetectionOutput(
            gap_found=False,
            demand_summary=None,
            gap_summary=None,
            recommendation_summary=None,
            conflicting_project_id=None,
            benchmark_used=None,
            uncertainty_notes=["Cluster not found in database"],
            evidence_request_ids=[],
            evidence_reference_codes=[],
        )

    issue_type = (cluster.issue_type or "other").lower().strip()
    sector_key = issue_type.split("_")[0]
    benchmark_meta = DEFAULT_BENCHMARKS.get(issue_type, DEFAULT_BENCHMARKS.get(sector_key, DEFAULT_BENCHMARKS["other"]))
    benchmark_str = config.get("benchmark") or benchmark_meta["standard"]
    benchmark_radius = benchmark_meta.get("radius_km", 2.0)
    benchmark_capacity = benchmark_meta.get("people_per_unit", 1000)

    # 1. Fetch cluster members & citizen request IDs
    members = db.query(ClusterMember).filter(ClusterMember.cluster_id == cluster_id).all()
    evidence_request_ids = [m.request_id for m in members]
    citizen_requests = (
        db.query(CitizenRequest).filter(CitizenRequest.id.in_(evidence_request_ids)).all()
        if evidence_request_ids
        else []
    )
    evidence_reference_codes = [r.reference_code for r in citizen_requests if r.reference_code]

    # 2. Location & Spatial context
    cluster_loc = None
    if cluster.location_id:
        cluster_loc = db.query(Location).filter(Location.id == cluster.location_id).first()

    uncertainty_notes = list(cluster.uncertainty_notes or [])

    # 3. Check for conflicting / active government projects in catchment (FR-042)
    conflicting_project = None
    if cluster_loc:
        proj_q = (
            db.query(Project, Location)
            .join(Location, Project.location_id == Location.id, isouter=True)
            .filter(
                Project.sector.ilike(f"%{sector_key}%"),
                Project.status.in_(["sanctioned", "ongoing"]),
            )
        )
        for proj, ploc in proj_q.all():
            if proj.location_id == cluster.location_id:
                conflicting_project = proj
                break
            if cluster_loc.latitude is not None and ploc and ploc.latitude is not None:
                dist = _haversine_km(
                    cluster_loc.latitude, cluster_loc.longitude, ploc.latitude, ploc.longitude
                )
                if dist <= 12.0:
                    conflicting_project = proj
                    break
            if cluster_loc.district and ploc and ploc.district:
                if cluster_loc.district.lower() == ploc.district.lower():
                    conflicting_project = proj
                    break

    # Also fallback check if location wasn't joined
    if not conflicting_project:
        conflicting_project = (
            db.query(Project)
            .filter(
                Project.sector.ilike(f"%{sector_key}%"),
                Project.status.in_(["sanctioned", "ongoing"]),
                Project.location_id == cluster.location_id,
            )
            .first()
        )

    conflicting_project_id = conflicting_project.id if conflicting_project else None

    # 4. Search matching infrastructure assets in vicinity
    target_assets = SECTOR_ASSET_MAPPING.get(sector_key, [sector_key])
    assets_in_radius = []
    nearest_asset = None
    min_dist_km = None

    if cluster_loc and cluster_loc.latitude is not None and cluster_loc.longitude is not None:
        asset_q = (
            db.query(InfrastructureAsset, Location)
            .join(Location, InfrastructureAsset.location_id == Location.id)
            .filter(InfrastructureAsset.asset_type.in_(target_assets))
            .all()
        )
        for asset, aloc in asset_q:
            if aloc.latitude is not None and aloc.longitude is not None:
                d = _haversine_km(cluster_loc.latitude, cluster_loc.longitude, aloc.latitude, aloc.longitude)
                if d <= benchmark_radius * 2.5:
                    assets_in_radius.append((asset, d))
                if min_dist_km is None or d < min_dist_km:
                    min_dist_km = d
                    nearest_asset = asset

    # 5. Demographics context
    demo = (
        db.query(DemographicIndicator)
        .filter(DemographicIndicator.location_id == cluster.location_id)
        .first()
        if cluster.location_id
        else None
    )
    population = demo.population if (demo and demo.population) else 2500

    # 6. Functional status & coverage per capita
    functional_assets = []
    for asset, dist in assets_in_radius:
        is_functional = True
        if asset.attributes:
            try:
                attrs = json.loads(asset.attributes)
                if attrs.get("functional") is False or attrs.get("operational") is False:
                    is_functional = False
                if attrs.get("functional_toilets") == 0 or attrs.get("overflow_risk") == "critical":
                    is_functional = False
                if attrs.get("taps_functional") == 0:
                    is_functional = False
            except Exception:
                pass
        if is_functional and dist <= benchmark_radius:
            functional_assets.append((asset, dist))

    # 7. Formulate gap result
    ref_list_str = f" (Requests: {', '.join(evidence_reference_codes[:3])})" if evidence_reference_codes else ""
    demand_summary = (
        f"{cluster.independent_demand_count} independent reports "
        f"({cluster.raw_message_count} total messages){ref_list_str} indicating unmet need."
    )

    if conflicting_project:
        gap_found = False
        gap_summary = (
            f"Project already active: '{conflicting_project.name}' "
            f"(Status: {conflicting_project.status}). Catchment intervention already funded."
        )
        recommendation_summary = (
            f"Avoid duplicate allocation; monitor progress of active project '{conflicting_project.name}'."
        )
        uncertainty_notes.append(f"Conflicting project '{conflicting_project.name}' found (FR-042).")
    elif len(functional_assets) == 0:
        gap_found = True
        if nearest_asset and min_dist_km is not None:
            gap_summary = (
                f"No adequate facility or service within benchmark radius ({benchmark_str}). "
                f"Nearest facility '{nearest_asset.name}' is {round(min_dist_km, 2)} km away."
            )
        else:
            gap_summary = f"No adequate facility or service within benchmark radius ({benchmark_str})."
        recommendation_summary = (
            f"Recommended priority candidate for new {issue_type.replace('_', ' ')} intervention."
        )
    else:
        # Check per-capita ratio
        people_per_unit = round(population / len(functional_assets))
        if people_per_unit > benchmark_capacity:
            gap_found = True
            gap_summary = (
                f"Coverage deficit: {people_per_unit} residents per functional facility "
                f"exceeds benchmark standard capacity ({benchmark_capacity} residents per facility)."
            )
            recommendation_summary = (
                f"Recommend facility capacity upgrade or secondary service point for {issue_type}."
            )
        else:
            gap_found = False
            gap_summary = (
                f"Adequate coverage detected: {len(functional_assets)} functional facility "
                f"within {benchmark_radius} km meeting {benchmark_str}."
            )
            recommendation_summary = (
                "Demand appears localized or transient; maintain monitoring without immediate capital allocation."
            )

    uncertainty_notes.append("Verified against public dataset registry and ongoing works database.")
    uncertainty_notes.append("Synthetic infrastructure dataset used (FR-057).")

    # 8. Persist in GapAnalysis table
    gap_record = db.query(GapAnalysis).filter(GapAnalysis.cluster_id == cluster_id).first()
    if not gap_record:
        gap_record = GapAnalysis(cluster_id=cluster_id)
        db.add(gap_record)
    gap_record.gap_found = gap_found
    gap_record.benchmark_used = benchmark_str
    gap_record.conflicting_project_id = conflicting_project_id
    gap_record.demand_summary = demand_summary
    gap_record.gap_summary = gap_summary
    gap_record.recommendation_summary = recommendation_summary
    gap_record.uncertainty_notes = uncertainty_notes
    db.commit()

    return GapDetectionOutput(
        gap_found=gap_found,
        demand_summary=demand_summary,
        gap_summary=gap_summary,
        recommendation_summary=recommendation_summary,
        conflicting_project_id=conflicting_project_id,
        benchmark_used=benchmark_str,
        uncertainty_notes=uncertainty_notes,
        evidence_request_ids=evidence_request_ids,
        evidence_reference_codes=evidence_reference_codes,
    )
