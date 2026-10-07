# Faza 6 — Apertium: backend

Data: 2026-09-30

Dodano `ApertiumBackend` jako cienką fasadę nad adapterem:
- implementuje wspólny kontrakt `TranslationBackend`;
- deleguje `translate` i `health_check`;
- nie zna CLI, procesu ani szczegółów runtime;
- nie wymaga instalacji runtime podczas działania.

Weryfikacja:
- 3 testy backendu — PASS;
- Ruff — PASS;
- mypy — PASS, 42 pliki źródłowe;
- pełny pytest V4 — 114 passed.
