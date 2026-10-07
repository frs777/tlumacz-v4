---
id: user-guide-v4
status: active
meta:
  contentType: Guide
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: project-documentation
source: src/tlumacz/qml_gui/, src/tlumacz/cli.py
depends_on: [docs/STATUS.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: change to active GUI/CLI surface
last_validation: "code and documentation inspection by SentinelX 2026-10-04; pytest 268 passed, compileall PASS, qmllint PASS"
---

## 2026-10-05 — current GUI contract

The active QML GUI has four tabs: Translation, API & Server, Switches, and Help. API & Server owns backend selection and backend-specific behavior settings. Switches contains glossary, skills, and LLM settings. The main Filter Engine supports DOCX, ODT, HTML/XHTML, Markdown, EPUB, and XLIFF. TXT and PDF are not registered in `build_filter_registry()`.

# User Guide — Tlumacz V4

## Active translation backends

- **llama.cpp** — local runtime.
- **Cloud** — cloud-service providers.
- **Apertium** — local backend through the Filter Engine.

## Basic flow

1. Start the current V4 from the correct environment.
2. Select a backend.
3. Select an input document in a supported format.
4. Set the source and target language and backend parameters.
5. Start translation.

The active document surface covers DOCX, ODT, HTML/XHTML, Markdown, EPUB and XLIFF according to the current FilterRegistry. TXT and PDF are not registered in the main V4 document pipeline.

For the TranslateGemma chat-template mode, the llama.cpp adapter uses the Lingua-based LanguageDetector and converts the detected source to ISO 639-1. Standard llama.cpp, Cloud and Apertium do not use this detector globally.

## Important

Do not start the application through historical environments pointing to `/home/frs/Projekty/agent-translator-v4` or through the global V3 package. The 2026-10-01 audit showed that such an environment can start version 0.31.2 instead of V4.

## Retired

FastAPI + Transformers and the old OpenVINO path with the TranslateGemma INT8 model are not active V4 paths. See `docs/RETIRED_FUNCTIONALITY.md`.
