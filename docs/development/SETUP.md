# Local Setup

Pick **one** workflow. Both use the same ports: frontend **3000**, backend **8000**, db **5432**.

## 0. Prerequisites

| Workflow | Needs |
|---|---|
| A — Full Docker | Docker Desktop (or Engine) with Compose v2 |
| B — Hybrid | Python 3.9+ · Node.js 20+ · Docker (for the database only) |

## 1. Get the code + environment

```bash
git clone <repo-url> civicpulse && cd civicpulse
cp .env.example .env      # never commit .env
```

The defaults in `.env.example` run the entire stack with **no paid API keys**
(all AI providers = `mock`).

## 2. Option A — full Docker

```bash
make dev          # db + backend + frontend (hot reload), builds images
make dev-logs     # tail logs
make dev-down     # stop
```

First start takes a few minutes (image builds). Backend waits for the db health check
before serving. Open http://localhost:3000 and http://localhost:8000/docs.

## 3. Option B — hybrid (db in Docker, apps local — best for daily dev)

```bash
make setup        # backend venv + frontend npm install (one-time)
make db-up        # PostgreSQL 16 + PostGIS on :5432 (health-checked)
make db-migrate   # alembic upgrade head (creates PostGIS extension + all tables)
make db-seed      # minimal SYNTHETIC seed rows
make backend      # terminal 1 → http://localhost:8000  (Swagger at /docs)
make frontend     # terminal 2 → http://localhost:3000
```

Backend reads `DATABASE_URL` from `.env` (defaults to `localhost:5432`).

## 4. Verify the stack

```bash
curl localhost:8000/health     # {"status":"ok", ...}
curl localhost:8000/version
make smoke                     # live-stack tests (skips what isn't running)
```

Frontend→backend connectivity: open http://localhost:3000/citizen and submit the
placeholder form — it calls `POST /requests` and surfaces the scaffold `501` envelope
(proof the client wiring works end-to-end).

## 5. Database commands

| Command | Effect |
|---|---|
| `make db-up` / `make db-down` | start / stop Postgres+PostGIS |
| `make db-migrate` | apply Alembic migrations |
| `make db-seed` | load minimal synthetic seed |
| `make db-reset` | **destructive:** drop volumes → migrate → seed |

Create a new migration after model edits (Member B):

```bash
cd backend && .venv/bin/alembic revision --autogenerate -m "describe change"
make db-migrate
```

## 6. Troubleshooting

- **Port already in use** — another service owns 3000/8000/5432; stop it or override `FRONTEND_PORT`/`BACKEND_PORT` in `.env`.
- **`postgres` extension errors** — you are not on the PostGIS image; use `make db-up` (uses `postgis/postgis:16-3.4`).
- **Docker absent** — use Option B; the db still needs Docker. Ask Member B for a managed dev db if neither is possible.
- **Frontend can't reach backend** — check `NEXT_PUBLIC_API_BASE_URL` in `.env` (must be `http://localhost:8000` for local dev; restarting the dev server is required after changing it).

More: [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`WORKFLOW.md`](WORKFLOW.md) · member guides in `../team/`.
