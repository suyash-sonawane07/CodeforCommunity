# ADR-005 — AI provider abstraction

- **Status:** Accepted · **Date:** 2026-09-27 · **Owner:** Member C

## Context
PRD §11: no STT/LLM provider is confirmed; free-tier limits are unknown; every AI stage
needs a deterministic fallback; the backend must not bind to a vendor; the default local
environment must run **without paid API keys**.

## Decision
The `ai/` package defines provider interfaces — `SpeechToTextProvider`, `LanguageDetector`,
`TextNormalizer`, `IssueClassifier`, `EntityExtractor`, `EmbeddingProvider`, `Geocoder` —
with dataclass result schemas carrying mandatory `confidence` fields. Placeholder
implementations ship in pairs: `Mock*Provider` (deterministic, offline, default) and one
`*Provider` skeleton (e.g. `WhisperSTTProvider`) raising `NotImplementedError` until
Member C implements it in Phase 1/2. Provider selection is env-driven
(`AI_STT_PROVIDER=mock|whisper`, `AI_EMBEDDING_PROVIDER=mock|tfidf`, `GEOCODING_PROVIDER=mock|gazetteer`, …)
via `ai/fallback/registry.py`.

## Reason
Backend (`backend/app/services/*`) stays provider-agnostic; Member C can swap
implementations without touching routing (scaffold requirement §11 of the brief);
mocks make CI and every teammate's laptop work offline; mirrors the PRD's
deterministic-fallback discipline.

## Alternatives
Direct SDK calls inside backend routes (rejected — vendor lock, untestable);
LangChain-style framework (rejected — unnecessary dependency for 7 interfaces).

## Consequences
- Every provider result must carry `confidence` + provenance fields (FR-017, §25) — enforced by shared dataclasses.
- Mocks return deterministic, obviously-fake values; they must never be mistaken for real AI output (labels + `provider="mock"`).
- Real providers land behind the same interfaces; only `registry.py` changes.
