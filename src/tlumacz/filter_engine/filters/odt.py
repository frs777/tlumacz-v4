"""ODT/OpenDocument Text filter with deterministic XML mapping."""

from __future__ import annotations

import hashlib
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

from tlumacz.domain.errors import FilterError

OFFICE_NS = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
TEXT_NS = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


@dataclass(slots=True)
class OdtUnit:
    id: str
    source: str
    metadata: dict[str, str]


@dataclass(slots=True)
class OdtSession:
    input_path: Path
    source_language: str
    target_language: str
    files: dict[str, bytes]
    root: ET.Element
    units: list[OdtUnit] = field(default_factory=list)


class OdtFilter:
    """Read and write content.xml while preserving other ODT resources."""

    def capabilities(self) -> dict[str, object]:
        return {"name": "odt", "suffixes": (".odt",)}

    def probe(self, input_path: Path) -> bool:
        path = Path(input_path)
        if path.suffix.lower() != ".odt" or not path.is_file():
            return False
        try:
            with zipfile.ZipFile(path) as archive:
                return "content.xml" in archive.namelist()
        except zipfile.BadZipFile:
            return False

    def open(
        self,
        input_path: Path,
        *,
        source_language: str,
        target_language: str,
        workspace: Path,
    ) -> OdtSession:
        path = Path(input_path)
        if not self.probe(path):
            raise FilterError(f"Nieprawidłowy dokument ODT: {path}")
        try:
            with zipfile.ZipFile(path) as archive:
                files = {
                    name: archive.read(name)
                    for name in archive.namelist()
                    if not name.endswith("/")
                }
            root = ET.fromstring(files["content.xml"])
        except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
            raise FilterError(f"Nie można odczytać dokumentu ODT: {path}") from exc
        Path(workspace).mkdir(parents=True, exist_ok=True)
        return OdtSession(
            input_path=path,
            source_language=source_language,
            target_language=target_language,
            files=files,
            root=root,
        )

    def extract(self, session: OdtSession) -> list[OdtUnit]:
        units: list[OdtUnit] = []
        for order, element in enumerate(_translatable_elements(session.root)):
            source = element.text or ""
            if not source.strip():
                continue
            path = _xpath(element, session.root)
            unit_id = "odt-" + hashlib.sha256(
                f"{session.input_path}:{path}".encode("utf-8")
            ).hexdigest()[:16]
            units.append(
                OdtUnit(
                    id=unit_id,
                    source=source,
                    metadata={
                        "format": "odt",
                        "path": "content.xml",
                        "xpath": path,
                        "order": str(order),
                        "source_sha256": _hash(source),
                    },
                )
            )
        session.units = units
        return list(units)

    def write(
        self,
        session: OdtSession,
        targets: dict[str, str],
        output_path: Path,
    ) -> Path:
        if set(targets) != {unit.id for unit in session.units}:
            raise FilterError("Niepełny zestaw targetów ODT.")
        for unit in session.units:
            element = _find(session.root, unit.metadata["xpath"])
            current = element.text or ""
            if _hash(current) != unit.metadata["source_sha256"]:
                raise FilterError(f"ODT source changed for unit {unit.id}")
            element.text = targets[unit.id]

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in session.files.items():
                if name == "content.xml":
                    data = ET.tostring(
                        session.root,
                        encoding="utf-8",
                        xml_declaration=True,
                    )
                archive.writestr(name, data)
        return output

    def close(self, session: OdtSession) -> None:
        session.units.clear()


def _translatable_elements(root: ET.Element) -> list[ET.Element]:
    return [
        element
        for element in root.iter()
        if isinstance(element.tag, str)
        and element.tag.startswith(f"{{{TEXT_NS}}}")
        and element.text
        and element.text.strip()
    ]


def _xpath(element: ET.Element, root: ET.Element) -> str:
    parts: list[str] = []
    current: ET.Element | None = element
    while current is not None:
        parent = _parent(root, current)
        siblings = (
            [child for child in list(parent) if child.tag == current.tag]
            if parent is not None
            else [current]
        )
        parts.append(f"{_local_name(current.tag)}[{siblings.index(current) + 1}]")
        if parent is None:
            break
        current = parent
    return "/" + "/".join(reversed(parts))


def _find(root: ET.Element, path: str) -> ET.Element:
    parts = [part for part in path.split("/") if part]
    current = root
    if not parts or _local_name(current.tag) != parts[0].split("[", 1)[0]:
        raise FilterError(f"Nieprawidłowa ścieżka ODT: {path}")
    for part in parts[1:]:
        name, _, index_text = part.partition("[")
        index = int(index_text.rstrip("]"))
        children = [child for child in list(current) if _local_name(child.tag) == name]
        if index < 1 or index > len(children):
            raise FilterError(f"Nie znaleziono elementu ODT: {path}")
        current = children[index - 1]
    return current


def _parent(root: ET.Element, target: ET.Element) -> ET.Element | None:
    if root is target:
        return None
    for element in root.iter():
        if target in list(element):
            return element
    return None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = ["OdtFilter", "OdtSession", "OdtUnit"]
