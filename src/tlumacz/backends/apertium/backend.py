"""Common backend facade for Apertium."""

from __future__ import annotations

from tlumacz.domain.contracts import BackendResult, HealthCheckResult

from .adapter import ApertiumAdapter
from .config import ApertiumConfig


class ApertiumBackend:
    """Expose Apertium through the application TranslationBackend contract."""

    name = "apertium"

    def __init__(self, adapter: ApertiumAdapter | None = None) -> None:
        self.adapter = adapter or ApertiumAdapter(ApertiumConfig())

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
    ) -> BackendResult:
        return self.adapter.translate(
            text,
            source_language=source_language,
            target_language=target_language,
        )

    def health_check(self) -> HealthCheckResult:
        return self.adapter.health_check()


__all__ = ["ApertiumBackend"]
