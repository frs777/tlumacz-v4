"""Routing języka źródłowego wyłącznie dla tłumaczeń llama.cpp."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Protocol

from tlumacz.language_detector import LanguageDetector


class LanguageDetectorProtocol(Protocol):
    """Minimalny kontrakt niezależnego detektora języka."""

    def detect_language_code(self, text: str) -> str | None:
        ...


class LlamaCppLanguageRouting:
    """Ustala kod ISO 639-1 źródła dla każdego chunka llama.cpp.

    Detekcja jest wykonywana przez niezależny moduł Lingua. Ten komponent
    nie tłumaczy tekstu i nie jest używany przez Cloud ani Apertium.
    """

    def __init__(self, detector: LanguageDetectorProtocol | None = None) -> None:
        self.detector = detector or LanguageDetector()

    def resolve_document_source(
        self,
        units: Sequence[str],
        *,
        configured_source: str,
    ) -> str | None:
        """Ustal język na podstawie całego dokumentu, pomijając cytaty w \"...\"."""
        if configured_source != "auto":
            return configured_source
        document_text = "\n".join(text for text in units if text.strip())
        document_text = re.sub(r'"[^"]*"', " ", document_text)
        document_text = re.sub(r"\s+", " ", document_text).strip()
        return self.detector.detect_language_code(document_text)

    def resolve_chunk_source(self, text: str, *, fallback_source: str) -> str | None:
        """Wykryj język bieżącej jednostki/chunka dla dokumentów wielojęzycznych."""
        if fallback_source != "auto":
            return fallback_source
        detection_text = re.sub(r'"[^"]*"', " ", text)
        detection_text = re.sub(r"\s+", " ", detection_text).strip()
        if not detection_text:
            return fallback_source if fallback_source != "auto" else None
        detected = self.detector.detect_language_code(detection_text)
        if detected is not None:
            return detected
        if fallback_source != "auto":
            return fallback_source
        return None


__all__ = ["LanguageDetectorProtocol", "LlamaCppLanguageRouting"]
