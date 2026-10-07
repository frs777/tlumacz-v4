"""Niezależna warstwa przygotowania dokumentu przed Filter Engine."""

from .preprocessor import (
    DEFAULT_SKIP_PATTERNS,
    MARKDOWN_SKIP_PATTERNS,
    PreflightPath,
    PreflightResult,
    PreprocessDecision,
    PreprocessedUnit,
    Preprocessor,
)

__all__ = [
    "DEFAULT_SKIP_PATTERNS",
    "MARKDOWN_SKIP_PATTERNS",
    "PreprocessDecision",
    "PreflightPath",
    "PreflightResult",
    "PreprocessedUnit",
    "Preprocessor",
]
