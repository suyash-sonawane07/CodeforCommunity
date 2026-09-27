# Ingest scripts (Member C + B, Phase 1–2)

Loads validated `data/synthetic/` datasets into PostgreSQL, tagging every row with
`dataset_version` + `source_label='synthetic'` (FR-038) and quarantining invalid rows
(FR-039 — run `data/scripts/validate/validate_synthetic.py` first).

**Status: SCAFFOLD — not implemented.** The canonical minimal seed lives in
`backend/app/db/seed.py` (`make db-seed`). TODO(PRD FR-034–039): implement
`ingest_dataset.py <file> --dataset-version synthetic_v0.2` with upsert semantics.
