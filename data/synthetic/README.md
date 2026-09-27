# data/synthetic/ — SYNTHETIC demo datasets

> ⚠️ **ALL DATA IN THIS DIRECTORY IS SYNTHETIC.**
> It is **not** official government data, **not** real citizen data, and **not**
> validated public statistics. Every file carries `"SYNTHETIC"` metadata
> (PRD FR-057; ADR-006). No real names, phone numbers, or identifiable people.

## Purpose

Structurally valid example records to verify:
database connectivity · API serialisation · cluster relations · location relations ·
infrastructure relations · project relations — and later, the demo dataset
(1 state, 2–3 districts, ~15–20 requests, PRD §15) built on the same schemas.

## Inventory (v0.1 — scaffold samples)

| File | Rows | Validated by |
|---|---|---|
| `requests/requests_v0.1.json` | 4 | `data/schemas/request.schema.json` |
| `demographics/demographics_v0.1.json` | 2 | `data/schemas/demographic_indicator.schema.json` |
| `infrastructure/infrastructure_v0.1.json` | 3 | `data/schemas/infrastructure_asset.schema.json` |
| `projects/projects_v0.1.json` | 2 | `data/schemas/project.schema.json` |

## Versioning (FR-038)

Filename = content version. When the dataset changes materially, bump the version
(`..._v0.2.json`) rather than editing in place, and record it in the
`public_datasets` registry on ingest.

## Demo-journey requirement (PRD §15)

When Member C builds the demo dataset: include 2–3 seeded "existing projects", **one of
which deliberately overlaps a cluster** — needed to demonstrate Journey 10 (existing
project prevents a duplicate gap flag).
