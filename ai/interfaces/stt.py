"""SpeechToTextProvider — FR-002/007/011. Implementations: stt/."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai.interfaces.schemas import TranscriptionResult


@runtime_checkable
class SpeechToTextProvider(Protocol):
    name: str

    def transcribe(
        self, audio_base64: str, language_hint: str | None = None
    ) -> TranscriptionResult:
        """Transcribe audio (≤60s, FR-002). Low confidence ⇒ caller flags
        needs_manual_review (FR-007) — providers never drop input."""
        ...
