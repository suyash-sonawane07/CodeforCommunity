"""Embedding providers — Mock (default) and TF-IDF fallback skeleton (PRD §11).

TODO(PRD FR-019, Phase 2, Member C): real multilingual embeddings; TF-IDF is the
documented fallback if embedding service is unavailable.
"""

from __future__ import annotations

from ai.interfaces.schemas import EmbeddingResult


class MockEmbeddingProvider:
    name = "mock"

    def embed(self, text: str) -> EmbeddingResult:
        # Fixed-size zero vector: obviously fake, deterministic, no model needed.
        return EmbeddingResult(
            provider=self.name,
            confidence=0.0,
            vector=[0.0] * 8,
            uncertainty_notes=["Mock embeddings — not semantically meaningful"],
        )


class TfidfEmbeddingProvider:
    """Placeholder for the deterministic fallback (PRD §11)."""

    name = "tfidf"

    def embed(self, text: str) -> EmbeddingResult:
        raise NotImplementedError("TfidfEmbeddingProvider is a placeholder — implement in Phase 2")


class RuleBasedEmbeddingProvider:
    """Deterministic hashed term-vector embedding for semantic similarity and deduplication (FR-019)."""

    name = "rule_based"

    def __init__(self, dim: int = 32) -> None:
        self.dim = dim

    def embed(self, text: str) -> EmbeddingResult:
        import hashlib
        import math
        import re

        words = re.findall(r"\w+", text.lower())
        if not words:
            return EmbeddingResult(provider=self.name, confidence=0.0, vector=[0.0] * self.dim)

        vector = [0.0] * self.dim
        for word in words:
            idx = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % self.dim
            vector[idx] += 1.0

        # L2 normalize
        magnitude = math.sqrt(sum(x * x for x in vector))
        if magnitude > 0:
            vector = [round(x / magnitude, 4) for x in vector]

        return EmbeddingResult(
            provider=self.name,
            confidence=0.85,
            vector=vector,
            uncertainty_notes=[],
        )

