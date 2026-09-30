"""STT providers — Mock (default, offline) and Whisper placeholder.

TODO(PRD FR-011, Phase 1 PoC, Member C): implement WhisperSTTProvider behind
the same interface; record measured confidence behaviour (PRD §21.6).
"""

from __future__ import annotations

import base64
import binascii

from ai.interfaces.schemas import TranscriptionResult


class MockSTTProvider:
    """Deterministic offline stand-in. Clearly labelled mock — never real output."""

    name = "mock"

    def transcribe(
        self, audio_base64: str, language_hint: str | None = None
    ) -> TranscriptionResult:
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
    """Whisper Speech-to-Text provider supporting Groq and OpenAI Whisper APIs (FR-002/007/011).

    Supports Hindi, Marathi, and English.
    Raises NotImplementedError if no API key or local model is configured.
    """

    name = "whisper"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        groq_api_key: str | None = None,
    ) -> None:
        import os

        self.openai_key = api_key or os.getenv("OPENAI_API_KEY")
        self.groq_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.model = model or ("whisper-large-v3-turbo" if self.groq_key else "whisper-1")

    def transcribe(
        self, audio_base64: str, language_hint: str | None = None
    ) -> TranscriptionResult:
        if not audio_base64:
            raise ValueError("audio_base64 is required (FR-006)")
        try:
            audio_bytes = base64.b64decode(audio_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("audio_base64 is not valid base64") from exc

        # Check for available keys
        if not self.openai_key and not self.groq_key:
            raise NotImplementedError(
                "WhisperSTTProvider requires OPENAI_API_KEY or GROQ_API_KEY "
                "to be configured (PRD §21.6)"
            )

        try:
            import httpx

            if self.groq_key:
                url = "https://api.groq.com/openai/v1/audio/transcriptions"
                headers = {"Authorization": f"Bearer {self.groq_key}"}
                model_name = self.model or "whisper-large-v3-turbo"
            else:
                url = "https://api.openai.com/v1/audio/transcriptions"
                headers = {"Authorization": f"Bearer {self.openai_key}"}
                model_name = "whisper-1"

            data = {"model": model_name}
            if language_hint and language_hint in ("hi", "mr", "en"):
                data["language"] = language_hint

            files = {"file": ("audio.wav", audio_bytes, "audio/wav")}

            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, headers=headers, data=data, files=files)
                if resp.status_code == 200:
                    res_json = resp.json()
                    transcript_text = res_json.get("text", "").strip()
                    return TranscriptionResult(
                        provider=f"{self.name}:{model_name}",
                        confidence=0.92,
                        text=transcript_text,
                        language=language_hint or res_json.get("language"),
                        uncertainty_notes=[],
                    )
                else:
                    return TranscriptionResult(
                        provider=self.name,
                        confidence=0.2,
                        text="[Speech transcription service returned an error]",
                        language=language_hint,
                        uncertainty_notes=[
                            f"Whisper API returned status {resp.status_code}: {resp.text}"
                        ],
                    )
        except Exception as exc:
            return TranscriptionResult(
                provider=self.name,
                confidence=0.0,
                text="[Audio transcription failed due to network error]",
                language=language_hint,
                uncertainty_notes=[f"Transcription request exception: {exc}"],
            )


class GeminiSTTProvider:
    """Multimodal audio transcription provider using Google Gemini 1.5 Flash.

    Accepts audio base64 directly and returns transcription in original Indian language.
    """

    name = "gemini"
    ENDPOINT = (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    )

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        import os

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def transcribe(
        self, audio_base64: str, language_hint: str | None = None
    ) -> TranscriptionResult:
        if not audio_base64:
            raise ValueError("audio_base64 is required (FR-006)")
        try:
            base64.b64decode(audio_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("audio_base64 is not valid base64") from exc

        if not self.api_key:
            return TranscriptionResult(
                provider=self.name,
                confidence=0.0,
                text="[Gemini STT: GEMINI_API_KEY not configured]",
                language=language_hint,
                uncertainty_notes=["GEMINI_API_KEY missing in environment"],
            )

        try:
            import httpx

            lang_context = (
                f"The speaker is likely speaking {language_hint}."
                if language_hint
                else "The speaker may be speaking Hindi, Marathi, or English."
            )
            prompt = (
                f"Transcribe the following citizen voice recording accurately. {lang_context} "
                "Transcribe in the exact original language and script "
                "(Devanagari for Hindi/Marathi, Latin for English). "
                "Return ONLY the transcription without quotes, explanations, or introductory text."
            )
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": "audio/mp3", "data": audio_base64}},
                        ]
                    }
                ],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1000},
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 404 and self.model != "gemini-3.8-flash":
                    fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={self.api_key}"
                    resp = client.post(fallback_url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            text = parts[0].get("text", "").strip()
                            return TranscriptionResult(
                                provider=self.name,
                                confidence=0.94,
                                text=text,
                                language=language_hint,
                                uncertainty_notes=[],
                            )
                return TranscriptionResult(
                    provider=self.name,
                    confidence=0.2,
                    text="[Gemini audio transcription returned an error]",
                    language=language_hint,
                    uncertainty_notes=[
                        f"Gemini API returned status {resp.status_code}: {resp.text}"
                    ],
                )
        except Exception as exc:
            return TranscriptionResult(
                provider=self.name,
                confidence=0.0,
                text="[Gemini audio transcription failed due to network error]",
                language=language_hint,
                uncertainty_notes=[f"Gemini STT request exception: {exc}"],
            )


class GroqWhisperSTTProvider(WhisperSTTProvider):
    """Specialized Groq Whisper provider (sub-second latency, excellent Indian accent support)."""

    name = "groq"

    def __init__(self, model: str = "whisper-large-v3-turbo") -> None:
        import os

        groq_key = os.getenv("GROQ_API_KEY")
        super().__init__(model=model, groq_api_key=groq_key)
