"""Główny launcher GUI Qt Quick/QML V4."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from tlumacz.infrastructure.logging import configure_logging
from tlumacz.user_config import initialize_user_config

# V4 ma zawsze ładować aktualne źródła QML, a nie stary cache dyskowy.
os.environ.setdefault("QML_DISABLE_DISK_CACHE", "1")

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QPalette
from PySide6.QtQml import QQmlApplicationEngine

from tlumacz.application.translation_app import TranslationApp

from .bridge import QmlApplicationBridge

QML_FILE = Path(__file__).with_name("Main.qml")
ICON_DARK = QML_FILE.parent.parent / "tlumacz-dark.svg"
ICON_LIGHT = QML_FILE.parent.parent / "tlumacz-light.svg"


def _apply_fusion_fallback_palette(app: QGuiApplication, theme: str) -> None:
    """Zastosuj pełną paletę Fusion tylko jako fallback jawnego motywu."""
    palette = QPalette(app.palette())
    if theme == "dark":
        colors = {
            QPalette.Window: "#202124",
            QPalette.WindowText: "#f1f3f4",
            QPalette.Base: "#303134",
            QPalette.AlternateBase: "#3c4043",
            QPalette.ToolTipBase: "#303134",
            QPalette.ToolTipText: "#f1f3f4",
            QPalette.Text: "#f1f3f4",
            QPalette.Button: "#303134",
            QPalette.ButtonText: "#f1f3f4",
            QPalette.BrightText: "#ffffff",
            QPalette.Light: "#4a4b4d",
            QPalette.Midlight: "#3c4043",
            QPalette.Mid: "#2a2b2d",
            QPalette.Dark: "#202124",
            QPalette.Shadow: "#000000",
            QPalette.Highlight: "#4285f4",
            QPalette.HighlightedText: "#ffffff",
            QPalette.Link: "#8ab4f8",
            QPalette.LinkVisited: "#c58af9",
            QPalette.PlaceholderText: "#9aa0a6",
        }
    else:
        colors = {
            QPalette.Window: "#ffffff",
            QPalette.WindowText: "#202124",
            QPalette.Base: "#ffffff",
            QPalette.AlternateBase: "#f8f9fa",
            QPalette.ToolTipBase: "#ffffff",
            QPalette.ToolTipText: "#202124",
            QPalette.Text: "#202124",
            QPalette.Button: "#f8f9fa",
            QPalette.ButtonText: "#202124",
            QPalette.BrightText: "#ffffff",
            QPalette.Light: "#ffffff",
            QPalette.Midlight: "#f8f9fa",
            QPalette.Mid: "#dadce0",
            QPalette.Dark: "#9aa0a6",
            QPalette.Shadow: "#5f6368",
            QPalette.Highlight: "#1a73e8",
            QPalette.HighlightedText: "#ffffff",
            QPalette.Link: "#1a73e8",
            QPalette.LinkVisited: "#681da8",
            QPalette.PlaceholderText: "#5f6368",
        }
    for role, color in colors.items():
        palette.setColor(role, QColor(color))
    app.setPalette(palette)


def _apply_theme(app: QGuiApplication, theme: str) -> None:
    """Użyj natywnego schematu Qt, z ograniczonym fallbackiem dla Fusion."""
    style_hints = app.styleHints()
    if theme == "dark":
        style_hints.setColorScheme(Qt.ColorScheme.Dark)
    elif theme == "light":
        style_hints.setColorScheme(Qt.ColorScheme.Light)
    else:
        style_hints.unsetColorScheme()
        # Usuń ewentualną paletę fallbacku i wróć do palety platformy/stylu.
        app.setPalette(QPalette())
        return

    app.processEvents()
    window_is_dark = app.palette().window().color().lightnessF() < 0.5
    if (theme == "dark") != window_is_dark:
        _apply_fusion_fallback_palette(app, theme)


def bind_application_lifecycle(app: QGuiApplication, core: TranslationApp) -> None:
    """Podepnij zamknięcie GUI do centralnego lifecycle rdzenia aplikacji."""
    app.aboutToQuit.connect(core.close)


def _set_application_icon(app: QGuiApplication, bridge: QmlApplicationBridge) -> None:
    if bridge.theme == "dark":
        icon_path = ICON_DARK
    elif bridge.theme == "light":
        icon_path = ICON_LIGHT
    else:
        icon_path = ICON_DARK if app.palette().window().color().lightnessF() < 0.5 else ICON_LIGHT
    app.setWindowIcon(QIcon(str(icon_path)))


def main() -> int:
    initialize_user_config()
    logger = configure_logging(level=logging.DEBUG)
    logger.info("Uruchamianie aplikacji Tłumacz V4")
    app = QGuiApplication()
    bridge = QmlApplicationBridge(core=TranslationApp())
    # Styl Qt Quick Controls musi zostać zainicjalizowany już po ustawieniu
    # schematu kolorów. Dzięki temu Fusion korzysta z palety platformy Qt,
    # tak jak przy rzeczywistej zmianie wyglądu systemu.
    _apply_theme(app, bridge.theme)
    engine = QQmlApplicationEngine()
    _set_application_icon(app, bridge)
    def refresh_application_theme() -> None:
        _apply_theme(app, bridge.theme)
        _set_application_icon(app, bridge)

    bridge.themeChanged.connect(refresh_application_theme)
    app.paletteChanged.connect(lambda: _set_application_icon(app, bridge))
    bind_application_lifecycle(app, bridge.core)
    engine.rootContext().setContextProperty("bridge", bridge)
    engine.load(QUrl.fromLocalFile(str(QML_FILE)))
    if not engine.rootObjects():
        logger.error("Nie udało się uruchomić głównego widoku QML.")
        return 1
    logger.info("Aplikacja Tłumacz V4 została uruchomiona.")
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
