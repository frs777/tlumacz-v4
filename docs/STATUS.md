## 2026-10-08 — przywrócenie właściwego magazynu TPlugin

- Przywrócono właściwy kontrakt trwałego magazynu filtrów: `$HOME/.config/tlumacz/filters/`.
- `FilterStore.default_path()`, launcher FilterHost oraz narzędzia TPlugin używają ścieżki zgodnej z konfiguracją aplikacji; `XDG_CONFIG_HOME` wskazuje katalog nadrzędny `tlumacz/filters`.
- Zaktualizowano testy regresyjne dla domyślnej ścieżki, konfiguracji XDG oraz magazynu użytkownika.
- Skorygowano dokumentację techniczną i wdrożeniową, która błędnie opisywała `$HOME/.config/filters/` jako aktualny magazyn.
- Nie wprowadzono `$HOME/.config/filters/` jako drugiego magazynu.

## 2026-10-08 — dokumentacja przepływu Okapi

- Stan: przebudowa dokumentacji wykonana w katalogu `docs/technical-docs/tworzenie-pluginow-okapi/`.
- Źródło diagramów: `latex/main.tex` (TikZ).
- Dokument kanoniczny `tworzenie-pluginow-okapi.md` jest teraz stroną wejściową do katalogu.
- Zweryfikowano w kodzie aktywnym, że `PlainTextFilter` jest rejestrowany w `FilterRegistry`.
- PDF pozostaje poza aktywnym `FilterRegistry`.
- Preprocessing jest opisany po ekstrakcji jednostek; chunkowanie, executor, detekcja Lingua i rekonstrukcja mają osobne rozdziały.
## 2026-10-08 — normalizacja zapisu ścieżek użytkownika

- Ujednolicono zapis ścieżek użytkownika: aktywne repozytorium stosuje jawny zapis `$HOME/...` zamiast skrótowej notacji katalogu domowego.
- Dotyczy to kodu, konfiguracji, testów i dokumentacji.
- Nie zmieniono znaczenia ścieżek XDG: warstwy runtime nadal używają `${XDG_CONFIG_HOME:-$HOME/.config}` lub odpowiednika w Pythonie.

## 2026-10-08 — usunięcie odniesień do skilli środowiska agenta z dokumentacji

- Usunięto z dokumentacji projektu bezpośrednie ścieżki do skilli środowiska agenta, w tym przykład reprodukcyjny oraz historyczne źródła procesu budowania Windows.
- Opisy zachowują informację o roli pliku/skilla, ale nie ujawniają ścieżek infrastruktury środowiska agenta.
- Nie zmieniono właściwych odniesień do skilli aplikacji Tłumacz przechowywanych w `$HOME/.config/tlumacz/skills/`.

## 2026-10-07 — naprawa discovery Apertium w GUI dla magazynu TAR-only

- `QmlApplicationBridge` nie skanuje już bezpośrednio magazynu `$HOME/.config/tlumacz/apertium` jako katalogu rozpakowanych pluginów. Korzysta z `discover_supported_pairs_from_store()`, który materializuje archiwa TAR wyłącznie do tymczasowego workspace i usuwa workspace po discovery.
- Zachowano obsługę jawnie wskazanego katalogu z rozpakowanymi pluginami dla integracji/systemowych instalacji; domyślny magazyn użytkownika pozostaje TAR-only.
- `bundled.py` nie traktuje już `native_runtime/share/apertium` jako źródła danych językowych; bundlowany runtime dostarcza wyłącznie executable.
- Usunięto również nieaktualny komentarz w `runtime.py` odwołujący się do starego `share/apertium`.
- Dodano regresję GUI potwierdzającą odkrywanie par z rzeczywistego archiwum `.tar` bez tworzenia trwałego katalogu pakietu w magazynie.
- Weryfikacja ukierunkowana po zmianie: **33 passed** (`runtime`, `bridge`, `packages`, `language_plugins`).

## 2026-10-07 — CI zsynchronizowane z Apertium TAR-only

- Usunięto z `.github/workflows/quality-gate.yml` historyczny kontrakt wymagający `eng-pol.mode`, `eng-pol.t1x.bin` i `eng-pol.autogen.bin` wewnątrz wheel.
- Wheel Audit sprawdza obecnie bundlowany executable runtime i explicite odrzuca dane językowe oraz archiwa par językowych w wheel.
- Product smoke CI korzysta z rzeczywistego artefaktu `tests/fixtures/apertium/apertium-eng-pol-1.0.0.tar` + `.sha256` w izolowanym magazynie użytkownika; testy lokalne domyślnie wskazują `$HOME/.config/tlumacz/apertium`.
- Weryfikacja lokalna po zmianie: **YAML parse PASS; wheel TAR-only audit PASS; clean-install Apertium TAR smoke PASS**.
- Kod produkcyjny bez zmian.

## 2026-10-07 — kolejny błąd test suite: test równoległości QML dla llama.cpp

- Pierwszy błąd po B6: `tests/test_cloud_parallel_guard.py::test_non_cloud_translation_keeps_configured_parallelism`.
- Przyczyna: test zakładał domyślny tryb obliczeń, podczas gdy konfiguracja środowiska mogła ustawić CPU. Aktualny kontrakt jest jednoznaczny: `llama.cpp` na CPU działa seryjnie (`effective_translation_parallel == 1`), natomiast dla GPU zachowuje skonfigurowany poziom równoległości.
- Test został doprecyzowany przez jawne ustawienie `set_compute_mode("gpu")`; osobny test CPU nadal chroni kontrakt seryjnego wykonywania.
- Nie zmieniano kodu produkcyjnego.
- Weryfikacja ukierunkowana: **4 passed in 1.43s**.
- Następny krok: ponownie uruchomić pełny suite z `-x` i zatrzymać się na pierwszym kolejnym błędzie.

## 2026-10-07 — kolejny błąd test suite: test bundlowanego runtime'u Apertium

- Pierwszy błąd po B5: `tests/test_apertium_runtime.py::test_bundled_runtime_contains_language_data_for_release`.
- Przyczyna była nieaktualna nazwa i założenie testu: aktualny release rozdziela bundlowany executable od danych językowych, które są dostarczane jako paczki użytkownika TAR-only. Bez izolacji test widział 28 paczek z rzeczywistego magazynu użytkownika.
- Test zmieniono na `test_bundled_runtime_has_no_language_data_without_installed_packages` i odizolowano przez tymczasowy `XDG_CONFIG_HOME`.
- Nie zmieniano kodu produkcyjnego.
- Weryfikacja ukierunkowana: **1 passed in 0.78s**.
- Następny krok: ponownie uruchomić pełny suite z `-x` i zatrzymać się na pierwszym kolejnym błędzie.

## 2026-10-07 — kolejny błąd test suite: discovery runtime Apertium

- Pierwszy błąd po B4: `tests/test_apertium_runtime.py::test_runtime_discovers_only_bundled_runtime`.
- Przyczyna: test nie izolował domyślnego magazynu paczek. `ApertiumRuntime.discover()` zgodnie z aktualnym modelem TAR-only materializował dostępne paczki z rzeczywistego magazynu użytkownika, przez co `language_pairs()` zwracało 24 realne kierunki zamiast dwóch kierunków fake runtime'u.
- Nie zmieniano kodu produkcyjnego. Test został dostosowany do aktualnego kontraktu przez ustawienie tymczasowego `XDG_CONFIG_HOME`.
- Weryfikacja ukierunkowana: **1 passed in 1.37s**.
- Następny krok: ponownie uruchomić pełny suite z `-x` i zatrzymać się na pierwszym kolejnym błędzie.

## 2026-10-07 — synchronizacja testu E2E DOCX z TAR-only

- Test `test_real_apertium_document_translation_produces_valid_final_docx` dostosowano do aktualnego modelu magazynu TAR-only.
- Test tworzy izolowany tymczasowy `XDG_CONFIG_HOME`, kopiuje `apertium-eng-pol-1.0.0.tar` oraz checksum i dopiero uruchamia `TranslationApp`.
- Zachowano rzeczywisty przepływ tłumaczenia DOCX przez Apertium oraz walidację końcowego archiwum DOCX, w tym `word/document.xml`, przetłumaczone `Świat` i zachowanie `word/media/resource.bin`.
- Weryfikacja testu: **1 passed in 3.14s**.
- Następny krok: ponownie uruchomić pełny suite z `-x` i zatrzymać się na pierwszym kolejnym błędzie.

## 2026-10-07 — synchronizacja testu E2E `TranslationApp` z TAR-only

- Test `test_translation_app_uses_bundled_apertium_for_real_eng_pol_runtime` dostosowano do aktualnego magazynu paczek Apertium.
- Test tworzy izolowany tymczasowy magazyn `XDG_CONFIG_HOME`, kopiuje do niego `apertium-eng-pol-1.0.0.tar` oraz checksum i dopiero uruchamia `TranslationApp`.
- Zachowano rzeczywiste tłumaczenie `Hello world.` przez bundlowany runtime Apertium oraz asercję wyniku zawierającego `Świat`.
- Weryfikacja: **1 passed in 1.33s**.

## 2026-10-07 — synchronizacja testu `test_apertium_pair_repairs.py`

- Zaktualizowano `tests/test_apertium_pair_repairs.py`, aby test nie zależał od usuniętego katalogu `Aperitium/`.
- Test odczytuje `apertium-eng-pol.pol-eng.t3x` bezpośrednio z aktualnego artefaktu `apertium-pol-eng-1.0.0.tar` z magazynu paczek testowych/użytkownika.
- Zachowano dotychczasową intencję regresji: obecność atrybutów `a_SN`, `PDET`, `gen` oraz `mp` w definicji transferu.
- Weryfikacja: **1 passed in 0.81s**.
- Drugi test Apertium z audytu został tym samym zsynchronizowany z modelem TAR-only.

## 2026-10-07 — synchronizacja testu Apertium z modelem TAR-only

- Zastąpiono przestarzały test `test_bundled_runtime_discovers_and_translates_eng_pol_without_external_environment` testem `test_bundled_runtime_discovers_and_translates_installed_tar_pair`.
- Test odpowiada aktualnemu kontraktowi: prywatny executable Apertium pozostaje bundlowany w `native_runtime`, natomiast para `eng-pol` jest dostarczana jako `.tar` + `.tar.sha256` z magazynu paczek i materializowana do katalogu tymczasowego.
- Test jest izolowany: kopiuje rzeczywisty artefakt `apertium-eng-pol-1.0.0.tar` wraz z checksumem ze skonfigurowanego źródła paczek do tymczasowego magazynu przez `XDG_CONFIG_HOME`.
- Weryfikacja: **1 passed**.
- W efekcie rozbieżność pierwszego testu Apertium z audytu została zamknięta. Pozostaje drugi test Apertium wymagający synchronizacji (`test_apertium_pair_repairs.py`).

## Raport audytu integracyjnego — 2026-10-07

Po pełnym audycie projektu wykonano świeżą weryfikację `PYTHONPATH=src python3 -m pytest -q tests`: **591 passed, 9 failed**. Wynik ten zastępuje wcześniejsze, historyczne liczby testów w kontekście bieżącego audytu.

Zidentyfikowane rozbieżności:
- 6 testów packaging/QML odwoływało się do głównego `pyproject.toml`; podczas audytu plik był nieobecny w katalogu głównym, ponieważ został wcześniej przypadkowo przeniesiony. **Pyproject został przywrócony do właściwej lokalizacji**; blocker braku root `pyproject.toml` należy traktować jako usunięty po przywróceniu.
- 2 testy Apertium (`test_apertium_backend.py`, `test_apertium_pair_repairs.py`) nadal odzwierciedlają starszy model dystrybucji/ścieżek i wymagają synchronizacji z aktualnym modelem TAR-only.
- 1 test warstwy dokumentowej zakłada jeden request dla całego dokumentu Markdown, podczas gdy aktualny kontrakt wykonawczy przewiduje jeden batch request na logiczny chunk.

Niezależnie od czerwonego pełnego suite, rzeczywisty runtime Apertium został zweryfikowany w środowisku użytkownika: wykryto 28 par językowych, wykonano rzeczywiste `eng → pol`, a `tests/test_apertium_e2e_documents.py` zakończył się wynikiem **4 passed**.

Dodatkowe ustalenia audytu: w kodzie pozostają hardcoded ścieżki `/home/frs` w `filter_store.py` i `filter-host/run.sh`; deklarowane minimum PySide6 `>=6.5` jest niższe niż wymaganie używanego `QStyleHints.setColorScheme()/unsetColorScheme()` (API od Qt 6.8). Plan 14 dotyczący realnego gate KDE pozostaje otwarty.

**Status audytu:** projekt nie jest jeszcze gotowy do końcowego zamknięcia/release gate. Po przywróceniu `pyproject.toml` kolejnym krokiem powinien być ponowny pełny pytest i zatrzymanie przy pierwszym nierozwiązanym błędzie.

## 2026-10-07 — ujednolicenie magazynu filtrów

- Jedyny trwały magazyn pakietów filtrów: `/home/frs/.config/tlumacz/filters`.
- Usunięto architekturę `$HOME/.config/tlumacz/filter-engine/plugins` oraz trwały `shared-libs`.
- `.tplugin` jest pakietem przechowywanym w magazynie użytkownika; rozpakowanie następuje wyłącznie do `/tmp/filters/` na czas pracy aplikacji.
- Wspólne biblioteki Okapi są w `src/tlumacz/resources/okapi-runtime/lib/`.
- Aktywne wejściowe pakiety Okapi: `epub`, `json`, `openoffice`, `openxml`, `yaml`. HTML i Markdown pozostają natywne.
- XLIFF nie jest wejściowym filtrem; wewnętrzna implementacja XLIFF 2.0 znajduje się w `src/tlumacz/documents/xliff.py`.
- Usunięto `dist/tplugins/` i `build/tplugins/`.
- Wykonano backup przed zmianą: `backups/filter-store-unification-20261007/pre-change.tar.gz`. SHA-256: `8682f0b0033bb89c2d52476fd46e2afcb39ce3f6ceed167b75b2e252b593e6b8`.

## 2026-10-07 — usunięcie nadmiarowych danych językowych z bundlowanego runtime'u

Usunięto duplikaty paczek językowych z `src/tlumacz/backends/apertium/native_runtime/share/apertium/`. W tym miejscu nie ma już rozpakowanych paczek ani katalogu `modes`; dane językowe są przechowywane wyłącznie w `/home/frs/.config/tlumacz/apertium/` jako nowe artefakty `.tar` + `.tar.sha256`. Przed usunięciem wykonano backup `backups/apertium-language-data-removal-before-20261007-184817.tar.gz` (SHA-256: `95b4de4a743715dac4500f3232342942e15fd38075feb02c18f8f0baeb2eda42`).

## 2026-10-07 — Apertium: magazyn TAR-only i tymczasowa materializacja

Skorygowano model paczek językowych zgodnie ze specyfikacją: .tar jest jedynym trwałym artefaktem przechowywanym w $HOME/.config/tlumacz/apertium/. Aplikacja nie instaluje już paczek do trwałych katalogów apertium-<pair>/. Przed użyciem prywatnego runtime'u weryfikuje .tar.sha256 i materializuje zawartość paczek w tymczasowym katalogu roboczym poza magazynem.

Wprowadzono regresje TDD dla TAR-only oraz przepięto testy runtime na magazyn archiwów. Weryfikacja ukierunkowana: 21 passed; compileall: PASS; Ruff po formatowaniu: PASS.

Backup przed zmianą: backups/apertium-tar-only-before-20261007-183228.tar.gz.

## 2026-10-07 — porządkowanie listy operacyjnej i dalsze logowanie

- **Apertium:** ustalono docelowy sposób dystrybucji: runtime jest dostarczany razem z kodem źródłowym aplikacji V4; nie jest potrzebna osobna procedura pobierania. Mały artefakt może być bezpośrednio wbudowany w zasoby aplikacji. Inventory licencji/NOTICE/source pozostaje dokumentacją dystrybucyjną.
- Pozostałe punkty omawianej listy operacyjnej użytkownik uznaje za zrealizowane; nie są ponownie otwierane. FastAPI/OpenVINO pozostają wycofane. `llama.cpp` i ZenDNN nie są częścią tej pracy.
- Centralne logowanie rozszerzono o granice `DocumentTranslationService`, `TranslationOrchestrator`, transport Cloud, transport llama.cpp oraz adapter Apertium.
- Logi pozostają szczegółowe (`DEBUG`), komunikaty aplikacyjne są po polsku, a redakcja sekretów obejmuje także wyjątki/tracebacki. Nie loguje się treści dokumentów, payloadów ani nagłówków autoryzacyjnych.
- Backup przed integracją loggerów: `backups/20261007-logging-integration-pre/logging-integration-pre.tar.gz`; SHA-256 `cfd9de9ce38edf6e3b62e0db6d42205a52715a8e71bd585dbc480e1e502c809c`.
- Świeża pełna weryfikacja po zmianach: **592 passed, 0 failed**; `compileall` i Ruff dla zmienionych plików: PASS.

---

## 2026-10-07 — konfiguracja logowania V4

Wdrożono pierwszy etap centralnego logowania aplikacji:
- logger `tlumacz` zapisuje logi do `$HOME/.config/tlumacz/logs/tlumacz.log` oraz na konsolę;
- poziom domyślny pozostaje `DEBUG`, bez ograniczania diagnostyki wersji testowej;
- format logów jest jednolity, a komunikaty dodawane przez V4 są po polsku;
- `SecretRedactionFilter` usuwa sekrety z komunikatów, struktur danych, nagłówków autoryzacyjnych, parametrów URL oraz wyjątków/tracebacków;
- `SecretStore` automatycznie rejestruje wartości sekretów w mechanizmie redakcji przy odczycie i zapisie;
- uruchomienie GUI korzysta z centralnej konfiguracji logowania i zapisuje komunikaty startu/błędu po polsku;
- dodano testy TDD dla redakcji sekretów, wyjątków, konfiguracji DEBUG i rejestracji sekretów w trakcie działania.

Status TODO-011: **ZAMKNIĘTE — 2026-10-07**. Centralne logowanie jest podłączone do kluczowych granic backendów i pipeline'u; szczegółowy poziom `DEBUG` pozostaje aktywny. Backup: `backups/20261007-logging-pre/logging-pre.tar.gz` (SHA-256 `24dc4db8a3e5229a869250228a2b3df68fbc73b232ac3a9843d790cea70e1c93`).

---

## 2026-10-07 — Markdown: natywna ścieżka tekstowa bez Okapi

- Markdown korzysta bezpośrednio z natywnego MarkdownFilter.
- Plugin Okapi Markdown został usunięty z aktywnego zestawu filtrów.
- FilterRegistry chroni .md i .markdown przed przejęciem przez plugin Okapi.
- test rejestru: 17 passed.
- Backup: backups/markdown-native-20261007-155201/pre-change.tar.gz.
- SHA-256: 04118914c9e86955e20c12db69eb7cc3f8a27a09201dcc54ea58da335bb01a29.

## 2026-10-07 — końcowa walidacja etapu rozszerzalności backendów

Świeży pełny suite po zakończeniu implementacji zakończył się wynikiem **573 passed**. Kierunkowe testy backendów/aplikacji/GUI oraz test E2E TestBackend również przechodzą.

Weryfikacja statyczna: Ruff PASS dla zmienionych modułów i testów; compileall PASS.

Etap rejestru, wydzielenia custom, separacji konfiguracji oraz dowodu E2E można uznać za zweryfikowany. Pozostaje dalsza realizacja planu poza tym etapem.
## 2026-10-07 — PLAN-14: stan naprawy regresji motywu QML

