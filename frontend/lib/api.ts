/**
 * Central API client — handles both direct backend calls and Next.js /api/proxy calls.
 *
 * Consumes the contract in docs/api/API_CONTRACT.md; typed by types/api.ts.
 */
import { API_BASE_URL } from "./config";
import type {
  AuditLogListResponse,
  ClusterDetail,
  ClusterListResponse,
  DatasetListResponse,
  EvidencePanel,
  GapAnalysisResult,
  GeoJSONFeatureCollection,
  InfrastructureLayerResponse,
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

const NEXT_PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL || '/api/proxy';

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

let isRedirecting = false;

export async function fetchApi<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${NEXT_PUBLIC_API_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && path !== '/auth/login') {
    if (typeof window !== 'undefined' && !isRedirecting) {
      isRedirecting = true;
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.replace('/login?expired=1');
    }
    return new Promise(() => {}); // never resolve while redirecting
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const code = errorBody?.error?.code || 'API_ERROR';
    const message = errorBody?.error?.message || response.statusText || 'API Error';
    throw new ApiError(response.status, code, message, errorBody?.error?.details);
  }

  return response.json();
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...((init.headers as Record<string, string>) ?? {}),
    },
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
 * Contract helpers                                                    *
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

  getGeospatialClusters: (token?: string) =>
    request<GeoJSONFeatureCollection>("/geospatial/clusters", { headers: authHeaders(token) }),

  getInfrastructure: (token?: string) =>
    request<InfrastructureLayerResponse>("/infrastructure", { headers: authHeaders(token) }),

  getDatasets: (token?: string) =>
    request<DatasetListResponse>("/datasets", { headers: authHeaders(token) }),

  getAuditLogs: (token?: string) =>
    request<AuditLogListResponse>("/audit-logs", { headers: authHeaders(token) }),

  uploadAudio: async (requestId: string, file: Blob, token?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE_URL}/requests/${requestId}/audio`, {
      method: "POST",
      body: formData,
      headers: authHeaders(token),
    });
    if (!res.ok) {
      throw new ApiError(res.status, "UPLOAD_ERROR", "Audio upload failed");
    }
    return res.json();
  },
};
