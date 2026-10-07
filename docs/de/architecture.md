---
id: architecture-v4-de
status: active
meta:
  contentType: Architecture
  category: governance
version: 0.40.0
updated: 2026-10-04
owner: platform-architecture
source: src/tlumacz/application/, src/tlumacz/backends/, src/tlumacz/filter_engine/, src/tlumacz/qml_gui/
depends_on: [docs/STATUS.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: Änderung der aktiven Schichtgrenzen oder GUI/Backends
last_validation: "Code- und Dokumentationsprüfung durch SentinelX 04.10.2026; pytest 268 passed, compileall PASS, qmllint PASS"
---

# V4-Architektur

V4 ist eine unabhängige Implementierung. V3 ist weder Runtime-Abhängigkeit noch Importquelle.

## Schichten

- domain/ — Domänenverträge und Fehler.
- application/ — Use Cases, Orchestrierung und Lifecycle.
- backends/ — Adapter für Übersetzungsprovider.
- filter_engine/ — Filter-Registry, Sessions, Extraktion, Einheiten-/Markerprüfung und Schreiben.
- infrastructure/ — technische Integrationen.
- qml_gui/ — aktive QML-Präsentationsschicht und Application-Bridge.
- interfaces/ — Schnittstellen außerhalb der aktiven QML-GUI.
- resources/ — Runtime-Ressourcen wie Java Filter Host und Okapi.

## Aktive Backends

- llama — lokales llama.cpp;
- cloud — Router für Cloud-Provider;
- apertium — lokales Apertium-Backend;
- custom — Endpoint über denselben CloudRouter.

FastAPI, OpenVINO und die historische BackendManager-Orchestrierung sind zurückgezogen.

## Übersetzungsfluss

QML → QmlApplicationBridge → TranslationApp → Backendauswahl + DocumentTranslationService → DocumentProcessor → FilterRegistry/FilterSession → TranslationOrchestrator → Validatoren → Ausgabedokument.

Die GUI liefert Zustand und Aktionen. Die Übersetzungslogik bleibt in den Anwendungs- und Backend-Schichten.

## llama.cpp

TranslationApp verwaltet den optionalen LlamaCppRuntimeManager: Start, Stop, Neustart, Health-Check, Prozessbesitz, GGUF-Modell, Port, Rechenmodus, Parallelität und Chat-Template.

TranslateGemma ist ein spezieller llama.cpp-Chat-Template-Modus und kein eigenes Backend. In diesem Modus verwendet LlamaCppAdapter language_detector.py und Lingua nur für Quellsprachenerkennung und ISO-639-1-Normalisierung. Standard-llama.cpp verwendet Lingua nicht.

## Cloud und Apertium

CloudRouter verwendet CloudProviderRegistry und die aktiven Provider-Adapter. Mozhi ist ein eigener Cloud-Pfad.

Apertium besitzt eigenen Adapter, Runtime, Sprach-Discovery und ISO-Mapping. Es wird nicht über den llama.cpp-Lifecycle verwaltet. Die Verfügbarkeit konkreter Sprachpaare hängt von den installierten Runtime-Daten ab; eng-pol/cas_sp bleibt ein Release-Blocker.

## Aktive QML-GUI

Der aktive GUI-Einstiegspunkt ist src/tlumacz/qml_gui/app.py.

QmlApplicationBridge stellt Backendauswahl, Cloud/Mozhi-Profile, llama.cpp-Einstellungen, Ein-/Ausgabe, Zielsprache, Fortschritt, Logs, Vorschau, Glossar, Skills, Einstellungen/Reset, Theme/Sprache, Hilfe, Übersetzungsstart/-abbruch und llama.cpp-Neustart bereit.

BackendController ist der einzige erhaltene Controller aus dem früheren GUI-Controller-Satz. TranslationController, DocumentController, SettingsController, ProgressController und DiagnosticsController wurden nach Zero-Reference-Prüfung entfernt und gehören nicht mehr zur aktiven Runtime.

## Quellsprache

Die GUI kann source_language=auto verwenden. Nur TranslateGemma aktiviert den Lingua-basierten LanguageDetector. Cloud, Apertium und Standard-llama.cpp verwenden diesen Detektor nicht global.

## Dokumente

Die aktive FilterRegistry enthält DOCX, ODT, HTML/XHTML, Markdown, EPUB und XLIFF 2.0. TXT und PDF sind im Haupt-Pipeline von V4 nicht registriert.

## Lokalisierung

PL/EN/DE sind aktive Anwendungssprachen. Hilfe wird aus lokalisierten Markdown-Dateien geladen.

## Verknüpfte Dokumente

- docs/technical-docs/functional-capabilities.md — funktionale Implementierungsmatrix;
- docs/technical-docs/index.md — technische Dokumentationskarte;
- docs/RETIRED_FUNCTIONALITY.md — zurückgezogene Funktionen;
- docs/STATUS.md — aktueller Projektstatus.