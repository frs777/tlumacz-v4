"""Apertium backend components."""

from .adapter import ApertiumAdapter
from .backend import ApertiumBackend
from .config import ApertiumConfig
from .runtime import ApertiumRuntime

__all__ = [
    "ApertiumAdapter",
    "ApertiumBackend",
    "ApertiumConfig",
    "ApertiumRuntime",
]
