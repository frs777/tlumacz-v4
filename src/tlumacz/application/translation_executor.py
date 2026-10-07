"""Execute translation units with bounded concurrency."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass

from tlumacz.application.cancellation import CancellationToken
from tlumacz.domain.contracts import BackendResult


@dataclass(frozen=True, slots=True)
class TranslationResult:
    id: str
    source: str
    target: str
    backend_result: BackendResult


class TranslationExecutor:
    """Execute independent translation units while preserving input order."""

    def __init__(self, max_workers: int = 1) -> None:
        if max_workers <= 0:
            raise ValueError("max_workers musi być dodatnie")
        self.max_workers = max_workers

    def execute_batch(
        self,
        units: Iterable[tuple[str, str, str]],
        *,
        translate_batch: Callable[[list[tuple[str, str, str]]], Mapping[str, BackendResult]],
        cancellation_token: CancellationToken | None = None,
    ) -> list[TranslationResult]:
        """Wykonaj cały logiczny chunk jako jeden request transportowy."""
        normalized = [
            (str(unit_id), str(source), str(source_language))
            for unit_id, source, source_language in units
        ]
        if any(not unit_id for unit_id, _, _ in normalized):
            raise ValueError("Jednostka musi mieć niepuste id")
        if cancellation_token is not None:
            cancellation_token.raise_if_cancelled()
        if not normalized:
            return []

        translated = dict(translate_batch(normalized))
        expected_ids = {unit_id for unit_id, _, _ in normalized}
        actual_ids = set(translated)
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        if missing:
            raise ValueError(f"Odpowiedź batcha ma brakujące jednostki: {sorted(missing)!r}")
        if extra:
            raise ValueError(f"Odpowiedź batcha ma nieznane jednostki: {sorted(extra)!r}")

        return [
            TranslationResult(
                id=unit_id,
                source=source,
                target=translated[unit_id].text,
                backend_result=translated[unit_id],
            )
            for unit_id, source, _ in normalized
        ]

    def execute(
        self,
        units: Iterable[tuple[str, str, str]],
        *,
        translate: Callable[[str, str], BackendResult],
        cancellation_token: CancellationToken | None = None,
    ) -> list[TranslationResult]:
        normalized = [
            (str(unit_id), str(source), str(source_language))
            for unit_id, source, source_language in units
        ]
        if any(not unit_id for unit_id, _, _ in normalized):
            raise ValueError("Jednostka musi mieć niepuste id")
        if cancellation_token is not None:
            cancellation_token.raise_if_cancelled()

        if not normalized:
            return []

        results: list[TranslationResult | None] = [None] * len(normalized)
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures: dict[Future[BackendResult], int] = {
                pool.submit(translate, source, source_language): index
                for index, (_, source, source_language) in enumerate(normalized)
            }
            try:
                for future, index in tuple(futures.items()):
                    if cancellation_token is not None:
                        cancellation_token.raise_if_cancelled()
                    backend_result = future.result()
                    unit_id, source, _ = normalized[index]
                    results[index] = TranslationResult(
                        id=unit_id,
                        source=source,
                        target=backend_result.text,
                        backend_result=backend_result,
                    )
            except BaseException:
                for future in futures:
                    future.cancel()
                raise

        return [result for result in results if result is not None]


__all__ = ["TranslationExecutor", "TranslationResult"]
