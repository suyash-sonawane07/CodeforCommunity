# data/ — Datasets, Schemas & Scripts

> **DISCLAIMER:** Everything under `data/synthetic/` is **SYNTHETIC** — fabricated for
> development and demo purposes only. Not official government data, not real citizen
> data, not validated public statistics (PRD FR-057, ADR-006).

| Path | Purpose | Owner |
|---|---|---|
| `synthetic/` | Versioned synthetic datasets (requests, demographics, infrastructure, projects) | Member C |
| `schemas/` | JSON Schemas validating the synthetic datasets | Member C |
| `scripts/ingest/` | Load validated datasets into PostgreSQL (with `dataset_version` tagging, FR-038) | Member C (+B) |
| `scripts/validate/` | `validate_synthetic.py` — schema + range checks; invalid rows quarantined (FR-039) | Member C |
| `scripts/seed/` | Optional seed helpers (canonical seed lives in `backend/app/db/seed.py`) | Member B+C |

## Commands

```bash
make validate-data   # validate all synthetic datasets (run after editing them)
```

## Rules (PRD §6.5 / FR-038/039/057)

1. Every dataset file carries `"SYNTHETIC"` metadata + a `dataset_version`.
2. Schema check + range checks on ingest; malformed rows are **quarantined**, never silently dropped.
3. Every DB row carries `dataset_version` + provenance (`source_label`).
4. No real names, phone numbers, or locations of real people — ever.
