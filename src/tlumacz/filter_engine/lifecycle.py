"""Session lifecycle for format filters."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from tlumacz.domain.contracts import FilterContract


class FilterLifecycle:
    """Own one filter session and guarantee deterministic cleanup."""

    def __init__(self, filter_contract: FilterContract) -> None:
        self._filter = filter_contract

    def open(
        self,
        input_path: Path,
        *,
        source_language: str,
        target_language: str,
        workspace: Path,
    ) -> FilterSessionContext:
        session = self._filter.open(
            input_path,
            source_language=source_language,
            target_language=target_language,
            workspace=workspace,
        )
        return FilterSessionContext(self._filter, session)


class FilterSessionContext:
    """Context manager that closes a successfully opened filter session once."""

    def __init__(self, filter_contract: FilterContract, session: Any) -> None:
        self._filter = filter_contract
        self._session = session
        self._closed = False

    @property
    def session(self) -> Any:
        return self._session

    def __enter__(self) -> Any:
        return self._session

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> Literal[False]:
        self.close()
        return False

    def close(self) -> None:
        if self._closed:
            return
        self._filter.close(self._session)
        self._closed = True
