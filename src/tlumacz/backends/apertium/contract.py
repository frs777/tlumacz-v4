"""Typy kontraktu niezależnego modułu Apertium."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ApertiumStatus(str, Enum):
    """Status wyniku pojedynczej jednostki tłumaczeniowej."""

    TRANSLATED = "translated"
    PARTIAL = "partial"
    UNSUPPORTED_PAIR = "unsupported_pair"
    TIMEOUT = "timeout"
    RUNTIME_UNAVAILABLE = "runtime_unavailable"
    VALIDATION_FAILED = "validation_failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class TranslationUnit:
    """Jednostka tekstowa przekazywana do backendu.

    Adapter nie zna formatu dokumentu. Markery są tylko danymi kontraktu i
    muszą wrócić w wyniku w tej samej liczbie oraz kolejności.
    """

    unit_id: str
    source_text: str
    source_language: str
    target_language: str
    inline_markers: tuple[str, ...] = ()
    context: str = ""

    def validate(self) -> None:
        """Sprawdź minimalne invariants przed uruchomieniem procesu."""
        if not self.unit_id.strip():
            raise ValueError("unit_id nie może być pusty.")
        if not self.source_language.strip() or not self.target_language.strip():
            raise ValueError("Język źródłowy i docelowy są wymagane.")
        if not self.source_text:
            raise ValueError("Tekst źródłowy nie może być pusty.")
        if len(set(self.inline_markers)) != len(self.inline_markers):
            raise ValueError("Markery inline muszą być unikalne.")


@dataclass(frozen=True, slots=True)
class TranslationResult:
    """Wynik backendu bez zależności od modelu dokumentowego."""

    unit_id: str
    target_text: str
    status: ApertiumStatus
    source_language: str
    target_language: str
    pair: str
    backend: str = "apertium"
    runtime_version: str | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)
    elapsed_seconds: float = 0.0


@dataclass(frozen=True, slots=True)
class ApertiumCapabilities:
    """Opis możliwości wykrytego runtime’u."""

    backend: str
    runtime_version: str
    language_pairs: tuple[str, ...]
    supports_stdin: bool = True
    supports_text_format: bool = True
