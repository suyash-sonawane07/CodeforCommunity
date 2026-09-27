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


class RuleBasedLanguageDetector:
    """Multilingual detector supporting Hindi, Marathi and English (FR-010)."""

    name = "rule_based"

    def detect(self, text: str) -> LanguageDetectionResult:
        if not text or not text.strip():
            return LanguageDetectionResult(provider=self.name, confidence=0.0, language="unknown")
        
        has_devanagari = any("\u0900" <= ch <= "\u097f" for ch in text)
        if has_devanagari:
            mr_markers = {"आहे", "नाही", "गावात", "शाळा", "शाळेत", "रस्ता", "पाणी", "मुलांना", "अडचण", "शौचालय", "येते", "होते", "केले", "करावे", "नळ", "स्थानक", "वाजेनंतर"}
            hi_markers = {"है", "में", "गाँव", "गांव", "नहीं", "सड़क", "पानी", "मिलती", "होता", "किए", "करना", "नल", "स्कूल", "शाम", "बजे"}
            
            words = set(text.replace("।", " ").replace(".", " ").replace(",", " ").split())
            mr_count = len(words.intersection(mr_markers))
            hi_count = len(words.intersection(hi_markers))
            
            if mr_count > hi_count:
                return LanguageDetectionResult(provider=self.name, confidence=0.88, language="mr")
            if hi_count > mr_count:
                return LanguageDetectionResult(provider=self.name, confidence=0.88, language="hi")
            return LanguageDetectionResult(provider=self.name, confidence=0.75, language="hi")
        
        has_latin = any("a" <= ch.lower() <= "z" for ch in text)
        if has_latin:
            return LanguageDetectionResult(provider=self.name, confidence=0.92, language="en")
            
        return LanguageDetectionResult(provider=self.name, confidence=0.3, language="unknown")


class RuleBasedTextNormalizer:
    name = "rule_based"

    def normalize(self, text: str) -> NormalizationResult:
        normalized = " ".join(text.strip().split())
        return NormalizationResult(
            provider=self.name,
            confidence=0.95,
            normalized_text=normalized,
        )


class RuleBasedIssueClassifier:
    """Multilingual keyword and taxonomy classifier (FR-014)."""

    name = "rule_based"

    def classify(self, text: str) -> ClassificationResult:
        lower = text.lower()
        
        # Priority keyword checks
        keywords = {
            "transport": [
                "bus", "transport", "travel", "rickshaw", "vehicle", "transit", "route",
                "बस", "वाहतूक", "गाडी", "सवारी", "बसें", "स्थानक", "स्टँड"
            ],
            "roads": [
                "road", "pothole", "highway", "bridge", "pavement", "street", "broken road",
                "सड़क", "रस्ता", "मार्ग", "पूल", "खड्डे", "खड्डा", "डांबरीकरण"
            ],
            "water": [
                "water", "drinking", "pipeline", "tap", "borewell", "tanker", "leakage",
                "पाणी", "पानी", "जल", "नळ", "नल", "टाकी", "टँकर", "विहीर"
            ],
            "education": [
                "school", "college", "teacher", "classroom", "toilet", "student", "education",
                "शाळा", "शाळेत", "स्कूल", "शिक्षक", "शिक्षिका", "वर्ग", "विद्यार्थी", "शौचालय"
            ],
            "health": [
                "hospital", "clinic", "dispensary", "doctor", "health", "medicine", "phc", "nurse",
                "दवाखाना", "रुग्णालय", "आरोग्य", "डॉक्टर", "औषध", "उपचार"
            ],
        }

        # Check for education/sanitation compound
        if any(w in lower for w in ["toilet", "शौचालय"]) and any(w in lower for w in ["school", "शाळा", "शाळेत", "स्कूल"]):
            return ClassificationResult(provider=self.name, confidence=0.92, label="education")

        for sector, kws in keywords.items():
            if any(kw in lower for kw in kws):
                return ClassificationResult(provider=self.name, confidence=0.88, label=sector)

        return ClassificationResult(
            provider=self.name,
            confidence=0.40,
            label="other",
            uncertainty_notes=["No distinct sector keyword matched; defaulting to other"],
        )


class RuleBasedEntityExtractor:
    """Extracts village, facility, time and urgency entities (FR-015/016)."""

    name = "rule_based"

    def extract(self, text: str) -> list[EntityResult]:
        entities: list[EntityResult] = []
        lower = text.lower()

        # Facilities
        facility_patterns = [
            ("school", ["school", "शाळा", "स्कूल"]),
            ("bus_stop", ["bus stop", "bus stand", "बस स्टँड", "बस स्थानक", "बस"]),
            ("toilet", ["toilet", "शौचालय"]),
            ("water_point", ["water supply", "pipe", "पाणी", "पानी", "नल", "नळ", "टाकी"]),
            ("clinic", ["hospital", "clinic", "dispensary", "दवाखाना", "रुग्णालय"]),
            ("temple", ["temple", "मंदिर"]),
        ]
        for fac_name, kws in facility_patterns:
            if any(kw in lower for kw in kws):
                entities.append(EntityResult(provider=self.name, confidence=0.85, entity_type="facility", value=fac_name))

        # Time constraints
        time_patterns = ["after 5 pm", "5 pm", "5 बजे के बाद", "5 वाजेनंतर", "hours a week", "शाम", "सकाळी"]
        for tp in time_patterns:
            if tp in lower:
                entities.append(EntityResult(provider=self.name, confidence=0.90, entity_type="time", value=tp))

        # Urgency
        urgency_patterns = ["broken", "urgent", "अडचण", "emergency", "नाही", "बंद", "खड्डे"]
        for up in urgency_patterns:
            if up in lower:
                entities.append(EntityResult(provider=self.name, confidence=0.80, entity_type="urgency", value=up))

        return entities

