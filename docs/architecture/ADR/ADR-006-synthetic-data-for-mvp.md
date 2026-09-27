# ADR-006 — Synthetic data for MVP

- **Status:** Accepted · **Date:** 2026-09-27 · **Owner:** Member C

## Context
PRD §6.5/§19 (R-04): no confirmed access to any government dataset; waiting to verify
data.gov.in / Census / eGramSwaraj access would block gap detection, the map and the
demo. PRD requires dataset provenance labelling (`confirmed | candidate | synthetic`)
and visible `SYNTHETIC` tagging in the UI (FR-038, FR-057).

## Decision
Build a small **SYNTHETIC** dataset (1 state, 2–3 districts, ~15–20 citizen requests,
demographic/infrastructure/projects rows) under `data/synthetic/`, every file carrying
`"SYNTHETIC"` metadata. JSON Schema files under `data/schemas/` validate them;
`data/scripts/validate/validate_synthetic.py` (`make validate-data`) enforces
schema + range checks and quarantines invalid rows rather than silently dropping
(FR-039). Seed data lives in `backend/app/db/seed.py` and reuses the same schema rules.

## Reason
Deterministic demo path from Day 1 (PRD fallback plan); no legal/PII risk — no real
citizen data; versioning fields (`dataset_version`, `ingested_at`) on every row keep
provenance auditable (FR-038).

## Alternatives
Live data.gov.in integration (rejected — unverified access, P2 per §16); fully manual
DB inserts (rejected — not versioned/repeatable).

## Consequences
- Every UI surface showing this data must display a `SYNTHETIC` badge (FR-057) — Member A TODO in each screen.
- The simulator's cost assumptions and the outcome demo must disclose synthetic basis (FR-056, FR-067).
- Swapping in verified public data later means adding a new versioned dataset, not changing schemas.
