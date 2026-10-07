# Faza 3 — Filter Engine: validator

Data: 2026-09-30

## Zakres

Dodano `FilterValidator` jako granicę integralności danych między filtrem a procesorem.

Walidator:
- normalizuje jednostki do par `(unit_id, source)`;
- odrzuca brakujące lub puste identyfikatory;
- odrzuca źródło o nieprawidłowym typie;
- odrzuca duplikaty identyfikatorów;
- wymaga dokładnego zbioru targetów odpowiadającego jednostkom;
- odrzuca targety o nieprawidłowym typie.

`DocumentProcessor` korzysta z walidatora przed tłumaczeniem oraz przed przekazaniem targetów do `write()`.

## TDD

RED:
- testy zostały napisane przed implementacją;
- początkowo kolekcja zakończyła się `ModuleNotFoundError` dla nowego modułu.

GREEN:
- dodano minimalny `FilterValidator`;
- podłączono go do procesora;
- API eksportuje `FilterValidator`.

## Weryfikacja

- focused validator + processor: **8 passed**
- Ruff: **passed**
- mypy: **Success: no issues found in 18 source files**
- pełny suite V4: **36 passed**

## Dokumentacja

Zaktualizowano `docs/ARCHITECTURE.md` o odpowiedzialność warstwy `filter_engine/`.

## Następny punkt

`marker validator`.
