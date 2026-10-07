---
id: historical-windows-exe-build
status: historical
meta:
  category: historical
  updated: 2026-10-01
  source: V3 research/build documentation
expires_when: replacement by current V4 documentation
---

# DOCUMENT STATUS: HISTORICAL / V3 RESEARCH

> This document is not a source of current V4 functionality. It describes historical research and V3 FastAPI/OpenVINO/TranslateGemma or build behavior. It is retained as reference material. For the current state, use `docs/STATUS.md`, `docs/technical-docs/index.md` and `docs/RETIRED_FUNCTIONALITY.md`.

# Tlumacz V3 — Windows EXE package build

## State as of 2026-09-10

Application version: **0.31.1**.
Repository: `frs777/tlumacz`, branch `main`.

The current Windows build is performed natively by GitHub Actions on `windows-latest`.
**PyInstaller 6.22.2** is used to package the Python/PySide6 application.
Python used in CI: **3.12**.

## Current workflow

File: `.github/workflows/build-windows.yml`

The workflow runs:
- manually through `workflow_dispatch`,
- automatically for `v*` tags.

Steps:
1. repository checkout,
2. Python 3.12 + pip cache,
3. installation of the project and test dependencies,
4. full `pytest` with `QT_QPA_PLATFORM=offscreen`,
5. PyInstaller using `build/windows/tlumacz.spec`,
6. EXE smoke test,
7. SHA256,
8. artifact upload to GitHub Actions.

CI test/build dependencies: `pyinstaller`, `pytest`, `fastapi`, `uvicorn`.
FastAPI and Uvicorn are installed for tests but are not packaged into the base EXE.

## PyInstaller file

File: `build/windows/tlumacz.spec`

Application entry point: `tlumacz/qt_gui/app.py`.
The EXE includes Qt resources (`*.qss`, `*.svg`) and built-in Markdown skills from `tlumacz.skills`.

The base build excludes optional backends:
- `fastapi`, `uvicorn`,
- `transformers`, `torch`, `accelerate`, `safetensors`,
- `openvino`, `openvino_genai`.

The EXE runs as a GUI application without a console (`console=False`).

## Last verified build

The workflow completed successfully:
`https://github.com/frs777/tlumacz/actions/runs/34456326653`

File: `Tlumacz-0.31.1-windows-x86_64.exe`
Size: 48 906 171 B (~46.6 MiB)
SHA256: `ca0334bbee4eb8ddc0961e977fc8adff12dfd1a04c911dac421a6c6b718ccca3`

Release:
`v0.31.1`

The EXE was added as a GitHub release asset.

## Important limitation of the current EXE

The current package is a **base Windows build**, not a complete runtime for all backends.
Optional AI components are not bundled.

The distribution architecture should ultimately be changed according to the decision from 2026-09-10.

## Target Windows distribution concept

The application is based on local translation. Therefore **llama-server should be part of the base Windows installation**, not an optional add-on.

The model should not be embedded in the EXE. The user should be able to select a llama.cpp-compatible model, such as TranslateGemma 4B/12B, Qwen or another suitable model.

Do not simplify the GUI to a single `C:\AI\Models\model.gguf` field. Preserve the existing `model_profiles` mechanism and extend it to support model selection/profiling.

Proposed component split:
1. Tlumacz GUI + llama-server — always.
2. Core document libraries and core — always.
3. FastAPI + Uvicorn — optional.
4. Transformers + PyTorch — optional.
5. OpenVINO — optional.
6. User translation skills — optional, synchronized with the GitHub repository.
7. Glossary/dictionaries — optional, synchronized with the GitHub repository.
8. Models — downloaded separately by the user, outside the installer.

Preferred target Windows product: `Tlumacz-Setup.exe` installer with checkboxes for optional components plus a separate portable/base EXE.

Optional Python dependencies should be installed into the application's private runtime/venv so that the system Python does not need to be modified.

The installer should clearly state that models are not part of the installer and must be selected for the user's hardware.

## EXE build skill

A full copy of the skill used is located next to this document:
`docs/technical-docs/windows-compiler-skill.md`

Skill source:
`SKILL.md` used during the historical Windows build process

Key rules:
- prefer a native build on `windows-latest`,
- use PyInstaller for Python applications,
- use `--windowed` / `console=False` for GUI applications,
- use a `.spec` file for more complex bundling,
- explicitly add data, resources and hidden imports,
- exclude unnecessary modules to reduce size,
- test the application before the build,
- smoke-test the resulting EXE,
- publish artifacts with `actions/upload-artifact`,
- use Git tags for releases,
- consider code signing for final distribution,
- an installer can be built with NSIS, Inno Setup or WiX.

## Next stage after reviewing the GUI

After GUI screenshots are provided, first compare the current interface with the concept above.
Then inspect the `model_profiles` implementation, server configuration and existing settings fields.
Only then design installer, model-selection and optional-component changes.

Do not change the GUI or model mechanism blindly.
