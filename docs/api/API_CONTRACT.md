# API Contract — CivicPulse

**STATUS: SCAFFOLD / NOT IMPLEMENTED** — every endpoint below is exposed by FastAPI with
real request/response schemas and returns **`501 NOT_IMPLEMENTED`** until built.

- **Binding contract:** the OpenAPI spec generated from the FastAPI app —
  `docs/api/openapi/openapi.json` (regenerate: `make openapi-export`; docs UI: `/docs`).
- **Change discipline:** contract PR first (Member B + reviewer), implementations follow
  (PRD §18.2, risk R-07). Member A builds only against this document / the spec.
- **Error envelope (all errors):** `{"error": {"code": "<MACHINE_CODE>", "message": "<human text>", "details": <object|null>}}`
  (`ErrorEnvelope` in the OpenAPI spec).
- **Auth:** JWT bearer on `analyst`+ endpoints (demo-login only, `POST /auth/login`; no
  production auth is implemented or claimed). Roles: `analyst`, `reviewer`,
  `decision_maker`, `admin` (PRD §5/§13). Citizen endpoints are public.

Legend — *Owning module* = backend router file; *FE consumer* = frontend page(s) by Screen ID.

| # | Endpoint | Method | Auth | Owning module | FE consumer | Purpose (PRD) |
|---|---|---|---|---|---|---|
| 1 | `/auth/login` | POST | none → issues token | `app/api/routes/auth.py` | S-04 | Demo role-scoped token |
| 2 | `/requests` | POST | public | `app/api/routes/requests.py` | S-01 | Text/voice intake (FR-001/002) |
| 3 | `/requests/{id}/audio` | POST | public | `app/api/routes/requests.py` | S-01/S-02 | Audio upload (FR-002) |
| 4 | `/requests/{id}` | GET | public (reference ID) | `app/api/routes/requests.py` | S-03 | Citizen checks own submission (FR-005) |
| 5 | `/clusters` | GET | analyst+ | `app/api/routes/clusters.py` | S-05/S-07 | List clusters, filters (FR-071) |
| 6 | `/clusters/{id}` | GET | analyst+ | `app/api/routes/clusters.py` | S-07 | Cluster detail |
| 7 | `/clusters/{id}` | PATCH | reviewer+ | `app/api/routes/clusters.py` | S-07/S-12 | Correct classification/location (FR-060) |
| 8 | `/clusters/{id}/evidence` | GET | analyst+ | `app/api/routes/clusters.py` | S-08 | Evidence panel payload (FR-051) |
| 9 | `/clusters/{id}/review` | POST | reviewer+ | `app/api/routes/clusters.py` | S-12 | Approve/reject/request-evidence (FR-059) |
| 10 | `/clusters/{id}/gap-analysis` | GET | analyst+ | `app/api/routes/clusters.py` | S-09 | Gap detection result (FR-040–044) |
| 11 | `/clusters/{id}/priority` | GET | analyst+ | `app/api/routes/clusters.py` | S-10 | Priority factor breakdown (FR-050) |
| 12 | `/clusters/{id}/outcome` | GET | analyst+ | `app/api/routes/outcomes.py` | S-14 | Outcome measurement (FR-064–067) |
| 13 | `/geospatial/clusters` | GET | analyst+ | `app/api/routes/geospatial.py` | S-06 | GeoJSON for map (FR-029) |
| 14 | `/infrastructure` | GET | analyst+ | `app/api/routes/infrastructure.py` | S-09 | Infra/demographic layer (FR-030–031) |
| 15 | `/simulations` | POST | decision_maker+ | `app/api/routes/simulations.py` | S-11 | Policy scenario (FR-053–056) |
| 16 | `/datasets` | GET | admin | `app/api/routes/datasets.py` | S-15 | Dataset registry + versions (FR-038, FR-073) |
| 17 | `/audit-logs` | GET | admin | `app/api/routes/audit.py` | S-13/S-15 | Audit trail (FR-062) |

Plus infrastructure endpoints (implemented, not PRD business): `GET /health`, `GET /`,
`GET /version`.

## Representative schemas

> The single source of truth for exact shapes is `docs/api/openapi/openapi.json`
> (Pydantic models in `backend/app/schemas/`). TypeScript mirrors live in
> `frontend/types/api.ts` — keep them in sync until types are generated from OpenAPI.

### `POST /requests` → 201 `RequestCreateResponse` (PRD §10.2)
```json
{ "request_id": "req_9f21ac", "status": "processing", "reference_code": "CP-2026-004821" }
```
Request body `RequestCreate`: `channel: text|voice`, `language_hint: null|hi|mr|en`,
`text?: string`, `location_text?: string`, `consent_ack: true` (rejected otherwise, FR-005/006).

### `GET /clusters/{id}/evidence` → `EvidencePanel` (PRD §10.3)
`cluster_id`, `issue_type`, `independent_demand_count`, `raw_message_count`, `location{...confidence}`,
`infrastructure_context{...dataset_version}`, `existing_project_check`, `priority_factors`,
`uncertainty_notes[]` — every number traceable to a stored field or documented formula (FR-052).

### `POST /clusters/{id}/review` — body `ReviewActionCreate`
`action: approve|reject|request_more_evidence` (required note per FR-059) → 501 until Phase 3.

### `GET /clusters/{id}/priority` → `PriorityBreakdown`
`demand, gap, impact, equity_adjustment, weights, priority_index, is_incomplete`
(missing-factor handling per FR-048; illustrative model per PRD §6.7).

### `POST /simulations` — body `SimulationCreate`
`sector_allocations: {roads, water, health, education}` (₹) → `501` until Phase 3;
output will include the FR-056 synthetic-data disclaimer fields.
