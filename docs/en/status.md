---
id: status-v4-en
status: active
meta:
  contentType: Status
  category: governance
version: 0.40.0
updated: 2026-10-04
owner: project-documentation
source: src/tlumacz/
depends_on: [docs/STATUS.md]
expires_when: change to current project state
last_validation: "code and documentation inspection by SentinelX 2026-10-04"
---

## 2026-10-04 — documentation synchronized with current code

The current code/documentation correlation confirms `TranslationApp.restart_llama()`, the isolated TranslateGemma/Lingua path, Cloud SecretStore migration for legacy API keys, and removal of unused GUI controllers. `BackendController` remains active. Verification: **268 passed**, compileall PASS, qmllint PASS.

# V4 STATUS

## 2026-09-30

### Migration status

- Phase 0 — baseline: CLOSED.
- Phase 1 — V4 bootstrap: CLOSED.
- Phase 2 — contracts: CLOSED.
- Phase 3 — Filter Engine: implemented components and filters; the full phase criterion remains subject to separate DOCX round-trip verification.
- Phase 4 — LlamaCppBackend: CLOSED.
- Phase 5 — Cloud: CLOSED.
- Phase 6 — Apertium: CLOSED according to the verification completed so far for adapter/backend/runtime/language plugins.
- Phase 7 — Document Services: CLOSED; DOCX, ODT, HTML/XHTML, Markdown, EPUB and XLIFF are verified.
- Phase 8 — Translator: CLOSED; ChunkPlanner, PromptBuilder, TranslationExecutor, TranslationCache, ResultValidator, TranslationOrchestrator and DocumentTranslationService are verified.
- Phase 9 — GUI: CLOSED; application controllers and contract tests are verified.
- Phase 10 — legacy removal: CLOSED after the zero-reference audit.

### Phase 10 verification — legacy removal

The V4 audit found:
- no references to `fastapi`, `FastAPIServerManager`, `fastapi_server`, `openvino`, `openvino_backend` or `TranslateGemma INT8` in active code and tests;
- no FastAPI/OpenVINO files in `src/`, `tests/` or active technical documentation;
- none of these dependencies in `pyproject.toml`;
- no configuration for these technologies in V4 configuration files;
- no feature flags referring to these technologies;
- no replaced document-processing paths pointing to them.

Remaining FastAPI/OpenVINO names occur in migration documentation and the V3 baseline as descriptions of the source and migration decisions; they are not active runtime references.

Verification:
- zero-reference scan of active code/tests/configuration — PASS;
- Phase 9/10/11 plan structure — PASS;
- full pytest — 180 passed;
- Ruff — PASS;
- mypy — PASS, 60 source files.

### Next stage

Phase 11 — packaging.

### Phase 11 — packaging — started, BLOCKED

Dependency-closure audit and a backup were performed before changes:
- backup: `.migration-backups/pre-packaging-phase11-20260930.tar.gz`;
- controlled Okapi runtime was copied from V3 into V4 at `filtry/runtime` (42 files, 22 MiB);
- the previously declared `filtry/runtime` was missing, so the Java launcher had no complete runtime;
- building a wheel in the checkout is blocked by parent repository ownership (`setuptools`/Git reports `dubious ownership`);
- building Apertium data from the working copy failed with a permissions error while cleaning staging in `/tmp`; the stage was stopped;
- V3 was not intentionally modified.

**The Phase 11 criterion is not satisfied.** No packaging item was marked complete without full verification.

### Phase 11 — packaging — partially completed, still OPEN

After retrying with staging under `./temp`:
- `tlumacz-0.40.0-py3-none-any.whl` was built (~43 MiB);
- the wheel contains Okapi runtime, Java Filter Host, private Apertium runtime and NOTICE/licenses;
- clean install from wheel: PASS;
- `tlumacz --version`: `0.40.0`;
- Java Filter Host from installed wheel resources: PASS;
- Apertium engine 3.9.12 from installed wheel resources: PASS;
- full pytest: 182 passed;
- Ruff: PASS;
- mypy: PASS, 60 files.

