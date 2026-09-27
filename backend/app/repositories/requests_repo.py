"""Repository for citizen requests, transcriptions, entities, and locations."""

from __future__ import annotations

import uuid
from typing import Optional

from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session

from app.models import CitizenRequest, ExtractedEntity, Location, RequestTranscription


class RequestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def generate_reference_code(self) -> str:
        unique = uuid.uuid4().hex[:6].upper()
        return f"CP-2026-{unique}"

    def create_request(
        self,
        channel: str,
        consent_ack: bool,
        raw_text: Optional[str] = None,
        audio_url: Optional[str] = None,
        language: Optional[str] = None,
        transcript: Optional[str] = None,
        status: str = "received",
        uncertainty_notes: Optional[list] = None,
    ) -> CitizenRequest:
        ref_code = self.generate_reference_code()
        req = CitizenRequest(
            reference_code=ref_code,
            channel=channel,
            consent_ack=consent_ack,
            raw_text=raw_text,
            audio_url=audio_url,
            language=language,
            transcript=transcript,
            status=status,
            uncertainty_notes=uncertainty_notes or [],
            source="web",
        )
        self.db.add(req)
        self.db.flush()
        return req

    def get_by_id_or_reference(self, identifier: str) -> Optional[CitizenRequest]:
        # Try reference_code first
        req = (
            self.db.query(CitizenRequest)
            .filter(CitizenRequest.reference_code == identifier)
            .first()
        )
        if req:
            return req

        # Try int ID or string ID (e.g. req_123 or 123)
        clean_id = identifier.replace("req_", "")
        if clean_id.isdigit():
            return (
                self.db.query(CitizenRequest)
                .filter(CitizenRequest.id == int(clean_id))
                .first()
            )
        return None

    def add_transcription(
        self,
        request_id: int,
        transcript: str,
        stt_model: str = "whisper-base",
        stt_provider: str = "mock",
        confidence: Optional[float] = None,
    ) -> RequestTranscription:
        transcription = RequestTranscription(
            request_id=request_id,
            stt_model=stt_model,
            stt_provider=stt_provider,
            confidence=confidence,
            transcript=transcript,
        )
        self.db.add(transcription)
        self.db.flush()
        return transcription

    def add_entities(
        self, request_id: int, entities: list[dict]
    ) -> list[ExtractedEntity]:
        created = []
        for ent in entities:
            rec = ExtractedEntity(
                request_id=request_id,
                entity_type=ent.get("entity_type", "place"),
                value=ent.get("value", ""),
                confidence=ent.get("confidence", 0.8),
                source="ai",
            )
            self.db.add(rec)
            created.append(rec)
        self.db.flush()
        return created

    def create_or_get_location(
        self,
        source_text: Optional[str],
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        state: Optional[str] = None,
        district: Optional[str] = None,
        block: Optional[str] = None,
        village_ward: Optional[str] = None,
        confidence: Optional[float] = None,
        resolution_method: str = "gazetteer_exact",
        status: str = "resolved",
        uncertainty_notes: Optional[str] = None,
    ) -> Location:
        geom = None
        if latitude is not None and longitude is not None:
            geom = WKTElement(f"POINT({longitude} {latitude})", srid=4326)

        loc = Location(
            source_text=source_text,
            latitude=latitude,
            longitude=longitude,
            geom=geom,
            state=state,
            district=district,
            block=block,
            village_ward=village_ward,
            confidence=confidence,
            resolution_method=resolution_method,
            status=status,
            uncertainty_notes=uncertainty_notes,
        )
        self.db.add(loc)
        self.db.flush()
        return loc
