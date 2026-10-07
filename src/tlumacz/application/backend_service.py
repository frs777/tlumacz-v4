"""Warstwa usług backendów niezależna od Qt.

Ten moduł przejmuje od GUI wybór, konfigurację i dostęp do aktywnych
backendów V4. Warstwa prezentacji nie zna konkretnych adapterów.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from tlumacz.application.backend_registry import BackendRegistry, BackendSelection
from tlumacz.backends.llama_cpp.adapter import LlamaCppConfig
from tlumacz.domain.contracts import (
    BackendCapabilities,
    BackendConfiguration,
    BackendResult,
    HealthCheckResult,
)


@dataclass(frozen=True, slots=True)
class BackendRequest:
    """Wybór backendu wraz z jego konfiguracją."""

    backend: str
    configuration: BackendConfiguration = BackendConfiguration()


class BackendService:
    """Fasada nad rejestrem backendów V4."""

    def __init__(self, registry: BackendRegistry | None = None) -> None:
        self.registry = registry or BackendRegistry()

    @property
    def active_backends(self) -> tuple[str, ...]:
        return self.registry.ACTIVE_BACKENDS

    def selection(self, request: BackendRequest) -> BackendSelection:
        if request.backend not in self.active_backends:
            raise ValueError(f"Nieznany backend: {request.backend!r}")
        return BackendSelection(
            backend=request.backend,
            configuration=request.configuration,
        )

    def configure_llama(self, config: LlamaCppConfig) -> None:
        self.registry.configure_llama(config)

    def restart_apertium_service(self) -> None:
        self.registry.restart_apertium_service()

    def reconnect_cloud(self) -> None:
        self.registry.reconnect_cloud()

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        selection: BackendSelection,
    ) -> BackendResult:
        return self.registry.translate(
            text,
            source_language=source_language,
            target_language=target_language,
            selection=selection,
        )

    def translate_many(
        self,
        units: Iterable[tuple[str, str, str]],
        *,
        target_language: str,
        selection: BackendSelection,
    ) -> dict[str, BackendResult]:
        return self.registry.translate_many(
            units,
            target_language=target_language,
            selection=selection,
        )

    def capabilities(self, backend: str) -> BackendCapabilities:
        return self.registry.capabilities(backend)

    def health_check(self, backend: str) -> HealthCheckResult:
        return self.registry.health_check(backend)


__all__ = ["BackendRequest", "BackendService"]
