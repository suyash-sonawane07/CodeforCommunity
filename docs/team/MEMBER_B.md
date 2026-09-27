# Member B — Backend, Database & DevOps

> Owns the FastAPI app, database, migrations, auth foundation, deployment and audit
> foundation end-to-end (PRD §17.1). Primary dependencies: Member A's API consumption
> (via contract) and Member C's service outputs (via interfaces).

## Owns

- `backend/` — FastAPI app (`app/main.py`, `core/`, `db/`, `api/routes/`), SQLAlchemy
  models + Alembic migrations, repositories, auth boundary, audit-log foundation.
- `deploy/` — Dockerfiles, Compose files, environment wiring.
- CI workflow (`.github/workflows/ci.yml`).

## Must NOT casually modify

- `ai/` provider implementations — Member C's territory. Member B owns only the
  **wiring**: `backend/app/services/ai_runtime.py` imports providers via
  `ai/fallback/registry.py` using env selection.
- `frontend/` (review PRs, don't push). `data/` contents (only the ingest entry points
  `backend/app/db/seed.py` in collaboration with C).
- `backend/app/services/*` algorithm bodies — Member C fills them; B keeps the
  boundaries/exports stable and may add repositories/APIs around them.

## Dependencies

- **From Member A:** feedback on contract ergonomics (response shapes, pagination,
  error codes) — captured in contract PRs.
- **From Member C:** provider selection contract (env vars `AI_*`, `GEOCODING_PROVIDER`)
  and typed service outputs. Until then, routes return 501 behind real schemas —
  that's the agreed Phase 1 behaviour.

## Phase mapping (PRD §17)

| Phase | Member B focus |
|---|---|
| 1 | This scaffold → review models/migrations, implement `POST /requests` intake pipeline (text + STT via mock), auth boundary |
| 2 | Expose clustering/geospatial/gap/priority endpoints on top of C's services |
| 3 | Review workflow + audit logging implementation, `/simulations`, deployment |

## Key files

| File | Purpose |
|---|---|
| `backend/app/main.py` | app factory, CORS, routers, error handlers |
| `backend/app/core/config.py` | env-based settings (`APP_ENV`, `DATABASE_URL`, …) |
| `backend/app/core/security.py` | demo JWT boundary — **placeholder, not production auth** |
| `backend/app/models/` | 18 PRD entities (SQLAlchemy 2) |
| `backend/migrations/` | Alembic; `0001` creates PostGIS + all tables |
| `backend/app/db/seed.py` | minimal SYNTHETIC seed (`make db-seed`) |
| `backend/scripts/export_openapi.py` | regenerates `docs/api/openapi/openapi.json` |

## Commands

```bash
make backend            # uvicorn :8000 (needs make db-up first)
make db-up / db-migrate / db-seed / db-reset
make test-backend       # pytest (DB tests auto-skip without postgres)
make lint               # ruff (also covers ai/)
make openapi-export     # after any schema change — commit the JSON
```

## First tasks (suggested)

1. Implement `POST /requests` for the text path: validate → persist
   (`citizen_requests`) → generate reference code → 201. Keep FR-004/005/006 rules.
2. Add audio upload handling for `POST /requests/{id}/audio` with file-type/size checks
   (validation only — transcription stays behind `SpeechToTextProvider`, mock default).
3. Implement demo `POST /auth/login` issuing role-scoped JWTs from a dev user table +
   wire `get_current_user` dependency into analyst+ routes.
4. Start CI on your first PR to confirm the workflow runs.
