# Faza 4 — LlamaCppBackend: cancellation

Data: 2026-09-30

Runtime manager został spięty z V4 `CancellationToken`.

Semantyka:
- anulowany token zatrzymuje wyłącznie własny proces llama.cpp;
- nieanulowany token nie zmienia stanu procesu;
- ownership check pozostaje obowiązkowy przed terminacją.

Weryfikacja:
- 2 testy cancellation — PASS;
- Ruff — PASS;
- mypy — PASS, 25 plików źródłowych;
- pełny pytest V4 — 79 passed.
