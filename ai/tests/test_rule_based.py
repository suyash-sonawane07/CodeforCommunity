"""Tests for multilingual rule-based NLP, geocoding and embeddings."""

from ai.embeddings import RuleBasedEmbeddingProvider
from ai.geocoding import GazetteerGeocoder
from ai.nlp import (
    RuleBasedEntityExtractor,
    RuleBasedIssueClassifier,
    RuleBasedLanguageDetector,
)


def test_language_detection_hindi():
    detector = RuleBasedLanguageDetector()
    res = detector.detect("गाँव में शाम 5 बजे के बाद बस नहीं मिलती।")
    assert res.language == "hi"
    assert res.confidence > 0.7


def test_language_detection_marathi():
    detector = RuleBasedLanguageDetector()
    res = detector.detect("शाळेत शौचालय नाही, मुलांना अडचण येते.")
    assert res.language == "mr"
    assert res.confidence > 0.7


def test_language_detection_english():
    detector = RuleBasedLanguageDetector()
    res = detector.detect("Water supply comes only two hours a week.")
    assert res.language == "en"
    assert res.confidence > 0.8


def test_issue_classifier():
    classifier = RuleBasedIssueClassifier()
    assert classifier.classify("गाँव में शाम 5 बजे के बाद बस नहीं मिलती।").label == "transport"
    assert classifier.classify("शाळेत शौचालय नाही, मुलांना अडचण येते.").label == "education"
    assert classifier.classify("Water supply comes only two hours a week.").label == "water"
    assert classifier.classify("The road near the old temple is broken.").label == "roads"
    assert classifier.classify("General random text with no keywords").label == "other"


def test_entity_extractor():
    extractor = RuleBasedEntityExtractor()
    entities = extractor.extract("गाँव में शाम 5 बजे के बाद बस नहीं मिलती।")
    facility_types = [e.value for e in entities if e.entity_type == "facility"]
    assert "bus_stop" in facility_types
    time_types = [e.entity_type for e in entities if e.entity_type == "time"]
    assert "time" in time_types


def test_gazetteer_geocoder():
    geocoder = GazetteerGeocoder()
    res1 = geocoder.geocode("Demo Village 1, Demo Block A")
    assert res1.resolved is True
    assert res1.latitude == 19.876
    assert res1.longitude == 75.343
    assert res1.admin_hierarchy["district"] == "Demo District 1"

    # Hindi script
    res2 = geocoder.geocode("डेमो गाँव 1, डेमो ब्लॉक A")
    assert res2.resolved is True
    assert res2.latitude == 19.876

    # Unknown
    res3 = geocoder.geocode("Unknown village somewhere far away")
    assert res3.resolved is False
    assert res3.latitude is None


def test_rule_based_embeddings_similarity():
    embedder = RuleBasedEmbeddingProvider()
    e1 = embedder.embed("no regular bus after 5pm")
    e2 = embedder.embed("bus not available in evening")
    e3 = embedder.embed("drinking water pipeline broken")

    # Cosine similarity between e1 and e2 should be positive
    sim_1_2 = sum(a * b for a, b in zip(e1.vector, e2.vector))
    sim_1_3 = sum(a * b for a, b in zip(e1.vector, e3.vector))

    assert len(e1.vector) == 32
    assert sim_1_2 > sim_1_3