- dark/light: natywny QStyleHints jest preferowany; gdy Qt/Fusion nie zmienia rzeczywistej palety, działa ograniczony fallback pełnej palety Fusion.
- system: bez fallbacku; unsetColorScheme() + reset QPalette() przywracają natywną paletę.
- Regresja TDD dla rzeczywistej palety: RED potwierdzony przed implementacją, następnie GREEN.
- tests/test_qml_gui.py: 157 passed.
- compileall: PASS.
- qmllint src/tlumacz/qml_gui/*.qml: PASS.
- Pełny suite po synchronizacji testu: 573 passed; test czasu został dopasowany do aktualnego TranslationPage.qml.
- Rzeczywisty gate KDE pozostaje otwarty z powodu ograniczenia sesji SentinelX; nie traktujemy offscreen/Xvfb jako substytutu.

Backup: backups/20261007-theme-regression-pre-fix/theme-regression-pre-fix.tar.gz.

---

## 2026-10-07 — pełny dowód rozszerzalności backendu

Dodano test E2E TestBackend przechodzący przez TranslationApp, DocumentTranslationService, DocumentProcessor, TranslationOrchestrator, BackendRegistry i writer dokumentu TXT. Wynik: **6 passed** dla pełnego pliku testowego rozszerzalności.

Łączny zestaw kierunkowy backendów, aplikacji i GUI: **64 passed, 139 deselected**. Ruff dla zmienionych modułów i testów: PASS; compileall: PASS.

Do formalnego zamknięcia etapu pozostaje wynik świeżego pełnego suite.
## 2026-10-07 — wynik końcowej walidacji etapu konfiguracji backendów

Po migracji wszystkich referencji starego API świeży pełny suite zakończył się wynikiem **571 passed, 1 failed**. Jedyny failure dotyczy istniejącego testu GUI `test_translation_page_displays_translation_time_as_minutes_and_seconds` i nie dotyczy konfiguracji backendów. Testy kierunkowe rozszerzalności/backendów/GUI po migracji: **28 passed**.

Ruff dla zmienionych modułów: PASS. `compileall`: PASS.

## 2026-10-07 — odseparowanie konfiguracji backendów

Kontynuacja wdrożenia rozszerzalności backendów:
- BackendRequest i BackendSelection zostały ograniczone do pól backend + BackendConfiguration;
- dodano domenowy kontener BackendConfiguration dla konfiguracji specyficznej dla implementacji;
- usunięto z wspólnego kontraktu pola provider/base_url/api_key/model/engine/timeout/compute_mode/chat_template/parallel;
- GUI, TranslationApp i adaptery backendów przekazują konfigurację przez BackendConfiguration;
- dodano testy regresyjne wymuszające brak backend-specific pól w BackendRequest i BackendSelection;
- testy kierunkowe po zmianie: **27 passed**;
- Ruff i compileall dla zmienionych modułów: PASS.

Backup etapu: backups/20261007-backend-config-pre/.
## 2026-10-07 — wdrożenie rozszerzalnego rejestru backendów i wydzielenie „Własny”

Zrealizowano główną część planu rozszerzalności backendów.

- BackendRegistry został przebudowany na rejestr instancji i adapterów; z metody translate() usunięto routing zależny od nazw konkretnych backendów.
- Dodano register() oraz możliwość wstrzyknięcia backendów przez konstruktor.
- Dodano BackendCapabilities i API capabilities(), aby możliwości backendu były dostępne bez znajomości jego implementacji.
- Zachowano kompatybilność z dotychczasową listą aktywnych backendów, w tym obecność llama przed konfiguracją runtime.
- Backend „Własny” został wydzielony do src/tlumacz/backends/custom/backend.py. Jest niezależnym backendem dla własnych lokalnych/zdalnych serwerów OpenAI-compatible.
- Custom współdzieli transport OpenAICompatibleProvider z Cloud, ale nie jest providerem Cloud i nie korzysta już z CloudRouter jako specjalnego przypadku routingu.
- Dodano TestBackend jako test rozszerzalności; przechodzi on przez rejestr bez zmian w pipeline dokumentowym.
- Nie zmieniano FilterRegistry/Okapi.

Weryfikacja kierunkowa po zmianie: **18 passed**.

Backup przed refaktorem: backups/20261007-backend-extensibility-pre/src oraz odpowiadające kopie dokumentacji i testów.
## 2026-10-07 — FilterRegistry: Okapi jako primary nad native fallbackiem

Zrealizowano wymagania z `instrukcja-okapi.md` dotyczące kolejności inicjalizacji i przejmowania rozszerzeń przez pluginy Okapi.

- Registry nadal rejestruje natywne filtry jako fallback.
- Discovery TPlugin nie odrzuca już rozszerzeń tylko dlatego, że są zajęte przez native fallback.
- `register_lazy()` pozwala pluginowi Okapi przejąć istniejący suffix native.
- Plugin może przejąć tylko część wspólnych rozszerzeń, a pozostałe rozszerzenia z manifestu nadal są rejestrowane.
- XLIFF zachowuje dotychczasowe specjalne fabryki wersji, ponieważ wymaga to osobnego kontraktu dokumentowego.

Testy: `tests/test_filter_registry.py` — **17 passed**; skoncentrowany gate Okapi/TPlugin — **47 passed**.
Backup: `backups/okapi-filter-engine-20261007/pre-instrukcja-okapi-20261007-144400.tar.gz`.
SHA-256: `7c4290ee5244a3e606f87dede28547249920fa1c9b9ba4a832270d8f60c70d4c`.

---

## 2026-10-07 — rozdzielenie prostych formatów tekstowych od Okapi

Markdown, Plain Text i HTML zostały skierowane na natywne filtry V4. `.md`/`.markdown` korzystają z `MarkdownFilter`, `.txt`/`.text`/`.log` z `PlainTextFilter`, a `.html`/`.htm`/`.xhtml` z `HtmlFilter`. Te formaty nie uruchamiają Java Filter Host ani Okapi. Formatów strukturalnych zapisanych tekstowo (np. JSON/YAML/CSV) nie przeniesiono automatycznie do filtra liniowego; wymagają własnego kontraktu strukturalnego.


## 2026-10-07 — rozdzielenie runtime Apertium od paczek językowych

Runtime Apertium 3.9.12 pozostaje bundlowany w src/tlumacz/backends/apertium/native_runtime/, ale pary językowe nie są już traktowane jako część tego runtime'u. Docelowym magazynem artefaktów dystrybucyjnych jest $HOME/.config/tlumacz/apertium/.

Aplikacja skanuje magazyn pod kątem apertium-<source>-<target>-<version>.tar, wymaga odpowiadającego .tar.sha256, weryfikuje SHA-256 całego archiwum i materializuje paczki wyłącznie do tymczasowego katalogu roboczego przed discovery. Magazyn użytkownika pozostaje TAR-only; archiwum .tar jest właściwym i jedynym trwałym artefaktem dystrybucyjnym.

Weryfikacja na kopii magazynu użytkownika: 28 archiwów → 28 instalacji → 28 wykrytych kierunków. Rzeczywiste tłumaczenie Hello world. przez eng-pol zakończyło się wynikiem @hello #Świat. z Apertium 3.9.12. Testy TDD zmiany: 26 passed dla paczek/runtime/bridge.

## 2026-10-07 — wydzielenie Preprocessora przed Filter Engine

Preprocessor został przeniesiony z `src/tlumacz/filter_engine/preprocessor.py` do niezależnego pakietu `src/tlumacz/preprocessing/`. `DocumentProcessor` wykonuje `preflight()` przed `FilterRegistry.for_path()`, a po `extract()` wywołuje `classify_units()` dla decyzji `TRANSLATE/KEEP`. Preprocessor nie importuje kontraktu ani implementacji filtra.

`KEEP` nadal nie trafia do backendu, zachowuje tekst źródłowy 1:1 i kolejność jednostek. Ochrona inline-code pozostaje poza Preprocessorem.

Weryfikacja kierunkowa: **13 passed** (`tests/test_preprocessor.py`, `tests/test_filter_processor.py`). Pełny suite po wdrożeniu: **577 passed in 106.77s**. `ruff` dla zmienionych plików: PASS. `compileall`: PASS. Granica pakietów: stary moduł `filter_engine/preprocessor.py` nie istnieje, a repozytorium nie zawiera już importów produkcyjnych z tej ścieżki. Backup: `backups/20261007-preprocessor-refactor-pre/preprocessor-refactor.tar.gz`.

## 2026-10-07 — wdrożenie wspólnego preprocessingu skip/keep

Rozpoczęto realizację uzupełnienia PLAN-12 od wspólnego kontraktu preprocessingu. Dodano src/tlumacz/filter_engine/preprocessor.py z jawnymi decyzjami translate/keep. DocumentProcessor wykonuje klasyfikację po ekstrakcji jednostek i przed backendem; jednostki keep nie trafiają ani do ścieżki jednostkowej, ani batchowej i wracają do writera z oryginalnym tekstem.

Wzorce V3 zostały przeniesione semantycznie, z ograniczeniem --- do Markdown, aby nie narzucać składni Markdown innym formatom. Ochrona inline markerów pozostaje osobnym mechanizmem placeholderów.

Weryfikacja: 23 passed w regresjach preprocessora/Filter Engine/chunkowania/ochrony inline; Ruff PASS; compileall PASS.

Pozostają niezrealizowane etapy: pełna wspólna ochrona struktur formatowych, usunięcie lokalnych obejść filtrów, GUI raportowania z nowego kontraktu, pełna regresja oraz rzeczywisty E2E TranslateGemma CPU.
## 2026-10-07 — produkcyjna ścieżka Markdown i raportowanie pominięć

Usunięto rozbieżność między testowanym `MarkdownFilter` a rzeczywistą ścieżką `FilterRegistry`: manifest pluginu `markdown` nadal dostarcza rozszerzenia, ale rejestr rozwiązuje go do Pythonowego `MarkdownFilter`, który faktycznie rejestruje nagłówki, tekst oznaczony składnią Markdown, fenced code i front matter jako pominięte fragmenty. Dzięki temu komunikat `Ominięto N fragmentów` korzysta z tej samej klasyfikacji, która obowiązuje podczas ekstrakcji, zamiast raportować `0` dla produkcyjnego filtra Okapi Markdown.

## 2026-10-07 — propozycja ścieżki pliku wynikowego

Naprawiono zachowanie GUI po wyborze pliku wejściowego. Automatyczna ścieżka wyniku jest tworzona jako ta sama lokalizacja i nazwa bazowa z przyrostkiem `_KOD_JĘZYKA` przed rozszerzeniem, np. `test.md` → `test_pl.md`. Kolejny wybór pliku aktualizuje automatyczną propozycję; ręcznie ustawiona ścieżka wyniku przestaje być automatycznie nadpisywana.

## 2026-10-07 — stabilizacja detekcji języka i statystyk GUI

- `LlamaCppLanguageRouting` ustala język źródłowy na podstawie całego dokumentu zamiast wykrywać go osobno dla każdej krótkiej jednostki Markdown. Dzięki temu krótkie nagłówki/linie nie mogą sztucznie rozbijać dokumentu na chunki tylko przez szum detektora.
- Przed detekcją usuwane są fragmenty w podwójnych cudzysłowach `"..."`, aby cytat w obcym języku nie zmieniał rozpoznanego języka dokumentu.
- Dla aktywnego llama.cpp wszystkie jednostki dokumentu otrzymują jeden ustalony source language; nadal obowiązuje limit znaków `chunk_size`, więc rzeczywiście długi dokument może zostać podzielony wyłącznie przez budżet planera.
- Dla dokumentu około 2 tys. znaków i jednego języka mechanizm nie tworzy sztucznych granic wynikających z detekcji per jednostka.
- Statystyki GUI pokazują czas i bieżącą prędkość w jednym formacie; cyfry czasu/prędkości są o 1 px większe od bazowego fontu i pogrubione. Prędkość jest prezentowana jako pojedyncza wartość `znaki/s`, bez formatu `bieżąca/średnia`.
- Backup przed zmianą: `backups/20261007-122210-ui-language-routing/pre-change.tar.gz`, SHA-256 w `SHA256SUMS`.
- Weryfikacja: `tests/test_language_routing.py` — **10 passed**; regresja QML statystyk — **1 passed**.

## 2026-10-07 — poprawka retry całego chunka i integralności wyników

W `TranslationOrchestrator` nieudany batch jest ponawiany jako cały logiczny chunk jeden raz. Dopiero po drugiej nieudanej próbie następuje kontrolowany fallback do tłumaczenia jednostkowego. Dodano twardą kontrolę unikalności identyfikatorów jednostek oraz zakaz zwracania częściowego wyniku, jeżeli jakakolwiek jednostka pozostała bez rezultatu.

Regresje obejmują retry całego chunka, przejście do fallbacku dopiero po dwóch nieudanych próbach batcha, zachowanie kolejności, błędy jednostkowe oraz duplikaty ID.

Weryfikacja po zmianie: testy kierunkowe `22 passed`; `compileall` i Ruff dla zmienionych plików — PASS; pełny suite `537 passed` w 96,77 s. Brak regresji.

## 2026-10-07 — Filter Engine / Okapi: ochrona inline codes i lifecycle

Zdiagnozowano i naprawiono dwie klasy problemów przekazanych w `reports/handoff-agent-okapi-filter-engine.md`.

- Reprodukcja README: 37 jednostek, 18 jednostek z inline codes, 72 wystąpienia kodów; aktualny Okapi extract oraz identity merge przechodzą.
- Potwierdzono lukę: PUA Okapi były przekazywane bezpośrednio do backendu tłumaczeniowego.
- Dodano inline_code_protection.py: PUA → __OKAPI_CODE_N__ przed backendem oraz ścisłe restore po odpowiedzi.
- Brak, duplikat lub przestawienie markera kończy przepływ błędem; brak automatycznego odtwarzania markera.
- Cache przechowuje wynik po przywróceniu PUA, a klucz pozostaje oparty na oryginalnym tekście.
- Reader threads Filter Host zmieniono z daemon na non-daemon; close() nadal wymusza zakończenie procesu i join obu czytników.
- Weryfikacja: 7 testów ochrony markerów/cache, 8 testów protokołu, 30 testów skoncentrowanego Filter Engine; pełny pytest 533 passed.
- Rzeczywisty backend llama.cpp był niedostępny podczas tej sesji (connection refused), dlatego raw request/response nie został sfałszowany ani uznany za potwierdzony.
- Pełny gate Qt/PySide6 pozostaje do świeżej weryfikacji; nie oznaczono SIGABRT jako definitywnie zamkniętego bez tej weryfikacji.

Backup przed zmianą: backups/okapi-filter-engine-20261007/pre-fix.tar.gz
SHA-256: 1c3edfad290f714c6fdbfee3be92fbf6c936f8ef9b4fba9a1cf1100fc7a9c533

---
## 2026-10-07 — unifikacja mechanizmu startu llama.cpp w GUI

- Usunięto rozproszone wywołania startu/restartu llama.cpp z przepływów GUI.
- Jeden mechanizm `_request_llama_server()` obsługuje start, restart oraz akcję oczekującą na gotowość serwera.
- `start_translation()` nie próbuje już rozpoczynać tłumaczenia równolegle z asynchronicznym startem llama.cpp. Rejestruje callback i uruchamia właściwy przepływ tłumaczenia dopiero po zakończeniu operacji serwera.
- Restart llama.cpp po tłumaczeniu oraz przycisk restartu korzystają z tego samego mechanizmu.
- Bezpośrednie `core.start_llama()` pozostaje wyłącznie w jednym wewnętrznym mechanizmie operacji serwera.
- Dodano regresję potwierdzającą, że tłumaczenie czeka na sygnał gotowości llama.cpp.
- Backup przed zmianą: `backups/20261007-090812-llama-start-unification-targeted/pre-change.tar.gz`, SHA-256 `ec6e634072e074650b7d6eeb551e96c6d60f2f3bccbf25def8556ef71189a517`.
- Weryfikacja: `tests/test_qml_gui.py` — **153 passed**; Ruff — **PASS**; `compileall` — **PASS**.

## 2026-10-07 — wdrożenie batchowego chunkowania TranslateGemma i mechanizmu skip

Wdrożono PLAN-12. V4 nie wykonuje już osobnego requestu dla każdej jednostki w logicznym chunku: `TranslationExecutor.execute_batch()` przekazuje chunk do `LlamaCppAdapter.translate_batch()`. Batch używa markerów `⟦TG_SEG_N⟧`, waliduje kompletność i kolejność, wykonuje jedną próbę naprawczą, a po drugim błędzie przechodzi do fallbacku jednostkowego.

`ChunkPlanner` otrzymał metadane strukturalne oraz regułę 60% przed nagłówkiem z V3. Granica zmiany języka źródłowego tworzy osobny chunk. `MarkdownFilter` przekazuje typ `heading`/`paragraph`.

Mechanizm skip został rozszerzony o YAML front matter i linie metadanych `name:`, `license:`, `author:`, `metadata:`, `version:`, `tags:`, `created:`, `updated:`. Pominięte fragmenty nie trafiają do backendu i pozostają w dokumencie bez zmian.

Normalizacja TranslateGemma obsługuje warianty regionalne `xx-YY`/`xx_YY`; `auto` nie jest wysyłane do modelu.

Weryfikacja: **42 testy ukierunkowane PASS**, Ruff PASS, `py_compile` PASS. Rzeczywisty E2E z aktywnym llama.cpp/TranslateGemma pozostaje do wykonania przez użytkownika.

- Bazowy pomiar CPU: pojedynczy request TranslateGemma `Hello world.` do aktywnego `29710` zakończył się w 15,49 s; prompt 35 tokenów ewaluował się 8,16 s, a 5 tokenów generowało się 7,01 s (~0,57 tokena/s).
- Większy request testowy nie zakończył się w limicie 60 s.
- Potwierdzone dwa składniki opóźnienia: wolna inferencja CPU oraz 17 osobnych requestów dla jednego logicznego chunka.

## 2026-10-07 — status diagnostyki wydajności TranslateGemma CPU

Stan po diagnostyce SentinelX:

- aktywny runtime Tłumacza: bundled llama.cpp na porcie `29710`, CPU, efektywne `parallel=1`;
- `/health` działa, a `/slots` pokazuje jeden slot;
- dokument testowy ma 2228 B, filtr Markdown tworzy 17 jednostek i 905 znaków źródłowych;
- planner tworzy 1 chunk przy `chunk_size=4000`;
- executor wykonuje jednak 17 oddzielnych wywołań backendu, po jednym na jednostkę;
- potwierdzony problem: kontrakt „chunk” nie jest kontraktem „request”;
- dodatkowy czynnik wydajnościowy: około 34 GiB użytego swapu przy 47 GiB dostępnego swapu w chwili pomiaru.

To jest etap diagnostyczny. Nie wprowadzono jeszcze zmiany kodu agregującej jednostki do jednego requestu. Taka zmiana wymaga osobnego TDD i backupu.

## 2026-10-07 — naprawa izolacji magazynu sekretów profili Cloud

- Naprawiono regresję `test_qml_bridge_switches_cloud_profiles_without_secret_leakage`: rekonstruowany `QmlApplicationBridge` otrzymuje jawnie ten sam `secret_path` co bridge zapisujący profile.
- Przyczyna była w teście: pierwszy bridge używał tymczasowego `SecretStore`, a rekonstruowany bridge bez `secret_path` odczytywał domyślny `$HOME/.config/tlumacz/.key`, gdzie istniał wpis `SERVICE/local`.
- Nie zmieniano produkcyjnego `bridge.py`, ponieważ implementacja prawidłowo rozdziela sekrety przez `SERVICE/<nazwa_usługi>` i nie ma fallbacku Cloud → `local`.
- Backup przed zmianą: `backups/SECRET-PROFILE-ISOLATION-BEFORE-2026-10-07.tar.gz`, SHA-256 `0e744e95b0b77498e656ea584cbd690093bfe356ddab97ab896e346311a12818`.
- Weryfikacja skoncentrowana: `tests/test_cloud_secrets.py` + `tests/test_gui_i18n.py` — **14 passed**.
- Rozszerzono regresje: test bridge'a zapisuje również osobny sekret `local` i potwierdza, że nie wraca on do profilu Cloud; test `SecretStore` potwierdza niezależne wpisy `SERVICE/ChatGPT`, `SERVICE/Codex` i `SERVICE/local`.
- Test zapisu konfiguracji potwierdza brak sekretów Cloud/local oraz pola `api_key` w JSON po `save_settings()`.
- Pełna suite pytest: **537 passed**; wykonano dwa niezależne przebiegi z identycznym wynikiem.
- `tests/test_qml_gui.py`: **153 passed**. Przejściowe 4 FAIL z pierwszego nakładającego się uruchomienia nie powtórzyły się w izolowanym module ani w dwóch pełnych przebiegach.
- `compileall`: PASS; kontrola sekretów w aktywnym `config.json`: PASS; `git diff --check`: PASS.

## 2026-10-07 — faktyczna korekta QML GUI po ponownej weryfikacji

- Poprzedni stan został zweryfikowany ponownie na źródłach. Cztery zgłoszone przez użytkownika problemy były realne: położenie przycisków, TranslateGemma, tooltipy Pomocy i reaktywność motywu.
- Wszystkie cztery zostały poprawione w kodzie i mają dedykowane regresje.
- Walidacja dedykowana: **6 passed**; `qmllint`: **PASS**.
- Pełny suite QML GUI nadal nie jest GREEN. Pierwszy wcześniejszy błąd to `test_qml_bridge_lists_and_toggles_real_user_skills`; przy dalszym przebiegu proces Qt/PySide6 kończy się `SIGABRT`. Nie deklaruję pełnego suite jako poprawnego.
- Rzeczywisty uruchomiony proces GUI PID 428116 nie został restartowany zdalnie, ponieważ środowisko SentinelX nie posiadało sesyjnego `DISPLAY`/Wayland/DBus/Xauthority. Nie użyto obejścia uwierzytelnienia X11. Oznacza to, że interaktywny wygląd bieżącego procesu wymaga kontrolowanego restartu w sesji użytkownika.

## 2026-10-07 — naprawa testu skip patterns przed backendem

Usunięto failure `test_document_translation_service_applies_skip_patterns_before_backend`. Przyczyną był wadliwy fixture testowy: nadpisany `HtmlFilter.extract()` nie utrzymywał kontraktu `session.units`, a wzorzec skip miał nadmiarowe escapowanie. Test korzysta teraz z rzeczywistego `HtmlFilter` i rzeczywistego dokumentu HTML.

Weryfikacja: test regresyjny **1 passed**; cały `tests/test_document_translation_service.py` **5 passed**.

---

## 2026-10-06 — korekty funkcjonalne QML GUI

- Przywrócono skille systemowe TXT (`plaintext.md`) i PDF (`pdf.md`) w GUI oraz automatyczny dobór skilla po rozszerzeniu.
- Przyciski „Przywróć domyślne” i „Zapisz ustawienia” są wspólne dla karty Przełączniki, na dole i wyrównane do lewej.
- Własny serwer ma osobny, domyślnie pusty URL z trwałym zapamiętaniem ostatniej wartości.
- Przejście z llama.cpp do innego backendu zatrzymuje serwer i zapisuje informację w logu; powrót do llama.cpp nie uruchamia go automatycznie, start wykonuje „Restartuj serwer”.
- Po starcie llama.cpp GUI sprawdza `/health` i odświeża adres z aktywnego runtime; port jest przekazywany jawnie do startu serwera.
- Dla Cloud pole klucza jest nieaktywne, gdy profil nie wymaga klucza. Mozhi pokazuje konkretną instancję lub efektywną instancję trybu `auto`.
- Zmiana motywu działa przez dedykowany `themeChanged`, a zakładki Pomocy mają tooltipy opisowe. Log i Podgląd mają po 300 px preferowanej wysokości.
- Nowe regresje GUI: **13 passed** w izolowanym uruchomieniu. `qmllint`, `compileall` i kontrola NUL: **PASS**.
- Pełny `tests/test_qml_gui.py` nadal kończy się `SIGABRT` po kilkudziesięciu testach Qt/PySide6; nie oznaczam pełnego suite jako GREEN.

## 2026-10-06 — poprawki lifecycle llama.cpp i przepływu tłumaczenia

- Start/restart llama.cpp przeniesiono poza wątek GUI, aby oczekiwanie na gotowość serwera nie zamrażało QML.
- Pole „Adres URL” dla llama.cpp jest normalnie widoczne, ale tylko do odczytu; port pozostaje ustawieniem z pola „Port”.
- Usunięto odtwarzanie portu z `base_url` podczas wczytywania ustawień.
- Naprawiono prezentację `TranslateGemma` w ComboBoxie.
- Podłączono wzorce pomijania do `DocumentProcessor`: pasujące fragmenty nie są wysyłane do backendu i są zachowywane bez zmian.
- Backup: `backups/20261006-server-lifecycle-translation/pre-change.tar.gz`, SHA-256 `f2b01672125a71ec6c7e352c4bc0805b1e337544cf78b0ba44e0abe4ac50d9e0`.
- Weryfikacja ukierunkowana po zmianach: 6 testów przechodzi.

## 2026-10-06 — źródło portu llama.cpp i adres URL w GUI

- Pole „Port” w karcie „API i serwer” jest źródłem portu uruchamianego llama.cpp; wartość trafia do AppSettings.server_port i jest używana przy starcie/restarcie runtime.
- Dodano bridge.serverUrl, który wylicza adres http://<host>:<port>/v1 z bieżącego hosta i portu GUI.
- Pole „Adres URL” dla llama.cpp pokazuje bridge.serverUrl jako informację zwrotną i jest nieedytowalne; nie może zmienić portu.
- Dla pozostałych backendów pole baseUrl zachowuje dotychczasową edycję.
- TDD: testy regresyjne najpierw zakończyły się 2 błędami RED, po implementacji GREEN: 2 passed.
- Backup przed zmianą: backups/20261006-server-port-url/pre-change.tar.gz, SHA-256 98d3efbd8cf854730e8fe32cde9830cfdee59642247126e96d3ae07dea99b47c.

## 2026-10-06 — końcowa walidacja

- Pełny `pytest -q`: **477 passed**.
- Apertium suite: **48 passed**.
- Regresje GUI Pomoc + `translationWorkOrb`: **2 passed**.
- `compileall`: **PASS**.
- Wheel staging + zawartość runtime: **PASS**.
- `ces-pol` pozostaje jawnie EXCLUDED; nie jest liczona jako READY.

## 2026-10-06 — domknięcie runtime Apertium i stabilizacja regresji GUI

- Prywatny runtime Apertium 3.9.12 uzupełniono o istniejące lokalnie `cg-proc`, `libcg3.so.1`, `lsx-proc`, `apertium-anaphora` i `libsqlite3.so.0`; nie instalowano ani nie usuwano pakietów systemowych.
- Smoke 28 paczek po uzupełnieniu: **27 READY / 1 EXCLUDED**. `ces-pol` pozostaje jawnie wyłączone z release scope z powodu potwierdzonej asercji `apertium-tagger` dla dostarczonego modelu `ces-pol.prob`.
- Wheel `dist/tlumacz-0.40.0-py3-none-any.whl` zbudowano w czystym staging-tree; SHA-256: `f8e9a9ab4b5924cb93708e7dbaed25a76a6c2ed173c6338f071b135ccb321028`.
- Bezpośredni build w istniejącym drzewie nadal blokuje ACL starego artefaktu Okapi; nie zmieniano jego właściciela ani uprawnień.
- Test GUI zależny od prywatnego języka konfiguracji został ustabilizowany przez użycie tymczasowej konfiguracji. Weryfikacja: **2 passed** dla pomocy i animowanego `translationWorkOrb`.
- Dokumentacja: `docs/technical-docs/apertium-pair-inventory-20261006.md` i `docs/reports/FAZA_6_APERTIUM_RUNTIME_GATE_2026-10-06.md`.

## 2026-10-06 — animowany wskaźnik pracy i wiarygodny stan błędu bloku

- Przywrócono w `TranslationPage.qml` animowany wskaźnik `translationWorkOrb`: obrót, pulsowanie i płynna zmiana koloru; tekstowy `translationStage` został usunięty z wiersza statystyk.
- Dodano kontrakt `chunkFailed(current, total, message)` między workerem a bridge. Błąd aktywnego bloku jest zapisywany w Logu i kończy stan tłumaczenia; nie pojawia się podsumowanie sukcesu ani postęp 100%.
- V4 przekazuje port lokalnego llama.cpp z `settings.server_port`; w bieżącej konfiguracji jest to **2782**. Proces bundled uruchomiony wcześniej na **28783** był osierocony i został zatrzymany; po cleanupie na 28783 nic nie nasłuchuje.
- Backup zmiany: `backups/20261006-translation-orb-status-port/pre-change.tar.gz`, SHA-256 `ca557a31265ceb27f2cf013a8ce000d21a9c1a4a9b2c9a00fc932b023ba567d3`.
- Świeży pełny suite: **477 passed**. Dodatkowo `qmllint`, `ruff` i `compileall` dla zmienionego zakresu przechodzą, a `/health` na porcie 2782 zwraca `{"status":"ok"}`.

## 2026-10-06 — Apertium runtime gate: discovery zależności wykonywalnych

- Discovery Apertium sprawdza teraz nie tylko pliki danych, ale również programy pipeline'u z modes.xml.
- ApertiumRuntime.language_pairs() zwraca wyłącznie rzeczywiste kierunki source-target; tryby pomocnicze nie są publikowane jako pary.
- Audyt 28 przygotowanych paczek: **17 READY / 11 BLOCKED** w prywatnym runtime.
- Zablokowane: cat-eng, ces-pol, deu-eng, eng-cat, eng-deu, eng-ita, ita-eng, pol-rus, pol-spa, rus-pol, spa-pol.
- Aktywny magazyn użytkownika /home/frs/.config/tlumacz/Apertium/ ma po filtrze **6 rzeczywistych par**.
- Testy Apertium po zmianie: **48 passed**; focused discovery/runtime: **13 passed**.
- Brakujących cg-proc, lsx-proc i apertium-anaphora nie instalowano do systemu.
- Szczegóły i dowody: docs/reports/FAZA_6_APERTIUM_RUNTIME_GATE_2026-10-06.md.

## 2026-10-06 — aktualny stan paczek Apertium po naprawie `pol-eng`

- Historyczny repozytoryjny magazyn paczek zawierał **28** osobnych, niekompresowanych paczek `.tar`; aktualny magazyn użytkownika przechowuje je poza repozytorium.
- `pol-eng` jest kompletne i przechodzi rzeczywisty runtime po instalacji do czystego magazynu;
- wszystkie 28 paczek przechodzi instalację i ponowne wykrycie przez mechanizm pluginów;
- wszystkie 28 plików `.mode` nie zawierają absolutnych ścieżek środowiska budowania;
- `SHA256SUMS` oraz indywidualne pliki `.tar.sha256` są aktualne;
- `hye-eng` usunięto z lokalnego magazynu runtime; nie należy go uwzględniać w aktualnym inventory.

## 2026-10-06 — przebieg komunikatów tłumaczenia

Bieżący GUI tłumaczenia używa tekstowego wskaźnika etapu zamiast animowanej kulki. Log ma deterministyczną kolejność: komunikaty uruchomieniowe → wybór skilla → „Gotowy do tłumaczenia.” → „Rozpoczęto tłumaczenie.” → typ dokumentu → pominięte fragmenty → liczba bloków → kolejne bloki → podsumowanie czasu/szybkości → zapisany plik → opcjonalne akcje końcowe.

Warstwa aplikacyjna raportuje rzeczywiste chunki przez `on_chunk_start/on_chunk_complete`. GUI pokazuje szybkość w znakach/s, a nie jednostkach/s.

Weryfikacja nowych kontraktów: **4 passed**; końcowy pełny `pytest`: **465 passed, 1 istniejący failure**. Pozostały failure dotyczy istniejącego testu `test_qml_bridge_exposes_help_topics_and_application_version`, który nadal odczytuje niemieckie tytuły tematów Pomocy z bieżącej konfiguracji, podczas gdy test wymaga polskich. Nie jest to regresja tej zmiany.

## 2026-10-06 — zamknięcie BUG-038: uprawnienia prywatnego runtime Apertium

BUG-038 został zamknięty po wykonaniu operacji przez właściciela checkoutu. Programy w `src/tlumacz/backends/apertium/native_runtime/bin/` i `libexec/` mają prawa wykonywania dla właściciela i grupy (`u+x`, `g+x`), przy zachowaniu właściciela `frs:frs`.

Świeża weryfikacja SentinelX:
- inspekcja praw plików: programy runtime są wykonywalne;
- `test_bundled_runtime_programs_are_owner_executable`: **1 passed, 8 deselected**;
- nie zmieniano właściciela ani ACL.

Wcześniejsze wpisy opisujące BUG-038 jako otwarty blocker uprawnień są historyczne i nie opisują już bieżącego stanu.

## 2026-10-06 — aktualizacja dwóch zgłoszonych defektów

Naprawiono reaktywność tytułów tematów Pomocy: HelpPage.qml korzysta bezpośrednio z bridge.helpTopics. Pierwszy temat dla języka polskiego to „Na początek”.

Problem trybów plików prywatnego runtime Apertium pozostaje otwarty i wymaga operacji wykonanej przez właściciela plików oraz świeżej weryfikacji testem regresyjnym.

## 2026-10-06 — status runtime'u llama.cpp

- Linux x86_64 na hoście referencyjnym Bmax: aplikacja domyślnie korzysta z bundled llama.cpp skompilowanej pod ten sprzęt (`runtime.source=bundled`).
- Inne Linux: do czasu przygotowania ogólnego bundled artefaktu stosować `runtime.source=system`.
- Windows/macOS: obecnie stosować runtime systemowy; brak bundled artefaktów dla tych platform.
- Dokumentacja rozróżnia build dedykowany i dystrybucyjny. Paczka dystrybucyjna ma używać bardziej ogólnych parametrów kompilacji, bez optymalizacji pod konkretny CPU/GPU.
- Dodano wzorzec `docs/wdrozenia/karta-referencyjna-llama-sprzet.md` oraz TODO dla automatycznego wykrywania sprzętu, generowania karty i kompilacji/benchmarku llama.cpp.


## 2026-10-06 — runtime llama.cpp

Domyślny runtime llama.cpp został przełączony z wyszukiwania systemowego `llama-server` na kompilację dołączoną do pakietu dla Linux x86_64. Kompilacja pochodzi ze źródeł `/home/frs/Projekty/llama.cpp`, revision `7ab4ee7baad2d920464cbacfad4f4b07cf111fd2`, i jest CPU-native.

Techniczny profil: `threads=auto`, `threads-batch=auto`, `batch-size=2048`, `ubatch-size=512`, `ctx-size=8192`, prompt cache ON, cache reuse 0, Flash Attention OFF, repack ON, KV K Q8_0/F16. Runtime dołączony korzysta z własnego katalogu bibliotek przez `LD_LIBRARY_PATH`.

Zachowano alternatywę `runtime.source=system` w `$HOME/.config/tlumacz/llama.json`, z `runtime.executable` jako nazwą z `PATH` albo pełną ścieżką.

Świeża walidacja runtime'u: `/health` OK; `parallel=1` → 1 slot i `n_ctx_slot=8192`; `parallel=4` → 4 sloty i `n_ctx_slot=2048`; rzeczywiste TranslateGemma PL→EN krótkiego tekstu → 5,57 s.

Dokumentacja: `docs/wdrozenia/llama-cpp-runtime.md`.

## 2026-10-06 — domknięcie TODO-022m: lifecycle TPlugin

TPluginInstaller obsługuje teraz pełny podstawowy cykl życia pluginu:

- update() wymaga istniejącej instalacji, zachowuje poprzedni stan w rollback/<plugin-id>/ i dopiero po przygotowaniu nowej paczki podmienia aktywny plugin;
- uninstall() usuwa wyłącznie wskazany plugin, wcześniej zapisując jego stan do rollbacku;
- rollback() przywraca najnowszy zachowany stan i ponownie rozwiązuje zależności shared;
- backup lifecycle zawiera również fizyczne kopie bibliotek shared wymaganych przez manifest, dzięki czemu rollback nie zależy od aktualnego stanu magazynu shared-libs;
- istniejące mechanizmy staging, path-traversal protection, checksum i atomowego commitowania instalacji pozostają aktywne.

Weryfikacja TDD: tests/test_tplugin.py — 12 passed. Macierz lifecycle obejmująca wszystkie 9 publicznych paczek .tplugin przechodzi sekwencję install → update → uninstall → rollback. Pełna macierz extract/merge/round-trip 9/9 pozostaje PASS.

Backup przed implementacją lifecycle:
backups/tplugin-lifecycle-20261006/pre-lifecycle.tar.gz
SHA-256: b9d14ea5f14b7684270ecc52b00c97f41a95727f0d7933674c3eb0c9eb9179bf.
## 2026-10-06 — korekta timeoutu lokalnego llama.cpp

Odtworzono błąd `Timeout komunikacji z llama.cpp` na rzeczywistym adapterze TranslateGemma dla pliku testowego `test_2000_chars.md`: przy timeout 120 s żądanie przekroczyło limit i zakończyło się `TimeoutError` podczas oczekiwania na nagłówki odpowiedzi HTTP. Zwiększono timeout przekazywany przez GUI dla backendu `llama.cpp` do **300 s**. Nie zmieniono timeoutu health-checku ani timeoutów startu/zatrzymania runtime.

Backup przed zmianą: `backups/llama-timeout-20261006/pre-change.tar.gz`, SHA-256 `d7beff92dfcd47e176af7a8504cb3972d53292d410825bdcb6edb2b46985676a`.

TDD: test `test_llama_translation_uses_gui_language_and_file_paths` najpierw RED (`120.0 != 300.0`), po zmianie GREEN. Pełny `tests/test_qml_gui.py`: **115 passed, 1 failed**; jedyny pozostały failure dotyczy niemieckich tytułów `help_topics` zamiast oczekiwanych polskich i nie jest związany z timeoutem.

## 2026-10-06 — domknięcie TODO-022j: samowystarczalne pakiety filtrów Okapi

Magazyn `filters/` zawiera fizyczne implementacje wszystkich aktywnych filtrów: `epub`, `html`, `json`, `markdown`, `openoffice`, `openxml`, `xliff`, `xliff2` i `yaml`. Wszystkie JAR-y znajdujące się bezpośrednio w pakietach filtrów są teraz fizycznymi plikami — nie ma już symlinków JAR.

Przeniesiono do właściwych konsumentów wszystkie wcześniej przejściowe zależności specyficzne dla filtrów oraz zależności TwelveMonkeys używane wyłącznie przez OpenXML: `runtime-abstractmarkup-1.49.0-local.jar`, `runtime-archive-1.49.0-local.jar`, `runtime-generated-parser-compat-1.48.jar`, `runtime-lib-xliff2-1.49.0-local.jar`, `common-io-3.12.0.jar` i `common-lang-3.12.0.jar`. Z `src/tlumacz/resources/okapi-runtime/` usunięto te JAR-y. Wspólny runtime zachowuje wyłącznie komponenty wspólne dla hosta i filtrów.

Dodano testy potwierdzające brak symlinków JAR w każdym pakiecie oraz brak tych czterech zależności w `okapi-runtime`. Testy zakresu migracji, dynamicznego loadera, walidacji zależności i zasobów pakietu: **16 passed**.

TODO-022j jest **ZAMKNIĘTE**. Pozostałe zadania 022d/022e dotyczą docelowej lokalizacji magazynu użytkownika i przyszłego loadera pakietów; nie są częścią tej migracji.

## 2026-10-06 — domknięcie zależności OpenXML i aktualny gate

Do `filters/openxml/` dołączono lokalny `common-io-3.12.0.jar`, wymagany przez `com.twelvemonkeys.io.ole2.CompoundDocument` i `CorruptDocumentException`. Descriptor OpenXML zawiera pełny artefakt `com.twelvemonkeys.common:common-io:3.12.0`. Walidator zależności potwierdza `usable=True`.

Pełny `pytest` po domknięciu 022j: **413 passed, 2 failed**. Pozostałe dwa failure dotyczą wyłącznie prywatnego runtime Apertium bez bitu `u+x` oraz niemieckiego stanu tematów Pomocy QML. Nie są to regresje migracji Okapi.

Biblioteka TwelveMonkeys nie była pobierana ani instalowana globalnie; wykorzystano już istniejący artefakt z prywatnego runtime Okapi.



Wdrożono i zweryfikowano mechanizm akcji wykonywanych po poprawnym zakończeniu tłumaczenia (QmlApplicationBridge._on_finished() → _post_translation_actions()):

- **Czyść cache po tłumaczeniu** — przy zaznaczonym `cache_clear_after_translation` wywoływane jest `TranslationApp.clear_translation_cache()`, które czyści `TranslationCache` używany przez sesję tłumaczenia;
- **Restart serwera llama.cpp po tłumaczeniu** — przy zaznaczonym `restart_llama_after_translation`, aktywnym backendzie `llama.cpp` i działającym runtime wykonywany jest kontrolowany `STOP → START`;
- restart po tłumaczeniu korzysta z **aktualnej konfiguracji GUI**: GGUF, host, port, tryb CPU/GPU, `parallel`, chat template i chunk size;
- wspólny helper `_restart_llama_from_gui()` zapewnia identyczną konfigurację dla restartu przyciskiem i restartu po tłumaczeniu;
- kolejność akcji jest deterministyczna: najpierw czyszczenie cache, następnie restart serwera;
- błędy akcji po tłumaczeniu są przechwytywane przez `_on_finished()` i raportowane w logu bez cofania stanu zakończenia tłumaczenia;
- analogiczny mechanizm pozostaje dostępny dla Apertium (`restart_apertium_after_translation`) i Chmury (`reconnect_cloud_after_translation`).

Weryfikacja TDD po zmianie: **7 testów lifecycle/post-translation — PASS**, **9 testów cache/core — PASS**. Backup przed zmianą: `backups/post-translation-actions/pre-change.tar.gz`, SHA-256 `9a2146b5843417076d36e05335b64baee6c15fff5cbae3a6980d94def1bfb2ae`.

## 2026-10-06 — korekta cyklu życia llama.cpp w GUI

Aktualny kontrakt `QmlApplicationBridge` jest następujący:

- ręczne wybranie `llama.cpp` uruchamia lokalny serwer natychmiast, niezależnie od checkboxa „Automatyczny start llama.cpp”;
- przejście z `llama.cpp` na inny backend najpierw zatrzymuje lokalny serwer;
- przycisk „Restartuj serwer” wykonuje kontrolowane `STOP → START` i używa bieżącej konfiguracji GUI, w tym aktualnego GGUF, hosta, portu, trybu obliczeń, parallel, szablonu czatu i chunk size;
- checkbox „Automatyczny start llama.cpp” dotyczy wyłącznie uruchomienia programu z aktywnym backendem `llama.cpp` — zaznaczenie uruchamia serwer przy starcie aplikacji, odznaczenie tego nie robi;
- wybór `llama.cpp` nie zmienia wartości checkboxa ani nie zapisuje wymuszonego `auto_start_server=True`.

Weryfikacja TDD: **5 testów cyklu życia GUI — PASS**. Pozostały pełny suite wymaga osobnej weryfikacji z uwagi na niezwiązaną regresję `_collect_filter_dependency_warnings` obserwowaną podczas jednego uruchomienia testów.

## 2026-10-06 — pełny gate po etapie 022i

Pełny `pytest` zakończył się wynikiem **389 passed, 2 failed**. Pozostałe dwa failure dotyczą wyłącznie: (1) braku `u+x` w 34 plikach prywatnego runtime Apertium oraz (2) niemieckiego domyślnego stanu tematów pomocy QML zamiast oczekiwanych polskich. Nie są to regresje etapu Okapi.

Status etapu 022i: **GREEN w zakresie własnym**. Status całego projektu: nadal **Release Candidate**, bez pełnego GREEN gate'u.

## 2026-10-06 — etap 3: rozdzielenie implementacji filtrów od wspólnego runtime

Wykonano analizę rzeczywistych JAR-ów Okapi i odseparowano fizyczne implementacje aktywnych filtrów od classpathu rodzica Java Filter Host. JAR-y implementacyjne EPUB, HTML, JSON, Markdown, OpenOffice, OpenXML, XLIFF, XLIFF2 i YAML zostały przeniesione do odpowiednich katalogów `filters/<nazwa>/`. Launcher nie dodaje już `okapi-runtime/*`; parent classpath zawiera `okapi-core` oraz wspólne biblioteki z `okapi-runtime/lib`.

Zależności wewnętrzne filtrów pozostają przejściowo reprezentowane przez symlinki, aby nie tworzyć fizycznych kopii JAR-ów. Zależności `flexmark*` są fizycznie przypisane do pakietu Markdown. OpenXML wymaga `com.twelvemonkeys.io.ole2.*`; lokalna inwentaryzacja wykazała zgodny artefakt `common-io-3.12.0.jar`, który został dołączony bezpośrednio do `filters/openxml/`. Walidator zależności potwierdza obecność obu wymaganych klas.

Regresje etapu: separacja runtime + dynamiczny FilterHost + registry/lifecycle + rzeczywiste round-trip Okapi — **22 passed**. `bash -n` obu launcherów, compileall i `git diff --check` — PASS. Dla filtrów wykorzystujących konfiguracje Okapi przez `ThreadSafeFilterConfigurationMapper` aktywowany jest kontekstowy `ClassLoader` konkretnego pakietu; dzięki temu EPUB/OpenXML mogą ładować zależności bez globalnego `okapi-runtime/*`.

Backup przed zmianą: `backups/okapi-runtime-split-20261006/pre-split.tar.gz`, SHA-256 `1085f98edcd58c6cee816571cce626452c80b3807b51ffe2e5b8b52561d5e9c2`.

## 2026-10-06 — etap 2 dynamicznego loadera Java filtrów

`FilterHost` otrzymał `FilterLoader`, który ładuje konkretny pakiet filtra z `TLUMACZ_FILTER_STORE` na żądanie. Pakiet jest opisany przez `filter.json` (`name`, `entry_class`) i zawiera JAR-y ładowane przez izolowany `URLClassLoader`. Dla pakietu filtra stosowany jest child-first dla całego jego pakietu klas, dzięki czemu klasa główna i jej klasy wewnętrzne pochodzą z tego samego loadera. Po zamknięciu sesji dokumentu zamykany jest także loader.

`run.sh` obsługuje `TLUMACZ_FILTER_HOST_RUNTIME_ROOT`, `TLUMACZ_FILTER_STORE` i kompiluje `FilterLoader.java` razem z `FilterHost.java`. Bieżący magazyn `filters/` zawiera przejściowe symlinki do istniejących JAR-ów runtime wraz z descriptorami. Nie wykonano usuwania JAR-ów z `okapi-runtime`; nie powstały też drugie fizyczne kopie implementacji.

Weryfikacja: łączony gate **38 passed**; Wcześniejszy test integracyjny ujawnił brak pakietów w magazynie; po dodaniu descriptorów i symlinków oraz poprawieniu izolacji classloadera całość przeszła.

Backup przed zmianą: `backups/filter-dynamic-loader-20261006/pre-java-loader.tar.gz`, SHA-256 `2a27b2c056e983a659eb511f166840f9a9f626d85ff2991f398320af558c0c44`.

## 2026-10-06 — etap 1 lazy-load filtrów dokumentowych

`FilterRegistry` nie przechowuje już instancji filtrów używanych przez bieżącą aplikację. `TranslationApp.build_filter_registry()` rejestruje fabryki filtrów przez `register_lazy()`; konkretna implementacja jest tworzona dopiero po rozpoznaniu rozszerzenia pliku przez `FilterRegistry.for_path()`. `DocumentProcessor` przejmuje tę instancję na czas sesji dokumentu, a `FilterLifecycle` zamyka sesję po zakończeniu lub błędzie. Po zakończeniu przetwarzania rejestr nie utrzymuje referencji do utworzonego filtra.

Oznacza to docelowy cykl: **załadowanie/rozpoznanie pliku → inicjalizacja właściwego filtra → gotowość przed tłumaczeniem → przetwarzanie → zamknięcie i zwolnienie instancji**. Nadal nie wykonano fizycznego przeniesienia implementacji JAR do magazynu `filters/`; ten etap pozostaje osobnym wdrożeniem dynamicznego loadera Java.

Weryfikacja etapu 1: `tests/test_filter_registry.py` — **8 passed**; `tests/test_filter_lifecycle.py` + `tests/test_okapi_runtime_integration.py` — **15 passed**.

Backup przed zmianą: `backups/filter-lazy-loading-20261006/pre-lazy-filter-loading.tar.gz`, SHA-256 `1f313719d06949def458097ecebbe66980904ba39a0c1c838279367b1244496a`.


## 2026-10-06 — przygotowanie magazynu filtrów użytkownika

Filter Engine otrzymał warstwę `FilterStore`, która oddziela lokalizację magazynu filtrów od rejestracji i wykonywania filtrów.

- bieżąca lokalizacja deweloperska: `<katalog projektu>/filters/`;
- przygotowana lokalizacja docelowa: `/home/frs/.config/tlumacz/filters/`;
- `FilterRegistry` przyjmuje jawnie ścieżkę magazynu;
- obecne filtry Okapi nadal są rejestrowane jawnie i nie zostały zastąpione automatycznym loaderem;
- migracja do katalogu użytkownika nastąpi przy instalacji docelowej.

## 2026-10-06 — Plan 03 llama.cpp + TranslateGemma: bieżący stan po weryfikacji

Plan 03 został zweryfikowany na aktualnym source V4 i aktualnym llama-server 0.4.0-dev (build 10809, commit 5266f24da). Nie wykonano niepotrzebnej zmiany produkcyjnego kodu, ponieważ bieżąca ścieżka llama.cpp działa poprawnie na rzeczywistym GGUF.

Obowiązujący kontrakt TranslateGemma to --no-jinja + ręcznie renderowany prompt Gemma + /v1/completions. Świeży test natywnego --jinja na aktualnym runtime wykazał błąd automatycznego parsera typed-content, dlatego wcześniejszy kontrakt chat_template_kwargs należy traktować jako historyczny wynik innego builda llama.cpp, nie jako wymaganie bieżącej implementacji.

Weryfikacja:
- 37 focused testów llama.cpp/TranslateGemma — PASS;
- 43 focused testy GUI — PASS;
- realny E2E TranslationApp z translategemma-4b-it.Q5_K_M.gguf — PASS;
- realny E2E przez QmlApplicationBridge — PASS;
- wynik Hello, how are you today? → Witaj, jak się masz dzisiaj?;
- translationFinished odebrane, status Tłumaczenie zakończone.;
- TranslationApp.close() zweryfikowane po E2E.

Pełny pytest aktualnego repozytorium: 379 passed, 2 failed. Dwa failures są poza Planem 03: uprawnienia bundlowanego runtime Apertium oraz zależność testu pomocy QML od globalnego stanu języka. Nie zmieniano tych obszarów.

## 2026-10-06 — wybór llama.cpp uruchamia serwer natychmiast

Naprawiono cykl życia po zmianie backendu w GUI. Przejście z Apertium, Chmury lub Własnego na `llama.cpp` natychmiast uruchamia serwer, ale nie zmienia ustawienia autostartu. Checkbox `auto_start_server` jest respektowany wyłącznie podczas uruchamiania programu z aktywnym backendem `llama.cpp`.

Przejście z llama.cpp na inny backend nadal najpierw zatrzymuje lokalny runtime.

Regresja TDD: przełączenie na llama.cpp musi wywołać `start_llama()` dokładnie raz.

## 2026-10-06 — świeży Plan 05: Release Candidate utrzymany

Ponowiony finalny gate nie potwierdził final release. Pełny pytest zakończył się wynikiem **373 passed, 1 failed**. Jedyna porażka dotyczy testu właścicielskiego bitu wykonywania prywatnego runtime Apertium: 34 pliki w `src/tlumacz/backends/apertium/native_runtime/bin/` i `libexec/` mają tryb `674`, bez `u+x`.

Bieżąca sesja nie ma praw do zmiany trybu tych plików, ponieważ są własnością `frs` i chroni je ACL; nie zmieniano właściciela ani ACL. Ruff, mypy, compileall i qmllint są **PASS**. Macierz backendów/dokumentów/GUI/packagingu zakończyła się **181 passed**.

Środowiskowy gate wykazał również, że `python -m tlumacz --version` nie jest obecnie poprawnym entrypointem V4 (brak `tlumacz.__main__`), a `/usr/bin/tlumacz` uruchamia globalny V3. Próba clean-wheel build zatrzymała się na ochronie Git `dubious ownership` dla `/home/frs/Projekty`.

**Status: RELEASE CANDIDATE. Final release niezatwierdzony.**

---
## 2026-10-06 — zabezpieczenie przed `Errno 111` w GUI llama.cpp

Dodano kontrolę lifecycle bezpośrednio przed rozpoczęciem tłumaczenia. Dla backendu `llama` `QmlApplicationBridge.start_translation()` ponownie wywołuje autostart, jeśli proces został wcześniej zatrzymany, i nie buduje usługi tłumaczenia dopóki runtime nie jest uruchomiony.

Weryfikacja regresji: rzeczywisty `Main.qml` został uruchomiony z konfiguracją GUI, serwer TranslateGemma został celowo zatrzymany, następnie rozpoczęto tłumaczenie. Aplikacja sama uruchomiła `llama-server` ponownie i wykonała tłumaczenie bez `Connection refused`.

Dodatkowo ustalono problem integracyjny środowiska: `/usr/bin/tlumacz` jest systemowym pakietem V3 `0.31.2` i wskazuje na `tlumacz.qt_gui`. V4 używa `tlumacz.qml_gui`. V3 nie został zmieniony. W repozytorium dodano `uruchom-tlumacz-v4.sh` oraz `Tlumacz-V4.desktop`; instalacja systemowego launchera wymaga uprawnień właściciela systemowych plików.

## 2026-10-06 — zmiana serwera zatrzymuje llama.cpp

Przy zmianie aktywnego backendu z llama.cpp na Apertium, Chmurę lub Własny `QmlApplicationBridge` najpierw wywołuje `core.stop_llama()`, a dopiero potem zmienia backend. Dzięki temu lokalny proces llama.cpp nie pozostaje uruchomiony po przełączeniu na inny serwer.

Dodano regresję TDD dla przełączenia llama.cpp → Chmura. Pełny suite pozostaje zależny od istniejącej, niezwiązanej regresji uprawnień bundlowanego runtime Apertium.

## 2026-10-06 — GUI llama.cpp korzysta z konfiguracji GUI i `llama.json`

Naprawiono kontrakt ścieżki GGUF między QML a runtime: wartości `file:///...` z `FileDialog` są normalizowane do lokalnej ścieżki przy ładowaniu i zapisie trwałych ustawień GUI. `QmlApplicationBridge` przekazuje następnie lokalną ścieżkę do `TranslationApp`.

Źródła konfiguracji są rozdzielone zgodnie z kontraktem V4:
- `$HOME/.config/tlumacz/config.json` — stan GUI: backend, host, port, GGUF, compute mode, chat template, parallel i autostart;
- `$HOME/.config/tlumacz/llama.json` — techniczne ustawienia llama.cpp, m.in. threads, batch, context, cache, Flash Attention, NUMA i GPU layers;
- `config/llama.json` — fallback repozytoryjny.

Świeże E2E QML/bridge/TranslationApp zakończyło się PASS na rzeczywistym GGUF. GUI odczytało `http://127.0.0.1:2782/v1`, a techniczne ustawienia runtime pochodziły z `/home/frs/.config/tlumacz/llama.json`. `llama-server` został uruchomiony przez aplikację na porcie `2782`; sygnał `translationFinished` został odebrany, status to `Tłumaczenie zakończone.`, a wynik Markdown został zapisany.

## 2026-10-06 — historyczna korekta autostartu llama.cpp

Wcześniejszy opis włączał `auto_start_server` przy wyborze backendu. Ten opis jest superseded przez bieżący kontrakt: wybór `llama.cpp` uruchamia serwer, ale zachowuje wartość checkboxa; autostart jest oceniany tylko podczas uruchamiania programu.

Focused testy: 3 passed, 101 deselected.

## 2026-10-06 — zamknięcie rzeczywistego E2E TranslateGemma

Świeży test przez rzeczywiste QML/bridge/TranslationApp zakończył się PASS. GUI użyło endpointu `http://127.0.0.1:2782/v1`; techniczne parametry runtime pochodziły z `/home/frs/.config/tlumacz/llama.json`. `llama-server` został uruchomiony przez aplikację na porcie `2782`, odebrano `translationFinished`, a wynik Markdown został zapisany. Plan 01/TODO-003 mogą być zamknięte.

## 2026-10-06 — korekta karty „API i serwer” llama.cpp

Przywrócono kontrakt wizualny karty do właściwego układu: usunięto dodatkową linię „Adres serwera” oraz pomocniczą linię z wyliczonym URL-em, które nie powinny występować w sekcji llama.cpp. Pozostawiono istniejące kontrolki `Port`, `Obliczenia serwera`, `Szablon czatu`, `Parallel`, `Model`, „Zachowanie backendu” i „Restartuj serwer”, wraz z dotychczasowymi separatorami i typografią.

Uzupełniono persystencję: przy zamknięciu `Main.qml` zapisuje pełny stan ustawień przez `bridge.saveSettings()`, więc ostatnie ustawienia llama.cpp są odtwarzane przy następnym uruchomieniu. Dodano regresje QML dla braku dodatkowego pola adresu i odtwarzania ustawień.

Focused `tests/test_qml_gui.py`: **102 passed**. Pełny pytest po zmianie: **366 passed, 1 failed**; jedyna porażka pozostaje poza zakresem tej korekty GUI: `tests/test_llama_adapter.py::test_llama_adapter_translategemma_uses_chat_template_kwargs` otrzymuje fixture z `choices[0].message.content`, podczas gdy aktualny adapter oczekuje pola `choices[0].text`.

## 2026-10-06 — Plan 01: rzeczywiste E2E Apertium i kontrakt środowiskowy

W rzeczywistym bundlowanym runtime Apertium wykryto brak jawnego APERTIUM_DATADIR: bez tego proces zwracał * zamiast dostępnych kierunków, mimo poprawnych artefaktów. Runtime i adapter V4 ustawiają teraz zmienną na skonfigurowany katalog danych. Dodano regresję routingu, która potwierdza zgodność detekcji Lingua en z konfiguracją Apertium eng.

Zweryfikowano rzeczywisty przepływ TranslationApp → DocumentTranslationService → BackendRegistry → Apertium → wynik dokumentowy dla eng → pol. Runtime Apertium 3.9.12 zwrócił @hello #Świat. Pełny pytest po zmianie: 363 passed, 0 failed. Backup: backups/plan-01-20261006-apertium-env/.

## 2026-10-06 — kolejna ochrona pustego targetu TranslateGemma

Błąd `Nieobsługiwany język docelowy TranslateGemma: ''` został odtworzony jako naruszenie kontraktu wejściowego adaptera. Dodano ochronę w `QmlApplicationBridge`: przed każdym startem tłumaczenia backendu llama.cpp pusty lub biały `target_language` jest normalizowany do `pl`. Dodano test regresyjny. Mechanizm detekcji źródła i odpowiedzialność komponentów zostały opisane kanonicznie w `docs/INDEX.md`.

## 2026-10-06 — separacja detekcji języka dla llama.cpp

Naprawiono granicę odpowiedzialności: Lingua pozostaje niezależnym detektorem w `src/tlumacz/language_detector.py`, a routing wykrytego `source_language` dla llama.cpp został wydzielony do `src/tlumacz/backends/llama_cpp/language_routing.py`. `LlamaCppAdapter` przyjmuje już ustalony kod źródłowy i wyłącznie tłumaczy. Cloud i custom nie korzystają z routingu llama.cpp. Usunięto ogólny `DynamicLanguageRouting` z aktywnej ścieżki aplikacyjnej.

## 2026-10-06 — naprawa pustego języka docelowego TranslateGemma

Zdiagnozowano regresję GUI: `ApertiumLanguageRouting` może prawidłowo wyzerować `_target_language`, gdy dla aktualnego źródła nie istnieje dostępna para. Przy przełączeniu backendu z Apertium na llama.cpp poprzedni stan pustego celu nie był jednak przywracany. `TranslationPage.qml` dodatkowo maskował taki stan przez `Math.max(0, ...)`, wizualnie pokazując pierwszy język mimo pustej wartości w bridge. Następnie `LlamaCppAdapter` otrzymywał `target_language=""` i zgłaszał `Nieobsługiwany język docelowy TranslateGemma: ''`.

Naprawa: przy przełączeniu z Apertium na backend z globalnym wyborem celu pusty target jest ustawiany na `pl`; selektor QML nie maskuje już nieprawidłowego indeksu. Dodano regresje TDD dla przełączenia Apertium → llama.cpp oraz selektora QML.

## 2026-10-06 — język i pliki wejścia/wyjścia w przepływie llama.cpp

Ujednolicono kontrakt startu tłumaczenia dla llama.cpp z ustawieniami GUI. Wybrany język źródłowy jest przekazywany do usługi dokumentowej; dla backendów innych niż Apertium nadal działa dynamiczne wykrywanie języka chunka, a ustawienie GUI pozostaje fallbackiem. Wybrany język docelowy jest przekazywany do backendu llama.cpp i dalej do `chat_template_kwargs` TranslateGemma. Plik wejściowy i wynikowy pozostają własnością warstwy dokumentowej: `DocumentTranslationService.translate_file()` otrzymuje obie ścieżki, wykonuje przetwarzanie dokumentu i zapisuje wynik; llama.cpp otrzymuje tekst/chunki, nie ścieżki plików.

Focused test kontraktu GUI: **2 passed**.

## 2026-10-06 — wynik pełnego gate po integracji GUI llama.cpp

Po dodatkowej korekcie kompatybilności `set_base_url()` focused GUI/runtime nadal przechodzi: **15 passed**. Ruff, compileall i qmllint przechodzą. Pełny pytest: **349 passed, 2 failed**; oba pozostałe błędy są w `tests/test_translategemma_special_mode.py` i wynikają z aktualnego adaptera TranslateGemma odrzucającego `source_language="auto"`. Mypy ma **3 istniejące błędy** w `src/tlumacz/application/translation_orchestrator.py`; parser llama.json nie generuje już własnych błędów mypy.

## 2026-10-06 — rozdzielenie detekcji języka Apertium i pozostałych backendów

Wdrożono dwa niezależne mechanizmy routingu języka:

- ApertiumLanguageRouting: detekcja dokumentu, zamrożony source → target, a następnie detekcja chunkowa wyłącznie do decyzji tłumacz/pomiń;
- DynamicLanguageRouting: niezależna detekcja każdego chunka dla backendów innych niż Apertium;
- TranslationOrchestrator przekazuje wykryty source do konkretnego żądania backendu;
- chunk odrzucony przez ścieżkę Apertium pozostaje bez zmian;
- cache tłumaczeń uwzględnia source_language;
- adapter TranslateGemma nie wykonuje już drugiej detekcji — korzysta z języka ustalonego przez routing.

Weryfikacja TDD: testy routingu Apertium/dynamiczne oraz regresje orkiestratora, executora, cache, usługi dokumentowej i adaptera llama.cpp — 25 passed. Pełny pytest po wdrożeniu: 351 passed, 0 failed.

Backup przed zmianą: backups/pre-language-detection-split-20261006.tar.gz, SHA-256 579c0ba7e5b9403661bb7e8a0b9ff7af43d1173a624bd882140977e6d102e238.

## 2026-10-06 — synchronizacja GUI z runtime llama.cpp

Zakończono integrację ustawień API i serwer oraz Przełączniki z zarządzanym runtime llama.cpp.

- adres serwera i port tworzą jeden endpoint http://<host>:<port>/v1;
- CPU/GPU, parallel, GGUF i szablon czatu trafiają do LlamaCppRuntimeConfig;
- rozmiar bloku trafia do pipeline tłumaczenia i służy również do wyliczenia automatycznego ctx-size zgodnie z llama.json;
- temperatura trafia do LlamaCppConfig i requestu /chat/completions;
- techniczne parametry runtime są ładowane z $HOME/.config/tlumacz/llama.json;
- start zarządzanego serwera czeka na /health HTTP 200;
- focused suite tej zmiany: 123 passed; compileall i qmllint — PASS.

## 2026-10-06 — cleanup magazynów Apertium i poprawka discovery runtime

Pełne archiwum katalogu użytkownika `/home/frs/.config/tlumacz/Apertium/` zostało zakończone i zweryfikowane przez `7z t`: `backups/tlumacz-user-Apertium-full-20261006.7z`, SHA-256 `d4a90e56875a75b0f467e2a28b3c522d87637309b91aaa5c638411dd3f1732d`. Archiwum obejmuje 5449 plików i 2,47 GiB danych źródłowych/runtime.

Po archiwizacji aktywny magazyn użytkownika odchudzono z pakietów źródłowych do zachowanych pakietów posiadających artefakty binarne. Źródła nie zostały utracone: pozostają w zweryfikowanym archiwum 7z. Repozytorium `Aperitium/` również ma pełne archiwum i usunięto z niego source-only pary; zasoby skompilowane pozostają do dalszego cleanupu.

Weryfikacja rzeczywista ujawniła i naprawiła błąd discovery/runtime: `ApertiumRuntime.language_pairs()` scala teraz tryby zgłoszone przez CLI z faktycznie skompilowanymi trybami znalezionymi w pakietach użytkownika, a `data_dir_for_pair()` rozróżnia tryby lokalne pakietu od trybów używających ścieżek względnych z prefiksem pakietu. Dodano regresje TDD. Focused suite Apertium: **26 passed**. Rzeczywisty adapter po poprawce tłumaczy `en→pl`: `@hello #Świat.` oraz `en→es`: `Hola Mundo.`.

## 2026-10-06 — mechanizm wyboru języka Apertium

Wdrożono pełny mechanizm wyboru języka w QML/Python zgodnie z dokumentami `docs/_inbox/wybor-jezyka-Apertium.md` i `docs/_inbox/plan-wdrozenia-jezyka-Apertium.md`.

- discovery Apertium uznaje wyłącznie skompilowane kierunki wynikające z faktycznie obecnych artefaktów binarnych wymaganych przez `modes.xml`;
- indeks par jest logicznie dwukierunkowy dla wyboru GUI, np. `pol-eng` daje `pl → en` oraz `en → pl`;
- źródło jest wybierane przez `bridge.apertiumSourceLanguages`;
- cele są filtrowane wyłącznie według bieżącego źródła;
- po zmianie źródła niezgodny cel jest zerowany;
- brak dostępnego celu pokazuje `brak pary` i blokuje selektor celu;
- dla tekstowych plików przy źródle automatycznym używany jest istniejący `LanguageDetector`/Lingua, a wykryty język staje się bieżącym źródłem;
- bridge korzysta z `default_data_dir()`, więc docelowy katalog danych pozostaje `$HOME/.config/tlumacz/Apertium/`, bez hardcodowania ścieżki użytkownika;
- start tłumaczenia odrzuca nieprawidłowe źródło lub cel zamiast przekazywać niedozwoloną kombinację do backendu.

Weryfikacja: **12 focused tests**, **12 testów adapter/backend/runtime**, **2 E2E dokumentowe Apertium**, **87 testów QML** — wszystkie GREEN. Rzeczywisty katalog `/home/frs/.config/tlumacz/Apertium/` zwrócił 8 gotowych kierunków na podstawie skompilowanych artefaktów.
## 2026-10-06 — TranslateGemma: działający runtime referencyjny

Rzeczywisty model /home/frs/Modele/translategemma-4b-it.Q5_K_M.gguf został uruchomiony na izolowanym llama-server z llama.cpp b7976 (972f323e7). Natywny szablon Jinja z GGUF działa poprawnie po przekazaniu source_lang_code i target_lang_code przez chat_template_kwargs. Test rzeczywisty zwrócił Dzień dobry, jak się masz dzisiaj? dla wejścia Hello, how are you today?.

Wniosek: problem nie dotyczy modelu ani braku wsparcia Jinja. Wcześniejsze typed-content było niewłaściwym kontraktem dla ścieżki /v1/chat/completions, ponieważ llama.cpp gubi dodatkowe pola. Aktywny adapter został przełączony na chat_template_kwargs; focused tests: 3 passed. Pełne E2E przez GUI/aplikację pozostaje kolejnym gate'em.

## 2026-10-06 — porządkowanie Apertium

Aperitium/ i /home/frs/.config/tlumacz/Apertium/ zawierają zarówno źródła, dane deweloperskie, historię Git, jak i skompilowane zasoby. Przed usuwaniem źródeł wykonano pełne archiwum repozytoryjne 7z: backups/Aperitium-sources-full-20261006.7z, zweryfikowane przez 7z t. Analogiczne archiwum katalogu użytkownika jest obecnie tworzone. Zasoby monojęzyczne pozostają chronione, ponieważ pary korzystają z ich skompilowanych automatów.

---
id: status-v4
status: active
meta:
  contentType: Status
  category: governance
version: 0.40.0
updated: 2026-10-06
owner: project-maintenance
source:
  - src/tlumacz/
  - docs/STATUS.md
depends_on: [docs/ARCHITECTURE.md, docs/TODO.md, docs/BUG.md]
expires_when: zmiana bieżącego stanu projektu
last_validation: "pełny pytest 373 passed, 1 failed; Ruff PASS; mypy PASS; compileall PASS; qmllint PASS; macierz backendów/dokumentów/GUI/packagingu 181 passed; Release Candidate 0.40.0, 2026-10-06"
---

## 2026-10-06 — kompilacja pozostałych par Apertium

Wykonano wymuszoną przebudowę źródeł par znajdujących się w `Aperitium/`. Backup przed zmianami: `backups/apertium-pairs-before-compile-20261006-002349.tar.gz`.

Potwierdzone `make -B` i rzeczywistym smoke-testem: `eng-cat`, `eng-deu`, `eng-ita`, `eng-spa`, `en-pt`, `pol-ces`, `pol-rus`, `pol-szl`, `pol-ukr`, `spa-pol`, a także `pl-csb` i `pl-sk` po naprawie ich źródeł.

Naprawy źródeł:
- `pol-rus`: `a_pprep` → istniejący `pprep`;
- `pl-sk`: dodano brakujący `a_vrb`;
- `pl-csb`: dodano brakujący `a_det`.

`pl-csb` nadal raportuje duplikaty `pardef` dla `wąg/ier__n` i `kwi/at__n`; build generuje artefakty, ale ten stan pozostaje ryzykiem jakości słownika i nie został usunięty arbitralnie.

`pl-uk` pozostaje nieprzebudowane: jego `configure.ac` wymaga `apertium-3.2`, którego obecny lokalny runtime nie publikuje w `pkg-config`. Zgodnie z zasadą braku nieautoryzowanych instalacji nie doinstalowano starego pakietu.

Dodatkowo potwierdzono rzeczywiste działanie `lsx-proc` po korekcie bitu wykonywania lokalnego artefaktu `.prefix/bin/lsx-proc`; bez tego `eng-cat` i `eng-deu` kończyły się pustym wynikiem mimo kodu 0.

## 2026-10-06 — wykonanie kolejnych pozycji planu naprawy

Zweryfikowano i wykonano bezpośrednio na kodzie: usunięto 1-sekundowy polling `refreshSkills()` z `ExtrasPage.qml`, usunięto zbędne `font.bold: false`, ustalono bazowy font GUI na 15 px zgodnie z `Main.qml`, uelastyczniono `uruchom-v4.sh` przez wyznaczanie katalogu z `BASH_SOURCE[0]` oraz dodano testy regresyjne. Dodano lokalny `.gitignore`; lokalna granica Git V4 nie jest tworzona, ponieważ repozytorium synchronizowane z GitHubem znajduje się poza katalogiem V4. Indeks dokumentacji został zweryfikowany względem filesystemu: 472 kanoniczne pliki, w tym wcześniej pominięty `docs/BUILD.md`; 11 plików `*.bak.*` pozostaje poza indeksem.

Weryfikacja zmian: pełny pytest — 319 passed; Ruff PASS; mypy PASS; compileall PASS; `qmllint` PASS; clean-wheel build PASS; wheel metadata nie zawiera usuniętych zależności; clean install CLI/Apertium/QML smoke PASS. Apertium w clean install wykrywa `('eng-pol',)` i tłumaczy `Hello world.` → `@hello #Świat.`. Accessibility: focused runtime/source tests 2 passed po dodaniu 4 `Accessible.name`. TranslateGemma: rzeczywisty model `$HOME/Modele/translategemma-4b-it.Q5_K_M.gguf` znaleziony; pierwszy E2E ujawnił, że lokalny `llama-server` odrzuca jawny `--chat-template translategemma`, więc BUG-025 pozostaje otwarty do naprawy kontraktu runtime.

## 2026-10-05 — zamknięcie krytycznych i poważnych blockerów release

Po korelacji aktualnego source z planem naprawczym zamknięto BUG-001 oraz BUG-005–015, z wyjątkiem osobnych decyzji platformowych/repozytoryjnych i pełnego dependency closure. Canonical wheel 0.40.0 został zbudowany z aktualnego source poza nadrzędnym checkoutem Git, zainstalowany do czystego katalogu i zweryfikowany przez CLI, QML oraz Apertium eng-pol.

Końcowy gate: 315 passed, Ruff PASS, mypy PASS, compileall PASS, QML smoke PASS, wheel audit PASS, clean-install eng-pol PASS.

Otwarte pozostają m.in. BUG-002 Windows runtime, BUG-003 dependency/licencje, BUG-004 ryzyko globalnego launchera V3, BUG-016/017 granica Git/.gitignore oraz BUG-025 rzeczywiste E2E TranslateGemma.

## 2026-10-05 — dokumentacja i pomoc po korelacji z kodem

Przeprowadzono przegląd aktualnego kodu QML/Python i dokumentacji. Uzupełniono pomoc PL/EN/DE, dokumentację techniczną backendów, lifecycle llama.cpp, Cloud/SecretStore, Filter Engine oraz aktualny kontrakt GUI.

W trakcie korelacji znaleziono jedną istotną rozbieżność: `TranslationPage.qml` nadal umieszcza pola Apertium w tym samym `RowLayout` co przyciski **Tłumacz** i **Anuluj**, mimo wcześniejszych wpisów changelogu opisujących osobny wiersz. Rozbieżność została oznaczona jako problem kodu do naprawy, a nie zamaskowana zmianą dokumentacji.

Pomoc użytkownika opisuje pięć tematów zgodnych z parserem `QmlApplicationBridge`. TXT i PDF zostały usunięte z deklarowanej obsługi głównego Filter Engine w pomocy, ponieważ nie są rejestrowane przez `build_filter_registry()`.

## 2026-10-06 — aktualny stan pól językowych Apertium

GUI udostępnia aktywne ComboBoxy Apertium. Źródło korzysta z wykrytych/znanych kodów Apertium, a cel jest filtrowany względem bieżącego źródła i faktycznie skompilowanych kierunków. Przy braku pary GUI pokazuje `brak pary` i blokuje wybór celu. Automatyczne wykrycie tekstowego źródła korzysta z istniejącego Lingua `LanguageDetector`; ręczny wybór pozostaje dostępny, gdy detekcja nie może dostarczyć użytecznego kodu.



Ponownie sprawdzono kod względem dokumentacji po najnowszej serii zmian. Potwierdzono aktywne: `TranslationApp.restart_llama()`, specjalny tryb TranslateGemma z `LanguageDetector`, migrację starszych `api_key` do `SecretStore` w bridge oraz brak aktywnych kontrolerów GUI poza `BackendController`. Zaktualizowano dokumentację architektury, macierz funkcjonalną, podręcznik oraz lokalizacje EN/DE. Weryfikacja: **268 passed**, `python3 -m compileall -q src tests` — PASS, `qmllint src/tlumacz/qml_gui/*.qml` — PASS.

## 2026-10-04 — Plan 04 / pierwsza optymalizacja

Wykonano pomiar i optymalizację pipeline'u dokumentowego. `DocumentTranslationService` wykonuje teraz jeden przebieg `TranslationOrchestrator` na dokument, zachowując walidację i postęp. Benchmark 200 jednostek: **200 → 1** wywołanie orchestratora, **0,048947 s → 0,009530 s**. Pełny suite: **266 passed**.

## 2026-10-04 — Plan 03 / audyt regresji

Po Planie 01 i bieżącym cleanupie Planu 02 wykonano skoncentrowany audyt regresji: **81 passed**, dodatkowo **62 passed** dla GUI/i18n/core/SecretStore. Nie wykryto nowej regresji wymagającej poprawki kodu.

Otwarte pozostają wyłącznie znane kwestie: Apertium eng-pol/cas_sp, Windows runtime, dependency/licencje oraz E2E rzeczywistego modelu TranslateGemma.

## 2026-10-04 — Plan 01 i Plan 02 zamknięte

- Plan 01 został zamknięty; E2E rzeczywistego TranslateGemma pozostaje w `docs/TODO.md` i nie blokuje dalszego cleanupu;
- Plan 02 usunął potwierdzone dead code: `profile_migration.py`, `DocumentProcessor._unit_parts()` oraz nieużywane kontrolery GUI (`TranslationController`, `DocumentController`, `SettingsController`, `DiagnosticsController`, `ProgressController`); aktywny pozostaje `BackendController`;
- `SecretStore` jest teraz podłączony do aktywnego QML bridge; sekrety Cloud są poza JSON;
- `BackendController` pozostaje aktywnym kontrolerem wyboru backendu;
- pełny suite po zmianach: **279 passed**.

## 2026-10-04 — przywrócenie specjalnego trybu TranslateGemma

W ramach Planu 01 przywrócono dedykowany kontrakt TranslateGemma w aktywnym backendzie llama.cpp.

- `chat_template="translategemma"` jest trybem specjalnym, a nie osobnym backendem;
- tryb TG korzysta z `src/tlumacz/language_detector.py` i Lingua wyłącznie dla TranslateGemma;
- źródło jest wykrywane dla tłumaczonego tekstu i przekazywane jako kod ISO 639-1;
- język docelowy jest normalizowany do kodu ISO 639-1;
- standardowy llama.cpp pozostaje na `/chat/completions` i nie korzysta z Lingua;
- TG używa dedykowanego promptu i `/completions`, zachowując specjalny kontrakt TranslateGemma bez reaktywacji FastAPI/OpenVINO;
- zależność `lingua-language-detector>=2.1.1` jest zadeklarowana w `pyproject.toml`; na Bmax zainstalowano `2.2.0`;
- weryfikacja kontraktu: **23 passed** dla testów TranslateGemma/runtime/GUI oraz **282 passed** dla pełnego suite V4;

E2E z rzeczywistym modelem TranslateGemma pozostaje do wykonania.

## 2026-10-04 — zapis konfiguracji końcowej bieżącej serii GUI

Bieżący stan interfejsu został zapisany jako punkt odniesienia:

- **API i serwer:** pod separatorem znajduje się pogrubiony nagłówek **Serwer llama.cpp — lokalny**; **Szablon czatu** zastępuje Temperaturę i oferuje jinja, chatml, TranslateGemma;
- **Przełączniki:** kolejność **Glosariusz → Umiejętności → Ustawienia LLM**;
- **Glosariusz:** przyciski **Przeglądaj...** i **Dodaj** mają po 120 px, a pola tekstowe dopasowują się do pozostałej szerokości;
- **Umiejętności:** trzy przyciski akcji mają po 180 px;
- **Ustawienia LLM:** Rozmiar bloku i Temperatura mają po 120 px;
- **ikony:** tlumacz-dark.svg i tlumacz-light.svg, wybierane automatycznie według aktywnego motywu;
- pełny suite po zmianach: **276 passed**.


## 2026-10-03 — korekta karty „Przełączniki”: Rozmiar bloku, czcionka i przyciski skilli

W `ExtrasPage.qml` skorygowano styl typografii: kontrolki pozostają przy **15 px**, **tytuły głównych sekcji są pogrubione, a pozostały tekst nie jest pogrubiony**. Pole **Rozmiar bloku** ma **140 px** (mieści wartości czterocyfrowe), a trzy przyciski akcji skilli mają jednakową szerokość **210 px**. Weryfikacja `tests/test_qml_gui.py`: **42 passed**; `compileall`: PASS.
## 2026-10-03 — korekta układu „Przełączniki”

Na podstawie aktualnego renderu GUI poprawiono `ExtrasPage.qml`: glosariusz ma krótkie, dopasowane wiersze; umiejętności są rozdzielone liniami i prezentowane w dwóch równoległych podpolach (**Skille systemowe** / **Skille użytkownika**); czcionki kontrolek zmniejszono do 15 px; karta nie wymusza zwiększania szerokości okna i przewija zawartość pionowo.

Zmieniono również lokalizowane wartości `settings.glossary_path_hint` w PL/EN/DE na krótką formę odpowiednią dla pola.

## 2026-10-03 — korekta szerokości kontrolek portu i llama.cpp

Kontrolki **Port**, **Obliczenia serwera**, **Temperatura** i **Wątki (parallel)** mają wspólną szerokość 140 px. Obok kontrolki Port znajduje się przycisk **„Losuj port”** wywołujący `randomServerPort()`.

## 2026-10-03 — karta „API i serwer”: port

Dodano obok pola **Port** przycisk **„Losuj port”** korzystający z istniejącego slotu `randomServerPort()`. Pole **Obliczenia serwera** ma teraz taką samą szerokość jak pole Port (140 px). Losowanie ustawia port z zakresu 1111–65535.

Backup przed zmianą: `backups/api-port-layout-20261003/pre-api-port-layout-20261003.tar.gz` (SHA-256 `37af9f67cc72e40b3a859b7cb7a00c223841d0fead8c928cb15214659cd3ed1e`).

## 2026-10-03 — korekta kolejności karty „API i serwer”

Separator po **Serwer** jest teraz stały, niezależnie od wybranego backendu. Dla llama.cpp kolejność pozostaje: **Ustawienia API → Adres URL serwera → Klucz API → Serwer → separator → Port → Obliczenia serwera → Temperatura → Wątki (parallel) → Model → Restartuj serwer**.

Weryfikacja: test regresji karty API **1 passed**, pełny suite **268 passed**, `python3 -m compileall -q src tests` — PASS.

## 2026-10-03 — weryfikacja końcowa GUI

Po ostatniej korekcie typografii pełny suite zakończył się wynikiem **268 passed**. `compileall` przechodzi. Smoke QML offscreen kończy się kontrolowanym timeoutem 124 bez komunikatu błędu. Jedno wcześniejsze uruchomienie pełnego suite miało przejściową porażkę testu `test_runtime_health_is_ok_for_owned_running_process`; ponowne uruchomienie testu oraz pełnego suite zakończyło się sukcesem.

## 2026-10-03 — końcowa seria korekt GUI

Wprowadzono pozostałe poprawki z bieżącej listy użytkowej: backendy Apertium/Chmura/Własny, siatkę skilli użytkownika, usuwanie skilli, szablon tworzenia skilla, krótkie kontrolki LLM, wybór języka docelowego w Pomocy, zawijanie zakładek Pomocy i natychmiastową zmianę motywu.

Weryfikacja końcowa tej serii: **267 passed**, `python3 -m compileall -q src tests` — PASS, smoke QML offscreen kończy się kontrolowanym timeoutem 124 bez komunikatu błędu.

## 2026-10-03 — bieżąca korekta karty „API i serwer”

Wprowadzono pierwszy etap korekty układu `ApiPage.qml` zgodnie z aktualnym wymaganiem użytkowym. Dla llama.cpp kolejność jest: **Ustawienia API → adres URL serwera → klucz API → serwer → separator → port → obliczenia serwera → temperatura → Wątki (parallel) → Model (plik GGUF) → Restartuj serwer**. Przycisk restartu zajmuje całą szerokość i jest ostatnim elementem.

Weryfikacja po zmianie: pełny suite **265 passed**, `python3 -m compileall -q src tests` — PASS, smoke QML w trybie offscreen zakończony kontrolowanym timeoutem 124 bez komunikatu błędu.

## 2026-10-03 — naprawa karty „Tłumaczenie”

`TranslationPage.qml` został zweryfikowany bezpośrednio na hoście Bmax i skorygowany zgodnie z aktywną specyfikacją `docs/technical-docs/QML_GUI_TRANSLATION_CARD_SPEC.md`. Usunięto dodatkowy nagłówek Sterowania oraz separatory wewnątrz sekcji Pliki. Pozostawiono dwa separatory: Pliki → Log i Log → Podgląd. Tłumacz/Anuluj pozostają po lewej, Język docelowy po prawej, a Anuluj ma jawne czerwone tło.

Weryfikacja: **265 passed**; compileall PASS; smoke QML offscreen zakończył się kontrolowanym `124` po 8 s bez komunikatu błędu; kontrola struktury QML PASS. Backup: `backups/translation-page-qml-expert-20261003/pre-translation-page.tar.gz` (SHA-256 `3092776287016ea0a1a823169c1b5dcae8c2070f67ad21edcbbba2d492740202`).

## 2026-10-03 — dokładna kolejność karty „Tłumaczenie”

- kolejność: Pliki → Sterowanie → Postęp → Statystyki → Log → Podgląd;
- dodano osobne sekcje i separatory;
- zachowano Tłumacz/Anuluj po lewej, Język docelowy po prawej;
- backup: `backups/translation-page-order-20261003/pre-translation-page-order.tar.gz`;
- SHA-256: `71111cccc110cf1317de486a87c218c721a6e300cc4cb2394575bb2c06aac98b`.

## 2026-10-03 — korekta karty „API i serwer”

- zachowano kolejność sekcji Backend → Połączenie → Cloud → llama.cpp → Apertium → Własny;
- ścieżkę GGUF przeniesiono nad parametry llama.cpp;
- pola Obliczenia serwera i Szablon czatu skrócono;
- przywrócono checkboxy Auto start, czyszczenie cache i restart po tłumaczeniu;
- przycisk zmieniono na **Restartuj serwer** i rozciągnięto na całą szerokość sekcji;
- poprawiono etykietę `settings.model` na **Model**.
- backup: `backups/api-page-layout-20261003/pre-api-page-layout.tar.gz`;
- SHA-256: `b035c0c796ad9356ca7a988acffff91e347c1a08191106fbfb8514d6c3f815b5`.

## 2026-10-03 — końcowa weryfikacja korekty GUI

- pełny pytest: **261 passed**;
- compileall: PASS;
- Ruff: PASS;
- smoke QML offscreen: `QML_EXIT:124` po kontrolowanym timeoutcie, bez błędu inicjalizacji;
- test persystencji geometrii X/Y/W/H: PASS;
- kontrakt karty „Przełączniki” oraz ustawień Pomocy jest zgodny z aktualną specyfikacją.
## 2026-10-03 — karta „Przełączniki” i poprawa geometrii okna

- przywrócono trzecią kartę jako **„Przełączniki”**;
- zaimplementowano dokładny układ trzech sekcji: Glosariusz, Skille, Ustawienia LMM;
- podłączono glosariusz do bridge, liczenie par oraz dodawanie wpisów CSV;
- dodano siedem stałych skilli i automatyczne wykrywanie skilli użytkownika;
- dodano zakresy LMM zgodne ze specyfikacją: blok 500–8000 / 500 oraz temperatura 0.0–1.0 / 0.1;
- przeniesiono Motyw i Język do karty Pomoc;
- dodano rzeczywiste przełączanie jasnego/ciemnego/systemowego motywu;
- poprawiono trwały zapis pozycji i rozmiaru okna;
- dokumentacja GUI została rozszerzona o pełny kontrakt karty.

Backup:
backups/switches-gui-20261003/pre-switches-gui.tar.gz

SHA-256:
633cd34e076ebfc41954e9b2ffba6c0a41bc681d6744a8a8bcfabd97a188836c


## 2026-10-03 — weryfikacja integracji „Serwer i API”

Po aktualizacji kontraktu testów powierzchni QML:
- pełny pytest: **257 passed**;
- compileall: **PASS**;
- Ruff: **PASS**;
- smoke QML offscreen: proces uruchomił GUI i pozostał aktywny do kontrolowanego timeoutu (QML_EXIT:124), bez błędu inicjalizacji.


## 2026-10-03 — integracja karty „Serwer i API” z runtime V4

Karta trzeciej zakładki została podłączona do rzeczywistego kodu programu.

- bridge wystawia ustawienia portu, autostartu, cache, restartu oraz Mozhi;
- wybór Chmura → Mozhi przekazuje wybraną instancję i silnik do BackendRequest;
- llama.cpp korzysta z rzeczywistego lifecycle TranslationApp;
- po tłumaczeniu możliwe jest rzeczywiste czyszczenie TranslationCache i restart zarządzanego llama.cpp;
- karta QML zawiera osobne powierzchnie dla llama.cpp, Apertium, Chmura i Własny;
- lista modeli chmurowych została ograniczona do kontraktu karty, z Mozhi jako osobną ścieżką;
- Apertium pozostaje procesowym CLI, więc nie jest udawany trwały restart procesu.

Backup przed zmianą:
backups/server-api-wiring-20261003/pre-server-api-wiring.tar.gz

SHA-256:
2611dcf73ca554761626e4cb044139d60451cede9a50c3561f6c1c44690dc60e


## 2026-10-03 — podłączenie kart „API i serwer” oraz „Serwer i API”

- `ApiPage.qml` korzysta teraz z jawnie wystawionych przez `QmlApplicationBridge` właściwości i metod camelCase: backend, profile Cloud, llama.cpp, GGUF, parametry połączenia i sterowanie serwerem.
- `ExtrasPage.qml` / karta „Serwer i API” korzysta z jawnie wystawionych właściwości i metod: glossariusz, skille, parametry, wzorce pomijania, język, motyw i zapis/przywracanie ustawień.
- Nie wykonano dalszego podłączania logiki karty „Serwer i API”. Jej docelowy układ został zapisany w `docs/technical-docs/QML_GUI_LAYOUT.md` oraz uzupełniony o dane Mozhi z V3.
- Backup przed zmianą: `backups/qml-api-switches-wiring-20261003-023205/pre-api-switches-wiring.tar.gz`.

Weryfikacja tego etapu: 250 passed.

## 2026-10-03 — finalizacja funkcjonalna dwóch kart

Dwie karty wskazane do ukończenia są podłączone do runtime QML:

- **Tłumaczenie:** pola plików, Browse, Tłumacz, Anuluj, język docelowy, postęp, czas, prędkość, Log i Podgląd korzystają z bridge.
- **Pomoc:** O Programie otwiera modalne okno; pomoc podręczna ma pięć tematów; treść jest ładowana z plików pomocy PL/EN/DE; zmiana języka przełącza plik.
- Jawne aliasy QML w bridge zapewniają połączenie nazw używanych przez Qt Quick z metodami i właściwościami Python.

Weryfikacja: 249 passed; compileall PASS; Ruff PASS; smoke startu QML zakończony bez błędu inicjalizacji (proces zatrzymany kontrolowanym timeoutem).

## 2026-10-03 — domknięcie dwóch kart GUI

Wykonano kolejny etap integracji GUI QML.

- **Tłumaczenie:** kolejność elementów odpowiada specyfikacji; Log znajduje się przed Podglądem tłumaczenia; sekcje są rozdzielone poziomymi separatorami.
- **Pomoc:** przycisk „O programie” jest po prawej stronie nagłówka; dialog korzysta z rzeczywistej wersji aplikacji; pomoc podręczna ma własne zakładki tematyczne z treścią z plików Markdown PL/EN/DE.
- **Zakładki główne:** Tłumaczenie | API i serwer | Serwer i API | Pomoc.
- Nazwa okna aplikacji: **Tłumacz**.
- Treść pomocy ma fallback do PL, gdy plik dla wybranego języka nie jest dostępny.

Backup przed zmianą: backups/help-translation-tabs-20261003-0207/pre-help-translation.tar.gz.
SHA-256: 2fb567259830a8d3f9dc3c993bc11ea40a70b546652bf203fc6b9b411ae45ef6.
# STATUS V4

## 2026-10-04 — aktualizacja dokumentacji względem rzeczywistego kodu

Przeprowadzono korelację dokumentacji z aktualnym `src/tlumacz/` i skorygowano rozbieżności.

### Potwierdzone funkcje aktywne

- aktywne backendy: llama.cpp, Cloud, Apertium oraz endpoint `custom` obsługiwany przez CloudRouter;
- aktywny pipeline: Filter Engine → jednostki → TranslationOrchestrator → backend → walidacja → zapis;
- aktywny cache SQLite z TTL 7 dni;
- anulowanie przez CancellationToken;
- walidacja wyników i markerów;
- aktywne GUI QML z QmlApplicationBridge;
- glosariusz, skille, ustawienia, i18n PL/EN/DE, pomoc Markdown;
- filtry: DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF 2.0.

### Skorygowane wcześniejsze twierdzenia

- historyczna uwaga o braku detektora Lingua została zamknięta przez Plan 01: aktywny V4 ma izolowany detektor używany wyłącznie przez `chat_template="translategemma"`; poza tym trybem `source_language="auto"` pozostaje kontraktem.
- TXT i PDF **nie są obecnie zarejestrowane w aktywnym FilterRegistry**. Nie są więc wykazywane jako aktywne formaty głównego pipeline'u.
- `custom` nie jest niezależnym silnikiem: korzysta z CloudRouter.
- `TranslateGemma` w aktywnym V4 oznacza szablon czatu llama.cpp, nie backend OpenVINO/FastAPI.
- klasyczne `src/tlumacz/qt_gui/` nie jest aktywną ścieżką; GUI zostało zmigrowane do QML.

### Dokumentacja

Dodano `docs/technical-docs/functional-capabilities.md` jako kanoniczną macierz funkcji kodu. Zakończone materiały migracyjne i historyczne instrukcje Windows przeniesiono do `docs/archive/`.


## 2026-09-30

### Stan migracji

- Faza 0 — baseline: ZAMKNIĘTA.
- Faza 1 — bootstrap V4: ZAMKNIĘTA.
- Faza 2 — kontrakty: ZAMKNIĘTA.
- Faza 3 — Filter Engine: wykonane komponenty i filtry; pełne kryterium fazy pozostaje do osobnej weryfikacji round-trip DOCX.
- Faza 4 — LlamaCppBackend: ZAMKNIĘTA.
- Faza 5 — Cloud: ZAMKNIĘTA.
- Faza 6 — Apertium: ZAMKNIĘTA wg dotychczasowej weryfikacji adaptera/backendu/runtime/language plugins.
- Faza 7 — Document Services: ZAMKNIĘTA; DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF są zweryfikowane.
- Faza 8 — Translator: ZAMKNIĘTA; ChunkPlanner, PromptBuilder, TranslationExecutor, TranslationCache, ResultValidator, TranslationOrchestrator i DocumentTranslationService są zweryfikowane.
- Faza 9 — GUI: ZAMKNIĘTA; kontrolery aplikacyjne i testy kontraktowe są zweryfikowane.
- Faza 10 — legacy removal: ZAMKNIĘTA po audycie zero-reference.

### Weryfikacja Fazy 10 — legacy removal

Audyt V4 wykazał:
- brak referencji do `fastapi`, `FastAPIServerManager`, `fastapi_server`, `openvino`, `openvino_backend` i `TranslateGemma INT8` w aktywnym kodzie oraz testach;
- brak plików FastAPI/OpenVINO w `src/`, `tests/` i aktywnej dokumentacji technicznej;
- brak tych zależności w `pyproject.toml`;
- brak konfiguracji tych technologii w plikach konfiguracyjnych V4;
- brak feature flags odnoszących się do tych technologii;
- brak zastąpionych ścieżek dokumentowych wskazujących na te komponenty.

Pozostałe wystąpienia nazw FastAPI/OpenVINO znajdują się w dokumentacji migracyjnej i baseline V3 jako opis źródła oraz decyzji migracyjnej; nie są aktywnymi referencjami runtime.

Weryfikacja:
- zero-reference scan aktywnego kodu/testów/konfiguracji — PASS;
- struktura planu Fazy 9/10/11 — PASS;
- pełny pytest — 180 passed;
- Ruff — PASS;
- mypy — PASS, 60 plików źródłowych.

### Następny etap

Faza 11 — packaging.

### Faza 11 — packaging — rozpoczęta, ZABLOKOWANA

Wykonano audyt dependency closure i backup przed zmianami:
- backup: `.migration-backups/pre-packaging-phase11-20260930.tar.gz`;
- do V4 skopiowano kontrolowany runtime Okapi z V3 do `filtry/runtime` (42 pliki, 22 MiB);
- wykryto brak wcześniej deklarowanego `filtry/runtime`, przez co launcher Java nie miał kompletnego runtime'u;
- próba zbudowania wheel w checkoutcie jest blokowana przez własność repozytorium nadrzędnego (`setuptools`/Git zgłasza `dubious ownership`);
- próba zbudowania danych Apertium z kopii roboczej zakończyła się błędem uprawnień podczas czyszczenia stagingu w `/tmp`; etap został zatrzymany;
- V3 nie był celowo modyfikowany.

**Kryterium Fazy 11 nie jest jeszcze spełnione.** Nie oznaczono żadnego punktu packagingu jako zakończonego bez pełnej weryfikacji.

### Faza 11 — packaging — częściowo wykonana, nadal OTWARTA

Po ponowieniu pracy ze stagingiem `./temp`:
- zbudowano `tlumacz-0.40.0-py3-none-any.whl` (~43 MiB);
- wheel zawiera Okapi runtime, Java Filter Host, prywatny runtime Apertium oraz NOTICE/licencje;
- clean install z wheel: PASS;
- `tlumacz --version`: `0.40.0`;
- Java Filter Host z zasobów zainstalowanego wheel: PASS;
- Apertium engine 3.9.12 z zasobów zainstalowanego wheel: PASS;
- pełny pytest: 182 passed;
- Ruff: PASS;
- mypy: PASS, 60 plików.

Pozostają blokady:
- brak kompletnego `eng-pol.t1x.bin`; próba odtworzenia z V3 kończy się `Undefined attr-item cas_sp` podczas `apertium-preprocess-transfer`;
- brak Windowsowego runtime'u Apertium/pozostałych natywnych zasobów — obecny artefakt jest Linux x86-64;
- pełne zamknięcie dependency closure i audytu licencji komponent-po-komponencie wymaga dalszej weryfikacji.

Kryterium Fazy 11 nadal **NIESPEŁNIONE**.
### Faza 12 — release 0.40.0 — RELEASE CANDIDATE

Zweryfikowano:
- pełny pytest: **182 passed**;
- compileall: **PASS**;
- Ruff: **PASS**;
- mypy: **PASS**, 60 plików;
- integration/E2E: **19 passed**;
- clean install Linux z wheel bez zależności: **PASS**;
- wersja artefaktu: **0.40.0**;
- Java Filter Host z wheel: **PASS**;
- Apertium engine 3.9.12 uruchamia się z wheel.

Artefakt: temp/wheel/tlumacz-0.40.0-py3-none-any.whl

SHA-256: 161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835

Dokumentacja Fazy 12:
- docs/release/RELEASE_NOTES_0.40.0.md;
- docs/archive/migration/MIGRATION_NOTES_V3_TO_V4.md;
- docs/release/ROLLBACK_0.40.0.md;
- docs/reports/FAZA_12_RELEASE_2026-09-30.md.

Faza 12 nie jest zamknięta. Pozostają Windows oraz packaging/dependency/licencje z Fazy 11.

Słownik nie jest blockerem: pozostaje osobnym zasobem i może zostać dodany później.

### Faza 13 — finalny handoff i freeze

Faza 13 została zamknięta jako lokalny handoff freeze. Udokumentowano aktualny stan Release Candidate 0.40.0, artefakt, SHA-256, backup dokumentacji oraz blokery pozostające z Fazy 11/12. Nie wykonano i nie wykonuje się push do GitHub.

Raport: docs/reports/FAZA_13_FINAL_HANDOFF_2026-09-30.md.

Finalny release 0.40.0 pozostaje otwarty przez Apertium eng-pol, Windows oraz dependency/licencje.

## Zmiana oficjalnego katalogu projektu V4 i czyszczenie plików tymczasowych — 2026-10-01

Oficjalnym katalogiem projektu V4 jest od tej chwili:

`/home/frs/Projekty/tlumacz-v4/`

Dotychczasowy katalog `/home/frs/Projekty/agent-translator-v4/` nie jest już traktowany jako bieżący katalog projektu.

W nowym katalogu wykonano pełne, rekurencyjne przejście przez wszystkie podkatalogi. Przed czyszczeniem znaleziono 513 plików pasujących do wzorca `*.bak*`, o łącznym rozmiarze około 2,9 MiB.

Usunięto wyłącznie te pliki `*.bak*`. Nie usuwano katalogów, plików projektu, dokumentacji, kodu, testów ani innych plików tymczasowych o innych nazwach.

Po czyszczeniu:
- liczba pozostałych plików `*.bak*`: 0;
- liczba katalogów w drzewie projektu: 970;
- liczba pozostałych zwykłych plików: 6449.

Czyszczenie objęło również podkatalogi archiwów i raportów. Nie wykonywano usuwania w starym katalogu `/home/frs/Projekty/agent-translator-v4/`.

Uwaga: `/home/frs/Projekty/tlumacz-v4/` nie zawiera obecnie katalogu `.git`. Stan repozytorium Git nie został przez tę operację zmieniony.

## Audyt inżynierski i naprawa jakościowa — 2026-10-01

Po wskazaniu właściwego katalogu projektu wykonano pełny przegląd dokumentacji, kodu, testów, statycznej analizy i packagingu.

### Wyniki bieżącej weryfikacji
- pytest: **182 passed**;
- Ruff: **PASS**;
- mypy: **PASS**, 60 plików;
- compileall: **PASS**;
- PYTHONPATH=src python3 -m tlumacz --version: **PASS**, 0.40.0;
- świeży venv z wheel: python -m tlumacz --version **PASS**;
- świeży venv z wheel: tlumacz --version **PASS**;
- Apertium runtime/E2E: **6 passed**;
- kompilacja eng-pol.t1x.bin: **BLOCKED** przez Undefined attr-item cas_sp.

### Naprawione
- import ordering w processor.py i test_docx_filter.py;
- Ruff nie analizuje regenerowalnego stagingu temp/ ani backupów migracyjnych;
- aktywne dokumenty migracyjne wskazują /home/frs/Projekty/tlumacz-v4/.

### CLI
Błąd z systemowego interpretera wynikał z importowania globalnego pakietu /usr/lib/python3.14/site-packages/tlumacz. Istniejące stare środowiska miały shebangi wskazujące na historyczny /home/frs/Projekty/agent-translator-v4. Świeży venv z aktualnego wheel działa poprawnie.

### Apertium
Nie wprowadzono niezweryfikowanej poprawki do cas_sp. Lokalny plik transferu i upstreamowa wersja apertium-eng-pol używają cas_sp bez deklaracji atrybutu; aktualny compiler odrzuca plik. Blokada pozostaje częścią Fazy 11.

## Regresja GUI/Cloud V3 → V4 — audyt i naprawa — 2026-10-01

Wykryto i naprawiono regresywną migrację GUI/Cloud. V4 nie posiadał wcześniej warstwy Qt ani większości providerów Cloud V3.

### Stan po naprawie
- GUI Qt V4: ODTWORZONE jako adapter nad warstwą aplikacyjną;
- aktywne backendy GUI: llama.cpp, Apertium, Cloud;
- FastAPI/OpenVINO: NIEPRZYWRÓCONE;
- providerzy Cloud: 8 adapterów;
- profile Cloud: 12;
- Mozhi GUI: ODTWORZONE;
- test GUI offscreen: 3 passed;
- test kompatybilności providerów V3: 21 passed;
- pełny suite: 195 passed;
- Ruff: PASS;
- mypy: PASS — 68 plików;
- compileall: PASS;
- wheel 0.40.0: BUILD PASS.

Raport niezgodności: docs/Audyt/AUDYT_REGRESJI_GUI_CLOUD_V3_V4_2026-10-01.md.
Raport naprawy: docs/Audyt/RAPORT_NAPRAWY_GUI_CLOUD_2026-10-01.md.
Plan: docs/archive/plans/PLAN_NAPRAWCZY_GUI_CLOUD_2026-10-01.md.
Backup: .migration-backups/pre-gui-cloud-repair-20261001.tar.gz.

## Uzupełnienie — pełna powierzchnia UI — 2026-10-01

Porównanie objectName V3/V4 potwierdziło brakujące elementy zakładek Dodatki/Pomoc. Odtworzono aktywną powierzchnię UI, z wyłączeniem elementów FastAPI/OpenVINO. Test powierzchni: 1 passed; testy GUI razem: 4 passed.

Końcowa weryfikacja tego etapu: **196 passed**, Ruff PASS, mypy PASS (68 plików), compileall PASS, wheel PASS.

## 2026-10-01 — zgłoszenie: serwer llama.cpp nie uruchamia się

- **Status:** zgłoszone, nierozpoznana przyczyna.
- **Komponent:** serwer/runtime llama.cpp.
- **Objaw:** serwer llama.cpp nie uruchamia się.
- **Klasyfikacja:** błąd funkcjonalny do reprodukcji i diagnozy.
- **Priorytet:** P1 — blokuje lokalny backend llama.cpp.
- **Przyczyna:** jeszcze nieustalona; nie zakładamy na tym etapie błędu konfiguracji, modelu, parametrów procesu ani środowiska.
- **Następny krok:** zebrać dokładny komunikat/log uruchomienia oraz ustalić, jaki executable, model i konfiguracja są faktycznie używane.


## Porządkowanie dokumentacji po migracji — 2026-10-01

Wykonano pierwszą uporządkowaną falę dokumentacji po migracji V3 → V4.

- V3 został potraktowany jako źródło historyczne; nie przenoszono ani nie usuwano jego dokumentów.
- Utworzono pełny rejestr wszystkich plików pod docs/: docs/INDEX.yml oraz mapę docs/INDEX.md.
- Utworzono docs/DOCUMENTATION_CHANGELOG.md jako dziennik zmian dokumentacji.
- Utworzono docs/RETIRED_FUNCTIONALITY.md jako jednoznaczny rejestr funkcji wycofanych.
- FastAPI + Transformers oraz stara ścieżka OpenVINO z modelem TranslateGemma INT8 są oznaczone jako WYCOFANE.
- Stary model V3 BackendManager/MainWindow nie jest traktowany jako aktywna architektura V4.
- Zaktualizowano indeks dokumentacji technicznej oraz dokumentację modeli/runtime.
- Przestarzały BUG.md V3 zastąpiono listą aktualnych ryzyk i blockerów V4.
- Historyczne dokumenty Windows i raporty zawierające stare ścieżki otrzymały jawne oznaczenia historyczne.
- Nie wykonywano usuwania funkcji, instalacji oprogramowania ani migracji fizycznej całej dokumentacji.

### Bieżąca reguła utrzymania

Po każdej zmianie dokumentacji należy odświeżyć INDEX.yml i dopisać wpis do DOCUMENTATION_CHANGELOG.md. Przed zmianą statusu dokumentu należy sprawdzić kod, testy i najnowszy audyt.

## 2026-10-01 — GUI: niewłaściwe zakładki / backendy

Zgłoszono niewłaściwy układ zakładek oraz brak współczesnego backendu przy jednoczesnej obecności dwóch starszych backendów. Do porównania wykorzystać działające GUI V3.2 jako referencję UX, natomiast backendy V4 pozostają: llama.cpp, Apertium, Cloud. Najpierw ustalić, jaki kod GUI jest faktycznie uruchamiany.

## Aktualizacja 2026-10-01 — korekta macierzy GUI/Cloud

- SimplyTranslate został usunięty z aktywnego V4 po decyzji o wycofaniu integracji z powodu braku skutecznego połączenia.
- DLX pozostaje wymaganym providerem Cloud.
- Własny endpoint pozostaje wymaganiem parytetu funkcjonalnego: docelowo selector ma mieć kategorię **Własny**, a konfiguracja adresu ma być edytowalna po jej wybraniu.
- TranslateGemma należy traktować jako specjalną funkcję/szablon dla kodów językowych, nie jako automatyczny start llama.cpp.
- Po usunięciu SimplyTranslate pełna regresja testowa: **197 passed** (QT_QPA_PLATFORM=offscreen).

## 2026-10-01 — refaktoryzacja rdzenia MainWindow rozpoczęta

Rozpoczęto wydzielanie kompetencji z warstwy Qt do warstwy aplikacyjnej.

- dodano BackendService jako fasadę nad aktywnymi backendami V4;
- dodano TranslationApp jako rdzeń aplikacyjny bez zależności od Qt;
- runtime llama.cpp został przeniesiony z bezpośredniej obsługi MainWindow do TranslationApp;
- qt_gui/app.py pełni teraz composition root i przekazuje rdzeń do MainWindow;
- MainWindow nie importuje już bezpośrednio BackendRegistry, BackendSelection ani LlamaCppRuntimeManager;
- pełny pytest: **199 passed**;
- Ruff: **PASS**;
- compileall: **PASS**.

Pozostaje dalsze wydzielanie ustawień, dokumentów, diagnostyki, postępu i pozostałej logiki GUI. BUG-007 pozostaje otwarty do czasu zakończenia tej refaktoryzacji.


### P0 — launcher V4 — zamknięty dla uruchamiania ze źródła

2026-10-01 naprawiono konflikt runtime V3/V4 przy uruchamianiu z katalogu `/home/frs/Projekty/tlumacz-v4`.

- usunięto lokalny symlink `tlumacz -> src/tlumacz`; jedynym źródłem pakietu pozostaje `src/tlumacz/`, a uruchamianie ze źródeł używa jawnego `PYTHONPATH=src`;
- nie zmieniano ani nie usuwano globalnego pakietu V3 `0.31.2`;
- zaktualizowano regresję bootstrapu do jawnego `PYTHONPATH=src`;
- `python -m tlumacz --version` zwraca `0.40.0`;
- import `tlumacz.qt_gui.app` wskazuje V4;
- pełny suite z `QT_QPA_PLATFORM=offscreen`: **201 passed**;
- Ruff: **PASS**;
- compileall: **PASS**.

Budowa wheel nadal ma niezależną blokadę własności nadrzędnego drzewa Git (`/home/frs/Projekty`); nie została ona rozwiązana przez zmianę globalnego `safe.directory`.


### P1 — dekompozycja GUI i trwałość konfiguracji — postęp 2026-10-01

W kolejnym kroku refaktoryzacji odpowiedzialności zostały rozdzielone od `MainWindow`:
- `BackendPresenter` — wybór backendu, konfiguracja widoczności i budowa selekcji;
- `SettingsPresenter` — mapowanie ustawień GUI i zapis konfiguracji;
- `DocumentPresenter` — wybór i walidacja ścieżek dokumentów;
- `ProgressPresenter` — mapowanie stanu postępu na Qt;
- `TranslationWorker` — wykonanie tłumaczenia w workerze `QObject`.

`MainWindow` zmniejszył się z 819 do **579 linii**.

Dodano trwałość `last_input_path` i `last_output_path`; `server_gguf_path` zachowuje round-trip. Test GUI obejmuje zapis tych trzech ścieżek.

Weryfikacja: **205 passed**, Ruff PASS, compileall PASS.

Pozostaje dalsza dekompozycja powierzchni budowania zakładek GUI oraz integracja diagnostyki.


## 2026-10-01 — P1 — wydzielenie builderów widoków GUI

- wydzielono budowę czterech zakładek z `MainWindow` do `qt_gui/view_builders.py`;
- `MainWindow` zmniejszono z 579 do **253 linii**;
- zachowano istniejącą powierzchnię kontrolek i callbacków Qt;
- test parytetu GUI zaktualizowano tak, aby uwzględniał `main_window.py` oraz `view_builders.py`, bez zmiany listy wymaganych kontrolek;
- dodano test kontraktowy builderów widoków;
- pełna regresja: **206 passed**;
- Ruff: **PASS**;
- compileall: **PASS**;
- backup przed zmianą: `/home/frs/Projekty/agent-translator-v3/backups/tlumacz-v4-tab-builders-20261001/pre-tab-builders.tar.gz`.

### Aktualny podział warstwy prezentacji

```text
MainWindow
├── BackendPresenter
├── SettingsPresenter
├── DocumentPresenter
├── ProgressPresenter
├── TranslationWorker
└── view_builders
    ├── build_translation_tab
    ├── build_api_tab
    ├── build_extras_tab
    └── build_help_tab
```

Ten historyczny punkt został zamknięty przez Plan 02: `DiagnosticsController` i pozostałe nieużywane kontrolery GUI usunięto po zero-reference gate. Pozostał audyt funkcji parytetowych V3/V4 oraz E2E TranslateGemma.


## 2026-10-02 — QML: uzupełnienie powierzchni Tłumaczenie i Dodatki

Izolowany prototyp src/tlumacz/qml_gui/ został rozszerzony zgodnie z bieżącym kontraktem GUI:
- usunięto z zakładki Tłumaczenie zbędny wskaźnik automatycznego źródła;
- pod paskiem postępu dodano czas tłumaczenia, bieżącą prędkość znaków/s oraz średnią po zakończeniu;
- dodano sekcję Podgląd tłumaczenia;
- w Dodatkach dodano listę skilli z przełącznikami, rozdzielenie skilli wbudowanych i użytkownika oraz przyciski Odśwież / Importuj skilla / Nowy skill;
- dodano ekspozycję bieżącego skilla użytkownika kontekst-ostatniego-chunka.md oraz ścieżki źródeł skilli;
- zachowano potwierdzone parametry LLM: Rozmiar bloku i Temperatura, a także Własny prompt;
- dodano Pomijane linie (regex).

Jest to nadal warstwa prototypowa QML: kontrolki nie są jeszcze podłączone do stanu aplikacji/backendów.


## 2026-10-02 — migracja głównego GUI do Qt Quick/QML

- Izolowany prototyp QML został podłączony do rzeczywistego `TranslationApp` przez `src/tlumacz/qml_gui/bridge.py`.
- GUI QML obsługuje rzeczywisty stan plików, konfiguracji backendu, postępu, czasu, prędkości, logu, podglądu i anulowania tłumaczenia.
- Dodano trwałe ustawienia QML, dynamiczną listę skilli użytkownika oraz akcje importu/tworzenia/odświeżania.
- Główny skrypt pakietu `tlumacz` wskazuje teraz `tlumacz.qml_gui.app:main`.
- Usunięto z drzewa źródłowego cały klasyczny interfejs `src/tlumacz/qt_gui/`.
- Dodano obsługę backendu `custom` w rejestrze aplikacyjnym, aby kontrakt GUI nie był wyłącznie wizualny.
- Dodano deklarację plików QML w `pyproject.toml`, aby były częścią artefaktu pakietu.
- Weryfikacja po migracji: **230 passed**, compileall PASS i Ruff PASS. Próba budowy wheel zatrzymała się na istniejącym problemie środowiska Git (`dubious ownership` dla `/home/frs/Projekty`); nie zmieniano konfiguracji Git.

## 2026-10-02 — pierwsza korekta podłączonego GUI QML

Po zgłoszeniu błędów rozmieszczenia i pustych/nieprawidłowych elementów interfejsu wykonano pierwszą falę zmian funkcjonalnych, bez przebudowy jeszcze karty **API i serwer**.

- usunięto wewnętrzny nagłówek „Tłumacz” oraz „V4 · Qt Quick”;
- odblokowano swobodne zmniejszanie okna;
- dodano trwałe zapisywanie i odtwarzanie pozycji oraz rozmiaru okna;
- czas tłumaczenia jest wyświetlany jako MM:SS;
- zakładkę „Dodatki” przemianowano na „Parametry”;
- język aplikacji pokazuje pełne nazwy Polski, English, Deutsch;
- skille pokazują katalog źródłowy zamiast checkboxów z nazwami plików;
- Pomoc nie ma już drugiego wyboru języka;
- Pomoc i „O programie” używają wersji **0.4.0** i zawierają właściwy tekst pomocy.

Backup przed zmianą: .migration-backups/qml-ui-immediate-20261002/pre-change.tar.gz.

Pełna regresja projektu po zmianie: **235 passed**; compileall i Ruff — PASS.


## 2026-10-03 — aktualny stan GUI QML

Główna warstwa GUI pozostaje QML/Qt Quick. W kolejnym etapie integracji:

- teksty statyczne czterech głównych stron są podłączone do kanonicznego i18n PL/EN/DE;
- profile Cloud są izolowane per usługa, a lokalny klucz llama.cpp jest przechowywany osobno;
- wybór backendu ładuje odpowiednią konfigurację Cloud lub lokalnego llama.cpp;
- stan zarządzanego serwera llama.cpp jest wystawiony bezpośrednio do QML;
- regresje GUI/QML: **28 passed**.

Pełny zakres i decyzje znajdują się w `docs/technical-docs/QML_GUI_DESIGN.md`.


## 2026-10-03 — weryfikacja runtime GUI QML

Źródła `src/tlumacz/qml_gui` i repozytoryjny shim `tlumacz/qml_gui` zawierają aktualny układ karty „Tłumaczenie”: **Pliki → Tłumacz/Anuluj/Język docelowy → Postęp → Statystyki → Log → Podgląd tłumaczenia**.

Weryfikacja wykazała, że `/usr/bin/tlumacz` należy do globalnie zainstalowanego pakietu 0.31.2 i nadal wskazuje `tlumacz.qt_gui.app:main`, dlatego uruchomienie tego polecenia pokazuje stare GUI Widgets. Aktualny launcher V4 QML ze źródła to:

```bash
cd /home/frs/Projekty/tlumacz-v4
python -m tlumacz.qml_gui.app
```

Test bootstrapu potwierdza import `src/tlumacz/qml_gui/app.py` przy jawnym `PYTHONPATH=src`.


## 2026-10-03 — końcowa korekta GUI

Wprowadzono aktualny kontrakt kart Tłumaczenie, API i serwer, Przełączniki oraz Pomoc zgodnie z ostatnimi uwagami UX. Dodano zarządzanie skillami użytkownika z filesystemu, szablon tworzenia skilla, usuwanie skilli, obsługę Mozhi i wybór języka docelowego w Pomocy.

- pełny test suite: 265 passed;
- python3 -m compileall -q src tests: PASS;
- backup przed zmianą: backups/gui-final-pass-20261003/pre-gui-final-pass.tar.gz;
- SHA-256 backupu: 25e91c7bc620e5fe23bdb6a1e937d89671f9f55e5604638cd6c8d98c6a975c76.


## 2026-10-03 — aktualizacja pomocy QML

Polska pomoc użytkownika została zaktualizowana na podstawie bieżącego `STATUS.md`, `OPIS_PROGRAMU_DLA_AGENTOW.md`, dokumentacji technicznej oraz rzeczywistego kontraktu `HelpPage.qml` i `QmlApplicationBridge`.

- źródło treści: `src/tlumacz/qml_gui/help.pl.md` (analogicznie `help.en.md` i `help.de.md`);
- aktywne backendy opisane jako `llama.cpp`, `Cloud`, `Apertium`;
- zachowano rozróżnienie modelu i backendu;
- opisano aktualny przepływ tłumaczenia, obsługiwane formaty, glosariusz, skille, diagnostykę i stan Release Candidate 0.40.0;
- testy GUI: **50 passed**; compileall: **PASS**.

## 2026-10-03 — korekta skilli i końcowych powierzchni GUI

Naprawiono ścieżkę tworzenia skilla: `newSkill()` zapisuje niepusty szablon do katalogu użytkownika. Przełączniki mają krótsze pola Glosariusza, szersze i równe pola Rozmiar bloku/Temperatura oraz przyciski ✕ przy skillach użytkownika. Apertium, Mozhi i Własny otrzymały uproszczone powierzchnie zgodnie z bieżącym kontraktem GUI.


## 2026-10-03 — naprawa renderowania pomocy Markdown w QML

Zidentyfikowano dwa problemy wpływające na wygląd Pomocy: bridge przekazywał do QML literalne `\\n` zamiast rzeczywistych znaków nowej linii, a `HelpPage.qml` używał nieprawidłowej nazwy formatu `TextEdit.Markdown`. W Qt 6 właściwą wartością jest `TextEdit.MarkdownText`.

- `QmlApplicationBridge._parse_help_file()` zachowuje teraz rzeczywiste podziały linii;
- wszystkie pięć paneli Pomocy używa `TextEdit.MarkdownText`;
- `ScrollView` wymusza szerokość treści przez `availableWidth`, dzięki czemu tekst Markdown zawija się w panelu;
- dodano marginesy, tło i możliwość zaznaczania tekstu w panelach pomocy;
- test regresyjny wykrywa literalne `\\n` w treści bridge;
- uruchomienie QML pod Xvfb oraz zrzut runtime potwierdziły poprawne renderowanie formatowania Markdown.

Backup przed zmianą: `backups/help-markdown-ui-20261003/pre-help-markdown-ui.tar.gz`.
SHA-256: `ca7cd925bf8196030b09b4d9c6be709f2ce440c158b0ed6bee3f7e2e0ef6ef8c`.

- W `ExtrasPage.qml` skrócono oba wiersze Glosariusza: około 10 mm wiersz pliku glosariusza oraz około 5 mm na każde pole Źródło/Tłumaczenie, aby przyciski Przeglądaj i Dodaj nie były obcinane.


### 2026-10-03 — mikro-korekta GUI
Glosariusz: przycisk „Przeglądaj” ma pełny napis; nagłówki Glosariusz, Umiejętności i Ustawienia LLM są pogrubione; separator nad Umiejętnościami pozostaje zachowany.


### 2026-10-03 — korekta Glosariusza
Pola Glosariusza są skracane lokalnie przed przyciskami; przyciski nie są ściskane. Pogrubione są wyłącznie tytuły Glosariusz, Umiejętności i Ustawienia LLM.


## 2026-10-03 — bieżąca korekta karty „Przełączniki”

Pole ścieżki Glosariusza jest skracane lokalnie, bez ściskania całego wiersza i przycisku **Przeglądaj**. Tytuły **Glosariusz**, **Umiejętności** i **Ustawienia LLM** są pogrubione, natomiast zawartość sekcji zachowuje normalną grubość.

Weryfikacja: tests/test_qml_gui.py — **42 passed**; python3 -m compileall -q src tests — PASS.

## 2026-10-03 — stan typografii karty „Przełączniki”
Po kontroli renderu `ExtrasPage.qml` usunięto niezamierzone pogrubienie tekstu wewnątrz sekcji. Pogrubione pozostają wyłącznie tytuły **Glosariusz**, **Umiejętności** i **Ustawienia LLM**; pozostałe elementy mają jawnie `font.bold: false`. Test regresyjny potwierdza 3 tytuły pogrubione i 26 normalnych deklaracji fontu.

## 2026-10-03 — pełna przebudowa Pomocy użytkownika

Pomoc użytkownika została przygotowana od nowa na podstawie aktualnego V4, bieżącej dokumentacji technicznej, kontraktu GUI oraz przeglądu kodu. Wykorzystano także procesowy opis przepływu tłumaczenia do uporządkowania instrukcji krok po kroku.

### Treść

- src/tlumacz/qml_gui/help.pl.md jest głównym polskim źródłem treści Pomocy;
- treść została podzielona na pięć tematów: **Na początek**, **Tłumacz dokument**, **Wybierz sposób tłumaczenia**, **Ustawienia i narzędzia**, **Wynik i problemy**;
- usunięto z pomocy odniesienia do wycofanych FastAPI, Transformers i OpenVINO;
- opisano aktywne ścieżki llama.cpp, Chmura, Apertium i Własny serwer;
- opisano formaty dokumentów, przebieg tłumaczenia, glosariusz, skille, ustawienia LLM, log, podgląd i diagnostykę;
- zachowano Markdown jako format źródłowy pomocy.

### Interfejs

- HelpPage.qml został przebudowany jako powierzchnia do czytania, a nie pole tekstowe;
- dodano HelpMarkdownView.qml jako wspólny komponent renderujący Markdown;
- usunięto wygląd TextArea z treści pomocy;
- treść jest ograniczona do szerokości czytelnej dla dłuższego tekstu i umieszczona w przewijanym polu;
- pasek tematów ma własny, jednoznaczny stan aktywny;
- język aplikacji, język docelowy, motyw i dialog **O Programie** pozostały podłączone do bridge;
- usunięto stare help.body z centralnego i18n, ponieważ rozbudowana pomoc należy do plików Markdown.

### Weryfikacja

- testy Pomocy: **9 passed**;
- pełny suite: **275 passed**;
- qmllint dla HelpPage.qml i HelpMarkdownView.qml: PASS;
- compileall: PASS;
- rzeczywisty runtime QML uruchomiony z wyłączoną pamięcią podręczną QML i sprawdzony pod Xvfb;
- zrzut runtime potwierdził czytelne nagłówki, listy, pogrubienia, przewijanie i aktywny temat;
- backup przed zmianą: backups/help-rebuild-20261003/pre-help-rebuild.tar.gz;
- SHA-256: d5cb8b80fe228a2ced692895ee1df7953de6d7174d200d95d28427dffc73afe9.

### Dokumentacja

Zaktualizowano docs/technical-docs/QML_GUI_DESIGN.md oraz docs/technical-docs/user-guide.md. Zmianę wpisano również do docs/DOCUMENTATION_CHANGELOG.md.


## 2026-10-04 — Plan 04 / llama.cpp baseline i Cloud SecretStore

- **llama.cpp:** baseline wykonany na rzeczywistym `translategemma-4b-it.Q5_K_M.gguf` z `/home/frs/Modele/`; wyniki i parametry zapisane w Planie 04. Nie zmieniono konfiguracji produkcyjnej na podstawie samego benchmarku.
- **Cloud secrets:** obowiązująca ścieżka lokalnego magazynu sekretów to `/home/frs/.config/tlumacz/.key`; plik hosta ma prawa `0600`.
- **Plan 04:** nadal `in-progress`; pozostały baseline Cloud, Filter Host/Engine i QML oraz decyzja końcowa o bezpiecznych optymalizacjach.


## 2026-10-04 — Plan 04 / Cloud baseline

- **Cloud:** baseline lokalnego routera/providerów wykonany; koszt inicjalizacji i serializacji jest pomijalny, a health-check Cloud nie generuje ruchu sieciowego.
- **Sekrety:** dane uwierzytelniające pozostają poza profilem i są zapisywane w `/home/frs/.config/tlumacz/.key` (`0600`).
- **Plan 04:** pozostały baseline Filter Host/Engine oraz QML.


## 2026-10-04 — Plan 04 / filtry

- proces Java cold-start: ~1,61 s;
- rozgrzane IPC: mediana ~0,37 ms/request;
- pipeline Markdown 200 jednostek: ~7,96 ms/document średnio;
- brak potwierdzonej bezpiecznej optymalizacji; pozostał baseline QML.


## 2026-10-04 — Plan 04 / QML baseline

- startup QML: około 0,30 s;
- drzewo root: 1309 obiektów QObject;
- refresh skills: ~0,0715 ms średnio;
- zmiana języka aplikacji: ~13,95 ms;
- brak potwierdzonej bezpiecznej optymalizacji QML; pozostał końcowy quality gate.


## 2026-10-04 — Plan 04 zamknięty

- Plan 04 optymalizacji zakończony po wykonaniu baseline'ów i quality gate.
- 268 testów przechodzi; compileall, Ruff, mypy i qmllint przechodzą.
- Nie wprowadzono nieuzasadnionych optymalizacji produkcyjnych; zachowano walidację i kontrakty.
- Sekrety Cloud: `/home/frs/.config/tlumacz/.key`, prawa `0600`.
- E2E TranslateGemma pozostaje TODO.


## 2026-10-04 — Plan 05 / finalny gate

Plan 05 został wykonany i zamknięty jako **Release Candidate gate**.

- pełny pytest: **268 passed**;
- macierz backendów: **205 passed**;
- macierz formatów dokumentów: **28 passed**;
- Filter Host/Engine: **26 passed**;
- compileall, Ruff, mypy, qmllint: **PASS**;
- clean wheel install: **PASS**, wersja `0.40.0`;
- rzeczywisty QML `Main.qml`: **PASS**;
- `docs/INDEX.yml`: **444/444** istniejących ścieżek, 0 duplikatów, poprawny YAML;
- V3: 128 zmian bazowych, bez zapisu do V3 podczas bieżącej sesji;
- Cloud SecretStore: `/home/frs/.config/tlumacz/.key`, `0600`.

Projekt pozostaje **Release Candidate**, nie final release. Otwarte blokery: Apertium eng-pol/cas_sp, Windows runtime oraz dependency closure/licencje. Dedykowane E2E TranslateGemma pozostaje TODO. `/usr/bin/tlumacz` nadal jest globalnym launcherem V3 i nie został zmieniony bez osobnej decyzji.

## 2026-10-06 — informacyjne pola języków na stronie tłumaczenia

Dwie nieedytowalne kontrolki języka źródłowego i docelowego na `TranslationPage.qml` są teraz podłączone do stanu Apertium: `apertiumSourceLanguageLabel` i `apertiumTargetLanguageLabel`. Ich sekcja pozostaje widoczna wyłącznie dla `backendType === "apertium"`. Kontrolki wyboru innych backendów zachowują własny mechanizm `targetLanguages`.
### 2026-10-06 — instalacja skompilowanej pary Apertium `eng-pol`
- Skompilowane artefakty `eng-pol` zostały umieszczone w `/home/frs/.config/tlumacz/Apertium/apertium-en-pl/` wraz z `modes.xml` i `modes/eng-pol.mode`.
- Discovery wykrywa `eng-pol`; dla źródła `en` dostępne są `pl` i `es`.
- Zweryfikowano rzeczywiste tłumaczenie `Hello world.` → `@hello #Świat.`.
- Naprawiono `ApertiumRuntime.data_dir_for_pair()`: runtime otrzymuje katalog nadrzędny paczek, zgodny ze ścieżkami względnymi używanymi przez tryby Apertium.



### 2026-10-06 — poprawka detekcji Apertium w GUI

- potwierdzono, że wstępna detekcja języka GUI korzysta z **Lingua** (LanguageDetector), a nie z LibreTranslate,
- usunięto nadpisywanie source_language wynikiem automatycznej detekcji,
- wynik Lingua jest przechowywany jako detectedSourceLanguage,
- ustawienie source_language=auto pozostaje stabilne pomiędzy kolejnymi dokumentami,
- stare zapisane źródło Apertium nie blokuje ponownej detekcji,
- dodano test regresyjny dla przypadku zapisanego wcześniej spa oraz dokumentu en/fr/de,
- testy GUI Apertium: oczekiwany stan auto + wykryty Angielski.


## 2026-10-06 — ponowna walidacja Planu 03

Ponowiono audyt regresji na aktualnym drzewie V4 zgodnie z Planem 03. Interpreter i tlumacz.__file__ wskazują /home/frs/Projekty/tlumacz-v4/src/tlumacz. Focused suite P1/P2 obejmujący Apertium, Cloud, custom, llama.cpp/TranslateGemma, GUI, persystencję ustawień i aktywne filtry dokumentowe: 128 passed. Pełny pytest: 367 passed, 0 failed. Compileall i qmllint: PASS.

Podczas pierwszego uruchomienia pełnego suite'u wystąpił pojedynczy niestabilny wynik testu TranslateGemma; ponowienie testu izolowanego oraz kolejny pełny suite przeszły. Nie potwierdzono regresji produkcyjnej ani potrzeby zmiany kodu. Ruff i mypy nadal mają opisane wcześniej problemy statyczne poza zakresem tego audytu.

### 2026-10-06 — przycisk Restart serwera llama.cpp

Przycisk `Restartuj serwer` w GUI dla backendu llama.cpp ma kontrakt: jeśli serwer nie działa, uruchamia go z aktualnymi ustawieniami; jeśli działa, wykonuje restart. Dodano regresję potwierdzającą uruchomienie llama.cpp przy braku aktywnego runtime.

## 2026-10-06 — Plan 04 / ponowny quality gate

Na aktualnym drzewie V4 ponowiono quality gate Planu 04. Usunięto 4 problemy statyczne bez zmiany kontraktu tłumaczenia: uporządkowano importy Ruff, sformatowano dwa długie fragmenty testu QML oraz doprecyzowano typowanie routingu języka w `TranslationOrchestrator` i `TranslationApp`.

- pełny pytest: **369 passed**;
- Ruff: **PASS**;
- mypy: **PASS** — 0 błędów / 67 plików;
- compileall: **PASS**;
- qmllint: **PASS**.

Plan 04 pozostaje zamknięty. Backupy zmian znajdują się w `backups/plan-04-20261006-lint-fix/` oraz `backups/plan-04-20261006-type-fix/`.

## 2026-10-06 — korekta kontraktu GUI → llama.json → llama-server

Potwierdzono i doprecyzowano przepływ konfiguracji llama.cpp. Aktualny stan GUI (config.json) dostarcza parametry operacyjne: GGUF, host, port, tryb obliczeń, parallel, szablon czatu i rozmiar bloku. $HOME/.config/tlumacz/llama.json dostarcza tuning techniczny: threads, threads_batch, batch, ubatch, context, cache, Flash Attention, repack, NUMA, GPU layers, KV unified i polling.

Usunięto rozjazd w trybie auto: threads=auto jest teraz rozwiązywane według liczby rdzeni fizycznych, a threads_batch=auto według liczby wątków logicznych. Test regresyjny potwierdza serializację tych wartości do komendy llama-server.

## 2026-10-06 — ścieżka GGUF

GUI jest źródłem ścieżki modelu GGUF. Po wyborze w GUI ścieżka jest zapisywana w $HOME/.config/tlumacz/config.json. llama.json nie przechowuje ani nie wybiera modelu; służy wyłącznie do tuningu llama.cpp.


## 2026-10-06 — walidacja zależności pakietów filtrów

Dodano FilterDependencyValidator dla filters/<nazwa>/filter.json. Deskryptor może deklarować wymagane JAR-y, klasy oraz odnośniki do źródeł zależności. Filtr ze niespełnioną zależnością otrzymuje usable=False; mechanizm nie pobiera ani nie instaluje brakujących bibliotek.

QmlApplicationBridge waliduje magazyn przy starcie oraz obserwuje katalog filters/ przez QFileSystemWatcher, więc dodanie nowego pakietu w czasie działania aplikacji jest wykrywane bez restartu. Każda brakująca zależność jest dopisywana do Logu GUI i wyświetlana w modalnym oknie komunikatu. Odnośniki z deskryptora są klikalne.

OpenXML otrzymał deklarację zależności TwelveMonkeys Common IO dla klas com.twelvemonkeys.io.ole2.*. Biblioteka nie została pobrana ani zainstalowana; przy obecnym stanie pakietu OpenXML walidator prawidłowo oznacza filtr jako nieużytkowy i zgłasza brak zależności.

Weryfikacja TDD: walidator 4 passed; regresje GUI walidacji 3 passed. Pełny pytest: 400 passed, 2 failed. Pozostałe dwa failure są niezależne: brak u+x w 34 plikach prywatnego runtime Apertium oraz niemieckie tematy Pomocy zamiast oczekiwanych polskich.

Backup zmienionych artefaktów: backups/filter-dependency-validation-20261006/pre-integration.tar.gz, SHA-256 04b407ca51d16de72f538da3769293ec67df63c67407fbfc15ff4677b58f20a3.


### 2026-10-06 — poprawka ładowania Main.qml
- Usunięto błąd QML `Property value set multiple times` powodowany przez dwa handlery `Component.onCompleted` w `ApplicationWindow`.
- Oba działania startowe zostały zachowane i połączone w jeden handler: przywracanie pozycji okna oraz `bridge.showNextFilterDependencyWarning()`.
- Nie zmieniono kontrolek, ich bindingów, sygnałów ani układu stron.
- `qmllint src/tlumacz/qml_gui/Main.qml` przechodzi bez błędów.
- Test regresyjny potwierdza istnienie dokładnie jednego `Component.onCompleted` i zachowanie obu operacji startowych.


### 2026-10-06 — poprawka ładowania Main.qml
- Usunięto błąd QML `Property value set multiple times` powodowany przez dwa handlery `Component.onCompleted` w `ApplicationWindow`.
- Oba działania startowe zostały zachowane i połączone w jeden handler: przywracanie pozycji okna oraz `bridge.showNextFilterDependencyWarning()`.
- Nie zmieniono kontrolek, ich bindingów, sygnałów ani układu stron.
- `qmllint src/tlumacz/qml_gui/Main.qml` przechodzi bez błędów.
- Test regresyjny potwierdza istnienie dokładnie jednego `Component.onCompleted` i zachowanie obu operacji startowych.


### 2026-10-06 — wskaźnik aktywnej pracy w statystykach tłumaczenia
- W `TranslationPage.qml` dodano animowaną kulkę `translationWorkIndicator` na początku wiersza zawierającego licznik czasu.
- Wskaźnik korzysta z istniejącego `bridge.isTranslating`; nie wprowadzono drugiego stanu pracy.
- Kulka jest widoczna i obraca się wyłącznie podczas aktywnego tłumaczenia. Po zakończeniu lub błędzie znika.
- Dodano punkt świetlny na kulce, aby ruch obrotowy był wizualnie jednoznaczny.
- Dodano test regresyjny oraz zweryfikowano `qmllint` dla `TranslationPage.qml`.

## TPlugin — stan 2026-10-06

Wdrożono fundament formatu pluginów filtrów Okapi:
- manifest TPlugin i builder Python;
- bezpieczny instalator do rozpakowanego magazynu runtime;
- centralny shared-libs z deduplikacją po identyfikatorze, wersji i SHA-256;
- Java FilterHost ładuje pluginy z lib/ oraz shared-libs;
- walidator zależności rozpoznaje zależności shared z manifestu;
- OpenXML zweryfikowano jako pierwszy rzeczywisty plugin w izolowanym profilu testowym.

Pełny suite po zmianach: **411 passed, 2 failed**. Oba FAIL są niezależnymi, wcześniej znanymi problemami: prawa wykonywania prywatnego runtime Apertium oraz niemieckie tematy Pomocy zamiast polskich. Testy TPlugin/FilterHost/dependency: **13 passed**.

Pełna migracja pozostałych filtrów do .tplugin pozostaje w trakcie i nie została jeszcze przełączona jako jedyna ścieżka runtime.
### 2026-10-06 — wskaźnik aktywnego tłumaczenia QML
- Poprawiono animowany wskaźnik pracy na stronie tłumaczenia: zastosowano `NumberAnimation on rotation`, uruchamiany wyłącznie podczas `bridge.isTranslating`.
- Średnica kulki zwiększona z 12×12 do 24×24 px (2×).
- Backup przed zmianą: `backups/qml-translation-orb-20261006/pre-change.tar.gz` (SHA-256: `3add2a4edd8178d157d6b02d7286e1600265324b4b264e90be57e44da205115a`).
## Aktualizacja 2026-10-06 — przygotowanie paczek TPlugin

Przygotowano wszystkie dziewięć filtrów Okapi obecnych w repozytorium jako paczki instalacyjne .tplugin: EPUB, HTML, JSON, Markdown, OpenOffice, OpenXML, XLIFF 1.2, XLIFF 2 i YAML.

Artefakty znajdują się w build/tplugins/. Nie są kopiowane do magazynu runtime.

Zweryfikowano:
- 14 ukierunkowanych testów TPlugin/FilterHost — PASS;
- instalację 9/9 paczek do pustego profilu — PASS;
- capabilities FilterHost 9/9 — PASS;
- brak archiwów .tplugin po instalacji — PASS;
- deduplikację shared-libs — PASS;
- OpenXML przez java/filter-host/run.sh — PASS.

Klasyfikacja A/B/C została zapisana w tools/tplugin/build_all.py. Biblioteki współdzielone są dostarczane w każdej paczce, która ich wymaga, ale po instalacji przechodzą do centralnego shared-libs.

To nie oznacza jeszcze pełnego przełączenia aplikacji na TPlugin jako jedyne źródło runtime. Migracja FilterStore/FilterRegistry oraz pełny E2E round-trip pozostają kolejnym etapem.

### 2026-10-06 — natychmiastowe anulowanie tłumaczenia llama.cpp
- Naprawiono anulowanie aktywnego tłumaczenia: żądanie z GUI ustawia token anulowania i natychmiast zatrzymuje należący do aplikacji proces llama.cpp.
- Dzięki temu blokujące oczekiwanie HTTP nie musi czekać do timeoutu; generacja zostaje przerwana razem z procesem backendu.
- Worker rozróżnia anulowanie od błędu transportu i nie zgłasza anulowania jako błędu tłumaczenia.
- Dodano osobny status `status.cancelled` dla PL/EN/DE oraz testy regresyjne.
- Backup przed zmianą: `backups/cancel-llama-immediate-20261006/pre-change.tar.gz` (SHA-256: `3cdb27ff3b92f1f715622ea996ec438152706de43b112f907d85eb5b9b5b4f3f`).

## Aktualizacja 2026-10-06 — migracja runtime na TPlugin

Migracja wykonawcza filtrów została przełączona na nowy format.

Produkcyjny magazyn rozpakowanych pluginów:
$HOME/.config/tlumacz/filter-engine/plugins/

Centralny magazyn shared:
$HOME/.config/tlumacz/filter-engine/shared-libs/

Zainstalowano 9/9 pluginów:
EPUB, HTML, JSON, Markdown, OpenOffice, OpenXML, XLIFF 1.2, XLIFF 2, YAML.

FilterRegistry odkrywa pluginy z plugin.json, mapuje extensions i tworzy adapter dopiero po rozpoznaniu dokumentu. Repozytoryjne filters/ pozostaje źródłem builda, nie runtime.

Katalog dystrybucyjny nierozpakowanych paczek:
dist/tplugins/

Smoke FilterHost na runtime /home/frs/.config/tlumacz/filter-engine/: 9/9 capabilities PASS.

Backup runtime wykonany przed przełączeniem:
backups/tplugin-migration-20261006/runtime-home-frs/filter-engine-before-runtime-switch.tar.gz
SHA-256: 8e1479b9b51a1f08ae38ee8321ce354ce2c27dcd4649d4fad74c2605f2e34709

Pozostaje TODO-022m: pełny extract/merge/round-trip oraz macierz update/uninstall/rollback.

Dodatkowa weryfikacja po przełączeniu:
- 4 testy rzeczywistego Okapi extract/merge na zainstalowanych pluginach — PASS;
- DOCX, ODT, HTML, Markdown, EPUB round-trip — PASS;
- XLIFF 1.2/2.0 automatyczny wybór wersji i merge — PASS;
- obsługa duplikatów identyfikatorów jednostek EPUB — PASS.

TODO-022m pozostaje otwarte wyłącznie dla macierzy lifecycle: update/uninstall/rollback.

Końcowa walidacja funkcjonalna wszystkich dostępnych formatów:
- 5 testów integracyjnych — PASS;
- obejmują 9 formatów: DOCX, ODT, HTML/XHTML, Markdown, EPUB, XLIFF 1.2, XLIFF 2.0, JSON, YAML;
- rzeczywisty extract/merge przez zainstalowany runtime TPlugin — PASS.
Pozostaje wyłącznie macierz lifecycle: update/uninstall/rollback.

## 2026-10-06 — paczki par językowych Apertium

Wprowadzono format dystrybucyjny pojedynczej pary Apertium jako **niekompresowany `.tar`**. Jedna paczka zawiera dokładnie jeden kierunek, manifest, SHA-256, `modes.xml`, tryb i wyłącznie skompilowane pliki wymagane przez ten tryb.

Dodano `src/tlumacz/backends/apertium/packages.py` z builderem i bezpiecznym instalatorem. Instalator sprawdza strukturę archiwum, manifest, checksumy i ścieżki przed zapisaniem danych do `$HOME/.config/tlumacz/Apertium/` oraz synchronizuje tryb do magazynu `modes/`.

Przygotowano w historycznym repozytoryjnym magazynie paczek cztery paczki z istniejących skompilowanych danych:
- `apertium-eng-pol-1.0.0.tar` — ok. 1.3 MB;
- `apertium-eng-spa-1.0.0.tar` — ok. 2.9 MB;
- `apertium-spa-eng-1.0.0.tar` — ok. 2.3 MB;
- `apertium-bn-en-1.0.0.tar` — ok. 570 KB.

Weryfikacja instalacji wszystkich czterech artefaktów do tymczasowych magazynów: każda paczka została poprawnie rozpakowana i ponownie wykryta jako dokładnie jeden kierunek. Potwierdzono również, że archiwum jest niekompresowanym tar.

`pol-eng` został naprawiony i jest publikowany jako `apertium-pol-eng-1.0.0.tar`. `hye-eng` został usunięty z lokalnego magazynu runtime i nie należy do bieżącego inventory.

Dokumentacja: `docs/technical-docs/apertium-pair-packages.md`.


## 11. Zarządzanie zależnościami TPlugin — 2026-10-06

System TPlugin posiada teraz pełny lifecycle zależności shared:

- kanoniczna tożsamość id+version+SHA-256;
- współistnienie wielu wersji;
- trwały shared-libs/index.json z referencjami pluginów;
- odbudowa indeksu z aktywnych plugin.json;
- GC tylko dla artefaktów bez referencji;
- inventory.json i checksums.json generowane przez builder;
- narzędzie tools/tplugin/dependencies.py: inventory, validate, rebuild, gc.

Weryfikacja 2026-10-06: tests/test_tplugin.py — 16 passed; walidacja paczek — 9/9; runtime gc --dry-run — 0 artefaktów do usunięcia.

Dokument architektury: docs/technical-docs/tplugin-zarzadzanie-zaleznosciami.md.


## 12. Backend administracyjny TPlugin — 2026-10-06

Dodano niezależny backend tools/tplugin_admin/, który nie jest częścią aplikacji Tłumacz. Udostępnia init, validate, build, verify i inspect. Backend korzysta z istniejącego TPluginBuilder/TPluginInventory.

Dodano również instrukcję ręcznego tworzenia paczek dla zaawansowanych użytkowników: docs/technical-docs/tplugin-reczne-tworzenie.md.

Weryfikacja bieżąca: 8 testów backendu PASS oraz rzeczywisty przepływ init → validate → build → verify → inspect PASS.

## 2026-10-06 — audyt i automatyzacja paczek par Apertium

Przeprowadzono pełny audyt lokalnych checkoutów `Aperitium/` oraz magazynu runtime Apertium. Rozpoznano kierunki dwukierunkowe jako niezależne artefakty: np. `eng-spa` i `spa-eng` są publikowane jako dwa osobne pliki.

Dodano pipeline `tools/apertium/package_pipeline.py` oraz CLI `tools/apertium/package_pairs.py`. Pipeline automatycznie wykrywa kompletne mode, buduje osobną paczkę dla każdego kierunku, może pobrać repozytorium z GitHub, uruchomić istniejący `Aperitium/apertium-get.py`, wygenerować checksumy i opcjonalnie oczyścić magazyn runtime.

Builder filtruje teraz `modes.xml` do jednego kierunku, dzięki czemu paczka nie zawiera definicji innych par.

Przygotowano **28 niekompresowanych paczek .tar** w historycznym repozytoryjnym magazynie paczek, obejmujących 14 rodzin dwukierunkowych oraz `eng-pol` i `pol-eng`. `pol-eng` przechodzi instalację oraz rzeczywisty test runtime. `hye-eng` został usunięty z magazynu runtime.

Magazyn `$HOME/.config/tlumacz/Apertium/` został oczyszczony z materiałów developerskich; pozostawiono wyłącznie dane potrzebne przez zachowane tryby i licencje. Backup wykonano przed operacją.

Weryfikacja: wszystkie 27 paczek zainstalowano do czystego magazynu tymczasowego i wszystkie 27 ponownie wykryto przez mechanizm pluginów.

Dokumentacja: `docs/technical-docs/apertium-pair-packages.md` oraz `docs/technical-docs/apertium-pair-inventory-20261006.md`.

## 2026-10-06 — domknięcie TODO-TPLUGIN-004: backend administracyjny

Backend administracyjny TPlugin pozostaje poza aplikacją Tłumacz i obsługuje przygotowanie paczek.

- dodano `test-install`, który wykonuje rzeczywistą instalację paczki przez produkcyjny `TPluginInstaller` w tymczasowym runtime;
- dodano `publish`, który buduje paczkę, wykonuje test instalacyjny i zapisuje raport publikacyjny JSON;
- raport zawiera SHA-256 artefaktu, inventory, wynik testu instalacyjnego, checksumy, ostrzeżenia i błędy;
- CLI zachowuje wcześniejsze polecenia `init`, `validate`, `build`, `verify` i `inspect`;
- `tests/test_tplugin_admin.py`: **11 passed**;
- wykonano backup przed rozszerzeniem: `backups/tplugin-admin-20261006/pre-admin-completion.tar.gz`;
- TODO-TPLUGIN-004 jest **ZAMKNIĘTE**.
## 2026-10-06 — Security/Lifecycle: faza 1

- Rozpoczęto realizację `PLAN-07-SECURITY-LIFECYCLE-2026-10-05.md`.
- Legacy klucze API są migrowane do `$HOME/.config/tlumacz/.key` przed dalszym użyciem ustawień; migracja obejmuje wszystkie profile Cloud.
- `config.json` nie otrzymuje kluczy API przy zapisie przez bridge.
- `TranslationApp.close()` zapewnia próbę zamknięcia cache także po błędzie shutdown runtime.
- `TranslationApp.stop_llama()` zgłasza niezamknięty proces i zachowuje referencję runtime, jeśli ownership identity nie pasuje; zapobiega to cichym orphan processes.
- Focused TDD: **30 passed**; Ruff dla zmienionego zakresu: **PASS**.
- Backup: `backups/SECURITY-LIFECYCLE-PHASE1-2026-10-06.tar.gz`.
- Segment pozostaje otwarty do pełnej walidacji suite + ResourceWarning/orphan-process gate.

## 2026-10-06 — Security/Lifecycle: ResourceWarning gate

- TranslationCache otrzymał awaryjny finalizer __del__; jawne close() pozostaje podstawowym mechanizmem shutdown.
- Focused suite z -W error::ResourceWarning: **32 passed**.
- W tym zakresie nie wykryto niezamkniętych połączeń SQLite ani orphan llama.cpp.
- Pełny suite pozostaje zablokowany przez niezależny failure test_document_translation_service_applies_skip_patterns_before_backend oraz niestabilny fatal abort Filter Engine po wcześniejszych failure'ach.

## 2026-10-07 — Stan po unifikacji konfiguracji

Trwała konfiguracja GUI została scalona do jednego pliku `$HOME/.config/tlumacz/config.json`. `settings-v4.json` nie jest już używany przez kod i został usunięty z aktywnego katalogu konfiguracji po wykonaniu kopii zapasowej. `AppSettings`, `load_settings()` i `save_settings()` korzystają bezpośrednio z `config.json`.


## 2026-10-07 — PLAN-07 gate / konfiguracja

- Kanoniczny plik trwałej konfiguracji GUI: `$HOME/.config/tlumacz/config.json`.
- `settings-v4.json` nie jest używany przez aktywny kod i nie może być tworzony ponownie.
- Wykonano backup przed dalszą pracą nad gate: `backups/PLAN-07-GATE-PRECONFIG-2026-10-07.tar.gz` (SHA-256: `1cc4c1d870a45a7146a67bbcf3695210dd4c0c2661d36debb3eed1f81373e972`).
- Świeży pełny suite został uruchomiony; PLAN-07 pozostaje otwarty do czasu wyniku pełnej walidacji oraz końcowej kontroli ResourceWarning/orphan processes.

## 2026-10-07 — Unifikacja konfiguracji: wynik i problemy walidacyjne

### Stan docelowy

- Jest **jeden kanoniczny plik trwałej konfiguracji GUI**: `$HOME/.config/tlumacz/config.json`.
- `settings-v4.json` nie jest aktywnym plikiem konfiguracji i został usunięty po wykonaniu backupu.
- `AppSettings`, `load_settings()` i `save_settings()` wskazują na `config.json`.
- `llama.json` pozostaje osobnym plikiem technicznego tuningu runtime llama.cpp; nie jest drugim plikiem ustawień GUI.
- Sekrety API pozostają poza `config.json`, w `SecretStore`.

### Co nie poszło / ograniczenia

- Pierwsza próba uruchomienia pełnego suite zakończyła się fatalnym `Aborted` w Qt/PySide6 podczas raportowania wcześniejszych failure'ów; w stack trace widoczne były również wątki Filter Engine. Nie należy traktować tego jako dowodu, że migracja konfiguracji jest przyczyną awarii.
- Pełny suite pozostaje wymagający dalszej walidacji. Ukierunkowany zakres konfiguracji i GUI zakończył się **41 passed**.
- W `tests/test_llama_config.py` pozostał jeden świadomy testowy zapis `settings-v4.json` w asercji negatywnej (`CONFIG_PATH.name != ...`); nie jest to odwołanie runtime, ale dokumentacyjnie należy je pozostawić tylko jako zabezpieczenie przed powrotem legacy.
- W dokumentacji historycznej pozostały odniesienia do `settings-v4.json`, które opisują stan historyczny. Nie należy ich przepisywać jako faktów o aktualnej konfiguracji; aktualny kontrakt jest opisany powyżej.


## 2026-10-07 — poprawki llama.cpp / TranslateGemma / Markdown

- Wybór backendu **llama.cpp** z innego backendu uruchamia zarządzany serwer automatycznie, jeżeli `config.json` ma `auto_start_server=true`; komunikat nie instruuje już użytkownika o ręcznym restarcie.
- Właściwość QML `chatTemplate` zwraca teraz wartość prezentacyjną `TranslateGemma` dla wewnętrznej wartości `translategemma`, dzięki czemu pozycja może być faktycznie wybrana i pozostaje zaznaczona.
- Filtr Markdown nie wysyła do backendu podstawowych znaczników blokowych (`#`, `-`, `1.`, `>`), zachowuje je przy zapisie oraz pomija linie będące wyłącznie separatorami (`---`, `***`, `___`). Bloki fenced code nadal są pomijane.
- Dodano regresyjne testy dla automatycznego uruchamiania llama.cpp, wyboru TranslateGemma i ochrony składni Markdown.
- Timeout żądania llama.cpp pozostaje na poziomie **300 s**; potwierdzono testem adaptera, że konfiguracja akceptuje co najmniej 300 s.
- Walidacja pełnego `tests/test_qml_gui.py` nadal ma znany problem środowiskowy: pojedynczy wcześniejszy failure powoduje `Fatal Python error: Aborted` podczas raportowania PySide6/pytest. Nie przypisano tego poprawkom bez dowodu.
- Backup przed zmianą: `backups/20261007-llama-md-fixes/pre-change.tar.gz`, SHA-256 `091c7d309a23fce53bed6cd58cd5b8932b3ad1178fe5198c34e8d5d4933e0769`.


## 2026-10-07 — diagnostyka legacy konfiguracji i skip-pattern

- `settings-v4.json` powstał o 00:09:15, przed uruchomieniem aktualnego procesu V4 o 00:25:51. Aktywny `src/` nie zawiera generatora tego pliku.
- Znaleziono historyczny artefakt `build/lib/tlumacz/qml_gui/config.py` z dawnym `CONFIG_PATH = $HOME/.config/tlumacz/settings-v4.json`; artefakt nie może być używany jako runtime V4.
- Usunięto `$HOME/.config/tlumacz/settings-v4.json` po wykonaniu backupu; aktywna konfiguracja pozostaje w `$HOME/.config/tlumacz/config.json`.
- `test_document_translation_service_applies_skip_patterns_before_backend`: **PASS**; cały `tests/test_document_translation_service.py`: **5 passed**. Regresję rozszerzono o kontrolę końcowego HTML.
- Backup: `backups/PLAN-07-SKIP-PATTERN-BEFORE-2026-10-07.tar.gz`, SHA-256 `da848a3ae5b6adfe8265798e54f01188f93557b4f10becde4d97d58cccf734b9`.


## 2026-10-07 — ponowna diagnostyka timeoutu llama.cpp

- Zdiagnozowano rzeczywistą przyczynę zgłoszonego timeoutu: aktywny runtime na porcie 29710 działa na CPU (`--n-gpu-layers 0`), a TranslateGemma 4B Q5_K_M generuje bardzo wolno; pomiar lokalny dla krótkiego żądania wykazał około 0,29 tokena/s. Przy takim czasie limit 300 s był za niski dla większego fragmentu.
- Dodatkowo podczas diagnostyki wykryto trzy lokalne procesy z tym samym GGUF: porty 2782, 18818 i 29710. Proces 18818 jest dodatkowym runtime'em bundled, ale SentinelX nie pozwolił go zakończyć z powodu ograniczenia uprawnień. Proces 2782 pozostawiono bez zmian zgodnie z wcześniejszą zasadą nieprzerywania systemowego serwera bez zgody.
- Timeout żądania `LlamaCppConfig` zwiększono z 300 s do **1800 s**. Timeout startu modelu zwiększono z 60 s do **300 s**.
- Adapter rozpoznaje teraz HTTP 503 `Loading model` i raportuje, że serwer nie jest jeszcze gotowy, zamiast maskować ten stan jako zwykły błąd HTTP.
- Bezpośredni test `/v1/completions` potwierdził, że serwer 29710 odpowiada poprawnym tłumaczeniem po załadowaniu modelu; problem nie jest błędem endpointu ani formatu promptu.
- Ważne: zwiększenie timeoutu usuwa przedwczesne przerwanie, ale nie przyspiesza CPU. Dalszym krokiem optymalizacyjnym jest użycie runtime'u z obsługą GPU/Vulkan lub innego szybszego backendu; nie instalowano żadnych nowych zależności bez zgody.
- Backup: `backups/20261007-llama-timeout-fix/pre-change.tar.gz`, SHA-256 `01164bb5fe5be2bef970931b90f93eda3aca9b95a349d3d19fcadf3b9ddbcde6`.

## 2026-10-07 — korekta runtime Pomocy i motywu

- Zakładki Pomocy są zweryfikowane na poziomie faktycznych obiektów QML: 5 delegatów Repeatera posiada tytuły z bridge.helpTopics.
- Tekst zakładek ma jawny poziom renderowania (z: 2) i korzysta z palette.buttonText, dzięki czemu pozostaje czytelny na tle przycisku; aktywna zakładka używa palette.highlightedText.
- Zmiana pola **Motyw** na **Jasny/Ciemny** aktualizuje również kolor całego okna, niezależnie od systemowego schematu. Runtime offscreen potwierdził #ffffff dla jasnego i #202124 dla ciemnego.
- Nie uznaję pełnego tests/test_qml_gui.py za GREEN; ograniczenia/SIGABRT opisane wcześniej pozostają obowiązujące.

## 2026-10-07 — serializacja TranslateGemma na CPU

Zdiagnozowano błąd tłumaczenia dokumentów na CPU: konfiguracja pozwalała jednocześnie uruchamiać do 4 żądań tłumaczenia (`server_parallel=4`), mimo że aktywny runtime TranslateGemma działa bez GPU. Naprawa wymusza jeden request tłumaczeniowy i jeden slot serwera llama.cpp w trybie CPU. Ustawienie `server_parallel` w aktywnej konfiguracji użytkownika zmieniono na `1`; tryb GPU zachowuje skonfigurowaną równoległość.

Weryfikacja runtime: świeży test bundled `llama-server` na CPU z `--parallel 1` przetłumaczył `Hello world.` → `Witaj świecie.` w 46,67 s bez błędu HTTP/timeoutu. Test jednostkowy regresji: `4 passed`.

Backup przed zmianą: `backups/20261007-llama-cpu-serial/pre-change.tar.gz` (SHA-256 `2e30305dbcaa9b488ca832595e12dce15284a23e915cacfd8837f3a6dde676c3`).

## 2026-10-07 — faktyczna korekta zakładek Pomocy

Problem z pustymi nazwami zakładek został usunięty w kodzie, nie tylko w testach. Repeater otrzymuje listę pięciu właściwości tytułów bridge, a treści tooltipów są pobierane przez indeks z odpowiadających właściwości treści.

Weryfikacja runtime offscreen potwierdziła wszystkie 5 tytułów w języku polskim i angielskim. Przełączenie motywu `system -> light -> dark` zmienia rzeczywisty kolor `ApplicationWindow` na `#ffffff` i `#202124`.

Testy regresyjne: **4/4 PASS**. Pełny plik `tests/test_qml_gui.py` nadal nie jest uznawany za GREEN z powodu wcześniej znanych problemów poza tym zakresem.

## 2026-10-07 — motyw: poprawka sygnału runtime

`bridge.theme` korzysta teraz z `themeChanged`, zgodnego z sygnałem emitowanym przez `set_theme()`. To usuwa rozjazd między wartością widoczną w ComboBoxie a rzeczywistą paletą/tłem `ApplicationWindow`.

Zweryfikowano zmianę Jasny/Ciemny w runtime QML. Zestaw regresyjny dotyczący Pomocy i motywu: **4/4 PASS**.

## 2026-10-07 — motyw QML: poprawka całej powierzchni aplikacji

Zgłoszony przez użytkownika objaw „motyw zmienia tylko ramki okna” został potwierdzony jako problem dziedziczenia palety. Sam `ApplicationWindow.color` zmieniał się prawidłowo, ale część zagnieżdżonych komponentów korzystała z lokalnego `palette`, przez co powierzchnie pozostawały jasne.

Paleta w komponentach QML jest teraz pobierana jawnie z `ApplicationWindow.window.palette`. Dotyczy to Pomocy, widoku treści Pomocy oraz istniejących powierzchni API, Tłumaczenia i Przełączników.

Napisy zakładek Pomocy pozostają jawnie związane z tą samą paletą. Runtime potwierdza pięć rzeczywistych tytułów zakładek oraz zmianę kolorów tekstu dla Jasny/Ciemny. Testy zakresu: **5/5 PASS**.

### 2026-10-07 — Markdown: raportowanie pominiętych fragmentów

Usunięto regresję, przez którą GUI pokazywało `Ominięto 0 fragmentów`, mimo że filtr Markdown pomijał elementy strukturalne dokumentu. Sesja `MarkdownSession` przechowuje teraz `skipped_fragments`; `DocumentProcessor` wykorzystuje tę informację do raportowania rzeczywistej liczby pominiętych fragmentów. Pomijane są m.in. nagłówki, jawnie oznaczony tekst Markdown, fenced code, YAML front matter i linie metadanych. Pominięte elementy pozostają bez zmian w pliku wynikowym.

### 2026-10-07 — formatowanie statystyk czasu i prędkości
Etykiety opisowe czasu i prędkości są prezentowane normalnie; wyróżniane są wyłącznie ich wartości.

## 2026-10-07 — wdrożenie czyszczenia artefaktów `.bak*`

Wdrożono kontrolowane czyszczenie regenerowalnych kopii bezpieczeństwa tworzonych niezależnie od kodu aplikacji (m.in. przez mechanizmy edycji narzędziowych).

- Przed wdrożeniem wykryto **818** plików pasujących do `*.bak*` w całym drzewie projektu.
- Usunięto wyłącznie pliki `*.bak*`; nie usuwano katalogów backupów ani archiwów `.tar`/`.tar.gz`.
- Po czyszczeniu: **0** plików `*.bak*`.
- Dodano `tools/cleanup-bak.sh` z bezpiecznym domyślnym zakresem projektu oraz ochroną przed uruchomieniem dla zbyt szerokich katalogów.
- Dodano regresję `tests/test_cleanup_bak.py`.
- Walidacja regresji: **1 passed**.
- `bash -n tools/cleanup-bak.sh`: wymagane jako szybka kontrola składni przed użyciem produkcyjnym.

Artefakty `.bak*` są traktowane jako regenerowalne i nie stanowią źródła prawdy ani historii projektu. Trwałe backupy/rollbacki pozostają w dedykowanych archiwach `backups/` i `.migration-backups/`.

### Walidacja pełnego suite po wdrożeniu `.bak*`

Świeży pełny suite uruchomiony przed końcową weryfikacją audytu zakończył się: **542 passed, 1 failed**. Jedyny FAIL dotyczy `tests/test_document_translation_service.py::test_document_translation_service_uses_structural_markdown_chunks_and_one_batch_request` i oczekuje dwóch wywołań `translate_batch`, podczas gdy bieżąca implementacja wykonała jedno. Nie jest to regresja mechanizmu czyszczenia `.bak*`; problem pozostaje osobnym zadaniem i nie został zmieniony w ramach tego wdrożenia.

## 2026-10-07 — PLAN-13: remediacja dokumentacji repozytorium

Przygotowano `docs/Plany/PLAN-13-REMEDIACJA-DOKUMENTACJI-REPO-2026-10-07.md` jako aktywny plan naprawy niezgodności wykrytych podczas audytu dokumentacji. Plan uwzględnia fakt, że repozytorium jest równolegle rozwijane: przed każdym etapem wymagany jest ponowny baseline i ponowna korelacja filesystem ↔ indeks.

Bieżący baseline: `docs` = 493 pliki, `*.bak*` = 0, `INDEX.yml` = 485 wpisów `path`; korelacja wykazała 15 istniejących plików nieobecnych w indeksie oraz 7 wpisów wskazujących na nieistniejące ścieżki. `PLAN-12` istnieje na dysku, ale nie jest indeksowany.

Pełny suite z ostatniego świeżego przebiegu: **542 passed, 1 failed**. Failure dotyczy `tests/test_document_translation_service.py::test_document_translation_service_uses_structural_markdown_chunks_and_one_batch_request`. Nie wolno przedstawiać pełnego suite jako GREEN.

Rozbieżność dokumentacyjna do naprawy: `PLAN-12` ma status `WDROŻONY`, ale jego własny exit gate nadal wymaga rzeczywistego E2E z llama.cpp/TranslateGemma. Status planu zostanie zsynchronizowany z rzeczywistym kryterium zakończenia.

## 2026-10-07 — PLAN-13 Etap 1: indeks dokumentacji zsynchronizowany

Na żywym repozytorium wykonano ponowny baseline po zmianach indeksu:

- `docs`: **494 pliki**;
- `*.bak*`: **0** w momencie pomiaru;
- `docs/INDEX.yml`: **494 wpisy**, poprawny YAML;
- filesystem ↔ `INDEX.yml`: **0 brakujących**, **0 martwych**, **0 duplikatów**;
- `file_count`: **494**;
- `INDEX.md`: zsynchronizowano liczbę plików, wersję indeksu i listę PLAN-12/PLAN-13;
- nie usuwano żadnego dokumentu projektu; usunięto wyłącznie martwe wpisy indeksu dotyczące nieistniejących ścieżek oraz historyczne wpisy rootowe spoza zakresu `scope: all-files-under-docs`.

Ostatni pełny przebieg testów pozostaje **542 passed, 1 failed**. Nie przedstawiamy go jako GREEN.

PLAN-12 został przełączony z `implemented` na `active`, ponieważ jego własny exit gate wymaga jeszcze rzeczywistego E2E llama.cpp/TranslateGemma.

## 2026-10-07 — PLAN-13 Etap 4–6: kontrakty techniczne i higiena artefaktów

- Dodano `docs/technical-docs/translation-pipeline-contracts.md` z potwierdzonym kontraktem chunk → batch → request, skip przed backendem, kodami TranslateGemma, ochroną inline codes, lifecycle oraz jawną luką `nested fields` / `complex fields`.
- Skorygowano `docs/technical-docs/functional-capabilities.md`: produkcyjny rejestr filtrów jest dynamiczny i oparty o TPlugin; nie należy utożsamiać obecności klas filtrów w `src/` z ich rejestracją runtime.
- `docs/technical-docs/index.md` wskazuje nowy dokument kontraktów.
- `*.bak*` po końcowym cleanupie etapu 6: **0**.
- Najnowszy pełny suite pozostaje **542 passed, 1 failed**; nie wykonywano nieuzasadnionego ponownego pełnego przebiegu po samych zmianach dokumentacji.

## 2026-10-07 — PLAN-13 zamknięty

Końcowa korelacja remediacji dokumentacji na żywym repozytorium:

- `docs`: **495 plików**;
- `INDEX.yml`: **495 wpisów**;
- 0 brakujących, 0 martwych, 0 duplikatów;
- poprawny YAML i zgodne metadane rozmiaru dla wpisów, które je posiadają;
- `*.bak*`: **0**;
- `PLAN-13` i `TODO-DOC-013`: **ZAMKNIĘTE**.

Nierozstrzygnięte kwestie projektowe pozostają jawne: `TODO-PLAN12-001` oraz ostatni pełny suite **542 passed, 1 failed**. Remediacja dokumentacji nie zmieniała implementacji produkcyjnej.


## 2026-10-07 — korekta budżetu CPU llama.cpp

Potwierdzono sprzęt: 8 rdzeni fizycznych / 16 wątków logicznych. Zgodnie z `docs/wdrozenia/rekomendacja-ustawien-llama.cpp.md` przywrócono profil V3 `threads=8` oraz `threads_batch=16`, przy zachowaniu `batch_size=2048` i `ubatch_size=512`. `parallel` pozostaje wartością sterowaną przez GUI i nie jest wpisywany na sztywno do tuningu. `ctx_size` pozostaje `auto` i jest wyliczany z parametrów dokumentu. Zaktualizowano zarówno `config/llama.json`, jak i aktywny `$HOME/.config/tlumacz/llama.json`.

## 2026-10-07 — PLAN-12: stan po weryfikacji poza Okapi

Poza pracami FilterRegistry/Okapi wykonano weryfikację kontraktu językowego oraz poprawiono charakter testu batchowego tak, aby odpowiadał aktualnej zasadzie jeden logiczny chunk = jeden request. Ukierunkowany gate obejmujący preprocessing, chunkowanie, batch, ochronę inline i detekcję języka: 35 passed. Rzeczywisty E2E z aktywnym TranslateGemma nadal wymaga osobnego dowodu runtime.

---

## 2026-10-07 — domknięcie wdrożenia rozszerzalności formatów

Warstwa filtrów została uznana za wdrożoną zgodnie z aktualnym kontraktem projektu. Okapi/FilterRegistry są utrzymywane przez osobny etap/agent i nie były ponownie modyfikowane w tym domknięciu.

- FilterRegistry: Okapi jako primary, native jako fallback — wdrożone i zweryfikowane przez gate registry/Okapi.
- Preprocessor `translate/keep` — wdrożony i zintegrowany ze wspólnym `DocumentProcessor`.
- Nowy typ dokumentu ma być podłączany przez deklarację/detekcję filtra i wspólny `FilterContract`, bez zmian w `ChunkPlanner`, `TranslationExecutor` i `TranslationOrchestrator`.
- TXT nie jest sztucznie transformowany do XLIFF; proste formaty tekstowe mają bezpośrednią ścieżkę tłumaczenia, a formaty strukturalne wymagają właściwego filtra.
- Regionalne kody językowe są obsługiwane w `language_code_for()`.
- Zakończono świeżą regresję ukierunkowaną: **19 passed**.
- Pełny suite SentinelX: **563 passed, 1 failed**. Jedyna porażka dotyczyła regresji GUI `test_translation_page_displays_translation_time_as_minutes_and_seconds`; poprawiono ją przez przywrócenie oczekiwanego pojedynczego pola czasu. Po poprawce test ukierunkowany przechodzi.

### Korekta wcześniejszego wpisu


## 2026-10-07 — przywrócenie tuningu V3 i detekcji dokumentów wielojęzycznych

- Przywrócono detekcję języka llama.cpp na poziomie jednostki/chunka, zgodnie z działającą ścieżką V3. Zmiana języka jest ponownie przekazywana do `ChunkPlanner`, więc dokument wielojęzyczny może być dzielony na granicy języka.
- Zachowano wykluczanie prostych cytatów `"..."` z próbki detekcyjnej.
- Przywrócono potwierdzony w V3 tuning CPU: `threads=8`, `threads_batch=16`, `batch_size=2048`, `ubatch_size=512`.
- `parallel` nadal pochodzi wyłącznie z GUI; nie zmieniono jego wartości programowo.
- `ctx_size` ustawiono na `auto`; runtime nadal wylicza go na podstawie parametrów dokumentu.
- Backup: `backups/20261007-backend-routing-tuning/pre-change.tar.gz`, SHA-256 `d1d479450229a2ad123397795bd3aa151c150a6d5e082e81feb7eac871fb55c2`.

## 2026-10-07 — stan regresji po korekcie backendu

- Pełna regresja poprzedniej wersji zakończyła się wynikiem `567 passed, 1 failed`; jedyna porażka dotyczyła starej asercji QML czasu.
- Asercja została zweryfikowana po korekcie `TranslationPage.qml`.
- Kolejny przebieg kierunkowy wykazał 3 błędy w istniejącym `BackendRequest` (`provider`/`base_url`), wynikające z równoległej zmiany API w projekcie. Nie zmieniano tej części kodu, aby nie nadpisywać pracy drugiego agenta.


## 2026-10-07 — GUI: motyw systemowy i link do strony projektu

- Zgodnie z decyzją użytkownika usunięto z karty **Pomoc** selektor motywu.
- GUI korzysta obecnie wyłącznie z motywu systemowego.
- Kod odpowiedzialny za przyszłe przełączanie `system/dark/light` pozostaje zachowany w `bridge.py` i launcherze, z komentarzem o planowanym przywróceniu opcji.
- W dialogu **O programie** dodano klikalny link do `https://frs777.github.io/tlumacz-v4/zrzuty.html`.
- Backup przed zmianą: `backups/20261007-theme-system-only-project-link/pre-change.tar.gz`, SHA-256 `66545269799ec0a51b1e73fd9b6a40f0c634652fac57ffa476193c9a8572a9ff`.


Weryfikacja po zmianie: dedykowany zestaw QML GUI **158 passed**; `compileall` i `qmllint` zakończone bez błędów. Pełny suite uruchomiony po zmianie zakończył się **574 passed / 3 failed**; dwa pozostałe błędy dotyczą równoległej nieobecności `tlumacz.filter_engine.preprocessor`, a trzeci był historycznym testem oczekującym dwóch selektorów motywu i został zaktualizowany do nowego kontraktu.


## Audyt bezpieczeństwa bindu lokalnego — 2026-10-07

Wbudowany serwer llama.cpp jest ograniczony do adresów pętli zwrotnej: `127.0.0.1`, `localhost` i `::1`. Próba ustawienia `0.0.0.0` albo adresu LAN jest odrzucana. Ograniczenie dotyczy wyłącznie backendu wbudowanego `llama`; backend `custom` nadal może używać dowolnego adresu serwera zewnętrznego.

FastAPI nie jest częścią aktualnego kodu projektu — wcześniejszy komponent został usunięty i nie jest przedmiotem tego ograniczenia.

## 2026-10-07 — Apertium: migracja danych językowych do bundlowanego runtime

Docelowa struktura Apertium została zrealizowana. Dane 27 kierunków objętych
release scope zostały skopiowane do:
src/tlumacz/backends/apertium/native_runtime/share/apertium/

Runtime nie zależy już domyślnie od $HOME/.config/tlumacz/Apertium/. ApertiumRuntime
wybiera bundlowane share/apertium, a jawny ApertiumConfig.data_dir nadal może
wskazać alternatywny katalog. Bridge GUI domyślnie korzysta z tego samego
bundlowanego drzewa.

Weryfikacja:
- Apertium 3.9.12: PASS;
- PATH=/nonexistent: PASS;
- wykrywanie: 27 par;
- smoke bundlowanego runtime'u: 27 READY / 0 FAIL;
- E2E adaptera en → pl: PASS;
- focused testy Apertium/GUI po zmianie: 24 passed;
- pełny gate pozostaje uruchomiony po tej zmianie.

Backup przed migracją: backups/apertium-bundled-migration-before-20261007-175229.tar.

Katalog Aperitium/ nie został jeszcze usunięty. Audyt zależności wykonany 2026-10-07 potwierdził, że aktywne `src/` nie zawiera żadnych odwołań do tej ścieżki. Pozostały dwa aktywne odwołania developerskie poza `src/`: `tools/apertium/package_pairs.py` wskazuje `Aperitium/` jako `SOURCE_ROOT`, a `tests/test_apertium_pair_repairs.py` wskazuje konkretny plik źródłowy w `Aperitium/`. Sam katalog zawiera checkouty źródeł, artefakty budowania i skompilowane dane Apertium, więc nie należy go usuwać przed odpięciem tych dwóch zależności, aktualizacją dokumentacji i końcową weryfikacją. Historyczne kopie `.backup/` mogą zawierać starsze wzmianki i nie są częścią aktywnego runtime.
## 2026-10-07 — narzędzia i specyfikacja TPlugin

- dodano tools/tplugin/create.py, generator minimalnego projektu źródłowego TPlugin;
- utworzono aktualną dokumentację technical-docs/tplugin-specyfikacja-reczne-tworzenie.md;
- zarejestrowano dokument w indeksach technical-docs/index.md, INDEX.md i INDEX.yml;
- starszy tplugin-reczne-tworzenie.md oznaczono jako superseded, ponieważ zawierał historyczny model magazynu runtime.
## 2026-10-07 — dokumentacja tworzenia pluginów Okapi

- jako dokument kanoniczny dla tworzenia pluginów Okapi wykorzystuje się docs/technical-docs/tworzenie-pluginow-okapi.md;
- dokument obejmuje specyfikację TPlugin oraz praktyczny workflow z tools/tplugin/ i tools/tplugin_admin/;
- potwierdzono, że java/filter-host/run.sh jest tylko duplikatem launchera wskazującego na src/tlumacz/resources/filter-host/; nie jest używanym źródłem implementacji FilterHost;
- nie usunięto java/filter-host/run.sh, ponieważ wymaga to osobnej operacji porządkowej.


### Inicjalizacja profilu użytkownika przy instalacji ze źródeł — 2026-10-07

- dodano tlumacz.user_config.initialize_user_config() tworzące $HOME/.config/tlumacz/;
- tworzone są puste katalogi skills/, filters/, apertium/, logs/;
- config.json, llama.json i cloud_models.json są seedowane wyłącznie z repozytoryjnego config/ przez zasoby pakietu;
- istniejące pliki użytkownika nie są nadpisywane;
- dodano instaluj-zrodla.sh jako kanoniczny instalator ze źródeł;
- mechanizm nie kopiuje danych z aktualnego $HOME/.config/tlumacz/.


## 2026-10-07 — walidacja po synchronizacji testów Apertium TAR-only

- B8: zsynchronizowano test pakowania/runtime'u z aktualnym kontraktem TAR-only.
- Kod produkcyjny bez zmian.
- Pełny suite `XDG_CACHE_HOME=/tmp PYTHONPATH=src python3 -m pytest -q tests -x`: **599 passed in 92.37s**.
- Brak FAIL i SKIP w tym uruchomieniu.
- Następny krok: audyt/obsługa kolejnego rzeczywistego problemu tylko po uzyskaniu nowego dowodu; obecny suite jest GREEN.

## 2026-10-07 — usunięcie hardcodowanych ścieżek użytkownika

- `FilterStore` nie zawiera już `/home/frs`; domyślny magazyn filtrów jest wyznaczany przez `XDG_CONFIG_HOME`, a bez niego przez `$HOME/.config/tlumacz/filters`.
- `filter-host/run.sh` używa `${XDG_CONFIG_HOME:-$HOME/.config}/tlumacz/filters` zamiast ścieżki konkretnego użytkownika.
- Launcher `uruchom-tlumacz-v4.sh` oraz `skrypt.sh` wyznaczają katalog projektu względem własnej lokalizacji.
- Testy nie zawierają już literalnych ścieżek `/home/frs/Modele`.
- Aktualny magazyn paczek Apertium pozostaje przenośny: `${XDG_CONFIG_HOME:-$HOME/.config}/tlumacz/apertium`.
- Backup przed zmianą: `backups/path-portability-before-20261007-2305.tar.gz` (SHA-256: `a667a9352e004306c7be964c9f09dda13a16f64c79571e3430d610696a518d39`).

## 2026-10-08 — weryfikacja po naprawie regresji ścieżki filtrów

- Testy ścieżki magazynu i rejestru: **32 passed**.
- `FilterStore.default()` przy `HOME=/home/frs XDG_CONFIG_HOME=/home/frs/.config` zwraca `/home/frs/.config/tlumacz/filters`.
- Przeszukanie aktywnego `src/`, `tools/` i `tests/` nie wykazuje już odwołań do `/home/frs/.config/filters` ani `${XDG_CONFIG_HOME:-$HOME/.config}/filters`.
- Przeszukano również aktywną dokumentację, artefakty build oraz README filtrów; błędne aktywne odwołania zostały usunięte. Historyczne wpisy CHANGELOG pozostawiono bez przepisywania historii.
- Pełny suite uruchomiony w technicznym środowisku SentinelX: **593 passed, 9 failed, 2 skipped**; niepowodzenia dotyczyły braku artefaktów Apertium/Okapi w profilu technicznym.
- Pełny suite z `HOME=/home/frs` i `XDG_CONFIG_HOME=/home/frs/.config`: **552 passed, 52 failed**; większość niepowodzeń wynika z braku uprawnień procesu testowego do `/home/frs/.config/tlumacz/.key` oraz zależnych testów GUI/Apertium, więc ten przebieg nie jest miarodajnym gate'em kodu.
- `compileall` zakończył się poprawnie. Ruff zgłasza dwa istniejące problemy importów (`src/tlumacz/filter_engine/__init__.py`, `tests/test_tplugin_create.py`), niezwiązane z tą zmianą.
- Fizyczny `/home/frs/.config/filters/` pozostaje jako stara kopia artefaktów, ale aktywny kod jej nie używa. SentinelX nie pozwala jej usunąć z bieżącego kontekstu z powodu ograniczenia zapisu.
