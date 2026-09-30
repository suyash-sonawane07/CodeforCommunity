"""Tests for real AI providers (Nominatim, Gemini, OpenAI, Whisper, TF-IDF)."""

import base64
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai.embeddings import (
    GeminiEmbeddingProvider,
    OpenAIEmbeddingProvider,
    TfidfEmbeddingProvider,
)
from ai.fallback import (
    get_embedding_provider,
    get_geocoder,
    get_issue_classifier,
    get_language_detector,
    get_stt_provider,
    get_text_normalizer,
)
from ai.geocoding import CompositeGeocoder, NominatimGeocoder
from ai.interfaces.language import LanguageDetector
from ai.interfaces.nlp import EntityExtractor, IssueClassifier, TextNormalizer
from ai.nlp import GeminiNLPProvider, OpenAINLPProvider
from ai.stt import GeminiSTTProvider, WhisperSTTProvider


# -------------------------------------------------------------
# 1. Geocoding Providers
# -------------------------------------------------------------
def test_nominatim_empty_string():
    g = NominatimGeocoder()
    res = g.geocode("")
    assert res.resolved is False
    assert res.latitude is None
    assert res.longitude is None


def test_nominatim_mocked_success():
    g = NominatimGeocoder()
    mock_payload = [
        {
            "lat": "19.8762",
            "lon": "75.3433",
            "importance": 0.85,
            "display_name": "Aurangabad, Maharashtra, India",
            "address": {
                "city": "Aurangabad",
                "state_district": "Chhatrapati Sambhajinagar",
                "state": "Maharashtra",
            },
        }
    ]

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_payload
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value.__enter__.return_value = mock_client

        res = g.geocode("Aurangabad")
        assert res.resolved is True
        assert res.latitude == 19.8762
        assert res.longitude == 75.3433
        assert res.admin_hierarchy["state"] == "Maharashtra"
        assert res.confidence >= 0.80


def test_composite_geocoder_gazetteer_hit():
    comp = CompositeGeocoder()
    # "Demo Village 1" is in the local curated gazetteer
    res = comp.geocode("Demo Village 1, Demo Block A")
    assert res.resolved is True
    assert res.latitude == 19.876
    assert res.provider == "gazetteer"


def test_composite_geocoder_falls_back_to_nominatim():
    comp = CompositeGeocoder()
    with patch.object(comp.nominatim, "geocode") as mock_nom:
        from ai.interfaces.schemas import GeocodeResult

        mock_nom.return_value = GeocodeResult(
            provider="nominatim",
            resolved=True,
            latitude=28.6139,
            longitude=77.2090,
            confidence=0.88,
            admin_hierarchy={"state": "Delhi", "district": "New Delhi"},
        )
        res = comp.geocode("New Delhi Central")
        assert res.resolved is True
        assert res.latitude == 28.6139
        mock_nom.assert_called_once()


# -------------------------------------------------------------
# 2. Embeddings Providers
# -------------------------------------------------------------
def test_tfidf_embedding_similarity():
    embedder = TfidfEmbeddingProvider(dim=64)
    res_water1 = embedder.embed("Drinking water pipeline broken in village")
    res_water2 = embedder.embed("Pani nall leakage problem in ward")
    res_road = embedder.embed("Road has potholes and broken asphalt")

    # Dot product of normalized vectors = cosine similarity
    sim_water = sum(a * b for a, b in zip(res_water1.vector, res_water2.vector))
    sim_cross = sum(a * b for a, b in zip(res_water1.vector, res_road.vector))

    assert len(res_water1.vector) == 64
    assert sim_water > sim_cross


def test_gemini_embedding_fallback_without_key():
    embedder = GeminiEmbeddingProvider(api_key=None)
    res = embedder.embed("road construction delayed")
    assert len(res.vector) == 64  # Fell back to TF-IDF 64-dim vector
    assert any("fallback" in note.lower() for note in res.uncertainty_notes)


def test_openai_embedding_fallback_without_key():
    embedder = OpenAIEmbeddingProvider(api_key=None)
    res = embedder.embed("road construction delayed")
    assert len(res.vector) == 64
    assert any("fallback" in note.lower() for note in res.uncertainty_notes)


