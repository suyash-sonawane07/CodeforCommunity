"""Cluster routes (PRD §10.1 #5–11) — the analytical core's API surface."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models import Location, User
from app.repositories import ClusterRepository, GovernanceRepository
from app.schemas import (
    ClusterCorrection,
    ClusterDetail,
    ClusterListResponse,
    ClusterSummary,
    EvidencePanel,
    GapAnalysisResult,
    PriorityBreakdown,
    ReviewActionCreate,
    ReviewActionResponse,
)
from app.services.evidence import EvidenceInput, build_evidence_panel
from app.services.gap_detection import GapDetectionInput, detect_gap
from app.services.prioritisation import PrioritisationInput, compute_priority

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get(
    "",
    response_model=ClusterListResponse,
    summary="List clusters, filterable by sector/district/status — FR-071 (analyst+)",
)
def list_clusters(
    sector: Optional[str] = Query(default=None, alias="sector"),
    issue_type: Optional[str] = Query(default=None, alias="issue_type"),
    district: Optional[str] = None,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    user=Depends(require_role("analyst")),
) -> ClusterListResponse:
    """List clusters with multi-factor filtering."""
    chosen_sector = sector or issue_type
    cluster_repo = ClusterRepository(db)
    clusters = cluster_repo.list_clusters(
        issue_type=chosen_sector, district=district, status=status_filter
    )

    items = []
    for c in clusters:
        dist = None
        if c.location_id:
            loc = db.query(Location).filter(Location.id == c.location_id).first()
            if loc:
                dist = loc.district

        items.append(
            ClusterSummary(
                id=c.id,
                issue_type=c.issue_type,
                status=c.status,
                independent_demand_count=c.independent_demand_count,
                raw_message_count=c.raw_message_count,
                district=dist,
            )
        )

    return ClusterListResponse(items=items, total=len(items))


@router.get(
    "/{cluster_id}",
    response_model=ClusterDetail,
    summary="Full cluster detail (analyst+)",
)
def get_cluster(
    cluster_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("analyst")),
) -> ClusterDetail:
    cluster_repo = ClusterRepository(db)
    c = cluster_repo.get_by_id(cluster_id)
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Cluster {cluster_id} not found"}},
        )

    loc_dict = None
    dist = None
    if c.location_id:
        loc = db.query(Location).filter(Location.id == c.location_id).first()
        if loc:
            dist = loc.district
            loc_dict = {
                "village": loc.village_ward or loc.source_text,
                "block": loc.block,
                "district": loc.district,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "confidence": loc.confidence,
                "resolution_method": loc.resolution_method,
            }

    return ClusterDetail(
        id=c.id,
        issue_type=c.issue_type,
        status=c.status,
        independent_demand_count=c.independent_demand_count,
        raw_message_count=c.raw_message_count,
        district=dist,
        location=loc_dict,
        review_status=c.review_status,
        uncertainty_notes=c.uncertainty_notes or [],
    )


@router.patch(
    "/{cluster_id}",
    response_model=ReviewActionResponse,
    summary="Correct classification/location — FR-060 (reviewer+)",
)
def correct_cluster(
    cluster_id: int,
    body: ClusterCorrection,
    db: Session = Depends(get_db),
    user=Depends(require_role("reviewer")),
) -> ReviewActionResponse:
    cluster_repo = ClusterRepository(db)
    gov_repo = GovernanceRepository(db)

    c = cluster_repo.get_by_id(cluster_id)
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Cluster {cluster_id} not found"}},
        )

    before_val = {"issue_type": c.issue_type, "uncertainty_notes": c.uncertainty_notes}

    # Apply corrections
    notes = list(c.uncertainty_notes or [])
    notes.append(f"Correction applied: {body.note}")
    if body.location_notes:
        notes.append(f"Location note: {body.location_notes}")

    c = cluster_repo.update_cluster(
        cluster_id=cluster_id,
        issue_type=body.issue_type or c.issue_type,
        uncertainty_notes=notes,
    )

    after_val = {"issue_type": c.issue_type, "uncertainty_notes": c.uncertainty_notes}

    # Record review action & audit log
    reviewer_user = db.query(User).filter(User.email == user.get("subject")).first()
    reviewer_id = reviewer_user.id if reviewer_user else None

    gov_repo.record_review_action(
        cluster_id=cluster_id,
        reviewer_id=reviewer_id,
        action="correction",
        note=body.note,
        before_value=before_val,
        after_value=after_val,
    )

    audit_entry = gov_repo.create_audit_log(
        actor_id=reviewer_id,
        action="CLUSTER_CORRECTION",
        entity_type="needs_clusters",
        entity_id=cluster_id,
        before_value=before_val,
        after_value=after_val,
        detail={"note": body.note},
    )

    db.commit()

    return ReviewActionResponse(
        cluster_id=cluster_id,
        action="correction",
        review_status=c.review_status or "pending",
        audit_log_id=audit_entry.id,
    )


@router.post(
    "/{cluster_id}/review",
    response_model=ReviewActionResponse,
    summary="Approve/reject/request-more-evidence — FR-059 (reviewer+)",
)
def review_cluster(
    cluster_id: int,
    body: ReviewActionCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("reviewer")),
) -> ReviewActionResponse:
    cluster_repo = ClusterRepository(db)
    gov_repo = GovernanceRepository(db)

    c = cluster_repo.get_by_id(cluster_id)
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Cluster {cluster_id} not found"}},
        )

    before_val = {"status": c.status, "review_status": c.review_status}

    # Map action to statuses
    new_status = c.status
    if body.action == "approve":
        new_status = "approved"
    elif body.action == "reject":
        new_status = "rejected"
    elif body.action == "request_more_evidence":
        new_status = "needs_more_evidence"

    c = cluster_repo.update_cluster(
        cluster_id=cluster_id,
        status=new_status,
        review_status=body.action,
    )

    after_val = {"status": c.status, "review_status": c.review_status}

    reviewer_user = db.query(User).filter(User.email == user.get("subject")).first()
    reviewer_id = reviewer_user.id if reviewer_user else None

    gov_repo.record_review_action(
        cluster_id=cluster_id,
        reviewer_id=reviewer_id,
        action=body.action,
        note=body.note,
        before_value=before_val,
        after_value=after_val,
    )

    audit_entry = gov_repo.create_audit_log(
        actor_id=reviewer_id,
        action=f"CLUSTER_REVIEW_{body.action.upper()}",
        entity_type="needs_clusters",
        entity_id=cluster_id,
        before_value=before_val,
        after_value=after_val,
        detail={"note": body.note},
    )

    db.commit()

    return ReviewActionResponse(
        cluster_id=cluster_id,
        action=body.action,
        review_status=c.review_status,
        audit_log_id=audit_entry.id,
    )


@router.get(
    "/{cluster_id}/evidence",
    response_model=EvidencePanel,
    summary="Evidence panel payload — FR-051 (analyst+)",
)
def get_evidence(
    cluster_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("analyst")),
) -> EvidencePanel:
    out = build_evidence_panel(EvidenceInput(cluster_id=cluster_id), db=db)
    return EvidencePanel(**out.payload)


@router.get(
    "/{cluster_id}/gap-analysis",
    response_model=GapAnalysisResult,
    summary="Gap detection result — FR-040–044 (analyst+)",
)
def get_gap_analysis(
    cluster_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("analyst")),
) -> GapAnalysisResult:
    out = detect_gap(GapDetectionInput(cluster_id=cluster_id), db=db)
    conflicting = None
    if out.conflicting_project_id:
        from app.models import Project

        proj = db.query(Project).filter(Project.id == out.conflicting_project_id).first()
        if proj:
            conflicting = {
                "id": proj.id,
                "name": proj.name,
                "sector": proj.sector,
                "status": proj.status,
            }

    return GapAnalysisResult(
        cluster_id=cluster_id,
        gap_found=out.gap_found,
        demand_summary=out.demand_summary,
        gap_summary=out.gap_summary,
        recommendation_summary=out.recommendation_summary,
        benchmark_used="National Infrastructure Service Radius Standards",
        conflicting_project=conflicting,
        uncertainty_notes=out.uncertainty_notes,
    )


@router.get(
    "/{cluster_id}/priority",
    response_model=PriorityBreakdown,
    summary="Priority factor breakdown — FR-050 (analyst+)",
)
def get_priority(
    cluster_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("analyst")),
) -> PriorityBreakdown:
    weights = {"demand": 0.25, "gap": 0.25, "impact": 0.25, "equity": 0.25}
    out = compute_priority(PrioritisationInput(cluster_id=cluster_id, weights=weights), db=db)
    return PriorityBreakdown(
        cluster_id=cluster_id,
        demand=out.demand,
        gap=out.gap,
        impact=out.impact,
        equity_adjustment=out.equity_adjustment,
        weights=weights,
        priority_index=out.priority_index,
        is_incomplete=out.is_incomplete,
    )
