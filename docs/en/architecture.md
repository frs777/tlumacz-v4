---
id: architecture-v4-en
status: active
meta:
  contentType: Architecture
  category: governance
version: 0.40.0
updated: 2026-10-04
owner: platform-architecture
source: src/tlumacz/application/, src/tlumacz/backends/, src/tlumacz/filter_engine/, src/tlumacz/qml_gui/
depends_on: [docs/STATUS.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: change to active layer boundaries or GUI/backends
last_validation: "code and documentation inspection by SentinelX 2026-10-04; pytest 268 passed, compileall PASS, qmllint PASS"
---

# V4 Architecture

V4 is an independent implementation. V3 is neither a runtime dependency nor an import source.

## Layers

- domain/ — domain contracts and errors.
- application/ — use cases, orchestration and lifecycle.
- backends/ — translation-provider adapters.
- filter_engine/ — filter registry, sessions, extraction, unit/marker validation and writing.
- infrastructure/ — technical integrations.
- qml_gui/ — active QML presentation layer and application bridge.
- interfaces/ — interfaces other than the active QML GUI.
- resources/ — runtime resources such as the Java Filter Host and Okapi.

## Active backends

- llama — local llama.cpp;
- cloud — cloud provider router;
- apertium — local Apertium backend;
- custom — endpoint handled through the same CloudRouter.

FastAPI, OpenVINO and the historical BackendManager orchestration are retired.

## Translation flow

QML → QmlApplicationBridge → TranslationApp → backend selection + DocumentTranslationService → DocumentProcessor → FilterRegistry/FilterSession → TranslationOrchestrator → validators → output document.

The GUI supplies state and actions. Translation logic remains in the application and backend layers.

## llama.cpp

TranslationApp manages the optional LlamaCppRuntimeManager: start, stop, restart, health-check, process ownership, GGUF model, port, compute mode, parallelism and chat template.

TranslateGemma is a special llama.cpp chat-template mode, not a separate backend. In this mode LlamaCppAdapter uses language_detector.py and Lingua only for source-language detection and ISO 639-1 normalization. Standard llama.cpp does not use Lingua.

## Cloud and Apertium

CloudRouter uses CloudProviderRegistry and the active provider adapters. Mozhi is a separate Cloud provider path.

Apertium has its own adapter, runtime, language discovery and ISO mapping. It is not managed by the llama.cpp lifecycle. Concrete language-pair availability depends on installed runtime data; eng-pol/cas_sp remains a release blocker.

## Active QML GUI

The active GUI entry point is src/tlumacz/qml_gui/app.py.

QmlApplicationBridge exposes backend selection, Cloud/Mozhi profiles, llama.cpp settings, input/output, target language, progress, logs, preview, glossary, skills, settings/reset, theme/language, Help, translation start/cancel and llama.cpp restart.

BackendController is the only retained controller from the previous GUI-controller set. TranslationController, DocumentController, SettingsController, ProgressController and DiagnosticsController were removed after zero-reference verification and are not part of the active runtime.

## Source language

The GUI may use source_language=auto. Only TranslateGemma activates the Lingua-based LanguageDetector. Cloud, Apertium and standard llama.cpp do not use this detector globally.

## Documents

The active FilterRegistry contains DOCX, ODT, HTML/XHTML, Markdown, EPUB and XLIFF 2.0. TXT and PDF are not registered in the main V4 document pipeline.

## Localization

PL/EN/DE are active application locales. Help content is loaded from localized Markdown files.

## Related documents

- docs/technical-docs/functional-capabilities.md — functional implementation matrix;
- docs/technical-docs/index.md — technical documentation map;
- docs/RETIRED_FUNCTIONALITY.md — retired functionality;
- docs/STATUS.md — current project state.