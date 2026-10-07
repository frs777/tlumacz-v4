"""Stable domain contracts for V4 integrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class BackendResult:
    """Normalized result returned by a translation backend."""

    text: str
    source_language: str | None = None
    target_language: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BackendConfiguration:
    """Nieprzezroczysta konfiguracja konkretnego backendu.

    Wspólny pipeline zna wyłącznie kontener wartości. Konkretne adaptery
    interpretują własne klucze, dzięki czemu dodanie backendu nie rozszerza
    wspólnego kontraktu o kolejne pola.
    """

    values: Mapping[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)


@dataclass(frozen=True, slots=True)
class BackendCapabilities:
    """Deklaratywne możliwości opcjonalnego backendu."""

    batch_translation: bool = False
    cancellation: bool = False
    health_check: bool = True


@runtime_checkable
class TranslationBackend(Protocol):
    """Port implemented by every translation backend."""

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
    ) -> BackendResult:
        """Translate text and return a normalized result."""

    def health_check(self) -> HealthCheckResult:
        """Report backend availability without changing application state."""


@runtime_checkable
class FilterContract(Protocol):
    """Port for format-specific extraction and writing."""

    def capabilities(self) -> Any: ...
    def probe(self, input_path: Path) -> bool: ...
    def open(
        self,
        input_path: Path,
        *,
        source_language: str,
        target_language: str,
        workspace: Path,
    ) -> Any: ...
    def extract(self, session: Any) -> list[Any]: ...
    def write(self, session: Any, targets: dict[str, str], output_path: Path) -> Path: ...
    def close(self, session: Any) -> None: ...


@runtime_checkable
class DocumentContract(Protocol):
    """Port for document formats that do not use the filter engine."""

    def read(self, path: Path) -> str: ...
    def write(self, path: Path, content: str) -> Path: ...
    def supported(self, path: Path) -> bool: ...


@dataclass(frozen=True, slots=True)
class InlineCode:
    """Immutable protected inline-code span."""

    value: str
    start: int
    end: int

    @property
    def span(self) -> tuple[int, int]:
        return self.start, self.end


@dataclass(frozen=True, slots=True)
class HealthCheckResult:
    """Explicit health-check outcome."""

    name: str
    healthy: bool
    error: str | None = None

    @classmethod
    def ok(cls, name: str) -> HealthCheckResult:
        return cls(name=name, healthy=True)

    @classmethod
    def failed(cls, name: str, error: str) -> HealthCheckResult:
        return cls(name=name, healthy=False, error=error)


@dataclass(frozen=True, slots=True)
class Session:
    """Filesystem scope for one translation operation."""

    session_id: str
    root: Path


@dataclass(slots=True)
class Workspace:
    """Root filesystem scope that owns translation sessions."""

    root: Path

    @classmethod
    def create(cls, root: Path) -> Workspace:
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        return cls(root=root)

    def create_session(self, session_id: str) -> Session:
        if (
            not session_id
            or session_id in {".", ".."}
            or "/" in session_id
            or "\\" in session_id
        ):
            raise ValueError("session_id must be a non-empty path-safe identifier")
        session_root = self.root / "sessions" / session_id
        session_root.mkdir(parents=True, exist_ok=True)
        return Session(session_id=session_id, root=session_root)
