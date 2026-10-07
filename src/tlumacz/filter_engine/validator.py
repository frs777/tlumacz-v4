"""Validation of extracted translation units and merged targets."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from tlumacz.domain.errors import FilterError


class FilterValidator:
    """Validate structural invariants at the filter-engine boundary."""

    @staticmethod
    def validate_units(units: Iterable[Any]) -> list[tuple[str, str]]:
        normalized: list[tuple[str, str]] = []
        seen: set[str] = set()

        for unit in units:
            try:
                if isinstance(unit, tuple) and len(unit) == 2:
                    unit_id, source = unit
                else:
                    unit_id, source = unit.id, unit.source
            except AttributeError as exc:
                raise FilterError("Filter returned an invalid translation unit") from exc

            if not isinstance(unit_id, str) or not unit_id.strip():
                raise FilterError("Filter returned a unit with invalid unit id")
            if not isinstance(source, str):
                raise FilterError("Filter returned a unit with invalid source")
            if unit_id in seen:
                raise FilterError(f"Filter returned a duplicate unit id: {unit_id}")
            seen.add(unit_id)
            normalized.append((unit_id, source))

        return normalized

    @staticmethod
    def validate_targets(
        units: Iterable[tuple[str, str]],
        targets: Mapping[str, str],
    ) -> None:
        expected = {unit_id for unit_id, _ in units}
        actual = set(targets)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            details: list[str] = []
            if missing:
                details.append(f"missing targets: {missing}")
            if extra:
                details.append(f"extra targets: {extra}")
            raise FilterError("Filter returned invalid targets: " + "; ".join(details))

        if any(not isinstance(target, str) for target in targets.values()):
            raise FilterError("Filter returned a target with invalid type")
