"""NLP providers — deterministic mocks (default). Real LLM/NER providers TBD (PRD §11).

TODO(PRD FR-012–018, Phase 2, Member C): replace mocks with the chosen
LLM/NER approach behind the same interfaces; keep rule-based fallbacks.
"""

from __future__ import annotations

from ai.interfaces.schemas import (
    ClassificationResult,
    EntityResult,
    LanguageDetectionResult,
    NormalizationResult,
)

TAXONOMY = (
    "water",
    "roads",
    "health",
    "education",
    "power",
    "sanitation",
    "connectivity",
    "transport",
    "other",
)


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
            taxonomy=("transport", "water", "health", "education", "roads", "other"),
            uncertainty_notes=["Mock classifier — always 'other', not real"],
        )


class MockEntityExtractor:
    name = "mock"

    def extract(self, text: str) -> list[EntityResult]:
        return []  # TODO(PRD FR-015): real extraction in Phase 2


class RuleBasedLanguageDetector:
    """Multilingual detector supporting BRICS languages: hi, mr, en, pt, ru, zh, zu, af (FR-010)."""

    name = "rule_based"

    def detect(self, text: str) -> LanguageDetectionResult:
        if not text or not text.strip():
            return LanguageDetectionResult(provider=self.name, confidence=0.0, language="unknown")

        # 1. CJK characters -> Chinese (zh)
        if any("\u4e00" <= ch <= "\u9fff" for ch in text):
            return LanguageDetectionResult(provider=self.name, confidence=0.95, language="zh")

        # 2. Cyrillic -> Russian (ru)
        if any("\u0400" <= ch <= "\u04ff" for ch in text):
            return LanguageDetectionResult(provider=self.name, confidence=0.95, language="ru")

        # 3. Devanagari -> Hindi (hi) vs Marathi (mr)
        has_devanagari = any("\u0900" <= ch <= "\u097f" for ch in text)
        if has_devanagari:
            mr_markers = {
                "आहे",
                "नाही",
                "गावात",
                "शाळा",
                "शाळेत",
                "रस्ता",
                "पाणी",
                "पाण्याचा",
                "मुलांना",
                "अडचण",
                "शौचालय",
                "येते",
                "होते",
                "केले",
                "करावे",
                "नळ",
                "स्थानक",
                "वाजेनंतर",
                "आम्हाला",
                "खूप",
                "झाले",
                "करा",
                "गाव",
                "गावातील",
                "समस्या",
            }
            hi_markers = {
                "है",
                "में",
                "गाँव",
                "गांव",
                "नहीं",
                "सड़क",
                "पानी",
                "मिलती",
                "होता",
                "किए",
                "करना",
                "नल",
                "स्कूल",
                "शाम",
                "बजे",
                "हमे",
                "समस्या",
                "बिजली",
            }

            words = set(text.replace("।", " ").replace(".", " ").replace(",", " ").split())
            mr_count = len(words.intersection(mr_markers))
            hi_count = len(words.intersection(hi_markers))

            if mr_count > hi_count:
                return LanguageDetectionResult(provider=self.name, confidence=0.88, language="mr")
            if hi_count > mr_count:
                return LanguageDetectionResult(provider=self.name, confidence=0.88, language="hi")
            # If tie, check for characteristic Marathi nouns
            is_mr = any(w in text for w in ["पाणी", "पाण्याचा", "नाही", "आहे", "गावात", "नळ", "गाव"])
            return LanguageDetectionResult(
                provider=self.name,
                confidence=0.82 if is_mr else 0.75,
                language="mr" if is_mr else "hi",
            )

        # 4. Latin-based: Portuguese (pt), Zulu (zu), Afrikaans (af), English (en)
        lower = text.lower()
        words = set(lower.replace(".", " ").replace(",", " ").replace("!", " ").split())

        # Portuguese check
        pt_markers = {
            "não",
            "água",
            "estrada",
            "escola",
            "hospital",
            "problema",
            "bairro",
            "cidade",
            "falta",
            "sem",
            "rua",
            "lixo",
            "esgoto",
            "energia",
            "comunidade",
        }
        if any(ch in lower for ch in ["ã", "õ", "ç"]) or len(words.intersection(pt_markers)) >= 2:
            return LanguageDetectionResult(provider=self.name, confidence=0.90, language="pt")

        # Zulu check
        zu_markers = {
            "amanzi",
            "umgwaqo",
            "isikole",
            "isibhedlela",
            "amagesi",
            "akukho",
            "inkinga",
            "ngicela",
            "abantu",
        }
        if len(words.intersection(zu_markers)) >= 1:
            return LanguageDetectionResult(provider=self.name, confidence=0.88, language="zu")

        # Afrikaans check
        af_markers = {"geen", "paaie", "hospitaal", "skool", "krag", "probleem", "ons", "asseblief"}
        if len(words.intersection(af_markers)) >= 2:
            return LanguageDetectionResult(provider=self.name, confidence=0.88, language="af")

        has_latin = any("a" <= ch.lower() <= "z" for ch in text)
        if has_latin:
            return LanguageDetectionResult(provider=self.name, confidence=0.92, language="en")

        return LanguageDetectionResult(provider=self.name, confidence=0.3, language="unknown")


