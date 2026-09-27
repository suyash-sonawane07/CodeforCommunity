# Member C — AI/ML, Geospatial & Data

> Owns the AI pipeline, geospatial intelligence, deterministic decision-support
> algorithms and all datasets (PRD §17.1). Primary dependency: backend schemas and
> the `ai/` interface contracts.

## Owns

- `ai/` — provider interfaces, mock + real provider implementations, prompts, fallbacks.
- `data/` — synthetic dataset (labelled `SYNTHETIC`), JSON Schemas, ingest/validate/seed scripts.
- `backend/app/services/` — algorithm bodies: `clustering/`, `geospatial/`,
  `gap_detection/`, `prioritisation/`, `evidence/`, `simulation/`
  (currently empty boundaries with typed inputs/outputs).

## Must NOT casually modify

- `backend/app/api/routes/*` — endpoints belong to Member B. Deliver algorithms as
  service functions/dataclasses; B exposes them.
- `backend/app/models/`, migrations, `deploy/` — schema/infra changes go through
  Member B via PR.
- `frontend/` — never.
- Shared schemas (`backend/app/schemas/`) only via contract PRs.

## Dependencies

- **From Member B:** Pydantic schemas (`backend/app/schemas/`) and stable service
  boundaries; also the DB (models carry `confidence`, `source`, `dataset_version`,
  `review_status`, `uncertainty_notes` fields your outputs must populate).
- **From Member A:** none directly; the evidence panel (S-08) renders whatever the
  `evidence_records.payload` schema defines — agree it early.

## Provider selection contract (already wired)

```env
AI_STT_PROVIDER=mock            # mock | whisper (implement in Phase 1 PoC)
AI_LLM_PROVIDER=mock            # mock | <TBD team decision, PRD §11>
AI_EMBEDDING_PROVIDER=mock      # mock | tfidf (fallback) | sentence-transformers
GEOCODING_PROVIDER=mock         # mock | gazetteer (curated) | nominatim
```

Add a real provider = implement the interface + register it in
`ai/fallback/registry.py` + document env values here. Backend code never imports a
concrete provider.

## Phase mapping (PRD §17)

| Phase | Member C focus |
|---|---|
| 1 | Synthetic dataset v1 (1 state, 2–3 districts) + STT/langdetect PoC on sample audio (§21.6) |
| 2 | Embedding+geo/time clustering (FR-019–025), geocoding w/ confidence (FR-026–033), gap detection (FR-040–044), priority factors (FR-045–050) |
| 3 | Simulator logic (FR-053–056) + synthetic outcome data (FR-064–067) |

## Commands

```bash
make test-ai            # ai/ interface + mock tests
make validate-data      # data/synthetic vs data/schemas (quarantine on failure, FR-039)
cd backend && .venv/bin/pytest tests/unit   # service-boundary tests
```

## First tasks (suggested)

1. Choose the demo state/districts; draft `data/synthetic/{demographics,infrastructure,projects,requests}` v1 against `data/schemas/`.
2. Prototype STT + language detection on real sample Hindi/Marathi audio with the
   chosen provider behind `WhisperSTTProvider` — record measured confidence behaviour
   (PRD §21.6 requires this PoC before Phase 2).
3. Sketch the embedding similarity PoC (curated 30-pair duplicate/distinct set, PRD §15).
