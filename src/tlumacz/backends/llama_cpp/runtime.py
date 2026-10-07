"""Lifecycle manager for an application-owned llama.cpp process."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tlumacz.application.cancellation import CancellationToken
from tlumacz.domain.contracts import HealthCheckResult

LLAMA_CONFIG_PATH = Path.home() / ".config" / "tlumacz" / "llama.json"
REPOSITORY_LLAMA_CONFIG_PATH = Path(__file__).resolve().parents[4] / "config" / "llama.json"


@dataclass(frozen=True, slots=True)
class LlamaCppTuning:
    """Techniczne ustawienia llama.cpp ładowane z llama.json."""

    threads: int | str = "auto"
    threads_batch: int | str = "auto"
    batch_size: int = 2048
    ubatch_size: int = 512
    ctx_size: int | str = "auto"
    prompt_cache: bool = True
    cache_reuse: int = 0
    flash_attention: str = "off"
    repack: str = "on"
    numa: str = "auto"
    gpu_layers: int | str = "auto"
    kv_unified: str = "auto"
    cache_type_k: str = "q8_0"
    cache_type_v: str = "f16"
    poll: int = 50
    runtime_source: str = "bundled"
    system_executable: str = "llama-server"


def load_llama_json(path: Path | None = None) -> LlamaCppTuning:
    """Wczytaj techniczne ustawienia llama.cpp z profilu użytkownika."""
    candidates = [path] if path is not None else [LLAMA_CONFIG_PATH, REPOSITORY_LLAMA_CONFIG_PATH]
    data: dict[str, object] = {}
    for candidate in candidates:
        if candidate is None or not candidate.is_file():
            continue
        try:
            decoded = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(decoded, dict):
            data = decoded
            break

    rules = data.get("zasady", {})
    auto = data.get("auto", {})
    if not isinstance(rules, dict):
        rules = {}
    if not isinstance(auto, dict):
        auto = {}

    def value(name: str, default: Any) -> Any:
        configured = rules.get(name, default)
        if configured == "auto" and name in auto:
            return auto[name]
        return configured

    def numeric_value(name: str, default: int) -> int:
        configured = value(name, default)
        return int(configured) if isinstance(configured, (int, float)) else default

    runtime = data.get("runtime", {})
    if not isinstance(runtime, dict):
        runtime = {}

    return LlamaCppTuning(
        threads=value("threads", "auto"),
        threads_batch=value("threads_batch", "auto"),
        batch_size=numeric_value("batch_size", 2048),
        ubatch_size=numeric_value("ubatch_size", 512),
        ctx_size=value("ctx_size", "auto"),
        prompt_cache=bool(value("prompt_cache", True)),
        cache_reuse=int(value("cache_reuse", 0)),
        flash_attention=str(value("flash_attention", "off")),
        repack=str(value("repack", "on")),
        numa=str(value("numa", "auto")),
        gpu_layers=value("gpu_layers", "auto"),
        kv_unified=str(value("kv_unified", "auto")),
        cache_type_k=str(auto.get("cache_type_k", "q8_0")),
        cache_type_v=str(auto.get("cache_type_v", "f16")),
        poll=int(auto.get("poll", 50)),
        runtime_source=str(runtime.get("source", "bundled")),
        system_executable=str(runtime.get("executable", "llama-server")),
    )


def resolve_llama_executable(tuning: LlamaCppTuning) -> str:
    """Rozwiąż wykonywalny llama-server zgodnie z profilem runtime."""
    if tuning.runtime_source == "bundled":
        if os.name != "posix" or os.uname().sysname.lower() != "linux" or os.uname().machine.lower() not in {"x86_64", "amd64"}:
            raise RuntimeError("Dołączony runtime llama.cpp jest obecnie dostępny tylko dla Linux x86_64.")
        executable: str | Path = Path(__file__).resolve().parent / "native" / "linux-x86_64" / "llama-server"
        if not Path(executable).is_file():
            raise RuntimeError(f"Brak dołączonego runtime llama.cpp: {executable}")
        return str(executable)
    if tuning.runtime_source == "system":
        executable = tuning.system_executable.strip() or "llama-server"
        if "/" not in executable and "\\" not in executable:
            resolved = shutil.which(executable)
            if not resolved:
                raise RuntimeError(f"Nie znaleziono systemowego llama-server: {executable}")
            return resolved
        if not Path(executable).is_file():
            raise RuntimeError(f"Nie znaleziono systemowego llama-server: {executable}")
        return executable
    raise ValueError(f"Nieznane źródło runtime llama.cpp: {tuning.runtime_source}")


@dataclass(frozen=True, slots=True)
class LlamaCppRuntimeConfig:
    """Command-line and lifecycle configuration for llama-server."""

    executable: str | None = None
    model_path: str = ""
    host: str = "127.0.0.1"
    port: int = 18080
    ctx_size: int | None = None
    parallel: int = 1
    compute_mode: str = "gpu"
    chat_template: str = ""
    tuning: LlamaCppTuning = field(default_factory=load_llama_json)
    chunk_size: int = 1000
    # Model TranslateGemma może ładować się długo przy presji pamięci.
    startup_timeout: float = 300.0
    shutdown_timeout: float = 5.0
    poll_interval: float = 0.05
    extra_args: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.model_path:
            raise ValueError("model_path nie może być pusty")
        executable = self.executable
        if executable is None:
            executable = resolve_llama_executable(self.tuning)
            object.__setattr__(self, "executable", executable)
        if not executable:
            raise ValueError("executable nie może być pusty")
        if not 1 <= self.port <= 65535:
            raise ValueError("port musi należeć do zakresu 1..65535")
        if self.ctx_size is not None and self.ctx_size <= 0:
            raise ValueError("ctx_size musi być dodatni")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size musi być dodatni")
        if self.parallel < 1:
            raise ValueError("parallel musi być dodatni")
        if self.compute_mode not in {"cpu", "gpu"}:
            raise ValueError("compute_mode musi być 'cpu' albo 'gpu'")
        if self.chat_template not in {"", "chatml", "translategemma"}:
            raise ValueError("chat_template musi być '', 'chatml' albo 'translategemma'")
        if self.startup_timeout <= 0:
            raise ValueError("startup_timeout musi być dodatni")
        if self.shutdown_timeout <= 0:
            raise ValueError("shutdown_timeout musi być dodatni")
        if self.poll_interval <= 0:
            raise ValueError("poll_interval musi być dodatni")

    def command(self) -> list[str]:
        executable = self.executable
        if executable is None:
            raise RuntimeError("executable nie może być pusty")
        command = [
            executable,
            "-m",
            self.model_path,
            "--alias",
            "local",
            "--host",
            self.host,
            "--port",
            str(self.port),
            "--ctx-size",
            str(self.resolved_ctx_size()),
            "--parallel",
            str(self.parallel),
            "--n-gpu-layers",
            str(self.resolved_gpu_layers()),
        ]
        command.extend(("--threads", str(self.resolved_threads())))
        command.extend(("--threads-batch", str(self.resolved_threads_batch())))
        command.extend(("--batch-size", str(self.tuning.batch_size)))
        command.extend(("--ubatch-size", str(self.tuning.ubatch_size)))
        command.extend(("--cache-type-k", self.tuning.cache_type_k))
        command.extend(("--cache-type-v", self.tuning.cache_type_v))
        command.extend(("--poll", str(self.tuning.poll)))
        if self.tuning.prompt_cache:
            command.append("--cache-prompt")
        else:
            command.append("--no-cache-prompt")
        command.extend(("--cache-reuse", str(self.tuning.cache_reuse)))
        if self.tuning.flash_attention in {"on", "off", "auto"}:
            command.extend(("--flash-attn", self.tuning.flash_attention))
        if self.tuning.repack == "on":
            command.append("--repack")
        elif self.tuning.repack == "off":
            command.append("--no-repack")
        if self.tuning.numa in {"distribute", "isolate", "numactl"}:
            command.extend(("--numa", self.tuning.numa))
        if self.tuning.kv_unified == "on":
            command.append("--kv-unified")
        elif self.tuning.kv_unified == "off":
            command.append("--no-kv-unified")
        if self.chat_template == "translategemma":
            # TranslateGemma jest renderowane ręcznie przez adapter przez
            # /v1/completions; natywny parser Jinja llama.cpp odrzuca typed-content
            # tego modelu w aktualnym runtime.
            command.append("--no-jinja")
        elif self.chat_template:
            command.extend(("--no-jinja", "--chat-template", self.chat_template))
        else:
            command.append("--jinja")
        command.extend(self.extra_args)
        return command

    def resolved_ctx_size(self) -> int:
        if self.ctx_size is not None:
            return self.ctx_size
        configured = self.tuning.ctx_size
        if isinstance(configured, int) and configured > 0:
            return configured
        ctx_rules = _load_ctx_rules()
        estimated = int(self.chunk_size / ctx_rules["znaki_na_token"])
        estimated += int(ctx_rules["rezerwa_promptu"])
        estimated += int(ctx_rules["rezerwa_generacji"])
        estimated += int(ctx_rules["rezerwa_skilla"])
        estimated += int(ctx_rules["margines"])
        minimum = int(ctx_rules["minimum_slotu"])
        rounding = int(ctx_rules["zaokraglenie"])
        estimated = max(estimated, minimum)
        return ((estimated + rounding - 1) // rounding) * rounding

    def resolved_threads(self) -> int:
        if isinstance(self.tuning.threads, int):
            return self.tuning.threads
        physical, logical = _hardware_thread_counts()
        return physical if self.tuning.threads == "auto" else logical

    def resolved_threads_batch(self) -> int:
        if isinstance(self.tuning.threads_batch, int):
            return self.tuning.threads_batch
        _physical, logical = _hardware_thread_counts()
        return logical if self.tuning.threads_batch == "auto" else logical

    def resolved_gpu_layers(self) -> int:
        if self.compute_mode == "cpu":
            return 0
        if isinstance(self.tuning.gpu_layers, int):
            return self.tuning.gpu_layers
        return 999

@dataclass(frozen=True, slots=True)
class ProcessIdentity:
    """Identity tuple required before terminating a managed process."""

    pid: int
    executable: str
    command_line: tuple[str, ...]
    parent_pid: int | None
    process_group: int | None
    session_id: int | None


class LlamaCppRuntimeManager:
    """Start and stop only a process whose identity matches the saved identity."""

    def __init__(self, config: LlamaCppRuntimeConfig) -> None:
        self.config = config
        self._process: subprocess.Popen[bytes] | None = None
        self._process_identity: ProcessIdentity | None = None
        self._ownership_error: str | None = None

    @property
    def pid(self) -> int | None:
        if self._process is None or self._process.poll() is not None:
            return None
        return self._process.pid

    @property
    def process_identity(self) -> ProcessIdentity | None:
        return self._process_identity

    @property
    def ownership_error(self) -> str | None:
        return self._ownership_error

    def is_running(self) -> bool:
        return self.pid is not None

    def start(
        self,
        *,
        wait_for_ready: Callable[[], bool] | None = None,
    ) -> int:
        if self.is_running():
            assert self._process is not None
            return self._process.pid

        executable = self.config.executable
        if executable is None:
            raise RuntimeError("executable nie może być pusty")
        if "/" not in executable and "\\" not in executable:
            executable = shutil.which(executable) or ""
        if not executable:
            raise RuntimeError(
                f"Nie znaleziono executable llama.cpp: {self.config.executable}"
            )

        command = [executable, *self.config.command()[1:]]
        environment = os.environ.copy()
        if self.config.tuning.runtime_source == "bundled":
            runtime_dir = str(Path(executable).resolve().parent)
            existing = environment.get("LD_LIBRARY_PATH", "")
            environment["LD_LIBRARY_PATH"] = (
                runtime_dir if not existing else f"{runtime_dir}:{existing}"
            )
        try:
            self._process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=environment,
                start_new_session=True,
            )
        except OSError as exc:
            self._process = None
            raise RuntimeError(f"Nie można uruchomić llama.cpp: {exc}") from exc

        self._process_identity = _capture_identity(self._process)
        self._ownership_error = None

        if wait_for_ready is not None:
            try:
                self.wait_for_ready(wait_for_ready)
            except Exception:
                self.stop()
                raise

        return self._process.pid

    def wait_for_ready(self, probe: Callable[[], bool]) -> None:
        deadline = time.monotonic() + self.config.startup_timeout
        while time.monotonic() < deadline:
            if not self.is_running():
                raise RuntimeError("llama.cpp zakończył się przed osiągnięciem gotowości")
            if probe():
                return
            time.sleep(self.config.poll_interval)
        raise TimeoutError(
            f"Timeout uruchomienia llama.cpp po {self.config.startup_timeout:.2f} s"
        )

    def cancel(self, token: CancellationToken) -> None:
        if token.is_cancelled:
            self.stop()

    def health_check(self) -> HealthCheckResult:
        if not self.is_running():
            return HealthCheckResult.failed(
                "llama_cpp_runtime",
                "llama.cpp nie jest uruchomiony",
            )
        if self._process is None or not self._matches_owned_identity(self._process):
            return HealthCheckResult.failed(
                "llama_cpp_runtime",
                "tożsamość uruchomionego procesu nie jest zgodna",
            )
        return HealthCheckResult.ok("llama_cpp_runtime")

    def stop(self) -> None:
        process = self._process
        if process is None:
            return
        if process.poll() is not None:
            self._process = None
            self._process_identity = None
            return

        if not self._matches_owned_identity(process):
            self._ownership_error = (
                "Tożsamość procesu llama.cpp nie odpowiada zapisanej tożsamości; "
                "proces nie zostanie zakończony."
            )
            return

        self._ownership_error = None
        self._process = None
        self._process_identity = None

        try:
            process.terminate()
            process.wait(timeout=self.config.shutdown_timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=self.config.shutdown_timeout)
        except OSError:
            pass

    def _matches_owned_identity(
        self,
        process: subprocess.Popen[bytes],
    ) -> bool:
        expected = self._process_identity
        if expected is None:
            return False
        current = _capture_identity(process)
        if current is None:
            return False
        return current == expected


def _load_ctx_rules() -> dict[str, float]:
    path = LLAMA_CONFIG_PATH if LLAMA_CONFIG_PATH.is_file() else REPOSITORY_LLAMA_CONFIG_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        section = data.get("ctx_size", {})
        if isinstance(section, dict):
            return {
                "znaki_na_token": float(section.get("znaki_na_token", 4.0)),
                "rezerwa_promptu": float(section.get("rezerwa_promptu", 512)),
                "rezerwa_generacji": float(section.get("rezerwa_generacji", 512)),
                "rezerwa_skilla": float(section.get("rezerwa_skilla", 256)),
                "margines": float(section.get("margines", 256)),
                "minimum_slotu": float(section.get("minimum_slotu", 4096)),
                "zaokraglenie": float(section.get("zaokraglenie", 1024)),
            }
    except (OSError, ValueError, TypeError):
        pass
    return {
        "znaki_na_token": 4.0,
        "rezerwa_promptu": 512.0,
        "rezerwa_generacji": 512.0,
        "rezerwa_skilla": 256.0,
        "margines": 256.0,
        "minimum_slotu": 4096.0,
        "zaokraglenie": 1024.0,
    }


def _capture_identity(
    process: subprocess.Popen[bytes],
) -> ProcessIdentity | None:
    pid = process.pid
    for _ in range(20):
        try:
            executable = str(Path(f"/proc/{pid}/exe").resolve())
            raw_command = Path(f"/proc/{pid}/cmdline").read_bytes()
            command_line = tuple(
                part.decode("utf-8", errors="replace")
                for part in raw_command.split(b"\0")
                if part
            )
            if not command_line:
                time.sleep(0.005)
                continue
            parent_pid = _read_status_int(pid, "PPid")
            process_group = os.getpgid(pid)
            session_id = os.getsid(pid)
            return ProcessIdentity(
                pid=pid,
                executable=executable,
                command_line=command_line,
                parent_pid=parent_pid,
                process_group=process_group,
                session_id=session_id,
            )
        except (OSError, ValueError):
            time.sleep(0.005)

    args = process.args
    command_line = (
        tuple(args)
        if isinstance(args, (list, tuple))
        else (str(args),)
    )
    executable = str(command_line[0]) if command_line else ""
    return ProcessIdentity(
        pid=pid,
        executable=executable,
        command_line=command_line,
        parent_pid=None,
        process_group=None,
        session_id=None,
    )

def _read_status_int(pid: int, field_name: str) -> int | None:
    status = Path(f"/proc/{pid}/status")
    if not status.is_file():
        return None
    prefix = f"{field_name}:"
    for line in status.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(prefix):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


__all__ = [
    "LlamaCppRuntimeConfig",
    "LlamaCppRuntimeManager",
    "LlamaCppTuning",
    "load_llama_json",
    "ProcessIdentity",
]


def _hardware_thread_counts() -> tuple[int, int]:
    """Zwróć liczbę rdzeni fizycznych i logicznych bez dodatkowej zależności."""
    logical = os.cpu_count() or 1
    physical = logical

    if os.name == "posix":
        try:
            if Path("/proc/cpuinfo").is_file():
                pairs: set[tuple[str, str]] = set()
                physical_id: str | None = None
                core_id: str | None = None
                for line in Path("/proc/cpuinfo").read_text(
                    encoding="utf-8", errors="replace"
                ).splitlines() + [""]:
                    if line.startswith("physical id:"):
                        physical_id = line.split(":", 1)[1].strip()
                    elif line.startswith("core id:"):
                        core_id = line.split(":", 1)[1].strip()
                    elif not line.strip():
                        if physical_id is not None and core_id is not None:
                            pairs.add((physical_id, core_id))
                        physical_id = None
                        core_id = None
                if pairs:
                    physical = len(pairs)
        except OSError:
            pass

    return max(1, physical), max(1, logical)