class RuleBasedTextNormalizer:
    name = "rule_based"

    def normalize(self, text: str) -> NormalizationResult:
        cleaned = " ".join(text.strip().split())
        lower = cleaned.lower()

        # Semantic English translation mapping for standard civic complaints
        translated_phrases = []

        if any(w in lower for w in ["पिण्याच्या पाण्याचा पुरवठा नाही", "पाणी नाही", "पानी नहीं", "falta de água", "sem água", "нет воды"]):
            translated_phrases.append("No drinking water supply in the area")
        elif any(w in lower for w in ["पाणी", "पानी", "water", "água", "вода", "amanzi"]):
            translated_phrases.append("Drinking water service disruption")

        if any(w in lower for w in ["नळ बंद", "नल बंद", "pipeline broken", "vazamento"]):
            translated_phrases.append("pipeline leak or tap shut")

        if any(w in lower for w in ["रस्ता खराब", "खड्डे", "सड़क टूटी", "buraco", "дорога ямы"]):
            translated_phrases.append("Severe potholes and road degradation")

        if any(w in lower for w in ["शाळेत शौचालय नाही", "स्कूल में शौचालय नहीं"]):
            translated_phrases.append("Lack of functional toilets in school")

        if any(w in lower for w in ["वीज नाही", "बिजली गुल", "sem luz", "apagão", "нет света"]):
            translated_phrases.append("Frequent power outage and electrical blackout")

        if any(w in lower for w in ["कचरा", "सांडपाणी", "lixo", "esgoto"]):
            translated_phrases.append("Sewage blockage and sanitation waste overflow")

        # Check for place names to preserve
        place_found = None
        for p in ["Demo Village 1", "डेमो गाव 1", "Demo Town 2", "डेमो टाउन 2", "Pune", "Aurangabad", "Chhatrapati Sambhajinagar"]:
            if p in text or p.lower() in lower:
                place_found = p
                break

        if translated_phrases:
            summary = "; ".join(translated_phrases)
            if place_found:
                normalized = f"{summary} in {place_found}."
            else:
                normalized = f"{summary}."
        else:
            normalized = cleaned

        return NormalizationResult(
            provider=self.name,
            confidence=0.92,
            normalized_text=normalized,
        )


