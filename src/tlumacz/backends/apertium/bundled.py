"""Lokalizacja prywatnego runtime'u Apertium dołączonego do aplikacji."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class BundledRuntime:
    """Ścieżki do samodzielnego runtime'u dostarczonego z aplikacją."""

    root: Path
    executable: Path
    data_dir: Path | None


def locate_bundled_runtime(root: Path | None = None) -> BundledRuntime | None:
    """Znajdź runtime w prywatnym katalogu pakietu, bez modyfikacji systemu.

    Opcjonalny ``root`` ułatwia testowanie i budowanie artefaktów. Produkcyjnie
    katalog ``native_runtime`` jest częścią paczki aplikacji.
    """
    runtime_root = root or Path(__file__).with_name("native_runtime")
    override = os.environ.get("TLUMACZ_APERTIUM_RUNTIME")
    if override and root is None:
        runtime_root = Path(override).expanduser()

    names = ("apertium.exe", "apertium") if os.name == "nt" else ("apertium",)
    executable = next(
        (runtime_root / "bin" / name for name in names if (runtime_root / "bin" / name).is_file()),
        None,
    )
    if executable is None or not os.access(executable, os.X_OK):
        return None

    # Dane językowe nie są częścią bundlowanego runtime’u. Są dostarczane
    # niezależnie jako paczki TAR w magazynie użytkownika.
    return BundledRuntime(runtime_root, executable, None)
