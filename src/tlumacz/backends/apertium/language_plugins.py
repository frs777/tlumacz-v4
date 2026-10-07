"""Wykrywanie lokalnych pakietów danych językowych Apertium."""

from __future__ import annotations

import os
import shlex
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ApertiumLanguagePlugin:
    """Opis jednej wtyczki danych językowych Apertium."""

    package_name: str
    root: Path
    modes: tuple[str, ...]
    compiled_modes: tuple[str, ...]


def _mode_requirements(root: Path, mode: ET.Element) -> tuple[Path, ...]:
    return tuple(
        root / filename
        for node in mode.findall(".//file")
        if (filename := node.get("name"))
        and not filename.startswith("$")
    )


def _mode_programs(mode: ET.Element) -> tuple[str, ...]:
    programs: list[str] = []
    for node in mode.findall(".//program"):
        name = node.get("name")
        if not name:
            continue
        try:
            command = shlex.split(name)[0]
        except ValueError:
            continue
        if command and command not in programs:
            programs.append(command)
    return tuple(programs)


def _available_programs(runtime_bin_dir: Path | None) -> set[str]:
    available: set[str] = set()

    if runtime_bin_dir is not None and runtime_bin_dir.is_dir():
        for candidate in runtime_bin_dir.iterdir():
            if candidate.is_file() and os.access(candidate, os.X_OK):
                available.add(candidate.name)

    for command in (
        "apertium",
        "apertium-anaphora",
        "apertium-interchunk",
        "apertium-postchunk",
        "apertium-pretransfer",
        "apertium-tagger",
        "apertium-transfer",
        "apertium-wblank-attach",
        "apertium-wblank-detach",
        "apertium-wblank-mode",
        "cg-proc",
        "lrx-proc",
        "lsx-proc",
        "lt-proc",
    ):
        if shutil.which(command):
            available.add(command)

    return available


def _parse_plugin(
    root: Path,
    *,
    runtime_bin_dir: Path | None = None,
) -> ApertiumLanguagePlugin | None:
    modes_file = root / "modes.xml"
    if not modes_file.is_file():
        return None
    try:
        document = ET.parse(modes_file)
    except ET.ParseError:
        return None

    available_programs = _available_programs(runtime_bin_dir)
    modes: list[str] = []
    compiled: list[str] = []
    for mode in document.getroot().findall("mode"):
        name = mode.get("name")
        if not name:
            continue
        modes.append(name)
        required = _mode_requirements(root, mode)
        programs = _mode_programs(mode)
        if (
            required
            and all(path.is_file() for path in required)
            and all(program in available_programs for program in programs)
        ):
            compiled.append(name)
    return ApertiumLanguagePlugin(root.name, root, tuple(modes), tuple(compiled))


def discover_language_plugins(
    data_dir: Path,
    *,
    runtime_bin_dir: Path | None = None,
) -> tuple[ApertiumLanguagePlugin, ...]:
    """Znajdź pakiety z modes.xml i zweryfikuj ich realne zależności runtime.

    Funkcja nie kompiluje, nie kopiuje i nie instaluje danych. Kierunek jest
    gotowy dopiero wtedy, gdy wszystkie pliki danych oraz wszystkie programy
    wymagane przez jego <program> są dostępne w prywatnym runtime albo
    w systemowym PATH.
    """
    if not data_dir.is_dir():
        return ()
    plugins = (
        plugin
        for plugin in sorted(data_dir.iterdir())
        if plugin.is_dir() and plugin.name.startswith("apertium-")
    )
    return tuple(
        parsed
        for plugin in plugins
        if (parsed := _parse_plugin(plugin, runtime_bin_dir=runtime_bin_dir)) is not None
    )


def discover_supported_pairs(
    data_dir: Path,
    *,
    runtime_bin_dir: Path | None = None,
) -> tuple[str, ...]:
    """Zwróć gotowe kierunki tłumaczenia wykryte w lokalnych trybach.

    Zwracane są tylko tryby skompilowane, których dane i zależności
    wykonywalne są dostępne dla aktywnego runtime'u Apertium.
    """
    pairs: list[str] = []
    for plugin in discover_language_plugins(
        data_dir,
        runtime_bin_dir=runtime_bin_dir,
    ):
        for mode in plugin.compiled_modes:
            pair = mode.casefold()
            if pair.count("-") == 1 and pair not in pairs:
                pairs.append(pair)
    return tuple(pairs)