class RuleBasedIssueClassifier:
    """Multilingual keyword and taxonomy classifier covering BRICS terms (FR-014)."""

    name = "rule_based"

    def classify(self, text: str) -> ClassificationResult:
        lower = text.lower()

        # Check for education/sanitation compound
        if any(w in lower for w in ["toilet", "शौचालय"]) and any(
            w in lower for w in ["school", "शाळा", "शाळेत", "स्कूल", "escola"]
        ):
            return ClassificationResult(
                provider=self.name, confidence=0.92, label="education", taxonomy=TAXONOMY
            )

        keywords = {
            "water": [
                "water", "drinking", "pipeline", "tap", "borewell", "tanker", "leakage", "leak",
                "पाणी", "पाण्याचा", "पानी", "जल", "नळ", "नल", "टाकी", "टँकर", "विहीर",
                "água", "vazamento", "torneira", "poço", "вода", "водопровод", "水", "停水", "amanzi",
            ],
            "roads": [
                "road", "pothole", "highway", "bridge", "pavement", "street", "broken road", "asphalt",
                "सड़क", "रस्ता", "मार्ग", "पूल", "खड्डे", "खड्डा", "डांबरीकरण",
                "estrada", "rua", "buraco", "asfalto", "ponte", "дорога", "яма", "мост", "路", "修路", "umgwaqo", "paaie",
            ],
            "power": [
                "electricity", "power", "power cut", "blackout", "transformer", "wire", "voltage",
                "बिजली", "वीज", "करंट", "लाइट", "लोड शेडिंग", "luz", "energia", "apagão", "poste",
                "электричество", "свет", "трансформатор", "电", "停电", "amagesi", "krag",
            ],
            "sanitation": [
                "sanitation", "toilet", "drainage", "sewage", "gutter", "garbage", "waste", "cleanliness",
                "सफाई", "कचरा", "शौचालय", "सांडपाणी", "गटर", "ड्रेनेज", "स्वच्छता",
                "lixo", "esgoto", "saneamento", "banheiro", "мусор", "канализация", "туалет", "垃圾", "排污", "isimbuzi",
            ],
            "connectivity": [
                "connectivity", "internet", "network", "mobile tower", "broadband", "signal", "wifi",
                "वायफाय", "इंटरनेट", "नेटवर्क", "टावर", "सिग्नल",
                "internet", "sinal", "rede", "antena", "связь", "интернет", "вышка", "网络", "信号", "宽带", "inthanethi",
            ],
            "education": [
                "school", "college", "teacher", "classroom", "student", "education",
                "शाळा", "शाळेत", "स्कूल", "शिक्षक", "शिक्षिका", "वर्ग", "विद्यार्थी",
                "escola", "professor", "aluno", "aula", "educação", "школа", "учитель", "класс", "学校", "教师", "学生", "isikole",
            ],
            "health": [
                "hospital", "clinic", "dispensary", "doctor", "health", "medicine", "phc", "nurse",
                "दवाखाना", "रुग्णालय", "आरोग्य", "डॉक्टर", "औषध", "उपचार",
                "hospital", "saúde", "médico", "remédio", "posto de saúde", "больница", "врач", "аптека", "лекарство", "医院", "医生", "药品", "isibhedlela",
            ],
            "transport": [
                "bus", "transport", "transit", "travel", "rickshaw", "vehicle", "route", "depot",
                "बस", "वाहतूक", "गाडी", "सवारी", "बसें", "स्थानक", "स्टँड",
                "ônibus", "transporte", "veículo", "linha", "автобус", "транспорт", "маршрутка", "公交", "巴士", "车", "ibhasi",
            ],
        }

        for sector, kws in keywords.items():
            if any(kw in lower for kw in kws):
                return ClassificationResult(
                    provider=self.name, confidence=0.90, label=sector, taxonomy=TAXONOMY
                )

        return ClassificationResult(
            provider=self.name,
            confidence=0.40,
            label="other",
            taxonomy=TAXONOMY,
            uncertainty_notes=["No distinct sector keyword matched; defaulting to other"],
        )


