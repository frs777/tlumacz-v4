"""Konfiguracja i limity modułu Apertium."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_EXECUTABLE = "apertium"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_INPUT_BYTES = 256 * 1024
DEFAULT_MAX_OUTPUT_BYTES = 512 * 1024
DEFAULT_MAX_STDERR_BYTES = 32 * 1024


def default_data_dir() -> Path:
    """Zwróć per-user katalog paczek Apertium.

    Paczki językowe są danymi użytkownika, dlatego nie są zapisywane obok
    kodu modułu ani w systemowym ``/usr/share``.
    """
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".config"
    return base / "tlumacz" / "apertium"


@dataclass(frozen=True, slots=True)
class ApertiumConfig:
    """Jawna konfiguracja procesu Apertium.

    ``executable_args`` służy do testowego fake runtime’u i kontrolowanych
    wrapperów; w normalnym użyciu pozostaje puste.
    """

    executable: str = DEFAULT_EXECUTABLE
    data_dir: Path | None = None
    executable_args: tuple[str, ...] = ()
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    max_input_bytes: int = DEFAULT_MAX_INPUT_BYTES
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES
    max_stderr_bytes: int = DEFAULT_MAX_STDERR_BYTES
    text_format: str = "txt"
    environment: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds musi być większe od zera.")
        for name in ("max_input_bytes", "max_output_bytes", "max_stderr_bytes"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} musi być większe od zera.")
        if not self.text_format.strip():
            raise ValueError("text_format nie może być pusty.")
