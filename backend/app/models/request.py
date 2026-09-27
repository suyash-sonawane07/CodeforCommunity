"""Citizen intake entities: `citizen_requests`, `request_transcriptions`,
`extracted_entities` (PRD §9.1).

Scaffold invariants (PRD FR-004, FR-017, §25):
- `raw_text` / `audio_url` originals are immutable once written.
- Every AI-derived field carries `confidence`.
"""

from typing import List, Optional

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models._mixins import TimestampMixin


class CitizenRequest(Base, TimestampMixin):
    __tablename__ = "citizen_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    channel: Mapped[str] = mapped_column(String(10))  # text | voice
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # immutable (FR-004)
    audio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # hi|mr|en|unknown
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    consent_ack: Mapped[bool] = mapped_column(default=False)  # FR-005: no store without it
    status: Mapped[str] = mapped_column(String(30), default="received")
    review_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # FR-063
    uncertainty_notes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # §25
    source: Mapped[str] = mapped_column(String(30), default="web")  # §25 provenance

    transcriptions: Mapped[List["RequestTranscription"]] = relationship(
        "RequestTranscription", back_populates="request"
    )
    entities: Mapped[List["ExtractedEntity"]] = relationship(
        "ExtractedEntity", back_populates="request"
    )


class RequestTranscription(Base, TimestampMixin):
    __tablename__ = "request_transcriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("citizen_requests.id"), index=True)
    stt_model: Mapped[str] = mapped_column(String(100))
    stt_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # FR-017
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    request: Mapped["CitizenRequest"] = relationship(
        "CitizenRequest", back_populates="transcriptions"
    )


class ExtractedEntity(Base, TimestampMixin):
    __tablename__ = "extracted_entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("citizen_requests.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(50))  # place|facility|time|urgency|...
    value: Mapped[str] = mapped_column(Text)  # never translated proper nouns (FR-016)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="ai")  # ai | human_correction
    extraction_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    request: Mapped["CitizenRequest"] = relationship("CitizenRequest", back_populates="entities")
