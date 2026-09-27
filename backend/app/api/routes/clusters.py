"""Cluster routes (PRD §10.1 #5–11) — the analytical core's API surface.

SCAFFOLD: endpoints exist with real schemas and return 501 until Member B/C implement.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.deps import require_role
from app.schemas import (
    ClusterCorrection,
    ClusterDetail,
    ClusterListResponse,
    EvidencePanel,
    GapAnalysisResult,
    NotImplementedResponse,
    PriorityBreakdown,
    ReviewActionCreate,
    ReviewActionResponse,
)

router = APIRouter(prefix="/clusters", tags=["clusters"])


def _not_implemented() -> JSONResponse:
    payload = NotImplementedResponse().model_dump()
    return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=payload)


@router.get(
    "",
    response_model=ClusterListResponse,
    responses={501: {"model": NotImplementedResponse}},
    summary="List clusters, filterable by sector/district/status — FR-071 (analyst+)",
)
def list_clusters(user=Depends(require_role("analyst"))) -> JSONResponse:
    """TODO(PRD FR-019–025, FR-071, Phase 2): query needs_clusters with filters."""
    return _not_implemented()


@router.get(
    "/{cluster_id}",
    response_model=ClusterDetail,
    responses={501: {"model": NotImplementedResponse}},
    summary="Full cluster detail (analyst+)",
)
def get_cluster(cluster_id: int, user=Depends(require_role("analyst"))) -> JSONResponse:
    return _not_implemented()


@router.patch(
    "/{cluster_id}",
    response_model=ReviewActionResponse,
    responses={501: {"model": NotImplementedResponse}},
    summary="Correct classification/location — FR-060 (reviewer+)",
)
def correct_cluster(
    cluster_id: int, body: ClusterCorrection, user=Depends(require_role("reviewer"))
) -> JSONResponse:
    """TODO(PRD FR-060, FR-062, Phase 3): apply correction, write review_action + audit_log."""
    return _not_implemented()


@router.get(
    "/{cluster_id}/evidence",
    response_model=EvidencePanel,
    responses={501: {"model": NotImplementedResponse}},
    summary="Evidence panel payload — FR-051 (analyst+)",
)
def get_evidence(cluster_id: int, user=Depends(require_role("analyst"))) -> JSONResponse:
    """TODO(PRD FR-051–052, Phase 2): assemble traceable evidence snapshot."""
    return _not_implemented()


@router.post(
    "/{cluster_id}/review",
    response_model=ReviewActionResponse,
    responses={501: {"model": NotImplementedResponse}},
    summary="Approve/reject/request-more-evidence — FR-059 (reviewer+)",
)
def review_cluster(
    cluster_id: int, body: ReviewActionCreate, user=Depends(require_role("reviewer"))
) -> JSONResponse:
    """TODO(PRD FR-058–063, Phase 3): state machine + exactly one audit row per action."""
    return _not_implemented()


@router.get(
    "/{cluster_id}/gap-analysis",
    response_model=GapAnalysisResult,
    responses={501: {"model": NotImplementedResponse}},
    summary="Gap detection result — FR-040–044 (analyst+)",
)
def get_gap_analysis(cluster_id: int, user=Depends(require_role("analyst"))) -> JSONResponse:
    """TODO(PRD FR-040–044, Phase 2): call gap_detection service."""
    return _not_implemented()


@router.get(
    "/{cluster_id}/priority",
    response_model=PriorityBreakdown,
    responses={501: {"model": NotImplementedResponse}},
    summary="Priority factor breakdown — FR-050 (analyst+)",
)
def get_priority(cluster_id: int, user=Depends(require_role("analyst"))) -> JSONResponse:
    """TODO(PRD FR-045–050, Phase 2): call prioritisation service; no hard-coded weights."""
    return _not_implemented()
