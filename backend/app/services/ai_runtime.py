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
from sqlalchemy.orm import Session


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

    # 1. Voice transcription (if audio provided)
    if audio_base64:
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
            detected_lang = (
                rb_lang.language if rb_lang.language != "unknown" else (language_hint or "en")
            )
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
                entities_list.append(
                    {"entity_type": e.entity_type, "value": e.value, "confidence": e.confidence}
                )
        else:
            rb_ner = RuleBasedEntityExtractor().extract(normalized)
            for e in rb_ner:
                entities_list.append(
                    {"entity_type": e.entity_type, "value": e.value, "confidence": e.confidence}
                )
    except Exception:
        rb_ner = RuleBasedEntityExtractor().extract(normalized)
        for e in rb_ner:
            entities_list.append(
                {"entity_type": e.entity_type, "value": e.value, "confidence": e.confidence}
            )

    # 6. Geocoding
    loc_resolved = False
    lat = None
    lon = None
    admin_hier = None
    target_loc_str = location_text or ""

    if not target_loc_str:
        # Check if an extracted entity contained a place
        places = [
            e["value"]
            for e in entities_list
            if e.get("entity_type") in ("place", "facility", "location")
        ]
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
                    uncertainty_notes.append(
                        f"Location '{target_loc_str}' unverified; queued for human geocoding."
                    )
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


def ingest_citizen_request(
    db: Session,
    channel: str,
    text: Optional[str] = None,
    audio_base64: Optional[str] = None,
    audio_url: Optional[str] = None,
    location_text: Optional[str] = None,
    language_hint: Optional[str] = None,
    consent_ack: bool = True,
    existing_request_id: Optional[int] = None,
):
    """Shared end-to-end ingestion pipeline:

    Processes input text/audio, extracts entities & location, assigns to clusters,
    and updates/creates the database entities with status='processed'.
    """
    from app.models import CitizenRequest
    from app.repositories import ClusterRepository, RequestRepository

    processed = process_citizen_request(
        channel=channel,
        text=text,
        language_hint=language_hint,
        audio_base64=audio_base64,
        location_text=location_text,
    )

    req_repo = RequestRepository(db)
    cluster_repo = ClusterRepository(db)

    # 1. Location persistence
    loc_id = None
    resolved_location_name = None
    if processed.location_resolved or location_text:
        admin = processed.admin_hierarchy or {}
        resolved_location_name = admin.get("village_ward") or admin.get("district") or location_text
        if not resolved_location_name and processed.entities:
            for ent in processed.entities:
                if ent.get("entity_type") in ("location", "place", "facility"):
                    resolved_location_name = ent.get("value")
                    break

        loc = req_repo.create_or_get_location(
            source_text=location_text or processed.raw_text,
            latitude=processed.latitude,
            longitude=processed.longitude,
            state=admin.get("state", "Demo State"),
            district=admin.get("district", "Demo District 1"),
            block=admin.get("block", "Demo Block A"),
            village_ward=resolved_location_name,
            confidence=0.85 if processed.location_resolved else 0.3,
            resolution_method="gazetteer_exact"
            if processed.location_resolved
            else "unresolved_text",
            status="resolved" if processed.location_resolved else "location_unresolved",
        )
        loc_id = loc.id

    # 2. Request creation or update
    if existing_request_id:
        req = db.query(CitizenRequest).filter(CitizenRequest.id == existing_request_id).first()
        if not req:
            req = req_repo.create_request(
                channel=channel,
                consent_ack=consent_ack,
                raw_text=text or processed.raw_text,
                audio_url=audio_url,
                language=processed.language,
                transcript=processed.transcript,
                status="processed",
                uncertainty_notes=processed.uncertainty_notes,
            )
        else:
            if not req.raw_text:
                req.raw_text = text or processed.raw_text
            if processed.transcript:
                req.transcript = processed.transcript
            if processed.language:
                req.language = processed.language
            if audio_url:
                req.audio_url = audio_url
            req.status = "processed"
            if processed.uncertainty_notes:
                notes = list(req.uncertainty_notes or [])
                for n in processed.uncertainty_notes:
                    if n not in notes:
                        notes.append(n)
                req.uncertainty_notes = notes
    else:
        req = req_repo.create_request(
            channel=channel,
            consent_ack=consent_ack,
            raw_text=text or processed.raw_text,
            audio_url=audio_url,
            language=processed.language,
            transcript=processed.transcript,
            status="processed",
            uncertainty_notes=processed.uncertainty_notes,
        )

    # 3. Save audio transcription record if available
    if processed.transcript:
        req_repo.add_transcription(
            request_id=req.id,
            transcript=processed.transcript,
            stt_model="whisper-base",
            stt_provider=processed.stt_provider or "whisper",
            confidence=processed.stt_confidence or 0.88,
        )

    # 4. Save entities
    if processed.entities:
        req_repo.add_entities(req.id, processed.entities)

    # 5. Cluster grouping
    matching_cluster = cluster_repo.find_matching_cluster(
        issue_type=processed.issue_type,
        location_id=loc_id,
        latitude=processed.latitude,
        longitude=processed.longitude,
    )
    if matching_cluster:
        cluster_repo.add_member(
            cluster_id=matching_cluster.id,
            request_id=req.id,
            similarity_score=0.88,
            assignment="auto",
        )
    else:
        new_cluster = cluster_repo.create_cluster(
            issue_type=processed.issue_type,
            location_id=loc_id,
            status="forming",
            independent_demand_count=1,
            raw_message_count=1,
            uncertainty_notes=processed.uncertainty_notes,
        )
        cluster_repo.add_member(
            cluster_id=new_cluster.id,
            request_id=req.id,
            similarity_score=1.0,
            assignment="auto",
        )

    db.commit()

    return req, processed, (resolved_location_name or location_text)
