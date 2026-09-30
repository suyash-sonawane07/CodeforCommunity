"""AI layer scaffold tests — interface conformance + mock determinism.

These verify the SCAFFOLD (interfaces resolve, mocks are deterministic and
honest about being mocks). No real AI capability is asserted.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

from ai.embeddings import MockEmbeddingProvider, TfidfEmbeddingProvider  # noqa: E402
from ai.fallback import (  # noqa: E402
    get_embedding_provider,
    get_geocoder,
    get_issue_classifier,
    get_language_detector,
    get_stt_provider,
    get_text_normalizer,
)
from ai.geocoding import MockGeocoder  # noqa: E402
from ai.interfaces.embeddings import EmbeddingProvider  # noqa: E402
from ai.interfaces.geocoding import Geocoder  # noqa: E402
from ai.interfaces.language import LanguageDetector  # noqa: E402
from ai.interfaces.nlp import (  # noqa: E402
    EntityExtractor,
    IssueClassifier,
    TextNormalizer,
)
from ai.interfaces.stt import SpeechToTextProvider  # noqa: E402
from ai.nlp import (  # noqa: E402
    MockEntityExtractor,
    MockIssueClassifier,
    MockLanguageDetector,
    MockTextNormalizer,
)
from ai.stt import MockSTTProvider, WhisperSTTProvider  # noqa: E402


def test_stt_mock_is_deterministic_and_labelled():
    p = MockSTTProvider()
    assert isinstance(p, SpeechToTextProvider)
    r1 = p.transcribe("dGVzdCBhdWRpbw==")
    r2 = p.transcribe("dGVzdCBhdWRpbw==")
    assert r1 == r2
    assert r1.provider == "mock"
    assert "MOCK" in r1.text
    assert r1.uncertainty_notes  # honesty about mock output


def test_stt_mock_rejects_invalid_base64():
    with pytest.raises(ValueError):
        MockSTTProvider().transcribe("!!!not-base64!!!")


def test_whisper_provider_is_placeholder():
    with pytest.raises(NotImplementedError):
        WhisperSTTProvider().transcribe("dGVzdA==")


def test_nlp_mocks_conform_and_stay_conservative():
    assert isinstance(MockLanguageDetector(), LanguageDetector)
    assert isinstance(MockTextNormalizer(), TextNormalizer)
    assert isinstance(MockIssueClassifier(), IssueClassifier)
    assert isinstance(MockEntityExtractor(), EntityExtractor)

    det = MockLanguageDetector().detect("बस नहीं मिलती")
    assert det.language == "unknown"  # conservative default (PRD §11)

    cls = MockIssueClassifier().classify("no bus after 5pm")
    assert cls.label == "other"  # never pretends to classify
    assert set(cls.taxonomy) == {"transport", "water", "health", "education", "roads", "other"}


def test_embedding_mock_is_fixed_size_and_deterministic():
    p = MockEmbeddingProvider()
    assert isinstance(p, EmbeddingProvider)
    v1 = p.embed("no bus").vector
    v2 = p.embed("no bus").vector
    assert v1 == v2 and len(v1) == 8


def test_tfidf_embedding_conforms_and_embeds():
    p = TfidfEmbeddingProvider()
    assert isinstance(p, EmbeddingProvider)
    res = p.embed("drinking water pipeline broken")
    assert len(res.vector) == 64
    assert res.confidence is not None
    assert any(x != 0.0 for x in res.vector)


def test_geocoder_mock_never_resolves():
    g = MockGeocoder()
    assert isinstance(g, Geocoder)
    r = g.geocode("near the old temple")
    assert r.resolved is False
    assert r.latitude is None and r.longitude is None  # FR-021/033


def test_registry_resolves_mocks_by_default(monkeypatch):
    for var in (
        "AI_STT_PROVIDER",
        "AI_LLM_PROVIDER",
        "AI_EMBEDDING_PROVIDER",
        "GEOCODING_PROVIDER",
    ):
        monkeypatch.delenv(var, raising=False)
    assert isinstance(get_stt_provider(), MockSTTProvider)
    assert isinstance(get_language_detector(), MockLanguageDetector)
    assert isinstance(get_text_normalizer(), MockTextNormalizer)
    assert isinstance(get_issue_classifier(), MockIssueClassifier)
    assert isinstance(get_embedding_provider(), MockEmbeddingProvider)
    assert isinstance(get_geocoder(), MockGeocoder)


def test_registry_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("GEOCODING_PROVIDER", "nonexistent")
    with pytest.raises(ValueError):
        get_geocoder()
