"""Centralna konfiguracja logowania aplikacji Tłumacz V4.

Logowanie pozostaje szczegółowe w wersji testowej. Ten moduł odpowiada za
jednolity format, poziom diagnostyczny oraz redakcję sekretów przed zapisaniem
komunikatu do handlera.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

LOGGER_NAME = "tlumacz"
_REGISTERED_SECRETS: set[str] = set()
DEFAULT_LOG_DIR = Path.home() / ".config" / "tlumacz" / "logs"
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "tlumacz.log"
REDACTED = "[UTAJNIONO]"

_SENSITIVE_KEY = re.compile(
    r"^(?:api[_-]?key|authorization|proxy-authorization|access[_-]?token|refresh[_-]?token|token|password|passwd|secret)$",
    re.IGNORECASE,
)
_BEARER = re.compile(r"(?i)(\bBearer\s+)[^\s,;]+")
_KEY_VALUE = re.compile(
    r"(?i)(\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|secret|token)\s*[=:]\s*)([^\s,;]+)"
)
_QUERY_SECRET = re.compile(
    r"(?i)([?&](?:api[_-]?key|access[_-]?token|refresh[_-]?token|key|token|password|secret)=)[^&#\s]+"
)


class SecretRedactionFilter(logging.Filter):
    """Usuwa znane i jawnie nazwane sekrety z rekordów logowania."""

    def __init__(self, secrets: Iterable[str] = ()) -> None:
        super().__init__()
        self._secrets = {secret for secret in secrets if secret}

    def add_secrets(self, secrets: Iterable[str]) -> None:
        self._secrets.update(secret for secret in secrets if secret)

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_secrets(record.msg, self._secrets)
        if record.args:
            if isinstance(record.args, Mapping):
                record.args = {key: redact_secrets(value, self._secrets) for key, value in record.args.items()}
            else:
                record.args = tuple(redact_secrets(value, self._secrets) for value in record.args)
        return True


def redact_secrets(value: Any, secrets: Iterable[str] = ()) -> Any:
    """Zwróć wartość z usuniętymi sekretami i polami wrażliwymi."""
    secret_set = {secret for secret in secrets if secret}

    if isinstance(value, Mapping):
        return {
            key: REDACTED
            if isinstance(key, str) and _SENSITIVE_KEY.fullmatch(key)
            else redact_secrets(item, secret_set)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_secrets(item, secret_set) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_secrets(item, secret_set) for item in value)
    if isinstance(value, set):
        return {redact_secrets(item, secret_set) for item in value}
    if not isinstance(value, str):
        return value

    result = value
    for secret in sorted(secret_set, key=len, reverse=True):
        result = result.replace(secret, REDACTED)
    result = _BEARER.sub(rf"\1{REDACTED}", result)
    result = _KEY_VALUE.sub(rf"\1{REDACTED}", result)
    result = _QUERY_SECRET.sub(rf"\1{REDACTED}", result)
    return result


class _PolishFormatter(logging.Formatter):
    """Jednolity format logów; komunikaty aplikacji są prowadzone po polsku."""

    def __init__(self, secrets: Iterable[str] = ()) -> None:
        super().__init__()
        self._secrets = tuple(secrets)

    def format(self, record: logging.LogRecord) -> str:
        message = redact_secrets(record.getMessage(), self._secrets)
        if record.exc_info:
            message = f"{message}\n{redact_secrets(self.formatException(record.exc_info), self._secrets)}"
        if record.stack_info:
            message = f"{message}\n{redact_secrets(self.formatStack(record.stack_info), self._secrets)}"
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        return f"{timestamp} | {record.levelname:<8} | {record.name} | {message}"


def register_secrets(secrets: Iterable[str]) -> None:
    """Zarejestruj sekrety do redakcji także po uruchomieniu loggera."""
    values = {secret for secret in secrets if secret}
    if not values:
        return
    _REGISTERED_SECRETS.update(values)

    logger = logging.getLogger(LOGGER_NAME)
    for handler in logger.handlers:
        for current_filter in handler.filters:
            if isinstance(current_filter, SecretRedactionFilter):
                current_filter.add_secrets(values)


def configure_logging(
    *,
    level: int = logging.DEBUG,
    log_file: Path | None = None,
    console: bool = True,
    secret_values: Iterable[str] = (),
) -> logging.Logger:
    """Skonfiguruj centralny logger Tłumacza bez wyłączania DEBUG."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    for handler in logger.handlers:
        handler.close()
    logger.handlers.clear()

    known_secrets = _REGISTERED_SECRETS | {secret for secret in secret_values if secret}
    redactor = SecretRedactionFilter(known_secrets)
    formatter = _PolishFormatter(known_secrets)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.addFilter(redactor)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file is None:
        log_file = DEFAULT_LOG_FILE
    log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.addFilter(redactor)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


__all__ = [
    "DEFAULT_LOG_DIR",
    "DEFAULT_LOG_FILE",
    "LOGGER_NAME",
    "REDACTED",
    "SecretRedactionFilter",
    "configure_logging",
    "redact_secrets",
]
