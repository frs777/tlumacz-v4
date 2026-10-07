## Normalizacja ścieżek użytkownika

W dokumentacji i konfiguracjach projektu ścieżki użytkownika zapisujemy jawnie jako `$HOME/...`. Dla katalogów XDG należy stosować `${XDG_CONFIG_HOME:-$HOME/.config}` albo odpowiednik oparty o `Path.home()` zgodnie z warstwą implementacji.

## Kontrakt natychmiastowego startu llama.cpp — 2026-10-06

Po wybraniu `llama.cpp` w GUI aplikacja:
1. ustawia `auto_start_server=True`;
2. zapisuje tę wartość do trwałych ustawień;
3. natychmiast uruchamia `core.start_llama()` przez `_maybe_autostart_server()`.

Nie trzeba rozpoczynać tłumaczenia ani restartować programu, aby serwer wystartował. Po zmianie z llama.cpp na inny backend lokalny runtime jest najpierw zatrzymywany.

## 2026-10-06 — poprawka `Connection refused`

- GUI sprawdza i zapewnia działający `llama-server` bezpośrednio przed tłumaczeniem;
- potwierdzono regresję E2E po zatrzymaniu serwera;
- `/usr/bin/tlumacz` pozostaje V3 `0.31.2`; V4 ma osobny launcher repozytoryjny.

## Kontrakt cyklu życia llama.cpp przy zmianie serwera — 2026-10-06

- wybór llama.cpp ustawia `auto_start_server=True`, aby serwer był uruchamiany razem z programem;
- zmiana z llama.cpp na inny backend najpierw wywołuje `core.stop_llama()`;
- dopiero po zatrzymaniu lokalnego runtime zmieniany jest aktywny backend;
- przełączenie Apertium, Chmura lub Własny nie pozostawia działającego procesu llama.cpp.

## Kontrakt autostartu llama.cpp — 2026-10-06

Wybór backendu llama.cpp w QmlApplicationBridge automatycznie ustawia settings.auto_start_server = True. Jest to część kontraktu wyboru lokalnego serwera: po zmianie serwera na llama.cpp aplikacja ma być skonfigurowana do uruchamiania llama.cpp razem ze startem programu.

Istniejący checkbox „Automatyczny start llama.cpp” pozostaje dostępny. Użytkownik może po wyborze llama.cpp wyłączyć autostart; przełączenie backendu ponownie na llama.cpp przywraca wartość True. setBackendType() zapisuje ten stan do trwałych ustawień.

## Kanoniczny mechanizm detekcji języka dla llama.cpp — 2026-10-06

To jest obowiązujący opis mechanizmu. Nie należy rekonstruować jego działania wyłącznie na podstawie kodu.

### 1. Odpowiedzialność komponentów

- `src/tlumacz/language_detector.py` — jedyny moduł odpowiedzialny za detekcję języka; używa biblioteki Lingua.
- `src/tlumacz/backends/llama_cpp/language_routing.py` — warstwa routingu źródła wyłącznie dla llama.cpp; wywołuje `LanguageDetector` dla każdego chunka.
- `src/tlumacz/backends/llama_cpp/adapter.py` — adapter transportowy/tłumaczeniowy; nie wykrywa języka.
- `QmlApplicationBridge` — właściciel stanu GUI, w tym języka docelowego.

### 2. Detekcja źródła dla llama.cpp

1. GUI może ustawić `source_language=auto`.
2. `DocumentTranslationService` przekazuje chunki do `TranslationOrchestrator`.
3. Dla backendu `llama` `TranslationApp` tworzy `LlamaCppLanguageRouting`.
4. `LlamaCppLanguageRouting.resolve_chunk_source()` przekazuje tekst bieżącego chunka do `LanguageDetector.detect_language_code()`.
5. Lingua zwraca kod ISO 639-1, np. `en`, `fr`, `de`, `pl`, albo `None`, jeśli detekcja się nie powiedzie.
6. Jeżeli detekcja zwróci kod, ten kod staje się `source_language` dla tego jednego chunka.
7. Jeżeli detekcja zwróci `None`, a GUI ma ręcznie ustawiony source różny od `auto`, używany jest ręczny source. Jeżeli source nadal jest `auto`, chunk nie może zostać przekazany do TranslateGemma z `auto`.
8. Kolejny chunk jest wykrywany niezależnie. Wykrycie `en` dla jednego chunka nie blokuje późniejszego `fr` lub `de`.

### 3. Język docelowy dla llama.cpp

Język docelowy nie jest wykrywany przez Lingua. Jest wybierany przez GUI. Dla llama.cpp obowiązuje invariant: `target_language` musi być niepustym kodem/nazwą języka obsługiwaną przez `language_code_for()`.

