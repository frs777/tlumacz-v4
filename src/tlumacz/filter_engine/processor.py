"""Document-level orchestration for the V4 Filter Engine."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path

from tlumacz.application.cancellation import CancellationToken
from tlumacz.domain.contracts import BackendResult, FilterContract
from tlumacz.domain.errors import FilterError

from tlumacz.preprocessing import PreprocessDecision, Preprocessor

from .lifecycle import FilterLifecycle
from .marker_validator import MarkerValidator
from .registry import FilterRegistry
from .validator import FilterValidator


class DocumentProcessor:
    """Orchestrate filter lifecycle without knowing a concrete format."""

    def __init__(
        self,
        registry: FilterRegistry,
        *,
        preprocessor: Preprocessor | None = None,
    ) -> None:
        self.registry = registry
        self.preprocessor = preprocessor or Preprocessor()

    def process(
        self,
        input_path: str | Path,
        output_path: str | Path,
        *,
        source_language: str,
        target_language: str,
        translate: Callable[[str], BackendResult] | None = None,
        translate_many: Callable[
            [list[tuple[str, str]], Mapping[str, Mapping[str, object]]],
            dict[str, BackendResult],
        ] | None = None,
        workspace: Path,
        cancellation_token: CancellationToken | None = None,
        on_progress: Callable[[int, int], None] | None = None,
        on_document_info: Callable[[str, int, int], None] | None = None,
        skip_line_patterns: Iterable[str] = (),
    ) -> Path:
        if cancellation_token is not None:
            cancellation_token.raise_if_cancelled()
        if translate is None and translate_many is None:
            raise FilterError("Translation callback is required")
        source = Path(input_path).resolve()
        destination = Path(output_path).resolve()
        if not source.is_file():
            raise FilterError(f"Input document does not exist: {source}")
        workspace.mkdir(parents=True, exist_ok=True)
        self.preprocessor.preflight(source)
        filter_contract = self.registry.for_path(source)
        lifecycle = FilterLifecycle(filter_contract)
        with lifecycle.open(
            source,
            source_language=source_language,
            target_language=target_language,
            workspace=workspace,
        ) as session:
            raw_units = filter_contract.extract(session)
            unit_metadata = {
                str(unit.id): dict(getattr(unit, "metadata", {}) or {})
                for unit in raw_units
                if hasattr(unit, "id")
            }
            units = FilterValidator.validate_units(raw_units)
            capabilities = filter_contract.capabilities()
            document_type = str(capabilities.get("name", source.suffix.lower().lstrip(".")))
            preprocessed = self.preprocessor.classify_units(
                units,
                skip_patterns=skip_line_patterns,
                format_name=document_type,
            )
            filter_skipped = list(getattr(session, "skipped_fragments", ()) or ())
            skipped_ids = {
                item.id for item in preprocessed if item.decision is PreprocessDecision.KEEP
            }
            if on_document_info is not None:
                on_document_info(
                    document_type,
                    len(units),
                    len(filter_skipped) + len(skipped_ids),
                )
            targets: dict[str, str] = {}
            total = len(units)
            if on_progress is not None:
                on_progress(0, total)
            completed = 0
            if translate_many is not None:
                batch = [(unit_id, text) for unit_id, text in units if unit_id not in skipped_ids]
                translated_batch = translate_many(batch, unit_metadata) if batch else {}
                for unit_id, text in units:
                    if cancellation_token is not None:
                        cancellation_token.raise_if_cancelled()
                    MarkerValidator.validate(text)
                    if unit_id in skipped_ids:
                        translated = text
                    else:
                        result = translated_batch.get(unit_id)
                        if result is None:
                            raise FilterError(f"Missing translation result for unit {unit_id!r}")
                        translated = result.text
                    MarkerValidator.validate(translated)
                    targets[unit_id] = translated
                    completed += 1
                    if on_progress is not None:
                        on_progress(completed, total)
            else:
                assert translate is not None
                for unit_id, text in units:
                    if cancellation_token is not None:
                        cancellation_token.raise_if_cancelled()
                    MarkerValidator.validate(text)
                    translated = text if unit_id in skipped_ids else translate(text).text
                    MarkerValidator.validate(translated)
                    targets[unit_id] = translated
                    completed += 1
                    if on_progress is not None:
                        on_progress(completed, total)
            FilterValidator.validate_targets(units, targets)
            return filter_contract.write(session, targets, destination)


__all__ = ["DocumentProcessor", "FilterContract"]
