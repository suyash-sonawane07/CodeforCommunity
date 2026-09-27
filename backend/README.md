# Backend — CivicPulse

**Owner: Member B (Backend/DB/DevOps)** — see `docs/team/MEMBER_B.md`.
Service bodies under `app/services/*` belong to **Member C** (`docs/team/MEMBER_C.md`).

**SCAFFOLD ONLY** — all business endpoints return `501 {"error":{"code":"NOT_IMPLEMENTED", ...}}`.

## Stack

FastAPI · SQLAlchemy 2 (declarative) · Alembic · PostgreSQL + PostGIS · pydantic-settings · pytest

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp ../.env.example ../.env        # adjust DATABASE_URL if needed
```

## Commands

```bash
uvicorn app.main:app --reload --port 8000   # dev server
pytest                                      # 26 tests (DB tests auto-skip without DB)
alembic upgrade head                        # apply migrations (needs PostGIS up)
alembic revision --autogenerate -m "..."    # new migration
python scripts/export_openapi.py            # refresh docs/api/openapi/openapi.json
```

Or from repo root: `make setup`, `make dev`, `make db-up`, `make migrate`, `make seed`, `make test-backend`, `make lint`, `make openapi-export`.

## Layout

| Path | Purpose |
|---|---|
| `app/main.py` | App factory, CORS, routers, /health with DB probe |
| `app/api/routes/` | 9 routers (auth, requests, clusters, geospatial, infrastructure, simulations, outcomes, datasets, audit) |
| `app/core/` | Config (pydantic-settings), logging, security (demo JWT + role hierarchy) |
| `app/db/` | session, base, seed |
| `app/models/` | 18 PRD entities (§9.1) — PostGIS geometry on locations |
| `app/schemas/` | Pydantic request/response schemas (+ error envelope) |
| `app/services/` | **Empty boundaries** — dataclass I/O + `NotImplementedError` (Member C) |
| `app/repositories/` | Data-access layer skeleton |
| `migrations/` | Alembic; `0001_initial_schema.py` creates postgis ext + 18 tables |
| `tests/` | unit / integration / smoke (pytest) |

## Known constraints

- Python 3.9: use `Optional[X]`, not `X | None` (runtime unions fail at class creation).
- Docker absent on this machine: DB tests auto-skip; `/health` reports
  `database: "unavailable"` until Postgres runs (acceptable for scaffold).
- Demo auth issues a signed dev JWT per role — **not** production auth.
