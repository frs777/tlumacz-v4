"""Rdzeń aplikacyjny używany przez GUI V4.

TranslationApp jest composition rootem warstwy aplikacyjnej: składa backendy,
usługę tłumaczenia dokumentów i runtime llama.cpp bez zależności od Qt.
"""

from __future__ import annotations

from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from tlumacz.backends.llama_cpp.adapter import LlamaCppConfig
from tlumacz.backends.llama_cpp.language_routing import LlamaCppLanguageRouting
from tlumacz.backends.llama_cpp.runtime import (
    LlamaCppRuntimeConfig,
    LlamaCppRuntimeManager,
)
from tlumacz.domain.contracts import BackendResult
from tlumacz.filter_engine.filter_store import FilterStore
from tlumacz.filter_engine.registry import FilterRegistry

from .backend_controller import BackendController
from .backend_service import BackendRequest, BackendService
from .document_translation_service import DocumentTranslationService
from .language_routing import ApertiumLanguageRouting
from .translation_cache import TranslationCache


def build_filter_registry(*, filter_store: Path | None = None) -> FilterRegistry:
    """Zbuduj rejestr deskryptorów filtrów bez inicjalizowania filtrów.

    Konkretna instancja powstaje dopiero po rozpoznaniu rozszerzenia wejściowego
    przez ``FilterRegistry.for_path()`` i żyje wyłącznie przez sesję dokumentu.
    """
    return FilterRegistry(
        filter_store=filter_store or FilterStore.default().path,
    )


class TranslationApp:
    """Rdzeń aplikacyjny tłumacza, niezależny od warstwy prezentacji."""

    def __init__(
        self,
        *,
        backend_service: BackendService | None = None,
        workspace: Path | None = None,
    ) -> None:
        self.backend_service = backend_service or BackendService()
        self.backend_controller = BackendController(self.backend_service.active_backends)
        self.translation_service: DocumentTranslationService | None = None
        self.workspace = workspace or (Path.home() / ".cache" / "tlumacz-v4" / "sessions")
        self._translation_cache = TranslationCache(self.workspace / "translation-cache")
        self._runtime: LlamaCppRuntimeManager | None = None

    @property
    def runtime(self) -> LlamaCppRuntimeManager | None:
        return self._runtime

    def select_backend(self, request: BackendRequest):
        return self.backend_service.selection(request)

    def build_translation_service(
        self,
        *,
        selection,
        source_language: str,
        target_language: str,
        chunk_size: int,
        temperature: float,
        parallel: int,
    ) -> DocumentTranslationService:
        if selection.backend == "llama":
            self.backend_service.configure_llama(
                LlamaCppConfig(
                    base_url=selection.configuration.get("base_url", ""),
                    api_key=selection.configuration.get("api_key", ""),
                    model=selection.configuration.get("model", "default"),
                    timeout=selection.configuration.get("timeout", 1800.0),
                    temperature=temperature,
                    chat_template=selection.configuration.get("chat_template", ""),
                )
            )

        def translate(text: str, detected_source_language: str) -> BackendResult:
            return self.backend_service.translate(
                text,
                source_language=detected_source_language,
                target_language=target_language,
                selection=selection,
            )

        def translate_batch(
            units: list[tuple[str, str, str]],
            batch_target_language: str,
        ) -> dict[str, BackendResult]:
            return self.backend_service.translate_many(
                units,
                target_language=batch_target_language,
                selection=selection,
            )

        language_routing: ApertiumLanguageRouting | LlamaCppLanguageRouting | None
        if selection.backend == "apertium":
            language_routing = ApertiumLanguageRouting()
        elif selection.backend == "llama":
            language_routing = LlamaCppLanguageRouting()
        else:
            # Cloud i custom mają własny kontrakt źródła; nie uruchamiamy
            # dla nich detekcji Lingua należącej do ścieżki llama.cpp.
            language_routing = None
        self.translation_service = DocumentTranslationService(
            registry=build_filter_registry(),
            translate=translate,
            translate_batch=translate_batch,
            max_chars=max(500, chunk_size),
            max_workers=max(1, parallel),
            language_routing=language_routing,
        )
        self.translation_service.orchestrator.cache = self._translation_cache
        return self.translation_service

    def clear_translation_cache(self) -> None:
        self._translation_cache.clear()

    def restart_apertium_service(self) -> None:
        self.backend_service.restart_apertium_service()

    def reconnect_cloud(self) -> None:
        self.backend_service.reconnect_cloud()

    def start_llama(
        self,
        *,
        model_path: str,
        port: int,
        compute_mode: str,
        parallel: int,
        chat_template: str = "",
        host: str = "127.0.0.1",
        chunk_size: int = 1000,
    ) -> None:
        if not model_path:
            raise ValueError("Wskaż plik GGUF.")
        self.stop_llama()
        self._runtime = LlamaCppRuntimeManager(
            LlamaCppRuntimeConfig(
                model_path=model_path,
                host=host,
                port=port,
                compute_mode=compute_mode,
                parallel=parallel,
                chat_template=chat_template,
                chunk_size=chunk_size,
            )
        )
        self._runtime.start(wait_for_ready=self._llama_ready_probe(host, port))

    def restart_llama(self) -> None:
        if self._runtime is None:
            raise RuntimeError("Serwer llama.cpp nie jest uruchomiony.")
        model_path = self._runtime.config.model_path
        host = self._runtime.config.host
        port = self._runtime.config.port
        compute_mode = self._runtime.config.compute_mode
        parallel = self._runtime.config.parallel
        chat_template = self._runtime.config.chat_template
        chunk_size = self._runtime.config.chunk_size
        self.stop_llama()
        self.start_llama(
            model_path=model_path,
            host=host,
            port=port,
            compute_mode=compute_mode,
            parallel=parallel,
            chat_template=chat_template,
            chunk_size=chunk_size,
        )

    @staticmethod
    def _llama_ready_probe(host: str, port: int):
        def probe() -> bool:
            request = Request(f"http://{host}:{port}/health", method="GET")
            try:
                with urlopen(request, timeout=1.0) as response:
                    return response.status == 200
            except (OSError, URLError):
                return False

        return probe

    def stop_llama(self) -> None:
        if self._runtime is None:
            return
        runtime = self._runtime
        runtime.stop()
        if runtime.is_running():
            reason = runtime.ownership_error or "llama.cpp nadal działa po próbie zamknięcia"
            raise RuntimeError(reason)
        self._runtime = None

    def close(self) -> None:
        """Zamknij wszystkie zasoby należące do rdzenia aplikacji.

        Shutdown jest idempotentny i best-effort: błąd jednego zasobu nie
        blokuje próby zamknięcia pozostałych.
        """
        try:
            self.stop_llama()
        finally:
            self._translation_cache.close()


__all__ = ["TranslationApp"]
