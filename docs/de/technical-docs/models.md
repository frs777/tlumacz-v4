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
expires_when: Änderung des Backend-Vertrags oder des Modellkatalogs
last_validation: "inspekcja dokumentacji SentinelX 2026-10-04"
---

## 2026-10-05 — aktuell bestätigter Backend-Vertrag

Aktive Übersetzungspfade sind llama.cpp, Cloud, Apertium und custom. `translategemma` ist eine llama.cpp-`chat_template`-Variante und kein eigenes Backend. Der aktive Cloud-Registry enthält OpenAI-kompatible Provider, DeepL, Microsoft, MyMemory, LibreTranslate, Mozhi und DLX. TXT und PDF sind nicht im aktiven Dokumentfilter registriert.

# Übersetzungsmodelle und Backends — Tlumacz V4

## Aktive Backends

V4 hat drei aktive Übersetzungsrichtungen:

- **llama.cpp** — lokale llama-server-Runtime;
- **Cloud** — Router für Cloud-Provider;
- **Apertium** — lokales Backend über die Filter Engine.

## llama.cpp

Die GUI besitzt die Einstellung `server_chat_template`, darunter den Wert `translategemma`. Dies wählt das Prompt-Format für die aktive llama.cpp-Runtime und **bedeutet nicht, dass das frühere FastAPI/Transformers-Backend wiederhergestellt wurde**.

## Cloud

Cloud ist eine Adapter-/Provider-Schicht. Die Provider-Dokumentation muss den aktuellen V4-Vertrag beschreiben, nicht den historischen V3-`BackendManager`.

## Apertium

Apertium arbeitet als separates V4-Backend über die Filter Engine. Die vollständige Distribution des Paars `eng-pol` bleibt ein offener Blocker für Release 0.40.0.

## Zurückgezogene Pfade

- FastAPI + Transformers als lokaler Übersetzungsserver — **ZURÜCKGEZOGEN**.
- Alter OpenVINO-Pfad mit TranslateGemma INT8 — **ZURÜCKGEZOGEN**.
- `FastAPIServerManager`, `fastapi_server`, `openvino_backend` — **ZURÜCKGEZOGEN**.

Details, Gründe für die Entfernung und Interpretation älterer Dokumente: `docs/RETIRED_FUNCTIONALITY.md`.

> **Hinweis:** Historische TranslateGemma/FastAPI/OpenVINO-Benchmarks sind V3-Nachweise. Sie sind nicht die aktuelle V4-Funktionsmatrix.

## Aktualisierungsregel

Ein Modell oder einen Provider nicht allein deshalb in diese Dokumentation aufnehmen, weil er im historischen V3 vorkommt. Zuerst müssen eine aktive V4-Implementierung und ein verifizierter Benutzerablauf vorhanden sein.
