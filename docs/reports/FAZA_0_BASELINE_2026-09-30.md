---
id: faza-0-baseline-2026-09-30
status: evidence
meta:
  contentType: MigrationReport
  category: evidence
version: 0.40.0
updated: 2026-09-30
owner: platform-architecture
source:
  - docs/MIGRATION_INVENTORY.md
  - docs/PLAN_MIGRACJI-v4.md
expires_when: zastąpienie raportu pełniejszym raportem końcowym migracji
---

# Raport migracji — Faza 0: V3 baseline

## Status

**ZAKOŃCZONA — warunki Fazy 0 spełnione.**

## Zakres wykonany

- skatalogowano stan Git V3;
- uwzględniono lokalne, nieśledzone obszary;
- zidentyfikowano entrypoint i główne obszary architektury;
- utworzono/zweryfikowano niezależny katalog V4;
- przeniesiono plan do V4 jako kopię referencyjną;
- utworzono inventory V3 → V4;
- zapisano baseline stanu Git V3;
- wykonano pełny baseline testów V3;
- potwierdzono, że V3 nie został zmodyfikowany.

## Dane baseline

- V3 tracked: 181 plików
- V3 untracked: 75 wpisów
- V3 modified/deleted tracked: 62 wpisy
- Python files w working tree: 799
- test files: 37
- docelowa wersja V4: 0.40.0

## Baseline testów

Komenda:

`python -m pytest -q`

Wynik: **FAIL podczas collection**.

16 modułów testowych zakończyło collection błędem `ModuleNotFoundError: No module named 'lingua'`. Nie instalowano zależności ani nie zmieniano środowiska w celu „naprawienia” baseline.

## Integralność V3

Stan `git status --porcelain=v1` przed i po Fazie 0 jest identyczny.
Globalna konfiguracja Git nie była modyfikowana.

## Kryterium Fazy 0

Tabela „źródło V3 → decyzja V4” znajduje się w `docs/MIGRATION_INVENTORY.md`.

## Następny punkt

**Faza 1 — bootstrap V4.**

Przed implementacją należy zbudować nowe `pyproject.toml`, strukturę pakietów, test runner, quality gates i dokumentację V4. Nie należy kopiować całego V3.
