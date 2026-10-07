# Faza 3 — Filter Host, protokół, DOCX i round-trip

Data: 2026-09-30

## Zakres

Zamknięto cztery ostatnie punkty Fazy 3:
- Filter Host;
- wersjonowany protokół JSON Lines;
- filtr DOCX/OpenXML;
- round-trip przez V4 Filter Engine.

## Implementacja

### Filter Host
- dodano `java/filter-host/src/main/java/pl/tlumacz/filterhost/FilterHost.java`;
- dodano kontrolowany launcher `java/filter-host/run.sh`;
- launcher nie korzysta z systemowego fallbacku Okapi;
- brak lokalnego runtime kończy działanie kodem 3;
- host pozostaje osobnym procesem JVM.

### Protokół
- dodano `tlumacz.filter_engine.protocol.FilterHostClient`;
- request ma `protocol_version`, `request_id`, `operation`, `payload`;
- odpowiedź jest walidowana względem wersji i request ID;
- błędy hosta zachowują `code` i `retryable`;
- komunikacja używa JSON Lines i jednego procesu hosta dla sesji.

### DOCX
- dodano `DocxFilter`;
- wejście jest walidowane jako kontener DOCX;
- ekstrakcja obejmuje tekstowe elementy WordprocessingML `w:t`;
- jednostki mają stabilne ID, kolejność i hash źródła;
- zapis modyfikuje wyłącznie właściwy XML, zachowując pozostałe wpisy ZIP;
- zmiana źródła po ekstrakcji jest wykrywana przed zapisem;
- test obejmuje zachowanie zasobu binarnego.

### Round-trip
Przepływ:
`DOCX → extract → stub translation → targets → write → DOCX`
został potwierdzony przez `DocumentProcessor`.

## TDD

RED:
- brak modułu Filter Host;
- brak klienta protokołu;
- brak filtra DOCX.

GREEN:
- testy hosta: 3 passed;
- testy protokołu: 6 passed;
- testy DOCX: 5 passed.

Weryfikacja końcowa:
- focused suite: 17 passed;
- Ruff: PASS;
- mypy: PASS, 22 pliki źródłowe;
- pełny V4 pytest: 58 passed.

## Uwagi architektoniczne

Implementacja DOCX jest pierwszym filtrem formatowym V4 i świadomie nie zna backendu tłumaczeniowego. Java Filter Host pozostaje izolacją dla filtrów Okapi; szczegółowe spięcie pełnego runtime'u Okapi z docelowym protokołem pozostaje zależne od dependency closure runtime'u.

## Status

Faza 3 jest kompletna według bieżącej listy planu. Następna jest Faza 4 — LlamaCppBackend.
