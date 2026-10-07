---
id: cloud-translation-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-01
owner: cloud-runtime
source: src/tlumacz/backends/cloud/
depends_on: [docs/ARCHITECTURE.md, docs/STATUS.md]
expires_when: change to CloudRouter/provider contract
last_validation: "GUI/Cloud V3 → V4 audit 2026-10-01"
---

## 2026-10-05 — current Cloud and SecretStore state

Cloud is active. The default provider registry contains OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate, Mozhi, and DLX. The QML bridge uses `SecretStore` and migrates legacy profile `api_key` values out of ordinary JSON settings.

# Cloud Translation — Tlumacz V4

Cloud is an active V4 backend. Orchestration is performed through CloudRouter and the provider registry; documentation does not rely on the historical V3 BackendManager.

## Active adapters

The current code contains adapters for:

- OpenAI-compatible
- DeepL
- Microsoft Translator
- MyMemory
- LibreTranslate
- DLX
- Mozhi as a separate adapter/provider

Exact classes and contracts are in `src/tlumacz/backends/cloud/`.

## Configuration

Cloud profile configuration is part of the V4 mechanism. Secrets must not be stored in documentation or in the repository.

## Retired paths

FastAPI/Transformers and OpenVINO are not part of Cloud or the active V4 architecture. Older documents describing `BackendManager` or historical V3 servers are migration material.

## Verification

Providers have contract/compatibility tests. When an adapter changes, update the corresponding test and documentation.

## Update 2026-10-01

SimplyTranslate was retired from the active V4 matrix. A connection was not successfully established; the provider, Cloud profile, engine setting and contract test were removed. Historical SimplyTranslate descriptions remain archival material and do not describe the active V4 configuration.
