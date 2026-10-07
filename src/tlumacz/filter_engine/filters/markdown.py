
"""Deterministyczny filtr Markdown zachowujący bloki kodu."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from tlumacz.domain.errors import FilterError


def _frontmatter_indexes(lines: list[str]) -> set[int]:
    """Zwróć indeksy YAML front matter znajdującego się na początku Markdown."""
    if not lines or lines[0].strip() != "---":
        return set()
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return set(range(index + 1))
    return set()


@dataclass(slots=True)
class MarkdownUnit:
    id: str
    source: str
    metadata: dict[str, str]


@dataclass(slots=True)
class MarkdownSession:
    input_path: Path
    source_language: str
    target_language: str
    lines: list[str]
    units: list[MarkdownUnit] = field(default_factory=list)
    skipped_fragments: list[str] = field(default_factory=list)


class MarkdownFilter:
    """Traktuj linie poza blokami kodu jako jednostki tłumaczeniowe."""

    def capabilities(self) -> dict[str, object]:
        return {"name": "markdown", "suffixes": (".md", ".markdown")}

    def probe(self, input_path: Path) -> bool:
        path = Path(input_path)
        if path.suffix.lower() not in {".md", ".markdown"} or not path.is_file():
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
    ) -> MarkdownSession:
        path = Path(input_path)
        if not self.probe(path):
            raise FilterError(f"Nieprawidłowy dokument Markdown: {path}")
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        Path(workspace).mkdir(parents=True, exist_ok=True)
        return MarkdownSession(path, source_language, target_language, lines)

    def extract(self, session: MarkdownSession) -> list[MarkdownUnit]:
        units: list[MarkdownUnit] = []
        skipped_fragments: list[str] = []
        fenced = False
        fence_start = -1
        marked_delimiter: str | None = None
        marked_lines: list[str] = []
        frontmatter = _frontmatter_indexes(session.lines)
        if frontmatter:
            skipped_fragments.append("".join(session.lines[index] for index in sorted(frontmatter)).rstrip("\r\n"))

        metadata_re = re.compile(r"^\s*(name|license|author|metadata|version|tags|created|updated)\s*:")
        for index, line in enumerate(session.lines):
            if index in frontmatter:
                continue
            stripped = line.lstrip()
            if fenced:
                if stripped.startswith("```") or stripped.startswith("~~~"):
                    block = "".join(session.lines[fence_start : index + 1]).rstrip("\r\n")
                    skipped_fragments.append(block)
                    fenced = False
                    fence_start = -1
                continue
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = "```" if stripped.startswith("```") else "~~~"
                if stripped.find(fence, len(fence)) >= 0:
                    skipped_fragments.append(line.rstrip("\r\n"))
                else:
                    fenced = True
                    fence_start = index
                continue

            source = line.rstrip("\r\n")
            if marked_delimiter is not None:
                marked_lines.append(source)
                if marked_delimiter in source:
                    skipped_fragments.append("\n".join(marked_lines))
                    marked_lines = []
                    marked_delimiter = None
                continue
            if not line.strip():
                continue
            if metadata_re.search(line) or _is_syntax_only(source):
                skipped_fragments.append(source)
                continue
            delimiter = _opening_markdown_delimiter(source)
            if delimiter is not None and source.count(delimiter) % 2 == 1:
                marked_delimiter = delimiter
                marked_lines = [source]
                continue
            if _is_marked_fragment(source):
                skipped_fragments.append(source)
                continue
            unit_id = (
                "md-" + hashlib.sha256(f"{session.input_path}:{index}".encode()).hexdigest()[:16]
            )
            units.append(
                MarkdownUnit(
                    unit_id,
                    source,
                    {
                        "format": "markdown",
                        "line": str(index),
                        "source_sha256": _hash(source),
                        "prefix": "",
                        "wrapper": "",
                        "kind": "paragraph",
                    },
                )
            )
        if fenced and fence_start >= 0:
            skipped_fragments.append("".join(session.lines[fence_start:]).rstrip("\r\n"))
        if marked_lines:
            skipped_fragments.append("\n".join(marked_lines))
        session.units = units
        session.skipped_fragments = skipped_fragments
        return list(units)

    def write(
        self,
        session: MarkdownSession,
        targets: dict[str, str],
        output_path: Path,
    ) -> Path:
        if set(targets) != {unit.id for unit in session.units}:
            raise FilterError("Niepełny zestaw targetów Markdown.")
        lines = list(session.lines)
        for unit in session.units:
            index = int(unit.metadata["line"])
            current = lines[index].rstrip("\r\n")
            if _hash(current) != unit.metadata["source_sha256"]:
                raise FilterError(f"Markdown source changed for unit {unit.id}")
            translated = targets[unit.id]
            prefix = unit.metadata.get("prefix", "")
            wrapper = unit.metadata.get("wrapper", "")
            if wrapper:
                translated = f"{wrapper}{translated}{wrapper}"
            newline = "\n" if lines[index].endswith("\n") else ""
            lines[index] = f"{prefix}{translated}{newline}"
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("".join(lines), encoding="utf-8")
        return output

    def close(self, session: MarkdownSession) -> None:
        session.units.clear()
        session.skipped_fragments.clear()


def _is_syntax_only(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and (stripped in {"---", "***", "___"} or all(ch in "-*_=~" for ch in stripped))


def _split_markdown_syntax(source: str) -> tuple[str, str, str]:
    """Oddziel podstawowe znaczniki blokowe od tekstu wysyłanego do tłumacza."""
    import re

    prefix = ""
    body = source
    match = re.match(r"^(\s*(?:#{1,6}\s+|[-+*]\s+|\d+[.)]\s+|>\s?))(.+)$", body)
    if match:
        prefix, body = match.group(1), match.group(2)
    wrapper = ""
    for marker in ("**", "__", "*", "_"):
        if body.startswith(marker) and body.endswith(marker) and len(body) > 2 * len(marker):
            wrapper = marker
            body = body[len(marker):-len(marker)]
            break
    return body, prefix, wrapper


def _is_marked_fragment(line: str) -> bool:
    """Rozpoznaj tekst jawnie oznaczony składnią Markdown jako pomijany przez filtr."""
    patterns = (
        r"^\s*#{1,6}\s+.+$",
        r"`[^`]+`",
        r"\*\*[^*]+\*\*",
        r"__[^_]+__",
        r"(?<!\*)\*[^*\n]+\*(?!\*)",
        r"(?<!\w)_[^_\n]+_(?!\w)",
        r"!?\[[^\]]+\]\([^\)]+\)",
    )
    return any(re.search(pattern, line) is not None for pattern in patterns)


def _opening_markdown_delimiter(line: str) -> str | None:
    """Zwróć znacznik otwierający wieloliniowy fragment Markdown."""
    for delimiter in ("**", "__", "`", "*", "_"):
        if delimiter in line and line.count(delimiter) % 2 == 1:
            return delimiter
    return None


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = ["MarkdownFilter", "MarkdownSession", "MarkdownUnit"]
