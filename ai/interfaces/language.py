"""LanguageDetector — FR-003/010. Deterministic-first rule (PRD §11)."""

from typing import Protocol, runtime_checkable

from ai.interfaces.schemas import LanguageDetectionResult


@runtime_checkable
class LanguageDetector(Protocol):
    name: str

    def detect(self, text: str) -> LanguageDetectionResult:
        """MVP set: {hi, mr, en}; anything else → 'unknown' (route to manual tag)."""
        ...
