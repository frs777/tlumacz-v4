"""Koordynacja chunkowania, detekcji języka, cache i walidacji wyników."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable, Mapping

from tlumacz.backends.llama_cpp.language_routing import LlamaCppLanguageRouting
from tlumacz.domain.contracts import BackendResult
from tlumacz.filter_engine.inline_code_protection import (
    ProtectedInlineText,
    protect_inline_codes,
    restore_inline_codes,
)

from .cancellation import CancellationToken
from .chunk_planner import ChunkPlanner
from .language_routing import ApertiumLanguageRouting
from .prompt_builder import PromptBuilder
from .result_validator import ResultValidator
from .translation_cache import TranslationCache
from .translation_executor import TranslationExecutor, TranslationResult

logger = logging.getLogger("tlumacz.application.translation_orchestrator")


class TranslationOrchestrator:
    """Koordynuje tłumaczenie bez znajomości formatu dokumentu i dostawcy."""

    def __init__(
        self,
        *,
        max_chars: int,
        max_workers: int = 1,
        cache: TranslationCache | None = None,
    ) -> None:
        self.planner = ChunkPlanner(max_chars=max_chars)
        self.executor = TranslationExecutor(max_workers=max_workers)
        self.cache = cache
        self.validator = ResultValidator()

    def translate_units(
        self,
        units: Iterable[tuple[str, str]],
        *,
        source_language: str,
        target_language: str,
        translate: Callable[[str, str], BackendResult],
        translate_batch: Callable[[list[tuple[str, str, str]]], dict[str, BackendResult]] | None = None,
        unit_metadata: Mapping[str, Mapping[str, object]] | None = None,
        language_routing: ApertiumLanguageRouting | LlamaCppLanguageRouting | None = None,
        cancellation_token: CancellationToken | None = None,
        on_progress: Callable[[int, int], None] | None = None,
        on_chunk_start: Callable[[int, int], None] | None = None,
        on_chunk_complete: Callable[[int, int, int], None] | None = None,
        model: str = "default",
        temperature: float = 0.0,
        skill_text: str = "",
    ) -> list[TranslationResult]:
        normalized = tuple((str(unit_id), str(source)) for unit_id, source in units)
        logger.debug(
            "Rozpoczęto orkiestrację tłumaczenia: jednostek=%d, źródło=%s, cel=%s",
            len(normalized),
            source_language,
            target_language,
        )
        unit_ids = [unit_id for unit_id, _ in normalized]
        if len(unit_ids) != len(set(unit_ids)):
            raise ValueError("Identyfikatory jednostek muszą być unikalne.")
        prompt_builder = PromptBuilder(target_language=target_language)
        system_prompt = prompt_builder.system_prompt()
        results: list[TranslationResult | None] = [None] * len(normalized)
        index_by_id = {unit_id: index for index, (unit_id, _) in enumerate(normalized)}
        completed = 0
        completed_characters = 0

        def report_progress() -> None:
            if on_progress is not None:
                on_progress(completed, len(normalized))

        frozen_source = source_language
        if isinstance(language_routing, ApertiumLanguageRouting):
            resolved_source = language_routing.resolve_document_source(
                [text for _, text in normalized],
                configured_source=source_language,
            )
            if resolved_source is None:
                raise ValueError("Nie udało się wykryć języka dokumentu.")
            frozen_source = resolved_source

        resolved_sources: dict[str, str] = {}
        skipped_sources: set[str] = set()
        if isinstance(language_routing, LlamaCppLanguageRouting):
            for unit_id, text in normalized:
                resolved = self._resolve_chunk_source(
                    text,
                    configured_source=source_language,
                    frozen_source=frozen_source,
                    language_routing=language_routing,
                )
                if resolved is None:
                    skipped_sources.add(unit_id)
                else:
                    resolved_sources[unit_id] = resolved
        else:
            for unit_id, text in normalized:
                resolved = self._resolve_chunk_source(
                    text,
                    configured_source=source_language,
                    frozen_source=frozen_source,
                    language_routing=language_routing,
                )
                if resolved is None:
                    skipped_sources.add(unit_id)
                else:
                    resolved_sources[unit_id] = resolved

        for unit_id in skipped_sources:
            index = index_by_id[unit_id]
            source_text = normalized[index][1]
            skipped = BackendResult(
                text=source_text,
                source_language=frozen_source,
                target_language=target_language,
                metadata={"language_detection": "skipped"},
            )
            results[index] = TranslationResult(unit_id, source_text, source_text, skipped)
            completed += 1
            report_progress()

        planned_units = [unit for unit in normalized if unit[0] not in skipped_sources]
        plan = self.planner.plan(
            planned_units,
            unit_metadata=unit_metadata,
            source_languages=resolved_sources,
        )
        completed_characters = 0

        for chunk_index, chunk in enumerate(plan.chunks, start=1):
            logger.debug(
                "Rozpoczęto chunk: numer=%d/%d, jednostek=%d, znaków=%d",
                chunk_index,
                len(plan.chunks),
                len(chunk),
                sum(len(unit.source) for unit in chunk),
            )
            if cancellation_token is not None:
                cancellation_token.raise_if_cancelled()
            if on_chunk_start is not None:
                on_chunk_start(chunk_index, len(plan.chunks))

            misses: list[tuple[str, str, str]] = []
            chunk_characters = sum(len(unit.source) for unit in chunk)
            for unit in chunk:
                chunk_source = unit.source_language
                if chunk_source is None:
                    raise ValueError(f"Brak ustalonego języka źródłowego dla jednostki {unit.id!r}")

                cached = (
                    self.cache.get(
                        unit.source,
                        system_prompt,
                        skill_text,
                        model,
                        temperature,
                        source_language=chunk_source,
                    )
                    if self.cache is not None
                    else None
                )
                if cached is None:
                    misses.append((unit.id, unit.source, chunk_source))
                    continue

                backend_result = BackendResult(
                    text=cached,
                    source_language=chunk_source,
                    target_language=target_language,
                    metadata={"cache": "hit"},
                )
                validated = self.validator.validate(
                    unit.source,
                    backend_result,
                    expected_source_language=chunk_source,
                    expected_target_language=target_language,
                )
                results[index_by_id[unit.id]] = TranslationResult(
                    unit.id,
                    unit.source,
                    validated.text,
                    validated,
                )
                completed += 1
                report_progress()

            if not misses:
                completed_characters += chunk_characters
                if on_chunk_complete is not None:
                    on_chunk_complete(chunk_index, len(plan.chunks), completed_characters)
                continue

            expected_source_by_id = {unit_id: source_language for unit_id, _, source_language in misses}
            original_source_by_id = {unit_id: text for unit_id, text, _ in misses}
            protected_by_id: dict[str, ProtectedInlineText] = {
                unit_id: protect_inline_codes(text)
                for unit_id, text, _ in misses
            }
            protected_misses = [
                (unit_id, protected_by_id[unit_id].text, source_language)
                for unit_id, _, source_language in misses
            ]

            if translate_batch is not None:
                translated = self._execute_batch_with_retry(
                    protected_misses,
                    translate_batch=translate_batch,
                    translate=translate,
                    cancellation_token=cancellation_token,
                )
            else:
                translated = self.executor.execute(
                    protected_misses,
                    translate=translate,
                    cancellation_token=cancellation_token,
                )

            for item in translated:
                restored_text = restore_inline_codes(
                    item.backend_result.text,
                    protected_by_id[item.id],
                )
                backend_result = BackendResult(
                    text=restored_text,
                    source_language=item.backend_result.source_language,
                    target_language=item.backend_result.target_language,
                    metadata=dict(item.backend_result.metadata),
                )
                original_source = original_source_by_id[item.id]
                validated = self.validator.validate(
                    original_source,
                    backend_result,
                    expected_source_language=expected_source_by_id[item.id],
                    expected_target_language=target_language,
                )
                resolved_source_language = validated.source_language
                if resolved_source_language is None:
                    raise ValueError("Wynik tłumaczenia nie zawiera języka źródłowego.")
                if self.cache is not None:
                    self.cache.put(
                        original_source,
                        system_prompt,
                        skill_text,
                        model,
                        temperature,
                        validated.text,
                        source_language=resolved_source_language,
                    )
                results[index_by_id[item.id]] = TranslationResult(
                    item.id,
                    original_source,
                    validated.text,
                    validated,
                )
                completed += 1
                report_progress()

            completed_characters += chunk_characters
            if on_chunk_complete is not None:
                on_chunk_complete(chunk_index, len(plan.chunks), completed_characters)

        if any(result is None for result in results):
            raise RuntimeError("Tłumaczenie zakończyło się bez wyniku dla jednej lub większej liczby jednostek.")
        logger.debug("Zakończono orkiestrację tłumaczenia: jednostek=%d", len(results))
        return [result for result in results if result is not None]

    def _execute_batch_with_retry(
        self,
        units: list[tuple[str, str, str]],
        *,
        translate_batch: Callable[[list[tuple[str, str, str]]], dict[str, BackendResult]],
        translate: Callable[[str, str], BackendResult],
        cancellation_token: CancellationToken | None,
    ) -> list[TranslationResult]:
        """Ponów cały chunk raz, zanim zostanie użyty fallback jednostkowy."""
        last_error: RuntimeError | ValueError | None = None
        for _attempt in range(2):
            try:
                return self.executor.execute_batch(
                    units,
                    translate_batch=translate_batch,
                    cancellation_token=cancellation_token,
                )
            except (RuntimeError, ValueError) as exc:
                last_error = exc
        if last_error is None:
            raise RuntimeError("Batch nie zwrócił wyniku.")
        # Po dwóch nieudanych próbach całego chunka przechodzimy do
        # kontrolowanego fallbacku jednostkowego.
        return self.executor.execute(
            units,
            translate=translate,
            cancellation_token=cancellation_token,
        )

    @staticmethod
    def _resolve_chunk_source(
        text: str,
        *,
        configured_source: str,
        frozen_source: str,
        language_routing: ApertiumLanguageRouting | LlamaCppLanguageRouting | None,
    ) -> str | None:
        if isinstance(language_routing, ApertiumLanguageRouting):
            return language_routing.resolve_chunk_source(
                text,
                frozen_source=frozen_source,
            )
        if isinstance(language_routing, LlamaCppLanguageRouting):
            return language_routing.resolve_chunk_source(
                text,
                fallback_source=configured_source,
            )
        return configured_source


__all__ = ["TranslationOrchestrator"]
