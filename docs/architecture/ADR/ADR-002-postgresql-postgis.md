# ADR-002 — PostgreSQL + PostGIS

- **Status:** Accepted · **Date:** 2026-09-27 · **Owner:** Member B

## Context
The data model (PRD §9) needs relational integrity across 18 entities **and** geospatial
queries (nearest facility, distance, cluster roll-up, GeoJSON map output).

## Decision
Single PostgreSQL 16 instance with the PostGIS extension. `locations` carries
`geometry(Point, 4326)` plus the generic admin hierarchy; spatial distance queries run
in SQL later (Phase 2+). SQLAlchemy 2 + Alembic manage schema; the extension is created
by migration `0001` and by the DB container's init script (belt and braces).

## Reason
One engine covers relational + spatial needs, avoiding a second geo-database (PRD §12);
PostGIS is the standard OSS choice and is explicitly named in the PRD and challenge
architecture.

## Alternatives
MongoDB (rejected in PRD — weaker relational fit); separate geospatial service
(rejected — overengineering); SQLite for dev (rejected — geometry + JSONB parity with
prod would be lost).

## Consequences
- Local dev requires the PostGIS Docker image (`postgis/postgis:16-3.4`) — covered by Compose.
- Migration 0001 creates `postgis` extension; running the app against a plain Postgres fails by design (fail fast).
- PostGIS distance queries must be PoC'd on demo data volume (PRD §21.6) in Phase 2.
