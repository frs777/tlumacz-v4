"""Common TranslationBackend adapter for the local Apertium CLI."""

from __future__ import annotations

import logging
import os
import subprocess
import time

from tlumacz.domain.contracts import BackendResult, HealthCheckResult

from .config import ApertiumConfig
from .errors import (
    ApertiumError,
    ApertiumOutputLimitError,
    ApertiumTimeoutError,
    ApertiumUnavailableError,
    ApertiumValidationError,
)
from .languages import build_language_pair
from .runtime import ApertiumRuntime

logger = logging.getLogger("tlumacz.backends.apertium.adapter")


class ApertiumAdapter:
    """Translate neutral text units through an application-owned Apertium runtime."""

    def __init__(
        self,
        config: ApertiumConfig | None = None,
        *,
        runtime: ApertiumRuntime | None = None,
    ) -> None:
        self.config = config or ApertiumConfig()
        self.runtime = runtime or ApertiumRuntime.discover(self.config)
        self._runtime_version: str | None = None

    def health_check(self) -> HealthCheckResult:
        try:
            self._runtime_version = self.runtime.version(
                timeout_seconds=self.config.timeout_seconds
            )
        except ApertiumError as exc:
            return HealthCheckResult.failed("apertium", str(exc))
        return HealthCheckResult.ok("apertium")

    def supported_language_pairs(self) -> tuple[str, ...]:
        return self.runtime.language_pairs(
            timeout_seconds=self.config.timeout_seconds
        )

    def translate(
        self,
        text: str,
        *,
        source_language: str,
        target_language: str,
    ) -> BackendResult:
        if not text:
            return BackendResult(
                text="",
                source_language=source_language,
                target_language=target_language,
                metadata={"backend": "apertium", "status": "empty"},
            )
        if not source_language.strip() or not target_language.strip():
            raise ApertiumValidationError(
                "Język źródłowy i docelowy są wymagane."
            )

        try:
            pair = build_language_pair(source_language, target_language)
        except ApertiumValidationError as exc:
            raise ApertiumValidationError(
                f"Nieprawidłowa para językowa Apertium: "
                f"{source_language!r} → {target_language!r}"
            ) from exc

        supported = self.supported_language_pairs()
        if pair not in supported:
            raise ApertiumValidationError(
                f"Para językowa {pair!r} jest niedostępna w aktualnym runtime Apertium."
            )

        source_bytes = text.encode("utf-8")
        if len(source_bytes) > self.config.max_input_bytes:
            raise ApertiumValidationError(
                "Tekst wejściowy przekracza limit Apertium."
            )

        command = [self.runtime.executable, *self.runtime.executable_args]
        data_dir = self.runtime.data_dir_for_pair(pair) or self.runtime.data_dir
        if data_dir is not None:
            command.extend(["-d", str(data_dir)])
        command.extend(["-f", self.config.text_format, pair])

        environment = os.environ.copy()
        if data_dir is not None:
            environment["APERTIUM_DATADIR"] = str(data_dir.resolve())
        environment.update(self.config.environment)
        started = time.monotonic()
        logger.debug("Rozpoczęto tłumaczenie Apertium: para=%s, znaków=%d", pair, len(text))

        try:
            completed = subprocess.run(
                command,
                input=source_bytes,
                capture_output=True,
                timeout=self.config.timeout_seconds,
                check=False,
                env=environment,
                cwd=str(data_dir) if data_dir is not None else None,
            )
        except subprocess.TimeoutExpired as exc:
            raise ApertiumTimeoutError(
                f"Apertium przekroczyło limit {self.config.timeout_seconds:.1f} s."
            ) from exc
        except OSError as exc:
            raise ApertiumUnavailableError(
                f"Nie można uruchomić Apertium: {exc}"
            ) from exc

        elapsed = time.monotonic() - started
        if len(completed.stdout) > self.config.max_output_bytes:
            raise ApertiumOutputLimitError(
                "Apertium przekroczyło limit wyjścia."
            )
        if len(completed.stderr) > self.config.max_stderr_bytes:
            raise ApertiumOutputLimitError(
                "Apertium przekroczyło limit stderr."
            )
        if completed.returncode != 0:
            detail = completed.stderr.decode("utf-8", errors="replace").strip()[-500:]
            raise ApertiumError(
                f"Apertium zakończyło pracę kodem {completed.returncode}."
                + (f" Szczegóły: {detail}" if detail else "")
            )

        target = completed.stdout.decode("utf-8", errors="strict")
        target = target.replace("\r\n", "\n").rstrip("\n")
        if not target.strip():
            raise ApertiumValidationError("Apertium zwróciło pusty wynik.")

        if self._runtime_version is None:
            self._runtime_version = self.runtime.version(
                timeout_seconds=self.config.timeout_seconds
            )

        warnings = tuple(
            line.strip()
            for line in completed.stderr.decode("utf-8", errors="replace").splitlines()
            if line.strip()
        )
        logger.debug(
            "Zakończono tłumaczenie Apertium: para=%s, czas %.3f s, wyników ostrzegawczych=%d",
            pair,
            elapsed,
            len(warnings),
        )
        return BackendResult(
            text=target,
            source_language=source_language,
            target_language=target_language,
            metadata={
                "backend": "apertium",
                "pair": pair,
                "runtime_version": self._runtime_version,
                "elapsed_seconds": elapsed,
                "warnings": warnings,
            },
        )


__all__ = ["ApertiumAdapter"]
