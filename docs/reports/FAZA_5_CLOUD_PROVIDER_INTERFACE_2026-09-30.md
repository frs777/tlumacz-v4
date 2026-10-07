# Faza 5 — Cloud: provider interface

Data: 2026-09-30

Dodano runtime-checkable `CloudProvider`:
- stabilna nazwa providera;
- wspólna metoda `translate`;
- wspólny wynik `BackendResult`;
- brak zależności od GUI i CloudRouter.

CloudRouter został dostosowany do rejestrowania obiektów spełniających ten kontrakt.

Weryfikacja:
- provider contract + router: 7 testów — PASS;
- Ruff — PASS;
- mypy — PASS, 28 plików źródłowych;
- pełny pytest V4 — 86 passed.
