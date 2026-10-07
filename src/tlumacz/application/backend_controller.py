"""Backend selection and health state for the GUI layer."""

from __future__ import annotations

from collections.abc import Iterable


class BackendController:
    """Keep backend selection independent from Qt and concrete implementations."""

    def __init__(self, supported_backends: Iterable[str]) -> None:
        backends = tuple(dict.fromkeys(str(item) for item in supported_backends))
        if not backends:
            raise ValueError("Musi istnieć co najmniej jeden backend.")
        self._supported = backends
        self._selected = backends[0]
        self._health: dict[str, bool] = {}

    @property
    def supported(self) -> tuple[str, ...]:
        return self._supported

    @property
    def selected(self) -> str:
        return self._selected

    def select(self, backend: str) -> None:
        if backend not in self._supported:
            raise ValueError(f"Nieznany backend: {backend!r}")
        self._selected = backend

    def set_health(self, backend: str, healthy: bool) -> None:
        if backend not in self._supported:
            raise ValueError(f"Nieznany backend: {backend!r}")
        self._health[backend] = bool(healthy)

    def is_healthy(self, backend: str | None = None) -> bool:
        name = backend or self._selected
        return self._health.get(name, False)


__all__ = ["BackendController"]
