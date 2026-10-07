# Raport Fazy 1 — bootstrap V4

Data: 2026-09-30

## Zakres

Zrealizowano wszystkie punkty Fazy 1 z `PLAN_MIGRACJI-v4.md`:

- struktura katalogów V4;
- nowe `pyproject.toml`;
- wersja `0.40.0`;
- entrypoint CLI oraz `python -m tlumacz`;
- pakiety bazowe warstw V4;
- konfiguracja pytest;
- konfiguracja Ruff i mypy jako quality gates;
- dokumentacja architektury i developmentu.

## Decyzja dotycząca Lingua

`lingua-language-detector` pozostaje zewnętrzną zależnością. Nie instalowano jej podczas Fazy 1. Decyzja jest zapisana w `docs/MIGRATION_DECISIONS.md`.

## Weryfikacja

- `python -m pytest -q` → **2 passed**
- `ruff check .` → **passed**
- `PYTHONPATH=src python -m tlumacz --version` → **0.40.0**
- kontrola źródeł `src/` pod kątem referencji do V3 → **brak**
- `mypy src` → narzędzie `mypy` nie jest obecnie zainstalowane; konfiguracja quality gate jest obecna w `pyproject.toml`.

## Kryterium Fazy 1

**Spełnione:** V4 uruchamia się bez importowania V3.

## Następny etap

Faza 2 — kontrakty domenowe: `TranslationBackend`, `BackendResult`, `FilterContract`, `DocumentContract`, `InlineCode`, błędy domenowe, cancellation, health-check oraz workspace/session.
