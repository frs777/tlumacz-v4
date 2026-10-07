"""Budowanie i instalacja samodzielnych paczek par językowych Apertium."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import tarfile
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


def _normalize_mode_paths(content: str, source: Path) -> str:
    """Usuń absolutny katalog źródłowy z wygenerowanego trybu paczki."""
    prefix = re.escape(str(source)) + r"/"
    return re.sub(rf"(['\"])({prefix})([^'\"]+)\1", r"\1\3\1", content)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class ApertiumPairPackageManifest:
    """Manifest pojedynczego kierunku tłumaczenia Apertium."""

    package_id: str
    pair: str
    version: str
    format_version: int = 1

    def to_dict(self) -> dict[str, object]:
        source, target = self.pair.split("-", 1)
        return {
            "format": "apertium-pair",
            "format_version": self.format_version,
            "id": self.package_id,
            "name": self.package_id,
            "version": self.version,
            "pair": self.pair,
            "source": source,
            "target": target,
        }

    @classmethod
    def from_file(cls, path: Path) -> "ApertiumPairPackageManifest":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("format") != "apertium-pair" or int(raw.get("format_version", 0)) != 1:
            raise ValueError("Niepoprawny lub nieobsługiwany manifest paczki Apertium.")
        package_id = str(raw.get("id", "")).strip()
        pair = str(raw.get("pair", "")).strip().casefold()
        version = str(raw.get("version", "")).strip()
        if not package_id or not pair or pair.count("-") != 1 or not version:
            raise ValueError("Manifest paczki Apertium nie zawiera wymaganych pól.")
        if package_id != f"apertium-{pair}":
            raise ValueError("Identyfikator paczki Apertium nie odpowiada parze.")
        return cls(package_id, pair, version)


class ApertiumPairPackageBuilder:
    """Tworzy niekompresowany .tar zawierający dokładnie jedną skompilowaną parę."""

    @classmethod
    def build(
        cls,
        source: str | Path,
        output: str | Path,
        *,
        pair: str,
        version: str,
        license_source: str | Path | None = None,
    ) -> Path:
        source = Path(source).expanduser().resolve()
        output = Path(output).expanduser().resolve()
        pair = pair.strip().casefold()
        if pair.count("-") != 1:
            raise ValueError("Para Apertium musi mieć postać source-target.")
        if not source.is_dir():
            raise ValueError(f"Brak źródła paczki Apertium: {source}")

        modes_path = source / "modes.xml"
        mode_file = source / "modes" / f"{pair}.mode"
        if not modes_path.is_file() or not mode_file.is_file():
            raise ValueError(f"Źródło nie zawiera trybu {pair!r}.")

        document = ET.parse(modes_path)
        mode = next(
            (node for node in document.getroot().findall("mode") if node.get("name", "").casefold() == pair),
            None,
        )
        if mode is None:
            raise ValueError(f"Para {pair!r} nie jest zdefiniowana w modes.xml.")

        required_names = {
            str(node.get("name")).strip()
            for node in mode.findall(".//file")
            if node.get("name") and not node.get("name", "").startswith("$")
        }
        required_paths = [source / name for name in sorted(required_names)]
        missing = [str(path.relative_to(source)) for path in required_paths if not path.is_file()]
        if missing:
            raise ValueError(f"Brak skompilowanych danych dla {pair}: {', '.join(missing)}")

        manifest = ApertiumPairPackageManifest(
            package_id=f"apertium-{pair}",
            pair=pair,
            version=version,
        )
        staging_parent = Path(tempfile.mkdtemp(prefix="apertium-pair-build-"))
        try:
            root = staging_parent / manifest.package_id
            root.mkdir()
            package_modes = ET.Element(document.getroot().tag, document.getroot().attrib)
            package_modes.append(copy.deepcopy(mode))
            ET.indent(package_modes, space="  ")
            ET.ElementTree(package_modes).write(
                root / "modes.xml",
                encoding="utf-8",
                xml_declaration=False,
            )
            (root / "modes").mkdir()
            mode_content = mode_file.read_text(encoding="utf-8")
            (root / "modes" / mode_file.name).write_text(
                _normalize_mode_paths(mode_content, source),
                encoding="utf-8",
            )
            for path in required_paths:
                shutil.copy2(path, root / path.name)

            license_path: Path | None
            if license_source is not None:
                license_path = Path(license_source).expanduser().resolve()
                if not license_path.is_file():
                    raise ValueError(f"Brak wskazanego pliku licencji: {license_path}")
            else:
                license_path = next(
                    (source / name for name in ("COPYING", "LICENSE", "LICENSE.txt") if (source / name).is_file()),
                    None,
                )
            if license_path is not None:
                shutil.copy2(license_path, root / license_path.name)
            else:
                raise ValueError(
                    "Źródło nie zawiera pliku licencji (COPYING, LICENSE lub LICENSE.txt)."
                )

            (root / "manifest.json").write_text(
                json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            checksums = {
                str(path.relative_to(root)): _sha256(path)
                for path in sorted(root.rglob("*"))
                if path.is_file()
            }
            (root / "checksums.json").write_text(
                json.dumps(checksums, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            output.mkdir(parents=True, exist_ok=True)
            archive = output / f"{manifest.package_id}-{version}.tar"
            archive.unlink(missing_ok=True)
            with tarfile.open(archive, "w:") as tar:
                tar.add(root, arcname=root.name)
            (output / f"{archive.name}.sha256").write_text(
                f"{_sha256(archive)}  {archive.name}\n",
                encoding="utf-8",
            )
            return archive
        finally:
            shutil.rmtree(staging_parent, ignore_errors=True)


class ApertiumPairPackageInstaller:
    """Bezpiecznie instaluje pojedynczą paczkę pary do magazynu Apertium."""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir).expanduser().resolve()

    def install(self, archive: str | Path) -> Path:
        archive = Path(archive).expanduser().resolve()
        if not archive.is_file():
            raise ValueError(f"Brak paczki Apertium: {archive}")
        verify_archive_checksum(archive)
        staging_parent = Path(tempfile.mkdtemp(prefix="apertium-pair-install-"))
        staging = staging_parent / "payload"
        staging.mkdir()
        try:
            self._extract_safely(archive, staging)
            roots = [path for path in staging.iterdir() if path.is_dir()]
            if len(roots) != 1:
                raise ValueError("Paczka Apertium musi zawierać dokładnie jeden katalog pary.")
            root = roots[0]
            manifest = ApertiumPairPackageManifest.from_file(root / "manifest.json")
            if root.name != manifest.package_id:
                raise ValueError("Katalog paczki nie odpowiada identyfikatorowi manifestu.")
            self._verify_checksums(root)
            mode = root / "modes" / f"{manifest.pair}.mode"
            if not mode.is_file() or not (root / "modes.xml").is_file():
                raise ValueError("Paczka Apertium nie zawiera kompletnego opisu trybu.")

            self.data_dir.mkdir(parents=True, exist_ok=True)
            destination = self.data_dir / manifest.package_id
            backup = self.data_dir / f".{manifest.package_id}.previous"
            shutil.rmtree(backup, ignore_errors=True)
            if destination.exists():
                destination.replace(backup)
            try:
                root.replace(destination)
                modes_dir = self.data_dir / "modes"
                modes_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination / "modes" / mode.name, modes_dir / mode.name)
            except Exception:
                if destination.exists():
                    shutil.rmtree(destination)
                if backup.exists():
                    backup.replace(destination)
                raise
            shutil.rmtree(backup, ignore_errors=True)
            return destination
        finally:
            shutil.rmtree(staging_parent, ignore_errors=True)

    @staticmethod
    def _extract_safely(archive: Path, destination: Path) -> None:
        with tarfile.open(archive, "r:") as tar:
            destination_root = destination.resolve()
            for member in tar.getmembers():
                member_path = (destination / member.name).resolve()
                if not member_path.is_relative_to(destination_root):
                    raise ValueError(f"Paczka Apertium zawiera niebezpieczną ścieżkę: {member.name}")
                if member.issym() or member.islnk():
                    raise ValueError("Paczka Apertium nie może zawierać dowiązań symbolicznych.")
            tar.extractall(destination)

    @staticmethod
    def _verify_checksums(root: Path) -> None:
        checksum_file = root / "checksums.json"
        if not checksum_file.is_file():
            raise ValueError("Paczka Apertium nie zawiera checksums.json.")
        expected = json.loads(checksum_file.read_text(encoding="utf-8"))
        actual = {
            str(path.relative_to(root))
            for path in root.rglob("*")
            if path.is_file() and path.name != "checksums.json"
        }
        listed = set(expected)
        unexpected = sorted(actual - listed)
        missing = sorted(listed - actual)
        if unexpected:
            raise ValueError(f"Plik paczki jest nieujęty w checksums.json: {unexpected[0]}")
        if missing:
            raise ValueError(f"Brak pliku ujętego w checksums.json: {missing[0]}")
        for relative, checksum in expected.items():
            path = root / relative
            if _sha256(path) != checksum:
                raise ValueError(f"Nieprawidłowa suma SHA-256 pliku paczki: {relative}")


def verify_archive_checksum(archive: str | Path) -> None:
    """Zweryfikuj zewnętrzny plik tar.sha256 zgodnie ze specyfikacją paczki."""
    archive = Path(archive).expanduser().resolve()
    checksum_file = Path(f"{archive}.sha256")
    if not checksum_file.is_file():
        raise ValueError(f"Brak zewnętrznego pliku SHA-256 paczki Apertium: {checksum_file}")
    expected = None
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[-1] == archive.name:
            expected = parts[0].lower()
            break
    if expected is None or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError(f"Niepoprawny plik SHA-256 paczki Apertium: {checksum_file}")
    actual = _sha256(archive)
    if actual != expected:
        raise ValueError(f"Nieprawidłowa suma SHA-256 całego artefaktu: {archive.name}")


def materialize_language_packages(data_dir: str | Path) -> Path:
    """Przygotuj paczki TAR w tymczasowym katalogu roboczym.

    Magazyn użytkownika pozostaje wyłącznie magazynem artefaktów TAR.
    Apertium potrzebuje rzeczywistych plików na dysku, dlatego zawartość
    paczek jest materializowana poza magazynem, w katalogu tymczasowym.
    """
    data_dir = Path(data_dir).expanduser().resolve()
    workspace = Path(tempfile.mkdtemp(prefix="apertium-pair-runtime-"))
    try:
        if not data_dir.is_dir():
            return workspace
        installer = ApertiumPairPackageInstaller(workspace)
        for archive in sorted(data_dir.glob("apertium-*.tar")):
            package_name = archive.name[:-4]
            if not re.fullmatch(r"apertium-[a-z]{2,3}-[a-z]{2,3}-[^/]+", package_name):
                continue
            verify_archive_checksum(archive)
            installer.install(archive)
        return workspace
    except Exception:
        shutil.rmtree(workspace, ignore_errors=True)
        raise


def discover_supported_pairs_from_store(data_dir: str | Path) -> tuple[str, ...]:
    """Odkryj pary językowe bez rozpakowywania ich do magazynu użytkownika.

    Magazyn zawiera wyłącznie archiwa TAR. Na czas odczytu listy par ich
    zawartość jest materializowana w katalogu tymczasowym i po odczycie usuwana.
    """
    import shutil

    from .language_plugins import discover_supported_pairs

    store = Path(data_dir).expanduser().resolve()
    # Zachowaj obsługę jawnie wskazanego katalogu z rozpakowanymi pluginami
    # dla integracji/systemowych instalacji; magazyn użytkownika pozostaje
    # jednak TAR-only i jest materializowany poniżej.
    has_unpacked_plugins = (
        any(
            path.is_dir() and path.name.startswith("apertium-")
            for path in store.iterdir()
        )
        if store.is_dir()
        else False
    )
    if has_unpacked_plugins:
        return discover_supported_pairs(store)

    workspace = materialize_language_packages(store)
    try:
        return discover_supported_pairs(workspace)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


__all__ = [
    "ApertiumPairPackageBuilder",
    "ApertiumPairPackageInstaller",
    "ApertiumPairPackageManifest",
    "materialize_language_packages",
    "discover_supported_pairs_from_store",
    "verify_archive_checksum",
]
