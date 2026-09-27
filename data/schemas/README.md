# data/schemas/

JSON Schema (draft-07) definitions validating `data/synthetic/`:

| Schema | Validates |
|---|---|
| `dataset_manifest.schema.json` | common envelope (version + `synthetic: true` + disclaimer) |
| `request.schema.json` | `synthetic/requests/*.json` rows |
| `demographic_indicator.schema.json` | `synthetic/demographics/*.json` rows |
| `infrastructure_asset.schema.json` | `synthetic/infrastructure/*.json` rows |
| `project.schema.json` | `synthetic/projects/*.json` rows |

These mirror the DB model shapes (PRD §9.1) for the **synthetic** pipeline only —
the database remains the source of truth for stored records.

Validate with `make validate-data` (invalid rows → `data/synthetic/_quarantine/`, FR-039).
`data/synthetic/_quarantine/` is gitignored.
