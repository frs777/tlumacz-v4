"""Bridge Qt Quick/QML dla rdzenia aplikacyjnego Tłumacza V4."""

from __future__ import annotations

import csv
import html
import shutil
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from PySide6.QtCore import Property, QFileSystemWatcher, QObject, QThread, QTimer, QUrl, Signal, Slot

from tlumacz import __version__
from tlumacz.application.backend_service import BackendRequest
from tlumacz.application.cancellation import CancellationToken
from tlumacz.application.translation_app import TranslationApp
from tlumacz.backends.apertium.config import default_data_dir
from tlumacz.backends.apertium.languages import (
    APERTIUM_LANGUAGE_CODES,
    supported_targets_for_source,
)
from tlumacz.backends.apertium.packages import discover_supported_pairs_from_store
from tlumacz.backends.cloud.mozhi import MOZHI_ENGINES, MOZHI_INSTANCES
from tlumacz.domain.contracts import BackendConfiguration
from tlumacz.filter_engine.dependencies import FilterDependencyValidator
from tlumacz.filter_engine.filter_store import FilterStore
from tlumacz.i18n import set_language, t
from tlumacz.infrastructure.secrets import SecretStore
from tlumacz.language_detector import LanguageDetector

from .config import (
    CLOUD_MODELS_CONFIG,
    AppSettings,
    load_settings,
    normalize_local_server_host,
    save_settings,
)

TARGET_LANGUAGE_OPTIONS = (
    ("Polski", "pl"),
    ("Angielski", "en"),
    ("Niemiecki", "de"),
    ("Francuski", "fr"),
    ("Hiszpański", "es"),
    ("Włoski", "it"),
    ("Portugalski", "pt"),
    ("Niderlandzki", "nl"),
    ("Szwedzki", "sv"),
    ("Norweski", "no"),
    ("Duński", "da"),
    ("Fiński", "fi"),
    ("Czeski", "cs"),
    ("Słowacki", "sk"),
    ("Węgierski", "hu"),
    ("Rumuński", "ro"),
    ("Bułgarski", "bg"),
    ("Grecki", "el"),
    ("Ukraiński", "uk"),
    ("Rosyjski", "ru"),
    ("Chorwacki", "hr"),
    ("Słoweński", "sl"),
    ("Serbski", "sr"),
    ("Turecki", "tr"),
    ("Islandzki", "is"),
    ("Estoński", "et"),
    ("Łotewski", "lv"),
    ("Litewski", "lt"),
)
TARGET_LANGUAGE_I18N_KEYS = (
    "language.polish", "language.english", "language.german", "language.french",
    "language.spanish", "language.italian", "language.portuguese", "language.dutch",
    "language.swedish", "language.norwegian", "language.danish", "language.finnish",
    "language.czech", "language.slovak", "language.hungarian", "language.romanian",
    "language.bulgarian", "language.greek", "language.ukrainian", "language.russian",
    "language.croatian", "language.slovenian", "language.serbian", "language.turkish",
    "language.icelandic", "language.estonian", "language.latvian", "language.lithuanian",
)

SKILL_OPTIONS = (
    ("Markdown - md", "markdown.md"),
    ("HTML/XHTML", "html.md"),
    ("DOCX", "docx.md"),
    ("ODT", "odt.md"),
    ("ePUB", "epub.md"),
    ("Text zwykły - TXT", "plaintext.md"),
    ("PDF", "pdf.md"),
)

LONG_TEXT_FILES = {
    "apertium.description": "apertium.description.txt",
    "cloud.mozhi_auto_info": "cloud.mozhi_auto_info.txt",
    "custom.description": "custom.description.txt",
    "help.about_text": "help.about_text.txt",
}


class _ServerWorker(QObject):
    """Wykonuje start/restart llama.cpp poza wątkiem interfejsu QML."""

    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, operation: Any, success_message: str) -> None:
        super().__init__()
        self.operation = operation
        self.success_message = success_message

    @Slot()
    def run(self) -> None:
        try:
            self.operation()
            self.finished.emit(self.success_message)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


class _TranslationWorker(QObject):
    """Wykonuje tłumaczenie poza wątkiem interfejsu QML."""

    finished = Signal(str)
    failed = Signal(str)
    cancelled = Signal()
    documentInfo = Signal(str, int, int)
    chunkStart = Signal(int, int)
    chunkComplete = Signal(int, int, int)
    chunkFailed = Signal(int, int, str)
    log = Signal(str)
    progress = Signal(int, int)

    def __init__(self, service: Any, operation: dict[str, Any]) -> None:
        super().__init__()
        self.service = service
        self.operation = operation
        self.token = CancellationToken()
        self._active_chunk: tuple[int, int] | None = None

    def _emit_chunk_start(self, current: int, total: int) -> None:
        self._active_chunk = (current, total)
        self.chunkStart.emit(current, total)

    def _emit_chunk_complete(self, current: int, total: int, characters: int) -> None:
        self._active_chunk = None
        self.chunkComplete.emit(current, total, characters)

    @Slot()
    def run(self) -> None:
        try:
            output = self.service.translate_file(
                self.operation["input"],
                self.operation["output"],
                source_language=self.operation["source"],
                target_language=self.operation["target"],
                workspace=self.operation["workspace"],
                cancellation_token=self.token,
                on_progress=self.progress.emit,
                on_document_info=self.documentInfo.emit,
                on_chunk_start=self._emit_chunk_start,
                on_chunk_complete=self._emit_chunk_complete,
                skip_line_patterns=self.operation.get("skip_line_patterns", ()),
            )
            self.finished.emit(str(output))
        except Exception as exc:  # noqa: BLE001
            if self.token.is_cancelled:
                self.cancelled.emit()
            else:
                message = str(exc)
                if self._active_chunk is not None:
                    current, total = self._active_chunk
                    self.chunkFailed.emit(current, total, message)
                self.failed.emit(message)


