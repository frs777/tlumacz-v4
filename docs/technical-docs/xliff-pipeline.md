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
expires_when: zmiana kontraktu XLIFF Filter Engine
last_validation: "weryfikacja Filter Engine V4 2026-10-01"
---

# Filtr XLIFF 2.0 — Tłumacz V4

XLIFF 2.0 jest wewnętrzną warstwą dokumentową V4, a nie aktywnym filtrem wejściowym. Implementacja znajduje się w `src/tlumacz/documents/xliff.py`.

## Przepływ

```text
XLIFF 2.0
  ↓
XliffFilter
  ↓
jednostki Filter Engine
  ↓
Translation Port / backend
  ↓
target
  ↓
zapis XLIFF
```

Filtr waliduje wersję dokumentu, zachowuje identyfikatory jednostek i sprawdza, czy source nie został zmieniony przed zapisaniem targetów.

## Rejestracja

Aktualne GUI rejestruje `XliffFilter` dla rozszerzeń `.xlf` i `.xliff`.

## Uwaga migracyjna

Starsze dokumenty V3 opisywały XLIFF jako centralny pipeline całej aplikacji. W V4 XLIFF jest jednym z aktywnych filtrów, obok innych formatów; nie należy przenosić starego modelu architektury.