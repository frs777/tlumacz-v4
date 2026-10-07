"""Trwała konfiguracja GUI QML V4 bez zależności od Qt Widgets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

CONFIG_DIR = Path.home() / ".config" / "tlumacz"
CONFIG_PATH = CONFIG_DIR / "config.json"


LOCAL_SERVER_HOSTS = {"127.0.0.1", "localhost", "::1"}


def normalize_local_server_host(value: str) -> str:
    """Zezwól wbudowanemu serwerowi wyłącznie na adres pętli zwrotnej."""
    host = value.strip()
    if host not in LOCAL_SERVER_HOSTS:
        raise ValueError(
            "Wbudowany serwer llama.cpp może nasłuchiwać wyłącznie na "
            "127.0.0.1, localhost lub ::1."
        )
    return host


def cloud_models_config() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parent.parent / "resources" / "default-config" / "cloud_models.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("cloud_models", []))


CLOUD_MODELS_CONFIG = cloud_models_config()


def normalize_local_file_path(value: str) -> str:
    """Zamień QML-owy URL file:// na lokalną ścieżkę pliku."""
    value = value.strip()
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme == "file":
        if parsed.netloc not in {"", "localhost"}:
            raise ValueError(f"Nieobsługiwany host URL pliku: {parsed.netloc}")
        return unquote(parsed.path)
    return value


@dataclass(slots=True)
class AppSettings:
    backend_type: str = "llama"
    base_url: str = "http://127.0.0.1:18080/v1"
    custom_server_url: str = ""
    api_key: str = ""
    last_local_api_key: str = ""
    model: str = "local"
    cloud_profiles: dict[str, dict[str, Any]] = field(default_factory=dict)
    enabled_skills: list[str] | None = None
    cloud_profile: str = "ChatGPT"
    mozhi_instance: str = "auto"
    mozhi_engine: str = "duckduckgo"
    server_host: str = "127.0.0.1"
    server_port: int = 18080
    server_gguf_path: str = ""
    last_input_path: str = ""
    last_output_path: str = ""
    server_compute_mode: str = "gpu"
    server_chat_template: str = ""
    server_parallel: int = 1
    auto_start_server: bool = False
    cache_clear_after_translation: bool = False
    restart_llama_after_translation: bool = False
    restart_apertium_after_translation: bool = False
    reconnect_cloud_after_translation: bool = False
    chunk_size: int = 2000
    temperature: float = 0.1
    target_language: str = "pl"
    source_language: str = "auto"
    glossary_path: str = ""
    system_prompt: str = ""
    skip_line_patterns: list[str] = field(
        default_factory=lambda: [
            r"^\s*---\s*$",
            r"^\s*\*(name|license|author|metadata|version|tags|created|updated)\s*",
        ]
    )
    theme: str = "system"
    language: str = "pl"
    window_x: int = -1
    window_y: int = -1
    window_width: int = 1120
    window_height: int = 780

    def normalized_cloud_profile(self) -> dict[str, Any]:
        selected = self.cloud_profile
        profile = dict(self.cloud_profiles.get(selected, {}))
        if not profile:
            for item in CLOUD_MODELS_CONFIG:
                if item.get("name") == selected:
                    profile = dict(item)
                    break
        return profile


def load_settings(path: Path = CONFIG_PATH) -> AppSettings:
    """Wczytaj wszystkie trwałe ustawienia aplikacji z jednego config.json."""
    if not path.is_file():
        return AppSettings()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return AppSettings()

    valid = {field.name for field in AppSettings.__dataclass_fields__.values()}
    values = {key: value for key, value in data.items() if key in valid}
    if "server_gguf_path" in values:
        values["server_gguf_path"] = normalize_local_file_path(
            str(values["server_gguf_path"])
        )

    # Migracja starej wspólnej flagi restartu: jej znaczenie zależało
    # wcześniej od aktualnie wybranego backendu, więc przenosimy ją tylko
    # do właściwego, nowego ustawienia backendowego.
    legacy_restart = data.get("restart_after_translation")
    if legacy_restart is not None:
        backend = values.get("backend_type", "llama")
        if backend == "llama":
            values["restart_llama_after_translation"] = bool(legacy_restart)
        elif backend == "apertium":
            values["restart_apertium_after_translation"] = bool(legacy_restart)
        elif backend in {"cloud", "custom"}:
            values["reconnect_cloud_after_translation"] = bool(legacy_restart)

    return AppSettings(**values)


def save_settings(settings: AppSettings, path: Path = CONFIG_PATH) -> None:
    """Zapisz wszystkie trwałe ustawienia aplikacji do jednego config.json."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = asdict(settings)
    # Klucze API są migrowane przez SecretStore i nie mogą być utrwalane w config.json.
    data.pop("api_key", None)
    data.pop("last_local_api_key", None)
    data["server_gguf_path"] = normalize_local_file_path(
        str(data.get("server_gguf_path", ""))
    )
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def reset_settings(path: Path = CONFIG_PATH) -> AppSettings:
    settings = AppSettings()
    save_settings(settings, path)
    return settings


__all__ = ["AppSettings", "CLOUD_MODELS_CONFIG", "CONFIG_PATH", "load_settings", "reset_settings", "save_settings"]
