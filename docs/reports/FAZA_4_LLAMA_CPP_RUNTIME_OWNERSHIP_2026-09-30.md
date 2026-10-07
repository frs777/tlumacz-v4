# Faza 4 — LlamaCppBackend: runtime manager i process ownership

Data: 2026-09-30

## Runtime manager
Dodano:
- `LlamaCppRuntimeConfig`;
- budowanie command line dla llama-server;
- start/stop procesu;
- idempotentny start;
- kontrolowane zakończenie procesu.

## Process ownership
Dodano `ProcessIdentity` zawierający:
- PID;
- executable;
- command line;
- parent PID;
- process group;
- session ID.

Manager zapisuje tożsamość przy starcie i sprawdza ją przed terminacją. Przy rozbieżności proces pozostaje uruchomiony.

## Weryfikacja
- runtime manager: 4 testy;
- ownership: 2 testy;
- Ruff: PASS;
- mypy: PASS, 25 plików źródłowych;
- pełny pytest V4: 67 passed.

## Następny punkt
Timeout procesu/startup readiness.
