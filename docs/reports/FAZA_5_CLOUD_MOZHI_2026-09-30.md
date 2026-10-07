# Faza 5 — Cloud: Mozhi

Data: 2026-09-30

Dodano `MozhiProvider` zgodny z `CloudProvider`.

Obsługa:
- endpoint `/api/translate`;
- silnik przekazywany przez route;
- normalizacja języków dla MyMemory;
- odpowiedź słownikowa i listowa;
- `base_url="auto"` przez selektor instancji;
- selektor sprawdza deklarowany silnik i listę języków, następnie wybiera najszybszą poprawną instancję;
- wybór instancji można wstrzyknąć w testach.

Weryfikacja:
- 2 testy Mozhi — PASS;
- Ruff — PASS;
- mypy — PASS, 30 plików źródłowych;
- pełny pytest V4 — 92 passed.
