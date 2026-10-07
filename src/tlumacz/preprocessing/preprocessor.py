"""Przygotowanie dokumentu przed wyborem i użyciem konkretnego filtra."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping


class PreflightPath(str, Enum):
    """Wysokopoziomowa ścieżka przetwarzania dokumentu."""

    NATIVE_TEXT = "native_text"
    FILTER_ENGINE = "filter_engine"


@dataclass(frozen=True, slots=True)
class PreflightResult:
    """Wynik preflightu bez wiedzy o konkretnej implementacji filtra."""

    input_path: Path
    path: PreflightPath
    suffix: str


class PreprocessDecision(str, Enum):
    """Decyzja klasyfikacji jednostki przed planowaniem transportu."""

    TRANSLATE = "translate"
    KEEP = "keep"


@dataclass(frozen=True, slots=True)
class PreprocessedUnit:
    """Jednostka po klasyfikacji; tekst źródłowy pozostaje niezmieniony."""

    id: str
    text: str
    decision: PreprocessDecision
    metadata: Mapping[str, Any]


DEFAULT_SKIP_PATTERNS: tuple[str, ...] = (
    r"^\s*(name|license|author|metadata|version|tags|created|updated)\s*:",
)

MARKDOWN_SKIP_PATTERNS: tuple[str, ...] = (
    r"^\s*---\s*$",
)

_NATIVE_TEXT_SUFFIXES = frozenset({".txt", ".text", ".log"})


class Preprocessor:
    """Wykonuj preflight dokumentu oraz klasyfikację jednostek."""

    def preflight(self, input_path: str | Path) -> PreflightResult:
        """Wybierz ścieżkę dokumentową bez tworzenia konkretnego filtra."""
        path = Path(input_path).resolve()
        suffix = path.suffix.strip().lower()
        route = (
            PreflightPath.NATIVE_TEXT
            if suffix in _NATIVE_TEXT_SUFFIXES
            else PreflightPath.FILTER_ENGINE
        )
        return PreflightResult(input_path=path, path=route, suffix=suffix)

    def classify_units(
        self,
        units: Iterable[Any],
        *,
        skip_patterns: Iterable[str] = (),
        format_name: str | None = None,
    ) -> tuple[PreprocessedUnit, ...]:
        """Klasyfikuj wyekstrahowane jednostki jako TRANSLATE albo KEEP."""
        normalized = tuple(self._normalize(unit) for unit in units)
        ids = [item.id for item in normalized]
        if len(ids) != len(set(ids)):
            raise ValueError("Identyfikatory jednostek muszą być unikalne.")

        patterns = tuple(skip_patterns)
        if not patterns:
            patterns = DEFAULT_SKIP_PATTERNS
            if str(format_name or "").lower() in {"markdown", "md"}:
                patterns += MARKDOWN_SKIP_PATTERNS

        compiled = self._compile(patterns)
        return tuple(
            PreprocessedUnit(
                id=item.id,
                text=item.text,
                decision=(
                    PreprocessDecision.KEEP
                    if not item.text.strip()
                    or any(pattern.search(item.text) is not None for pattern in compiled)
                    else PreprocessDecision.TRANSLATE
                ),
                metadata=item.metadata,
            )
            for item in normalized
        )

    def process(
        self,
        units: Iterable[Any],
        *,
        skip_patterns: Iterable[str] = (),
        format_name: str | None = None,
    ) -> tuple[PreprocessedUnit, ...]:
        """Zachowaj dotychczasową nazwę operacji dla kodu wewnętrznego."""
        return self.classify_units(
            units,
            skip_patterns=skip_patterns,
            format_name=format_name,
        )

    @staticmethod
    def _normalize(unit: Any) -> PreprocessedUnit:
        if isinstance(unit, tuple) and len(unit) == 2:
            return PreprocessedUnit(str(unit[0]), str(unit[1]), PreprocessDecision.TRANSLATE, {})

        try:
            metadata = getattr(unit, "metadata", {}) or {}
            return PreprocessedUnit(
                id=str(unit.id),
                text=str(unit.source),
                decision=PreprocessDecision.TRANSLATE,
                metadata=dict(metadata),
            )
        except AttributeError as exc:
            raise TypeError("Jednostka musi mieć id i source") from exc

    @staticmethod
    def _compile(patterns: Iterable[str]) -> tuple[re.Pattern[str], ...]:
        compiled: list[re.Pattern[str]] = []
        for raw_pattern in patterns:
            pattern = str(raw_pattern).strip()
            if not pattern:
                continue
            try:
                compiled.append(re.compile(pattern))
            except re.error as exc:
                raise ValueError(f"Nieprawidłowy wzorzec pomijania: {pattern!r}") from exc
        return tuple(compiled)


__all__ = [
    "DEFAULT_SKIP_PATTERNS",
    "MARKDOWN_SKIP_PATTERNS",
    "PreprocessDecision",
    "PreflightPath",
    "PreflightResult",
    "PreprocessedUnit",
    "Preprocessor",
]
