"""JSON Lines protocol client for the isolated Filter Host."""

from __future__ import annotations

import json
import subprocess
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Mapping, Sequence

PROTOCOL_VERSION = 1


@dataclass(frozen=True, slots=True)
class FilterHostResponse:
    """Validated response returned by the Filter Host."""

    protocol_version: int
    request_id: str
    result: object


class FilterHostError(RuntimeError):
    """Transport, protocol or structured Filter Host error."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "INTERNAL_ERROR",
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class FilterHostClient:
    """Long-lived JSON Lines client for one Filter Host process."""

    def __init__(
        self,
        command: Sequence[str],
        *,
        timeout: float = 120.0,
        protocol_version: int = PROTOCOL_VERSION,
    ) -> None:
        if not command:
            raise ValueError("Polecenie hosta filtra nie może być puste.")
        if timeout <= 0:
            raise ValueError("Timeout hosta filtra musi być dodatni.")
        if protocol_version <= 0:
            raise ValueError("Wersja protokołu musi być dodatnia.")

        self.command = tuple(command)
        self.timeout = timeout
        self.protocol_version = protocol_version
        self._process: subprocess.Popen[str] | None = None
        self._responses: Queue[dict[str, object] | None] = Queue()
        self._request_lock = threading.Lock()
        self._reader: threading.Thread | None = None
        self._stderr_reader: threading.Thread | None = None
        self._stderr_tail: deque[str] = deque(maxlen=32)

    def __enter__(self) -> FilterHostClient:
        self.start()
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def start(self) -> None:
        if self._process is not None and self._process.poll() is None:
            return
        try:
            process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except OSError as exc:
            raise FilterHostError(
                f"Nie można uruchomić Filter Host: {exc}",
                code="HOST_START_ERROR",
            ) from exc

        self._process = process
        self._responses = Queue()
        self._stderr_tail.clear()
        self._reader = threading.Thread(
            target=self._read_responses,
            name="tlumacz-filter-host-reader",
            daemon=False,
        )
        self._reader.start()
        self._stderr_reader = threading.Thread(
            target=self._read_stderr,
            name="tlumacz-filter-host-stderr",
            daemon=False,
        )
        self._stderr_reader.start()

    def close(self) -> None:
        process = self._process
        self._process = None
        if process is None:
            return

        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=min(self.timeout, 2.0))
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2.0)

        # Proces potomny może już nie żyć, ale wątki czytające pipe'y nadal są
        # osobnymi aktywnościami Pythona. Muszą zakończyć się przed zamknięciem
        # właściciela klienta; inaczej kolejne testy/GC mogą wejść w Qt/PySide6
        # z pozostawionymi wątkami Filter Host. Najpierw dajemy im szansę
        # zobaczyć EOF, a dopiero potem zamykamy deskryptory, aby odblokować
        # przypadek, w którym potomny proces pozostawił otwarty pipe.
        self._join_io_threads(timeout=0.5)

        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                try:
                    stream.close()
                except (OSError, ValueError):
                    pass

        self._join_io_threads(timeout=0.5)

    def _join_io_threads(self, *, timeout: float) -> None:
        """Poczekaj ograniczony czas na zakończenie wątków czytających pipe'y."""
        deadline = time.monotonic() + max(timeout, 0.0)
        current = threading.current_thread()
        for thread in (self._reader, self._stderr_reader):
            if thread is None or thread is current or not thread.is_alive():
                continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                thread.join(timeout=remaining)
            except RuntimeError:
                # Thread może zakończyć się pomiędzy is_alive() a join().
                continue

    def request(self, operation: str, payload: Mapping[str, object]) -> FilterHostResponse:
        if not operation:
            raise ValueError("Operation hosta filtra nie może być pusta.")
        if not isinstance(payload, Mapping):
            raise TypeError("Payload hosta filtra musi być obiektem mapowania.")

        self.start()
        process = self._process
        if process is None or process.stdin is None:
            raise FilterHostError(
                "Filter Host nie jest uruchomiony.",
                code="HOST_NOT_RUNNING",
            )

        request_id = uuid.uuid4().hex
        request = {
            "protocol_version": self.protocol_version,
            "request_id": request_id,
            "operation": operation,
            "payload": dict(payload),
        }

        with self._request_lock:
            try:
                process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
                process.stdin.flush()
            except (BrokenPipeError, OSError) as exc:
                raise FilterHostError(
                    "Nie można zapisać żądania do Filter Host.",
                    code="HOST_IO_ERROR",
                    retryable=True,
                ) from exc

            try:
                response = self._responses.get(timeout=self.timeout)
            except Empty as exc:
                self.close()
                raise FilterHostError(
                    f"Filter Host przekroczył limit czasu ({self.timeout:.1f} s).",
                    code="TIMEOUT",
                    retryable=True,
                ) from exc

        if response is None:
            details = " ".join(self._stderr_tail).strip()
            message = "Filter Host zakończył pracę bez odpowiedzi."
            if details:
                message += f" Szczegóły: {details[-2000:]}"
            raise FilterHostError(message, code="HOST_EXITED", retryable=True)

        self._validate_response(response, request_id)

        return FilterHostResponse(
            protocol_version=self.protocol_version,
            request_id=request_id,
            result=response.get("result"),
        )

    def _validate_response(
        self,
        response: dict[str, object],
        request_id: str,
    ) -> None:
        version = response.get("protocol_version")
        if version != self.protocol_version:
            raise FilterHostError(
                f"Nieobsługiwana wersja protokołu odpowiedzi: {version!r}.",
                code="UNSUPPORTED_PROTOCOL",
            )

        returned_id = response.get("request_id")
        if returned_id != request_id:
            raise FilterHostError(
                "Niezgodny request_id odpowiedzi: "
                f"oczekiwano {request_id!r}, otrzymano {returned_id!r}.",
                code="PROTOCOL_ERROR",
            )

        if response.get("ok") is True:
            return

        error = response.get("error")
        if not isinstance(error, dict):
            raise FilterHostError(
                "Filter Host zwrócił błędną odpowiedź error.",
                code="PROTOCOL_ERROR",
            )

        code = str(error.get("code", "INTERNAL_ERROR"))
        message = str(error.get("message", "Brak szczegółów błędu."))
        raise FilterHostError(
            f"{code}: {message}",
            code=code,
            retryable=bool(error.get("retryable", False)),
        )

    def _read_responses(self) -> None:
        process = self._process
        if process is None or process.stdout is None:
            return
        try:
            for line in process.stdout:
                if not line.strip():
                    continue
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(message, dict):
                    self._responses.put(message)
        except (OSError, ValueError):
            # close() może zamknąć pipe, aby odblokować czytnik.
            pass
        finally:
            self._responses.put(None)

    def _read_stderr(self) -> None:
        process = self._process
        if process is None or process.stderr is None:
            return
        try:
            for line in process.stderr:
                line = line.rstrip()
                if line:
                    self._stderr_tail.append(line)
        except (OSError, ValueError):
            # close() może zamknąć pipe, aby odblokować czytnik.
            pass
