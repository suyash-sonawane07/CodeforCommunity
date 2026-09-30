"""CivicPulse FastAPI application — modular monolith (ADR-001).

SCAFFOLD ONLY: /health, /, /version are implemented; all PRD business endpoints
(PRD §10.1) are exposed with real schemas and return 501 until implemented.
"""

import sys
from pathlib import Path

# Ensure root (containing ai/ layer) is on sys.path
_root_dir = str(Path(__file__).resolve().parents[2])
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import models  # noqa: F401 — register all models with Alembic/Base
from app.api.routes import (
    audit,
    auth,
    clusters,
    datasets,
    geospatial,
    infrastructure,
    outcomes,
    requests,
    simulations,
    webhooks,
)
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.schemas import HealthResponse, VersionResponse

settings = get_settings()
configure_logging(settings.LOG_LEVEL)

app = FastAPI(
    title=f"{settings.APP_NAME} API",
    version=settings.APP_VERSION,
    description=(
        "AI Development-Needs Intelligence Layer — Code for Communities 2.0 Track 1. "
        "Intake, Multilingual NLP, Clustering, Geospatial, Evidence, Gap Detection, and Policy Simulation. "
        "Contract: docs/api/API_CONTRACT.md"
    ),
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS via configuration only (never wildcard + credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (
    auth.router,
    requests.router,
    clusters.router,
    geospatial.router,
    infrastructure.router,
    simulations.router,
    outcomes.router,
    datasets.router,
    audit.router,
    webhooks.router,
):
    app.include_router(router)


# ---------------------------------------------------------------- infra endpoints


@app.get("/health", response_model=HealthResponse, tags=["infra"], summary="Liveness/readiness")
def health() -> HealthResponse:
    db_status = "unknown"
    try:  # lightweight connectivity probe; never crashes health
        from sqlalchemy import text

        from app.db.session import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:  # noqa: BLE001 — health must always answer
        db_status = "unavailable"
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        env=settings.APP_ENV,
        database=db_status,
    )


@app.get("/", response_model=VersionResponse, tags=["infra"], summary="Service info")
def root() -> VersionResponse:
    return VersionResponse(name=settings.APP_NAME, version=settings.APP_VERSION)


@app.get("/version", response_model=VersionResponse, tags=["infra"], summary="Version")
def version() -> VersionResponse:
    return VersionResponse(name=settings.APP_NAME, version=settings.APP_VERSION)


# ---------------------------------------------------------------- error handlers


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Uniform error envelope for unhandled errors (never leaks internals)."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {"code": "INTERNAL_ERROR", "message": "Internal server error", "details": None}
        },
    )