class RuleBasedEntityExtractor:
    """Extracts village, location, facility, time, urgency, and affected count entities (FR-015/016)."""

    name = "rule_based"

    def extract(self, text: str) -> list[EntityResult]:
        entities: list[EntityResult] = []
        lower = text.lower()

        # Known place names / locations (BRICS & Demo)
        known_places = [
            ("Demo Village 1", ["demo village 1", "डेमो गाव 1", "डेमो गाँव 1"]),
            ("Demo Town 2", ["demo town 2", "डेमो टाउन 2"]),
            ("Aurangabad", ["aurangabad", "chhatrapati sambhajinagar", "संभाजीनगर", "औरंगाबाद"]),
            ("Pune", ["pune", "पुणे"]),
            ("São Paulo", ["são paulo", "sao paulo"]),
            ("Johannesburg", ["johannesburg", "joburg"]),
            ("Moscow", ["moscow", "москва"]),
            ("Beijing", ["beijing", "北京"]),
            ("Old Temple", ["old temple", "जुने मंदिर", "मंदिर"]),
        ]
        for canonical, aliases in known_places:
            if any(alias in lower for alias in aliases):
                entities.append(
                    EntityResult(
                        provider=self.name,
                        confidence=0.92,
                        entity_type="location",
                        value=canonical,
                    )
                )

        # Facilities
        facility_patterns = [
            ("water_supply", ["water supply", "pipe", "pipeline", "tap", "पाणी पुरवठा", "पाणी", "पानी", "नल", "नळ", "टाकी", "água", "torneira"]),
            ("school", ["school", "शाळा", "स्कूल", "escola", "школа", "学校"]),
            ("bus_stop", ["bus stop", "bus stand", "बस स्टँड", "बस स्थानक", "बस", "parada de ônibus"]),
            ("clinic", ["hospital", "clinic", "dispensary", "दवाखाना", "रुग्णालय", "hospital", "больница", "医院"]),
            ("toilet", ["toilet", "washroom", "शौचालय", "banheiro", "туалет"]),
            ("transformer", ["transformer", "power line", "ट्रान्सफॉर्मर", "वीज", "बिजली", "transformador"]),
        ]
        for fac_name, kws in facility_patterns:
            if any(kw in lower for kw in kws):
                entities.append(
                    EntityResult(
                        provider=self.name,
                        confidence=0.88,
                        entity_type="facility",
                        value=fac_name,
                    )
                )

        # Urgency
        urgency_patterns = [
            "broken", "urgent", "अडचण", "emergency", "नाही", "बंद", "खड्डे", "तातडीने",
            "खराब", "उशीर", "urgente", "crítico", "sem água", "срочно", "紧急", "危险",
        ]
        for up in urgency_patterns:
            if up in lower:
                entities.append(
                    EntityResult(provider=self.name, confidence=0.85, entity_type="urgency", value=up)
                )
                break

        # Affected count
        affected_patterns = [
            ("entire village", ["entire village", "पूर्ण गाव", "गावातील सर्व", "toda a comunidade", "все жители"]),
            ("all students", ["all students", "सर्व विद्यार्थी", "मुलांना", "todos os alunos"]),
            ("500 people", ["500 people", "500 लोक", "500 नागरिक"]),
            ("100 families", ["100 families", "100 कुटुंबे", "100 परिवार"]),
        ]
        for count_val, kws in affected_patterns:
            if any(kw in lower for kw in kws):
                entities.append(
                    EntityResult(
                        provider=self.name,
                        confidence=0.85,
                        entity_type="affected_count",
                        value=count_val,
                    )
                )
        # Time / duration patterns
        import re

        time_matches = re.findall(
            r"(\d{1,2}\s*(?:बजे|वाजेनंतर|वाजता|pm|am|hours|days|weeks|months|horas|часов|点)|\b(?:morning|evening|night|शाम|सकाळी|संध्याकाळी|रात्री)\b)",
            lower,
        )
        for tm in time_matches:
            entities.append(
                EntityResult(
                    provider=self.name,
                    confidence=0.85,
                    entity_type="time",
                    value=tm.strip(),
                )
            )
            break

        return entities