class QmlApplicationBridge(QObject):
    """Stan prezentacyjny i akcje GUI QML nad TranslationApp."""

    stateChanged = Signal()
    progressChanged = Signal()
    logChanged = Signal()
    previewChanged = Signal()
    skillsChanged = Signal()
    errorChanged = Signal()
    languageChanged = Signal()
    themeChanged = Signal()
    translationFinished = Signal()
    translationFailed = Signal()
    filterDependencyWarning = Signal(str)

    def __init__(
        self,
        *,
        core: TranslationApp | None = None,
        settings_path: Path | None = None,
        secret_path: Path | None = None,
        user_skills_dir: Path | None = None,
        apertium_data_dir: Path | None = None,
        filter_store: Path | None = None,
    ) -> None:
        super().__init__()
        self.core = core or TranslationApp()
        self.settings_path = settings_path
        self.secret_store = SecretStore(secret_path or (Path.home() / ".config" / "tlumacz" / ".key"))
        self.settings = load_settings(settings_path) if settings_path else load_settings()
        self.user_skills_dir = user_skills_dir or (Path.home() / ".config" / "tlumacz" / "skills")
        self.builtin_skills_dir = Path(__file__).resolve().parent.parent / "skills"
        self.help_files_dir = Path(__file__).resolve().parent
        self.long_text_files_dir = self.help_files_dir / "texts"
        self._long_text_cache: dict[tuple[str, str], str] = {}
        self.filter_store = Path(filter_store).expanduser().resolve() if filter_store else FilterStore.default().path
        self.apertium_data_dir = apertium_data_dir or default_data_dir()
        self._language_detector = LanguageDetector()

        self._input_path: str = ""
        self._output_path: str = ""
        self._output_path_auto_generated = True
        self._target_language: str = "pl"
        self._backend_type: str = "llama"
        self._base_url: str = ""
        self._api_key: str = ""
        self._model_name: str = ""
        self._gguf_path: str = ""
        self._compute_mode: str = "gpu"
        self._chat_template: str = ""
        self._parallel: int = 1
        self._chunk_size: int = 2000
        self._temperature: float = 0.1
        self._system_prompt: str = ""
        self._skip_patterns: str = ""
        self._glossary_path: str = ""
        self._theme: str = "system"
        self._application_language: str = "pl"
        self._source_language: str = "auto"
        self._detected_source_language: str | None = None
        self._cloud_profile: str = ""
        self._effective_mozhi_url: str = ""

        self._migrate_legacy_secrets()
        self._load_settings(self.settings)

        self._progress = 0
        self._elapsed_seconds = 0
        self._current_speed: float = 0.0
        self._average_speed: float = 0.0
        self._server_thread: QThread | None = None
        self._server_worker: _ServerWorker | None = None
        self._server_operation_busy = False
        self._server_ready_callbacks: list[Callable[[], None]] = []
        self._translation_stage = ""
        self._translation_block_current = 0
        self._translation_block_total = 0
        self._translated_characters = 0
        self._is_translating = False
        self._status_text = "Gotowy."
        self._log_text = ""
        self._filter_dependency_warnings = self._collect_filter_dependency_warnings()
        self._filter_dependency_warning_queue = list(self._filter_dependency_warnings)
        self._filter_store_watcher = QFileSystemWatcher(self)
        if self.filter_store.is_dir():
            self._filter_store_watcher.addPath(str(self.filter_store))
            self._filter_store_watcher.directoryChanged.connect(self.refreshFilterDependencies)
        self._skill_watcher = QFileSystemWatcher(self)
        self._skill_watcher.directoryChanged.connect(self._on_skills_directory_changed)
        self._preview_text = ""
        self._error_message = ""
        available_builtin_skills = {
            filename
            for _, filename in SKILL_OPTIONS
            if (self.builtin_skills_dir / filename).is_file()
        }
        configured_skills = self.settings.enabled_skills
        if configured_skills is None:
            self._enabled_skills = set(available_builtin_skills)
            self._disabled_user_skills: set[str] = set()
        else:
            configured = set(configured_skills)
            self._enabled_skills = configured & available_builtin_skills
            self._disabled_user_skills = {
                filename for filename in self.user_skills if filename not in configured
            }
        self._skill_template = """# Nazwa skilla

## Cel
Opisz krótko, do czego służy skill.

## Zakres
- Kiedy należy go użyć.
- Jakie dane wejściowe obsługuje.
- Jakiego wyniku oczekuje.

## Instrukcje
Opisz dokładnie sposób działania, ograniczenia i kolejność kroków.

## Przykłady
Dodaj krótkie przykłady poprawnego użycia.
"""

        self._thread: QThread | None = None
        self._worker: _TranslationWorker | None = None
        self._started_at = 0.0
        self._last_progress = 0
        self._last_progress_at = 0.0

        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._update_metrics)

        set_language(self._application_language)
        self._help_topics = self._load_help_topics(self._application_language)

        self.refresh_skills()
        self._watch_user_skills_directory()
        self._maybe_autostart_server()
        self._move_ready_message_to_end()

    def _collect_filter_dependency_warnings(
        self,
        *,
        append_log: bool = True,
    ) -> list[dict[str, str]]:
        warnings: list[dict[str, str]] = []
        for validation in FilterDependencyValidator(self.filter_store).validate_all():
            if validation.usable:
                continue
            for missing in validation.missing:
                details: list[str] = []
                if missing.jars:
                    details.append("Pliki: " + ", ".join(missing.jars))
                if missing.classes:
                    details.append("Klasy: " + ", ".join(missing.classes))
                if missing.urls:
                    details.append("Odnośniki: " + ", ".join(missing.urls))
                detail_text = "; ".join(details)
                log_message = (
                    f"FILTR NIEDOSTĘPNY: {validation.name}. "
                    f"Brakująca zależność: {missing.name}."
                )
                if detail_text:
                    log_message += f" {detail_text}"
                links = "".join(
                    f'<br/><a href="{html.escape(url, quote=True)}">{html.escape(url)}</a>'
                    for url in missing.urls
                )
                dialog_message = (
                    f"<b>Filtr:</b> {html.escape(validation.name)}<br/>"
                    f"<b>Brakująca zależność:</b> {html.escape(missing.name)}<br/>"
                    f"<b>Status:</b> filtr nie jest użytkowy do czasu spełnienia zależności."
                    f"{links}"
                )
                warnings.append(
                    {
                        "filter": validation.name,
                        "message": log_message,
                        "dialog": dialog_message,
                    }
                )
                if append_log:
                    self._append_log(log_message)
        return warnings

    @Property("QVariantList", notify=stateChanged)
    def filter_dependency_warnings(self) -> list[dict[str, str]]:
        return list(self._filter_dependency_warnings)

    @Slot()
    def refreshFilterDependencies(self) -> None:
        previous_keys = {
            (warning["filter"], warning["message"])
            for warning in self._filter_dependency_warnings
        }
        warnings = self._collect_filter_dependency_warnings(append_log=False)
        new_warnings = [
            warning
            for warning in warnings
            if (warning["filter"], warning["message"]) not in previous_keys
        ]
        for warning in new_warnings:
            self._append_log(warning["message"])
        self._filter_dependency_warnings = warnings
        self._filter_dependency_warning_queue.extend(new_warnings)
        for package in self.filter_store.iterdir() if self.filter_store.is_dir() else ():
            if package.is_dir() and str(package) not in self._filter_store_watcher.directories():
                self._filter_store_watcher.addPath(str(package))
        self.stateChanged.emit()

    @Slot(result=bool)
    def showNextFilterDependencyWarning(self) -> bool:
        if not self._filter_dependency_warning_queue:
            return False
        warning = self._filter_dependency_warning_queue.pop(0)
        self.filterDependencyWarning.emit(warning["dialog"])
        return True

    def _load_long_text(self, key: str, language: str) -> str:
        filename = LONG_TEXT_FILES.get(key)
        if filename is None:
            return ""

        cache_key = (language, key)
        cached = self._long_text_cache.get(cache_key)
        if cached is not None:
            return cached

        path = self.long_text_files_dir / language / filename
        if not path.is_file() and language != "pl":
            path = self.long_text_files_dir / "pl" / filename
        if not path.is_file():
            return ""

        value = path.read_text(encoding="utf-8").strip()
        self._long_text_cache[cache_key] = value
        return value

    @staticmethod
    def _parse_help_file(path: Path) -> list[dict[str, str]]:
        if not path.is_file():
            return []
        sections: list[dict[str, str]] = []
        title = ""
        content: list[str] = []
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            if raw_line.startswith("## "):
                if title:
                    sections.append({"title": title, "content": "\n".join(content).strip()})
                title = raw_line[3:].strip()
                content = []
            elif title:
                content.append(raw_line)
        if title:
            sections.append({"title": title, "content": "\n".join(content).strip()})
        return [section for section in sections if section["content"]]

    def _load_help_topics(self, language: str) -> list[dict[str, str]]:
        path = self.help_files_dir / f"help.{language}.md"
        topics = self._parse_help_file(path)
        if topics:
            return topics
        fallback = self.help_files_dir / "help.pl.md"
        return self._parse_help_file(fallback)

    def _notify(self) -> None:
        self.stateChanged.emit()

    def _get(self, name: str) -> Any:
        return getattr(self, name)

    def _set_str(self, attr: str, value: str, signal: Signal | None = None) -> None:
        if getattr(self, attr) == value:
            return
        setattr(self, attr, value)
        (signal or self.stateChanged).emit()

    @Property(str, notify=stateChanged)
    def input_path(self) -> str:
        return self._input_path

    @Property(str, notify=stateChanged)
    def output_path(self) -> str:
        return self._output_path

    @Property(str, notify=stateChanged)
    def target_language(self) -> str:
        return self._target_language

    @Property(str, notify=stateChanged)
    def backend_type(self) -> str:
        return self._backend_type

    @Property(str, notify=stateChanged)
    def base_url(self) -> str:
        return self._base_url

    @Property(str, notify=stateChanged)
    def api_key(self) -> str:
        return self._api_key

    @Property(str, notify=stateChanged)
    def model_name(self) -> str:
        return self._model_name

    @Property(str, notify=stateChanged)
    def gguf_path(self) -> str:
        return self._gguf_path

    @Property(str, notify=stateChanged)
    def compute_mode(self) -> str:
        return self._compute_mode

    @Property(str, notify=stateChanged)
    def chat_template(self) -> str:
        return {
            "": "jinja",
            "chatml": "chatml",
            "translategemma": "TranslateGemma",
        }.get(self._chat_template, self._chat_template)

    @Property(int, notify=stateChanged)
    def parallel(self) -> int:
        return self._parallel

    @Property(int, notify=stateChanged)
    def chunk_size(self) -> int:
        return self._chunk_size

    @Property(float, notify=stateChanged)
    def temperature(self) -> float:
        return self._temperature

    @Property(str, notify=stateChanged)
    def system_prompt(self) -> str:
        return self._system_prompt

    @Property(str, notify=stateChanged)
    def skip_patterns(self) -> str:
        return self._skip_patterns

    @Property(str, notify=stateChanged)
    def glossary_path(self) -> str:
        return self._glossary_path

    @Property(str, notify=themeChanged)
    def theme(self) -> str:
        return self._theme

    @Property(str, notify=stateChanged)
    def application_language(self) -> str:
        return self._application_language

    @Property(str, constant=True)
    def application_version(self) -> str:
        return __version__

    @Property(str, constant=True)
    def applicationVersion(self) -> str:
        return __version__

    @Property(str, notify=languageChanged)
    def about_text(self) -> str:
        return self._load_long_text("help.about_text", self._application_language)

    @Property(str, notify=languageChanged)
    def aboutText(self) -> str:
        return self.about_text

    @Property("QVariantList", notify=languageChanged)
    def help_topics(self) -> list[dict[str, str]]:
        return list(self._help_topics)

    @Property("QVariantList", notify=languageChanged)
    def helpTopics(self) -> list[dict[str, str]]:
        return list(self._help_topics)

    def _help_topic_value(self, index: int, field: str) -> str:
        if 0 <= index < len(self._help_topics):
            return self._help_topics[index][field]
        return ""

    @Property(str, notify=languageChanged)
    def helpTopic1Title(self) -> str:
        return self._help_topic_value(0, "title")

    @Property(str, notify=languageChanged)
    def helpTopic2Title(self) -> str:
        return self._help_topic_value(1, "title")

    @Property(str, notify=languageChanged)
    def helpTopic3Title(self) -> str:
        return self._help_topic_value(2, "title")

    @Property(str, notify=languageChanged)
    def helpTopic4Title(self) -> str:
        return self._help_topic_value(3, "title")

    @Property(str, notify=languageChanged)
    def helpTopic5Title(self) -> str:
        return self._help_topic_value(4, "title")

    @Property(str, notify=languageChanged)
    def helpTopic1Content(self) -> str:
        return self._help_topic_value(0, "content")

    @Property(str, notify=languageChanged)
    def helpTopic2Content(self) -> str:
        return self._help_topic_value(1, "content")

    @Property(str, notify=languageChanged)
    def helpTopic3Content(self) -> str:
        return self._help_topic_value(2, "content")

    @Property(str, notify=languageChanged)
    def helpTopic4Content(self) -> str:
        return self._help_topic_value(3, "content")

    @Property(str, notify=languageChanged)
    def helpTopic5Content(self) -> str:
        return self._help_topic_value(4, "content")

    @Slot(str, result=str)
    def tr(self, key: str) -> str:
        """Zwraca krótki tekst GUI dla bieżącego języka."""
        return t(key)

    @Slot(str, result=str)
    def long_text(self, key: str) -> str:
        """Zwraca długi statyczny tekst GUI z pliku tekstowego."""
        return self._load_long_text(key, self._application_language)

    @Property(bool, notify=stateChanged)
    def llama_server_running(self) -> bool:
        """Zwraca rzeczywisty stan zarządzanego serwera llama.cpp."""
        return bool(self.core.runtime is not None and self.core.runtime.is_running())

    @Property(int, constant=True)
    def settings_window_x(self) -> int:
        return self.settings.window_x

    @Property(int, constant=True)
    def settings_window_y(self) -> int:
        return self.settings.window_y

    @Property(int, constant=True)
    def settings_window_width(self) -> int:
        return self.settings.window_width

    @Property(int, constant=True)
    def settings_window_height(self) -> int:
        return self.settings.window_height

    @Property(str, constant=True)
    def builtin_skills_directory(self) -> str:
        return str(self.builtin_skills_dir)

    @Property(str, constant=True)
    def user_skills_directory(self) -> str:
        return str(self.user_skills_dir)

    @Property(str, notify=stateChanged)
    def source_language(self) -> str:
        return self._source_language

    @Property(str, notify=stateChanged)
    def cloud_profile(self) -> str:
        return self._cloud_profile

    @Slot(str, result=bool)
    def cloud_profile_requires_api_key(self, name: str) -> bool:
        profile = self._cloud_profile_data(name)
        explicit = profile.get("requires_api_key")
        if explicit is not None:
            return bool(explicit)
        return str(profile.get("provider", "")).lower() not in {"mozhi", "mymemory", "dlx"}

    @Property(bool, notify=stateChanged)
    def cloud_requires_api_key(self) -> bool:
        return self.cloud_profile_requires_api_key(self._cloud_profile)

    @Property(str, notify=stateChanged)
    def server_host(self) -> str:
        return self.settings.server_host

    @Property(str, notify=stateChanged)
    def cloud_server_url(self) -> str:
        if self._cloud_profile == "Mozhi":
            if self.settings.mozhi_instance == "auto":
                return self._effective_mozhi_url or "auto"
            return self.settings.mozhi_instance
        return self._base_url

    @Property(str, notify=stateChanged)
    def server_url(self) -> str:
        host = self.settings.server_host.strip() or "127.0.0.1"
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        return f"http://{host}:{self.settings.server_port}/v1"

    @Property(int, notify=stateChanged)
    def server_port(self) -> int:
        return self.settings.server_port

    @Property(bool, notify=stateChanged)
    def auto_start_server(self) -> bool:
        return self.settings.auto_start_server

    @Property(bool, notify=stateChanged)
    def cache_clear_after_translation(self) -> bool:
        return self.settings.cache_clear_after_translation

    @Property(bool, notify=stateChanged)
    def restartLlamaAfterTranslation(self) -> bool:
        return self.settings.restart_llama_after_translation

    @Property(bool, notify=stateChanged)
    def restartApertiumAfterTranslation(self) -> bool:
        return self.settings.restart_apertium_after_translation

    @Property(bool, notify=stateChanged)
    def reconnectCloudAfterTranslation(self) -> bool:
        return self.settings.reconnect_cloud_after_translation

    @Property(str, notify=stateChanged)
    def mozhi_instance(self) -> str:
        return self.settings.mozhi_instance

    @Property(str, notify=stateChanged)
    def mozhi_engine(self) -> str:
        return self.settings.mozhi_engine

    @Property("QVariantList", constant=True)
    def mozhi_instances(self) -> list[str]:
        return ["auto", *MOZHI_INSTANCES]

    @Property("QVariantList", constant=True)
    def mozhi_engines(self) -> list[str]:
        return [engine_id for _, engine_id in MOZHI_ENGINES]

    @Property(int, notify=progressChanged)
    def progress(self) -> int:
        return self._progress

    @Property(int, notify=progressChanged)
    def elapsed_seconds(self) -> int:
        return self._elapsed_seconds

    @Property(float, notify=progressChanged)
    def current_speed(self) -> float:
        return self._current_speed

    @Property(float, notify=progressChanged)
    def average_speed(self) -> float:
        return self._average_speed

    @Property(str, notify=progressChanged)
    def translation_stage(self) -> str:
        return self._translation_stage

    @Property(int, notify=progressChanged)
    def translation_block_current(self) -> int:
        return self._translation_block_current

    @Property(int, notify=progressChanged)
    def translation_block_total(self) -> int:
        return self._translation_block_total

    @Property(bool, notify=stateChanged)
    def is_translating(self) -> bool:
        return self._is_translating

    @Property(str, notify=stateChanged)
    def status_text(self) -> str:
        return self._status_text

    @Property(str, notify=logChanged)
    def log_text(self) -> str:
        return self._log_text

    @Property(str, notify=previewChanged)
    def preview_text(self) -> str:
        return self._preview_text

    @Property(str, notify=errorChanged)
    def error_message(self) -> str:
        return self._error_message

    @Property("QVariantList", constant=True)
    def backend_types(self) -> list[str]:
        return [
            t("backend.local_server"),
            t("backend.apertium_local_server"),
            t("backend.cloud_server"),
            t("custom.server_type"),
        ]

    @Property("QVariantList", constant=True)
    def target_languages(self) -> list[str]:
        return [t(key) for key in TARGET_LANGUAGE_I18N_KEYS]

    @Property("QVariantList", constant=True)
    def skill_options(self) -> list[str]:
        return [label for label, _ in SKILL_OPTIONS]

    @Property("QVariantList", constant=True)
    def chat_templates(self) -> list[str]:
        return ["jinja", "chatml", "TranslateGemma"]

    @Property("QVariantList", constant=True)
    def compute_modes(self) -> list[str]:
        return ["gpu", "cpu"]

    @Property(int, notify=stateChanged)
    def effective_translation_parallel(self) -> int:
        # llama.cpp na CPU wykonuje inferencję seryjnie. Równoległe żądania
        # tego samego modelu na CPU prowadzą do przeciążenia slotów i błędów
        # transportu podczas tłumaczenia dokumentów.
        if self._backend_type == "llama" and self._compute_mode == "cpu":
            return 1
        return 1 if self._backend_type == "cloud" else self._parallel

    @Property(int, notify=stateChanged)
    def effective_server_parallel(self) -> int:
        """Liczba slotów llama.cpp; na CPU zawsze jeden."""
        if self._compute_mode == "cpu":
            return 1
        return self._parallel

    @Property("QVariantList", constant=True)
    def cloud_profiles(self) -> list[str]:
        allowed = {
            "Cohere", "ChatGPT", "Codex", "Gemini Flash", "Gemini Flash Lite",
            "DeepSeek", "DeepL API Free", "MyMemory", "Microsoft Translator", "DLX", "Mozhi",
        }
        return [
            str(item.get("name", ""))
            for item in CLOUD_MODELS_CONFIG
            if item.get("name") in allowed
        ]

    @Property("QVariantList", notify=skillsChanged)
    def builtin_skills(self) -> list[dict[str, Any]]:
        return [
            {"name": path.stem, "file": path.name, "enabled": False}
            for path in sorted(self.builtin_skills_dir.glob("*.md"))
        ]

    @Property("QVariantList", notify=skillsChanged)
    def user_skills(self) -> list[str]:
        return sorted(path.name for path in self.user_skills_dir.glob("*.md")) if self.user_skills_dir.is_dir() else []

    @Property(str, notify=stateChanged)
    def applicationLanguage(self) -> str:
        return self._application_language

    @Property(str, notify=stateChanged)
    def inputPath(self) -> str:
        return self._input_path

    @Property(str, notify=stateChanged)
    def outputPath(self) -> str:
        return self._output_path

    @Property(str, notify=stateChanged)
    def targetLanguage(self) -> str:
        return self._target_language

    @Property(str, notify=stateChanged)
    def targetLanguageLabel(self) -> str:
        for (_, code), key in zip(TARGET_LANGUAGE_OPTIONS, TARGET_LANGUAGE_I18N_KEYS, strict=True):
            if code == self._target_language:
                return t(key)
        return self._target_language

    @Property("QVariantList", constant=True)
    def targetLanguages(self) -> list[str]:
        return self.target_languages

    @property
    def _apertium_supported_pairs(self) -> tuple[str, ...]:
        return discover_supported_pairs_from_store(self.apertium_data_dir)

    @property
    def _apertium_source_options(self) -> tuple[tuple[str, str], ...]:
        known_labels = {
            code: t(key)
            for (_, code), key in zip(
                TARGET_LANGUAGE_OPTIONS, TARGET_LANGUAGE_I18N_KEYS, strict=True
            )
        }
        return tuple(
            (known_labels.get(code, code), code)
            for _, code in TARGET_LANGUAGE_OPTIONS
            if code in APERTIUM_LANGUAGE_CODES
        )

    @property
    def _apertium_effective_source_language(self) -> str:
        """Zwróć wykryty source Apertium bez nadpisywania trybu auto."""
        if self._source_language == "auto" and self._detected_source_language:
            return self._detected_source_language
        return self._source_language

    @property
    def _apertium_target_options(self) -> tuple[tuple[str, str], ...]:
        source_language = self._apertium_effective_source_language
        if source_language == "auto":
            return ()
        targets = supported_targets_for_source(
            source_language,
            self._apertium_supported_pairs,
        )
        known_labels = {
            code: t(key)
            for (_, code), key in zip(
                TARGET_LANGUAGE_OPTIONS, TARGET_LANGUAGE_I18N_KEYS, strict=True
            )
        }
        target_set = set(targets)
        ordered_targets = (
            code for _, code in TARGET_LANGUAGE_OPTIONS if code in target_set
        )
        return tuple(
            (known_labels.get(code, code), code)
            for code in ordered_targets
        )

    def _refresh_apertium_language_selection(self) -> None:
        if self._backend_type != "apertium":
            return
        options = self._apertium_target_options
        valid_targets = {code for _, code in options}
        if self._target_language not in valid_targets:
            self._target_language = ""

    def _detect_apertium_source_from_input(self, path: Path) -> None:
        self._detected_source_language = None
        if not path.is_file() or self._source_language != "auto":
            return
        if path.suffix.casefold() not in {
            ".txt", ".md", ".markdown", ".html", ".htm", ".xhtml", ".csv", ".json"
        }:
            return
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:12000]
        except OSError:
            return
        detected = self._language_detector.detect_language_code(text)
        if detected not in APERTIUM_LANGUAGE_CODES:
            return
        self._detected_source_language = detected
        self._refresh_apertium_language_selection()

    @Property("QVariantList", notify=stateChanged)
    def apertiumSourceLanguages(self) -> list[str]:
        return [label for label, _ in self._apertium_source_options]

    @Property("QVariantList", notify=stateChanged)
    def apertiumTargetLanguages(self) -> list[str]:
        options = self._apertium_target_options
        if not options:
            return [t("apertium.no_pair")]
        return [label for label, _ in options]

    @Property(bool, notify=stateChanged)
    def apertiumTargetSelectionEnabled(self) -> bool:
        return bool(self._apertium_target_options)

    @Property(str, notify=stateChanged)
    def apertiumTargetLanguageLabel(self) -> str:
        if not self._target_language:
            return t("apertium.no_pair")
        for label, code in self._apertium_target_options:
            if code == self._target_language:
                return label
        return t("apertium.no_pair")

    @Property(str, notify=stateChanged)
    def apertiumSourceLanguageLabel(self) -> str:
        for label, code in self._apertium_source_options:
            if code == self._source_language:
                return label
        return t("apertium.no_pair")

    @Property(str, notify=stateChanged)
    def detectedSourceLanguage(self) -> str:
        if not self._detected_source_language:
            return ""
        for label, code in self._apertium_source_options:
            if code == self._detected_source_language:
                return label
        return self._detected_source_language

    @Property(bool, notify=stateChanged)
    def isTranslating(self) -> bool:
        return self._is_translating

    @Property(int, notify=progressChanged)
    def elapsedSeconds(self) -> int:
        return self._elapsed_seconds

    @Property(float, notify=progressChanged)
    def currentSpeed(self) -> float:
        return self._current_speed

    @Property(float, notify=progressChanged)
    def averageSpeed(self) -> float:
        return self._average_speed

    @Property(str, notify=progressChanged)
    def translationStage(self) -> str:
        return self._translation_stage

    @Property(int, notify=progressChanged)
    def translationBlockCurrent(self) -> int:
        return self._translation_block_current

    @Property(int, notify=progressChanged)
    def translationBlockTotal(self) -> int:
        return self._translation_block_total

    @Property(str, notify=logChanged)
    def logText(self) -> str:
        return self._log_text

    @Property(str, notify=previewChanged)
    def previewText(self) -> str:
        return self._preview_text

    @Property(int, constant=True)
    def settingsWindowX(self) -> int:
        return self.settings.window_x

    @Property(int, constant=True)
    def settingsWindowY(self) -> int:
        return self.settings.window_y

    @Property(int, constant=True)
    def settingsWindowWidth(self) -> int:
        return self.settings.window_width

    @Property(int, constant=True)
    def settingsWindowHeight(self) -> int:
        return self.settings.window_height

    @Property(str, notify=stateChanged)
    def backendType(self) -> str:
        return self._backend_type

    @Property("QVariantList", constant=True)
    def backendTypes(self) -> list[str]:
        return self.backend_types

    @Property(str, notify=stateChanged)
    def baseUrl(self) -> str:
        return self._base_url

    @Property(str, notify=stateChanged)
    def apiKey(self) -> str:
        return self._api_key

    @Property(str, notify=stateChanged)
    def modelName(self) -> str:
        return self._model_name

    @Property(str, notify=stateChanged)
    def ggufPath(self) -> str:
        return self._gguf_path

    @Property(str, notify=stateChanged)
    def computeMode(self) -> str:
        return self._compute_mode

    @Property("QVariantList", constant=True)
    def computeModes(self) -> list[str]:
        return self.compute_modes

    @Property(str, notify=stateChanged)
    def chatTemplate(self) -> str:
        return {
            "": "jinja",
            "chatml": "chatml",
            "translategemma": "TranslateGemma",
        }.get(self._chat_template, self._chat_template)

    @Property("QVariantList", constant=True)
    def chatTemplates(self) -> list[str]:
        return self.chat_templates

    @Property(str, notify=stateChanged)
    def cloudProfile(self) -> str:
        return self._cloud_profile

    @Property(int, notify=stateChanged)
    def serverPort(self) -> int:
        return self.server_port

    @Property(bool, notify=stateChanged)
    def serverOperationBusy(self) -> bool:
        return self._server_operation_busy

    @Property(str, notify=stateChanged)
    def serverUrl(self) -> str:
        return self.server_url

    @Property(bool, notify=stateChanged)
    def autoStartServer(self) -> bool:
        return self.auto_start_server

    @Property(bool, notify=stateChanged)
    def cacheClearAfterTranslation(self) -> bool:
        return self.cache_clear_after_translation

    @Property(bool, notify=stateChanged)
    def restartAfterTranslation(self) -> bool:
        return self.restart_after_translation

    @Property(str, notify=stateChanged)
    def mozhiInstance(self) -> str:
        return self.mozhi_instance

    @Property(str, notify=stateChanged)
    def mozhiEngine(self) -> str:
        return self.mozhi_engine

    @Property("QVariantList", constant=True)
    def mozhiInstances(self) -> list[str]:
        return self.mozhi_instances

    @Property("QVariantList", constant=True)
    def mozhiEngines(self) -> list[str]:
        return self.mozhi_engines

    @Property("QVariantList", constant=True)
    def cloudProfiles(self) -> list[str]:
        return self.cloud_profiles

    @Property(bool, notify=stateChanged)
    def llamaServerRunning(self) -> bool:
        return self.llama_server_running

    @Property(str, notify=stateChanged)
    def sourceLanguage(self) -> str:
        return self._source_language

    @Property(str, constant=True)
    def builtinSkillsDirectory(self) -> str:
        return self.builtin_skills_directory

    @Property(str, constant=True)
    def userSkillsDirectory(self) -> str:
        return self.user_skills_directory

    @Property("QVariantList", notify=skillsChanged)
    def builtinSkills(self) -> list[dict[str, Any]]:
        return self.builtin_skills

    @Property("QVariantList", notify=skillsChanged)
    def userSkills(self) -> list[str]:
        return self.user_skills

    @Property(str, constant=True)
    def skillTemplate(self) -> str:
        return self._skill_template

    @Property(str, notify=stateChanged)
    def glossaryPath(self) -> str:
        return self._glossary_path

    @Property(str, notify=stateChanged)
    def glossaryStatus(self) -> str:
        return self.glossary_status

    @Property("QVariantList", constant=True)
    def skillOptions(self) -> list[str]:
        return self.skill_options

    @Property(int, notify=stateChanged)
    def chunkSize(self) -> int:
        return self._chunk_size

    @Property(str, notify=stateChanged)
    def systemPrompt(self) -> str:
        return self._system_prompt

    @Property(str, notify=stateChanged)
    def skipPatterns(self) -> str:
        return self._skip_patterns

    def _cloud_profiles_data(self) -> list[dict[str, Any]]:
        return [dict(item) for item in CLOUD_MODELS_CONFIG]

    def _cloud_profile_data(self, name: str) -> dict[str, Any]:
        stored = self.settings.cloud_profiles.get(name)
        if stored:
            return dict(stored)
        for item in CLOUD_MODELS_CONFIG:
            if item.get("name") == name:
                return dict(item)
        return {"name": name}

    def _store_active_cloud_profile(self) -> None:
        if self._backend_type != "cloud" or not self._cloud_profile:
            return
        profile = self._cloud_profile_data(self._cloud_profile)
        profile.update(
            {
                "name": self._cloud_profile,
                "provider": profile.get("provider", "openai"),
                "base_url": self._base_url,
                "model": self._model_name,
            }
        )
        profile.pop("api_key", None)
        self.settings.cloud_profiles[self._cloud_profile] = profile
        self.secret_store.set_service_api_key(self._cloud_profile, self._api_key)

    def _store_local_api_key(self) -> None:
        if self._backend_type == "llama":
            self.secret_store.set_service_api_key("local", self._api_key)

    def _load_cloud_profile(self, name: str) -> None:
        profile = self._cloud_profile_data(name)
        legacy_key = str(profile.get("api_key", ""))
        stored_key = self.secret_store.get_service_api_key(name)
        self._base_url = str(profile.get("base_url", ""))
        self._api_key = stored_key or legacy_key
        self._model_name = str(profile.get("model", profile.get("engine", "default")))
        if legacy_key and not stored_key:
            self.secret_store.set_service_api_key(name, legacy_key)
            profile.pop("api_key", None)
            self.settings.cloud_profiles[name] = profile

    def _append_log(self, message: str) -> None:
        self._log_text = f"{self._log_text}\n{message}" if self._log_text else message
        self.logChanged.emit()

    def _set_error(self, message: str) -> None:
        self._error_message = message
        self.errorChanged.emit()
        self._status_text = message
        self._notify()

    def _skill_formats_for_file(self, filename: str) -> dict[str, set[str]]:
        """Zwróć mapę nazw skilli do obsługiwanych rozszerzeń pliku."""
        formats: dict[str, set[str]] = {}
        builtin_formats = {
            "markdown.md": {"md", "markdown"},
            "html.md": {"html", "htm", "xhtml"},
            "docx.md": {"docx"},
            "odt.md": {"odt"},
            "epub.md": {"epub"},
            "plaintext.md": {"txt", "text"},
            "pdf.md": {"pdf"},
        }
        formats.update(builtin_formats)

        if self.user_skills_dir.is_dir():
            for path in self.user_skills_dir.glob("*.md"):
                try:
                    lines = path.read_text(encoding="utf-8").splitlines()
                except (OSError, UnicodeError):
                    continue
                if not lines or lines[0].strip() != "---":
                    continue
                for line in lines[1:]:
                    if line.strip() == "---":
                        break
                    if line.startswith("formats:"):
                        values = line.split(":", 1)[1]
                        formats[path.name] = {
                            item.strip().lower().lstrip(".")
                            for item in values.split(",")
                            if item.strip()
                        }
                        break
        return formats

    def _auto_select_skill_for_input(self, value: str) -> None:
        """Automatycznie wybierz skill zgodny z rozszerzeniem pliku."""
        if not value.strip():
            return
        extension = Path(value.strip()).suffix.lower().lstrip(".")
        if not extension:
            return

        formats = self._skill_formats_for_file(value)
        self._enabled_skills.clear()
        self._disabled_user_skills = set(self.user_skills)

        for filename, extensions in formats.items():
            if extension not in extensions:
                continue
            if filename in {item[1] for item in SKILL_OPTIONS}:
                self._enabled_skills.add(filename)
            else:
                self._disabled_user_skills.discard(filename)
            break
        self.settings.enabled_skills = sorted(
            self._enabled_skills | (set(self.user_skills) - self._disabled_user_skills)
        )
        self.skillsChanged.emit()

    def _propose_output_path(self) -> None:
        if not self._input_path or not self._target_language:
            return
        source = Path(self._input_path)
        self._output_path = str(
            source.with_name(f"{source.stem}_{self._target_language}{source.suffix}")
        )
        self._output_path_auto_generated = True

    @Slot(str)
    def set_input_path(self, value: str) -> None:
        value = value.replace("file://", "")
        if not value:
            return
        self._input_path = value
        self._auto_select_skill_for_input(value)
        if self._backend_type == "apertium":
            self._detect_apertium_source_from_input(Path(value))
        if self._output_path_auto_generated:
            self._propose_output_path()
        self._notify()

    @Slot(str)
    def set_output_path(self, value: str) -> None:
        self._output_path = value.replace("file://", "")
        self._output_path_auto_generated = False
        self._notify()

    @Slot(str)
    def set_target_language(self, value: str) -> None:
        normalized = value.strip()
        if not normalized:
            return
        if self._backend_type == "apertium":
            language_map = {
                label: code for label, code in self._apertium_target_options
            }
            selected = language_map.get(normalized)
            if selected is not None:
                self._target_language = selected
            if self._output_path_auto_generated:
                self._propose_output_path()
            self._notify()
            return

        language_map = {
            t(key): code
            for (_, code), key in zip(TARGET_LANGUAGE_OPTIONS, TARGET_LANGUAGE_I18N_KEYS, strict=True)
        }
        self._target_language = language_map.get(normalized, normalized)
        if self._output_path_auto_generated:
            self._propose_output_path()
        self._notify()

    @Slot(str)
    def set_source_language(self, value: str) -> None:
        normalized = value.strip()
        language_map = {label: code for label, code in self._apertium_source_options}
        selected = language_map.get(normalized, normalized)
        if selected != "auto" and selected not in APERTIUM_LANGUAGE_CODES:
            return
        self._source_language = selected
        self._detected_source_language = selected if selected != "auto" else None
        self._refresh_apertium_language_selection()
        self.settings.source_language = (
            "auto" if self._backend_type == "apertium" else self._source_language
        )
        if self.settings_path:
            save_settings(self.settings, self.settings_path)
        else:
            save_settings(self.settings)
        self._notify()

    @Slot(str)
    def setInputPath(self, value: str) -> None:
        self.set_input_path(value)

    @Slot(str)
    def setOutputPath(self, value: str) -> None:
        self.set_output_path(value)

    @Slot(str)
    def setTargetLanguage(self, value: str) -> None:
        self.set_target_language(value)

    @Slot(str)
    def setSourceLanguage(self, value: str) -> None:
        self.set_source_language(value)

    @Slot()
    def startTranslation(self) -> None:
        self.start_translation()

    @Slot()
    def cancelTranslation(self) -> None:
        self.cancel_translation()

    @Slot(str)
    def setBackendType(self, value: str) -> None:
        self.set_backend_type(value)
        self.settings.backend_type = self._backend_type
        save_settings(self.settings, self.settings_path) if self.settings_path else save_settings(self.settings)

    @Slot(int)
    def setBackendTypeIndex(self, index: int) -> None:
        self.set_backend_type_index(index)
        self.settings.backend_type = self._backend_type
        save_settings(self.settings, self.settings_path) if self.settings_path else save_settings(self.settings)

    @Slot(str)
    def setBaseUrl(self, value: str) -> None:
        self.set_base_url(value)

    @Slot(str)
    def setApiKey(self, value: str) -> None:
        self.set_api_key(value)

    @Slot(str)
    def setModelName(self, value: str) -> None:
        self.set_model_name(value)

    @Slot(str)
    def setGgufPath(self, value: str) -> None:
        self.set_gguf_path(value)

    @Slot(str)
    def setComputeMode(self, value: str) -> None:
        self.set_compute_mode(value)

    @Slot(str)
    def setChatTemplate(self, value: str) -> None:
        self.set_chat_template(value)

    @Slot(int)
    def setParallel(self, value: int) -> None:
        self.set_parallel(value)

    @Slot(str)
    def setCloudProfile(self, value: str) -> None:
        self.set_cloud_profile(value)

    @Slot()
    def toggleLlamaServer(self) -> None:
        self.toggle_llama_server()

    @Slot(str)
    def setGlossaryPath(self, value: str) -> None:
        self.set_glossary_path(value)

    @Slot(str, str)
    def addGlossaryEntry(self, term: str, translation: str) -> None:
        self.add_glossary_entry(term, translation)

    @Slot(str, result=bool)
    def skillEnabled(self, skill_name: str) -> bool:
        return self.skill_enabled(skill_name)

    @Slot(str, bool)
    def setSkillEnabled(self, skill_name: str, enabled: bool) -> None:
        self.set_skill_enabled(skill_name, enabled)

    @Slot()
    def refreshSkills(self) -> None:
        self.refresh_skills()

    @Slot(str)
    def importSkill(self, source_path: str) -> None:
        self.import_skill(source_path)

    @Slot()
    def newSkill(self) -> None:
        self.saveSkillTemplate(self._skill_template)

    @Slot(int)
    def setChunkSize(self, value: int) -> None:
        self.set_chunk_size(value)

    @Slot(float)
    def setTemperature(self, value: float) -> None:
        self.set_temperature(value)

    @Slot(str)
    def setSystemPrompt(self, value: str) -> None:
        self.set_system_prompt(value)

    @Slot(str)
    def setSkipPatterns(self, value: str) -> None:
        self.set_skip_patterns(value)

    @Slot(str)
    def setTheme(self, value: str) -> None:
        self.set_theme(value)

    @Slot(str)
    def setApplicationLanguage(self, value: str) -> None:
        self.set_application_language(value)

    @Slot()
    def saveSettings(self) -> None:
        self.save_settings()

    @Slot()
    def resetSettings(self) -> None:
        self.reset_settings()

    @Slot(str)
    def set_server_host(self, value: str) -> None:
        host = normalize_local_server_host(value)
        self.settings.server_host = host
        self._notify()

    @Slot(int)
    def set_server_port(self, value: int) -> None:
        self.settings.server_port = max(1111, min(65535, int(value)))
        self._notify()

    @Slot(bool)
    def set_auto_start_server(self, value: bool) -> None:
        self.settings.auto_start_server = bool(value)
        self._notify()

    @Slot(bool)
    def set_cache_clear_after_translation(self, value: bool) -> None:
        self.settings.cache_clear_after_translation = bool(value)
        self._notify()

    @Slot(bool)
    def set_restart_llama_after_translation(self, value: bool) -> None:
        self.settings.restart_llama_after_translation = bool(value)
        self._notify()

    @Slot(bool)
    def set_restart_apertium_after_translation(self, value: bool) -> None:
        self.settings.restart_apertium_after_translation = bool(value)
        self._notify()

    @Slot(bool)
    def set_reconnect_cloud_after_translation(self, value: bool) -> None:
        self.settings.reconnect_cloud_after_translation = bool(value)
        self._notify()

    @Slot(str)
    def set_mozhi_instance(self, value: str) -> None:
        value = value.strip() or "auto"
        if value != "auto" and value not in MOZHI_INSTANCES:
            raise ValueError(f"Nieznana instancja Mozhi: {value}")
        self.settings.mozhi_instance = value
        self._store_active_cloud_profile()
        self._notify()

    @Slot(str)
    def set_mozhi_engine(self, value: str) -> None:
        valid = {engine_id for _, engine_id in MOZHI_ENGINES}
        if value not in valid:
            raise ValueError(f"Nieznany silnik Mozhi: {value}")
        self.settings.mozhi_engine = value
        self._store_active_cloud_profile()
        self._notify()

    @Slot()
    def random_server_port(self) -> None:
        import random

        self.set_server_port(random.randint(1111, 65535))

    @Slot()
    def restart_server(self) -> None:
        if self._backend_type == "apertium":
            self._append_log(
                "Apertium uruchamia osobny proces dla każdego tłumaczenia; "
                "nie ma trwałego procesu do restartu."
            )
            self._notify()
            return
        if self._backend_type != "llama":
            return
        self._request_llama_server(
            restart=True,
            success_message="Uruchomiono ponownie serwer llama.cpp.",
        )

    @Slot(str)
    def setServerHost(self, value: str) -> None:
        self.set_server_host(value)

    @Slot(int)
    def setServerPort(self, value: int) -> None:
        self.set_server_port(value)

    @Slot(bool)
    def setAutoStartServer(self, value: bool) -> None:
        self.set_auto_start_server(value)

    @Slot(bool)
    def setCacheClearAfterTranslation(self, value: bool) -> None:
        self.set_cache_clear_after_translation(value)

    @Slot(bool)
    def setRestartLlamaAfterTranslation(self, value: bool) -> None:
        self.set_restart_llama_after_translation(value)

    @Slot(bool)
    def setRestartApertiumAfterTranslation(self, value: bool) -> None:
        self.set_restart_apertium_after_translation(value)

    @Slot(bool)
    def setReconnectCloudAfterTranslation(self, value: bool) -> None:
        self.set_reconnect_cloud_after_translation(value)

    @Slot(str)
    def setMozhiInstance(self, value: str) -> None:
        self.set_mozhi_instance(value)

    @Slot(str)
    def setMozhiEngine(self, value: str) -> None:
        self.set_mozhi_engine(value)

    @Slot()
    def randomServerPort(self) -> None:
        self.random_server_port()

    @Slot()
    def restartServer(self) -> None:
        self.restart_server()

    def _set_backend_type_value(self, backend_type: str) -> None:
        self._store_active_cloud_profile()
        self._store_local_api_key()
        previous_backend = self._backend_type
        if self._backend_type == "llama" and backend_type != "llama":
            # Zmiana na inny backend kończy lokalny proces llama.cpp.
            self.core.stop_llama()
        self._backend_type = backend_type
        if self._backend_type == "apertium":
            self._detect_apertium_source_from_input(Path(self._input_path))
            self._refresh_apertium_language_selection()
        elif not self._target_language:
            # Apertium może wyczyścić target, gdy dla wykrytego źródła nie ma pary.
            # Po przełączeniu na backend z globalnym wyborem celu stan musi być ważny.
            self._target_language = "pl"
        if self._backend_type == "cloud":
            self._load_cloud_profile(self._cloud_profile)
        elif self._backend_type == "custom":
            self._base_url = self.settings.custom_server_url
            self._api_key = ""
        elif self._backend_type == "llama":
            self._api_key = self.secret_store.get_service_api_key("local")
        if previous_backend == "llama" and self._backend_type != "llama":
            self._append_log("Zatrzymano serwer llama.cpp przy zmianie serwera.")
        if previous_backend != "llama" and self._backend_type == "llama":
            self._append_log("Wybrano llama.cpp. Uruchamianie serwera automatycznie...")
            self._maybe_autostart_server(force=True)
        self._notify()

    @Slot(str)
    def set_backend_type(self, value: str) -> None:
        mapping = {
            t("backend.local_server"): "llama",
            t("backend.apertium_local_server"): "apertium",
            t("ui.apertium"): "apertium",
            t("backend.cloud_server"): "cloud",
            t("custom.server_type"): "custom",
            "llama.cpp": "llama",
            "Apertium": "apertium",
            "Chmura": "cloud",
            "Własny": "custom",
        }
        self._set_backend_type_value(mapping.get(value, value))

    @Slot(int)
    def set_backend_type_index(self, index: int) -> None:
        backend_types = ("llama", "apertium", "cloud", "custom")
        if not 0 <= index < len(backend_types):
            raise ValueError(f"Nieprawidłowy indeks serwera: {index}")
        self._set_backend_type_value(backend_types[index])

    @Slot(str)
    def set_base_url(self, value: str) -> None:
        self._base_url = value
        if self._backend_type == "llama":
            parsed = urlsplit(value)
            if parsed.hostname:
                self.settings.server_host = normalize_local_server_host(parsed.hostname)
            if parsed.port:
                self.settings.server_port = parsed.port
        elif self._backend_type == "custom":
            self.settings.custom_server_url = value
        self._store_active_cloud_profile()
        self._notify()

    @Slot(str)
    def set_api_key(self, value: str) -> None:
        self._api_key = value
        if self._backend_type == "cloud":
            self._store_active_cloud_profile()
        elif self._backend_type == "llama":
            self._store_local_api_key()
        self._notify()

    @Slot(str)
    def set_model_name(self, value: str) -> None:
        self._model_name = value
        self._store_active_cloud_profile()
        self._notify()

    @Slot(str)
    def set_gguf_path(self, value: str) -> None:
        """Zapisz ścieżkę GGUF jako lokalną ścieżkę pliku, także z QML QUrl."""
        url = QUrl(value)
        if url.isLocalFile():
            value = url.toLocalFile()
        self._gguf_path = value
        self.settings.server_gguf_path = value
        self._notify()

    @Slot(str)
    def set_compute_mode(self, value: str) -> None:
        self._compute_mode = value
        self._notify()

    @Slot(str)
    def set_chat_template(self, value: str) -> None:
        normalized = {
            "janji": "",
            "jinja": "",
            "chatml": "chatml",
            "TranslateGemma": "translategemma",
        }.get(value, value)
        self._chat_template = normalized
        self._notify()

    @Slot(int)
    def set_parallel(self, value: int) -> None:
        self._parallel = max(1, min(8, value))
        self._notify()

    @Slot(int)
    def set_chunk_size(self, value: int) -> None:
        self._chunk_size = max(100, min(100000, value))
        self._notify()

    @Slot(float)
    def set_temperature(self, value: float) -> None:
        self._temperature = max(0.0, min(1.0, value))
        self._notify()

    @Slot(str)
    def set_system_prompt(self, value: str) -> None:
        self._system_prompt = value
        self._notify()

    @Slot(str)
    def set_skip_patterns(self, value: str) -> None:
        self._skip_patterns = value
        self._notify()

    @Slot(str)
    def set_glossary_path(self, value: str) -> None:
        self._glossary_path = value.replace("file://", "")
        self._notify()

    @Property(str, notify=stateChanged)
    def glossary_status(self) -> str:
        path = Path(self._glossary_path)
        if not path.is_file():
            return t("glossary.no_file")
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = [row for row in csv.reader(handle) if any(cell.strip() for cell in row)]
        except (OSError, UnicodeError, csv.Error):
            return t("glossary.no_file")
        return t("glossary.count", count=len(rows))

    @staticmethod
    def _skill_translation_keys() -> tuple[str, ...]:
        return (
            "skill.markdown",
            "skill.html",
            "skill.docx",
            "skill.odt",
            "skill.epub",
            "skill.plain_text",
            "skill.pdf",
        )

    def _skill_filename_for_label(self, skill_name: str) -> str | None:
        keys = self._skill_translation_keys()
        for (default_label, filename), key in zip(SKILL_OPTIONS, keys, strict=True):
            if skill_name in {default_label, t(key)}:
                return filename
        return None

    @Slot(str, result=bool)
    def skill_enabled(self, skill_name: str) -> bool:
        filename = self._skill_filename_for_label(skill_name)
        if filename:
            return filename in self._enabled_skills
        if skill_name in self.user_skills:
            return skill_name not in self._disabled_user_skills
        return False

    @Slot(str, bool)
    def set_skill_enabled(self, skill_name: str, enabled: bool) -> None:
        filename = self._skill_filename_for_label(skill_name)
        if filename:
            if enabled:
                self._enabled_skills.add(filename)
            else:
                self._enabled_skills.discard(filename)
        elif skill_name in self.user_skills:
            if enabled:
                self._disabled_user_skills.discard(skill_name)
            else:
                self._disabled_user_skills.add(skill_name)
        self.settings.enabled_skills = sorted(
            self._enabled_skills | (set(self.user_skills) - self._disabled_user_skills)
        )
        self._notify()

    @Slot(str)
    def set_theme(self, value: str) -> None:
        if value not in {"system", "dark", "light"}:
            return
        self._theme = value
        self.settings.theme = value
        self.themeChanged.emit()
        self._notify()

    @Slot(str)
    def set_application_language(self, value: str) -> None:
        if value == self._application_language:
            return
        self._application_language = value
        self.settings.language = value
        set_language(value)
        self._help_topics = self._load_help_topics(value)
        self.languageChanged.emit()
        self._notify()

    @Slot(str)
    def set_cloud_profile(self, value: str) -> None:
        self._store_active_cloud_profile()
        self._cloud_profile = value
        self.settings.cloud_profile = value
        self._load_cloud_profile(value)
        if value == "Mozhi":
            # Mozhi jest usługą bez klucza API; wybór instancji „auto”
            # uruchamia pomiar dostępnych instancji i wybór najszybszej.
            self._base_url = "auto"
            self._api_key = ""
        self._store_active_cloud_profile()
        self._notify()

    @Slot(int, int, int, int)
    def save_window_state(self, x: int, y: int, width: int, height: int) -> None:
        self.settings.window_x = int(x)
        self.settings.window_y = int(y)
        self.settings.window_width = max(1, int(width))
        self.settings.window_height = max(1, int(height))
        save_settings(self.settings, self.settings_path) if self.settings_path else save_settings(self.settings)

    @Slot(int, int, int, int)
    def saveWindowState(self, x: int, y: int, width: int, height: int) -> None:
        self.save_window_state(x, y, width, height)

    @Slot()
    def save_settings(self) -> None:
        self._store_active_cloud_profile()
        self.settings.backend_type = self._backend_type
        if self._backend_type == "llama":
            self.settings.base_url = self.server_url
        elif self._backend_type == "custom":
            self.settings.custom_server_url = self._base_url
        else:
            self.settings.base_url = self._base_url
        self._store_local_api_key()
        self.settings.model = self._model_name
        self.settings.cloud_profile = self._cloud_profile
        self.settings.enabled_skills = sorted(
            self._enabled_skills | (set(self.user_skills) - self._disabled_user_skills)
        )
        self.settings.server_host = self.settings.server_host.strip() or "127.0.0.1"
        self.settings.server_gguf_path = self._gguf_path
        self.settings.last_input_path = self._input_path
        self.settings.last_output_path = self._output_path
        self.settings.server_compute_mode = self._compute_mode
        self.settings.server_chat_template = self._chat_template
        self.settings.server_parallel = self._parallel
        self.settings.server_port = self.settings.server_port
        self.settings.auto_start_server = self.settings.auto_start_server
        self.settings.cache_clear_after_translation = self.settings.cache_clear_after_translation
        self.settings.restart_llama_after_translation = self.settings.restart_llama_after_translation
        self.settings.restart_apertium_after_translation = self.settings.restart_apertium_after_translation
        self.settings.reconnect_cloud_after_translation = self.settings.reconnect_cloud_after_translation
        self.settings.mozhi_instance = self.settings.mozhi_instance
        self.settings.mozhi_engine = self.settings.mozhi_engine
        self.settings.chunk_size = self._chunk_size
        self.settings.temperature = self._temperature
        self.settings.target_language = self._target_language
        self.settings.source_language = self._source_language
        self.settings.glossary_path = self._glossary_path
        self.settings.system_prompt = self._system_prompt
        self.settings.skip_line_patterns = [line for line in self._skip_patterns.splitlines() if line]
        self.settings.theme = self._theme
        self.settings.language = self._application_language
        save_settings(self.settings, self.settings_path) if self.settings_path else save_settings(self.settings)
        self._status_text = "Ustawienia zapisane."
        self._notify()

    @Slot()
    def reset_settings(self) -> None:
        self.settings = AppSettings()
        save_settings(self.settings, self.settings_path) if self.settings_path else save_settings(self.settings)
        self._load_settings(self.settings)
        self._notify()

    def _refresh_llama_server_url(self) -> None:
        """Potwierdź gotowość llama.cpp i odśwież adres używany przez GUI."""
        if self.core.runtime is None or not self.core.runtime.is_running():
            return
        host = self.core.runtime.config.host
        port = self.core.runtime.config.port
        health_url = f"http://{host}:{port}/health"
        try:
            with urlopen(Request(health_url, method="GET"), timeout=2.0) as response:
                if response.status != 200:
                    return
        except (OSError, URLError):
            return
        self.settings.server_host = host
        self.settings.server_port = port
        self._base_url = self.server_url
        self._notify()

    def _request_llama_server(
        self,
        *,
        restart: bool = False,
        on_ready: Callable[[], None] | None = None,
        success_message: str | None = None,
    ) -> bool:
        """Zleć start/restart llama.cpp i opcjonalnie wykonaj akcję po gotowości."""
        if self._backend_type != "llama":
            return False
        if not restart and self.core.runtime is not None and self.core.runtime.is_running():
            if on_ready is not None:
                on_ready()
            return True
        if on_ready is not None:
            self._server_ready_callbacks.append(on_ready)
        if self._server_operation_busy:
            return False
        self._queue_server_operation(
            restart=restart,
            success_message=success_message
            or ("Uruchomiono ponownie serwer llama.cpp." if restart else "Uruchomiono serwer llama.cpp."),
        )
        return False

    def _queue_server_operation(self, *, restart: bool, success_message: str) -> None:
        if self._server_operation_busy:
            return
        if self._backend_type != "llama":
            return
        model_path = self._gguf_path
        host = normalize_local_server_host(self.settings.server_host)
        self.settings.server_host = host
        port = self.settings.server_port
        compute_mode = self._compute_mode
        parallel = self.effective_server_parallel
        chat_template = self._chat_template
        chunk_size = self._chunk_size

        def operation() -> None:
            if restart and self.core.runtime is not None and self.core.runtime.is_running():
                self.core.stop_llama()
            self.core.start_llama(
                model_path=model_path,
                host=host,
                port=port,
                compute_mode=compute_mode,
                parallel=parallel,
                chat_template=chat_template,
                chunk_size=chunk_size,
            )

        self._server_operation_busy = True
        self._status_text = "Uruchamianie serwera llama.cpp..." if not restart else "Restartowanie serwera llama.cpp..."
        self._notify()
        thread = QThread()
        worker = _ServerWorker(operation, success_message)
        self._server_thread = thread
        self._server_worker = worker
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.finished.connect(self._on_server_operation_finished)
        worker.failed.connect(self._on_server_operation_failed)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_server_operation)
        thread.start()

    @Slot()
    def _on_server_operation_finished(self, success_message: str) -> None:
        self._server_operation_busy = False
        self._refresh_llama_server_url()
        self._status_text = "Serwer uruchomiony."
        self._append_log(success_message)
        self._move_ready_message_to_end()
        self._notify()
        callbacks = self._server_ready_callbacks
        self._server_ready_callbacks = []
        for callback in callbacks:
            callback()

    @Slot(str)
    def _on_server_operation_failed(self, message: str) -> None:
        self._server_operation_busy = False
        self._server_ready_callbacks.clear()
        self._set_error(message)
        self._notify()

    @Slot()
    def _clear_server_operation(self) -> None:
        self._server_thread = None
        self._server_worker = None

    def _maybe_autostart_server(
        self,
        *,
        force: bool = False,
        on_ready: Callable[[], None] | None = None,
    ) -> bool:
        """Uruchom llama.cpp lub podepnij akcję oczekującą na gotowość."""
        if self._backend_type != "llama":
            return False
        if not force and not self.settings.auto_start_server:
            return False
        return self._request_llama_server(on_ready=on_ready)

    def _post_translation_actions(self) -> None:
        if self.settings.cache_clear_after_translation:
            self.core.clear_translation_cache()
            self._append_log(t("log.buffer_cleared"))
        if (
            self.settings.restart_llama_after_translation
            and self._backend_type == "llama"
        ):
            self._request_llama_server(
                restart=True,
                success_message=t("log.server_started"),
            )

        if (
            self.settings.restart_apertium_after_translation
            and self._backend_type == "apertium"
        ):
            self.core.restart_apertium_service()
            self._append_log(t("log.apertium_service_restarted"))

        if (
            self.settings.reconnect_cloud_after_translation
            and self._backend_type in {"cloud", "custom"}
        ):
            self.core.reconnect_cloud()
            self._append_log(t("log.cloud_reconnected"))

    def _migrate_legacy_secrets(self) -> None:
        """Przenieś wszystkie legacy secrets do SecretStore przed dalszą pracą GUI."""
        legacy_local_key = self.settings.last_local_api_key or self.settings.api_key
        if legacy_local_key and not self.secret_store.get_service_api_key("local"):
            self.secret_store.set_service_api_key("local", legacy_local_key)

        for name, profile in self.settings.cloud_profiles.items():
            if not isinstance(profile, dict):
                continue
            legacy_key = str(profile.get("api_key", ""))
            if legacy_key and not self.secret_store.get_service_api_key(name):
                self.secret_store.set_service_api_key(name, legacy_key)
            profile.pop("api_key", None)

        self.settings.last_local_api_key = ""
        self.settings.api_key = ""

    def _load_settings(self, settings: AppSettings) -> None:
        self._input_path = settings.last_input_path
        self.settings.server_host = self.settings.server_host.strip() or "127.0.0.1"
        self._output_path = settings.last_output_path
        self._target_language = settings.target_language.strip()
        self._backend_type = settings.backend_type
        if not self._target_language and self._backend_type != "apertium":
            self._target_language = "pl"
        self._base_url = settings.base_url
        if self._backend_type == "custom":
            self._base_url = settings.custom_server_url
        stored_local_key = self.secret_store.get_service_api_key("local")
        self._api_key = stored_local_key if self._backend_type == "llama" else ""
        self._model_name = settings.model
        self._gguf_path = settings.server_gguf_path
        self._compute_mode = settings.server_compute_mode
        self._chat_template = settings.server_chat_template
        self._parallel = settings.server_parallel
        self._chunk_size = settings.chunk_size
        self._temperature = settings.temperature
        self._system_prompt = settings.system_prompt
        self._skip_patterns = "\n".join(settings.skip_line_patterns)
        self._glossary_path = settings.glossary_path
        # GUI udostępnia obecnie wyłącznie motyw systemowy.
        # Mechanizm zmiany motywu pozostaje zachowany i ma zostać przywrócony
        # po rozwiązaniu problemu z przełączaniem schematu w Qt/Fusion.
        self._theme = "system"
        self.settings.theme = "system"
        self._application_language = settings.language
        self._source_language = (
            "auto" if self._backend_type == "apertium" else settings.source_language
        )
        self._cloud_profile = settings.cloud_profile
        if self._backend_type == "cloud":
            self._load_cloud_profile(self._cloud_profile)

    def _selection(self):
        backend = self._backend_type
        self.core.backend_controller.select(backend)
        if backend == "cloud":
            profile = self.settings.normalized_cloud_profile()
            provider = profile.get("provider", "openai")
            base_url = self._base_url
            engine = profile.get("model", profile.get("engine", "default"))
            if provider == "mozhi":
                base_url = self.settings.mozhi_instance
                engine = self.settings.mozhi_engine
            selection = self.core.select_backend(
                BackendRequest(
                    backend="cloud",
                    configuration=BackendConfiguration(
                        {
                            "provider": provider,
                            "base_url": base_url,
                            "api_key": self._api_key,
                            "model": profile.get("model", self._model_name),
                            "engine": engine,
                            "timeout": 30.0,
                        }
                    ),
                )
            )
            if provider == "mozhi":
                self._effective_mozhi_url = selection.configuration.get("base_url", "")
                self.stateChanged.emit()
            return selection
        if backend == "apertium":
            return self.core.select_backend(BackendRequest(backend="apertium"))
        if backend == "custom":
            return self.core.select_backend(
                BackendRequest(
                    backend="custom",
                    configuration=BackendConfiguration(
                        {
                            "base_url": self._base_url,
                            "api_key": self._api_key,
                            "model": self._model_name,
                            "timeout": 120.0,
                        }
                    ),
                )
            )
        return self.core.select_backend(
            BackendRequest(
                backend="llama",
                configuration=BackendConfiguration(
                    {
                        "base_url": self.server_url,
                        "api_key": self._api_key or "local",
                        "model": self._gguf_path or self._model_name,
                        # TranslateGemma na CPU może potrzebować długiego czasu przy dużych
                        # chunkach. Limit obejmuje oczekiwanie na cały response HTTP.
                        "timeout": 1800.0,
                        "compute_mode": self._compute_mode,
                        "chat_template": self._chat_template,
                        "parallel": self._parallel,
                    }
                ),
            )
        )

    def _normalize_target_language_for_backend(self) -> None:
        """Zapewnij niepusty język docelowy przed uruchomieniem tłumaczenia.

        Dla llama.cpp pusty target nie jest prawidłowym stanem kontraktu
        TranslateGemma. Domyślnym celem aplikacji jest język polski.
        """
        if self._backend_type == "llama" and not self._target_language.strip():
            self._target_language = "pl"

    def _selected_skill_label(self) -> str:
        for label, filename in SKILL_OPTIONS:
            if filename in self._enabled_skills:
                return label
        enabled_user = sorted(set(self.user_skills) - self._disabled_user_skills)
        return enabled_user[0] if enabled_user else "brak"

    def _move_ready_message_to_end(self) -> None:
        ready = t("log.ready")
        skill_prefix = "Wybrano skill: "
        lines = [
            line
            for line in self._log_text.splitlines()
            if line != ready and not line.startswith(skill_prefix)
        ]
        self._log_text = "\n".join(lines)
        self._append_log(t("log.skill_selected", skill=self._selected_skill_label()))
        self._append_log(ready)

    @Slot()
    def start_translation(self) -> None:
        if self._backend_type == "llama" and (
            self.core.runtime is None or not self.core.runtime.is_running()
        ):
            self._maybe_autostart_server(
                force=True,
                on_ready=self._start_translation_now,
            )
            return
        self._start_translation_now()

    def _start_translation_now(self) -> None:
        if self._is_translating:
            return
        self._normalize_target_language_for_backend()
        input_path = Path(self._input_path)
        output_path = Path(self._output_path)
        if not input_path.is_file():
            self._set_error(t("msg.input_file_required"))
            return
        if not output_path.name:
            self._set_error(t("msg.output_file_required"))
            return
        try:
            selection = self._selection()
            self._move_ready_message_to_end()
            source_language = self._source_language
            if self._backend_type == "apertium":
                available_targets = {
                    code for _, code in self._apertium_target_options
                }
                if source_language == "auto":
                    self._set_error(t("apertium.no_pair"))
                    return
                if self._target_language not in available_targets:
                    self._set_error(t("apertium.no_pair"))
                    return
            service = self.core.build_translation_service(
                selection=selection,
                source_language=source_language,
                target_language=self._target_language,
                chunk_size=self._chunk_size,
                temperature=self._temperature,
                parallel=self.effective_translation_parallel,
            )
        except Exception as exc:  # noqa: BLE001
            self._set_error(str(exc))
            return

        self._progress = 0
        self._elapsed_seconds = 0
        self._current_speed = 0
        self._average_speed = 0
        self._translation_stage = "Przygotowanie tłumaczenia"
        self._translation_block_current = 0
        self._translation_block_total = 0
        self._translated_characters = 0
        self._error_message = ""
        self._is_translating = True
        self._status_text = t("status.translating")
        self._append_log(t("log.translation_started_short"))
        self.progressChanged.emit()
        self._notify()

        self._started_at = time.monotonic()
        self._last_progress = 0
        self._last_progress_at = self._started_at
        self._timer.start()

        operation = {
            "input": input_path,
            "output": output_path,
            "source": source_language,
            "target": self._target_language,
            "workspace": self.core.workspace,
            "skip_line_patterns": tuple(line for line in self._skip_patterns.splitlines() if line.strip()),
        }
        self._thread = QThread()
        self._worker = _TranslationWorker(service, operation)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.log.connect(self._append_log)
        self._worker.documentInfo.connect(self._on_document_info)
        self._worker.chunkStart.connect(self._on_chunk_start)
        self._worker.chunkComplete.connect(self._on_chunk_complete)
        self._worker.chunkFailed.connect(self._on_chunk_failed)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.cancelled.connect(self._on_cancelled)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._worker.cancelled.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    @Slot()
    def cancel_translation(self) -> None:
        if self._worker is not None:
            self._worker.token.cancel()
            runtime = self.core.runtime
            if runtime is not None:
                runtime.cancel(self._worker.token)
            self._status_text = t("status.cancelling")
            self._append_log(t("log.cancel_requested"))
            self._notify()

    @Slot()
    def toggle_llama_server(self) -> None:
        if self._backend_type != "llama" or self._server_operation_busy:
            return
        if self.core.runtime is not None and self.core.runtime.is_running():
            self._queue_server_stop()
            return
        self._request_llama_server()

    def _queue_server_stop(self) -> None:
        if self._server_operation_busy:
            return
        self._server_operation_busy = True
        self._status_text = "Zatrzymywanie serwera llama.cpp..."
        self._notify()
        thread = QThread()
        worker = _ServerWorker(self.core.stop_llama, "Zatrzymano serwer llama.cpp.")
        self._server_thread = thread
        self._server_worker = worker
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._on_server_operation_finished)
        worker.failed.connect(self._on_server_operation_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_server_operation)
        thread.start()

    @Slot(str)
    def add_glossary_entry(self, term: str, translation: str) -> None:
        path = Path(self._glossary_path)
        if not path.name or not term.strip() or not translation.strip():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="") as handle:
            csv.writer(handle).writerow([term.strip(), translation.strip()])
        self._append_log("Dodano wpis do glossariusza.")
        self._notify()

    def _watch_user_skills_directory(self) -> None:
        self.user_skills_dir.mkdir(parents=True, exist_ok=True)
        path = str(self.user_skills_dir)
        if path not in self._skill_watcher.directories():
            self._skill_watcher.addPath(path)

    @Slot(str)
    def _on_skills_directory_changed(self, _path: str) -> None:
        self.refresh_skills()
        self._watch_user_skills_directory()

    @Slot()
    def refresh_skills(self) -> None:
        self.user_skills_dir.mkdir(parents=True, exist_ok=True)
        self.skillsChanged.emit()

    @Slot(str)
    def import_skill(self, source_path: str) -> None:
        source = Path(source_path.replace("file://", ""))
        if not source.is_file():
            return
        self.user_skills_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, self.user_skills_dir / source.name)
        self.refresh_skills()

    @Slot(str)
    def saveSkillTemplate(self, content: str) -> None:
        self.user_skills_dir.mkdir(parents=True, exist_ok=True)
        target = self.user_skills_dir / "nowa-umiejetnosc.md"
        index = 2
        while target.exists():
            target = self.user_skills_dir / f"nowa-umiejetnosc-{index}.md"
            index += 1
        text = content.strip() or self._skill_template
        target.write_text(text + "\n", encoding="utf-8")
        self.refresh_skills()

    @Slot(str)
    def deleteSkill(self, filename: str) -> None:
        if not filename.endswith(".md"):
            return
        target = self.user_skills_dir / Path(filename).name
        if target.is_file():
            target.unlink()
        self.refresh_skills()

    @Slot()
    def _update_metrics(self) -> None:
        if not self._is_translating:
            return
        now = time.monotonic()
        elapsed = max(0, int(now - self._started_at))
        if elapsed != self._elapsed_seconds:
            self._elapsed_seconds = elapsed
            if elapsed > 0 and self._translated_characters > 0:
                self._average_speed = round(self._translated_characters / elapsed, 2)
                self._current_speed = self._average_speed
            self.progressChanged.emit()

    @Slot(str, int, int)
    def _on_document_info(self, document_type: str, total: int, skipped: int) -> None:
        self._translation_stage = f"Wczytano dokument: {document_type}"
        self._append_log(t("log.document_loaded", document_type=document_type.upper()))
        self._append_log(t("log.fragments_skipped", count=skipped))
        self.progressChanged.emit()

    @Slot(int, int)
    def _on_chunk_start(self, current: int, total: int) -> None:
        self._translation_block_current = current
        self._translation_block_total = total
        self._translation_stage = f"Tłumaczenie bloku {current} z {total}"
        if current == 1:
            self._append_log(t("log.blocks_total", count=total))
        self._append_log(t("log.block_translation", current=current, total=total))
        self.progressChanged.emit()

    @Slot(int, int, int)
    def _on_chunk_complete(self, current: int, total: int, characters: int) -> None:
        self._translation_block_current = current
        self._translation_block_total = total
        self._translated_characters = characters
        elapsed = max(time.monotonic() - self._started_at, 0.001)
        self._current_speed = round(characters / elapsed, 2)
        self._average_speed = self._current_speed
        self._translation_stage = f"Zakończono blok {current} z {total}"
        self.progressChanged.emit()

    @Slot(int, int, str)
    def _on_chunk_failed(self, current: int, total: int, message: str) -> None:
        self._translation_block_current = current
        self._translation_block_total = total
        self._translation_stage = f"Błąd bloku {current} z {total}"
        self._is_translating = False
        self._current_speed = 0
        self._status_text = t("status.error")
        self._append_log(
            t("log.chunk_failed", current=current, total=total, message=message)
        )
        self.progressChanged.emit()

    @Slot(int, int)
    def _on_progress(self, current: int, total: int) -> None:
        self._progress = 0 if total <= 0 else int(current * 100 / total)
        self._last_progress = current
        self._last_progress_at = time.monotonic()
        self.progressChanged.emit()

    @staticmethod
    def _format_elapsed(seconds: int) -> str:
        minutes, remainder = divmod(max(0, seconds), 60)
        return f"{minutes:02d}:{remainder:02d}"

    @Slot(str)
    def _on_finished(self, path: str) -> None:
        self._timer.stop()
        self._is_translating = False
        self._progress = 100
        elapsed = max(0, int(time.monotonic() - self._started_at))
        self._elapsed_seconds = elapsed
        if elapsed > 0:
            self._average_speed = int(self._last_progress / elapsed)
        self._status_text = t("status.finished")
        self._translation_stage = "Tłumaczenie zakończone"
        if elapsed > 0:
            self._current_speed = round(self._translated_characters / elapsed, 2)
            self._average_speed = self._current_speed
        self._preview_text = self._preview_for_output(Path(path))
        self._append_log(
            t(
                "log.blocks_summary",
                count=self._translation_block_total,
                time=self._format_elapsed(elapsed),
                speed=self._current_speed,
            )
        )
        self._append_log(t("log.translation_document_saved", path=path))
        try:
            self._post_translation_actions()
        except Exception as exc:  # noqa: BLE001
            self._append_log(t("log.post_action_error", message=exc))
        self.progressChanged.emit()
        self.previewChanged.emit()
        self._notify()
        self.translationFinished.emit()

    @Slot()
    def _on_cancelled(self) -> None:
        self._timer.stop()
        self._is_translating = False
        self._current_speed = 0
        self._status_text = t("status.cancelled")
        self._append_log(t("log.translation_cancelled"))
        self.progressChanged.emit()
        self._notify()

    @Slot(str)
    def _on_failed(self, message: str) -> None:
        self._timer.stop()
        self._is_translating = False
        self._current_speed = 0
        self._status_text = t("status.error")
        self._set_error(message)
        self._append_log(t("log.error_prefix", message=message))
        self.progressChanged.emit()
        self._notify()
        self.translationFailed.emit()

    @staticmethod
    def _preview_for_output(path: Path) -> str:
        if path.suffix.lower() in {".txt", ".md", ".markdown", ".html", ".htm", ".xhtml"} and path.is_file():
            try:
                return path.read_text(encoding="utf-8")[:12000]
            except (OSError, UnicodeError):
                pass
        return f"Wynik zapisano w:\n{path}"


__all__ = ["QmlApplicationBridge"]
