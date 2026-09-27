"""Shared AI result schemas (FR-017 confidence discipline, §25 provenance)."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AIResult:
    """Base for all AI outputs: provenance + confidence are mandatory (FR-017)."""

    provider: str = "mock"
    confidence: Optional[float] = None
    uncertainty_notes: list[str] = field(default_factory=list)


@dataclass
class TranscriptionResult(AIResult):
    text: str = ""
    language: Optional[str] = None  # ISO-639-1 hint from the model


@dataclass
class LanguageDetectionResult(AIResult):
    language: str = "unknown"  # hi|mr|en|unknown


@dataclass
class NormalizationResult(AIResult):
    normalized_text: str = ""


@dataclass
class ClassificationResult(AIResult):
    """FR-014 taxonomy is fixed: transport, water, health, education, roads, other."""

    label: str = "other"
    taxonomy: tuple = ("transport", "water", "health", "education", "roads", "other")


@dataclass
class EntityResult(AIResult):
    entity_type: str = "place"  # place|facility|time|urgency
    value: str = ""


@dataclass
class EmbeddingResult(AIResult):
    vector: list[float] = field(default_factory=list)


@dataclass
class GeocodeResult(AIResult):
    """FR-021/033: `resolved=False` means NO coordinates are provided, ever."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    admin_hierarchy: Optional[dict] = None
    resolved: bool = False
