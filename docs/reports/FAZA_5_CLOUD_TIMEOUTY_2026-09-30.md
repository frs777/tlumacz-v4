# Faza 5 — Cloud: timeouty

Data: 2026-09-30

CloudRoute wymusza dodatni timeout, a providerzy otrzymują go bezpośrednio jako limit requestu. Mozhi został zweryfikowany na sztucznym serwerze opóźniającym odpowiedź: request kończy się błędem w zadanym limicie zamiast czekać na odpowiedź.

Weryfikacja:
- 1 test timeoutu HTTP — PASS;
- Ruff — PASS;
- mypy — PASS, 30 plików źródłowych;
- pełny pytest V4 — 93 passed.
