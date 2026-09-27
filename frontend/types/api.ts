/**
 * Shared API types — the frontend mirror of backend/app/schemas/api.py.
 *
 * SCAFFOLD NOTE: manually mirrored today; generate from OpenAPI later
 * (`make openapi-export` → openapi-typescript) per docs/api/API_CONTRACT.md.
 * Changes here must go through a contract PR.
 */

/* ---------------------------------------------------------------- errors */

export interface ErrorBody {
  code: string;
  message: string;
  details?: Record<string, unknown> | null;
}

export interface ErrorEnvelope {
  error: ErrorBody;
}

/* ---------------------------------------------------------------- auth */

export type Role = "citizen" | "analyst" | "reviewer" | "decision_maker" | "admin";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: Role;
}

/* ---------------------------------------------------------------- requests */

export type Channel = "text" | "voice";
export type LanguageHint = "hi" | "mr" | "en";

export interface RequestCreate {
  channel: Channel;
  language_hint?: LanguageHint | null;
  text?: string;
  location_text?: string;
  audio_base64?: string;
  consent_ack: true; // FR-005: literally must be true
}

export interface RequestCreateResponse {
  request_id: string;
  status: string;
  reference_code: string;
}

export interface RequestStatusResponse {
  request_id: string;
  reference_code: string;
  status: string;
  language?: string | null;
  transcript?: string | null;
  created_at?: string | null;
}

/* ---------------------------------------------------------------- clusters */

export type ClusterStatus =
  | "forming"
  | "active"
  | "under_review"
  | "approved"
  | "rejected"
  | "archived"; // FR-022 lifecycle

export interface ClusterSummary {
  id: number;
  issue_type: string;
  status: ClusterStatus;
  independent_demand_count: number; // FR-024: always shown alongside raw count
  raw_message_count: number;
  district?: string | null;
}

export interface ClusterDetail extends ClusterSummary {
  location?: Record<string, unknown> | null;
  review_status?: string | null;
  uncertainty_notes: string[];
}

export interface ClusterListResponse {
  items: ClusterSummary[];
  total: number;
}

/* ---------------------------------------------------------------- review */

export type ReviewActionType = "approve" | "reject" | "request_more_evidence"; // FR-059

export interface ReviewActionCreate {
  action: ReviewActionType;
  note: string; // required
}

export interface ReviewActionResponse {
  cluster_id: number;
  action: ReviewActionType;
  review_status: string;
  audit_log_id?: number | null;
}

export interface ClusterCorrection {
  issue_type?: string;
  location_notes?: string;
  note: string;
}

/* ---------------------------------------------------------------- evidence */

export interface EvidencePanel {
  cluster_id: number;
  issue_type: string;
  independent_demand_count: number;
  raw_message_count: number;
  location?: Record<string, unknown> | null;
  infrastructure_context?: Record<string, unknown> | null;
  existing_project_check?: Record<string, unknown> | null;
  priority_factors?: Record<string, unknown> | null;
  uncertainty_notes: string[];
  dataset_versions: string[];
}

export interface GapAnalysisResult {
  cluster_id: number;
  gap_found?: boolean | null;
  demand_summary?: string | null; // FR-044: three separate labelled fields
  gap_summary?: string | null;
  recommendation_summary?: string | null;
  benchmark_used?: string | null;
  conflicting_project?: Record<string, unknown> | null;
  uncertainty_notes: string[];
}

export interface PriorityBreakdown {
  cluster_id: number;
  demand?: number | null;
  gap?: number | null;
  impact?: number | null;
  equity_adjustment?: number | null;
  weights?: Record<string, number> | null;
  priority_index?: number | null;
  is_incomplete: boolean; // FR-048
}

/* ---------------------------------------------------------------- geo / infra */

export interface GeoJSONFeature {
  type: "Feature";
  geometry: Record<string, unknown> | null; // null → needs-geocoding list (FR-033)
  properties: Record<string, unknown>;
}

export interface GeoJSONFeatureCollection {
  type: "FeatureCollection";
  features: GeoJSONFeature[];
}

export interface InfrastructureLayerResponse {
  infrastructure: Record<string, unknown>[];
  demographics: Record<string, unknown>[];
  dataset_version?: string | null;
  source_label?: "confirmed" | "candidate" | "synthetic" | null; // FR-057
}

/* ---------------------------------------------------------------- simulation */

export interface SimulationCreate {
  sector_allocations: Partial<Record<"roads" | "water" | "health" | "education", number>>; // FR-053
}

export interface SimulationResult {
  scenario_id: string;
  sector_allocations: Record<string, number>;
  coverable_clusters_before?: number | null;
  coverable_clusters_after?: number | null;
  disclaimer: string; // FR-056
}

/* ---------------------------------------------------------------- outcome */

export interface OutcomeResponse {
  cluster_id: number;
  baseline?: Record<string, unknown> | null;
  followup?: Record<string, unknown> | null;
  is_synthetic: boolean; // FR-057
  disclaimer: string; // FR-067
}

/* ---------------------------------------------------------------- datasets/audit */

export interface DatasetInfo {
  id: number;
  name: string;
  source_label: "confirmed" | "candidate" | "synthetic";
  version: string;
  ingested_at?: string | null;
}

export interface DatasetListResponse {
  items: DatasetInfo[];
}

export interface AuditLogEntry {
  id: number;
  actor_id?: number | null;
  action: string;
  entity_type?: string | null;
  entity_id?: number | null;
  before_value?: Record<string, unknown> | null;
  after_value?: Record<string, unknown> | null;
  created_at?: string | null;
}

export interface AuditLogListResponse {
  items: AuditLogEntry[];
  total: number;
}