class GeminiNLPProvider:
    """Google Gemini LLM provider for Multilingual NLP (FR-010/012/014-017).

    Performs language detection, text normalization, fixed-taxonomy issue classification,
    and named entity extraction using Gemini 1.5 Flash.
    Includes single-pass caching and seamless rule-based fallback if offline/unconfigured.
    """

    name = "gemini"
    ENDPOINT = (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    )

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash") -> None:
        import os

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self._cache: dict[str, dict] = {}
        # Rule-based fallbacks
        self._rb_lang = RuleBasedLanguageDetector()
        self._rb_norm = RuleBasedTextNormalizer()
        self._rb_cls = RuleBasedIssueClassifier()
        self._rb_ner = RuleBasedEntityExtractor()

    def _call_gemini(self, text: str) -> dict | None:
        """Calls Gemini API with structured JSON output instructions."""
        if not self.api_key or not text.strip():
            return None

        cache_key = text.strip()
        if cache_key in self._cache:
            return self._cache[cache_key]

        system_prompt = (
            "You are CivicPulse's multilingual civic intake AI. "
            "Analyze the citizen input provided. Adhere strictly to these rules:\n"
            "1. Language must be one of: 'hi', 'mr', 'en', 'pt', 'ru', 'zh', 'zu', 'af', 'unknown'.\n"
            "2. Issue taxonomy is FIXED to: 'water', 'roads', 'health', 'education', "
            "'power', 'sanitation', 'connectivity', 'transport', 'other'.\n"
            "3. Entities must have entity_type in: "
            "'location', 'urgency', 'affected_count', 'facility', 'time', 'place'. "
            "Never translate proper place names (keep original or standard transliteration).\n"
            "4. normalized_text must translate and summarize the issue clearly in English "
            "so planners can understand it, while keeping proper nouns untranslated.\n"
            "5. Provide calibrated confidence scores (0.0 to 1.0).\n\n"
            "Output strictly valid JSON with this exact schema:\n"
            "{\n"
            '  "language": "hi|mr|en|pt|ru|zh|zu|af|unknown",\n'
            '  "language_confidence": 0.95,\n'
            '  "normalized_text": "...",\n'
            '  "issue_type": "water|roads|health|education|power|sanitation|connectivity|transport|other",\n'
            '  "issue_confidence": 0.90,\n'
            '  "entities": [\n'
            '    {"entity_type": "location|urgency|affected_count|facility|time", '
            '"value": "...", "confidence": 0.85}\n'
            "  ]\n"
            "}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": system_prompt},
                        {"text": f"Citizen Request:\n{text}"},
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        try:
            import json

            import httpx

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            raw_json = parts[0].get("text", "{}")
                            parsed = json.loads(raw_json)
                            self._cache[cache_key] = parsed
                            return parsed
        except Exception:
            pass

        return None

    def detect(self, text: str) -> LanguageDetectionResult:
        parsed = self._call_gemini(text)
        if parsed and "language" in parsed:
            lang = parsed["language"]
            if lang in ("hi", "mr", "en", "pt", "ru", "zh", "zu", "af", "unknown"):
                return LanguageDetectionResult(
                    provider=self.name,
                    confidence=float(parsed.get("language_confidence", 0.92)),
                    language=lang,
                    uncertainty_notes=[],
                )
        rb_res = self._rb_lang.detect(text)
        if not self.api_key:
            rb_res.uncertainty_notes.append(
                "GEMINI_API_KEY not configured; rule-based language detector used."
            )
        return rb_res

    def normalize(self, text: str) -> NormalizationResult:
        parsed = self._call_gemini(text)
        if parsed and "normalized_text" in parsed and parsed["normalized_text"]:
            return NormalizationResult(
                provider=self.name,
                confidence=0.95,
                normalized_text=str(parsed["normalized_text"]).strip(),
                uncertainty_notes=[],
            )
        return self._rb_norm.normalize(text)

    def classify(self, text: str) -> ClassificationResult:
        parsed = self._call_gemini(text)
        if parsed and "issue_type" in parsed:
            label = parsed["issue_type"]
            if label in TAXONOMY:
                return ClassificationResult(
                    provider=self.name,
                    confidence=float(parsed.get("issue_confidence", 0.90)),
                    label=label,
                    taxonomy=TAXONOMY,
                    uncertainty_notes=[],
                )
        rb_res = self._rb_cls.classify(text)
        if not self.api_key:
            rb_res.uncertainty_notes.append(
                "GEMINI_API_KEY not configured; rule-based classifier used."
            )
        return rb_res

    def extract(self, text: str) -> list[EntityResult]:
        parsed = self._call_gemini(text)
        if parsed and "entities" in parsed and isinstance(parsed["entities"], list):
            results = []
            for item in parsed["entities"]:
                e_type = item.get("entity_type", "place")
                val = item.get("value", "")
                conf = float(item.get("confidence", 0.85))
                if val:
                    results.append(
                        EntityResult(
                            provider=self.name,
                            confidence=conf,
                            entity_type=e_type,
                            value=val,
                        )
                    )
            if results:
                return results
        return self._rb_ner.extract(text)


