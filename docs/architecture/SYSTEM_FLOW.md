# System Flow — PRD journeys → scaffold boundaries

This document maps the PRD's end-to-end journeys (PRD §7) onto the scaffold's module
boundaries. **Every intelligence step is a placeholder** — the flow describes where logic
will live, not what exists. Traceability: pipeline stages = PRD §11; endpoints = §10.1;
screens = §8.1.

## Pipeline stages (PRD §11) and their scaffold home

| # | Stage (FR refs) | Scaffold home | Owner | Status |
|---|---|---|---|---|
| 1 | Intake — text/voice (FR-001–009) | `POST /requests`, `POST /requests/{id}/audio` (route schema ready) | B | 501 placeholder |
| 2 | Language detection (FR-003, FR-010) | `ai/interfaces/language.py` → `LanguageDetector` | C | mock provider |
| 3 | Transcription (FR-002, FR-007, FR-011) | `ai/interfaces/stt.py` → `SpeechToTextProvider` | C | mock provider |
| 4 | Normalisation (FR-012) | `ai/interfaces/nlp.py` → `TextNormalizer` | C | mock provider |
| 5 | Entity extraction (FR-015–016) | `ai/interfaces/nlp.py` → `EntityExtractor` | C | mock provider |
| 6 | Issue classification (FR-014, FR-017) | `ai/interfaces/nlp.py` → `IssueClassifier` | C | mock provider |
| 7 | Geospatial resolution (FR-026–028, FR-033) | `ai/interfaces/geocoding.py` → `Geocoder` + `backend/app/services/geospatial/` | C | empty boundary |
| 8 | Deduplication / clustering (FR-019–025) | `EmbeddingProvider` + `backend/app/services/clustering/` | C | empty boundary |
| 9 | Dataset matching (FR-030–039) | `backend/app/services/geospatial/` + `data/scripts/ingest/` | B+C | empty boundary |
| 10 | Gap detection (FR-040–044) | `backend/app/services/gap_detection/` | C | empty boundary |
| 11 | Priority / equity (FR-045–050) | `backend/app/services/prioritisation/` | C | empty boundary |
| 12 | Evidence generation (FR-051–052) | `backend/app/services/evidence/` | C | empty boundary |
| 13 | Human review (FR-058–063) | `POST /clusters/{id}/review`, `PATCH /clusters/{id}`, `review_actions` + `audit_logs` models | B | 501 placeholder |
| 14 | Simulation (FR-053–056) | `backend/app/services/simulation/` | C | empty boundary |
| 15 | Outcome (FR-064–067) | `backend/app/services/evidence/` (outcome part) | C | empty boundary |

## Journey wiring (PRD §7)

| Journey | Route through scaffold | Endpoint(s) | Screen(s) |
|---|---|---|---|
| 1–2 Marathi/Hindi intake | FE citizen form → requests router → STT/langdetect providers | `POST /requests`, `POST /requests/{id}/audio`, `GET /requests/{id}` | S-01–S-03 |
| 3 Clustering | clustering service + embeddings provider | (internal; reflected in `GET /clusters`) | S-07 |
| 4 Context match | geospatial service + dataset tables | `GET /clusters/{id}`, `GET /infrastructure` | S-07/S-09 |
| 5 Gap flag | gap_detection service | `GET /clusters/{id}/gap-analysis` | S-08/S-09 |
| 6 Review | review router + audit log | `POST /clusters/{id}/review`, `PATCH /clusters/{id}` | S-12/S-13 |
| 7 Simulation | simulation service | `POST /simulations` | S-11 |
| 8 Outcome | evidence service (outcome) | `GET /clusters/{id}/outcome` | S-14 |
| 9 Low-confidence location | geocoder confidence → `location_unresolved` queue | `GET /geospatial/clusters` (needs-geocoding filter) | S-06 |
| 10 Existing-project conflict | gap_detection project check | `GET /clusters/{id}/gap-analysis` | S-09 |

## Data flow rules enforced by the scaffold (PRD §25)

- Original text/audio preserved verbatim (`citizen_requests.raw_text` immutable; FR-004).
- Location uncertainty represented (`locations.confidence`, `location_unresolved`; FR-028/033).
- Evidence traceable (`evidence_records.payload` regenerable snapshot; FR-051).
- Synthetic data labelled (`public_datasets.source_label = 'synthetic'`; FR-038/057).
- AI suggestion ≠ human decision (`review_status` separate from `status`; FR-063).
