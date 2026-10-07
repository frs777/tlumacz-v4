---
id: todo-v4-en
status: active
meta:
  contentType: TaskList
  category: governance
version: 0.40.0
updated: 2026-10-04
owner: project-documentation
source: src/tlumacz/
depends_on: [docs/STATUS.md]
expires_when: closure of current release-candidate tasks
last_validation: "code and documentation inspection by SentinelX 2026-10-04"
---

# TODO V4

## Phase 13 — FINAL HANDOFF AND FREEZE — CLOSED
- [x] migration state documented;
- [x] current artifact and SHA-256 recorded;
- [x] F11/F12 blockers explicitly recorded;
- [x] no publication to GitHub;
- [x] documentation backup;
- [x] handoff report.

Final release 0.40.0 remains open because of Apertium eng-pol, Windows, and dependency/licensing work.

# TODO V4

## Next stage

### Phase 12 — release 0.40.0 — RELEASE CANDIDATE, OPEN

- [x] full suite — 182 passed;
- [x] compile;
- [x] static analysis — Ruff + mypy;
- [x] contract suite;
- [x] integration/E2E — 19 passed;
- [ ] Windows;
- [ ] packaging — dependent on Phase 11 closure;
- [x] documentation;
- [x] CHANGELOG;
- [x] migration notes;
- [x] clean Linux install;
- [x] rollback procedure.

Artifact: `temp/wheel/tlumacz-0.40.0-py3-none-any.whl`. SHA-256: `161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835`.

The glossary remains outside the blocking scope: it is a separate resource and is not compiled into the artifact.

### Phase 11 — packaging — OPEN, PARTIALLY COMPLETED

- [ ] dependency closure;
- [ ] licenses;
- [x] NOTICE;
- [x] Java runtime;
- [x] Okapi;
- [ ] Apertium — complete `eng-pol.t1x.bin` is missing;
- [x] Python package — wheel 0.40.0 built;
- [x] Linux — clean install and smoke PASS;
- [ ] Windows — native Windows runtime missing;
- [x] clean environment — verified on clean venv;
- [x] artifact smoke test — PASS for Python/Java/Apertium engine;
- [x] clean install — Linux PASS;
- [x] rollback procedure.

State: Phase 11 remains open because of Apertium, Windows, dependency closure and the full license audit.

- [x] no FastAPI;
- [x] no OpenVINO;
- [x] no configuration for them;
- [x] no tests for them;
- [x] no imports;
- [x] no dependencies;
- [x] no feature flags;
- [x] no replaced document paths.

### Phase 9 — GUI — CLOSED / post-cleanup state
- [x] BackendController — active backend-selection controller;
- [x] removal of unused TranslationController, SettingsController, DocumentController, ProgressController and DiagnosticsController;
- [x] removal of their private dependencies and TranslationApp instances;
- [x] GUI-layer contract tests.

### Phase 8 — Translator — CLOSED
- [x] ChunkPlanner;
- [x] PromptBuilder;
- [x] TranslationExecutor;
- [x] TranslationCache;
- [x] ResultValidator;
- [x] TranslationOrchestrator;
- [x] DocumentTranslationService.

### Phase 7 — Document Services — CLOSED
- [x] DOCX;
- [x] ODT;
- [x] HTML/XHTML;
- [x] Markdown;
- [x] EPUB;
- [x] XLIFF;
- [x] other formats only when need is demonstrated.

### Closed
- Phase 0 — baseline;
- Phase 1 — bootstrap;
- Phase 2 — contracts;
- Phase 3 — Filter Engine;
- Phase 4 — LlamaCppBackend;
- Phase 5 — Cloud;
- Phase 6 — Apertium.

Remaining phases follow `docs/archive/migration/PLAN_MIGRACJI-v4.md`.

## Audit 2026-10-01 — update

- [x] documentation audit;
- [x] code audit;
- [x] current pytest — 182 passed;
- [x] Ruff — PASS;
- [x] mypy — PASS;
- [x] compileall — PASS;
- [x] CLI in a fresh wheel environment — PASS;
- [ ] Apertium eng-pol — blocked by `cas_sp`;
- [ ] dependency closure/licensing;
- [ ] final release verification.

## GUI/Cloud — 2026-10-01

- [x] V3/V4 GUI comparison;
- [x] V3/V4 Cloud comparison;
- [x] reference screenshot analysis;
- [x] backup before major change;
- [x] Qt GUI restoration;
- [x] active Cloud provider restoration;
- [x] Cloud profile restoration;
- [x] Mozhi GUI;
- [x] FastAPI/OpenVINO removal from active GUI;
- [x] offscreen GUI tests;
- [x] full suite 195 passed;
- [x] Ruff;
- [x] mypy;
- [x] compileall;
- [ ] Apertium eng-pol / cas_sp;
- [ ] dependency closure/licensing;
- [ ] Windows;
- [ ] final release verification.

## UI surface completion — 2026-10-01

- [x] V3/V4 objectName comparison;
- [x] active Translation/API/Extras/Help surface;
- [x] UI glossary;
- [x] skills management UI;
- [x] PL/EN Help and About dialog;
- [x] output splitter, elapsed/spinner;
- [x] GUI surface parity test.

Current full suite: 196 passed.

## GUI/Cloud requirements correction — 2026-10-01

- [ ] add a **Custom** category for external API endpoints and expose editable address configuration after selection;
- [ ] verify behavior of the special **TranslateGemma** template for language codes;
- [x] retire SimplyTranslate from active V4;
- [ ] confirm DLX availability in the actually running GUI;
- [ ] confirm Apertium availability in the actually running GUI.

## Schedule — state after P0 launcher — 2026-10-01

- [x] P0: separate V4 startup from global V3 for `python -m tlumacz...` from the project directory;
- [x] P0: bootstrap test without `PYTHONPATH`;
- [x] P0: full offscreen regression — 201 passed;
- [ ] P1: further `MainWindow` decomposition;
- [ ] P1: persistence of `last_input_path`, `last_output_path`, `server_gguf_path`;
- [ ] P1: parity functions for Custom, DLX, Apertium and TranslateGemma;
- [ ] P2: cleanup of V3-related relics and tests.

## Verification update — 2026-10-01

- [x] P1: extracted backend selection, settings, documents, progress and worker from `MainWindow`;
- [x] P1: persistence of `last_input_path`, `last_output_path`, `server_gguf_path`;
- [x] GUI offscreen regression — 205 passed;
- [ ] further extraction of GUI tab construction;
- [ ] diagnostics integration into GUI flow.

## 2026-10-01 — P1 — state after GUI decomposition

- [x] extract Translation tab construction;
- [x] extract API and server tab construction;
- [x] extract Extras tab construction;
- [x] extract Help tab construction;
- [x] preserve Qt object names required by parity tests;
- [x] update parity test for the new module boundary;
- [x] full regression — 206 tests;
- [x] Ruff;
- [x] compileall;
- [x] backup before major change.

### Next steps

- [ ] audit parity functions: Custom, DLX, Apertium in the actual GUI surface and TranslateGemma;
- [ ] execute full TranslateGemma E2E through the real application and GGUF model;
- [ ] verify round-trip of all `AppSettings` against the current QML integration;
- [ ] remove `*.bak.*` backup relics only after a separate audit and while preserving required history.