Remaining blockers:
- missing complete `eng-pol.t1x.bin`; rebuilding from V3 fails with `Undefined attr-item cas_sp`;
- missing Windows Apertium runtime and other native resources — the current artifact is Linux x86-64;
- complete dependency closure and component-by-component license audit require further verification.

The Phase 11 criterion remains **NOT SATISFIED**.

### Phase 12 — release 0.40.0 — RELEASE CANDIDATE

Verified:
- full pytest: **182 passed**;
- compileall: **PASS**;
- Ruff: **PASS**;
- mypy: **PASS**, 60 files;
- integration/E2E: **19 passed**;
- clean Linux install from wheel without dependencies: **PASS**;
- artifact version: **0.40.0**;
- Java Filter Host from wheel: **PASS**;
- Apertium engine 3.9.12 starts from the wheel.

Artifact: `temp/wheel/tlumacz-0.40.0-py3-none-any.whl`

SHA-256: `161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835`

Phase 12 documentation:
- `docs/release/RELEASE_NOTES_0.40.0.md`;
- `docs/archive/migration/MIGRATION_NOTES_V3_TO_V4.md`;
- `docs/release/ROLLBACK_0.40.0.md`;
- `docs/reports/FAZA_12_RELEASE_2026-09-30.md`.

Phase 12 is not closed. Windows and Phase 11 packaging/dependency/licensing blockers remain.

The glossary is not a blocker: it remains a separate resource and can be added later.

### Phase 13 — final handoff and freeze

Phase 13 was closed as a local handoff freeze. The current Release Candidate 0.40.0 state, artifact, SHA-256, documentation backup and blockers remaining from Phases 11/12 were documented. No push to GitHub is performed.

Report: `docs/reports/FAZA_13_FINAL_HANDOFF_2026-09-30.md`.

Final release 0.40.0 remains open because of Apertium eng-pol, Windows and dependency/licensing work.

## Official V4 project directory and temporary-file cleanup — 2026-10-01

The official V4 project directory is now:

`/home/frs/Projekty/tlumacz-v4/`

The former directory `/home/frs/Projekty/agent-translator-v4/` is no longer treated as the current project directory.

A full recursive pass was performed in the new directory. Before cleanup, 513 files matching `*.bak*` were found, totaling about 2.9 MiB.

Only those `*.bak*` files were removed. No project directories, documentation, code, tests or other temporary files with different names were removed.

After cleanup:
- remaining `*.bak*` files: 0;
- directories in the project tree: 970;
- remaining regular files: 6449.

Cleanup also covered archive and report subdirectories. Nothing was removed from the old `/home/frs/Projekty/agent-translator-v4/` directory.

Note: `/home/frs/Projekty/tlumacz-v4/` currently has no `.git` directory. Git repository state was not changed by this operation.

## Engineering audit and quality repair — 2026-10-01

After identifying the correct project directory, a full review of documentation, code, tests, static analysis and packaging was performed.

### Current verification results
- pytest: **182 passed**;
- Ruff: **PASS**;
- mypy: **PASS**, 60 files;
- compileall: **PASS**;
- `PYTHONPATH=src python3 -m tlumacz --version`: **PASS**, 0.40.0;
- fresh venv from wheel: `python -m tlumacz --version` **PASS**;
- fresh venv from wheel: `tlumacz --version` **PASS**;
- Apertium runtime/E2E: **6 passed**;
- building `eng-pol.t1x.bin`: **BLOCKED** by `Undefined attr-item cas_sp`.

### Fixed
- import ordering in `processor.py` and `test_docx_filter.py`;
- Ruff no longer analyzes regenerable `temp/` staging or migration backups;
- active migration documents now point to `/home/frs/Projekty/tlumacz-v4/`.

