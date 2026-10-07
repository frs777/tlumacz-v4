# Tlumacz V4

A new implementation of the translator application, developed independently from V3.

## Migration status

V4 bootstrap: 0.40.0.

V4 does not import code from agent-translator-v3. Feature migration is performed in stages according to `docs/PLAN_MIGRACJI-v4.md`.

## Running

    python -m tlumacz --version

After installing the package:

    tlumacz --version

## Tests

    python -m pytest -q

## Quality gates

    ruff check .
    mypy src
    python -m pytest -q

## Localization

The QML interface, user help and user-visible log labels are available in PL/EN/DE. The application language can be changed from the Help tab.
See docs/I18N_STATUS.md for the translation register.

## Project website

[Project website — downloads](https://frs777.github.io/tlumacz-v4/pobieranie.html)
