"""Validate translation backend results before document write."""

from __future__ import annotations

from tlumacz.domain.contracts import BackendResult
from tlumacz.filter_engine.marker_validator import MarkerValidator


class ResultValidator:
    """Validate semantic invariants of one backend result."""

    def validate(
        self,
        source_text: str,
        result: BackendResult,
        *,
        expected_source_language: str,
        expected_target_language: str,
    ) -> BackendResult:
        if not isinstance(result.text, str):
            raise ValueError("Wynik tłumaczenia musi być tekstem.")
        if source_text.strip() and not result.text.strip():
            raise ValueError("Wynik tłumaczenia jest pusty.")
        if expected_source_language and result.source_language != expected_source_language:
            raise ValueError(
                f"Niezgodny język źródłowy: {result.source_language!r}."
            )
        if expected_target_language and result.target_language != expected_target_language:
            raise ValueError(
                f"Niezgodny język docelowy: {result.target_language!r}."
            )
        MarkerValidator.validate(result.text)
        return result
        return result


__all__ = ["ResultValidator"]
