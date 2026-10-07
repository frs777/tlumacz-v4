"""Kontrakt, walidacja, budowanie i bezpieczne rozpakowanie paczek .tplugin."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class TPluginManifest:
    """Minimalny manifest wykonawczy pakietu filtra."""

    plugin_id: str
    name: str
    version: str
    format_version: int
    entrypoint_jar: str
    extensions: tuple[str, ...] = ()
    engine_min_version: str | None = None
    engine_max_version: str | None = None
    dependencies: dict[str, tuple[dict[str, Any], ...]] | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "TPluginManifest":
        if raw.get("format") != "tplugin":
            raise ValueError("Niepoprawny format manifestu TPlugin")
        if int(raw.get("format_version", 0)) != 1:
            raise ValueError("Nieobsługiwana wersja formatu TPlugin")
        plugin_id = str(raw.get("id", "")).strip()
        name = str(raw.get("name", "")).strip()
        version = str(raw.get("version", "")).strip()
        entrypoint = raw.get("entrypoint") or {}
        jar = str(entrypoint.get("jar", "")).strip()
        if not plugin_id or not name or not version or not jar:
            raise ValueError("Manifest TPlugin nie zawiera wymaganych pól")
        engine = raw.get("engine") or {}
        dependencies_raw = raw.get("dependencies") or {}
        dependencies = {
            key: tuple(value for value in values if isinstance(value, dict))
            for key, values in dependencies_raw.items()
            if isinstance(values, list)
        }
        return cls(
            plugin_id=plugin_id,
            name=name,
            version=version,
            format_version=1,
            entrypoint_jar=jar,
            extensions=tuple(str(value) for value in raw.get("extensions", ())),
            engine_min_version=engine.get("min_version"),
            engine_max_version=engine.get("max_version"),
            dependencies=dependencies,
        )

    @classmethod
    def from_file(cls, path: Path) -> "TPluginManifest":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": "tplugin",
            "format_version": self.format_version,
            "id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "engine": {"min_version": self.engine_min_version, "max_version": self.engine_max_version},
            "dependencies": {key: list(values) for key, values in (self.dependencies or {}).items()},
            "extensions": list(self.extensions),
            "entrypoint": {"kind": "okapi-filter", "jar": self.entrypoint_jar},
        }


class TPluginArchive:
    """Operacje na paczce bez instalowania jej do trwałego runtime."""

    @staticmethod
    def extract(archive: str | Path, destination: str | Path) -> Path:
        archive = Path(archive).expanduser().resolve()
        destination = Path(destination).expanduser().resolve()
        if not archive.is_file():
            raise ValueError(f"Brak paczki TPlugin: {archive}")
        destination.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix="tplugin-extract-"))
        try:
            with zipfile.ZipFile(archive) as zf:
                for member in zf.infolist():
                    member_path = Path(member.filename)
                    if member_path.is_absolute() or ".." in member_path.parts:
                        raise ValueError(f"Paczka zawiera niebezpieczną ścieżkę: {member.filename}")
                zf.extractall(staging)
            plugin_root = TPluginArchive._locate_plugin_root(staging)
            manifest = TPluginManifest.from_file(plugin_root / "plugin.json")
            TPluginArchive.validate(plugin_root)
            target = destination / manifest.plugin_id
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(plugin_root, target)
            return target
        finally:
            shutil.rmtree(staging, ignore_errors=True)

    @staticmethod
    def validate(plugin_root: str | Path) -> dict[str, Any]:
        root = Path(plugin_root).expanduser().resolve()
        manifest = TPluginManifest.from_file(root / "plugin.json")
        entrypoint = root / manifest.entrypoint_jar
        if not entrypoint.is_file():
            shared = (manifest.dependencies or {}).get("shared", ())
            if not any(str(dep.get("file", "")).strip() == manifest.entrypoint_jar for dep in shared):
                raise ValueError(f"Brak entrypoint JAR: {manifest.entrypoint_jar}")
        checksums = root / "checksums.json"
        if checksums.is_file():
            expected = json.loads(checksums.read_text(encoding="utf-8"))
            for relative, checksum in expected.items():
                target = (root / relative).resolve()
                if not target.is_relative_to(root) or not target.is_file():
                    raise ValueError(f"Niepoprawna ścieżka checksum: {relative}")
                if _sha256(target) != checksum:
                    raise ValueError(f"Nieprawidłowy checksum: {relative}")
        return manifest.to_dict()

    @staticmethod
    def _locate_plugin_root(staging: Path) -> Path:
        direct = staging / "plugin.json"
        if direct.is_file():
            return staging
        children = [path for path in staging.iterdir() if path.is_dir()]
        if len(children) != 1 or not (children[0] / "plugin.json").is_file():
            raise ValueError("Paczka TPlugin musi zawierać jeden katalog pluginu")
        return children[0]


class TPluginInventory:
    """Buduje inventory paczki/pluginu z checksumami."""

    @classmethod
    def from_plugin(cls, plugin_root: str | Path) -> dict[str, Any]:
        root = Path(plugin_root).expanduser().resolve()
        manifest = TPluginManifest.from_file(root / "plugin.json")
        files = {
            str(path.relative_to(root)): {"sha256": _sha256(path)}
            for path in sorted(root.rglob("*"))
            if path.is_file() and path.name != "checksums.json"
        }
        dependencies: dict[str, list[dict[str, Any]]] = {}
        for dependency_class, values in (manifest.dependencies or {}).items():
            dependencies[dependency_class] = []
            for raw in values:
                item = dict(raw)
                relative = str(item.get("file", "")).strip()
                if relative:
                    target = (root / relative).resolve()
                    if not target.is_relative_to(root):
                        raise ValueError(f"Niebezpieczny plik zależności: {relative}")
                    if target.is_file():
                        item["sha256"] = _sha256(target)
                    elif dependency_class != "shared":
                        raise ValueError(f"Brak pliku zależności: {relative}")
                    else:
                        item["external"] = True
                dependencies[dependency_class].append(item)
        return {
            "plugin": {"id": manifest.plugin_id, "name": manifest.name, "version": manifest.version},
            "dependencies": dependencies,
            "files": files,
        }

    @classmethod
    def from_archive(cls, archive: str | Path) -> dict[str, Any]:
        staging = Path(tempfile.mkdtemp(prefix="tplugin-inventory-"))
        try:
            root = TPluginArchive.extract(archive, staging)
            inventory = cls.from_plugin(root)
            inventory["validation"] = {"checksums": "ok"}
            return inventory
        finally:
            shutil.rmtree(staging, ignore_errors=True)


class TPluginBuilder:
    """Buduje deterministyczny artefakt .tplugin."""

    @classmethod
    def build(
        cls,
        source: str | Path,
        output: str | Path,
        *,
        plugin_id: str,
        name: str,
        version: str,
        entrypoint_jar: str,
        shared_dependencies: list[dict[str, Any]] | None = None,
        extensions: tuple[str, ...] = (),
    ) -> Path:
        source = Path(source).expanduser().resolve()
        output = Path(output).expanduser().resolve()
        if not source.is_dir():
            raise ValueError(f"Brak źródła pluginu: {source}")
        shared_dependencies = shared_dependencies or []
        manifest = TPluginManifest(
            plugin_id=plugin_id,
            name=name,
            version=version,
            format_version=1,
            entrypoint_jar=entrypoint_jar,
            extensions=tuple(extensions),
            dependencies={"shared": tuple(shared_dependencies)},
        )
        staging = Path(tempfile.mkdtemp(prefix="tplugin-build-"))
        try:
            root = staging / plugin_id
            shutil.copytree(source, root)
            (root / "plugin.json").write_text(
                json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            inventory = TPluginInventory.from_plugin(root)
            (root / "inventory.json").write_text(
                json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            checksums = {
                str(path.relative_to(root)): _sha256(path)
                for path in sorted(root.rglob("*"))
                if path.is_file() and path.name != "checksums.json"
            }
            (root / "checksums.json").write_text(
                json.dumps(checksums, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            output.mkdir(parents=True, exist_ok=True)
            archive = output / f"{plugin_id}-{version}.tplugin"
            archive.unlink(missing_ok=True)
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for path in sorted(root.rglob("*")):
                    if path.is_file():
                        zf.write(path, path.relative_to(staging))
            return archive
        finally:
            shutil.rmtree(staging, ignore_errors=True)


__all__ = ["TPluginArchive", "TPluginBuilder", "TPluginInventory", "TPluginManifest"]
