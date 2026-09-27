"""NLP providers — deterministic mocks (default). Real LLM/NER providers TBD (PRD §11).

TODO(PRD FR-012–018, Phase 2, Member C): replace mocks with the chosen
LLM/NER approach behind the same interfaces; keep rule-based fallbacks.
"""

from __future__ import annotations

from typing import Optional

from ai.interfaces.schemas import (
    ClassificationResult,
    EntityResult,
    LanguageDetectionResult,
    NormalizationResult,
)

TAXONOMY = ("transport", "water", "health", "education", "roads", "other")


class MockLanguageDetector:
    name = "mock"

    def detect(self, text: str) -> LanguageDetectionResult:
        """Real language detection lands in Phase 1 (FR-010); mock returns 'unknown'."""
        return LanguageDetectionResult(
            provider=self.name,
            confidence=None,
            language="unknown",
            uncertainty_notes=["Mock language detector — not real detection"],
        )


class MockTextNormalizer:
    name = "mock"

    def normalize(self, text: str) -> NormalizationResult:
        # FR-004: normalisation never replaces the original — output is additive only.
        return NormalizationResult(
            provider=self.name,
            confidence=0.0,
            normalized_text=text.strip(),
            uncertainty_notes=["Mock normalizer — passthrough only"],
        )


class MockIssueClassifier:
    name = "mock"

    def classify(self, text: str) -> ClassificationResult:
        return ClassificationResult(
            provider=self.name,
            confidence=0.0,
            label="other",
            uncertainty_notes=["Mock classifier — always 'other', not real"],
        )


class MockEntityExtractor:
    name = "mock"

    def extract(self, text: str) -> list[EntityResult]:
        return []  # TODO(PRD FR-015): real extraction in Phase 2
