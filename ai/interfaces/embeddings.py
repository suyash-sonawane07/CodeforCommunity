"""EmbeddingProvider — FR-019 (dedup similarity). Fallback: TF-IDF (PRD §11)."""

from typing import Protocol, runtime_checkable

from ai.interfaces.schemas import EmbeddingResult


@runtime_checkable
class EmbeddingProvider(Protocol):
    name: str

    def embed(self, text: str) -> EmbeddingResult: ...
