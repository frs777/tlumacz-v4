"""Provider-neutral router for cloud translation backends."""

from __future__ import annotations

from dataclasses import dataclass

from tlumacz.backends.cloud.provider import CloudProvider
from tlumacz.domain.contracts import BackendResult


@dataclass(frozen=True, slots=True)
class CloudRoute:
    """Runtime route selecting exactly one cloud provider."""

    provider: str
    base_url: str = ""
    api_key: str = ""
    engine: str = "default"
    timeout: float = 30.0

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("provider nie może być pusty")
        if self.timeout <= 0:
            raise ValueError("timeout musi być dodatni")


class CloudRouter:
    """Route translation calls without provider-specific knowledge."""

    def __init__(self) -> None:
        self._providers: dict[str, CloudProvider] = {}

    def register(self, provider: CloudProvider) -> None:
        name = provider.name.strip()
        if not name:
            raise ValueError("provider.name nie może być pusty")
        if name in self._providers:
            raise ValueError(f"Provider {name!r} jest już zarejestrowany")
        self._providers[name] = provider

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        route: CloudRoute,
    ) -> BackendResult:
        try:
            provider = self._providers[route.provider]
        except KeyError as exc:
            raise ValueError(
                f"Provider {route.provider!r} nie jest zarejestrowany"
            ) from exc

        return provider.translate(
            text,
            source_language=source_language,
            target_language=target_language,
            base_url=route.base_url,
            api_key=route.api_key,
            engine=route.engine,
            timeout=route.timeout,
        )


__all__ = ["CloudRoute", "CloudRouter"]
