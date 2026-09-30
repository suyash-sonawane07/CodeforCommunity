"""Shared API schemas (PRD §10) — the request/response contract.

SCAFFOLD: routes validate against these, then return 501 until implemented.
Member B/C own changes here via contract PRs; Member A mirrors them in
`frontend/types/api.ts` until types are generated from OpenAPI.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

# ---------------------------------------------------------------- errors


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None


class ErrorEnvelope(BaseModel):
    error: ErrorBody


# ---------------------------------------------------------------- infra


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    version: str
    env: str
    database: str = "unknown"


class VersionResponse(BaseModel):
    name: str
    version: str
    api_version: str = "v1"
    scaffold: bool = True


# ---------------------------------------------------------------- auth


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user: Optional[UserResponse] = None


# ---------------------------------------------------------------- requests (FR-001..009)


class RequestCreate(BaseModel):
    channel: str = Field(pattern="^(text|voice)$")
    language_hint: Optional[str] = Field(default=None, pattern="^(hi|mr|en|pt|ru|zh|zu|af)$")
    text: Optional[str] = None
    location_text: Optional[str] = None
    audio_base64: Optional[str] = None
    consent_ack: bool

    @model_validator(mode="after")
    def check_submission(self) -> "RequestCreate":
        if not self.consent_ack:
            raise ValueError("consent_ack must be true (FR-005)")
        if self.channel == "text" and not (self.text and self.text.strip()):
            raise ValueError("text is required for channel=text (FR-006)")
        if self.channel == "voice" and not self.audio_base64:
            raise ValueError("audio_base64 is required for channel=voice (FR-006)")
        return self


class RequestCreateResponse(BaseModel):
    request_id: str
    status: str
    reference_code: str
    issue_type: Optional[str] = None
    location: Optional[str] = None


class AudioUploadResponse(BaseModel):
    request_id: str
    audio_url: str
    status: str


class RequestStatusResponse(BaseModel):
    request_id: str
    reference_code: str
    status: str
    language: Optional[str] = None
    transcript: Optional[str] = None
    created_at: Optional[str] = None
    issue_type: Optional[str] = None
    location: Optional[str] = None


# ---------------------------------------------------------------- clusters


class ClusterSummary(BaseModel):
    id: int
    issue_type: str
    status: str
    independent_demand_count: int
    raw_message_count: int
    district: Optional[str] = None


class ClusterListResponse(BaseModel):
    items: list[ClusterSummary]
    total: int


class ClusterDetail(ClusterSummary):
    location: Optional[dict[str, Any]] = None
    review_status: Optional[str] = None
    uncertainty_notes: list[str] = Field(default_factory=list)


class ClusterCorrection(BaseModel):
    issue_type: Optional[str] = None
    location_notes: Optional[str] = None
    note: str = Field(min_length=1)  # FR-060: correction requires a note


class ReviewActionCreate(BaseModel):
    action: str = Field(pattern="^(approve|reject|request_more_evidence)$")  # FR-059
    note: str = Field(min_length=1)


class ReviewActionResponse(BaseModel):
    cluster_id: int
    action: str
    review_status: str
    audit_log_id: Optional[int] = None


# ---------------------------------------------------------------- evidence / gap / priority


class EvidencePanel(BaseModel):
    """PRD §10.3 shape. Every number traceable to a stored field or formula (FR-052)."""

    cluster_id: int
    issue_type: str
    independent_demand_count: int
    raw_message_count: int
    location: Optional[dict[str, Any]] = None
    infrastructure_context: Optional[dict[str, Any]] = None
    existing_project_check: Optional[dict[str, Any]] = None
    priority_factors: Optional[dict[str, Any]] = None
    uncertainty_notes: list[str] = Field(default_factory=list)
    dataset_versions: list[str] = Field(default_factory=list)
    evidence_request_ids: list[int] = Field(default_factory=list)
    evidence_reference_codes: list[str] = Field(default_factory=list)


class GapAnalysisResult(BaseModel):
    cluster_id: int
    gap_found: Optional[bool] = None
    demand_summary: Optional[str] = None  # FR-044: three separate fields
    gap_summary: Optional[str] = None
    recommendation_summary: Optional[str] = None
    benchmark_used: Optional[str] = None
    conflicting_project: Optional[dict[str, Any]] = None
    uncertainty_notes: list[str] = Field(default_factory=list)
    evidence_request_ids: list[int] = Field(default_factory=list)
    evidence_reference_codes: list[str] = Field(default_factory=list)


class PriorityBreakdown(BaseModel):
    cluster_id: int
    demand: Optional[float] = None
    gap: Optional[float] = None
    impact: Optional[float] = None
    equity_adjustment: Optional[float] = None
    funded_penalty: Optional[float] = None
    weights: Optional[dict[str, float]] = None
    priority_index: Optional[float] = None
    is_incomplete: bool = False  # FR-048
    evidence_request_ids: list[int] = Field(default_factory=list)



# ---------------------------------------------------------------- geospatial / infra


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Optional[dict[str, Any]] = None  # None → appears in needs-geocoding list
    properties: dict[str, Any] = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[GeoJSONFeature] = Field(default_factory=list)


class InfrastructureLayerResponse(BaseModel):
    infrastructure: list[dict[str, Any]] = Field(default_factory=list)
    demographics: list[dict[str, Any]] = Field(default_factory=list)
    dataset_version: Optional[str] = None
    source_label: Optional[str] = None  # confirmed|candidate|synthetic (FR-057)


# ---------------------------------------------------------------- simulations


class SimulationCreate(BaseModel):
    sector_allocations: dict[str, float] = Field(
        description="Budget per sector in ₹: roads|water|health|education (FR-053)"
    )


class SimulationResult(BaseModel):
    scenario_id: str
    sector_allocations: dict[str, float]
    coverable_clusters_before: Optional[int] = None
    coverable_clusters_after: Optional[int] = None
    disclaimer: str = Field(
        default="Estimates use synthetic/curated cost data — not official budget figures (FR-056)"
    )


# ---------------------------------------------------------------- outcomes


class OutcomeResponse(BaseModel):
    cluster_id: int
    baseline: Optional[dict[str, Any]] = None
    followup: Optional[dict[str, Any]] = None
    is_synthetic: bool = True  # FR-057
    disclaimer: str = Field(default="Observed change, not proven causal impact (FR-067)")


# ---------------------------------------------------------------- datasets / audit


class DatasetInfo(BaseModel):
    id: int
    name: str
    source_label: str
    version: str
    ingested_at: Optional[str] = None


class DatasetListResponse(BaseModel):
    items: list[DatasetInfo]


class AuditLogEntry(BaseModel):
    id: int
    actor_id: Optional[int] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    before_value: Optional[dict[str, Any]] = None
    after_value: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None


class AuditLogListResponse(BaseModel):
    items: list[AuditLogEntry]
    total: int


# ---------------------------------------------------------------- 501 placeholder


class NotImplementedResponse(BaseModel):
    """Uniform scaffold response for every unimplemented business endpoint."""

    error: ErrorBody = Field(
        default_factory=lambda: ErrorBody(
            code="NOT_IMPLEMENTED",
            message="Scaffold endpoint — logic not implemented yet (see docs/api/API_CONTRACT.md)",
        )
    )


# ---------------------------------------------------------------- stats and priorities

class StatsResponse(BaseModel):
    totals: int
    hotspots: list[str]
    critical_gaps: int
    approved: int

class PriorityItem(BaseModel):
    cluster_id: int
    issue: str
    country: str
    date: str
    rank: int
    score: float

class PrioritiesResponse(BaseModel):
    items: list[PriorityItem]
