# Tworzenie i integracja filtrów Okapi

> Dokumentacja przebudowana 2026-10-08. Źródłem prawdy dla opisów procesu jest aktualny kod V4 oraz bieżąca dokumentacja architektury. Starsze twierdzenia sprzeczne z kodem nie są tu powielane.

## Cel

Ten katalog opisuje rzeczywisty przepływ dokumentu przez Tłumacza, ze szczególnym uwzględnieniem filtrów Okapi, Filter Engine, preprocessingu, jednostek dokumentowych, planowania chunków, detekcji języka, tłumaczenia równoległego oraz rekonstrukcji.

## Najważniejsze rozróżnienie

Okapi jest mechanizmem obsługi strukturalnych formatów dokumentowych. Nie należy jednak przedstawiać wszystkich formatów jako jednej identycznej ścieżki:

- formaty z aktywnymi filtrami strukturalnymi przechodzą przez Filter Engine;
- TXT ma aktywny `PlainTextFilter`, ale nie wymaga strukturalnego modelu Okapi;
- Markdown ma własny filtr Filter Engine;
- PDF nie jest obecnie zarejestrowany w aktywnym FilterRegistry i posiada osobną obsługę bloków tekstowych w warstwie umiejętności;
- Apertium korzysta z własnego adaptera/backendu oraz integracji z Filter Engine.

## Spis

1. [Model procesu](01-model-procesu.md)
2. [Formaty wejściowe i wybór ścieżki](02-wejscie-formaty.md)
3. [Filter Engine i Okapi](03-filter-engine-okapi.md)
4. [Preprocessing i klasyfikacja jednostek](04-preprocessing.md)
5. [Chunkowanie i tłumaczenie równoległe](05-chunkowanie-i-rownoleglosc.md)
6. [Detekcja języka](06-detekcja-jezyka.md)
7. [Apertium i kody inline](07-apertium-inline.md)
8. [Rekonstrukcja i walidacja](08-rekonstrukcja-walidacja.md)
9. [Diagramy LaTeX](latex/main.tex)

## Źródła kodowe

- `src/tlumacz/filter_engine/registry.py`
- `src/tlumacz/filter_engine/processor.py`
- `src/tlumacz/filter_engine/filters/`
- `src/tlumacz/preprocessing/preprocessor.py`
- `src/tlumacz/application/chunk_planner.py`
- `src/tlumacz/application/translation_orchestrator.py`
- `src/tlumacz/application/translation_executor.py`
- `src/tlumacz/backends/llama_cpp/`
- `src/tlumacz/backends/apertium/`
- `docs/ARCHITECTURE.md`
- `docs/technical-docs/translation-pipeline-contracts.md`

## Zasada dokumentacyjna

Jeżeli dokumentacja ogólna i kod aktywny są rozbieżne, rozbieżność musi zostać jawnie oznaczona. Nie wolno tworzyć diagramu na podstawie starego opisu tylko dlatego, że jest prostszy.
