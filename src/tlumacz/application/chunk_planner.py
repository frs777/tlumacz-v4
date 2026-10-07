"""Deterministic chunk planning independent from providers and prompts."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PlannedUnit:
    id: str
    source: str
    kind: str = "paragraph"
    source_language: str | None = None


@dataclass(frozen=True, slots=True)
class ChunkPlan:
    chunks: tuple[tuple[PlannedUnit, ...], ...]
    total_units: int
    total_characters: int


class ChunkPlanner:
    """Group translation units under a character budget without reordering."""

    def __init__(self, *, max_chars: int, separator_chars: int = 8) -> None:
        if max_chars <= 0:
            raise ValueError("max_chars musi być dodatnie")
        if separator_chars < 0:
            raise ValueError("separator_chars nie może być ujemne")
        self.max_chars = max_chars
        self.separator_chars = separator_chars

    def plan(
        self,
        units: Iterable[Any],
        *,
        unit_metadata: Mapping[str, Mapping[str, Any]] | None = None,
        source_languages: Mapping[str, str] | None = None,
    ) -> ChunkPlan:
        """Grupuj jednostki według budżetu i granic strukturalnych V3."""
        metadata = unit_metadata or {}
        languages = source_languages or {}
        normalized = tuple(
            self._normalize(
                unit,
                metadata=metadata.get(str(unit[0]) if isinstance(unit, tuple) else str(unit.id), {}),
                source_language=languages.get(str(unit[0]) if isinstance(unit, tuple) else str(unit.id)),
            )
            for unit in units
        )
        chunks: list[tuple[PlannedUnit, ...]] = []
        current: list[PlannedUnit] = []
        current_chars = 0
        current_source_language: str | None = None

        for unit in normalized:
            unit_chars = len(unit.source)
            source_changed = (
                current_source_language is not None
                and unit.source_language is not None
                and unit.source_language != current_source_language
            )
            heading_boundary = (
                bool(current)
                and unit.kind == "heading"
                and current_chars >= self.max_chars * 0.6
            )
            extra = unit_chars + (self.separator_chars if current else 0)
            if current and (source_changed or heading_boundary or current_chars + extra > self.max_chars):
                chunks.append(tuple(current))
                current = []
                current_chars = 0
                current_source_language = None
                extra = unit_chars

            current.append(unit)
            current_chars += extra
            if current_source_language is None:
                current_source_language = unit.source_language

        if current:
            chunks.append(tuple(current))

        return ChunkPlan(
            chunks=tuple(chunks),
            total_units=len(normalized),
            total_characters=sum(len(unit.source) for unit in normalized),
        )

    @staticmethod
    def _normalize(
        unit: Any,
        *,
        metadata: Mapping[str, Any] | None = None,
        source_language: str | None = None,
    ) -> PlannedUnit:
        if isinstance(unit, tuple) and len(unit) == 2:
            return PlannedUnit(
                str(unit[0]),
                str(unit[1]),
                str((metadata or {}).get("kind", "paragraph")),
                source_language,
            )
        try:
            return PlannedUnit(
                str(unit.id),
                str(unit.source),
                str((metadata or getattr(unit, "metadata", {})).get("kind", "paragraph")),
                source_language,
            )
        except AttributeError as exc:
            raise TypeError("Jednostka musi mieć id i source") from exc


__all__ = ["ChunkPlan", "ChunkPlanner", "PlannedUnit"]
