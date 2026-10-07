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
expires_when: Änderung der Struktur der technischen Dokumentation
last_validation: "Dokumentationsaudit V3 → V4 2026-10-01"
---

# Tlumacz V4 — Technische Dokumentation

Dies ist die Karte der **aktuellen V4-Implementierung**. Historische, migrationsbezogene und archivierte Dokumente sind keine Quelle der aktuellen Architektur.

## Quellen der Wahrheit

- `docs/STATUS.md` — aktueller Projektstatus.
- `docs/BUG.md` — aktive Defekte und Risiken.
- `docs/ARCHITECTURE.md` — aktuelles Architekturmodell.
- `docs/RETIRED_FUNCTIONALITY.md` — aus V4 entfernte Funktionen und Technologien.
- `docs/INDEX.md` / `docs/INDEX.yml` — vollständiges Dokumentationsinventar.
- `src/tlumacz/` — Implementierung.

## Aktive Architektur

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

Die Filter Engine unterstützt eigene Python-Filter sowie einen isolierten Java Filter Host für Formate, die Okapi benötigen.

## Aktive Dokumentationsbereiche

### GUI und Benutzer

- `user-guide.md`
- `help-content.md`
- `models.md`

### Backend und Runtime

- `cloud-translation.md`
- `server-management.md`
- `apertium-backend-integration.md`
- `packaging-release.md`
- `xliff-pipeline.md`

### Architekturdokumente

- `docs/ARCHITECTURE.md`
- `docs/ARCHITEKTURA_FILTER_ENGINE_V4_PYTHON_OKAPI_BRIDGE_2026-09-26.md`
- `docs/ARCHITEKTURA_WLASNEGO_SILNIKA_FILTROW_V4_2026-09-26.md`

## Historische Dokumente

Material zu FastAPI, OpenVINO, dem alten `BackendManager`, dem alten TranslateGemma/FastAPI und anderen inaktiven Pfaden ist als historisch zu behandeln. Das vollständige Register befindet sich in `docs/RETIRED_FUNCTIONALITY.md`.

Historische Architektur darf nicht allein deshalb in aktive Anweisungen übernommen werden, weil sie eine frühere Implementierung beschreibt.

## Synchronisationsregel

Wenn ein technisches Dokument dem V4-Code, einem Test oder `STATUS.md` widerspricht, haben aktueller Code und verifizierter Projektstand Vorrang. Jedes Testergebnis muss Datum und exakten Befehl enthalten.
