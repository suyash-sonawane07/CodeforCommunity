"""Provider registry — the ONLY place concrete providers are resolved (ADR-005).

Selection is environment-driven (AI_*_PROVIDER / GEOCODING_PROVIDER). Unknown
values raise so misconfiguration is loud, and mocks keep local dev offline.
"""

from __future__ import annotations

import os
from typing import Any, Callable

# name → zero-argument factory
STT_PROVIDERS: dict[str, Callable[[], Any]] = {
    "mock": lambda: _stt().MockSTTProvider(),
    "whisper": lambda: _stt().WhisperSTTProvider(),
}

LANGUAGE_PROVIDERS: dict[str, Callable[[], Any]] = {
    "mock": lambda: _nlp().MockLanguageDetector(),
}

LLM_PROVIDERS: dict[str, Callable[[], Any]] = {
    "mock": lambda: _nlp().MockTextNormalizer(),  # LLM choice TBD (PRD §11)
}

EMBEDDING_PROVIDERS: dict[str, Callable[[], Any]] = {
    "mock": lambda: _emb().MockEmbeddingProvider(),
    "tfidf": lambda: _emb().TfidfEmbeddingProvider(),
}

GEOCODING_PROVIDERS: dict[str, Callable[[], Any]] = {
    "mock": lambda: _geo().MockGeocoder(),
    "gazetteer": lambda: _geo().GazetteerGeocoder(),
    "nominatim": lambda: _geo().NominatimGeocoder(),
}

_CLASSIFIER_FACTORIES = {
    "mock": lambda: _nlp().MockIssueClassifier(),
}
_EXTRACTOR_FACTORIES = {
    "mock": lambda: _nlp().MockEntityExtractor(),
}


def _stt():
    from ai import stt as stt_module

    return stt_module


def _nlp():
    from ai import nlp as nlp_module

    return nlp_module


def _emb():
    from ai import embeddings as emb_module

    return emb_module


def _geo():
    from ai import geocoding as geo_module

    return geo_module


def _resolve(registry: dict, env_value: str, kind: str):
    factory = registry.get(env_value)
    if factory is None:
        raise ValueError(
            f"Unknown {kind} provider '{env_value}'. Available: {sorted(registry)}"
        )
    return factory()


def get_stt_provider() -> Any:
    return _resolve(STT_PROVIDERS, os.getenv("AI_STT_PROVIDER", "mock"), "STT")


def get_language_detector() -> Any:
    return _resolve(LANGUAGE_PROVIDERS, os.getenv("AI_LLM_PROVIDER", "mock"), "language")


def get_text_normalizer() -> Any:
    return _resolve(LLM_PROVIDERS, os.getenv("AI_LLM_PROVIDER", "mock"), "LLM")


def get_issue_classifier() -> Any:
    return _resolve(_CLASSIFIER_FACTORIES, os.getenv("AI_LLM_PROVIDER", "mock"), "classifier")


def get_entity_extractor() -> Any:
    return _resolve(_EXTRACTOR_FACTORIES, os.getenv("AI_LLM_PROVIDER", "mock"), "entity extractor")


def get_embedding_provider() -> Any:
    return _resolve(EMBEDDING_PROVIDERS, os.getenv("AI_EMBEDDING_PROVIDER", "mock"), "embedding")


def get_geocoder() -> Any:
    return _resolve(GEOCODING_PROVIDERS, os.getenv("GEOCODING_PROVIDER", "mock"), "geocoding")
