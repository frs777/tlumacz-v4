"""Detekcja języka źródłowego dla dedykowanego trybu TranslateGemma.

Detektor jest używany wyłącznie wtedy, gdy aktywny jest chat template
translategemma. Wynikiem jest kod ISO 639-1 zgodny z kontraktem
TranslateGemma.
"""

from __future__ import annotations

from collections.abc import Mapping
import re

from lingua import Language, LanguageDetectorBuilder
from lingua import LanguageDetector as LinguaDetector

TRANSLATE_GEMMA_LANGUAGE_CODES: dict[str, str] = {
    "Polish": "pl", "English": "en", "German": "de", "French": "fr",
    "Spanish": "es", "Italian": "it", "Ukrainian": "uk", "Czech": "cs",
    "Dutch": "nl", "Russian": "ru", "Chinese": "zh", "Japanese": "ja",
    "Korean": "ko", "Arabic": "ar", "Portuguese": "pt", "Turkish": "tr",
    "Vietnamese": "vi", "Thai": "th", "Indonesian": "id", "Malay": "ms",
    "Hindi": "hi", "Bengali": "bn", "Tamil": "ta", "Telugu": "te",
    "Marathi": "mr", "Gujarati": "gu", "Kannada": "kn", "Malayalam": "ml",
    "Punjabi": "pa", "Urdu": "ur", "Persian": "fa", "Hebrew": "he",
    "Greek": "el", "Bulgarian": "bg", "Romanian": "ro", "Hungarian": "hu",
    "Finnish": "fi", "Swedish": "sv", "Norwegian": "no", "Danish": "da",
    "Icelandic": "is", "Estonian": "et", "Latvian": "lv", "Lithuanian": "lt",
    "Slovak": "sk", "Slovenian": "sl", "Croatian": "hr", "Serbian": "sr",
    "Bosnian": "bs", "Macedonian": "mk", "Albanian": "sq", "Montenegrin": "cnr",
    "Welsh": "cy", "Irish": "ga", "Scottish Gaelic": "gd", "Breton": "br",
    "Basque": "eu", "Catalan": "ca", "Galician": "gl", "Maltese": "mt",
    "Luxembourgish": "lb", "Romansh": "rm", "Faroese": "fo", "Sami": "se",
    "Greenlandic": "kl", "Esperanto": "eo", "Latin": "la",
}


class LanguageDetector:
    """Współdzielony detektor źródła dla trybu TranslateGemma."""

    def __init__(self, language_codes: Mapping[str, str] | None = None) -> None:
        mapping = language_codes or TRANSLATE_GEMMA_LANGUAGE_CODES
        language_to_code: dict[Language, str] = {}
        for name, code in mapping.items():
            try:
                language = Language.from_str(name)
            except ValueError:
                continue
            language_to_code[language] = code

        if not language_to_code:
            raise RuntimeError("Nie udało się zbudować listy języków Lingua.")

        self._language_to_code = language_to_code
        self._detector: LinguaDetector = (
            LanguageDetectorBuilder.from_languages(*language_to_code.keys()).build()
        )

    @property
    def supported_language_codes(self) -> frozenset[str]:
        """Zwróć kody języków dostępne dla detekcji."""
        return frozenset(self._language_to_code.values())

    def detect_language_code(self, text: str) -> str | None:
        """Wykryj język tekstu i zwróć kod ISO 639-1 lub None."""
        if not text or not text.strip():
            return None
        language = self._detector.detect_language_of(text)
        if language is None:
            return None
        return self._language_to_code.get(language)


def language_code_for(value: str) -> str:
    """Znormalizuj nazwę lub kod języka do kodu używanego przez TranslateGemma."""
    normalized = value.strip()
    if normalized.casefold() == "auto":
        return "auto"
    for name, code in TRANSLATE_GEMMA_LANGUAGE_CODES.items():
        if normalized.casefold() in {name.casefold(), code.casefold()}:
            return code
    regional = re.fullmatch(r"([a-z]{2})[-_]([a-z]{2})", normalized, flags=re.IGNORECASE)
    if regional:
        base, country = regional.groups()
        if base.casefold() in {code.split("-", 1)[0].casefold() for code in TRANSLATE_GEMMA_LANGUAGE_CODES.values()}:
            return f"{base.lower()}-{country.upper()}"
    return "auto"


def language_name_for(code: str) -> str:
    """Zwróć nazwę języka dla kodu TranslateGemma."""
    normalized = code.replace("_", "-").split("-", 1)[0].casefold()
    for name, mapped_code in TRANSLATE_GEMMA_LANGUAGE_CODES.items():
        if mapped_code.casefold() == normalized:
            return name
    return code


__all__ = [
    "LanguageDetector",
    "TRANSLATE_GEMMA_LANGUAGE_CODES",
    "language_code_for",
    "language_name_for",
]
