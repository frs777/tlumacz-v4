"""EPUB filter preserving the ZIP package and XHTML structure."""

from __future__ import annotations

import hashlib
import posixpath
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

from tlumacz.domain.errors import FilterError

XHTML_NS = "http://www.w3.org/1999/xhtml"
SKIP_TAGS = {"script", "style", "head", "meta", "link", "title"}


@dataclass(slots=True)
class EpubUnit:
    id: str
    source: str
    metadata: dict[str, str]


@dataclass(slots=True)
class EpubSession:
    input_path: Path
    source_language: str
    target_language: str
    files: dict[str, bytes]
    documents: dict[str, ET.Element]
    units: list[EpubUnit] = field(default_factory=list)


class EpubFilter:
    """Extract XHTML text slots from an EPUB and rebuild the package."""

    def capabilities(self) -> dict[str, object]:
        return {"name": "epub", "suffixes": (".epub",)}

    def probe(self, input_path: Path) -> bool:
        path = Path(input_path)
        if path.suffix.lower() != ".epub" or not path.is_file():
            return False
        try:
            with zipfile.ZipFile(path) as archive:
                return bool(_xhtml_paths({name: archive.read(name) for name in archive.namelist()}))
        except (OSError, zipfile.BadZipFile):
            return False

    def open(
        self,
        input_path: Path,
        *,
        source_language: str,
        target_language: str,
        workspace: Path,
    ) -> EpubSession:
        path = Path(input_path)
        if not self.probe(path):
            raise FilterError(f"Nieprawidłowy dokument EPUB: {path}")
        try:
            with zipfile.ZipFile(path) as archive:
                files = {name: archive.read(name) for name in archive.namelist()}
            documents = {name: ET.fromstring(files[name]) for name in _xhtml_paths(files)}
        except (zipfile.BadZipFile, ET.ParseError, KeyError) as exc:
            raise FilterError(f"Nie można odczytać dokumentu EPUB: {path}") from exc
        Path(workspace).mkdir(parents=True, exist_ok=True)
        return EpubSession(path, source_language, target_language, files, documents)

    def extract(self, session: EpubSession) -> list[EpubUnit]:
        units: list[EpubUnit] = []
        for path, root in session.documents.items():
            for order, element in enumerate(root.iter()):
                if not isinstance(element.tag, str):
                    continue
                if _local_name(element.tag) in SKIP_TAGS:
                    continue
                source = element.text or ""
                if not source.strip():
                    continue
                xpath = _xpath(element, root)
                unit_id = (
                    "epub-" + hashlib.sha256(f"{path}:{xpath}".encode("utf-8")).hexdigest()[:16]
                )
                units.append(
                    EpubUnit(
                        unit_id,
                        source,
                        {
                            "format": "epub",
                            "path": path,
                            "xpath": xpath,
                            "order": str(order),
                            "source_sha256": _hash(source),
                        },
                    )
                )
        session.units = units
        return list(units)

    def write(
        self,
        session: EpubSession,
        targets: dict[str, str],
        output_path: Path,
    ) -> Path:
        if set(targets) != {unit.id for unit in session.units}:
            raise FilterError("Niepełny zestaw targetów EPUB.")
        for unit in session.units:
            root = session.documents[unit.metadata["path"]]
            element = _find(root, unit.metadata["xpath"])
            current = element.text or ""
            if _hash(current) != unit.metadata["source_sha256"]:
                raise FilterError(f"EPUB source changed for unit {unit.id}")
            element.text = targets[unit.id]

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            if "mimetype" in session.files:
                archive.writestr(
                    "mimetype",
                    session.files["mimetype"],
                    compress_type=zipfile.ZIP_STORED,
                )
            for name, data in session.files.items():
                if name == "mimetype":
                    continue
                if name in session.documents:
                    data = ET.tostring(
                        session.documents[name],
                        encoding="utf-8",
                        xml_declaration=True,
                    )
                archive.writestr(name, data)
        return output

    def close(self, session: EpubSession) -> None:
        session.units.clear()
        session.documents.clear()


def _xhtml_paths(files: dict[str, bytes]) -> list[str]:
    paths = [name for name in files if name.lower().endswith((".xhtml", ".html", ".htm"))]
    if not paths:
        return []
    try:
        container = ET.fromstring(files["META-INF/container.xml"])
        ns = "{urn:oasis:names:tc:opendocument:xmlns:container}"
        rootfile = container.find(f".//{ns}rootfile")
        opf_path = rootfile.get("full-path") if rootfile is not None else None
        if not opf_path or opf_path not in files:
            return sorted(paths)
        opf = ET.fromstring(files[opf_path])
        opf_ns = "{http://www.idpf.org/2007/opf}"
        manifest = {
            item.get("id"): item.get("href")
            for item in opf.findall(f".//{opf_ns}manifest/{opf_ns}item")
        }
        base = posixpath.dirname(opf_path)
        ordered: list[str] = []
        for ref in opf.findall(f".//{opf_ns}spine/{opf_ns}itemref"):
            href = manifest.get(ref.get("idref"))
            if not href:
                continue
            path = posixpath.normpath(posixpath.join(base, href.split("#", 1)[0]))
            if path in files and path in paths and path not in ordered:
                ordered.append(path)
        return ordered + sorted(path for path in paths if path not in ordered)
    except (ET.ParseError, KeyError, ValueError):
        return sorted(paths)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _xpath(element: ET.Element, root: ET.Element) -> str:
    parts: list[str] = []
    current: ET.Element | None = element
    while current is not None:
        parent = _parent(root, current)
        siblings = [child for child in list(parent)] if parent is not None else [current]
        same = [child for child in siblings if _local_name(child.tag) == _local_name(current.tag)]
        parts.append(f"{_local_name(current.tag)}[{same.index(current) + 1}]")
        if parent is None:
            break
        current = parent
    return "/" + "/".join(reversed(parts))


def _parent(root: ET.Element, target: ET.Element) -> ET.Element | None:
    if root is target:
        return None
    for element in root.iter():
        if target in list(element):
            return element
    return None


def _find(root: ET.Element, path: str) -> ET.Element:
    parts = [part for part in path.split("/") if part]
    current = root
    if not parts or _local_name(current.tag) != parts[0].split("[", 1)[0]:
        raise FilterError(f"Nieprawidłowa ścieżka EPUB: {path}")
    for part in parts[1:]:
        name, _, index_text = part.partition("[")
        index = int(index_text.rstrip("]"))
        children = [child for child in list(current) if _local_name(child.tag) == name]
        if index < 1 or index > len(children):
            raise FilterError(f"Nie znaleziono elementu EPUB: {path}")
        current = children[index - 1]
    return current


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = ["EpubFilter", "EpubSession", "EpubUnit"]
