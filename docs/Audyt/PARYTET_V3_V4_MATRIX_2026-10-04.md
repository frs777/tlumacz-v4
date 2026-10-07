---
id: parity-matrix-v3-v4-2026-10-04
status: evidence
meta:
  contentType: Audit
  category: parity
version: 1.0.0
updated: 2026-10-06
owner: project-maintenance
source:
  - docs/Plany/00-BASELINE-MAPA-PARYTETU-V3-V4.md
  - docs/Audyt/AUDYT_FORENSICZNY_V3_V4_2026-10-01.md
depends_on: [docs/STATUS.md, docs/ARCHITECTURE.md]
expires_when: zakończenie planu 00 i zatwierdzenie baseline'u
last_validation: SentinelX + Apertium docs 2026-10-06
---

# Kanoniczna macierz parytetu V3 → V4

## Baseline źródłowy

- V3 tag: 'v0.31.2'; annotated tag object: '060471a52ec9b213591ee54923f1de5996c14607'; commit wskazywany przez tag: 'bfcb0facbe13f46e7e0cd72ee9dd66e70d11dc93'.
- V3 working tree: 'v0.31.2-dirty', 128 zmian/plików w git status; zawiera dodatkowe pliki nieobecne w tagu.
- V4: '0.40.0'.
- V3 pozostaje nietknięty; ta macierz jest wyłącznie materiałem dowodowym.

## Kryteria

| Status | Znaczenie |
|---|---|
| RESTORE | funkcja potwierdzona jako brakująca i wymaga odtworzenia |
| REBUILD | funkcja istnieje częściowo, ale wymaga odbudowy kontraktu |
| REPLACE | funkcja istnieje przez nową architekturę/implementację |
| KEEP | odpowiednik zachowany bez potrzeby migracji |
| RETIRED | świadomie wycofane |
| DEAD | udowodniony brak callerów i brak kontraktu |
| VERIFY-FIRST | brak wystarczającego dowodu do decyzji |

## Macierz funkcji

