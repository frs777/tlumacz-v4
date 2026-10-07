"""Validation of Okapi-style inline code markers."""

from __future__ import annotations

from tlumacz.domain.errors import FilterError


class MarkerValidator:
    """Validate the two-character representation of inline codes."""

    MARKER_OPENING = "\ue101"
    MARKER_CLOSING = "\ue102"
    MARKER_ISOLATED = "\ue103"
    INDEX_BASE = 0xE110

    @classmethod
    def validate(cls, text: str, *, code_count: int | None = None) -> str:
        index = 0
        while index < len(text):
            marker = text[index]
            if marker not in {
                cls.MARKER_OPENING,
                cls.MARKER_CLOSING,
                cls.MARKER_ISOLATED,
            }:
                if 0xE000 <= ord(marker) <= 0xF8FF:
                    raise FilterError(
                        f"Invalid inline marker index character at position {index}"
                    )
                index += 1
                continue

            if index + 1 >= len(text):
                raise FilterError("Inline marker is missing its index character")

            index_char = text[index + 1]
            code_index = ord(index_char) - cls.INDEX_BASE
            if code_index < 0:
                raise FilterError("Invalid inline marker index")

            if code_count is not None and code_index >= code_count:
                raise FilterError(
                    f"Inline marker index {code_index} is outside code table"
                )

            index += 2

        return text
