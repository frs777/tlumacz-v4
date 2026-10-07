"""Backend „Własny” dla lokalnych i zdalnych serwerów OpenAI-compatible."""

from __future__ import annotations

from tlumacz.backends.cloud.providers import OpenAICompatibleProvider
from tlumacz.domain.contracts import BackendResult, HealthCheckResult


class CustomBackend:
    """Adapter własnego serwera bez uzależniania go od katalogu Cloud.

    Transport OpenAI-compatible jest współdzielony z backendem Cloud, ale
    konfiguracja i granica odpowiedzialności backendu „Własny” pozostają
    niezależne od providerów Cloud.
    """

    name = "custom"

    def __init__(self) -> None:
        self._transport = OpenAICompatibleProvider()

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float,
    ) -> BackendResult:
        if not base_url.strip():
            raise ValueError("Backend „Własny” wymaga adresu serwera.")
        if not model.strip():
            raise ValueError("Backend „Własny” wymaga nazwy modelu.")
        result = self._transport.translate(
            text,
            source_language=source_language,
            target_language=target_language,
            base_url=base_url,
            api_key=api_key,
            engine=model,
            timeout=timeout,
        )
        return BackendResult(
            text=result.text,
            source_language=result.source_language,
            target_language=result.target_language,
            metadata={
                **result.metadata,
                "backend": self.name,
                "provider": "custom-openai-compatible",
            },
        )

    def health_check(self) -> HealthCheckResult:
        """Transport jest bezstanowy; dostępność endpointu sprawdza tłumaczenie."""
        return HealthCheckResult.ok(self.name)


__all__ = ["CustomBackend"]
