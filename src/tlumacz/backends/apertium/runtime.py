"""Discovery and diagnostics for the private Apertium runtime."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from .bundled import locate_bundled_runtime
from .config import DEFAULT_EXECUTABLE, ApertiumConfig, default_data_dir
from .contract import ApertiumCapabilities
from .errors import ApertiumError, ApertiumUnavailableError
from .language_plugins import discover_language_plugins, discover_supported_pairs
from .packages import materialize_language_packages


@dataclass(frozen=True, slots=True)
class ApertiumRuntime:
    """Resolved executable and optional data directory."""

    executable: str
    data_dir: Path | None = None
    executable_args: tuple[str, ...] = ()
    _workspace: TemporaryDirectory[str] | None = None

    @classmethod
    def discover(
        cls,
        config: ApertiumConfig,
        *,
        bundled_root: Path | None = None,
    ) -> ApertiumRuntime:
        """Resolve the runtime without installing or mutating the system."""

        if config.executable == DEFAULT_EXECUTABLE:
            bundled = locate_bundled_runtime(bundled_root)
            if bundled is not None:
                # Runtime wykonywalny jest bundlowany z aplikacją, natomiast
                # pary językowe są niezależnymi paczkami użytkownika.
                store_dir = config.data_dir or default_data_dir()
                store_dir.mkdir(parents=True, exist_ok=True)
                materialized = materialize_language_packages(store_dir)
                workspace = TemporaryDirectory(prefix="apertium-pair-runtime-")
                temporary_root = Path(workspace.name)
                for child in materialized.iterdir():
                    child.replace(temporary_root / child.name)
                materialized.rmdir()
                return cls(
                    str(bundled.executable),
                    temporary_root,
                    config.executable_args,
                    workspace,
                )
            raise ApertiumUnavailableError("Brak prywatnego runtime’u Apertium dołączonego do aplikacji.")

        executable = shutil.which(config.executable)
        if executable is None:
            configured = Path(config.executable).expanduser()
            if configured.is_file() and os.access(configured, os.X_OK):
                executable = str(configured)
        if executable is None:
            raise ApertiumUnavailableError(f"Nie znaleziono runtime’u Apertium: {config.executable!r}.")
        return cls(executable, config.data_dir, config.executable_args)

    def _command(self, *args: str) -> list[str]:
        command = [self.executable, *self.executable_args]
        if self.data_dir is not None:
            command.extend(["-d", str(self.data_dir)])
        command.extend(args)
        return command

    def version(self, *, timeout_seconds: float) -> str:
        return self._run_probe(["-V"], timeout_seconds).strip()

    def language_pairs(self, *, timeout_seconds: float) -> tuple[str, ...]:
        output = self._run_probe(["-l"], timeout_seconds)
        pairs = tuple(line.strip() for line in output.splitlines() if line.strip() and line.strip() != "*")
        data_dir = self.data_dir
        discovered = (
            discover_language_plugins(
                data_dir,
                runtime_bin_dir=Path(self.executable).parent,
            )
            if data_dir
            else ()
        )
        if discovered:
            assert data_dir is not None
            return discover_supported_pairs(
                data_dir,
                runtime_bin_dir=Path(self.executable).parent,
            )
        return tuple(sorted(pairs))

    def data_dir_for_pair(self, pair: str) -> Path | None:
        if self.data_dir is None:
            return None
        for plugin in discover_language_plugins(
            self.data_dir,
            runtime_bin_dir=Path(self.executable).parent,
        ):
            if pair in plugin.compiled_modes:
                package_mode = plugin.root / "modes" / f"{pair}.mode"
                if package_mode.is_file():
                    try:
                        mode_text = package_mode.read_text(encoding="utf-8")
                    except OSError:
                        mode_text = ""
                    if f"{plugin.root.name}/" in mode_text:
                        return self.data_dir
                    return plugin.root
                # Materializowany workspace zawiera tryby wymagane przez
                # runtime; pipeline może odwoływać się względnie do pakietu.
                return self.data_dir
        return None

    def capabilities(self, *, timeout_seconds: float) -> ApertiumCapabilities:
        return ApertiumCapabilities(
            backend="apertium",
            runtime_version=self.version(timeout_seconds=timeout_seconds),
            language_pairs=self.language_pairs(timeout_seconds=timeout_seconds),
        )

    def _run_probe(self, args: list[str], timeout_seconds: float) -> str:
        environment = os.environ.copy()
        if self.data_dir is not None:
            environment["APERTIUM_DATADIR"] = str(self.data_dir.resolve())
        try:
            completed = subprocess.run(
                self._command(*args),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                check=False,
                env=environment,
            )
        except subprocess.TimeoutExpired as exc:
            raise ApertiumUnavailableError(f"Diagnostyka Apertium przekroczyła limit {timeout_seconds:.1f} s.") from exc
        except OSError as exc:
            raise ApertiumUnavailableError(f"Nie można uruchomić Apertium: {exc}") from exc
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()[-500:]
            raise ApertiumError(
                f"Diagnostyka Apertium zakończyła się kodem {completed.returncode}."
                + (f" Szczegóły: {detail}" if detail else "")
            )
        return completed.stdout


__all__ = ["ApertiumRuntime"]
