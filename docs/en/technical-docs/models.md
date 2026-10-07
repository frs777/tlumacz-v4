---
id: models-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: technical-documentation
source: src/tlumacz/qml_gui/, src/tlumacz/backends/
depends_on: [docs/STATUS.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: change to backend contract or model catalog
last_validation: "inspekcja dokumentacji SentinelX 2026-10-04"
---

## 2026-10-05 — current verified backend contract

Active translation paths are llama.cpp, Cloud, Apertium, and custom. `translategemma` is a llama.cpp `chat_template`, not a backend. The active Cloud registry contains OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate, Mozhi, and DLX. TXT and PDF are not registered in the active document Filter Engine.

# Translation Models and Backends — Tlumacz V4

## Active backends

V4 has three active translation directions:

- **llama.cpp** — local llama-server runtime;
- **Cloud** — cloud-provider router;
- **Apertium** — local backend through the Filter Engine.

## llama.cpp

The GUI has a `server_chat_template` setting, including the value `translategemma`. This selects the prompt format for the active llama.cpp runtime and **does not mean that the former FastAPI/Transformers backend has been restored**.

## Cloud

Cloud is an adapter/provider layer. Provider documentation must describe the current V4 contract, not the historical V3 `BackendManager`.

## Apertium

Apertium operates as a separate V4 backend through the Filter Engine. Distribution completeness of the `eng-pol` pair remains an open release 0.40.0 blocker.

## Retired paths

- FastAPI + Transformers as a local translation server — **RETIRED**.
- The old OpenVINO path with the TranslateGemma INT8 model — **RETIRED**.
- `FastAPIServerManager`, `fastapi_server`, `openvino_backend` — **RETIRED**.

Details, reasons for retirement and how to interpret older documents: `docs/RETIRED_FUNCTIONALITY.md`.

> **Note:** historical TranslateGemma/FastAPI/OpenVINO benchmarks are V3 evidence. They are not the current V4 feature matrix.

## Update rule

Do not add a model or provider to this documentation merely because it appears in historical V3. There must first be an active V4 implementation and a verified user flow.
