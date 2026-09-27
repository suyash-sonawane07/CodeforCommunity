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