Przed rozpoczęciem tłumaczenia `QmlApplicationBridge._normalize_target_language_for_backend()` sprawdza stan. Jeżeli aktywnym backendem jest `llama` i target jest pusty lub zawiera wyłącznie białe znaki, stan jest ustawiany na `pl`. Dzięki temu pusty target nie może wejść do `TranslationApp` jako prawidłowa konfiguracja tłumaczenia.

### 4. Przekazanie do TranslateGemma

Dla aktualnego llama-server 0.4.0-dev obowiązuje ścieżka --no-jinja + /v1/completions. LlamaCppAdapter renderuje format Gemma ręcznie, w tym kody ISO source/target. Nie należy opierać bieżącej implementacji na historycznym kontrakcie chat_template_kwargs z wcześniejszego builda llama.cpp.

### 5. Cloud i custom

`LlamaCppLanguageRouting` nie jest używany przez backendy `cloud` ani `custom`. Każdy backend ma własny kontrakt źródła i celu.

### 6. Diagnostyka błędu `Nieobsługiwany język docelowy TranslateGemma: ''`

Ten komunikat oznacza konkretnie, że do `LlamaCppAdapter._translate_translategemma()` dotarł pusty `target_language`. Nie oznacza problemu z Lingua ani z wykrywaniem `source_language`. Aktualna ochrona znajduje się przed uruchomieniem pipeline'u w `QmlApplicationBridge` i ustawia pusty target llama.cpp na `pl`.

### 7. Kontrakt wizualny zakładki „API i serwer” dla llama.cpp — 2026-10-06

W sekcji llama.cpp obowiązuje układ bez osobnego pola „Adres serwera” oraz bez dodatkowej etykiety z wyliczonym URL-em. Po nagłówku „Serwer llama.cpp — lokalny” i separatorze widoczne są bezpośrednio: `Port`, `Obliczenia serwera`, `Szablon czatu`, `Parallel`, `Model`, sekcja „Zachowanie backendu” oraz przycisk „Restartuj serwer”.

Nie należy dodawać do tej sekcji kolejnej linii edycji hosta ani etykiety `http://<host>:<port>/v1`. Host i endpoint pozostają częścią konfiguracji technicznej bridge/runtime, ale nie są osobnym kontrolkiem w tej karcie.

Ustawienia llama.cpp nie są celowo zerowane przy otwarciu karty. Są ładowane z trwałego profilu `$HOME/.config/tlumacz/config.json` przez `AppSettings`; przy zamknięciu głównego okna `Main.qml` wywołuje `bridge.saveSettings()`, więc ostatni stan portu, trybu obliczeń, szablonu, parallel i ścieżki GGUF jest zapisywany i odtwarzany przy następnym uruchomieniu.

Ten kontrakt jest częścią regresji QML i nie należy go rekonstruować wyłącznie ze screenshotu.

---
id: docs-index-v4
status: active
meta:
  contentType: Reference
  category: governance
version: 3.5.0
updated: 2026-10-07
owner: project-documentation
source: docs/INDEX.yml
depends_on: [docs/AGENTS.md, docs/DOCUMENTATION_CHANGELOG.md]
expires_when: zmiana struktury docs
last_validation: 'Inwentaryzacja dokumentacji 2026-10-07 — 510 plików; 510 wpisów; 0 brakujących; 0 martwych; 0 duplikatów'
---

# Indeks dokumentacji Tłumacz V4

## Źródła prawdy

- docs/STATUS.md
- docs/ARCHITECTURE.md
- docs/technical-docs/
- docs/BUG.md
- docs/TODO.md
- docs/DOCUMENTATION_CHANGELOG.md
- docs/INDEX.yml

## Plany

- docs/Plany/PLAN-2026-10-05.md
- docs/Plany/PLAN-naprawy-2026-10-05.md
- docs/Plany/PLAN-00..11-* — plany modułowe i ich dokumentacja historyczna.
- docs/Plany/PLAN-12-TRANSLATEGEMMA-CHUNKOWANIE-JEZYKI-SKIP-2026-10-07.md
- docs/Plany/PLAN-13-REMEDIACJA-DOKUMENTACJI-REPO-2026-10-07.md
- docs/Plany/PLAN-14-MOTYW-QML-REGRESJA-2026-10-07.md

Liczba plików objętych indeksem: **510**.

- archive: 32
- audit: 23
- plans: 29
- root: 47
- screenshots: 17
- technical: 35
- tests: 259
- deployment: 5
- release: 2
- research: 2
- reports: 58
- inbox: 1

## Ostatnia korekta runtime — 2026-10-06