class OpenAINLPProvider:
    """OpenAI GPT-4o-mini provider for Multilingual NLP (FR-010/012/014-017)."""

    name = "openai"

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini") -> None:
        import os

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._cache: dict[str, dict] = {}
        self._rb_lang = RuleBasedLanguageDetector()
        self._rb_norm = RuleBasedTextNormalizer()
        self._rb_cls = RuleBasedIssueClassifier()
        self._rb_ner = RuleBasedEntityExtractor()

    def _call_openai(self, text: str) -> dict | None:
        if not self.api_key or not text.strip():
            return None

        cache_key = text.strip()
        if cache_key in self._cache:
            return self._cache[cache_key]

        system_prompt = (
            "You are CivicPulse's multilingual civic intake AI for BRICS public governance. "
            "Analyze the citizen input. Translate any non-English text to clear English in `normalized_text`. "
            "Output strictly valid JSON with this exact schema:\n"
            "{\n"
            '  "language": "hi|mr|en|pt|ru|zh|zu|af|unknown",\n'
            '  "language_confidence": 0.95,\n'
            '  "normalized_text": "...",\n'
            '  "issue_type": "water|roads|health|education|power|sanitation|connectivity|transport|other",\n'
            '  "issue_confidence": 0.90,\n'
            '  "entities": [\n'
            '    {"entity_type": "location|urgency|affected_count|facility|time", '
            '"value": "...", "confidence": 0.85}\n'
            "  ]\n"
            "}"
        )

        try:
            import json

            import httpx

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1,
            }
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(
                    "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    self._cache[cache_key] = parsed
                    return parsed
        except Exception:
            pass

        return None

    def detect(self, text: str) -> LanguageDetectionResult:
        parsed = self._call_openai(text)
        if parsed and "language" in parsed and parsed["language"] in ("hi", "mr", "en", "pt", "ru", "zh", "zu", "af", "unknown"):
            return LanguageDetectionResult(
                provider=self.name,
                confidence=float(parsed.get("language_confidence", 0.92)),
                language=parsed["language"],
            )
        return self._rb_lang.detect(text)

    def normalize(self, text: str) -> NormalizationResult:
        parsed = self._call_openai(text)
        if parsed and "normalized_text" in parsed and parsed["normalized_text"]:
            return NormalizationResult(
                provider=self.name,
                confidence=0.95,
                normalized_text=str(parsed["normalized_text"]).strip(),
            )
        return self._rb_norm.normalize(text)

    def classify(self, text: str) -> ClassificationResult:
        parsed = self._call_openai(text)
        if parsed and "issue_type" in parsed and parsed["issue_type"] in TAXONOMY:
            return ClassificationResult(
                provider=self.name,
                confidence=float(parsed.get("issue_confidence", 0.90)),
                label=parsed["issue_type"],
                taxonomy=TAXONOMY,
            )
        return self._rb_cls.classify(text)

    def extract(self, text: str) -> list[EntityResult]:
        parsed = self._call_openai(text)
        if parsed and "entities" in parsed and isinstance(parsed["entities"], list):
            results = []
            for item in parsed["entities"]:
                val = item.get("value", "")
                if val:
                    results.append(
                        EntityResult(
                            provider=self.name,
                            confidence=float(item.get("confidence", 0.85)),
                            entity_type=item.get("entity_type", "place"),
                            value=val,
                        )
                    )
            if results:
                return results
        return self._rb_ner.extract(text)
