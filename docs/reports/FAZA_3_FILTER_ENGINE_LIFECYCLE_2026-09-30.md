# Faza 3 — Filter Engine: lifecycle

Data: 2026-09-30

## Zakres

Zaimplementowano jawny lifecycle sesji filtra:
- `FilterLifecycle.open(...)`;
- `FilterSessionContext` jako context manager;
- gwarantowane `close()` po zakończeniu bloku, także po wyjątku;
- idempotentne zamknięcie sesji;
- brak `close()` po nieudanym `open()`.

`DocumentProcessor` korzysta teraz z `FilterLifecycle`, więc lifecycle jest częścią rzeczywistej ścieżki przetwarzania.

## TDD

RED:
- brak modułu `tlumacz.filter_engine.lifecycle`;
- następnie test ujawnił błędne oczekiwanie API dotyczące miejsca `close()`.

GREEN:
- dodano minimalną implementację lifecycle;
- testy doprecyzowano do granicy odpowiedzialności contextu sesji;
- poprawiono adnotację `__exit__` wymaganą przez mypy.

## Weryfikacja

- focused lifecycle + processor: **6 passed**
- Ruff: **passed**
- mypy: **Success: no issues found in 17 source files**
- pełny suite V4: **30 passed**

## Następny punkt

`validator`.
