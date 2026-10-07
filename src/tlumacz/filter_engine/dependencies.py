"""Walidacja zależności pakietów filtrów dokumentowych."""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FilterDependency:
    """Opis pojedynczej wymaganej zależności filtra."""

    name: str
    jars: tuple[str, ...] = ()
    classes: tuple[str, ...] = ()
    urls: tuple[str, ...] = ()


@dataclass(frozen=True)
class MissingFilterDependency:
    """Zależność, której pakiet filtra obecnie nie spełnia."""

    name: str
    jars: tuple[str, ...] = ()
    classes: tuple[str, ...] = ()
    urls: tuple[str, ...] = ()


@dataclass(frozen=True)
class FilterValidation:
    """Wynik walidacji pakietu filtra."""

    name: str
    usable: bool
    missing: tuple[MissingFilterDependency, ...] = ()


class FilterDependencyValidator:
    """Sprawdza zależności zadeklarowane w filter.json."""

    def __init__(self, store: str | Path, *, shared_root: str | Path | None = None) -> None:
        self.store = Path(store).expanduser().resolve()
        self.shared_root = (
            Path(shared_root).expanduser().resolve()
            if shared_root is not None
            else Path(__file__).resolve().parents[1] / "resources" / "okapi-runtime" / "lib"
        )

    def validate_all(self) -> tuple[FilterValidation, ...]:
        if not self.store.is_dir():
            return ()
        return tuple(self.validate(path.name) for path in sorted(self.store.iterdir()) if path.is_dir())

    def validate(self, name: str) -> FilterValidation:
        package = self.store / name
        descriptor_path = package / "filter.json"
        if not descriptor_path.is_file():
            return FilterValidation(
                name=name,
                usable=False,
                missing=(
                    MissingFilterDependency(
                        name="Deskryptor filtra",
                        jars=("filter.json",),
                    ),
                ),
            )

        plugin_manifest = package / "plugin.json"
        try:
            descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
            manifest = json.loads(plugin_manifest.read_text(encoding="utf-8")) if plugin_manifest.is_file() else None
        except (OSError, json.JSONDecodeError):
            return FilterValidation(
                name=name,
                usable=False,
                missing=(MissingFilterDependency(name="Poprawny filter.json"),),
            )

        missing: list[MissingFilterDependency] = []
        for raw in descriptor.get("dependencies", []):
            dependency = self._dependency(raw)
            if not self._satisfied(package, dependency) and not self._satisfied_shared(dependency):
                missing.append(
                    MissingFilterDependency(
                        name=dependency.name,
                        jars=dependency.jars,
                        classes=dependency.classes,
                        urls=dependency.urls,
                    )
                )

        if isinstance(manifest, dict):
            for raw in manifest.get("dependencies", {}).get("shared", []):
                if not isinstance(raw, dict):
                    missing.append(MissingFilterDependency(name="Niepoprawna zależność shared"))
                    continue
                dependency_id = str(raw.get("id") or raw.get("artifact") or "").strip()
                version = str(raw.get("version") or "unknown").strip()
                if not dependency_id:
                    missing.append(MissingFilterDependency(name="Niepoprawna zależność shared"))
                    continue
                safe_id = dependency_id.replace("/", "_").replace(":", "_")
                safe_version = version.replace("/", "_").replace(":", "_")
                shared_root = self.shared_root
                declared_file = Path(str(raw.get("file", "")).strip()).name
                shared_jar = (
                    shared_root / declared_file if declared_file else shared_root / f"{safe_id}--{safe_version}.jar"
                )
                if not shared_jar.is_file():
                    shared_jar = shared_root / f"{safe_id}--{safe_version}.jar"
                if not shared_jar.is_file():
                    missing.append(
                        MissingFilterDependency(
                            name=dependency_id,
                            jars=(str(shared_jar),),
                        )
                    )

        return FilterValidation(name=name, usable=not missing, missing=tuple(missing))

    @staticmethod
    def _dependency(raw: object) -> FilterDependency:
        if not isinstance(raw, dict):
            return FilterDependency(name="Niepoprawna deklaracja zależności")
        return FilterDependency(
            name=str(raw.get("name") or raw.get("artifact") or "Nieznana zależność"),
            jars=tuple(str(value) for value in raw.get("jars", ()) if str(value).strip()),
            classes=tuple(str(value) for value in raw.get("classes", ()) if str(value).strip()),
            urls=tuple(str(value) for value in raw.get("urls", ()) if str(value).strip()),
        )

    @staticmethod
    def _satisfied(package: Path, dependency: FilterDependency) -> bool:
        if dependency.jars and not all((package / jar).is_file() for jar in dependency.jars):
            return False
        if dependency.classes and not all(
            FilterDependencyValidator._class_available(package, class_name) for class_name in dependency.classes
        ):
            return False
        return bool(dependency.jars or dependency.classes)

    def _satisfied_shared(self, dependency: FilterDependency) -> bool:
        if dependency.jars:
            return all((self.shared_root / Path(jar).name).is_file() for jar in dependency.jars)
        if dependency.classes:
            shared_root = self.shared_root
            for jar in shared_root.glob("*.jar"):
                try:
                    with zipfile.ZipFile(jar) as archive:
                        if all(
                            class_name.replace(".", "/") + ".class" in archive.namelist()
                            for class_name in dependency.classes
                        ):
                            return True
                except (OSError, zipfile.BadZipFile):
                    continue
        return False

    @staticmethod
    def _class_available(package: Path, class_name: str) -> bool:
        entry = class_name.replace(".", "/") + ".class"
        for jar in package.glob("*.jar"):
            try:
                with zipfile.ZipFile(jar) as archive:
                    if entry in archive.namelist():
                        return True
            except (OSError, zipfile.BadZipFile):
                continue
        return False


__all__ = [
    "FilterDependency",
    "MissingFilterDependency",
    "FilterValidation",
    "FilterDependencyValidator",
]