# -------------------------------------------------------------
# 3. NLP Providers (Gemini / OpenAI)
# -------------------------------------------------------------
def test_gemini_nlp_unconfigured_falls_back_safely():
    nlp = GeminiNLPProvider(api_key=None)
    assert isinstance(nlp, (LanguageDetector, TextNormalizer, IssueClassifier, EntityExtractor))

    # Should transparently use rule-based fallback without throwing exceptions
    lang = nlp.detect("गाँव में शाम 5 बजे के बाद बस नहीं मिलती।")
    assert lang.language == "hi"

    cls = nlp.classify("गाँव में शाम 5 बजे के बाद बस नहीं मिलती।")
    assert cls.label == "transport"

    entities = nlp.extract("गाँव में शाम 5 बजे के बाद बस नहीं मिलती।")
    assert any(e.entity_type == "facility" for e in entities)


def test_gemini_nlp_with_mocked_api_response():
    nlp = GeminiNLPProvider(api_key="fake-key-for-test")
    mock_json = {
        "language": "mr",
        "language_confidence": 0.96,
        "normalized_text": "शाळेत शौचालय नाही, मुलांना खूप अडचण येते.",
        "issue_type": "education",
        "issue_confidence": 0.94,
        "entities": [
            {"entity_type": "facility", "value": "शाळा", "confidence": 0.95},
            {"entity_type": "facility", "value": "शौचालय", "confidence": 0.92},
            {"entity_type": "urgency", "value": "अडचण", "confidence": 0.88},
        ],
    }

    with patch.object(nlp, "_call_gemini", return_value=mock_json):
        lang = nlp.detect("sample text")
        assert lang.language == "mr"
        assert lang.confidence == 0.96

        norm = nlp.normalize("sample text")
        assert "शाळेत" in norm.normalized_text

        cls = nlp.classify("sample text")
        assert cls.label == "education"
        assert cls.confidence == 0.94

        ents = nlp.extract("sample text")
        assert len(ents) == 3
        assert ents[0].entity_type == "facility"


def test_openai_nlp_unconfigured_falls_back():
    nlp = OpenAINLPProvider(api_key=None)
    cls = nlp.classify("Water pipeline is broken and leaking everywhere")
    assert cls.label == "water"


# -------------------------------------------------------------
# 4. Speech-to-Text Providers
# -------------------------------------------------------------
def test_whisper_stt_requires_key():
    stt = WhisperSTTProvider(api_key=None, groq_api_key=None)
    dummy_b64 = base64.b64encode(b"RIFFdummydataWAVEfmt").decode("utf-8")
    with pytest.raises(NotImplementedError):
        stt.transcribe(dummy_b64)


def test_whisper_stt_mocked_groq():
    stt = WhisperSTTProvider(groq_api_key="gsk-fake-key")
    dummy_b64 = base64.b64encode(b"RIFFdummydataWAVEfmt").decode("utf-8")

    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "text": "गावात पाणी वेळेवर येत नाही",
            "language": "mr",
        }
        mock_client.post.return_value = mock_resp
        mock_client_cls.return_value.__enter__.return_value = mock_client

        res = stt.transcribe(dummy_b64, language_hint="mr")
        assert "पाणी" in res.text
        assert res.confidence == 0.92


def test_gemini_stt_unconfigured_graceful():
    stt = GeminiSTTProvider(api_key=None)
    dummy_b64 = base64.b64encode(b"RIFFdummydataWAVEfmt").decode("utf-8")
    res = stt.transcribe(dummy_b64)
    assert res.confidence == 0.0
    assert "not configured" in res.text


# -------------------------------------------------------------
# 5. Fallback Registry Resolution with Real Providers
# -------------------------------------------------------------
def test_registry_resolves_gemini(monkeypatch):
    monkeypatch.setenv("AI_LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEOCODING_PROVIDER", "nominatim")
    monkeypatch.setenv("AI_EMBEDDING_PROVIDER", "tfidf")
    monkeypatch.setenv("AI_STT_PROVIDER", "gemini")

    assert isinstance(get_language_detector(), GeminiNLPProvider)
    assert isinstance(get_text_normalizer(), GeminiNLPProvider)
    assert isinstance(get_issue_classifier(), GeminiNLPProvider)
    assert isinstance(get_geocoder(), NominatimGeocoder)
    assert isinstance(get_embedding_provider(), TfidfEmbeddingProvider)
    assert isinstance(get_stt_provider(), GeminiSTTProvider)


def test_registry_resolves_composite_and_openai(monkeypatch):
    monkeypatch.setenv("AI_LLM_PROVIDER", "openai")
    monkeypatch.setenv("GEOCODING_PROVIDER", "composite")

    assert isinstance(get_language_detector(), OpenAINLPProvider)
    assert isinstance(get_geocoder(), CompositeGeocoder)
