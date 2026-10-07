# Faza 3 — Filter Engine: marker validator

Data: 2026-09-30

## Zakres

Dodano `MarkerValidator` dla markerów inline zgodnych z reprezentacją Okapi:
- U+E101 — opening;
- U+E102 — closing;
- U+E103 — isolated;
- drugi znak markera wskazuje indeks kodu od U+E110.

Walidator:
- akceptuje zwykły tekst;
- wymaga kompletnej pary marker + indeks;
- odrzuca nieznany typ markera;
- odrzuca nieprawidłowy znak indeksu;
- opcjonalnie sprawdza indeks względem rozmiaru tablicy kodów.

`DocumentProcessor` waliduje tekst źródłowy przed tłumaczeniem oraz wynik tłumaczenia przed przekazaniem go do `write()`.

## Odniesienie do V3

V3 zawiera testy ochrony i odtwarzania par markerów Okapi oraz test brakującego markera. V4 przejmuje odpowiedzialność integralności markerów jako osobny komponent; właściwa ochrona/odtwarzanie treści markerów pozostaje częścią dalszej implementacji pipeline'u filtrów.

## TDD

RED:
- testy uruchomione przed utworzeniem modułu;
- kolekcja zakończyła się `ModuleNotFoundError`.

GREEN:
- dodano minimalny walidator;
- zintegrowano go z procesorem;
- dodano eksport publiczny.

## Weryfikacja

- focused marker + processor: **10 passed**
- Ruff: **passed**
- mypy: **Success: no issues found in 19 source files**
- pełny suite V4: **44 passed**

## Dokumentacja

Zaktualizowano `docs/ARCHITECTURE.md`.

## Następny punkt

`Filter Host`.
