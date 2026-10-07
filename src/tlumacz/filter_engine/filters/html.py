"""HTML filter with deterministic text-slot mapping."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lxml import html  # type: ignore[import-untyped]

from tlumacz.domain.errors import FilterError

_SKIP_TAGS = {"script", "style", "head", "meta", "link", "title"}


@dataclass(slots=True)
class HtmlUnit:
    id: str
    source: str
    metadata: dict[str, str]


@dataclass(slots=True)
class HtmlSession:
    input_path: Path
    source_language: str
    target_language: str
    raw: str
    root: Any
    doctype: str
    units: list[HtmlUnit] = field(default_factory=list)


class HtmlFilter:
    """Extract and replace visible HTML text without touching excluded tags."""

    def capabilities(self) -> dict[str, object]:
        return {"name": "html", "suffixes": (".html", ".htm", ".xhtml")}

    def probe(self, input_path: Path) -> bool:
        path = Path(input_path)
        if path.suffix.lower() not in {".html", ".htm", ".xhtml"}:
            return False
        if not path.is_file():
            return False
        try:
            html.fromstring(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            return False
        return True

    def open(
        self,
        input_path: Path,
        *,
        source_language: str,
        target_language: str,
        workspace: Path,
    ) -> HtmlSession:
        path = Path(input_path)
        if not self.probe(path):
            raise FilterError(f"Nieprawidłowy dokument HTML: {path}")
        raw = path.read_text(encoding="utf-8")
        doctype_match = re.match(r"\s*(<!DOCTYPE[^>]*>)", raw, re.IGNORECASE)
        doctype = doctype_match.group(1) if doctype_match else ""
        parser = html.HTMLParser(remove_comments=False, recover=True, encoding="utf-8")
        parsed = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", raw, count=1, flags=re.I)
        root = html.fromstring(parsed, parser=parser)
        Path(workspace).mkdir(parents=True, exist_ok=True)
        return HtmlSession(
            input_path=path,
            source_language=source_language,
            target_language=target_language,
            raw=raw,
            root=root,
            doctype=doctype,
        )

    def extract(self, session: HtmlSession) -> list[HtmlUnit]:
        units: list[HtmlUnit] = []
        for order, (element, slot, text) in enumerate(_text_slots(session.root)):
            path = _xpath(element, session.root)
            unit_id = "html-" + hashlib.sha256(
                f"{session.input_path}:{path}:{slot}".encode("utf-8")
            ).hexdigest()[:16]
            units.append(
                HtmlUnit(
                    id=unit_id,
                    source=text,
                    metadata={
                        "format": "html",
                        "path": str(session.input_path),
                        "xpath": path,
                        "slot": slot,
                        "order": str(order),
                        "source_sha256": _hash(text),
                    },
                )
            )
        session.units = units
        return list(units)

    def write(
        self,
        session: HtmlSession,
        targets: dict[str, str],
        output_path: Path,
    ) -> Path:
        expected = {unit.id for unit in session.units}
        if set(targets) != expected:
            raise FilterError("Niepełny zestaw targetów HTML.")

        for unit in session.units:
            element = _find(session.root, unit.metadata["xpath"])
            slot = unit.metadata["slot"]
            current = element.text if slot == "text" else element.tail
            if current is None or _hash(current) != unit.metadata["source_sha256"]:
                raise FilterError(f"HTML source changed for unit {unit.id}")
            if slot == "text":
                element.text = targets[unit.id]
            elif slot == "tail":
                element.tail = targets[unit.id]
            else:
                raise FilterError(f"Nieznany slot HTML: {slot}")

        result = html.tostring(session.root, encoding="unicode", method="html")
        if session.doctype:
            result = session.doctype + "\n" + result
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result, encoding="utf-8")
        return output

    def close(self, session: HtmlSession) -> None:
        session.units.clear()


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _local_name(tag: object) -> str:
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def _text_slots(root: Any) -> list[tuple[Any, str, str]]:
    slots: list[tuple[Any, str, str]] = []
    for element in root.iter():
        if not isinstance(element.tag, str) or _local_name(element.tag) in _SKIP_TAGS:
            continue
        if element.text and element.text.strip():
            slots.append((element, "text", element.text))
        if element.tail and element.tail.strip():
            slots.append((element, "tail", element.tail))
    return slots


def _xpath(element: Any, root: Any) -> str:
    parts: list[str] = []
    current = element
    while current is not None and current.getparent() is not None:
        parent = current.getparent()
        siblings = [
            child for child in parent
            if _local_name(child.tag) == _local_name(current.tag)
        ]
        parts.append(f"{_local_name(current.tag)}[{siblings.index(current) + 1}]")
        if parent is root:
            parts.append(_local_name(root.tag))
            break
        current = parent
    return "/" + "/".join(reversed(parts))


def _find(root: Any, path: str) -> Any:
    parts = [part for part in path.split("/") if part]
    current = root
    if not parts or _local_name(current.tag) != parts[0].split("[", 1)[0]:
        raise FilterError(f"Nieprawidłowy XPath HTML: {path}")
    for part in parts[1:]:
        name, _, index_text = part.partition("[")
        index = int(index_text.rstrip("]"))
        children = [
            child for child in current
            if _local_name(child.tag) == name
        ]
        if index < 1 or index > len(children):
            raise FilterError(f"Nie znaleziono elementu HTML: {path}")
        current = children[index - 1]
    return current


__all__ = ["HtmlFilter", "HtmlSession", "HtmlUnit"]
