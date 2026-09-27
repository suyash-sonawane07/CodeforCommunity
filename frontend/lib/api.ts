/**
 * Central API client — the ONLY module that talks to the backend.
 *
 * Consumes the contract in docs/api/API_CONTRACT.md; typed by types/api.ts.
 * Member A: extend per-endpoint helpers here as screens are wired (Phase 2+).
 */
import { API_BASE_URL } from "./config";
import type {
  ClusterDetail,
  ClusterListResponse,
  EvidencePanel,
  GapAnalysisResult,
  OutcomeResponse,
  PriorityBreakdown,
  RequestCreate,
  RequestCreateResponse,
  RequestStatusResponse,
  ReviewActionCreate,
  ReviewActionResponse,
  SimulationCreate,
  SimulationResult,
} from "@/types/api";

/** Uniform API error carrying the backend's error envelope (docs/api contract). */
export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details?: unknown;

  constructor(status: number, code: string, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
    // Next.js must never cache citizen/planner API responses
    cache: "no-store",
  });

  if (!res.ok) {
    let code = "HTTP_ERROR";
    let message = `Request failed with status ${res.status}`;
    let details: unknown = undefined;
    try {
      const body = await res.json();
      const envelope = body?.error ?? body?.detail?.error;
      if (envelope?.code) {
        code = envelope.code;
        message = envelope.message ?? message;
        details = envelope.details;
      }
    } catch {
      // non-JSON error body — keep defaults
    }
    throw new ApiError(res.status, code, message, details);
  }
  return (await res.json()) as T;
}

function authHeaders(token?: string): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/* ------------------------------------------------------------------ *
 * Contract helpers (all backend business endpoints are 501 today —
 * callers must handle ApiError with code NOT_IMPLEMENTED).          *
 * ------------------------------------------------------------------ */

export const api = {
  health: () => request<{ status: string }>("/health"),

  login: (email: string, password: string) =>
    request<{ access_token: string; role: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  createRequest: (body: RequestCreate, token?: string) =>
    request<RequestCreateResponse>("/requests", {
      method: "POST",
      body: JSON.stringify(body),
      headers: authHeaders(token),
    }),

  getRequestStatus: (requestId: string, token?: string) =>
    request<RequestStatusResponse>(`/requests/${requestId}`, { headers: authHeaders(token) }),

  listClusters: (
    params: { sector?: string; district?: string; status?: string } = {},
    token?: string,
  ) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined),
    ).toString();
    return request<ClusterListResponse>(`/clusters${qs ? `?${qs}` : ""}`, {
      headers: authHeaders(token),
    });
  },

  getCluster: (id: number, token?: string) =>
    request<ClusterDetail>(`/clusters/${id}`, { headers: authHeaders(token) }),

  getEvidence: (id: number, token?: string) =>
    request<EvidencePanel>(`/clusters/${id}/evidence`, { headers: authHeaders(token) }),

  getGapAnalysis: (id: number, token?: string) =>
    request<GapAnalysisResult>(`/clusters/${id}/gap-analysis`, { headers: authHeaders(token) }),

  getPriority: (id: number, token?: string) =>
    request<PriorityBreakdown>(`/clusters/${id}/priority`, { headers: authHeaders(token) }),

  reviewCluster: (id: number, body: ReviewActionCreate, token?: string) =>
    request<ReviewActionResponse>(`/clusters/${id}/review`, {
      method: "POST",
      body: JSON.stringify(body),
      headers: authHeaders(token),
    }),

  runSimulation: (body: SimulationCreate, token?: string) =>
    request<SimulationResult>("/simulations", {
      method: "POST",
      body: JSON.stringify(body),
      headers: authHeaders(token),
    }),

  getOutcome: (id: number, token?: string) =>
    request<OutcomeResponse>(`/clusters/${id}/outcome`, { headers: authHeaders(token) }),
};