| Funkcja | V3 evidence | V4 location | Status | Dowód/uwaga |
|---|---|---|---|---|
| Detekcja języka Lingua dla TranslateGemma | tlumacz/language_detector.py + tests/test_language_detector.py + core.py | src/tlumacz/language_detector.py + backends/llama_cpp/adapter.py | REBUILD | Przywrócona jako izolowany kontrakt wyłącznie dla `chat_template="translategemma"`; standardowy llama.cpp nie używa detektora. |
| TXT | tlumacz/skills/plaintext.md | brak FilterRegistry | VERIFY-FIRST | Skill istnieje, ale aktywny registry nie rejestruje TXT. |
| Markdown | tlumacz/markdown/* | filter_engine/filters/markdown.py | REPLACE | Nowy Filter Engine. |
| HTML/XHTML | tlumacz/html.py | filter_engine/filters/html.py | REPLACE | Nowy Filter Engine. |
| DOCX | tlumacz/office.py | filter_engine/filters/docx.py | REPLACE | Nowy Filter Engine. |
| ODT | tlumacz/office.py | filter_engine/filters/odt.py | REPLACE | Nowy Filter Engine. |
| EPUB | tlumacz/epub.py | filter_engine/filters/epub.py | REPLACE | Nowy Filter Engine. |
| XLIFF 2.0 | tlumacz/xliff.py | filter_engine/filters/xliff.py | REPLACE | Nowy Filter Engine. |
| PDF | tlumacz/pdf_extractor.py | brak FilterRegistry | VERIFY-FIRST | Kod V4 nie ma aktywnego filtra PDF. |
| Cloud | tlumacz/cloud_providers.py | backends/cloud/router.py + providers.py | REPLACE | Router/provider registry. |
| DLX | tlumacz/cloud_providers.py | backends/cloud/providers.py::DLXProvider | REBUILD | Provider istnieje, ale aktywna konfiguracja wymaga potwierdzenia. |
| Apertium | backends/apertium/* | backends/apertium/* | KEEP | Aktywny backend; eng-pol pozostaje blockerem. |
| llama.cpp | server.py + llama_config.py | backends/llama_cpp/* | REPLACE | Nowy runtime ownership/lifecycle. |
| QML GUI | qt_gui/* | qml_gui/* | REPLACE | Migracja GUI zakończona. |
| Konfiguracja | config.py/config.json/llama_config.py | qml_gui/config.py + application/settings_controller.py | REPLACE | Nowy model ustawień. |

## Moduły V3 — inwentaryzacja

| V3 moduł | W tagu | V4 odpowiednik | Status |
|---|---:|---|---|
| 'tlumacz/__init__.py' | TAK | 'src/tlumacz/__init__.py' | **KEEP** |
| 'tlumacz/backends/__init__.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/backends/apertium/__init__.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/backends/apertium/adapter.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/backends/apertium/bundled.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/backends/apertium/config.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/backends/apertium/contract.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/backends/apertium/errors.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/backends/apertium/filter_adapter.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/backends/apertium/language_plugins.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/backends/apertium/languages.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/backends/apertium/runtime.py' | NIE | 'src/tlumacz/backends/' | **REPLACE** |
| 'tlumacz/cache.py' | TAK | 'src/tlumacz/application/translation_cache.py' | **REPLACE** |
| 'tlumacz/cloud_providers.py' | NIE | 'src/tlumacz/backends/cloud/' | **REPLACE** |
| 'tlumacz/core.py' | TAK | 'src/tlumacz/application/translation_orchestrator.py' | **REPLACE** |
| 'tlumacz/epub.py' | NIE | 'src/tlumacz/filter_engine/filters/epub.py' | **REPLACE** |
| 'tlumacz/extract.py' | TAK | '—' | **VERIFY-FIRST** |
| 'tlumacz/fastapi_manager.py' | TAK | '—' | **VERIFY-FIRST** |
| 'tlumacz/fastapi_server.py' | TAK | '—' | **VERIFY-FIRST** |
| 'tlumacz/filter_engine/__init__.py' | NIE | 'src/tlumacz/filter_engine/' | **REPLACE** |
| 'tlumacz/filter_engine/engine.py' | NIE | 'src/tlumacz/filter_engine/' | **REPLACE** |
| 'tlumacz/filter_engine/protocol.py' | NIE | 'src/tlumacz/filter_engine/' | **REPLACE** |
| 'tlumacz/glossary.py' | TAK | 'src/tlumacz/domain/contracts.py' | **VERIFY-FIRST** |
| 'tlumacz/html.py' | NIE | 'src/tlumacz/filter_engine/filters/html.py' | **REPLACE** |
| 'tlumacz/i18n.py' | TAK | 'src/tlumacz/i18n.py' | **KEEP** |
| 'tlumacz/installer.py' | NIE | '—' | **VERIFY-FIRST** |
| 'tlumacz/keys.py' | NIE | '—' | **VERIFY-FIRST** |
| 'tlumacz/language_detector.py' | NIE | '—' | **VERIFY-FIRST** |
| 'tlumacz/llama_config.py' | NIE | 'src/tlumacz/backends/llama_cpp/' | **REPLACE** |
| 'tlumacz/markdown/__init__.py' | TAK | 'src/tlumacz/filter_engine/filters/markdown.py' | **REPLACE** |
| 'tlumacz/markdown/chunker.py' | TAK | 'src/tlumacz/filter_engine/filters/markdown.py' | **REPLACE** |
| 'tlumacz/markdown/parser.py' | TAK | 'src/tlumacz/filter_engine/filters/markdown.py' | **REPLACE** |
| 'tlumacz/markdown/pipeline.py' | TAK | 'src/tlumacz/filter_engine/filters/markdown.py' | **REPLACE** |
| 'tlumacz/markdown/protection.py' | TAK | 'src/tlumacz/filter_engine/filters/markdown.py' | **REPLACE** |
| 'tlumacz/markdown/validator.py' | TAK | 'src/tlumacz/filter_engine/filters/markdown.py' | **REPLACE** |
| 'tlumacz/mozhi.py' | NIE | '—' | **VERIFY-FIRST** |
| 'tlumacz/office.py' | NIE | 'src/tlumacz/filter_engine/filters/docx.py + odt.py' | **REPLACE** |
| 'tlumacz/okapi.py' | NIE | '—' | **VERIFY-FIRST** |
| 'tlumacz/openvino_backend.py' | TAK | '—' | **VERIFY-FIRST** |
| 'tlumacz/pdf_extractor.py' | TAK | '—' | **VERIFY-FIRST** |
| 'tlumacz/preprocess.py' | TAK | 'src/tlumacz/filter_engine/processor.py' | **REPLACE** |
| 'tlumacz/qt_gui/__init__.py' | TAK | 'src/tlumacz/qml_gui/' | **REPLACE** |
| 'tlumacz/qt_gui/app.py' | TAK | 'src/tlumacz/qml_gui/' | **REPLACE** |
| 'tlumacz/qt_gui/backend_manager.py' | TAK | 'src/tlumacz/qml_gui/' | **REPLACE** |
| 'tlumacz/qt_gui/config.py' | TAK | 'src/tlumacz/qml_gui/' | **REPLACE** |
| 'tlumacz/qt_gui/help_texts.py' | TAK | 'src/tlumacz/qml_gui/' | **REPLACE** |
| 'tlumacz/qt_gui/main_window.py' | TAK | 'src/tlumacz/qml_gui/' | **REPLACE** |
| 'tlumacz/qt_gui/resources/__init__.py' | TAK | 'src/tlumacz/qml_gui/' | **REPLACE** |
| 'tlumacz/qt_gui/theme.py' | TAK | 'src/tlumacz/qml_gui/' | **REPLACE** |
| 'tlumacz/qt_gui/worker.py' | TAK | 'src/tlumacz/qml_gui/' | **REPLACE** |
| 'tlumacz/segmentation.py' | NIE | 'src/tlumacz/application/chunk_planner.py' | **REPLACE** |
| 'tlumacz/server.py' | TAK | 'src/tlumacz/backends/llama_cpp/runtime.py' | **REPLACE** |
| 'tlumacz/simplytranslate.py' | NIE | '—' | **VERIFY-FIRST** |
| 'tlumacz/skill.py' | TAK | 'src/tlumacz/skills/' | **REPLACE** |
| 'tlumacz/skills/__init__.py' | TAK | 'src/tlumacz/skills/__init__.py' | **KEEP** |
| 'tlumacz/version.py' | TAK | '—' | **VERIFY-FIRST** |
| 'tlumacz/xliff.py' | NIE | 'src/tlumacz/filter_engine/filters/xliff.py' | **REPLACE** |

## Jawnie wycofane ścieżki

| V3 | Status | Uzasadnienie |
|---|---|---|
| 'tlumacz/fastapi_manager.py' | **RETIRED** | FastAPI + Transformers nie jest aktywnym backendem V4. |
| 'tlumacz/fastapi_server.py' | **RETIRED** | FastAPI + Transformers nie jest aktywnym backendem V4. |
| 'tlumacz/openvino_backend.py' | **RETIRED** | OpenVINO TranslateGemma INT8 nie jest aktywnym backendem V4. |
| 'tlumacz/markdown/pipeline.py' | **RETIRED** | V4 używa Filter Engine; stara ścieżka MarkdownPipeline nie jest aktywna. |
| 'tlumacz/simplytranslate.py' | **RETIRED** | SimplyTranslate został usunięty z aktywnego V4. |

## Zasady dalszej pracy

1. VERIFY-FIRST nie jest zgodą na implementację.
2. Różnica nazwy pliku nie jest dowodem braku funkcji.
3. REPLACE wymaga testu kontraktu V4; nie oznacza automatycznie pełnej parytetu zachowania.
4. Funkcje dokumentowe wymagają osobnej macierzy E2E: extract → units/markers → language → chunk → translate → reconstruct → validation.
5. Detekcja języka jest osobnym punktem parytetu i nie zostanie uznana za przywróconą bez dowodu rzeczywistego działania.
6. TXT/PDF pozostają VERIFY-FIRST, mimo obecności materiałów skillów, ponieważ registry V4 ich nie rejestruje.
7. Apertium eng-pol pozostaje otwartym blockerem; nie klasyfikować go jako pełnego KEEP.

## Kryterium zamknięcia planu 00

Macierz jest źródłem dla planów 01–05. Każda pozycja wymagająca implementacji musi wskazywać proving test przed zmianą kodu.

## Macierz pipeline'u dokumentowego — obowiązkowa dla planów 01–05

| Format | Extract/probe | Jednostki/markery | Tłumaczenie | Reconstruction/write | Validation | Stan baseline |
|---|---|---|---|---|---|---|
| DOCX | Filter Engine | wymagane | wspólny Orchestrator | Filter Engine | FilterValidator/marker validation | VERIFY-FIRST E2E |
| ODT | Filter Engine | wymagane | wspólny Orchestrator | Filter Engine | FilterValidator/marker validation | VERIFY-FIRST E2E |
| HTML/XHTML | Filter Engine | wymagane | wspólny Orchestrator | Filter Engine | FilterValidator/marker validation | VERIFY-FIRST E2E |
| Markdown | Filter Engine | wymagane | wspólny Orchestrator | Filter Engine | FilterValidator/marker validation | VERIFY-FIRST E2E |
| EPUB | Filter Engine | wymagane | wspólny Orchestrator | Filter Engine | FilterValidator/marker validation | VERIFY-FIRST E2E |
| XLIFF 2.0 | Filter Engine | wymagane | wspólny Orchestrator | Filter Engine | FilterValidator/marker validation | VERIFY-FIRST E2E |
| TXT | brak aktywnego filtra | n/d | n/d | n/d | n/d | VERIFY-FIRST |
| PDF | brak aktywnego filtra | n/d | n/d | n/d | n/d | VERIFY-FIRST |

Dla każdego aktywnego formatu proving test musi sprawdzić nie tylko obecność klasy filtra, ale pełny przepływ: plik wejściowy → probe/open → extract → units/inline markers → source language → Chunk Planner → translation backend → ResultValidator/MarkerValidator → write/reconstruct → ponowny odczyt i kontrola integralności.

### Detekcja języka — osobna bramka

V3 working tree posiada `tlumacz/language_detector.py` z `detect_language_code()` i `supported_language_codes()` oraz używa wyniku detekcji w `_translate_chunk()` i kluczu cache. V3 tag v0.31.2 nie zawiera tego pliku, ale dokumentacja i working tree potwierdzają późniejszy kontrakt TranslateGemma.

V4 przywraca detekcję Lingua **wyłącznie dla `chat_template="translategemma"`**. `LlamaCppAdapter` tworzy detektor tylko w tym trybie, wykrywa źródło osobno dla każdego requestu/chunku i przekazuje kod ISO 639-1 do promptu TG. Standardowy llama.cpp pozostaje bez detekcji Lingua. Status bramki: **REBUILD — test kontraktu GREEN, E2E z rzeczywistym modelem pozostaje do wykonania**.

### Cloud — macierz kontraktu

| Provider V3 working tree | V4 provider | Kontrakt | Status |
|---|---|---|---|
| OpenAI-compatible | OpenAICompatibleProvider | base URL, API key, model, timeout, wynik/error | REPLACE |
| DeepL | DeepLProvider | endpoint, key, source/target, timeout | REPLACE |
| Microsoft | MicrosoftProvider | endpoint, key, source/target, timeout | REPLACE |
| MyMemory | MyMemoryProvider | UTF-8 limit, endpoint, source/target | REPLACE |
| LibreTranslate | LibreTranslateProvider | endpoint, key, source/target | REPLACE |
| Mozhi | MozhiProvider | instance, engine, language normalization | REPLACE |
| DLX | DLXProvider | endpoint, limit, source/target, error mapping | REBUILD |
| SimplyTranslate | brak | provider usunięty | RETIRED |

cloud_models.json V4 nie zawiera obecnie profilu DLX, mimo że DLXProvider istnieje w kodzie. To jest jawny punkt planu 01, a nie automatyczna decyzja o zmianie konfiguracji.

## GUI — kontrakt funkcjonalny

Migracja Widgets → QML jest klasyfikowana jako REPLACE, nie RESTORE. Plan 01 nie powinien odtwarzać qt_gui; powinien jedynie sprawdzać parytet zachowania aktywnego qml_gui: backend selection, file input/output, language selection, progress, cancellation, settings, glossary, skills, help/i18n i cloud profile selection.

## Round-trip konfiguracji

Do proving testów należy zaliczyć: odczyt ustawień → normalizacja → zapis → ponowny odczyt → porównanie semantyczne. Nie wystarcza test pojedynczego load_settings().

## Wynik fazy 00

Baseline został zamrożony w tej macierzy. Nie wprowadzono zmian w kodzie V4 ani V3. Wszystkie punkty bez wystarczającego dowodu pozostawiono VERIFY-FIRST; nie przekształcono ich w braki przez samo porównanie nazw plików.


## Rewalidacja baseline — 2026-10-06

Ponowna kontrola potwierdziła stan V3 i V4 bez zmian funkcjonalnych w ramach tej pracy.

- V3 `v0.31.2` wskazuje na commit `bfcb0facbe13f46e7e0cd72ee9dd66e70d11dc93`; `060471a52ec9b213591ee54923f1de5996c14607` jest identyfikatorem obiektu annotated tag.
- V3 `git status --porcelain=v1` zawiera 128 pozycji: 62 zmiany śledzonych plików i 66 pozycji nieśledzonych.
- Aktualny V4 zawiera 66 plików Python pod `src/tlumacz/`, 6 plików QML i 61 plików `test_*.py`.
- Zależności i kod V3 nie były modyfikowane.
- Zewnętrzna dokumentacja Apertium potwierdza, że dostępne kierunki par językowych są jawnie kierunkowe i nie każda para jest rozwijana w obu kierunkach; tryby są związane z konkretną parą/kierunkiem.

Wniosek: macierz pozostaje obowiązującym baseline'em; VERIFY-FIRST nadal wymaga dowodu wykonawczego przed zmianą kodu.