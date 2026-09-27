# ============================================================
# CivicPulse — developer task runner
# `make help` lists everything. Ports: frontend 3000 · backend 8000 · db 5432
# ============================================================

SHELL := /bin/bash

BACKEND_DIR   := backend
FRONTEND_DIR  := frontend
VENV_BIN      := $(BACKEND_DIR)/.venv/bin
PY            := $(VENV_BIN)/python

# Use root .env if present; compose variables otherwise fall back to in-file defaults.
ENV_FILE      := $(if $(wildcard .env),--env-file .env,)
COMPOSE       := docker compose $(ENV_FILE) -f deploy/docker-compose.yml
COMPOSE_DEV   := $(COMPOSE) -f deploy/docker-compose.dev.yml

BACKEND_PORT  ?= 8000
FRONTEND_PORT ?= 3000

.DEFAULT_GOAL := help
.PHONY: help setup venv npm-install dev dev-down dev-logs backend frontend \
        db-up db-down db-migrate db-seed db-reset \
        test test-backend test-frontend test-ai test-contract smoke \
        lint format openapi-export validate-data

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# ---------- One-time setup ----------
setup: venv npm-install ## First-time setup: backend venv + frontend deps

venv: ## Create backend/.venv and install Python deps
	python3 -m venv $(BACKEND_DIR)/.venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r $(BACKEND_DIR)/requirements.txt

npm-install: ## Install frontend dependencies
	cd $(FRONTEND_DIR) && npm install

# ---------- Run ----------
dev: ## Full stack via Docker (db + backend + frontend), hot-reload overlay
	$(COMPOSE_DEV) up -d --build
	@echo "Frontend: http://localhost:$(FRONTEND_PORT)  Backend: http://localhost:$(BACKEND_PORT)  Swagger: http://localhost:$(BACKEND_PORT)/docs"

dev-down: ## Stop the Docker stack
	$(COMPOSE_DEV) down

dev-logs: ## Tail Docker stack logs
	$(COMPOSE_DEV) logs -f

backend: ## Run backend locally (needs db-up first): uvicorn with hot reload
	cd $(BACKEND_DIR) && .venv/bin/uvicorn app.main:app --reload --port $(BACKEND_PORT)

frontend: ## Run frontend dev server locally
	cd $(FRONTEND_DIR) && npm run dev

# ---------- Database ----------
db-up: ## Start PostgreSQL+PostGIS container (Docker)
	$(COMPOSE) up -d db
	@until $(COMPOSE) exec -T db pg_isready -U $${POSTGRES_USER:-civicpulse} >/dev/null 2>&1; do sleep 1; done
	@echo "Database ready on localhost:5432"

db-down: ## Stop the database container
	$(COMPOSE) stop db

db-migrate: ## Apply Alembic migrations
	cd $(BACKEND_DIR) && .venv/bin/alembic upgrade head

db-seed: ## Seed minimal SYNTHETIC example data
	cd $(BACKEND_DIR) && .venv/bin/python -m app.db.seed

db-reset: ## DROP everything and re-migrate + re-seed (destructive)
	$(COMPOSE) down -v
	$(COMPOSE) up -d db
	@until $(COMPOSE) exec -T db pg_isready -U $${POSTGRES_USER:-civicpulse} >/dev/null 2>&1; do sleep 1; done
	$(MAKE) db-migrate db-seed

# ---------- Quality ----------
test: test-backend test-ai test-contract test-frontend ## Run all test suites

test-backend: ## Backend pytest (unit + smoke; DB tests auto-skip)
	cd $(BACKEND_DIR) && .venv/bin/pytest

test-ai: ## AI layer tests (mock providers)
	cd ai && ../backend/.venv/bin/pytest

test-contract: ## Root contract tests (OpenAPI surface vs PRD endpoints)
	cd $(BACKEND_DIR) && .venv/bin/pytest ../tests/contract

test-frontend: ## Frontend jest tests
	cd $(FRONTEND_DIR) && npm test

smoke: ## Live-stack smoke test (start the stack first; skips if backend down)
	cd $(BACKEND_DIR) && .venv/bin/pytest ../tests/smoke

lint: ## Ruff (backend+ai), eslint + prettier (frontend)
	cd $(BACKEND_DIR) && .venv/bin/ruff check .
	cd ai && ../backend/.venv/bin/ruff check .
	cd $(FRONTEND_DIR) && npm run lint && npm run format:check

format: ## Auto-format: ruff format + prettier write
	cd $(BACKEND_DIR) && .venv/bin/ruff format . && .venv/bin/ruff check --fix .
	cd ai && ../backend/.venv/bin/ruff format . && ../backend/.venv/bin/ruff check --fix .
	cd $(FRONTEND_DIR) && npm run format

# ---------- Contracts / data ----------
openapi-export: ## Regenerate docs/api/openapi/openapi.json from the FastAPI app
	cd $(BACKEND_DIR) && .venv/bin/python scripts/export_openapi.py

validate-data: ## Validate data/synthetic samples against data/schemas
	$(PY) data/scripts/validate/validate_synthetic.py