### CLI
The system-interpreter error was caused by importing the global V3 package `/usr/lib/python3.14/site-packages/tlumacz`. Existing old environments had shebangs pointing to historical `/home/frs/Projekty/agent-translator-v4`. A fresh venv from the current wheel works correctly.

### Apertium
No unverified `cas_sp` fix was introduced. The local transfer file and the upstream apertium-eng-pol version use `cas_sp` without declaring the attribute; the current compiler rejects the file. The blocker remains part of Phase 11.

## GUI/Cloud V3 → V4 regression — audit and repair — 2026-10-01

A regression in the GUI/Cloud migration was found and fixed. V4 previously lacked a Qt layer and most V3 Cloud providers.

### State after repair
- V4 Qt GUI: RESTORED as an adapter over the application layer;
- active GUI backends: llama.cpp, Apertium, Cloud;
- FastAPI/OpenVINO: NOT RESTORED;
- Cloud providers: 8 adapters;
- Cloud profiles: 12;
- Mozhi GUI: RESTORED;
- offscreen GUI test: 3 passed;
- V3 provider compatibility test: 21 passed;
- full suite: 195 passed;
- Ruff: PASS;
- mypy: PASS — 68 files;
- compileall: PASS;
- wheel 0.40.0: BUILD PASS.

Regression report: `docs/Audyt/AUDYT_REGRESJI_GUI_CLOUD_V3_V4_2026-10-01.md`.
Repair report: `docs/Audyt/RAPORT_NAPRAWY_GUI_CLOUD_2026-10-01.md`.
Plan: `docs/archive/plans/PLAN_NAPRAWCZY_GUI_CLOUD_2026-10-01.md`.
Backup: `.migration-backups/pre-gui-cloud-repair-20261001.tar.gz`.

## UI surface completion — 2026-10-01

A comparison of V3/V4 objectNames confirmed missing elements in the Extras/Help tabs. The active UI surface was restored, excluding FastAPI/OpenVINO elements. Surface test: 1 passed; GUI tests together: 4 passed.

Final verification for this stage: **196 passed**, Ruff PASS, mypy PASS (68 files), compileall PASS, wheel PASS.

## 2026-10-01 — report: llama.cpp server does not start

- **Status:** reported, cause unknown.
- **Component:** llama.cpp server/runtime.
- **Symptom:** the llama.cpp server does not start.
- **Classification:** functional defect requiring reproduction and diagnosis.
- **Priority:** P1 — blocks the local llama.cpp backend.
- **Cause:** not yet determined; no assumption is made at this stage about configuration, model, process parameters or environment.
- **Next step:** collect the exact startup message/log and determine which executable, model and configuration are actually used.

## Documentation cleanup after migration — 2026-10-01

The first structured documentation cleanup wave after the V3 → V4 migration was completed.

- V3 was treated as a historical source; its documents were neither moved nor deleted.
- A complete registry of all files under docs/ was created: docs/INDEX.yml and docs/INDEX.md.
- docs/DOCUMENTATION_CHANGELOG.md was created as the documentation change log.
- docs/RETIRED_FUNCTIONALITY.md was created as the unambiguous registry of retired functions.
- FastAPI + Transformers and the old OpenVINO path with TranslateGemma INT8 are marked RETIRED.
- The old V3 BackendManager/MainWindow model is not treated as active V4 architecture.
- The technical documentation index and model/runtime documentation were updated.
- The outdated V3 BUG.md was replaced by a list of current V4 risks and blockers.
- Historical Windows documents and reports containing old paths received explicit historical markings.
- No functionality removal, software installation or physical migration of the complete documentation set was performed.

### Current maintenance rule

After every documentation change, refresh INDEX.yml and add an entry to DOCUMENTATION_CHANGELOG.md. Before changing a document's status, check the code, tests and latest audit.

## 2026-10-01 — GUI: incorrect tabs / backends

