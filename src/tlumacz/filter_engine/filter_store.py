"""Jedyny magazyn pakietów filtrów użytkownika oraz ich runtime tymczasowy."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from .tplugin import TPluginArchive


class FilterStore:
    """Źródło pakietów filtrów i jednorazowy katalog ich rozpakowania.

    Trwałe pakiety znajdują się wyłącznie w ``$HOME/.config/tlumacz/filters``. Jeżeli
    aplikacja otrzyma paczki ``.tplugin``, rozpakowuje je do ``/tmp/filters``;
    nie tworzy drugiego trwałego magazynu runtime.
    """

    @staticmethod
    def default_path() -> Path:
        """Zwróć domyślny magazyn filtrów zgodny z konfiguracją XDG."""
        xdg = os.environ.get("XDG_CONFIG_HOME", "").strip()
        base = Path(xdg).expanduser() if xdg else Path.home() / ".config"
        return base / "tlumacz" / "filters"
    TEMP_ROOT = Path("/tmp/filters")

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self._runtime_temp: tempfile.TemporaryDirectory[str] | None = None
        self._runtime_path: Path | None = None

    @classmethod
    def default(cls) -> "FilterStore":
        """Zwróć jedyny trwały magazyn filtrów użytkownika."""
        configured = os.environ.get("TLUMACZ_FILTER_STORE", "").strip()
        return cls(configured) if configured else cls(cls.default_path())

    @classmethod
    def user_config(cls) -> "FilterStore":
        """Zwróć jedyny trwały magazyn filtrów użytkownika."""
        return cls(cls.default_path())

    def ensure_exists(self) -> Path:
        """Utwórz trwały magazyn pakietów, jeśli nie istnieje."""
        self.path.mkdir(parents=True, exist_ok=True)
        return self.path

    def runtime_path(self) -> Path:
        """Przygotuj jednorazowy runtime filtrów w ``/tmp/filters``.

        Rozpakowane katalogi i paczki z magazynu są kopiowane do izolowanego
        katalogu procesu. Trwały magazyn użytkownika pozostaje nietknięty.
        """
        if self._runtime_path is not None:
            return self._runtime_path
        self.ensure_exists()
        self.TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        self._runtime_temp = tempfile.TemporaryDirectory(
            prefix="tlumacz-",
            dir=self.TEMP_ROOT,
        )
        runtime = Path(self._runtime_temp.name)
        for entry in sorted(self.path.iterdir()):
            if entry.is_dir():
                shutil.copytree(entry, runtime / entry.name)
                continue
            if entry.is_file() and entry.suffix.lower() == ".tplugin":
                TPluginArchive.extract(entry, runtime)
        self._runtime_path = runtime
        return runtime

    def close(self) -> None:
        """Usuń tymczasowy runtime filtrów."""
        if self._runtime_temp is not None:
            self._runtime_temp.cleanup()
            self._runtime_temp = None
            self._runtime_path = None

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


__all__ = ["FilterStore"]
