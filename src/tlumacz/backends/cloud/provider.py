"""Shared contract for cloud translation providers."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from tlumacz.domain.contracts import BackendResult


@runtime_checkable
class CloudProvider(Protocol):
    """Provider adapter independent from CloudRouter and UI."""

    name: str

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        base_url: str,
        api_key: str,
        engine: str,
        timeout: float,
    ) -> BackendResult:
        """Translate one text unit and return the common backend result."""
        ...


__all__ = ["CloudProvider"]
