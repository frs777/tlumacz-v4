"""Format-to-filter registry for the V4 Filter Engine."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from tlumacz.domain.contracts import FilterContract
from tlumacz.domain.errors import FilterError

from .filter_store import FilterStore
from .filters.markdown import MarkdownFilter
from .filters.okapi import OkapiFilter
from .filters.plain_text import PlainTextFilter


class FilterRegistry:
    """Resolve a filter implementation from a document suffix."""

    def __init__(self, *, filter_store: Path | None = None) -> None:
        self._filters: dict[str, Callable[[], FilterContract]] = {}
        self._auto_registered_suffixes: set[str] = set()
        self._native_registered_suffixes: set[str] = set()
        self._filter_store = FilterStore(filter_store) if filter_store is not None else FilterStore.default()
        self._runtime_store = self._filter_store.runtime_path()
        self._register_native_text_filters()
        self._discover_tplugins()
        self._restore_native_markdown_path()

    def _register_native_text_filters(self) -> None:
        """Zarejestruj natywne fallbacki tylko dla formatów bez Okapi."""
        markdown_suffixes = (".md", ".markdown")
        self.register_lazy(markdown_suffixes, MarkdownFilter)
        self._native_registered_suffixes.update(markdown_suffixes)
        self.register_lazy(PlainTextFilter._SUFFIXES, PlainTextFilter)
        self._native_registered_suffixes.update(PlainTextFilter._SUFFIXES)

    def _restore_native_markdown_path(self) -> None:
        """Utrzymaj Markdown na natywnej ścieżce tekstowej V4.

        Markdown jest prostym formatem tekstowym z własną składnią, dla którego
        nie uruchamiamy Okapi. Nawet pozostałość starego pluginu markdown
        w magazynie runtime nie może przejąć rozszerzeń .md/.markdown.
        """
        markdown_suffixes = (".md", ".markdown")
        self.register_lazy(markdown_suffixes, MarkdownFilter)
        self._native_registered_suffixes.update(markdown_suffixes)

    @property
    def filter_store(self) -> Path:
        """Zwróć katalog magazynu filtrów używany przez rejestr."""
        return self._filter_store.path

    def _discover_tplugins(self) -> None:
        """Odkryj wyłącznie rozpakowane pluginy TPlugin z magazynu runtime."""
        root = self._runtime_store
        if not root.is_dir():
            return
        for package in sorted(path for path in root.iterdir() if path.is_dir()):
            manifest_path = package / "plugin.json"
            if not manifest_path.is_file():
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if manifest.get("format") != "tplugin" or int(manifest.get("format_version", 0)) != 1:
                    continue
                plugin_id = str(manifest.get("id", package.name)).strip()
                extensions = tuple(
                    str(value).strip().lower() for value in manifest.get("extensions", ()) if str(value).strip()
                )
                if not extensions:
                    continue
                factory = self._factory_for_plugin(plugin_id, extensions, self._runtime_store)
                self.register_lazy(extensions, factory)
                self._auto_registered_suffixes.update(self._normalize_suffix(suffix) for suffix in extensions)
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                continue

    @staticmethod
    def _factory_for_plugin(
        plugin_id: str, extensions: tuple[str, ...], runtime_store: Path
    ) -> Callable[[], FilterContract]:
        return lambda: OkapiFilter(plugin_id, extensions, filter_store=runtime_store)

    def register(self, suffixes: tuple[str, ...], filter_contract: FilterContract) -> None:
        """Zarejestruj istniejącą implementację filtra dla zgodności wstecznej.

        Ta metoda zachowuje referencję do przekazanego obiektu. Kod aplikacji
        powinien używać :meth:`register_lazy`, aby instancja filtra powstawała
        dopiero po rozpoznaniu rozszerzenia dokumentu.
        """
        if not isinstance(filter_contract, FilterContract):
            raise FilterError("Registered object does not implement FilterContract")
        self.register_lazy(suffixes, lambda: filter_contract)

    def register_lazy(
        self,
        suffixes: tuple[str, ...],
        factory: Callable[[], FilterContract],
    ) -> None:
        """Zarejestruj fabrykę filtra bez tworzenia jego instancji.

        Fabryka jest wywoływana dopiero przez ``for_path()`` dla dokumentu
        korzystającego z danego rozszerzenia. Rejestr nie przechowuje
        utworzonej instancji.
        """
        if not callable(factory):
            raise FilterError("Filter factory must be callable")
        normalized = tuple(self._normalize_suffix(suffix) for suffix in suffixes)
        for suffix in normalized:
            if (
                suffix in self._filters
                and suffix not in self._auto_registered_suffixes
                and suffix not in self._native_registered_suffixes
            ):
                raise FilterError(f"Filter suffix {suffix!r} is already registered")
        for suffix in normalized:
            if suffix in self._auto_registered_suffixes or suffix in self._native_registered_suffixes:
                del self._filters[suffix]
                self._auto_registered_suffixes.discard(suffix)
                self._native_registered_suffixes.discard(suffix)
        for suffix in normalized:
            self._filters[suffix] = factory

    def for_path(self, input_path: str | Path) -> FilterContract:
        suffix = self._normalize_suffix(Path(input_path).suffix)
        try:
            factory = self._filters[suffix]
        except KeyError as exc:
            raise FilterError(f"No filter registered for suffix {suffix or '<none>'}") from exc
        filter_contract = factory()
        if not isinstance(filter_contract, FilterContract):
            raise FilterError(f"Filter factory for suffix {suffix!r} returned invalid object")
        return filter_contract

    def suffixes(self) -> tuple[str, ...]:
        return tuple(sorted(self._filters))

    @staticmethod
    def _normalize_suffix(suffix: str) -> str:
        normalized = suffix.strip().lower()
        if not normalized:
            raise FilterError("Filter suffix cannot be empty")
        if not normalized.startswith("."):
            normalized = f".{normalized}"
        if normalized == ".":
            raise FilterError("Filter suffix cannot be empty")
        return normalized