- GUI QML normalizuje ścieżki GGUF `file:///...` do lokalnych ścieżek przed uruchomieniem llama.cpp.
- Stan GUI pozostaje w `$HOME/.config/tlumacz/config.json`, a techniczny tuning llama.cpp w `$HOME/.config/tlumacz/llama.json` z fallbackiem `config/llama.json`.
- Świeże E2E GUI użyło endpointu `http://127.0.0.1:2782/v1`; techniczne ustawienia runtime pochodziły z `$HOME/.config/tlumacz/llama.json`; wynik Markdown został zapisany, a `translationFinished` potwierdził zakończenie tłumaczenia.

### Przycisk „Restartuj serwer” llama.cpp

Dla backendu llama.cpp przycisk `Restartuj serwer` jest operacją uruchomienia-oraz-restartu: gdy runtime nie istnieje lub nie działa, wywoływane jest uruchomienie serwera z bieżącą konfiguracją; gdy runtime działa, wykonywany jest restart.

## TPlugin / filtry Okapi

- `technical-docs/plugin-okapi-filter.md` — format, zależności A/B/C i architektura runtime `.tplugin`.
- `Plany/tworzenie-tplugin.md` — wewnętrzna metodologia produkcji pluginów.
- `wdrozenia/wdrozenie-tplugin.md` — plan migracji Filter Engine i stan pilota OpenXML.

## TPlugin lifecycle — 2026-10-06

- `TPluginInstaller.update()` — aktualizacja istniejącego pluginu z backupem poprzedniej wersji.
- `TPluginInstaller.uninstall()` — bezpieczne usunięcie wskazanego pluginu z zachowaniem rollbacku.
- `TPluginInstaller.rollback()` — przywrócenie poprzedniego stanu wraz z wymaganymi shared-libs.
- Macierz wszystkich 9 publicznych paczek: install → update → uninstall → rollback — PASS.
- `TODO-022m` — ZAMKNIĘTE.

## Paczki par językowych Apertium — 2026-10-06

- `technical-docs/apertium-pair-packages.md` — kanoniczny format pojedynczej paczki pary Apertium, builder, instalator, bezpieczeństwo, licencje i procedura tworzenia paczek przez użytkowników.
- `$HOME/.config/tlumacz/apertium/` — aktywny magazyn paczek użytkownika; w repozytorium reprezentatywne artefakty testowe znajdują się w `tests/fixtures/apertium/`.
- `src/tlumacz/backends/apertium/packages.py` — implementacja formatu transportowego i instalacji.
- `tests/test_apertium_packages.py` — testy TDD formatu i instalatora.

## Paczki Apertium i automatyzacja — 2026-10-06

- `technical-docs/apertium-pair-packages.md` — format pojedynczej paczki, dwukierunkowość, builder, instalator, CLI, kompilacja i czyszczenie.
- `technical-docs/apertium-pair-inventory-20261006.md` — audyt ściągniętych repozytoriów, gotowych kierunków i nieudanych kompilacji.
- `../tools/apertium/package_pairs.py` — pobieranie/kompilacja/pakowanie/checksumy/czyszczenie.
- `../tools/apertium/package_pipeline.py` — wewnętrzna logika wykrywania kompletnych kierunków i automatycznego budowania paczek; narzędzie nie należy do runtime.
- `technical-docs/tworzenie-paczek-jezykowych.md` — specyfikacja paczek Apertium i instrukcja użycia narzędzi `tools/apertium/`.
- `tests/fixtures/apertium/` — minimalny zestaw artefaktów używany przez smoke CI; produkcyjne paczki pozostają poza repozytorium, w magazynie użytkownika.

## TPlugin backend administracyjny — 2026-10-06

- `technical-docs/tplugin-administracja-pakiety.md` — niezależny backend przygotowywania paczek; CLI `init`, `validate`, `build`, `verify`, `inspect`, `test-install`, `publish`.
- `technical-docs/tplugin-reczne-tworzenie.md` — ręczne tworzenie paczek bez backendu.
- `TODO-TPLUGIN-004` — ZAMKNIĘTE.

- technical-docs/tworzenie-pluginow-okapi.md — kanoniczna instrukcja tworzenia pluginów Okapi z wykorzystaniem narzędzi TPlugin.
- technical-docs/tplugin-specyfikacja-reczne-tworzenie.md — aktualna specyfikacja TPlugin, narzędzia w tools/ i instrukcja ręcznego tworzenia.


## Katalog fizyczny dokumentacji — 2026-10-07

Dokumentacja została posegregowana według odpowiedzialności: `Audyt/`, `Plany/`, `technical-docs/`, `wdrozenia/`, `release/`, `research/`, `reports/`, `Testy/`, `Zrzuty/` oraz `archive/`. `docs/_inbox/` zawiera wyłącznie własny plik sterujący `AGENT.md`.

Pełny, maszynowy spis wszystkich plików znajduje się w `docs/INDEX.yml`. Indeks należy traktować jako źródło korelacji filesystemu z dokumentacją; po każdej zmianie struktury musi zostać ponownie wygenerowany.
