"""Public document translation service."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
import logging

from tlumacz.backends.llama_cpp.language_routing import LlamaCppLanguageRouting
from tlumacz.domain.contracts import BackendResult

from ..filter_engine.processor import DocumentProcessor
from ..filter_engine.registry import FilterRegistry
from .cancellation import CancellationToken
from .language_routing import ApertiumLanguageRouting
from .translation_orchestrator import TranslationOrchestrator

logger = logging.getLogger("tlumacz.application.document_translation_service")


class DocumentTranslationService:
    """Translate documents without exposing filter or provider details."""

    def __init__(
        self,
        *,
        registry: FilterRegistry,
        translate: Callable[[str, str], BackendResult],
        translate_batch: Callable[[list[tuple[str, str, str]], str], dict[str, BackendResult]] | None = None,
        max_chars: int,
        max_workers: int = 1,
        language_routing: ApertiumLanguageRouting | LlamaCppLanguageRouting | None = None,
    ) -> None:
        self.processor = DocumentProcessor(registry)
        self.translate = translate
        self.translate_batch = translate_batch
        self.orchestrator = TranslationOrchestrator(
            max_chars=max_chars,
            max_workers=max_workers,
        )
        self.language_routing = language_routing

    def translate_file(
        self,
        input_path: str | Path,
        output_path: str | Path,
        *,
        source_language: str,
        target_language: str,
        workspace: Path,
        cancellation_token: CancellationToken | None = None,
        on_progress: Callable[[int, int], None] | None = None,
        on_document_info: Callable[[str, int, int], None] | None = None,
        on_chunk_start: Callable[[int, int], None] | None = None,
        on_chunk_complete: Callable[[int, int, int], None] | None = None,
        skip_line_patterns: Iterable[str] = (),
    ) -> Path:
        logger.debug(
            "Rozpoczęto przetwarzanie dokumentu: wejście=%s, wyjście=%s, źródło=%s, cel=%s",
            input_path,
            output_path,
            source_language,
            target_language,
        )
        translate_batch = self.translate_batch

        def translate_many(
            units: list[tuple[str, str]],
            unit_metadata: Mapping[str, Mapping[str, object]],
        ) -> dict[str, BackendResult]:
            results = self.orchestrator.translate_units(
                units,
                source_language=source_language,
                target_language=target_language,
                translate=self.translate,
                translate_batch=(
                    (lambda batch: translate_batch(batch, target_language))
                    if translate_batch is not None
                    else None
                ),
                unit_metadata=unit_metadata,
                language_routing=self.language_routing,
                cancellation_token=cancellation_token,
                on_progress=on_progress,
                on_chunk_start=on_chunk_start,
                on_chunk_complete=on_chunk_complete,
            )
            return {result.id: result.backend_result for result in results}

        result = self.processor.process(
            input_path,
            output_path,
            source_language=source_language,
            target_language=target_language,
            translate_many=translate_many,
            workspace=workspace,
            cancellation_token=cancellation_token,
            on_progress=on_progress,
            on_document_info=on_document_info,
            skip_line_patterns=skip_line_patterns,
        )
        logger.debug("Zakończono przetwarzanie dokumentu: wynik=%s", result)
        return result


__all__ = ["DocumentTranslationService"]
