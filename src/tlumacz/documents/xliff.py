"""XLIFF 2.0 filter."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

from tlumacz.domain.errors import FilterError

XLIFF_NS = "urn:oasis:names:tc:xliff:document:2.0"
UNIT = f"{{{XLIFF_NS}}}unit"
SOURCE = f"{{{XLIFF_NS}}}source"
TARGET = f"{{{XLIFF_NS}}}target"


@dataclass(slots=True)
class XliffUnit:
    id: str
    source: str
    metadata: dict[str, str]


@dataclass(slots=True)
class XliffSession:
    input_path: Path
    source_language: str
    target_language: str
    root: ET.Element
    units: list[XliffUnit] = field(default_factory=list)


class XliffFilter:
    """Extract XLIFF 2.0 source segments and write targets in place."""

    def capabilities(self) -> dict[str, object]:
        return {"name": "xliff", "suffixes": (".xlf", ".xliff")}

    def probe(self, input_path: Path) -> bool:
        path = Path(input_path)
        if path.suffix.lower() not in {".xlf", ".xliff"} or not path.is_file():
            return False
        try:
            root = ET.parse(path).getroot()
        except (OSError, ET.ParseError):
            return False
        return root.tag == f"{{{XLIFF_NS}}}xliff" and root.get("version") == "2.0"

    def open(
        self,
        input_path: Path,
        *,
        source_language: str,
        target_language: str,
        workspace: Path,
    ) -> XliffSession:
        path = Path(input_path)
        if not self.probe(path):
            raise FilterError(f"Nieprawidłowy dokument XLIFF: {path}")
        try:
            root = ET.parse(path).getroot()
            file_element = root.find(f"{{{XLIFF_NS}}}file")
            if file_element is None:
                raise ValueError("brak file")
        except (OSError, ET.ParseError, ValueError) as exc:
            raise FilterError(f"Nie można odczytać dokumentu XLIFF: {path}") from exc
        Path(workspace).mkdir(parents=True, exist_ok=True)
        return XliffSession(path, source_language, target_language, root)

    def extract(self, session: XliffSession) -> list[XliffUnit]:
        units: list[XliffUnit] = []
        for element in session.root.findall(f".//{UNIT}"):
            unit_id = element.get("id")
            source = element.find(f".//{SOURCE}")
            if not unit_id or source is None or not (source.text or "").strip():
                continue
            text = source.text or ""
            units.append(
                XliffUnit(
                    unit_id,
                    text,
                    {
                        "format": "xliff",
                        "unit_id": unit_id,
                        "source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    },
                )
            )
        session.units = units
        return list(units)

    def write(
        self,
        session: XliffSession,
        targets: dict[str, str],
        output_path: Path,
    ) -> Path:
        if set(targets) != {unit.id for unit in session.units}:
            raise FilterError("Niepełny zestaw targetów XLIFF.")
        for unit in session.units:
            unit_element = next(
                element for element in session.root.findall(f".//{UNIT}")
                if element.get("id") == unit.id
            )
            source = unit_element.find(f".//{SOURCE}")
            if source is None or (source.text or "") != unit.source:
                raise FilterError(f"XLIFF source changed for unit {unit.id}")
            target = unit_element.find(f".//{TARGET}")
            if target is None:
                segment = unit_element.find(f".//{{{XLIFF_NS}}}segment")
                if segment is None:
                    raise FilterError(f"XLIFF unit has no segment: {unit.id}")
                target = ET.SubElement(segment, TARGET)
            target.text = targets[unit.id]

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        ET.register_namespace("", XLIFF_NS)
        ET.ElementTree(session.root).write(
            output,
            encoding="utf-8",
            xml_declaration=True,
        )
        return output

    def close(self, session: XliffSession) -> None:
        session.units.clear()


__all__ = ["XliffFilter", "XliffSession", "XliffUnit"]
