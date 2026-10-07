# Tlumacz V4

Eine neue Implementierung der Übersetzungsanwendung, unabhängig von V3 entwickelt.

## Migrationsstatus

V4-Bootstrap: 0.40.0.

V4 importiert keinen Code aus agent-translator-v3. Die Migration der Funktionen erfolgt schrittweise gemäß `docs/PLAN_MIGRACJI-v4.md`.

## Start

    python -m tlumacz --version

Nach Installation des Pakets:

    tlumacz --version

## Tests

    python -m pytest -q

## Quality Gates

    ruff check .
    mypy src
    python -m pytest -q

## Lokalisierung

Die QML-Oberfläche, Benutzerhilfe und sichtbaren Log-Bezeichnungen sind in PL/EN/DE verfügbar. Die Anwendungssprache kann im Tab Hilfe geändert werden.
Der Übersetzungsstatus steht in docs/I18N_STATUS.md.
