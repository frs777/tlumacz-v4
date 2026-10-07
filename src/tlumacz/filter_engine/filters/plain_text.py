"""Natywny filtr prostego tekstu bez zależności od Okapi."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from tlumacz.domain.errors import FilterError


@dataclass(slots=True)
class PlainTextUnit:
    id: str
    source: str
    metadata: dict[str, str]


@dataclass(slots=True)
class PlainTextSession:
    input_path: Path
    source_language: str
    target_language: str
    lines: list[str]
    units: list[PlainTextUnit] = field(default_factory=list)


class PlainTextFilter:
    """Filtruje zwykły tekst bez uruchamiania Okapi."""

    _SUFFIXES = (".txt", ".text", ".log")

    def capabilities(self) -> dict[str, object]:
        return {
            "name": "plain-text",
            "suffixes": self._SUFFIXES,
            "backend": "native",
        }

    def probe(self, input_path: Path) -> bool:
        path = Path(input_path)
        if path.suffix.lower() not in self._SUFFIXES or not path.is_file():
            return False
        try:
            path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return False
        return True

    def open(
        self,
        input_path: Path,
        *,
        source_language: str,
        target_language: str,
        workspace: Path,
    ) -> PlainTextSession:
        path = Path(input_path)
        if not self.probe(path):
            raise FilterError(f"Nieprawidłowy dokument tekstowy: {path}")
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        Path(workspace).mkdir(parents=True, exist_ok=True)
        return PlainTextSession(path, source_language, target_language, lines)

    def extract(self, session: PlainTextSession) -> list[PlainTextUnit]:
        units: list[PlainTextUnit] = []
        for index, line in enumerate(session.lines):
            source = line.rstrip("\r\n")
            if not source.strip():
                continue
            unit_id = "txt-" + hashlib.sha256(
                f"{session.input_path}:{index}".encode("utf-8")
            ).hexdigest()[:16]
            units.append(
                PlainTextUnit(
                    id=unit_id,
                    source=source,
                    metadata={
                        "format": "plain-text",
                        "line": str(index),
                        "source_sha256": _hash(source),
                        "kind": "line",
                    },
                )
            )
        session.units = units
        return list(units)

    def write(
        self,
        session: PlainTextSession,
        targets: dict[str, str],
        output_path: Path,
    ) -> Path:
        if set(targets) != {unit.id for unit in session.units}:
            raise FilterError("Niepełny zestaw targetów tekstu prostego.")
        lines = list(session.lines)
        for unit in session.units:
            index = int(unit.metadata["line"])
            current = lines[index].rstrip("\r\n")
            if _hash(current) != unit.metadata["source_sha256"]:
                raise FilterError(f"Źródło tekstu zmieniło się dla jednostki {unit.id}")
            newline = "\n" if lines[index].endswith("\n") else ""
            lines[index] = f"{targets[unit.id]}{newline}"
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("".join(lines), encoding="utf-8")
        return output

    def close(self, session: PlainTextSession) -> None:
        session.units.clear()


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = ["PlainTextFilter", "PlainTextSession", "PlainTextUnit"]
