"""AI Runtime Service — wires AI interfaces and fallback providers for the intake pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ai.embeddings import RuleBasedEmbeddingProvider
from ai.fallback import (
    get_embedding_provider,
    get_entity_extractor,
    get_geocoder,
    get_issue_classifier,
    get_language_detector,
    get_stt_provider,
    get_text_normalizer,
)
from ai.geocoding import GazetteerGeocoder
from ai.nlp import (
    RuleBasedEntityExtractor,
    RuleBasedIssueClassifier,
    RuleBasedLanguageDetector,
    RuleBasedTextNormalizer,
)


@dataclass
class ProcessedIntake:
    raw_text: str
    channel: str
    language: str
    normalized_text: str
    issue_type: str
    entities: list[dict] = field(default_factory=list)
    location_resolved: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    admin_hierarchy: Optional[dict] = None
    embedding: list[float] = field(default_factory=list)
    transcript: Optional[str] = None
    stt_provider: Optional[str] = None
    stt_confidence: Optional[float] = None
    uncertainty_notes: list[str] = field(default_factory=list)


def process_citizen_request(
    channel: str,
    text: Optional[str] = None,
    language_hint: Optional[str] = None,
    audio_base64: Optional[str] = None,
    location_text: Optional[str] = None,
) -> ProcessedIntake:
    """End-to-end ingestion pipeline: STT -> LangDetect -> Normalization -> Classification -> NER -> Geocoding -> Embeddings."""
    uncertainty_notes: list[str] = []
    effective_text = (text or "").strip()
    transcript = None
    stt_provider_name = None
    stt_conf = None

    # 1. Voice transcription (if voice channel)
    if channel == "voice" and audio_base64:
        try:
            stt = get_stt_provider()
            stt_res = stt.transcribe(audio_base64, language_hint=language_hint)
            transcript = stt_res.text
            stt_provider_name = stt_res.provider
            stt_conf = stt_res.confidence
            if not effective_text:
                effective_text = transcript
            if stt_res.uncertainty_notes:
                uncertainty_notes.extend(stt_res.uncertainty_notes)
        except Exception as exc:
            uncertainty_notes.append(f"STT transcription failed: {exc}")
            effective_text = effective_text or "[Unintelligible audio submission]"

    # 2. Language detection
    detected_lang = language_hint
    try:
        lang_detector = get_language_detector()
        lang_res = lang_detector.detect(effective_text)
        if lang_res.language != "unknown":
            detected_lang = lang_res.language
        else:
            # Try rule-based fallback
            rb_lang = RuleBasedLanguageDetector().detect(effective_text)
            detected_lang = rb_lang.language if rb_lang.language != "unknown" else (language_hint or "en")
    except Exception:
        detected_lang = language_hint or "en"

    # 3. Text Normalization
    try:
        normalizer = get_text_normalizer()
        norm_res = normalizer.normalize(effective_text)
        normalized = norm_res.normalized_text or effective_text
    except Exception:
        normalized = RuleBasedTextNormalizer().normalize(effective_text).normalized_text

    # 4. Issue Classification
    issue_type = "other"
    try:
        classifier = get_issue_classifier()
        cls_res = classifier.classify(normalized)
        if cls_res.label != "other":
            issue_type = cls_res.label
        else:
            # Rule-based fallback
            rb_cls = RuleBasedIssueClassifier().classify(normalized)
            issue_type = rb_cls.label
    except Exception:
        issue_type = RuleBasedIssueClassifier().classify(normalized).label

    # 5. Entity Extraction
    entities_list: list[dict] = []
    try:
        extractor = get_entity_extractor()
        ner_res = extractor.extract(normalized)
        if ner_res:
            for e in ner_res:
                entities_list.append({"entity_type": e.entity_type, "value": e.value, "confidence": e.confidence})
        else:
            rb_ner = RuleBasedEntityExtractor().extract(normalized)
            for e in rb_ner:
                entities_list.append({"entity_type": e.entity_type, "value": e.value, "confidence": e.confidence})
    except Exception:
        rb_ner = RuleBasedEntityExtractor().extract(normalized)
        for e in rb_ner:
            entities_list.append({"entity_type": e.entity_type, "value": e.value, "confidence": e.confidence})

    # 6. Geocoding
    loc_resolved = False
    lat = None
    lon = None
    admin_hier = None
    target_loc_str = location_text or ""

    if not target_loc_str:
        # Check if an extracted entity contained a place
        places = [e["value"] for e in entities_list if e.get("entity_type") in ("place", "facility")]
        if places:
            target_loc_str = places[0]

    if target_loc_str:
        try:
            geocoder = get_geocoder()
            geo_res = geocoder.geocode(target_loc_str)
            if geo_res.resolved:
                loc_resolved = True
                lat = geo_res.latitude
                lon = geo_res.longitude
                admin_hier = geo_res.admin_hierarchy
            else:
                rb_geo = GazetteerGeocoder().geocode(target_loc_str)
                if rb_geo.resolved:
                    loc_resolved = True
                    lat = rb_geo.latitude
                    lon = rb_geo.longitude
                    admin_hier = rb_geo.admin_hierarchy
                else:
                    uncertainty_notes.append(f"Location '{target_loc_str}' unverified; queued for human geocoding.")
        except Exception:
            rb_geo = GazetteerGeocoder().geocode(target_loc_str)
            if rb_geo.resolved:
                loc_resolved = True
                lat = rb_geo.latitude
                lon = rb_geo.longitude
                admin_hier = rb_geo.admin_hierarchy

    # 7. Embedding
    embedding_vec: list[float] = []
    try:
        embedder = get_embedding_provider()
        emb_res = embedder.embed(normalized)
        if any(emb_res.vector):
            embedding_vec = emb_res.vector
        else:
            embedding_vec = RuleBasedEmbeddingProvider().embed(normalized).vector
    except Exception:
        embedding_vec = RuleBasedEmbeddingProvider().embed(normalized).vector

    return ProcessedIntake(
        raw_text=effective_text,
        channel=channel,
        language=detected_lang,
        normalized_text=normalized,
        issue_type=issue_type,
        entities=entities_list,
        location_resolved=loc_resolved,
        latitude=lat,
        longitude=lon,
        admin_hierarchy=admin_hier,
        embedding=embedding_vec,
        transcript=transcript,
        stt_provider=stt_provider_name,
        stt_confidence=stt_conf,
        uncertainty_notes=uncertainty_notes,
    )
