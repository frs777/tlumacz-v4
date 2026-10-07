# Faza 3 — Filter Engine: registry

Data: 2026-09-30

## Zakres

Zakończono pierwszy punkt Fazy 3 planu migracji V3 → V4: **registry**.

## Implementacja

- `src/tlumacz/filter_engine/registry.py`
- `src/tlumacz/filter_engine/__init__.py`
- `tests/test_filter_registry.py`

Registry:
- normalizuje rozszerzenia do postaci lowercase z kropką;
- rozwiązuje filtr na podstawie ścieżki dokumentu;
- odrzuca nieznane rozszerzenia przez `FilterError`;
- odrzuca duplikaty rejestracji;
- udostępnia deterministyczną listę zarejestrowanych suffixów;
- wymaga zgodności obiektu z `FilterContract`.

Implementacja jest niezależna od Qt, konkretnego providera i V3.

## TDD

1. RED: test registry utworzony przed implementacją; kolekcja zakończyła się `ModuleNotFoundError: No module named 'tlumacz.filter_engine'`.
2. GREEN: minimalna implementacja registry.
3. REFACTOR/quality: korekta długości linii w teście.

## Weryfikacja

- focused tests: `4 passed`
- Ruff: `All checks passed!`
- mypy: `Success: no issues found in 2 source files`
- full suite: `15 passed`

## Stan

Punkt `registry` jest zamknięty. Następny punkt zgodnie z planem: `processor`.