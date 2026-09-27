# Deploy — Docker setup

Docker is **optional** for this scaffold: the hybrid workflow (Postgres in Docker,
backend + frontend running locally) is the documented default in
`docs/development/SETUP.md` because the primary dev machine has no Docker daemon.

## Full stack in Docker

```bash
cp .env.example .env
docker compose -f deploy/docker-compose.yml up --build
# dev overlay (hot reload):
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml up --build
```

Services: `db` (postgis/postgis:16-3.4, port 5432) → `backend` (alembic upgrade +
uvicorn, port 8000) → `frontend` (port 3000). Healthchecks gate startup order.

## Just the database (recommended locally)

```bash
docker compose -f deploy/docker-compose.yml up -d db
cd backend && alembic upgrade head && python -m app.db.seed
```

If `make db-up` fails because Docker is missing, install Docker Desktop or use a
remote/managed Postgres with the PostGIS extension and set `DATABASE_URL`.
