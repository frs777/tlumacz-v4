"""Minimal DOCX/OpenXML filter for the V4 Filter Engine."""

from __future__ import annotations

import hashlib
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import NamedTemporaryFile
from xml.etree import ElementTree as ET

from tlumacz.domain.errors import FilterError

DOCX_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W_T = f"{{{DOCX_NS}}}t"
ET.register_namespace("w", DOCX_NS)


@dataclass(slots=True)
class DocxUnit:
    """Neutral translation unit extracted from one DOCX text node."""

    id: str
    source: str
    metadata: dict[str, str]


@dataclass(slots=True)
class _DocxDocument:
    path: str
    root: ET.Element
    source_bytes: bytes


@dataclass(slots=True)
class DocxSession:
    """Mutable state owned by one DOCX filter session."""

    input_path: Path
    source_language: str
    target_language: str
    files: dict[str, bytes]
    documents: list[_DocxDocument] = field(default_factory=list)
    units: list[DocxUnit] = field(default_factory=list)


class DocxFilter:
    """Read and write the main WordprocessingML document part."""

    def capabilities(self) -> dict[str, object]:
        return {
            "name": "docx",
            "suffixes": (".docx",),
            "mime_type": (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
        }

    def probe(self, input_path: Path) -> bool:
        path = Path(input_path)
        if path.suffix.lower() != ".docx" or not path.is_file():
            return False
        try:
            with zipfile.ZipFile(path) as archive:
                return "word/document.xml" in archive.namelist()
        except zipfile.BadZipFile:
            return False

    def open(
        self,
        input_path: Path,
        *,
        source_language: str,
        target_language: str,
        workspace: Path,
    ) -> DocxSession:
        path = Path(input_path)
        if not self.probe(path):
            raise FilterError(f"Nieprawidłowy dokument DOCX: {path}")

        with zipfile.ZipFile(path) as archive:
            files = {
                name: archive.read(name)
                for name in archive.namelist()
                if not name.endswith("/")
            }

        try:
            root = ET.fromstring(files["word/document.xml"])
        except (ET.ParseError, KeyError) as exc:
            raise FilterError(f"Nie można odczytać word/document.xml: {path}") from exc

        session = DocxSession(
            input_path=path,
            source_language=source_language,
            target_language=target_language,
            files=files,
        )
        session.documents.append(
            _DocxDocument(
                path="word/document.xml",
                root=root,
                source_bytes=files["word/document.xml"],
            )
        )
        Path(workspace).mkdir(parents=True, exist_ok=True)
        return session

    def extract(self, session: DocxSession) -> list[DocxUnit]:
        units: list[DocxUnit] = []
        ordinal = 1

        for document in session.documents:
            for element, path in _iter_with_paths(document.root):
                if element.tag != W_T:
                    continue
                source = element.text or ""
                if not source.strip():
                    continue

                unit_id = (
                    "docx-"
                    + hashlib.sha1(
                        f"{document.path}:{path}".encode("utf-8")
                    ).hexdigest()[:16]
                )
                units.append(
                    DocxUnit(
                        id=unit_id,
                        source=source,
                        metadata={
                            "format": "docx",
                            "path": document.path,
                            "xpath": path,
                            "order": str(ordinal),
                            "source_sha256": hashlib.sha256(
                                source.encode("utf-8")
                            ).hexdigest(),
                        },
                    )
                )
                ordinal += 1

        session.units = units
        return list(units)


    def write(
        self,
        session: DocxSession,
        targets: dict[str, str],
        output_path: Path,
    ) -> Path:
        expected = {unit.id for unit in session.units}
        actual = set(targets)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise FilterError(
                f"Niepełny zestaw targetów DOCX: missing={missing!r}, extra={extra!r}"
            )

        for unit in session.units:
            if not isinstance(targets[unit.id], str):
                raise FilterError(f"Target DOCX musi być tekstem: {unit.id}")
            document = _document_for_unit(session, unit)
            element = _find_element(document.root, unit.metadata["xpath"])
            current = element.text or ""
            current_hash = hashlib.sha256(current.encode("utf-8")).hexdigest()
            if current_hash != unit.metadata["source_sha256"]:
                raise ValueError(f"DOCX source changed for unit {unit.id}")
            element.text = targets[unit.id]

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp:
            temporary = Path(temp.name)

        try:
            with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for name, data in session.files.items():
                    if name == "word/document.xml":
                        data = ET.tostring(
                            session.documents[0].root,
                            encoding="utf-8",
                            xml_declaration=True,
                        )
                    archive.writestr(name, data)
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)

        return output

    def close(self, session: DocxSession) -> None:
        session.documents.clear()
        session.units.clear()


def _iter_with_paths(
    root: ET.Element,
) -> list[tuple[ET.Element, str]]:
    result: list[tuple[ET.Element, str]] = []

    def visit(element: ET.Element, path: str) -> None:
        result.append((element, path))
        counts: dict[str, int] = {}
        for child in list(element):
            name = _local_name(child.tag)
            counts[name] = counts.get(name, 0) + 1
            visit(child, f"{path}/{name}[{counts[name]}]")

    visit(root, f"/{_local_name(root.tag)}[1]")
    return result


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _find_element(root: ET.Element, path: str) -> ET.Element:
    parts = [part for part in path.split("/") if part]
    if not parts:
        raise ValueError("Pusta ścieżka XML")

    current = root
    if _local_name(current.tag) != parts[0].split("[", 1)[0]:
        raise ValueError(f"Nieprawidłowy korzeń XML: {path}")

    for part in parts[1:]:
        name, _, index_text = part.partition("[")
        index = int(index_text.rstrip("]")) if index_text else 1
        children = [
            child
            for child in list(current)
            if _local_name(child.tag) == name
        ]
        if index < 1 or index > len(children):
            raise ValueError(f"Nie znaleziono elementu XML: {path}")
        current = children[index - 1]
    return current


def _document_for_unit(session: DocxSession, unit: DocxUnit) -> _DocxDocument:
    path = unit.metadata["path"]
    for document in session.documents:
        if document.path == path:
            return document
    raise ValueError(f"Nie znaleziono dokumentu dla jednostki: {unit.id}")


__all__ = ["DocxFilter", "DocxSession", "DocxUnit"]
