# Seed scripts

The canonical seed is `backend/app/db/seed.py` → run with `make db-seed`
(minimal structurally-valid SYNTHETIC rows only, per brief §9).

Place additional seed helpers here (e.g. loading `data/synthetic/*.json` once
`data/scripts/ingest/` is implemented). All seeded rows must carry
`dataset_version` + synthetic provenance (FR-038/057).
