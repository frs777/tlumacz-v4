"""Local secret storage kept outside V4 configuration profiles."""

from __future__ import annotations

import os
from pathlib import Path

from .logging import register_secrets


class SecretStore:
    """Small service-scoped secret store compatible with V3 .key format."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def get_service_api_key(self, service_id: str) -> str:
        name = _service_secret_key_name(service_id)
        for key, value in _load(self.path).items():
            if key == name:
                register_secrets((value,))
                return value
        return ""

    def set_service_api_key(self, service_id: str, value: str) -> None:
        path = self.path
        path.parent.mkdir(parents=True, exist_ok=True)
        keys = _load(path)
        name = _service_secret_key_name(service_id)
        if value:
            keys[name] = value
            register_secrets((value,))
        else:
            keys.pop(name, None)

        lines = [f'{key}="{keys[key]}"' for key in sorted(keys)]
        path.write_text(
            "\n".join(lines) + ("\n" if lines else ""),
            encoding="utf-8",
        )
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass


def _service_secret_key_name(service_id: str) -> str:
    normalized = service_id.strip()
    if not normalized:
        raise ValueError("service_id nie może być pusty")
    return f"SERVICE/{normalized}"


def _load(path: Path) -> dict[str, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    result: dict[str, str] = {}
    for line in content.splitlines():
        parsed = _parse_line(line)
        if parsed is not None:
            result[parsed[0]] = parsed[1]
    return result


def _parse_line(line: str) -> tuple[str, str] | None:
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        return None
    name, value = line.split("=", 1)
    name = name.strip()
    value = value.strip()
    if not name:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return name, value


__all__ = ["SecretStore"]
