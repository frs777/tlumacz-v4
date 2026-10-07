---
id: server-management-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: runtime-maintenance
source: src/tlumacz/qml_gui/, src/tlumacz/backends/llama_cpp/
depends_on: [docs/ARCHITECTURE.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: change to llama.cpp lifecycle
last_validation: "inspekcja dokumentacji SentinelX 2026-10-04"
---

## 2026-10-05 — current llama.cpp lifecycle

`TranslationApp` manages an optional `LlamaCppRuntimeManager` with start, stop, and restart. Restart preserves the current model path, port, compute mode, parallelism, and chat template. Cloud and Apertium do not use the llama.cpp lifecycle.

# Runtime Management — Tlumacz V4

## Scope

The current local runtime is **llama.cpp / llama-server**. Cloud does not require a local process. Apertium has its own runtime and lifecycle, documented in the Apertium documentation.

## Active architecture

```text
Qt GUI / application
    ↓
LlamaCpp backend
    ↓
runtime manager
    ↓
llama-server
```

Implementation details should be read in `src/tlumacz/backends/llama_cpp/` and the current GUI code.

## Retired runtimes

FastAPI/Transformers and the old OpenVINO path with TranslateGemma INT8 are not started by V4. Do not restore their entries to the active backend selector or document them as required runtime components.

## Diagnostic rule

If program behavior points to FastAPI, OpenVINO or other V3 elements, first check the interpreter, `tlumacz.__file__`, runtime environment and launcher. The 2026-10-01 audit identified the global Tlumacz 0.31.2 installation as a source of such discrepancies.

## Verification

Runtime tests should be executed in an environment built from the current V4 wheel/checkout. The result must contain the date and exact command.
