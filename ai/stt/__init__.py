"""STT providers — Mock (default, offline) and Whisper placeholder.

TODO(PRD FR-011, Phase 1 PoC, Member C): implement WhisperSTTProvider behind
the same interface; record measured confidence behaviour (PRD §21.6).
"""

from __future__ import annotations

import base64
import binascii
from typing import Optional

from ai.interfaces.schemas import TranscriptionResult


class MockSTTProvider:
    """Deterministic offline stand-in. Clearly labelled mock — never real output."""

    name = "mock"

    def transcribe(self, audio_base64: str, language_hint: Optional[str] = None) -> TranscriptionResult:
        if not audio_base64:
            raise ValueError("audio_base64 is required (FR-006)")
        try:
            base64.b64decode(audio_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("audio_base64 is not valid base64") from exc
        return TranscriptionResult(
            provider=self.name,
            confidence=0.0,
            text="[MOCK TRANSCRIPTION — placeholder scaffold output]",
            language=language_hint,
            uncertainty_notes=["Mock STT provider — not real transcription"],
        )


class WhisperSTTProvider:
    """Placeholder for the Phase 1 PoC (self-hosted or free-tier API, PRD §11)."""

    name = "whisper"

    def __init__(self, model: str = "base") -> None:
        self.model = model

    def transcribe(self, audio_base64: str, language_hint: Optional[str] = None) -> TranscriptionResult:
        raise NotImplementedError(
            "WhisperSTTProvider is a placeholder — implement in Phase 1 (PRD §21.6)"
        )
