"""Embedding providers — Mock (default) and TF-IDF fallback skeleton (PRD §11).

TODO(PRD FR-019, Phase 2, Member C): real multilingual embeddings; TF-IDF is the
documented fallback if embedding service is unavailable.
"""

from __future__ import annotations

from ai.interfaces.embeddings import EmbeddingProvider
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
    """Multilingual TF-IDF embedding provider with character n-grams and domain vocabulary (FR-019).

    Deterministic, offline, and language-agnostic across Hindi, Marathi, and English.
    Produces unit-normalized dense vectors suitable for cosine similarity.
    """

    name = "tfidf"

    # Fixed semantic topic clusters mapped to designated subspace coordinates
    TOPIC_CLUSTERS = {
        0: [  # Water
            "water",
            "drinking",
            "pani",
            "paani",
            "jal",
            "nal",
            "nall",
            "tanker",
            "pipe",
            "pipeline",
            "borewell",
            "leakage",
            "leak",
            "clean water",
            "पाणी",
            "पानी",
            "जल",
            "नळ",
            "नल",
            "टाकी",
            "टँकर",
            "विहीर",
        ],
        1: [  # Roads
            "road",
            "roads",
            "pothole",
            "potholes",
            "asphalt",
            "highway",
            "bridge",
            "street",
            "pavement",
            "broken road",
            "tar",
            "khadde",
            "khadda",
            "सड़क",
            "रस्ता",
            "मार्ग",
            "पूल",
            "खड्डे",
            "खड्डा",
            "डांबरीकरण",
        ],
        2: [  # Transport
            "bus",
            "buses",
            "transport",
            "transit",
            "depot",
            "route",
            "stop",
            "bus stop",
            "station",
            "rickshaw",
            "vehicle",
            "commute",
            "बस",
            "वाहतूक",
            "गाडी",
            "सवारी",
            "बसें",
            "स्थानक",
            "स्टँड",
        ],
        3: [  # Education
            "school",
            "college",
            "shala",
            "education",
            "teacher",
            "student",
            "classroom",
            "toilet",
            "washroom",
            "study",
            "books",
            "शाळा",
            "शाळेत",
            "स्कूल",
            "शिक्षक",
            "वर्ग",
            "विद्यार्थी",
            "शौचालय",
        ],
        4: [  # Health
            "hospital",
            "clinic",
            "doctor",
            "health",
            "phc",
            "dispensary",
            "medicine",
            "nurse",
            "medical",
            "patient",
            "treatment",
            "दवाखाना",
            "रुग्णालय",
            "आरोग्य",
            "डॉक्टर",
            "औषध",
            "उपचार",
        ],
    }

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    def embed(self, text: str) -> EmbeddingResult:
        import hashlib
        import math
        import re

        cleaned = text.lower().strip()
        if not cleaned:
            return EmbeddingResult(provider=self.name, confidence=0.0, vector=[0.0] * self.dim)

        words = re.findall(r"\w+", cleaned)
        char_3grams = [cleaned[i : i + 3] for i in range(max(0, len(cleaned) - 2))]

        vector = [0.0] * self.dim

        # 1. Topic subspace encoding (dedicated 8-dim subspace per topic: 0..39)
        for topic_idx, keywords in self.TOPIC_CLUSTERS.items():
            subspace_start = topic_idx * 8
            topic_matched = False
            for kw in keywords:
                if kw in cleaned:
                    topic_matched = True
                    offset = 1 + (int(hashlib.md5(kw.encode("utf-8")).hexdigest(), 16) % 7)
                    vector[subspace_start + offset] += 2.0
            if topic_matched:
                # Primary anchor coordinate for this topic
                vector[subspace_start] += 6.0

        # 2. General vocabulary & word tokens across remaining space (40..63)
        general_dim = max(1, self.dim - 40)
        for w in words:
            idx = 40 + (int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16) % general_dim)
            vector[idx] += 1.0

        # 3. Char 3-grams for subword similarity across remaining space
        for g in char_3grams:
            idx = 40 + (int(hashlib.md5(g.encode("utf-8")).hexdigest(), 16) % general_dim)
            vector[idx] += 0.3

        # L2 normalize
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 0:
            norm_vector = [round(v / magnitude, 4) for v in vector]
        else:
            norm_vector = [0.0] * self.dim

        return EmbeddingResult(
            provider=self.name,
            confidence=0.90,
            vector=norm_vector,
            uncertainty_notes=[],
        )


class GeminiEmbeddingProvider:
    """Google Gemini embedding provider using text-embedding-004."""

    name = "gemini"
    ENDPOINT = (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
    )

    def __init__(
        self, api_key: str | None = None, fallback: EmbeddingProvider | None = None
    ) -> None:
        import os

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.fallback = fallback or TfidfEmbeddingProvider()

    def embed(self, text: str) -> EmbeddingResult:
        if not self.api_key:
            res = self.fallback.embed(text)
            res.uncertainty_notes.append("Gemini API key not configured; used TF-IDF fallback")
            return res

        try:
            import httpx

            url = f"{self.ENDPOINT}?key={self.api_key}"
            payload = {
                "model": "models/gemini-embedding-001",
                "content": {"parts": [{"text": text[:2000]}]},
            }
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    values = data.get("embedding", {}).get("values", [])
                    if values:
                        return EmbeddingResult(
                            provider=self.name,
                            confidence=0.96,
                            vector=values,
                            uncertainty_notes=[],
                        )
        except Exception as exc:
            res = self.fallback.embed(text)
            res.uncertainty_notes.append(
                f"Gemini embedding API call failed: {exc}; used TF-IDF fallback"
            )
            return res

        res = self.fallback.embed(text)
        res.uncertainty_notes.append(
            "Gemini embedding returned non-200 response; used TF-IDF fallback"
        )
        return res


class OpenAIEmbeddingProvider:
    """OpenAI embedding provider using text-embedding-3-small."""

    name = "openai"
    ENDPOINT = "https://api.openai.com/v1/embeddings"

    def __init__(
        self, api_key: str | None = None, fallback: EmbeddingProvider | None = None
    ) -> None:
        import os

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.fallback = fallback or TfidfEmbeddingProvider()

    def embed(self, text: str) -> EmbeddingResult:
        if not self.api_key:
            res = self.fallback.embed(text)
            res.uncertainty_notes.append("OpenAI API key not configured; used TF-IDF fallback")
            return res

        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "text-embedding-3-small",
                "input": text[:2000],
            }
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(self.ENDPOINT, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("data", [])
                    if items and "embedding" in items[0]:
                        return EmbeddingResult(
                            provider=self.name,
                            confidence=0.96,
                            vector=items[0]["embedding"],
                            uncertainty_notes=[],
                        )
        except Exception as exc:
            res = self.fallback.embed(text)
            res.uncertainty_notes.append(
                f"OpenAI embedding API call failed: {exc}; used TF-IDF fallback"
            )
            return res

        res = self.fallback.embed(text)
        res.uncertainty_notes.append(
            "OpenAI embedding returned non-200 response; used TF-IDF fallback"
        )
        return res


class RuleBasedEmbeddingProvider:
    """Hashed term-vector embedding for semantic similarity and deduplication (FR-019)."""

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
