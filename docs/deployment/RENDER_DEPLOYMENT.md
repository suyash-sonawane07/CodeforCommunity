# Render Deployment Guide — CivicPulse

This repository is pre-configured for automated deployment to [Render](https://render.com) using Infrastructure-as-Code (Render Blueprint `render.yaml`) or manual service creation.

---

## Architecture on Render

```
                             [ Citizen / Public Browser ]
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │  civicpulse-frontend (Next.js 14)     │
                      │  - Google Material Design 3 UI        │
                      │  - Gemini Copilot AI Integration      │
                      │  - Citizen / Supervisor / Admin Hub   │
                      └───────────────────┬───────────────────┘
                                          │
                                          │  API Proxy / JWT Cookie
                                          ▼
                      ┌───────────────────────────────────────┐
                      │  civicpulse-backend (FastAPI + AI)    │
                      │  - Multilingual BRICS NLP Pipeline    │
                      │  - Geospatial HDBSCAN Clustering      │
                      │  - Explainable Priority Formula       │
                      │  - Deterministic Policy Simulator     │
                      └───────────────────┬───────────────────┘
                                          │
                                          │  SQLAlchemy + GeoAlchemy2
                                          ▼
                      ┌───────────────────────────────────────┐
                      │  civicpulse-db (PostgreSQL + PostGIS) │
                      │  - Seeded synthetic datasets          │
                      │  - Immutable audit logs               │
                      └───────────────────────────────────────┘
```

---

## Option 1: One-Click Blueprint Deployment (Recommended)

1. **Connect GitHub to Render**:
   - Log in to your [Render Dashboard](https://dashboard.render.com).
   - Click **New +** and select **Blueprint**.
   - Connect the `CodeforCommunity` repository.

2. **Render auto-detects `render.yaml`**:
   - It will automatically create:
     - **`civicpulse-db`**: Managed PostgreSQL database.
     - **`civicpulse-backend`**: Python FastAPI Web Service with automated database migration (`alembic upgrade head`) and synthetic demo data seeding (`python -m app.db.seed`).
     - **`civicpulse-frontend`**: Next.js Web Service pre-wired to the backend with Next.js API proxy and server-side JWT authentication.

3. **Deploy**:
   - Click **Apply**.
   - Render will build and deploy the database and both services.

---

## Option 2: Manual Web Service Setup on Render

If creating services manually:

### 1. Create PostgreSQL Database
- **Name**: `civicpulse-db`
- **Database**: `civicpulse`
- **User**: `civicpulse`
- Note the **Internal Database URL**.

### 2. Create Backend Web Service
- **Name**: `civicpulse-backend`
- **Runtime**: `Python`
- **Build Command**:
  ```bash
  pip install --upgrade pip && pip install -r backend/requirements.txt -r ai/requirements.txt
  ```
- **Start Command**:
  ```bash
  cd backend && PYTHONPATH=..:$PYTHONPATH alembic upgrade head && PYTHONPATH=..:$PYTHONPATH python -m app.db.seed && PYTHONPATH=..:$PYTHONPATH uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- **Health Check Path**: `/health`
- **Environment Variables**:
  - `DATABASE_URL`: *(Your Render PostgreSQL connection string — the app auto-converts `postgres://` to `postgresql+psycopg2://`)*
  - `PYTHONPATH`: `..:.`
  - `CORS_ORIGINS`: `*`
  - `AI_STT_PROVIDER`: `mock`
  - `AI_LLM_PROVIDER`: `mock`
  - `AI_EMBEDDING_PROVIDER`: `mock`
  - `GEOCODING_PROVIDER`: `mock`
  - `APP_ENV`: `production`
  - `JWT_SECRET`: *(A random 32+ character string)*

### 3. Create Frontend Web Service
- **Name**: `civicpulse-frontend`
- **Root Directory**: `frontend`
- **Runtime**: `Node`
- **Build Command**:
  ```bash
  npm install && npm run build
  ```
- **Start Command**:
  ```bash
  npm run start
  ```
- **Environment Variables**:
  - `NEXT_PUBLIC_API_BASE_URL`: `https://civicpulse-backend.onrender.com`
  - `BACKEND_URL`: `https://civicpulse-backend.onrender.com`
  - `JWT_SECRET`: *(Same string as backend `JWT_SECRET`)*
  - `NODE_ENV`: `production`
  - `NEXT_TELEMETRY_DISABLED`: `1`

---

## Demo Credentials for Evaluators

Once deployed, evaluators can test the system using pre-configured RBAC personas:

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Intelligence Analyst** | `analyst@civicpulse.dev` | Any (`demo123`) | Cluster exploration, gap detection, evidence panel |
| **Independent Reviewer** | `reviewer@civicpulse.dev` | Any (`demo123`) | Human review gate (approve / reject / corrections) |
| **Decision-Maker** | `decision@civicpulse.dev` | Any (`demo123`) | Policy what-if simulator & capital budget allocation |
| **System Administrator** | `admin@civicpulse.dev` | Any (`demo123`) | Public dataset registry & immutable audit trails |
| **Citizen Demo User** | `user@demo.com` | `demo123` | Personal request tracking & grievance submission |
| **Demo Supervisor** | `supervisor@demo.com` | `demo123` | Quick cluster review and status management |