An incorrect tab layout and missing modern backend were reported while two older backends were still present. The working V3.2 GUI is the UX reference; V4 backends remain llama.cpp, Apertium and Cloud. First determine which GUI code is actually running.

## Update 2026-10-01 — GUI/Cloud matrix correction

- SimplyTranslate was removed from active V4 after the decision to retire the integration because no effective connection was available.
- DLX remains a required Cloud provider.
- A custom endpoint remains a functional-parity requirement: the target selector should have a **Custom** category, with editable address configuration after selection.
- TranslateGemma should be treated as a special feature/template for language codes, not as automatic llama.cpp startup.

## 2026-10-01 — MainWindow core refactor started

The extraction of responsibilities from the Qt layer into the application layer was started.

- BackendService was added as a facade over active V4 backends;
- TranslationApp was added as the application core without Qt dependency;
- llama.cpp runtime was moved from direct MainWindow handling to TranslationApp;
- qt_gui/app.py is now the composition root and passes the core to MainWindow;
- MainWindow no longer directly imports BackendRegistry, BackendSelection or LlamaCppRuntimeManager;
- full pytest: **199 passed**;
- Ruff: **PASS**;
- compileall: **PASS**.

Further extraction of settings, documents, diagnostics, progress and remaining GUI logic is still required. BUG-007 remains open until this refactor is completed.

## P0 — V4 launcher — closed for source execution

On 2026-10-01, the V3/V4 runtime conflict when launching from `/home/frs/Projekty/tlumacz-v4` was fixed.

- local symlink `tlumacz -> src/tlumacz` was added so `python -m tlumacz...` from the project directory resolves V4 without `PYTHONPATH=src`;
- global V3 package `0.31.2` was neither changed nor removed;
- bootstrap regression without `PYTHONPATH` was added;
- `python -m tlumacz --version` returns `0.40.0`;
- import `tlumacz.qt_gui.app` points to V4;
- full suite with `QT_QPA_PLATFORM=offscreen`: **201 passed**;
- Ruff: **PASS**;
- compileall: **PASS**.

Wheel builds still have an independent blocker caused by parent Git tree ownership (`/home/frs/Projekty`); it was not resolved by changing global `safe.directory`.

## 2026-10-01 — P1 — GUI decomposition and configuration persistence — progress

In the next refactoring step, responsibilities were separated from `MainWindow`:
- `BackendPresenter` — backend selection, visibility configuration and selection building;
- `SettingsPresenter` — GUI settings mapping and configuration persistence;
- `DocumentPresenter` — document path selection and validation;
- `ProgressPresenter` — progress-state mapping to Qt;
- `TranslationWorker` — document translation execution in a `QObject` worker.

`MainWindow` was reduced from 819 to **579 lines**.

Persistence of `last_input_path` and `last_output_path` was added; `server_gguf_path` retains round-trip behavior. GUI tests cover persistence of these three paths.

Verification: **205 passed**, Ruff PASS, compileall PASS.

Further decomposition of GUI tab builders and integration of diagnostics remain.

## 2026-10-01 — P1 — GUI view builders

- construction of four tabs was extracted from `MainWindow` to `qt_gui/view_builders.py`;
- `MainWindow` was reduced from 579 to **253 lines**;
- the existing control and Qt callback surface was preserved;
- the GUI parity test was updated to account for `main_window.py` and `view_builders.py`, without changing the required control list;
- a view-builder contract test was added;
- full regression: **206 passed**;
- Ruff: **PASS**;
- compileall: **PASS**;
- backup before the change: `/home/frs/Projekty/agent-translator-v3/backups/tlumacz-v4-tab-builders-20261001/pre-tab-builders.tar.gz`.

Historical controller plan closed by the 2026-10-04 cleanup: `DiagnosticsController` and the other unused GUI controllers were removed after zero-reference verification. Remaining work is limited to the documented parity audit and TranslateGemma E2E.
