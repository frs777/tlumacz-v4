# CHANGELOG V4

## 2026-10-01 — P1 — MainWindow decomposition and path persistence

- extracted `BackendPresenter`, `SettingsPresenter`, `DocumentPresenter`, `ProgressPresenter` and `TranslationWorker`;
- reduced `MainWindow` from 819 to 579 lines;
- `TranslationApp` now owns backend, settings, document, progress and diagnostics controllers;
- added `last_input_path` and `last_output_path` to `AppSettings`;
- confirmed round-trip persistence of input, output and GGUF paths;
- full suite: 205 passed; Ruff and compileall: PASS.

## 2026-10-01 — P0 V4 launcher

- removed ambiguity when running V4 from source through the repository shim `tlumacz -> src/tlumacz`;
- `python -m tlumacz --version` from the project directory resolves V4 `0.40.0` without `PYTHONPATH`;
- added V3/V4 bootstrap regression tests;
- confirmed full suite: 201 passed, Ruff PASS, compileall PASS;
- the global V3 package `0.31.2` was not modified.

## 2026-10-01 — Final V3 → V4 migration report

- added `docs/Raport_koncowy_migracji_v3-v4.md`;
- summarized phases 0–13, successes, encountered problems and resolved blockers;
- documented remaining final-release blockers: Apertium `eng-pol`, Windows runtime, dependency closure and license audit;
- confirmed local handoff freeze and Linux Release Candidate 0.40.0;
- confirmed V3 remains untouched as the reference source and no GitHub publication was performed.

## 2026-09-30 — Phase 13 — final handoff and freeze

- closed the local handoff freeze for the current Release Candidate 0.40.0;
- documented the artifact, SHA-256, F11/F12 blockers and follow-up procedure;
- backed up documentation before changes;
- performed no GitHub push or artifact publication;
- final release 0.40.0 remains open because of Apertium `eng-pol`, Windows and licensing/dependency work.

## 2026-09-30 — Phase 12 — release 0.40.0 — release candidate

- prepared the Linux release candidate for version 0.40.0;
- full suite: 182 passed;
- compileall, Ruff and mypy: PASS;
- integration/E2E: 19 passed;
- clean wheel installation without dependencies: PASS;
- added `RELEASE_NOTES_0.40.0.md`, `MIGRATION_NOTES_V3_TO_V4.md` and `ROLLBACK_0.40.0.md`;
- artifact SHA-256: `161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835`;
- Phase 12 remains open because of Windows and Phase 11 packaging blockers;
- the separate glossary is not a blocker and is not part of the bundled artifact.

## 2026-09-30 — Phase 11 — packaging resumed

- staging was moved to local `./temp`, without writing outside the V4 tree;
- added Okapi resources and Java Filter Host to the Python package;
- added bundled Apertium runtime to the wheel and verified engine 3.9.12;
- added `LICENSE`, `NOTICE` and license texts to the distribution;
- built and verified wheel `tlumacz-0.40.0-py3-none-any.whl` in a clean venv;
- Java Filter Host from the wheel passed smoke testing;
- full suite: 182 passed, Ruff PASS, mypy PASS;
- Phase 11 remains open: incomplete `eng-pol.t1x.bin`, missing Windows runtime and incomplete dependency/license audit.

## 2026-09-30 — Phase 11 — packaging start

- started dependency closure for the V4 artifact;
- performed backup before changes: `.migration-backups/pre-packaging-phase11-20260930.tar.gz`;
- added controlled Okapi runtime from V3 (`filtry/runtime`, 42 files, 22 MiB);
- detected wheel-build blocking by `setuptools`/Git and parent repository ownership;
- detected an additional Apertium data-build blocker in `/tmp` caused by permissions;
- Phase 11 remains open and blocked; its completion criterion was not marked satisfied.

## 2026-09-30 — Phase 10

- closed Phase 10 — legacy removal after the zero-reference audit;
- confirmed no FastAPI/OpenVINO in active V4 code, tests or configuration;
- removed inconsistencies in phase 9–10 documentation;
- updated STATUS and TODO;
- verification: 180 tests, Ruff and mypy — PASS.

# Earlier V4 milestones

## Phase 4 — LlamaCppBackend

- added the llama.cpp OpenAI-compatible adapter;
- added the `/v1/models` health-check endpoint;
- full V4 suite: 61 passed;
- added runtime manager and process-ownership validation;
- added explicit startup/shutdown timeouts and readiness probe;
- closed health-check, contract suite and E2E;
- real llama-server plus Jan-v3.5-4B-Q4_K_XL passed smoke translation;
- full V4 suite: 77 passed;
- completed cancellation through V4 CancellationToken.

## Phase 5 — Cloud

- added CloudRouter and CloudRoute;
- added runtime-checkable CloudProvider;
- added V3 → V4 cloud-profile migration without moving API keys;
- added MozhiProvider and automatic instance selection;
- added and enforced HTTP request timeouts;
- closed error classification, secret isolation and contract tests.

