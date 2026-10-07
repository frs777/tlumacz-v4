---
id: xliff-pipeline-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-01
owner: document-runtime
source: src/tlumacz/documents/xliff.py
depends_on: [docs/ARCHITECTURE.md]
expires_when: Änderung des XLIFF-Filter-Engine-Vertrags
last_validation: "V4 Filter Engine-Verifikation 2026-10-01"
---

# XLIFF-2.0-Filter — Tlumacz V4

XLIFF 2.0 ist eine interne V4-Dokumentebene und kein aktiver Eingabefilter. Die Implementierung befindet sich in `src/tlumacz/documents/xliff.py`.

## Ablauf

```text
XLIFF 2.0
  ↓
XliffFilter
  ↓
Filter-Engine-Einheiten
  ↓
Translation Port / Backend
  ↓
target
  ↓
XLIFF schreiben
```

Der Filter validiert die Dokumentversion, erhält die Einheiten-IDs und prüft vor dem Schreiben der Targets, dass die Source nicht verändert wurde.

## Registrierung

Die aktuelle GUI registriert `XliffFilter` für die Erweiterungen `.xlf` und `.xliff`.

## Migrationshinweis

Ältere V3-Dokumente beschrieben XLIFF als zentrale Pipeline der gesamten Anwendung. In V4 ist XLIFF einer von mehreren aktiven Filtern; das alte Architekturmodell darf nicht übernommen werden.
