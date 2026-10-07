"""Okapi-backed document filters exposed through the Python Filter Engine."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from tlumacz.domain.errors import FilterError

from ..marker_validator import MarkerValidator
from ..protocol import FilterHostClient, FilterHostError


@dataclass(frozen=True, slots=True)
class OkapiUnit:
    """Translation unit produced by an Okapi Java filter."""

    id: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OkapiSession:
    """Python-owned lifecycle state for one document conversion."""

    client: FilterHostClient
    input_path: Path
    workspace: Path
    source_language: str
    target_language: str
    filter_name: str
    units: list[OkapiUnit] = field(default_factory=list)
    closed: bool = False
    cancelled: bool = False


class OkapiFilter:
    """Minimal Python adapter over an Okapi Java filter.

    Python owns lifecycle, validation, workspace and translation-unit contracts.
    Java owns only the Okapi filter implementation and document reconstruction.
    """

    def __init__(
        self,
        filter_name: str,
        suffixes: tuple[str, ...],
        *,
        command: Sequence[str] | None = None,
        timeout: float = 120.0,
        filter_store: Path | None = None,
    ) -> None:
        if not filter_name.strip():
            raise ValueError("Nazwa filtra Okapi nie może być pusta.")
        if not suffixes:
            raise ValueError("Filtr Okapi musi mieć co najmniej jedno rozszerzenie.")
        self.filter_name = filter_name
        self.suffixes = tuple(suffixes)
        self.timeout = timeout
        self.filter_store = Path(filter_store).resolve() if filter_store is not None else None
        self.command = tuple(command) if command is not None else _default_host_command(self.filter_store)

    def capabilities(self) -> dict[str, object]:
        return {
            "name": self.filter_name,
            "suffixes": self.suffixes,
            "backend": "okapi-java",
        }

    def probe(self, input_path: Path) -> bool:
        path = Path(input_path)
        return path.is_file() and path.suffix.lower() in {suffix.lower() for suffix in self.suffixes}

    def open(
        self,
        input_path: Path,
        *,
        source_language: str,
        target_language: str,
        workspace: Path,
    ) -> OkapiSession:
        path = Path(input_path).resolve()
        if not self.probe(path):
            raise FilterError(f"Nieprawidłowy dokument dla filtra {self.filter_name}: {path}")

        workspace = Path(workspace).resolve()
        workspace.mkdir(parents=True, exist_ok=True)
        selected_filter = self._resolve_filter_name(path)
        client = FilterHostClient(self.command, timeout=self.timeout)
        try:
            client.start()
        except FilterHostError as exc:
            client.close()
            raise FilterError(f"Nie można uruchomić filtra {self.filter_name}: {exc}") from exc

        return OkapiSession(
            client=client,
            input_path=path,
            workspace=workspace,
            source_language=source_language,
            target_language=target_language,
            filter_name=selected_filter,
        )

    def extract(self, session: OkapiSession) -> list[OkapiUnit]:
        self._ensure_active(session)
        units_path = session.workspace / "okapi-units.json"
        try:
            result = session.client.request(
                "extract",
                {
                    "filter": session.filter_name,
                    "input": str(session.input_path),
                    "units": str(units_path),
                    "source": session.source_language,
                    "target": session.target_language,
                },
            ).result
        except FilterHostError as exc:
            raise FilterError(f"Błąd ekstrakcji Okapi: {exc}") from exc

        if not isinstance(result, dict) or not isinstance(result.get("units"), list):
            raise FilterError("Filter Host zwrócił nieprawidłowy wynik ekstrakcji.")

        units: list[OkapiUnit] = []
        for raw_unit in result["units"]:
            unit = _unit_from_host(raw_unit)
            code_count = int(unit.metadata.get("code_count", 0))
            MarkerValidator.validate(unit.source, code_count=code_count)
            units.append(unit)

        unique_units: list[OkapiUnit] = []
        occurrences: dict[str, int] = {}
        for unit in units:
            occurrence = occurrences.get(unit.id, 0) + 1
            occurrences[unit.id] = occurrence
            if occurrence == 1:
                unique_units.append(unit)
                continue
            metadata = dict(unit.metadata)
            metadata["source_unit_id"] = unit.id
            metadata["occurrence"] = occurrence
            unique_units.append(
                OkapiUnit(
                    id=f"{unit.id}::{occurrence}",
                    source=unit.source,
                    metadata=metadata,
                )
            )

        session.units = unique_units
        return list(unique_units)

    def write(
        self,
        session: OkapiSession,
        targets: dict[str, str],
        output_path: Path,
    ) -> Path:
        self._ensure_active(session)
        expected = {unit.id for unit in session.units}
        if set(targets) != expected:
            missing = sorted(expected - set(targets))
            extra = sorted(set(targets) - expected)
            raise FilterError(f"Niepełny zestaw targetów Okapi: missing={missing!r}, extra={extra!r}")

        validated_targets: dict[str, str] = {}
        for unit in session.units:
            target = targets[unit.id]
            if not isinstance(target, str):
                raise FilterError(f"Target Okapi musi być tekstem: {unit.id}")
            MarkerValidator.validate(
                target,
                code_count=int(unit.metadata.get("code_count", 0)),
            )
            validated_targets[unit.id] = target

        targets_path = session.workspace / "okapi-targets.json"
        targets_path.write_text(
            json.dumps(validated_targets, ensure_ascii=False),
            encoding="utf-8",
        )
        output = Path(output_path).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)

        try:
            result = session.client.request(
                "merge",
                {
                    "filter": session.filter_name,
                    "input": str(session.input_path),
                    "targets": str(targets_path),
                    "output": str(output),
                    "source": session.source_language,
                    "target": session.target_language,
                },
            ).result
            if not isinstance(result, dict) or result.get("output") != str(output):
                raise FilterError("Filter Host nie potwierdził prawidłowego pliku wynikowego.")
            if not output.is_file():
                raise FilterError(f"Filter Host nie utworzył pliku wynikowego: {output}")
            session.closed = True
            session.client.close()
            return output
        except FilterHostError as exc:
            self._cancel_quietly(session)
            raise FilterError(f"Błąd zapisu Okapi: {exc}") from exc

    def close(self, session: OkapiSession) -> None:
        if session.closed or session.cancelled:
            session.client.close()
            return
        session.cancelled = True
        session.client.close()

    def _cancel_quietly(self, session: OkapiSession) -> None:
        session.cancelled = True
        session.client.close()

    def _resolve_filter_name(self, input_path: Path) -> str:
        return self.filter_name

    @staticmethod
    def _ensure_active(session: OkapiSession) -> None:
        if session.closed or session.cancelled:
            raise FilterError("Sesja filtra Okapi nie jest aktywna.")


def _unit_from_host(value: object) -> OkapiUnit:
    if not isinstance(value, dict):
        raise FilterError("Filter Host zwrócił nieprawidłową jednostkę.")
    unit_id = value.get("id")
    source = value.get("source")
    if not isinstance(unit_id, str) or not unit_id:
        raise FilterError("Jednostka Okapi ma nieprawidłowe id.")
    if not isinstance(source, str):
        raise FilterError(f"Jednostka Okapi {unit_id!r} ma nieprawidłowe source.")

    metadata = {key: item for key, item in value.items() if key not in {"id", "source"}}
    metadata["code_count"] = _count_codes(value)
    return OkapiUnit(id=unit_id, source=source, metadata=metadata)


def _count_codes(value: object) -> int:
    if not isinstance(value, dict):
        return 0
    parts = value.get("parts")
    if not isinstance(parts, list):
        return 0
    count = 0
    for part in parts:
        if isinstance(part, dict) and isinstance(part.get("codes"), list):
            count += len(part["codes"])
    return count


def _default_host_command(filter_store: Path | None = None) -> tuple[str, ...]:
    root = Path(__file__).resolve().parents[2]
    launcher = root / "resources" / "filter-host" / "run.sh"
    if os.name == "nt":
        raise FilterError("Domyślny Filter Host wymaga launchera POSIX; podaj command dla środowiska Windows.")
    shared = root / "resources" / "okapi-runtime" / "lib"
    command = ["env", f"TLUMACZ_FILTER_SHARED_LIBS={shared}"]
    if filter_store is not None:
        command.append(f"TLUMACZ_FILTER_STORE={filter_store}")
    command.extend(["bash", str(launcher)])
    return tuple(command)


__all__ = ["OkapiFilter", "OkapiSession", "OkapiUnit"]