## Phase 6 — Apertium

- added private Apertium 3.9.12 runtime and discovery without system installation;
- completed Apertium adapter against the TranslationBackend contract.

## Phase 3 — Filter Engine

- added isolated Java Filter Host;
- added versioned JSON Lines client;
- added DOCX/OpenXML filter;
- added DOCX round-trip through the Filter Engine;
- closed all Phase 3 items;
- full V4 suite: 58 passed.

## 2026-10-01 — Engineering audit and quality repair

- added documentation audit: `docs/Audyt/AUDYT_DOKUMENTACJI_2026-10-01.md`;
- added code audit: `docs/Audyt/AUDYT_KODU_2026-10-01.md`;
- added remediation plan: `docs/Plany/PLAN_NAPRAWCZY_AUDYT_2026-10-01.md`;
- added current verification report: `docs/Testy/AUDYT_TESTY_2026-10-01.md`;
- performed backup: `.migration-backups/pre-audit-repair-20261001.tar.gz`;
- fixed Ruff issues;
- excluded regenerable artifacts from Ruff;
- unified active V4 paths;
- verified CLI in a fresh wheel environment;
- confirmed the Apertium `eng-pol` blocker caused by `cas_sp`.

## 2026-10-01 — V3 → V4 GUI/Cloud regression repair

- found that V4 lacked an actual Qt layer despite having GUI controllers;
- found loss of most V3 Cloud providers;
- found incomplete configuration of 12 Cloud profiles;
- performed backup: `.migration-backups/pre-gui-cloud-repair-20261001.tar.gz`;
- restored the Qt GUI as a V4 adapter;
- restored active GUI backends: llama.cpp, Apertium and Cloud;
- restored Cloud providers: OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate, SimplyTranslate, Mozhi and DLX;
- restored 12 Cloud profiles;
- restored Mozhi/SimplyTranslate fields;
- kept FastAPI/OpenVINO retired;
- added GUI regression and Cloud compatibility tests;
- full suite: 195 passed;
- Ruff: PASS;
- mypy: PASS;
- wheel 0.40.0 built successfully.

Regression report: `docs/Audyt/AUDYT_REGRESJI_GUI_CLOUD_V3_V4_2026-10-01.md`.
Repair report: `docs/Audyt/RAPORT_NAPRAWY_GUI_CLOUD_2026-10-01.md`.

## 2026-10-01 — UI surface completion

- compared the complete V3/V4 objectName set;
- restored active Extras/Help elements;
- added glossary, skills management, Help language, About dialog and output splitter;
- added `tests/test_gui_surface_parity.py`;
- final suite for this stage: **196 passed**;
- Ruff, mypy, compileall and wheel: PASS.

## 2026-10-01 — llama.cpp server report

- **Status:** reported, cause unknown.
- **Component:** llama.cpp server/runtime.
- **Symptom:** the llama.cpp server does not start.
- **Classification:** functional defect requiring reproduction and diagnosis.
- **Priority:** P1 — blocks the local llama.cpp backend.
- **Cause:** not yet determined; no assumption is made about configuration, model, process parameters or environment.
- **Next step:** collect the exact startup message/log and identify the actual executable, model and configuration.

## 2026-10-01 — GUI/Cloud matrix correction

- SimplyTranslate was retired from active V4 because an effective connection could not be established;
- DLX remains a required Cloud provider;
- a **Custom** category with editable external API address remains a functional-parity requirement;
- TranslateGemma is a special language-code feature/template, not automatic llama.cpp startup.

## 2026-10-01 — GUI application core extraction

- added BackendService as a facade over active backends;
- added TranslationApp as the application core without Qt dependency;
- moved llama.cpp runtime handling from MainWindow into TranslationApp;
- changed qt_gui/app.py to the composition root;
- MainWindow no longer directly imports backend registry/selection or LlamaCppRuntimeManager;
- full suite: **199 passed**;
- Ruff: PASS;
- compileall: PASS.

## 2026-10-01 — P1 — GUI view builders

- extracted four tab builders into `src/tlumacz/qt_gui/view_builders.py`;
- reduced MainWindow from 579 to 253 lines without changing the GUI surface contract;
- adjusted the parity test to the new module boundary;
- added `test_gui_view_builders.py`;
- full suite: **206 passed**; Ruff and compileall: PASS;
- backup: `/home/frs/Projekty/agent-translator-v3/backups/tlumacz-v4-tab-builders-20261001/pre-tab-builders.tar.gz`.


## 2026-10-03 — QML GUI and help localization

- completed localization of the active QML surface in PL/EN/DE;
- localized file dialogs, backend labels, glossary, settings and runtime messages;
- synchronized PL/EN/DE user help;
- added docs/I18N_STATUS.md as the translation-status register;
- full regression: 272 passed, compileall PASS, QML offscreen smoke ended with controlled code 124.
