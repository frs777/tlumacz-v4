# Tlumacz V4

Nowa implementacja aplikacji tłumacza budowana niezależnie od V3.

## Stan migracji

Bootstrap V4: 0.40.0.

V4 nie importuje kodu z agent-translator-v3. Migracja funkcjonalności odbywa się etapami według docs/PLAN_MIGRACJI-v4.md.

## Strona projektu

[Strona projektu — pobieranie](https://frs777.github.io/tlumacz-v4/pobieranie.html)

## Uruchomienie

    python -m tlumacz --version

Po zainstalowaniu pakietu:

    tlumacz --version

## Testy

    python -m pytest -q

## Quality gates

    ruff check .
    mypy src
    python -m pytest -q
