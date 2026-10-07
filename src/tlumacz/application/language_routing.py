"""Niezależne strategie detekcji języka dla backendów tłumaczeniowych V4."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from tlumacz.backends.apertium.errors import ApertiumValidationError
from tlumacz.backends.apertium.languages import normalize_language_code
from tlumacz.language_detector import LanguageDetector


class LanguageDetectorProtocol(Protocol):
    """Minimalny kontrakt detektora używany przez strategie routingu."""

    def detect_language_code(self, text: str) -> str | None:
        ...


class ApertiumLanguageRouting:
    """Detekcja dokumentowa Apertium z zamrożonym językiem źródłowym."""

    def __init__(self, detector: LanguageDetectorProtocol | None = None) -> None:
        self.detector = detector or LanguageDetector()

    def resolve_document_source(
        self,
        units: Sequence[str],
        *,
        configured_source: str,
    ) -> str | None:
        """Ustal source dokumentu; kolejne chunki nie mogą go zmienić."""
        if configured_source != "auto":
            return configured_source
        document_text = "\n".join(text for text in units if text.strip())
        return self.detector.detect_language_code(document_text)

    def resolve_chunk_source(self, text: str, *, frozen_source: str) -> str | None:
        """Zwróć zamrożony source tylko dla chunka zgodnego z nim językowo."""
        detected = self.detector.detect_language_code(text)
        if detected is None:
            return None
        try:
            detected_normalized = normalize_language_code(detected)
            frozen_normalized = normalize_language_code(frozen_source)
        except ApertiumValidationError:
            return None
        if detected_normalized != frozen_normalized:
            return None
        return frozen_source


__all__ = [
    "ApertiumLanguageRouting",
    "LanguageDetectorProtocol",
]
