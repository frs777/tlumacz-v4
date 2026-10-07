"""Inicjalizacja prywatnej struktury konfiguracji użytkownika Tłumacza."""

from __future__ import annotations

import shutil
from pathlib import Path

USER_CONFIG_DIR = Path.home() / ".config" / "tlumacz"
RUNTIME_DIRECTORIES = ("skills", "filters", "apertium", "logs")
CONFIG_FILES = ("config.json", "llama.json", "cloud_models.json")


def _template_dir() -> Path:
    """Zwróć źródło wzorców, bez odwoływania się do aktywnego profilu użytkownika."""
    source_templates = Path(__file__).resolve().parents[2] / "config"
    if source_templates.is_dir():
        return source_templates
    package_templates = Path(__file__).with_name("resources") / "default-config"
    if package_templates.is_dir():
        return package_templates
    raise FileNotFoundError("Nie znaleziono wzorców konfiguracji Tłumacza.")


def initialize_user_config(config_dir: Path = USER_CONFIG_DIR) -> Path:
    """Utwórz strukturę użytkownika i skopiuj brakujące wzorce konfiguracji."""
    config_dir.mkdir(parents=True, exist_ok=True)
    for name in RUNTIME_DIRECTORIES:
        (config_dir / name).mkdir(parents=True, exist_ok=True)

    templates = _template_dir()
    for name in CONFIG_FILES:
        source = templates / name
        target = config_dir / name
        if not source.is_file():
            raise FileNotFoundError(f"Brak wzorca konfiguracji: {source}")
        if not target.exists():
            shutil.copyfile(source, target)
    return config_dir


__all__ = ["CONFIG_FILES", "RUNTIME_DIRECTORIES", "USER_CONFIG_DIR", "initialize_user_config"]
