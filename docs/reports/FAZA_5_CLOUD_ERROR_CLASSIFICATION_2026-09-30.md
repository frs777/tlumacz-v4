# Faza 5 — Cloud: klasyfikacja błędów

Data: 2026-09-30

Dodano wspólny model CloudError:
- configuration;
- authentication;
- rate_limit;
- timeout;
- network;
- http;
- invalid_response;
- provider;
- unknown.

Każdy błąd ma provider, retryable i opcjonalny HTTP status.

Mozhi korzysta z klasyfikatora dla błędów transportu, HTTP i niepoprawnych odpowiedzi.

Weryfikacja:
- 9 testów błędów/timeoutu/Mozhi — PASS;
- Ruff — PASS;
- mypy — PASS, 31 plików źródłowych;
- pełny pytest V4 — 99 passed.
