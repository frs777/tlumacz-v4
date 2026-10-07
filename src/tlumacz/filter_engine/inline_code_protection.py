"""Ochrona markerów inline Okapi na granicy z backendem tłumaczeniowym."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .marker_validator import MarkerValidator


class InlineCodeProtectionError(ValueError):
    """Backend zmienił integralność chronionych markerów inline."""


@dataclass(frozen=True, slots=True)
class ProtectedInlineText:
    """Tekst z markerami Okapi zastąpionymi stabilnymi tokenami ASCII."""

    text: str
    markers: tuple[str, ...]
    originals: tuple[str, ...]


_TOKEN_RE = re.compile(r"__OKAPI_CODE_(\d+)__")


def protect_inline_codes(text: str) -> ProtectedInlineText:
    """Zamień markery PUA Okapi na tokeny ASCII przed wywołaniem backendu."""
    if not isinstance(text, str):
        raise TypeError("Tekst do ochrony markerów musi być tekstem.")

    MarkerValidator.validate(text)
    markers: list[str] = []
    originals: list[str] = []
    output: list[str] = []
    index = 0

    while index < len(text):
        char = text[index]
        if char not in {
            MarkerValidator.MARKER_OPENING,
            MarkerValidator.MARKER_CLOSING,
            MarkerValidator.MARKER_ISOLATED,
        }:
            output.append(char)
            index += 1
            continue

        if index + 1 >= len(text):
            raise InlineCodeProtectionError("Marker inline nie ma znaku indeksu.")
        original = text[index : index + 2]
        token = f"__OKAPI_CODE_{len(markers)}__"
        markers.append(token)
        originals.append(original)
        output.append(token)
        index += 2

    protected = "".join(output)
    if markers and _TOKEN_RE.search(text):
        raise InlineCodeProtectionError(
            "Tekst źródłowy zawiera zarezerwowany token __OKAPI_CODE_N__; "
            "nie można bezpiecznie rozróżnić go od markera transportowego."
        )

    return ProtectedInlineText(
        text=protected,
        markers=tuple(markers),
        originals=tuple(originals),
    )


def restore_inline_codes(text: str, protected: ProtectedInlineText) -> str:
    """Przywróć markery PUA po zweryfikowaniu odpowiedzi backendu."""
    if not isinstance(text, str):
        raise TypeError("Odpowiedź backendu musi być tekstem.")

    matches = list(_TOKEN_RE.finditer(text))
    expected = list(protected.markers)
    actual = [match.group(0) for match in matches]

    if actual != expected:
        raise InlineCodeProtectionError(
            "Backend zmodyfikował lub zgubił markery inline Filter Engine: "
            f"oczekiwano={expected!r}, otrzymano={actual!r}."
        )

    restored: list[str] = []
    cursor = 0
    for match, original in zip(matches, protected.originals):
        restored.append(text[cursor : match.start()])
        restored.append(original)
        cursor = match.end()
    restored.append(text[cursor:])
    return "".join(restored)


__all__ = [
    "InlineCodeProtectionError",
    "ProtectedInlineText",
    "protect_inline_codes",
    "restore_inline_codes",
]
