"""Rejestr backendów V4 oparty na wspólnym kontrakcie rejestracji."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from tlumacz.backends.apertium.backend import ApertiumBackend
from tlumacz.backends.cloud.providers import CloudProviderRegistry
from tlumacz.backends.cloud.router import CloudRoute, CloudRouter
from tlumacz.backends.custom.backend import CustomBackend
from tlumacz.backends.llama_cpp.adapter import LlamaCppAdapter, LlamaCppConfig
from tlumacz.domain.contracts import (
    BackendCapabilities,
    BackendConfiguration,
    BackendResult,
    HealthCheckResult,
    TranslationBackend,
)


@dataclass(frozen=True, slots=True)
class BackendSelection:
    backend: str
    configuration: BackendConfiguration = BackendConfiguration()


class _BackendAdapter(Protocol):
    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        selection: BackendSelection,
    ) -> BackendResult: ...

    def health_check(self) -> HealthCheckResult: ...


class _CloudBackendAdapter:
    """Adapter wiążący wspólny kontrakt z konfiguracją routingu Cloud."""

    def __init__(self, router: CloudRouter) -> None:
        self._router = router

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        selection: BackendSelection,
    ) -> BackendResult:
        return self._router.translate(
            text,
            source_language=source_language,
            target_language=target_language,
            route=CloudRoute(
                provider=selection.configuration.get("provider", "openai"),
                base_url=selection.configuration.get("base_url", ""),
                api_key=selection.configuration.get("api_key", ""),
                engine=selection.configuration.get(
                    "engine",
                    selection.configuration.get("model", "default"),
                ),
                timeout=selection.configuration.get("timeout", 30.0),
            ),
        )

    def health_check(self) -> HealthCheckResult:
        return HealthCheckResult.ok("cloud")


class _CustomBackendAdapter:
    """Adapter konfigurujący backend „Własny” przez BackendSelection."""

    def __init__(self, backend: CustomBackend) -> None:
        self._backend = backend

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        selection: BackendSelection,
    ) -> BackendResult:
        return self._backend.translate(
            text,
            source_language=source_language,
            target_language=target_language,
            base_url=selection.configuration.get("base_url", ""),
            api_key=selection.configuration.get("api_key", ""),
            model=selection.configuration.get(
                "model",
                selection.configuration.get("engine", "default"),
            ),
            timeout=selection.configuration.get("timeout", 30.0),
        )

    def health_check(self) -> HealthCheckResult:
        return self._backend.health_check()


class _DirectBackendAdapter:
    """Adapter zwykłego backendu TranslationBackend do kontraktu rejestru."""

    def __init__(self, backend: TranslationBackend) -> None:
        self._backend = backend

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        selection: BackendSelection,
    ) -> BackendResult:
        return self._backend.translate(
            text,
            source_language=source_language,
            target_language=target_language,
        )

    def capabilities(self) -> BackendCapabilities:
        declared = getattr(self._backend, "capabilities", None)
        if callable(declared):
            return declared()
        return BackendCapabilities(
            batch_translation=callable(getattr(self._backend, "translate_batch", None))
        )

    def health_check(self) -> HealthCheckResult:
        return self._backend.health_check()

    def translate_batch(
        self,
        units: list[tuple[str, str, str]],
        *,
        target_language: str,
    ) -> dict[str, BackendResult]:
        batch = getattr(self._backend, "translate_batch", None)
        if not callable(batch):
            raise AttributeError("Backend nie udostępnia natywnego translate_batch().")
        return batch(units, target_language=target_language)


class _UnavailableLlamaBackend:
    """Zachowuje publiczną obecność llama przed konfiguracją adaptera."""

    def translate(self, text: str, *, source_language: str, target_language: str) -> BackendResult:
        raise RuntimeError("Backend llama.cpp nie został skonfigurowany.")

    def health_check(self) -> HealthCheckResult:
        return HealthCheckResult.failed("llama", "Backend nie został skonfigurowany.")


class BackendRegistry:
    """Rejestr backendów bez routingu zależnego od nazw implementacji.

    Nowy backend implementujący TranslationBackend można zarejestrować przez
    register() bez zmian w metodzie translate() ani w pozostałym pipeline.
    """

    def __init__(self, backends: dict[str, TranslationBackend] | None = None) -> None:
        self.cloud = CloudRouter()
        for provider in CloudProviderRegistry.default().providers():
            self.cloud.register(provider)
        self.apertium = ApertiumBackend()
        self.custom = CustomBackend()
        self._llama: LlamaCppAdapter | None = None
        self._backends: dict[str, _BackendAdapter] = {}
        self.register("llama", _DirectBackendAdapter(_UnavailableLlamaBackend()))
        self.register("cloud", _CloudBackendAdapter(self.cloud))
        self.register("apertium", _DirectBackendAdapter(self.apertium))
        self.register("custom", _CustomBackendAdapter(self.custom))
        if backends:
            for name, backend in backends.items():
                self.register(name, _DirectBackendAdapter(backend))

    @property
    def ACTIVE_BACKENDS(self) -> tuple[str, ...]:
        return tuple(self._backends)

    def register(self, name: str, backend: _BackendAdapter) -> None:
        """Dodaj backend do rejestru; jego implementacja nie trafia do routingu."""
        normalized = name.strip()
        if not normalized:
            raise ValueError("Nazwa backendu nie może być pusta")
        if normalized in self._backends:
            raise ValueError(f"Backend {normalized!r} jest już zarejestrowany")
        if not hasattr(backend, "translate") or not hasattr(backend, "health_check"):
            raise TypeError("Backend musi udostępniać translate() i health_check()")
        self._backends[normalized] = backend

    def configure_llama(self, config: LlamaCppConfig) -> None:
        self._llama = LlamaCppAdapter(config)
        self._backends["llama"] = _DirectBackendAdapter(self._llama)

    def restart_apertium_service(self) -> None:
        """Odśwież lokalną usługę Apertium przed kolejnym użyciem."""
        self.apertium = ApertiumBackend()
        self._backends["apertium"] = _DirectBackendAdapter(self.apertium)

    def reconnect_cloud(self) -> None:
        """Odśwież warstwę klientów Cloud; kolejne żądanie otworzy nowe połączenie."""
        router = CloudRouter()
        for provider in CloudProviderRegistry.default().providers():
            router.register(provider)
        self.cloud = router
        self._backends["cloud"] = _CloudBackendAdapter(self.cloud)

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        selection: BackendSelection,
    ) -> BackendResult:
        try:
            backend = self._backends[selection.backend]
        except KeyError as exc:
            raise ValueError(f"Nieznany backend: {selection.backend!r}") from exc
        return backend.translate(
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
        normalized = [(str(unit_id), str(text), str(source)) for unit_id, text, source in units]
        if not normalized:
            return {}
        backend = self._backends.get(selection.backend)
        if backend is None:
            raise ValueError(f"Nieznany backend: {selection.backend!r}")
        batch = getattr(backend, "translate_batch", None)
        if callable(batch):
            try:
                return batch(normalized, target_language=target_language)
            except AttributeError:
                pass
        return {
            unit_id: self.translate(
                text,
                source_language=source,
                target_language=target_language,
                selection=selection,
            )
            for unit_id, text, source in normalized
        }

    def capabilities(self, backend: str) -> BackendCapabilities:
        """Zwróć możliwości zadeklarowane lub wywnioskowane z adaptera."""
        implementation = self._backends.get(backend)
        if implementation is None:
            raise ValueError(f"Nieznany backend: {backend!r}")
        declared = getattr(implementation, "capabilities", None)
        if callable(declared):
            return declared()
        return BackendCapabilities(batch_translation=callable(getattr(implementation, "translate_batch", None)))

    def health_check(self, backend: str) -> HealthCheckResult:
        implementation = self._backends.get(backend)
        if implementation is None:
            return HealthCheckResult.failed(backend, f"Nieznany backend: {backend}")
        return implementation.health_check()


__all__ = ["BackendRegistry", "BackendSelection"]
