"""Błędy modułu Apertium."""

from __future__ import annotations


class ApertiumError(RuntimeError):
    """Bazowy błąd adaptera Apertium."""


class ApertiumUnavailableError(ApertiumError):
    """Runtime lub wymagana para językowa nie są dostępne."""


class ApertiumTimeoutError(ApertiumError):
    """Proces Apertium przekroczył limit czasu."""


class ApertiumOutputLimitError(ApertiumError):
    """Proces Apertium wygenerował wynik większy od dozwolonego limitu."""


class ApertiumValidationError(ApertiumError):
    """Wejście lub wynik Apertium nie spełnia kontraktu modułu."""
