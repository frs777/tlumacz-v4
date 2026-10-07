# Faza 3 — Filter Engine: processor

Data: 2026-09-30

## Zakres

Zakończono punkt `processor`.

## Implementacja

- `src/tlumacz/filter_engine/processor.py`
- `tests/test_filter_processor.py`

Processor orkiestruje: wybór filtra → open → extract → translate → write → close.
Nie zawiera wiedzy o konkretnym formacie ani backendzie.
Puste jednostki są zachowywane bez wywołania funkcji tłumaczącej.

## TDD

RED: testy utworzono przed implementacją; kolekcja zakończyła się brakiem modułu `processor`.
GREEN: dodano minimalny processor zgodny z istniejącym `FilterContract` i `BackendResult`.

## Weryfikacja

- focused tests: `2 passed`
- Ruff: `All checks passed!`
- mypy: `Success: no issues found in 3 source files`
- full suite: `17 passed`

## Stan

Punkt `processor` jest zamknięty. Następny punkt: `workspace`.