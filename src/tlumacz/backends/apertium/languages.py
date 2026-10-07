"""Mapowanie kodów ISO używanych przez aplikację na kody Apertium."""

from __future__ import annotations

from .errors import ApertiumValidationError

# Mapowanie jest jawne, ponieważ kod par Apertium nie zawsze jest kodem ISO
# 639-1. Lista będzie rozszerzana dopiero po potwierdzeniu konkretnej pary.
APERTIUM_LANGUAGE_CODES: dict[str, str] = {
    "ca": "cat",
    "cs": "ces",
    "de": "deu",
    "en": "eng",
    "eo": "epo",
    "es": "spa",
    "fr": "fra",
    "it": "ita",
    "lt": "lit",
    "lv": "lav",
    "nl": "nld",
    "pl": "pol",
    "pt": "por",
    "ru": "rus",
    "sk": "slk",
    "uk": "ukr",
}

APERTIUM_LANGUAGE_NAMES: dict[str, str] = {
    "Catalan": "ca",
    "Czech": "cs",
    "German": "de",
    "English": "en",
    "Esperanto": "eo",
    "Spanish": "es",
    "French": "fr",
    "Italian": "it",
    "Lithuanian": "lt",
    "Latvian": "lv",
    "Dutch": "nl",
    "Polish": "pl",
    "Portuguese": "pt",
    "Russian": "ru",
    "Slovak": "sk",
    "Ukrainian": "uk",
}

def apertium_pair_to_iso(pair: str) -> tuple[str, str]:
    """Zamień parę Apertium, np. `eng-spa`, na kody ISO 639-1."""
    try:
        source, target = pair.casefold().split("-", 1)
    except ValueError as exc:
        raise ApertiumValidationError(f"Nieprawidłowa para Apertium: {pair!r}.") from exc
    reverse = {value: key for key, value in APERTIUM_LANGUAGE_CODES.items()}
    try:
        return reverse[source], reverse[target]
    except KeyError as exc:
        raise ApertiumValidationError(
            f"Nieznany kod języka w parze Apertium: {pair!r}."
        ) from exc

def build_language_pair_index(
    supported_pairs: tuple[str, ...] | list[str],
) -> dict[str, tuple[str, ...]]:
    """Zbuduj deterministyczny indeks logicznie dwukierunkowych par."""
    index: dict[str, set[str]] = {}
    for pair in supported_pairs:
        try:
            source, target = pair.casefold().split("-", 1)
            source = normalize_language_code(source)
            target = normalize_language_code(target)
        except (ApertiumValidationError, ValueError):
            continue
        if source == target:
            continue
        index.setdefault(source, set()).add(target)
        index.setdefault(target, set()).add(source)

    return {
        source: tuple(sorted(targets))
        for source, targets in sorted(index.items())
    }


def supported_targets_for_source(
    source_language: str, supported_pairs: tuple[str, ...] | list[str]
) -> tuple[str, ...]:
    """Zwróć docelowe kody ISO z indeksu logicznie dwukierunkowych par."""
    source = normalize_language_code(source_language)
    reverse_codes = {value: key for key, value in APERTIUM_LANGUAGE_CODES.items()}
    index = build_language_pair_index(supported_pairs)
    return tuple(
        reverse_codes[target]
        for target in index.get(source, ())
        if target in reverse_codes
    )


def normalize_language_code(code: str) -> str:
    """Znormalizuj kod ISO 639-1/639-3 do kodu Apertium."""
    normalized = code.strip().casefold()
    if not normalized:
        raise ApertiumValidationError("Kod języka nie może być pusty.")
    if normalized in APERTIUM_LANGUAGE_CODES.values():
        return normalized
    try:
        return APERTIUM_LANGUAGE_CODES[normalized]
    except KeyError as exc:
        raise ApertiumValidationError(
            f"Nieznany kod języka Apertium: {code!r}."
        ) from exc


def build_language_pair(source_language: str, target_language: str) -> str:
    """Zbuduj kierunkowy identyfikator pary, np. ``eng-pol``."""
    source = normalize_language_code(source_language)
    target = normalize_language_code(target_language)
    if source == target:
        raise ApertiumValidationError("Język źródłowy i docelowy muszą być różne.")
    return f"{source}-{target}"
