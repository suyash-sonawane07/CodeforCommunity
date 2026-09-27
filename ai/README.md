# ai/ — Provider Abstraction Layer

Member C owns this directory. The backend depends **only on the interfaces** here,
never on a concrete provider (ADR-005, PRD §11).

## Interfaces (`ai/interfaces/`)

| Interface | Purpose (PRD) | Default impl |
|---|---|---|
| `SpeechToTextProvider` | FR-002/007/011 | `MockSTTProvider` |
| `LanguageDetector` | FR-003/010 | `MockLanguageDetector` |
| `TextNormalizer` | FR-012 | `MockTextNormalizer` |
| `IssueClassifier` | FR-014/017 | `MockIssueClassifier` |
| `EntityExtractor` | FR-015/016/017 | `MockEntityExtractor` |
| `EmbeddingProvider` | FR-019 | `MockEmbeddingProvider` |
| `Geocoder` | FR-026–028/033 | `MockGeocoder` |

Result dataclasses always carry `confidence` + `provider` (FR-017, §25 provenance).

## Adding a real provider (Member C, Phase 1/2)

1. Implement the interface in the matching package (`stt/`, `nlp/`, `embeddings/`, `geocoding/`).
2. Register it in `ai/fallback/registry.py`.
3. Document the env value in `.env.example` and `docs/team/MEMBER_C.md`.
4. Never let `backend/` import a concrete provider — only `ai/fallback/registry.py` resolves them.

## Selection (env)

```env
AI_STT_PROVIDER=mock            # mock | whisper
AI_LLM_PROVIDER=mock            # mock | <TBD>
AI_EMBEDDING_PROVIDER=mock      # mock | tfidf
GEOCODING_PROVIDER=mock         # mock | gazetteer
```

Default local env runs fully offline with mocks — no API keys.

## Tests

`ai/tests/` — interface conformance + mock determinism. Run: `make test-ai`.
