# Faza 4 — LlamaCppBackend: timeout

Data: 2026-09-30

Dodano jawne limity lifecycle:
- `startup_timeout`;
- `shutdown_timeout`;
- `poll_interval`;
- `wait_for_ready(probe)`.

Timeout startupu kończy oczekiwanie i zatrzymuje własny proces. Shutdown ma osobny limit i eskalację do kill po jego przekroczeniu.

Weryfikacja:
- 3 testy timeoutu — PASS;
- Ruff — PASS;
- mypy — PASS, 25 plików źródłowych;
- pełny pytest V4 — 70 passed.
