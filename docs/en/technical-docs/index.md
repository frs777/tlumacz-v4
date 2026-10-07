---
id: technical-docs-index
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-01
owner: technical-documentation
source: src/tlumacz/
depends_on: [docs/AGENTS.md, docs/INDEX.md, docs/INDEX.yml, docs/STATUS.md]
expires_when: change to technical documentation structure
last_validation: "V3 → V4 documentation audit 2026-10-01"
---

# Tlumacz V4 — Technical Documentation

This is the map of the **current V4 implementation**. Historical, migration and archived documents are not sources of the current architecture.

## Sources of truth

- `docs/STATUS.md` — current project status.
- `docs/BUG.md` — active defects and risks.
- `docs/ARCHITECTURE.md` — current architecture model.
- `docs/RETIRED_FUNCTIONALITY.md` — functions and technologies retired from V4.
- `docs/INDEX.md` / `docs/INDEX.yml` — complete documentation inventory.
- `src/tlumacz/` — implementation.

## Active architecture

```text
Qt GUI / CLI
    ↓
application
    ↓
Document / Translation services
    ↓
Filter Engine + Translation backends
    ├── llama.cpp
    ├── Cloud
    └── Apertium
```

The Filter Engine supports custom Python filters and an isolated Java Filter Host for formats requiring Okapi.

## Active documentation areas

### GUI and user

- `user-guide.md`
- `help-content.md`
- `models.md`

### Backend and runtime

- `cloud-translation.md`
- `server-management.md`
- `apertium-backend-integration.md`
- `packaging-release.md`
- `xliff-pipeline.md`

### Architecture documents

- `docs/ARCHITECTURE.md`
- `docs/ARCHITEKTURA_FILTER_ENGINE_V4_PYTHON_OKAPI_BRIDGE_2026-09-26.md`
- `docs/ARCHITEKTURA_WLASNEGO_SILNIKA_FILTROW_V4_2026-09-26.md`

## Historical documents

Materials concerning FastAPI, OpenVINO, the old `BackendManager`, old TranslateGemma/FastAPI and other inactive paths must be treated as historical. The detailed register is in `docs/RETIRED_FUNCTIONALITY.md`.

Do not copy historical architecture into active instructions merely because it describes an earlier implementation.

## Synchronization rule

If a technical document contradicts V4 code, a test or `STATUS.md`, the current code and verified project state take precedence. Every test result must include a date and command.
