"""TextNormalizer / IssueClassifier / EntityExtractor — FR-012, FR-014–017.

Original text is always preserved upstream (FR-004); normalisation output is
additional. Entity values must never translate proper nouns (FR-016).
"""

from typing import Protocol, runtime_checkable

from ai.interfaces.schemas import ClassificationResult, EntityResult, NormalizationResult


@runtime_checkable
class TextNormalizer(Protocol):
    name: str

    def normalize(self, text: str) -> NormalizationResult: ...


@runtime_checkable
class IssueClassifier(Protocol):
    name: str

    def classify(self, text: str) -> ClassificationResult:
        """Fixed taxonomy (FR-014): transport|water|health|education|roads|other."""
        ...


@runtime_checkable
class EntityExtractor(Protocol):
    name: str

    def extract(self, text: str) -> list[EntityResult]:
        """Place names, facility names, time expressions, urgency keywords (FR-015)."""
        ...
