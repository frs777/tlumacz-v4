## 2026-10-08 — naprawa regresji ścieżki magazynu filtrów

- Przywrócono właściwy magazyn pakietów TPlugin: `$HOME/.config/tlumacz/filters/`.
- `FilterStore` ponownie uwzględnia segment `tlumacz` po `XDG_CONFIG_HOME`; launcher FilterHost korzysta z tej samej ścieżki.
- Zaktualizowano testy ścieżek domyślnych i XDG oraz dokumentację kontraktową.
- Historyczne wpisy CHANGELOG zachowano bez przepisywania ich znaczenia.

## 2026-10-08 — przebudowa dokumentacji tworzenia pluginów Okapi

- rozbito monolityczny dokument `tworzenie-pluginow-okapi.md` na katalog powiązanych dokumentów Markdown;
- dodano dokumentację rzeczywistego przepływu: FilterRegistry → extract → preprocessing → chunkowanie → orkiestracja → executor → backend → walidacja → writer;
- rozdzielono ścieżki strukturalnych filtrów Okapi, PlainTextFilter, Markdown i osobnej obsługi PDF;
- opisano detekcję Lingua dla TranslateGemma, równoległość TranslationExecutor oraz integrację Apertium z markerami inline;
- dodano źródło diagramów TikZ w `docs/technical-docs/tworzenie-pluginow-okapi/latex/main.tex`;
- skorygowano wcześniejsze stwierdzenie, że TXT nie jest aktywnie rejestrowany: aktualny `registry.py` rejestruje `PlainTextFilter`.
## 2026-10-08 — normalizacja zapisu ścieżek użytkownika

- Zastąpiono w aktywnym repozytorium skrótową notację katalogu domowego jednoznacznym zapisem `$HOME/...`.
- Normalizacja objęła kod, konfiguracje, testy oraz dokumentację; katalogi backupów i kopie historyczne pozostawiono poza operacją.
- Zachowano konwencję `${XDG_CONFIG_HOME:-$HOME/.config}` tam, gdzie ścieżka musi respektować XDG.

## 2026-10-08 — oczyszczenie dokumentacji z odniesień do skilli środowiska agenta

- Usunięto z dokumentacji projektu bezpośrednie ścieżki skilli środowiska agenta.
- Zastąpiono je opisami neutralnymi dla środowiska wykonawczego, zachowując kontekst historyczny i reprodukcyjny.
- Pozostawiono bez zmian właściwy model skilli aplikacji Tłumacz: `$HOME/.config/tlumacz/skills/`.

## 2026-10-07 — naprawa pozostałych odwołań Apertium do magazynu językowego

- Naprawiono discovery par językowych w `QmlApplicationBridge` dla aktualnego kontraktu TAR-only.
- Dodano wspólny mechanizm `discover_supported_pairs_from_store()`: archiwa `.tar` są weryfikowane i materializowane tylko tymczasowo na potrzeby discovery.
- Bundlowany runtime Apertium nie jest już traktowany jako źródło `share/apertium`; dane językowe pozostają niezależnymi paczkami użytkownika.
- Dodano regresję potwierdzającą działanie selektora języków GUI bez rozpakowywania danych do trwałego magazynu.

## 2026-10-07 — usunięcie odwołań do starego źródła paczek `pary/`

- Wszystkie aktywne odwołania kodu testowego do `pary/` zastąpiono źródłem zgodnym z aktualnym modelem magazynu paczek.
- Testy lokalne korzystają domyślnie z `$HOME/.config/tlumacz/apertium` przez `tests/apertium_package_source.py`.
- Źródło testowe można jawnie wskazać przez `TLUMACZ_APERTIUM_PACKAGE_SOURCE`.
- CI korzysta z reprezentatywnych artefaktów w `tests/fixtures/apertium/`, a nie z historycznego katalogu `pary/`.
- `tools/apertium/package_pairs.py` nie zapisuje już domyślnie do `pary/`; domyślnym miejscem wyjściowym jest magazyn użytkownika `$HOME/.config/tlumacz/apertium`.
- Zaktualizowano dokumentację BUILD/STATUS/TODO/INDEX.

## 2026-10-07 — naprawa CI: kontrakt Apertium TAR-only

- Zaktualizowano `.github/workflows/quality-gate.yml`, aby Wheel Audit nie wymagał historycznych danych językowych w `native_runtime/share/apertium`.
- CI wymaga obecnie wyłącznie bundlowanego executable runtime'u Apertium (`VERSION`, `bin/apertium`, `libexec/apertium-real`).
- Dodano asercje, że wheel nie zawiera danych językowych ani archiwów `.tar` par językowych.
- Clean-install/product smoke CI instaluje rzeczywistą parę `apertium-eng-pol-1.0.0.tar` + checksum do izolowanego `XDG_CONFIG_HOME`, zgodnie z aktualnym modelem dystrybucji.
- Lokalna weryfikacja odpowiednika gate'u: YAML parse PASS, wheel TAR-only audit PASS, clean-install Apertium TAR smoke PASS.
- Kod produkcyjny nie został zmieniony.

## 2026-10-07 — synchronizacja testów Apertium TAR-only: pełny suite GREEN

- Zsynchronizowano test pakowania/runtime'u Apertium z aktualnym kontraktem TAR-only.
- Test nie oczekuje już danych językowych w `native_runtime/share/apertium`; dane są dostarczane jako osobne paczki TAR + checksum.
- Test izoluje `XDG_CONFIG_HOME` i udostępnia rzeczywistą parę `apertium-eng-pol-1.0.0.tar` + `.sha256` w tymczasowym magazynie.
- Kod produkcyjny nie został zmieniony.
- Pełna weryfikacja po synchronizacji: **599 passed in 92.37s**.

## 2026-10-07 — synchronizacja testu równoległości QML

- Test `test_non_cloud_translation_keeps_configured_parallelism` został doprecyzowany: scenariusz zachowania równoległości `llama.cpp` otrzymuje jawny tryb GPU.
- Zachowano osobny scenariusz CPU wymuszający jeden slot.
- Kod produkcyjny bez zmian.
- Weryfikacja: **4 passed in 1.43s**.

## 2026-10-07 — synchronizacja testu bundlowanego runtime'u Apertium

- Test `test_bundled_runtime_contains_language_data_for_release` zastąpiono testem `test_bundled_runtime_has_no_language_data_without_installed_packages`.
- Test izoluje `XDG_CONFIG_HOME`, aby nie odczytywać rzeczywistych paczek użytkownika z domyślnego magazynu.
- Aktualny kontrakt TAR-only został zachowany: bundlowany jest executable, a dane językowe pojawiają się dopiero po zainstalowaniu paczek użytkownika.
- Nie zmieniano kodu produkcyjnego.
- Weryfikacja ukierunkowana: **1 passed in 0.78s**.

## 2026-10-07 — synchronizacja testu discovery runtime Apertium

- Test `test_runtime_discovers_only_bundled_runtime` został odizolowany od rzeczywistego magazynu paczek użytkownika przez tymczasowy `XDG_CONFIG_HOME`.
- Test zachowuje pierwotną intencję: weryfikuje wybór bundlowanego executable oraz wynik `-V` i `-l` dla kontrolowanego fake runtime'u.
- Przyczyna błędu była testowa: bez izolacji `ApertiumRuntime.discover()` materializował paczki z domyślnego magazynu, więc discovery zwracało 24 rzeczywiste kierunki zamiast dwóch kierunków fake runtime'u.
- Weryfikacja ukierunkowana: **1 passed in 1.37s**.

## 2026-10-07 — synchronizacja testu E2E DOCX z TAR-only

- Test `test_real_apertium_document_translation_produces_valid_final_docx` otrzymał izolowany tymczasowy magazyn `XDG_CONFIG_HOME` z rzeczywistym `apertium-eng-pol-1.0.0.tar` i checksumem.
- Zachowano pełną walidację wyniku DOCX: `word/document.xml`, tłumaczenie `Świat` oraz zachowanie `word/media/resource.bin`.
- Weryfikacja ukierunkowana: **1 passed in 3.14s**.

## 2026-10-07 — synchronizacja testu E2E `TranslationApp` z TAR-only

- Test `test_translation_app_uses_bundled_apertium_for_real_eng_pol_runtime` korzysta teraz z izolowanego tymczasowego magazynu paczek zamiast zależności od zewnętrznego/globalnego środowiska.
- Do magazynu testowego kopiowane są rzeczywiste artefakty `apertium-eng-pol-1.0.0.tar` i `.sha256`.
- Weryfikacja ukierunkowana: **1 passed in 1.33s**.

## 2026-10-07 — synchronizacja `test_apertium_pair_repairs.py` z TAR-only

- Test przeniesiono z nieaktualnej ścieżki `Aperitium/` na rzeczywisty artefakt `pary/apertium-pol-eng-1.0.0.tar`.
- Test nadal sprawdza regresję atrybutów `a_SN`, `PDET`, `gen` i `mp` w pliku `apertium-eng-pol.pol-eng.t3x` znajdującym się w paczce.
- Weryfikacja ukierunkowana: **1 passed in 0.81s**.

## 2026-10-07 — synchronizacja testu Apertium z modelem TAR-only

- Zaktualizowano test bundlowanego runtime'u, aby używał aktualnego modelu: runtime wykonywalny z `native_runtime` + para językowa z artefaktu `.tar` i `.tar.sha256`, materializowana tymczasowo.
- Test wykorzystuje rzeczywisty artefakt `apertium-eng-pol-1.0.0.tar` z `pary/`, ale izoluje magazyn przez tymczasowy `XDG_CONFIG_HOME`.
- Weryfikacja ukierunkowana: **1 passed**.

## 2026-10-07 — link do strony projektu w README

- Dodano do głównego `README.md` link do strony projektu z sekcją pobierania: `https://frs777.github.io/tlumacz-v4/pobieranie.html`.

## 2026-10-07 — audyt katalogu `Aperitium/`

- Zapisano wynik audytu zależności katalogu `/home/frs/Projekty/tlumacz-v4/Aperitium/`.
- Potwierdzono brak odwołań do `Aperitium/` w aktywnym `src/`.
- Potwierdzono dwie aktywne zależności developerskie poza `src/`: `tools/apertium/package_pairs.py` (`SOURCE_ROOT`) oraz `tests/test_apertium_pair_repairs.py` (konkretny plik źródłowy).
- Udokumentowano, że `Aperitium/` zawiera źródła, artefakty build/configuration i skompilowane zasoby oraz nie jest częścią `native_runtime` używanego przez aplikację.
- Usunięcie katalogu pozostaje odłożone do czasu odpięcia tych dwóch zależności, aktualizacji dokumentacji i końcowej weryfikacji.
- Historyczne kopie `.backup/` mogą zawierać starsze wzmianki o `Aperitium/`; nie są częścią aktywnego runtime.

# 2026-10-07 — uproszczenie magazynu filtrów

- Ujednolicono trwały magazyn filtrów do `/home/frs/.config/filters`.
- Usunięto trwały runtime `$HOME/.config/tlumacz/filter-engine/plugins` oraz centralny `shared-libs`.
- Rozpakowywanie `.tplugin` odbywa się wyłącznie w `/tmp/filters/`.
- Wspólne biblioteki Okapi przeniesiono do `src/tlumacz/resources/okapi-runtime/lib/`.
- XLIFF przeniesiono do `src/tlumacz/documents/xliff.py` i wyłączono z wejściowego `FilterRegistry`.
- Usunięto `dist/tplugins/` i `build/tplugins/`.
- Aktywny zestaw wejściowych pakietów Okapi ograniczono do EPUB, JSON, OpenOffice, OpenXML i YAML; HTML/Markdown są natywne.

### Apertium — usunięcie duplikatu danych językowych z runtime

- usunięto z `native_runtime/share/apertium/` rozpakowane kopie paczek językowych oraz katalog `modes`;
- dane językowe pozostają wyłącznie w nowym magazynie `$HOME/.config/tlumacz/apertium/` jako TAR + SHA-256;
- wykonano backup przed usunięciem: `backups/apertium-language-data-removal-before-20261007-184817.tar.gz`;

### Apertium — TAR jako jedyna trwała postać paczki

- magazyn $HOME/.config/tlumacz/apertium/ przechowuje wyłącznie artefakty .tar i .tar.sha256;
- aplikacja nie tworzy trwałych katalogów apertium-<pair>/ w magazynie;
- paczki są weryfikowane i materializowane do tymczasowego katalogu roboczego przed użyciem przez Apertium;
- dodano regresje potwierdzające model TAR-only.

## [Unreleased] — 2026-10-07

### Strona WWW / I18N — 2026-10-07
- Dodano anglojęzyczną stronę główną `gh-pages/en/index.html`.
- Dodano przełącznik języka PL ↔ EN na stronie głównej.
- Zachowano wspólny motyw, logo, układ i linki do istniejących materiałów; angielska wersja jest obecnie zakresem strony głównej.

### Apertium — magazyn paczek językowych
- rozdzielono prywatny runtime Apertium 3.9.12 od danych par językowych;
- zmieniono domyślny magazyn paczek na $HOME/.config/tlumacz/apertium/;
- aplikacja automatycznie wykrywa archiwa apertium-<source>-<target>-<version>.tar, weryfikuje zewnętrzny .tar.sha256 i materializuje je tymczasowo przed discovery;
- builder paczek generuje również wymagany zewnętrzny plik SHA-256 całego artefaktu;
- GUI QmlApplicationBridge korzysta z tego samego magazynu użytkownika;
- zweryfikowano przepływ na 28 lokalnych archiwach oraz rzeczywiste tłumaczenie eng-pol przez Apertium 3.9.12;
- zaktualizowano specyfikację paczek, dokumentację integracji i README runtime'u.

## [Unreleased] — 2026-10-07 — domknięcie integracji logowania

### Logowanie
- Podłączono centralny logger do granic pipeline'u dokumentowego i orkiestracji chunków.
- Dodano diagnostykę transportu Cloud, llama.cpp oraz wykonania Apertium.
- Logowane są wyłącznie metadane operacyjne: endpoint/metoda, backend, para językowa, liczba jednostek/znaków i czas wykonania; bez treści dokumentów, payloadów i nagłówków autoryzacyjnych.
- Redakcja sekretów pozostaje aktywna dla komunikatów, struktur danych oraz wyjątków/tracebacków.

### Apertium / dystrybucja
- Ustalono, że bundlowany runtime Apertium jest dostarczany razem ze źródłami aplikacji V4; nie przewiduje się osobnego mechanizmu pobierania runtime'u.

### Status pozostałych punktów listy operacyjnej
- Odnotowano jako zrealizowane pozostałe omawiane punkty poza logowaniem; FastAPI/OpenVINO pozostają wycofane, a `llama.cpp`/ZenDNN są poza zakresem tej pracy.

---

## 2026-10-07 — Ikona usuwania skilla użytkownika

- Każda umiejętność użytkownika w sekcji **Skille** ma na końcu osobny `ToolButton` z ikoną `window-close`.
- Kliknięcie ikony nadal wywołuje `bridge.deleteSkill(modelData)` i usuwa wskazany plik skilla.
- Dodano nazwę dostępnościową oraz tooltip `Usuń skill` / odpowiednik lokalizacyjny.
- Walidacja: test QML i testy builderów — 3 passed; `qmllint` dla `ExtrasPage.qml` — PASS.

## [Unreleased] — 2026-10-07 — centralne logowanie i ochrona sekretów

- dodano centralną konfigurację loggera `tlumacz` z poziomem `DEBUG` odpowiednim dla wersji testowej;
- logi są zapisywane do `$HOME/.config/tlumacz/logs/tlumacz.log` oraz na konsolę;
- komunikaty aplikacji dodane w tej warstwie są prowadzone po polsku;
- dodano redakcję pól wrażliwych, nagłówków `Authorization`/Bearer, sekretów w parametrach URL oraz znanych wartości z `.key`;
- redakcja obejmuje również wyjątki i tracebacki;
- `SecretStore` automatycznie przekazuje odczytane i zapisane sekrety do redaktora logów;
- uruchomienie GUI korzysta z centralnej konfiguracji logowania;
- dodano testy TDD dla redakcji sekretów i konfiguracji logowania;
- TODO-011 został zamknięty po podłączeniu loggerów do istotnych ścieżek backendów i pipeline'u.
- backup: `backups/20261007-logging-pre/logging-pre.tar.gz`.

## [Unreleased] — 2026-10-07 — zamknięcie etapu rozszerzalności backendów

- świeży pełny suite: **573 passed**;
- TestBackend przechodzi cały pipeline dokumentowy;
- rejestr backendów, backend custom oraz separacja konfiguracji są zweryfikowane;
- Ruff: PASS; compileall: PASS.
## 2026-10-07 — PLAN-14: naprawa regresji motywu QML/Fusion

- dodano test rzeczywistego wyniku palety dla dark/light i potwierdzono RED przed zmianą;
- zachowano natywny QStyleHints jako pierwszy mechanizm;
- dodano pełny fallback palety Fusion wyłącznie dla dark/light, gdy Qt nie zastosuje żądanego schematu;
- system resetuje paletę do natywnej i nie korzysta z fallbacku;
- pełne tests/test_qml_gui.py: 157 passed; pełny suite: 573 passed;
- compileall i qmllint: PASS;
- zsynchronizowano niezależny test czasu TranslationPage.qml z aktualnym układem dwóch etykiet;
- rzeczywisty gate KDE pozostaje otwarty z powodu ograniczenia dostępu SentinelX do sesji użytkownika;
- backup: backups/20261007-theme-regression-pre-fix/theme-regression-pre-fix.tar.gz.

## [Unreleased] — 2026-10-07 — dowód rozszerzalności E2E

- TestBackend przechodzi cały przepływ TranslationApp → DocumentTranslationService → DocumentProcessor → TranslationOrchestrator → BackendRegistry → writer;
- test pliku rozszerzalności: **6 passed**;
- kierunkowy zestaw backendów/aplikacji/GUI: **64 passed, 139 deselected**;
- pełny suite zostanie ponownie oceniony po tej zmianie testowej.
## [Unreleased] — 2026-10-07 — walidacja konfiguracji backendów

- świeży pełny suite: **571 passed, 1 failed**;
- 1 failure dotyczy istniejącego testu QML czasu tłumaczenia, poza zakresem refaktoru backendów;
- testy kierunkowe backendów/rozszerzalności/GUI: **28 passed**;
- Ruff: PASS; compileall: PASS.
## [Unreleased] — 2026-10-07 — konfiguracja backendów

### Architektura
- usunięto backend-specific pola z BackendRequest i BackendSelection;
- dodano BackendConfiguration jako wspólny kontener konfiguracji przekazywany do konkretnego adaptera;
- GUI i TranslationApp zostały dostosowane do nowego kontraktu;
- dodano testy regresyjne potwierdzające rozszerzalność bez rozszerzania wspólnego modelu.

### Weryfikacja
- 27 testów kierunkowych: PASS;
- Ruff: PASS;
- compileall: PASS;
- backup: backups/20261007-backend-config-pre/.
## 2026-10-07 — FilterRegistry: Okapi primary, native fallback

- Discovery TPlugin nie blokuje już pluginu Okapi przez wcześniejszy native fallback.
- Plugin Okapi może przejąć suffix natywny przez istniejący mechanizm `register_lazy()`.
- Dodano regresje dla przejęcia `.txt` oraz pluginu deklarującego jednocześnie suffix natywny i nowy.
- Zaktualizowano test discovery HTML, aby weryfikował kontrakt `OkapiFilter`.
- Weryfikacja: 17/17 testów registry oraz 47/47 skoncentrowanego gate'u Okapi/TPlugin.
- Backup: `backups/okapi-filter-engine-20261007/pre-instrukcja-okapi-20261007-144400.tar.gz`.

---

## [Unreleased] — 2026-10-07 — PLAN-12

### Filter Engine
- Markdown, zwykły tekst i HTML zostały odseparowane od Okapi: `.md`/`.markdown` korzystają z natywnego `MarkdownFilter`, `.txt`/`.text`/`.log` z `PlainTextFilter`, a `.html`/`.htm`/`.xhtml` z `HtmlFilter`.
- Dodano regresje potwierdzające brak `OkapiFilter` dla prostych formatów tekstowych oraz poprawny round-trip TXT.
- Formatów strukturalnych zapisanych tekstowo nie przeniesiono do naiwnego filtra liniowego; migracja wymaga osobnego kontraktu strukturalnego.


## 2026-10-07 — PLAN-12: wspólny Preprocessor skip/keep

- Dodano filter_engine.preprocessor jako wspólną warstwę klasyfikacji jednostek przed backendem.
- KEEP nie jest wysyłane do translate ani translate_batch; oryginalny tekst pozostaje dostępny dla rekonstrukcji.
- Walidowane są unikalne identyfikatory jednostek i poprawność regexów.
- Wspólne wzorce metadanych są stosowane w preprocessingu, a separator --- jest domyślnie ograniczony do Markdown.
- Nie połączono semantycznie KEEP z techniczną ochroną inline markerów.
- Dodano regresje preprocessora oraz integracji z DocumentProcessor.
- Weryfikacja: 23 passed, Ruff PASS, compileall PASS.
## 2026-10-07 — naprawa produkcyjnego pomijania fragmentów Markdown

- Produkcyjny `FilterRegistry` rozwiązuje plugin `markdown` do Pythonowego `MarkdownFilter` zamiast do adaptera Okapi Markdown.
- Dzięki temu rzeczywista ścieżka GUI korzysta z klasyfikacji pominięć obejmującej nagłówki, oznaczony tekst Markdown, fenced code i YAML front matter.
- Usunięto rozbieżność, przez którą `MarkdownFilter` poprawnie raportował pominięcia w testach, ale produkcyjny rejestr wybierał `OkapiFilter` bez pola `skipped_fragments`, powodując komunikat `Ominięto 0 fragmentów`.
- Dodano regresję rejestru potwierdzającą wybór właściwego filtra Markdown.

## 2026-10-07 — poprawka automatycznej propozycji pliku wynikowego

- Po wybraniu pliku wejściowego GUI ponownie generuje automatyczną propozycję pliku wynikowego na podstawie jego nazwy, katalogu i aktualnego kodu języka docelowego.
- Przykład: `test.md` → `test_pl.md` przy języku docelowym `pl`.
- Zmiana pliku wejściowego aktualizuje propozycję, dopóki użytkownik nie ustawi ręcznie własnej ścieżki wyniku.
- Dodano test regresyjny dla kolejnych wyborów pliku wejściowego.

# CHANGELOG — Agent Translator V4

## [Unreleased] — 2026-10-07

### Filter Engine / Preprocessor
- wydzielono `Preprocessor` do `src/tlumacz/preprocessing/`, poza pakietem `filter_engine`;
- dodano jawny `preflight()` wykonywany przed `FilterRegistry.for_path()` oraz `classify_units()` wykonywane po ekstrakcji;
- zachowano semantykę `TRANSLATE/KEEP`, kolejność jednostek, rekonstrukcję `KEEP` 1:1 i odrębność ochrony inline-code;
- dodano regresję kolejności `preflight → registry` oraz przeniesiono testy preprocessingu na niezależny kontrakt;
- weryfikacja kierunkowa: **13 passed**;
- backup przed zmianą: `backups/20261007-preprocessor-refactor-pre/preprocessor-refactor.tar.gz`.

## 2026-10-07 — GUI / motyw: przejście na natywny mechanizm schematu Qt

- usunięto ręczne budowanie pełnej palety `QPalette` dla `Ciemny` / `Jasny`;
- launcher używa `QStyleHints::setColorScheme(Qt::ColorScheme::Dark/Light)` oraz `unsetColorScheme()` dla `Systemowy`;
- `Main.qml` nie nadpisuje już ról `palette.*`; tło korzysta z `palette.window`, a Fusion/Qt Quick Controls dziedziczą paletę platformy;
- zachowano wymaganie ustawienia schematu przed utworzeniem `QQmlApplicationEngine`;
- dodano regresje potwierdzające delegowanie motywu do `QStyleHints` i brak ręcznych ról palety;
- weryfikacja: `qmllint` PASS, 12 ukierunkowanych testów GUI PASS;
- ważne ograniczenie: Qt traktuje `setColorScheme()` jako mechanizm zależny od wsparcia platformy; w `offscreen` i izolowanym Xvfb nie zmienia on palety, więc rzeczywisty runtime KDE wymaga oceny po restarcie GUI.
- backup: `backups/20261007-122616-theme-qstylehints/`.

### Tłumaczenie / detekcja języka i GUI
- **Detekcja źródła dla llama.cpp zgodna z V3** — język jest ponownie rozpoznawany dla bieżącej jednostki/chunka, dzięki czemu dokumenty wielojęzyczne mogą poprawnie zmieniać `source_language` między chunkami. Cytaty w prostych `"..."` są wyłączane z próbki detekcyjnej.
- **Cytaty wyłączone z detekcji** — tekst pomiędzy podwójnymi cudzysłowami `"..."` jest usuwany przed rozpoznaniem języka, więc cytat w obcym języku nie zmienia wyniku detekcji dokumentu.
- **Statystyki czasu/prędkości** — cyfry czasu i prędkości w `TranslationPage.qml` są o 1 px większe od bazowego fontu i pogrubione. GUI pokazuje jedną bieżącą prędkość w znakach/s, bez zapisu `0/0`.
- **Regresje** — utrzymano test jednego chunka dla krótkiego dokumentu jednojęzycznego oraz dodano test dokumentu wielojęzycznego potwierdzający osobne kody źródłowe dla jednostek.

### Tłumaczenie / niezawodność chunków
- **Ponowienie całego chunka przed fallbackiem jednostkowym** — po nieudanym batchu TranslationOrchestrator wykonuje drugą próbę tego samego chunka, zanim przejdzie do tłumaczenia jednostka po jednostce. Chroni to przed kosztownym i przedwczesnym rozbiciem poprawnego logicznie chunka na pojedyncze requesty.
- **Brak cichego pomijania jednostek** — wynik orkiestratora jest odrzucany, jeżeli któraś jednostka nie otrzymała wyniku; identyfikatory jednostek muszą być unikalne. Nie wolno zwracać częściowo przetłumaczonego dokumentu jako sukcesu.
- **Regresje retry i kompletności** — dodano testy potwierdzające: retry całego chunka, fallback jednostkowy dopiero po dwóch nieudanych próbach batcha, zachowanie kolejności oraz odrzucenie duplikatów i błędów jednostkowych.

### GUI / motyw — 2026-10-07 — weryfikacja mechanizmu Qt
- Historyczna próba zastąpienia palety mechanizmem schematu Qt została zweryfikowana i wycofana; aktualny mechanizm opisano w sekcji powyżej.

## 2026-10-07 — Filter Engine / Okapi: ochrona inline codes i lifecycle

- Dodano ochronę markerów Okapi na granicy backendu: PUA TextFragment jest przed tłumaczeniem zamieniany na tokeny ASCII __OKAPI_CODE_N__, a po odpowiedzi następuje ścisłe przywrócenie.
- Odpowiedź z brakującym, zduplikowanym lub przestawionym markerem jest odrzucana; system nie rekonstruuje markerów na podstawie samej liczby.
- Cache zachowuje oryginalny klucz źródłowy i wynik po restore.
- Reader threads stdout/stderr FilterHostClient nie są już daemon threads; shutdown wymusza zakończenie procesu i join obu wątków.
- Backup: backups/okapi-filter-engine-20261007/pre-fix.tar.gz, SHA-256 1c3edfad290f714c6fdbfee3be92fbf6c936f8ef9b4fba9a1cf1100fc7a9c533.
- Weryfikacja: 7 passed ochrony markerów/cache, 8 passed protokołu, 30 passed skoncentrowanego Filter Engine; pełny pytest 533 passed.
- Rzeczywisty backend llama.cpp był niedostępny w tej sesji; E2E raw request/response pozostaje otwarty.

---
## 2026-10-07

### Zmieniono — unifikacja startu llama.cpp w GUI

- Zunifikowano start, restart i autostart llama.cpp przez `_request_llama_server()`.
- Usunięto bezpośrednie uruchamianie llama.cpp z przepływu `start_translation()`.
- Tłumaczenie po kliknięciu „Tłumacz” jest teraz kontynuowane dopiero po zakończeniu asynchronicznego startu serwera.
- Restart po tłumaczeniu korzysta z tego samego mechanizmu co pozostałe wywołania.
- Dodano test regresyjny dla oczekiwania na gotowość serwera.
- Weryfikacja: 153 testy GUI PASS, Ruff PASS, compileall PASS.

## 2026-10-07 — redukcja obramowania treści Pomocy

- Usunięto widoczne obramowanie powierzchni `HelpMarkdownView`; `border.width` ustawiono jawnie na `0`, ponieważ wcześniejsze dodanie samego `border.color` korzystało z domyślnej szerokości 1 px i wprowadzało ramkę, której wcześniej nie było.

## 2026-10-07 — redukcja obramowania treści Pomocy

- Usunięto widoczne obramowanie powierzchni `HelpMarkdownView`; `border.width` ustawiono jawnie na `0`, ponieważ wcześniejsze dodanie samego `border.color` korzystało z domyślnej szerokości 1 px i wprowadzało ramkę, której wcześniej nie było.

## 2026-10-07 — Wdrożenie PLAN-12: TranslateGemma / chunkowanie / skip

- Wdrożono batchowe tłumaczenie: jeden logiczny chunk jest jednym requestem TranslateGemma w normalnej ścieżce.
- Dodano markery `⟦TG_SEG_N⟧`, walidację odpowiedzi, jedną próbę naprawczą oraz fallback jednostkowy.
- Rozszerzono `ChunkPlanner` o granice strukturalne V3: nagłówki po przekroczeniu 60% budżetu oraz granice zmiany języka źródłowego.
- Przekazano metadane Markdown z filtra do planera.
- Wdrożono pomijanie YAML front matter i linii metadanych zgodnie z semantyką V3.
- Dodano obsługę regionalnych kodów językowych `xx-YY` / `xx_YY` w normalizacji TranslateGemma.
- Dodano backup przed zmianą: `backups/20261007-plan12-pre-implementation/pre-change.tar.gz`.
- Weryfikacja ukierunkowana: 42 testy zakończone powodzeniem; Ruff i kompilacja modułów również zakończone powodzeniem.

## 2026-10-07 — naprawa pełnego motywu QML

- Naprawiono kolejność inicjalizacji GUI: paleta wybranego motywu jest ustawiana przed utworzeniem `QQmlApplicationEngine`.
- Nie wymuszamy zmiany stylu Qt Quick Controls; tryb `Systemowy` zachowuje natywne zachowanie systemu.
- Uzupełniono paletę jawnych motywów `Ciemny` i `Jasny` o komplet ról używanych przez styl Fusion (`Light`, `Midlight`, `Mid`, `Dark`, `Shadow`, `Highlight`, tooltipy, linki itd.), aby standardowe kontrolki nie odziedziczały jasnych kolorów z palety systemowej.
- Dodano regresję pilnującą kolejności `_apply_theme()` → `QQmlApplicationEngine()`.
- Udokumentowano defekt jako BUG-041 w `docs/BUG.md`.

## Aktualizacja 2026-10-07 — GUI/QML

- Naprawiono rzeczywistą przyczynę niewidocznych napisów zakładek Pomocy: aktywny QML cache mógł ładować starą skompilowaną wersję HelpPage.qml.
- Zakładki Pomocy zastąpiono pięcioma jawnymi elementami QML, związanymi bezpośrednio z bridge.helpTopic1Title–bridge.helpTopic5Title.
- Test GUI wymusza QML_DISABLE_DISK_CACHE=1 i sprawdza rzeczywiste teksty zakładek oraz ich zmianę DE → PL.
- Potwierdzono runtime motywu: dla ciemnego tło okna #202124 i zawartość #303134; dla jasnego #ffffff.

## 2026-10-07 — PLAN-12 TranslateGemma / chunkowanie / skip

- Przygotowano plan naprawczy na podstawie porównania V3 i V4.
- Potwierdzono, że V3 stosuje chunkowanie świadome struktury oraz mechanizm keep/skip przed backendem.
- Potwierdzono, że V4 obecnie grupuje jednostki w chunk, ale TranslationExecutor nadal wysyła każdą jednostkę jako osobny request.
- Ustalono docelowy kontrakt: jeden logiczny chunk = jeden request w normalnej ścieżce, jawny protokół segmentów, walidacja odpowiedzi i kontrolowany fallback.
- Ustalono konieczność formalnej walidacji kodów source/target TranslateGemma względem konkretnego tokenizer/runtime.
- Plan zapisano w `docs/Plany/PLAN-12-TRANSLATEGEMMA-CHUNKOWANIE-JEZYKI-SKIP-2026-10-07.md`.

## 2026-10-07 — bazowy pomiar inferencji CPU TranslateGemma

- Bezpośredni request do aktywnego `127.0.0.1:29710/completion` dla `Hello world.` zakończył się poprawnie w około **15,49 s**.
- Prompt miał 35 tokenów; ewaluacja promptu trwała **8,16 s** (około 4,29 tokena/s).
- Generowanie 5 tokenów trwało **7,01 s** (około 0,57 tokena/s).
- Wynik: `Witaj świecie.`, poprawny stop/EOS.
- Osobny większy request testowy nie zakończył się w limicie 60 s, co potwierdza, że większe wejścia mogą przekraczać minutę już dla pojedynczej inferencji.
- W połączeniu z potwierdzonymi 17 requestami dla jednego logicznego chunka daje to dwa niezależne źródła opóźnienia: wolna bazowa inferencja CPU oraz mnożenie kosztu przez liczbę requestów.

## 2026-10-07 — diagnostyka wydajności TranslateGemma na CPU

- Diagnostyka SentinelX na żywym runtime potwierdziła aktywny bundled `llama-server` Tłumacza na `127.0.0.1:29710`, CPU, `--parallel 1`, z poprawnym `/health` i jednym slotem.
- Dla rzeczywistego pliku `test_2000_chars.md` (2228 B) MarkdownFilter tworzy 17 jednostek o łącznej długości 905 znaków.
- `ChunkPlanner(max_chars=4000)` tworzy z nich jeden chunk, ale `TranslationExecutor` wywołuje `translate(...)` osobno dla każdej jednostki. Oznacza to 17 osobnych requestów HTTP/inferencji zamiast jednego requestu dla logicznego chunka.
- Jest to potwierdzony defekt architektoniczny przepływu i główny kandydat do naprawy wydajnościowej na CPU.
- W czasie diagnostyki host miał około 34 GiB zajętego swapu z 47 GiB, więc presja pamięci jest dodatkowym czynnikiem spowalniającym.
- `chunk_size` nie może być interpretowany jako liczba requestów; samo jego zwiększenie nie usuwa problemu wielokrotnych inferencji.
- Następna zmiana wymaga agregacji jednostek chunka do jednego requestu z zachowaniem mapowania wyników, cache, walidacji i zapisu formatu.
- Wyłączona/historyczna binarka llama.cpp v3 została świadomie wyłączona z tej diagnozy.

## 2026-10-07 — poprawka pomiaru szybkości tłumaczenia

- Naprawiono raportowanie szybkości tłumaczenia dla wolnego CPU.
- Wartości current_speed i average_speed nie są już obcinane do liczby całkowitej; są przechowywane z dokładnością do dwóch miejsc po przecinku.
- Przypadek 39 znaków / 100 s jest teraz raportowany jako 0,39 znaku/s, zamiast 0 znaków/s.
- Dodano test regresyjny dla szybkości poniżej 1 znaku/s.

## 2026-10-07 — izolacja sekretów profili Cloud

- Naprawiono test rekonstrukcji `QmlApplicationBridge`, aby wszystkie instancje testowe korzystały z tego samego jawnego `SecretStore`.
- Potwierdzono niezależność sekretów `ChatGPT` i `Codex` oraz brak wpływu domyślnego wpisu `local` na odczyt profilu Cloud.
- Nie wprowadzono niepotrzebnej zmiany produkcyjnego `bridge.py`; kontrakt `SERVICE/<service_id>` pozostaje bez zmian.
- Backup: `backups/SECRET-PROFILE-ISOLATION-BEFORE-2026-10-07.tar.gz`, SHA-256 `0e744e95b0b77498e656ea584cbd690093bfe356ddab97ab896e346311a12818`.
- Weryfikacja skoncentrowana: **14 passed** (`tests/test_cloud_secrets.py` + `tests/test_gui_i18n.py`).
- Rozszerzono regresje o jawne rozdzielenie `SERVICE/ChatGPT`, `SERVICE/Codex` i `SERVICE/local` oraz kontrolę, że zapis `config.json` nie zawiera sekretów ani `api_key`.
- Pełna suite pytest: **537 passed** w dwóch niezależnych przebiegach.
- `tests/test_qml_gui.py`: **153 passed**; przejściowe FAIL z nakładającego się uruchomienia nie powtórzyły się w kolejnych czystych przebiegach.
- Kontrole końcowe: `compileall` PASS, skan `config.json` bez sekretów PASS, `git diff --check` PASS.

## 2026-10-07 — skip-pattern / legacy konfiguracja

- Wzmocniono test regresyjny `test_document_translation_service_applies_skip_patterns_before_backend`: sprawdza również końcowy HTML, a nie tylko listę wywołań backendu.
- Potwierdzono, że aktywny V4 używa `$HOME/.config/tlumacz/config.json`; historyczny `build/lib/tlumacz/qml_gui/config.py` nadal zawiera dawny `settings-v4.json` i nie może być używany jako runtime.
- Usunięto pozostały aktywny `$HOME/.config/tlumacz/settings-v4.json`.

---

## 2026-10-07 — kanoniczna konfiguracja GUI

- `$HOME/.config/tlumacz/config.json` jest jedynym aktywnym źródłem trwałej konfiguracji GUI.
- `settings-v4.json` jest plikiem historycznym/legacy i nie może być tworzony ani używany przez aktywny kod.
- Zaktualizowano dokumentację PLAN-07 oraz raport Security/Lifecycle do kontraktu `config.json`.

---

## 2026-10-07 — naprawa testu skip patterns

- Naprawiono `test_document_translation_service_applies_skip_patterns_before_backend`.
- Test używa rzeczywistego `HtmlFilter` zamiast fixture'a naruszającego kontrakt `session.units`.
- Poprawiono wzorzec `^\\[NO_TRANSLATE\\]`, aby prawidłowo identyfikował jednostkę pomijaną przed backendem.
- Weryfikacja: cały `tests/test_document_translation_service.py` — **5 passed**.

---

## 2026-10-06 — lifecycle llama.cpp, URL i pomijanie fragmentów

- Start/restart llama.cpp wykonywany asynchronicznie poza wątkiem QML.
- „Adres URL” llama.cpp jest normalnym, nieedytowalnym polem informacyjnym.
- Port llama.cpp pochodzi wyłącznie z pola „Port”; `base_url` nie nadpisuje już portu przy odczycie ustawień.
- Naprawiono wybór `TranslateGemma` w ComboBoxie.
- Wzorce pomijania są stosowane przed wywołaniem backendu i zachowują pomijane fragmenty bez zmian.

## 2026-10-06 — port llama.cpp z GUI i zwrotny adres URL

- Uporządkowano kontrakt karty „API i serwer”: port llama.cpp jest pobierany wyłącznie z kontrolki „Port”.
- Dodano QML-ową właściwość bridge.serverUrl wyliczaną z hosta i aktualnego portu.
- Pole „Adres URL” dla llama.cpp prezentuje ten adres jako informację zwrotną i jest nieedytowalne.
- Zmiana portu w GUI automatycznie zmienia prezentowany endpoint http://<host>:<port>/v1; restart korzysta z tego samego settings.server_port.
- Dodano regresje TDD dla źródła portu i prezentacji adresu URL.

## [Unreleased] — 2026-10-06 — domknięcie Apertium runtime

### Apertium / runtime
- Uzupełniono prywatny runtime Apertium 3.9.12 o `cg-proc`, `libcg3.so.1`, `lsx-proc`, `apertium-anaphora` i `libsqlite3.so.0`, bez instalacji systemowej.
- Gotowość paczek po smoke: **27 READY / 1 EXCLUDED** z 28 przygotowanych kierunków.
- `ces-pol` pozostaje wyłączone z release scope, ponieważ dostarczony model `ces-pol.prob` powoduje wewnętrzną asercję `apertium-tagger`; nie oznaczono go jako READY na podstawie samego kodu wyjścia procesu.
- Do runtime dodano dokument `TOOLS-ADDITIONS.md` oraz licencje GPL-3 dla CG-3 i Apertium Anaphora.

### Packaging
- Wheel `tlumacz-0.40.0-py3-none-any.whl` zweryfikowano w czystym staging-tree; artefakt zawiera nowe narzędzia runtime.
- Bezpośredni build w istniejącym drzewie pozostaje ograniczony przez ACL właściciela starego artefaktu Okapi; nie zmieniano uprawnień ani właściciela.

### GUI / testy
- Ustabilizowano test tematów Pomocy tak, aby nie zależał od prywatnego `$HOME/.config/tlumacz/config.json`.
- Potwierdzono obecność animowanego `translationWorkOrb` w wierszu statystyk.

## 2026-10-06 — przywrócenie animowanego wskaźnika i semantyki błędu bloku

- Przywrócono animowany `translationWorkOrb` w `TranslationPage.qml`: obrót, pulsowanie i zmiana koloru podczas aktywnego tłumaczenia.
- Usunięto tekstowy etap `translationStage` z wiersza statystyk; diagnostyka pozostaje w Logu.
- Dodano `chunkFailed(current, total, message)` oraz komunikat lokalizowany `log.chunk_failed`.
- Błąd bloku kończy stan tłumaczenia, zatrzymuje wskaźnik i nie może prowadzić do komunikatu podsumowującego sukces.
- Potwierdzono spójność portu: GUI → `TranslationApp.start_llama()` → `LlamaCppRuntimeConfig` używa `server_port=2782`; wcześniejszy osierocony bundled `llama-server` na 28783 został zatrzymany.
- Backup: `backups/20261006-translation-orb-status-port/pre-change.tar.gz`, SHA-256 `ca557a31265ceb27f2cf013a8ce000d21a9c1a4a9b2c9a00fc932b023ba567d3`.

## 2026-10-06 — Apertium runtime discovery gate

- discovery weryfikuje teraz wymagane programy pipeline'u z modes.xml, a nie tylko obecność plików danych;
- ApertiumRuntime.language_pairs() zwraca wyłącznie rzeczywiste pary source-target i odrzuca tryby pomocnicze;
- smoke 28 przygotowanych paczek potwierdził 17 READY i 11 BLOCKED w prywatnym runtime;
- nie instalowano brakujących cg-proc, lsx-proc ani apertium-anaphora;
- dodano regresje TDD dla brakujących i dostępnych programów runtime;
- testy warstwy Apertium: 48 passed; focused discovery/runtime: 13 passed;
- raport: docs/reports/FAZA_6_APERTIUM_RUNTIME_GATE_2026-10-06.md;
- backup przed zmianą discovery: backups/plan-04-apertium-before-discovery-fix-20261006-221425.tar;
- backup przed aktualizacją dokumentacji: backups/plan-04-apertium-before-docs-20261006-221901.tar.

## 2026-10-06 — naprawa `pol-eng` i przenośność paczek Apertium

- naprawiono `apertium-eng-pol.pol-eng.t3x`: zadeklarowano brakujący atrybut `a_SN` z wartością `PDET`;
- wygenerowano brakujący `pol-eng.autogen.bin`; ostrzeżenia o duplikatach `pardef` w `apertium-eng-pol.pol.dix` pozostają odnotowane, ale nie blokują bezpośredniego `lt-comp`;
- przygotowano `apertium-pol-eng-1.0.0.tar`; instalacja do czystego magazynu i rzeczywiste tłumaczenie `pl → en` przeszły poprawnie;
- poprawiono builder paczek, aby usuwał absolutne ścieżki hosta z plików `.mode`; znormalizowano istniejące 27 paczek i dodano 28. paczkę `pol-eng`;
- wszystkie 28 archiwów mają odświeżone checksumy indywidualne oraz `SHA256SUMS`;
- usunięto `hye-eng` z lokalnego magazynu runtime Apertium; przed usunięciem wykonano backup;
- backup naprawy `pol-eng`: `backups/pol-eng-fix-20261006-215919/pol-eng-before-fix.tar`, SHA-256 `9af0a21fb5d089b59c97fb4fd6a333743540f04dd8e461e6ce1f9407063a7d1c`;
- backup magazynu `pary/` przed normalizacją trybów: `backups/pary-mode-normalization-20261006-220233/pary-before.tar`, SHA-256 `b3483ef7d2399fe397d7f3930befe502b287672af20653c2651ad511adddf43d`;
- backup usuniętego runtime `hye-eng`: `backups/hye-runtime-removal-20261006-220126/hye-runtime.tar`, SHA-256 `21219c36321936b42ff684c68133940e3b9a4efcd01cfd0a9ea89cac7f3e79ec`;

## 2026-10-06 — przebieg komunikatów tłumaczenia i wskaźnik postępu

- usunięto animowaną kulkę z `TranslationPage.qml` i zastąpiono ją tekstowym wskaźnikiem etapu oraz licznikiem bloków;
- usunięto podwójne emitowanie komunikatu `Rozpoczęto tłumaczenie.`;
- dodano komunikat o wybranym skillu i uporządkowano `Gotowy do tłumaczenia.` tak, aby występował po komunikatach uruchomieniowych;
- dodano komunikaty o wczytaniu dokumentu, pominiętych fragmentach, liczbie bloków, każdym tłumaczonym bloku, podsumowaniu czasu/szybkości i ścieżce wyniku;
- szybkość tłumaczenia jest prezentowana jako znaki/s na podstawie rzeczywistych ukończonych chunków;
- akcje końcowe raportują opróżnienie bufora oraz zatrzymanie/uruchomienie llama.cpp, gdy odpowiednie opcje lifecycle są aktywne;
- dodano callbacki chunków w `TranslationOrchestrator` i `DocumentTranslationService` oraz regresje TDD dla GUI i pipeline'u dokumentowego;
- backup implementacji: `backups/20261006-translation-progress-ui/pre-change.tar.gz`, SHA-256 `cc1d4e07d4df76d30987ee8eeee30b634b2e11e5e3e118b816399546ee1d060a`;
- backup dokumentacji: `backups/20261006-translation-progress-ui/docs/pre-docs-update.tar.gz`, SHA-256 `9509108d75cae8d26e2dc7fb1a6f75a9a7dd7271d72178a931ea054847e6c0dc`.

---

## 2026-10-06 — zamknięcie BUG-038: runtime Apertium

- przywrócono `u+x` oraz `g+x` dla programów prywatnego runtime Apertium w `native_runtime/bin` i `native_runtime/libexec`;
- nie zmieniano właściciela ani ACL;
- świeża inspekcja potwierdziła prawa wykonywania dla programów runtime;
- regresja `test_bundled_runtime_programs_are_owner_executable`: **1 passed, 8 deselected**;
- BUG-038 jest zamknięty; wcześniejsze informacje o braku `u+x` pozostają wyłącznie jako historia diagnozy.


## 2026-10-06 — audyt par i automatyzacja paczek Apertium

- Dodano `package_pipeline.py` do wykrywania kompletnych kierunków, budowania wszystkich kierunków z jednego repozytorium oraz oczyszczania magazynu runtime.
- Dodano `tools/apertium/package_pairs.py`, który może pobierać repozytorium, uruchamiać istniejący `apertium-get.py`, pakować oba kierunki i generować SHA-256.
- Builder filtruje `modes.xml` do jednego kierunku zamiast kopiować definicje pozostałych trybów.
- Przygotowano 27 osobnych paczek .tar dla 13 rodzin dwukierunkowych oraz kierunku eng-pol.
- Dodano pełny audyt `apertium-pair-inventory-20261006.md`.
- Oczyszczono magazyn `$HOME/.config/tlumacz/Apertium/` z materiałów developerskich po wykonaniu backupu.
- pol-eng pozostaje nieopublikowany po nieudanej kompilacji `pol-eng.t3x.bin`; hye-eng pozostaje nieopublikowany do ustalenia licencji.

## 2026-10-06 — paczki par językowych Apertium

- Dodano format `apertium-<pair>-<version>.tar` jako niekompresowany kontener pojedynczego kierunku Apertium.
- Dodano builder `ApertiumPairPackageBuilder` oraz bezpieczny `ApertiumPairPackageInstaller` z manifestem, SHA-256 i ochroną ścieżek.
- Dodano testy formatu, instalacji i path traversal w `tests/test_apertium_packages.py`.
- Przygotowano cztery publikowalne artefakty w `pary/`: eng-pol, eng-spa, spa-eng i bn-en.
- Udokumentowano pełną procedurę tworzenia paczek przez innych twórców w `docs/technical-docs/apertium-pair-packages.md`.
- Nie publikujemy pol-eng z powodu braku kompletnego zestawu skompilowanych danych oraz hye-eng do czasu ustalenia licencji źródłowej.
## 2026-10-06 — polityka platformowa llama.cpp

- Udokumentowano, że obecny bundled runtime Linux x86_64 jest buildem dedykowanym dla hosta referencyjnego Bmax.
- Dla innych Linux, Windows i macOS do czasu przygotowania osobnych ogólnych artefaktów należy korzystać z runtime'u systemowego.
- Zdefiniowano zasadę, że paczka dystrybucyjna musi używać bardziej ogólnych parametrów kompilacji, a optymalizacje pod konkretny CPU/GPU pozostają wyłącznie dla buildów dedykowanych.
- Dodano kartę referencyjną sprzętu oraz TODO dla automatycznego wykrywania sprzętu, generowania konfiguracji, kompilacji i benchmarków llama.cpp.

# Zmiany — 2026-10-06

## llama.cpp — dołączony runtime

- Dodano dedykowany runtime llama.cpp dla Linux x86_64, zbudowany ze źródeł `/home/frs/Projekty/llama.cpp` w konfiguracji CPU-native: Release, GGML_NATIVE, CPU repack, OpenMP, bez CUDA/Vulkan/SYCL/OpenCL/ZenDNN.
- Domyślna konfiguracja odzyskanego profilu V3 została ustawiona na `threads=auto`, `threads-batch=auto`, `batch-size=2048`, `ubatch-size=512`, `ctx-size=8192`, prompt cache ON, cache reuse 0, Flash Attention OFF, repack ON, KV K Q8_0, KV V F16.
- Aplikacja domyślnie uruchamia runtime dołączony do pakietu i ustawia lokalny `LD_LIBRARY_PATH`, aby biblioteki llama.cpp pochodziły z tej samej kompilacji.
- Zachowano wybór runtime'u systemowego przez `$HOME/.config/tlumacz/llama.json`: `runtime.source=system` oraz `runtime.executable`.
- Dodano dokumentację podmiany dołączonej kompilacji własnym buildem i diagnostyki ABI.
- Dodano regresje konfiguracji runtime'u oraz obecności binariów w pakiecie.
- Świeża walidacja: dołączony runtime uruchamia `/health`, `parallel=1` daje 1 slot z `n_ctx_slot=8192`, `parallel=4` daje 4 sloty z `n_ctx_slot=2048`, a rzeczywiste PL→EN krótkiego tekstu przez TranslateGemma zakończyło się w 5,57 s.
- Narzut plików binarnych runtime'u wynosi około 23,2 MB przed kompresją.


## 2026-10-06 — TPlugin lifecycle: update / uninstall / rollback

- TPluginInstaller otrzymał operacje update(), uninstall() i rollback().
- Update i uninstall wykonują backup aktywnego pluginu przed zmianą.
- Backup lifecycle zawiera również wymagane biblioteki shared, aby rollback był samowystarczalny.
- Dodano testy TDD dla wersjonowania, rollbacku po aktualizacji, odinstalowania oraz rollbacku po uninstall.
- Dodano macierz obejmującą wszystkie 9 publicznych paczek .tplugin.
- Weryfikacja: 12 passed w tests/test_tplugin.py.
- TODO-022m zamknięte.
- Backup implementacji: backups/tplugin-lifecycle-20261006/pre-lifecycle.tar.gz; SHA-256 b9d14ea5f14b7684270ecc52b00c97f41a95727f0d7933674c3eb0c9eb9179bf.
## [Unreleased] — 2026-10-06 — migracja runtime TPlugin

### Zmienione
- FilterStore domyślnie wskazuje rozpakowane pluginy w $HOME/.config/tlumacz/filter-engine/plugins/.
- FilterRegistry automatycznie odkrywa pluginy na podstawie plugin.json i extensions.
- Dodano obsługę entrypointu znajdującego się w shared-libs.
- Wszystkie 9 filtrów Okapi zostało zainstalowanych do runtime TPlugin.
- Przygotowano publiczny katalog nierozpakowanych paczek w dist/tplugins/.

### Weryfikacja
- 21 testów TPlugin/FilterRegistry/FilterHost — PASS.
- FilterHost capabilities 9/9 — PASS.
- Registry runtime wykrywa wszystkie wymagane rozszerzenia.
- Backup runtime wykonany przed przełączeniem.
## [Unreleased] — 2026-10-06 — naprawa reaktywności tematów Pomocy po zmianie języka

### Naprawione
- naprawiono przypadek, w którym zakładki tematów Pomocy pozostawały z niemieckimi tytułami po przełączeniu GUI na język polski;
- zmieniono model `Repeater` w `HelpPage.qml` ze statycznej tablicy właściwości bridge na reaktywny kontrakt `helpTopicTitles` + `model: 5`;
- dodano regresję potwierdzającą zmianę tytułów tematów przy zmianie języka;
- zaktualizowano dokumentację GUI i `docs/BUG.md`.

### Weryfikacja
- regresja HelpPage — PASS;
- test runtime etykiet Pomocy — PASS;
- `qmllint` — PASS;
- `compileall` — PASS.
## [Unreleased] — 2026-10-06 — TPlugin: wszystkie filtry Okapi

### Dodane
- Przygotowano dziewięć paczek instalacyjnych .tplugin dla aktualnych filtrów Okapi: EPUB, HTML, JSON, Markdown, OpenOffice, OpenXML, XLIFF 1.2, XLIFF 2 i YAML.
- Dodano deklaratywny inventory budowania w tools/tplugin/build_all.py.
- Rozszerzono TPluginBuilder o fizyczne przenoszenie zależności shared do lib-shared oraz manifestowanie ich jako shared dependencies.
- Umożliwiono entrypointowi pluginu wskazywanie JAR-a znajdującego się w lib-shared.
- Poprawiono launcher java/filter-host/run.sh, aby korzystał z aktualnych źródeł FilterHost/FilterLoader.

### Weryfikacja
- 14 ukierunkowanych testów TPlugin/FilterHost — PASS.
- Instalacja wszystkich 9 paczek do pustego profilu — PASS.
- FilterHost capabilities dla 9/9 pluginów — PASS.
- Brak archiwów .tplugin w runtime po instalacji — PASS.
- Deduplikacja shared-libs — PASS.
## 2026-10-06 — zwiększenie timeoutu lokalnego llama.cpp dla TranslateGemma

- odtworzono timeout 120 s na rzeczywistym requestcie TranslateGemma przez `/v1/completions` dla większego chunku;
- timeout przekazywany przez GUI dla backendu `llama.cpp` zwiększono z **120 s do 300 s**;
- zakres zmiany obejmuje oczekiwanie na pełną odpowiedź HTTP i nie zmienia timeoutów lifecycle serwera;
- dodano regresję QML potwierdzającą wartość `selection.timeout == 300.0`;
- backup: `backups/llama-timeout-20261006/pre-change.tar.gz`, SHA-256 `d7beff92dfcd47e176af7a8504cb3972d53292d410825bdcb6edb2b46985676a`.

## 2026-10-06 — pełne udokumentowanie separacji magazynu filtrów

Udokumentowano rzeczywisty stan katalogu `filters/` po etapach lazy-load, dynamicznego `FilterLoader` oraz separacji implementacji od wspólnego runtime. Potwierdzono fizyczną obecność implementacji filtrów `epub`, `html`, `json`, `markdown`, `openoffice`, `openxml`, `xliff`, `xliff2` i `yaml` w `filters/<nazwa>/`. Wyszczególniono, że część zależności nadal jest przejściowo reprezentowana przez symlinki do `okapi-runtime`. Zapisano fizyczne zależności już dołączone do pakietów, w tym zestaw `flexmark*` dla Markdown oraz `common-io-3.12.0.jar` dla OpenXML. Doprecyzowano, że TODO-022j dotyczy końcowej migracji zależności do samowystarczalnych pakietów i nie jest jeszcze zamknięte.

## 2026-10-06 — domknięcie zależności OpenXML

- do `filters/openxml/` dołączono lokalny `common-io-3.12.0.jar` wymagany przez klasy OLE2 filtra OpenXML;
- `filters/openxml/filter.json` wskazuje pełny artefakt `com.twelvemonkeys.common:common-io:3.12.0`;
- walidator zależności potwierdza teraz `usable=True` dla OpenXML i obecność `CompoundDocument` oraz `CorruptDocumentException`;
- nie wykonano pobierania ani instalacji biblioteki do systemu — wykorzystano już obecną kopię z prywatnego runtime Okapi;
- testy zależności i dynamicznego Filter Host: **7 passed**.

## 2026-10-06 — akcje po zakończeniu tłumaczenia: cache i restart llama.cpp

- checkbox „Czyść cache po tłumaczeniu” wykonuje `TranslationApp.clear_translation_cache()` po poprawnym zakończeniu tłumaczenia;
- checkbox „Restart serwera llama.cpp po tłumaczeniu” wykonuje kontrolowany `STOP → START` tylko dla aktywnego i działającego llama.cpp;
- restart po tłumaczeniu korzysta z aktualnej konfiguracji GUI, tak samo jak restart przyciskiem;
- dodano test regresyjny potwierdzający przekazanie aktualnego GGUF i parametrów serwera do restartu po tłumaczeniu;
- zachowano niezależne akcje po tłumaczeniu dla Apertium i Chmury.

## 2026-10-06 — korekta sterowania cyklem życia llama.cpp

- ręczny wybór backendu `llama.cpp` uruchamia serwer natychmiast i nie zmienia ustawienia autostartu;
- zmiana z `llama.cpp` na inny backend zatrzymuje lokalny serwer przed zmianą backendu;
- `Restartuj serwer` wykonuje `STOP → START` na bieżącej konfiguracji GUI, zamiast odtwarzać konfigurację starego runtime;
- `auto_start_server` jest respektowane wyłącznie przy uruchomieniu programu z aktywnym `llama.cpp`;
- dodano regresje TDD dla rozdzielenia ręcznego startu od autostartu oraz dla restartu z aktualną konfiguracją GUI.

## 2026-10-06 — pełny gate po etapie 022i

- pełny pytest: **389 passed, 2 failed**;
- dwa pozostałe failure dotyczą niezależnie runtime Apertium i lokalizacji języka pomocy QML;
- regresje Okapi wprowadzone podczas separacji runtime zostały usunięte; testy zakresu etapu zakończyły się **22 passed**.

## 2026-10-06 — etap 3 rozdzielenia runtime Okapi

- przeniesiono fizyczne JAR-y implementacji dziewięciu aktywnych filtrów do `filters/<nazwa>/`;
- zmieniono launchery Java Filter Host tak, aby parent classpath zawierał tylko `okapi-core` i wspólne biblioteki, bez `okapi-runtime/*`;
- przypisano zależności wewnętrzne filtrów do ich pakietów przez przejściowe symlinki bez tworzenia drugich fizycznych kopii;
- przeniesiono biblioteki `flexmark*` do pakietu Markdown jako zależność specyficzną dla tego filtra;
- dodano regresję `tests/test_okapi_runtime_split.py` dla separacji implementacji i zależności;
- dodano kontekstowy `ClassLoader` dla konfiguracji Okapi, co przywróciło rzeczywiste round-trip EPUB/OpenXML bez globalnego classpathu implementacji;
- wykryto brakujący artefakt `com.twelvemonkeys.io.ole2` wymagany przez część OpenXML; nie pobierano nowych bibliotek;
- backup: `backups/okapi-runtime-split-20261006/pre-split.tar.gz`, SHA-256 `1085f98edcd58c6cee816571cce626452c80b3807b51ffe2e5b8b52561d5e9c2`.

## 2026-10-06 — etap 2 dynamicznego loadera Java filtrów

- dodano `FilterLoader` dla pakietów filtrów opisanych przez `filter.json`;
- konkretny filtr jest tworzony dopiero po żądaniu danego formatu, w osobnym `URLClassLoader`;
- loader obejmuje cały pakiet klas implementacji filtra, aby klasy wewnętrzne nie były mieszane z klasami z globalnego classpathu;
- po zamknięciu sesji dokumentu zamykany jest również `URLClassLoader`;
- `run.sh` obsługuje jawny runtime i magazyn filtrów przez zmienne środowiskowe;
- dodano przejściowe symlinki pakietów aktywnych filtrów w `filters/`, bez kopiowania i usuwania istniejących JAR-ów;
- weryfikacja: łączony gate **38 passed**; Ruff, compileall, składnia launcherów i `git diff --check` — PASS.

## 2026-10-06 — etap 1 lazy-load filtrów dokumentowych

- `FilterRegistry` otrzymał `register_lazy()` i przechowuje fabryki zamiast instancji filtrów w aktywnej ścieżce aplikacji.
- `TranslationApp` rejestruje filtry Okapi przez fabryki; implementacja konkretnego formatu jest tworzona dopiero po rozpoznaniu rozszerzenia wejściowego.
- Instancja filtra jest własnością sesji dokumentu i jest zamykana przez `FilterLifecycle` po zakończeniu lub błędzie.
- Dodano regresje potwierdzające brak inicjalizacji przed użyciem oraz brak zatrzymania instancji przez rejestr po jej użyciu.
- Nie przeniesiono jeszcze JAR-ów z `okapi-runtime`; dynamiczny Java `ClassLoader` jest kolejnym etapem.
- Weryfikacja: rejestr **8 passed**, lifecycle/runtime **15 passed**.


## 2026-10-06 — magazyn filtrów użytkownika

- dodano `FilterStore` jako warstwę lokalizacji magazynu filtrów;
- bieżący magazyn deweloperski wskazuje `<katalog projektu>/filters/`;
- przygotowano docelową lokalizację `/home/frs/.config/tlumacz/filters/`;
- `FilterRegistry` przyjmuje jawnie ścieżkę magazynu;
- nie wprowadzono jeszcze automatycznego ładowania dowolnych pakietów filtrów; aktywne filtry pozostają jawnie rejestrowane.

## 2026-10-06 — weryfikacja i zamknięcie Planu 03 llama.cpp + TranslateGemma

- zweryfikowano aktualny runtime llama-server 0.4.0-dev (build 10809, commit 5266f24da);
- potwierdzono stabilny kontrakt TranslateGemma: --no-jinja + ręcznie renderowany prompt Gemma + /v1/completions;
- świeży test natywnego Jinja wykazał niekompatybilność automatycznego parsera typed-content w aktualnym runtime, dlatego nie przywracano historycznej ścieżki chat_template_kwargs;
- realny model translategemma-4b-it.Q5_K_M.gguf przeszedł E2E przez TranslationApp oraz QmlApplicationBridge;
- focused suite: 37 testów llama.cpp/TranslateGemma i 43 testy GUI — PASS;
- nie zmieniono produkcyjnego kodu, ponieważ bieżąca implementacja spełnia kontrakt Planu 03.

## 2026-10-06 — synchronizacja dokumentacji bieżącej wersji 0.40.0

- oznaczono rzeczywisty TranslateGemma GUI E2E jako wykonany;
- zsynchronizowano bieżący gate: 373 passed, 1 failed;
- wskazano jedyny aktualny failure: 34 pliki runtime Apertium bez `u+x`;
- zaktualizowano STATUS, TODO, BUG, ARCHITECTURE i RELEASE_NOTES_0.40.0 do stanu Release Candidate;
- zachowano otwarte blokery: runtime Apertium, entrypoint V4, clean-wheel/Git ownership oraz dependency closure/licencje.

## 2026-10-06 — natychmiastowy start llama.cpp po zmianie backendu

- zmiana backendu na `llama.cpp` uruchamia serwer natychmiast;
- `auto_start_server=True` jest zapisywane od razu do ustawień;
- llama.cpp nie czeka już na rozpoczęcie tłumaczenia;
- przejście z llama.cpp na inny backend nadal zatrzymuje serwer;
- dodano regresję TDD dla natychmiastowego `start_llama()`.

## 2026-10-06 — świeży Plan 05: Release Candidate utrzymany

- wykonano ponowny pełny gate jakości na aktualnym stanie V4;
- pełny pytest: **373 passed, 1 failed**;
- wykryto brak `u+x` w 34 plikach bundlowanego runtime Apertium; próba korekty z bieżącej sesji została odrzucona przez ACL i nie zmieniano właściciela plików;
- Ruff, mypy, compileall i qmllint: **PASS**;
- macierz backendów/dokumentów/GUI/packagingu: **181 passed**;
- `python -m tlumacz --version` nie działa z powodu braku `tlumacz.__main__`, a globalny `/usr/bin/tlumacz` pozostaje V3;
- clean-wheel build został zablokowany przez Git `dubious ownership` dla `/home/frs/Projekty`;
- decyzja: projekt pozostaje **Release Candidate**, bez oznaczenia final release.

## 2026-10-06 — zabezpieczenie połączenia GUI z llama.cpp

- `start_translation()` zapewnia działający runtime llama.cpp tuż przed budową usługi tłumaczenia;
- jeśli serwer został zatrzymany po uruchomieniu GUI, aplikacja automatycznie uruchamia go ponownie z bieżącej konfiguracji GUI;
- dodano regresję obejmującą rzeczywisty przepływ QML → bridge → TranslationApp → TranslateGemma po celowym zatrzymaniu serwera;
- zidentyfikowano osobny problem launchera systemowego: `/usr/bin/tlumacz` uruchamia V3 `0.31.2`; V4 otrzymał repozytoryjny launcher `uruchom-tlumacz-v4.sh` i `Tlumacz-V4.desktop`.

## 2026-10-06 — korekta i zamknięcie E2E TranslateGemma

- skorygowano wcześniejsze przedwczesne oznaczenie E2E, a następnie wykonano świeżą weryfikację przez rzeczywiste GUI;
- GUI użyło endpointu `http://127.0.0.1:2782/v1`; techniczne parametry runtime pochodziły z `/home/frs/.config/tlumacz/llama.json`;
- `llama-server` został uruchomiony przez aplikację na porcie `2782`;
- odebrano `translationFinished`, status `Tłumaczenie zakończone.`, a wynik Markdown został zapisany;
- Plan 01 i TODO-003 są zamknięte na podstawie świeżego dowodu E2E.

## 2026-10-06 — zatrzymywanie llama.cpp przy zmianie serwera

- zmiana z llama.cpp na inny backend zatrzymuje lokalny runtime llama.cpp przed zmianą backendu;
- dodano regresję TDD dla przełączenia llama.cpp → Chmura;
- testy funkcjonalne GUI potwierdzają oba kierunki: wybór llama.cpp włącza autostart, a opuszczenie llama.cpp zatrzymuje serwer.

## 2026-10-06 — naprawa połączenia GUI z konfiguracją llama.cpp

- naprawiono normalizację ścieżki GGUF z QML `file:///...` do lokalnej ścieżki pliku podczas ładowania i zapisu ustawień GUI;
- zachowano rozdzielenie źródeł konfiguracji: stan GUI z `settings-v4.json`, tuning techniczny z `/home/frs/.config/tlumacz/llama.json` z fallbackiem do `config/llama.json`;
- potwierdzono rzeczywiste uruchomienie `llama-server` przez `QmlApplicationBridge`, bez ręcznego uruchamiania z wiersza poleceń;
- świeże GUI E2E na `translategemma-4b-it.Q5_K_M.gguf` zakończyło się wynikiem `Witaj świecie. To krótkie testowanie.`;
- po weryfikacji serwer TranslateGemma został zatrzymany.

## 2026-10-06 — wybór llama.cpp włącza autostart serwera

- przełączenie backendu na llama.cpp ustawia auto_start_server=True;
- wybór llama.cpp w GUI oznacza uruchamianie lokalnego serwera razem ze startem programu;
- istniejący checkbox „Automatyczny start llama.cpp” nadal pozwala użytkownikowi wyłączyć autostart;
- dodano regresję TDD dla przełączenia Apertium → llama.cpp;
- focused testy: 3 passed, 101 deselected.

## 2026-10-06 — finalna weryfikacja V4

- pełny pytest: **367 passed, 0 failed**;
- compileall, qmllint i git diff --check: PASS;
- rzeczywisty GUI E2E TranslateGemma: PASS.

## 2026-10-06 — Plan 01 / TranslateGemma GUI E2E

- Podłączono i zweryfikowano rzeczywisty przepływ TranslateGemma przez QML GUI, QmlApplicationBridge, TranslationApp, DocumentTranslationService i llama.cpp.
- Naprawiono obsługę ścieżki GGUF z QML `FileDialog`: QUrl `file://...` jest normalizowany do lokalnej ścieżki i zapisywany w ustawieniach.
- Naprawiono runtime TranslateGemma: `--no-jinja`, ręcznie renderowany prompt Gemma i endpoint `/v1/completions`, zgodnie z rzeczywistym kontraktem aktualnego llama.cpp.
- Rzeczywisty E2E na `translategemma-4b-it.Q5_K_M.gguf`: en→pl PASS; wynik dokumentowy zapisany poprawnie.
- Zamknięto macierz round-trip aktywnych formatów: **28 passed**.
- Plan 01 oznaczono jako zamknięty.

## 2026-10-06 — korekta karty API i persystencji ustawień llama.cpp

- usunięto z sekcji llama.cpp osobne pole „Adres serwera” i dodatkową etykietę wyliczonego URL-u;
- przywrócono właściwą kolejność: separator → nagłówek serwera → port → obliczenia → szablon czatu → parallel → model → zachowanie backendu → restart;
- zachowano istniejącą typografię i separatory QML;
- `Main.qml` zapisuje `bridge.saveSettings()` przy zamknięciu okna, dzięki czemu ostatnie ustawienia llama.cpp są odtwarzane po ponownym uruchomieniu;
- dodano regresje dla powierzchni QML i persystencji ustawień;
- focused GUI: **102 passed**.

## 2026-10-06 — ochrona targetu TranslateGemma

- odtworzono stan pustego `target_language` przed wejściem do llama.cpp;
- dodano normalizację pustego targetu llama.cpp do `pl` w bridge przed startem tłumaczenia;
- dodano test regresyjny;
- rozszerzono kanoniczny opis detekcji Lingua i routingu llama.cpp w `docs/INDEX.md` oraz `docs/ARCHITECTURE.md`.

## 2026-10-06 — separacja routingu języka llama.cpp

- wydzielono `LlamaCppLanguageRouting` do backendu llama.cpp;
- detekcja Lingua pozostaje niezależnym modułem;
- llama.cpp wykrywa źródło osobno dla każdego chunka;
- `LlamaCppAdapter` nie wykonuje detekcji;
- Cloud/custom nie otrzymują routingu llama.cpp;
- usunięto ogólny `DynamicLanguageRouting` z aktywnej ścieżki;
- dodano regresje TDD dla separacji i routingu.

## 2026-10-06 — naprawa pustego targetu po przełączeniu Apertium → llama.cpp

- ustalono przyczynę błędu `Nieobsługiwany język docelowy TranslateGemma: ''`;
- Apertium może wyzerować target, gdy filtrowanie par nie znajduje dostępnego celu;
- przełączenie na llama.cpp nie przywracało wcześniej wartości docelowej, więc pusty target trafiał do `LlamaCppAdapter`;
- po przełączeniu na backend z globalnym targetem pusty stan jest normalizowany do `pl`;
- `TranslationPage.qml` nie maskuje już nieprawidłowego indeksu ComboBox przez wymuszenie `0`;
- dodano regresje TDD dla przełączenia backendu i zachowania selektora QML.

## 2026-10-06 — GUI tłumaczenia → llama.cpp

- źródłowy język z konfiguracji tłumaczenia nie jest już zastępowany bezwarunkowo wartością `auto` przy starcie llama.cpp;
- język docelowy pozostaje przekazywany do adaptera i specjalnego kontraktu TranslateGemma;
- ścieżka wejściowa i wyjściowa są jawnie utrzymane w operacji dokumentowej obsługującej llama.cpp;
- dodano test kontraktu GUI: język + GGUF + endpoint + pliki wejścia/wyjścia.

## 2026-10-06 — rozdzielenie mechanizmów detekcji języka

- wdrożono ApertiumLanguageRouting jako niezależny mechanizm: detekcja dokumentu, zamrożony source/target i decyzja chunk tłumacz/pomiń;
- wdrożono DynamicLanguageRouting dla pozostałych backendów: detekcja źródła niezależnie dla każdego chunka;
- TranslationOrchestrator przekazuje źródło wykryte dla bieżącego chunka do backendu;
- pominięte fragmenty Apertium pozostają niezmienione;
- cache uwzględnia source_language;
- adapter TranslateGemma korzysta z source przekazanego przez routing zamiast wykonywać własną detekcję;
- dodano testy TDD obu ścieżek oraz regresje executora, orkiestratora, cache i usługi dokumentowej.

## 2026-10-06 — GUI/runtime llama.cpp: kontrakt ustawień

- dodano w karcie API i serwer jawny adres serwera powiązany z osobnym polem portu;
- port, CPU/GPU, parallel, GGUF i szablon czatu są przekazywane do llama-server;
- Rozmiar bloku 500–8000 i Temperatura 0.0–1.0 są przekazywane do pipeline/adaptera;
- runtime odczytuje techniczne ustawienia z $HOME/.config/tlumacz/llama.json, z fallbackiem do config/llama.json;
- ctx-size, batch, cache, Flash Attention, repack, NUMA, GPU layers, KV unified i polling są składane do komendy zgodnie z profilem technicznym;
- start serwera oczekuje na /health HTTP 200, eliminując wyścig startowy zakończony Connection refused;
- focused suite: 123 passed; compileall i qmllint: PASS.

## 2026-10-06 — finalny gate po korekcie runtime

- zaktualizowano regresje TranslateGemma do aktualnego kontraktu `/v1/chat/completions` i `chat_template_kwargs`;
- usunięto nieużywany import `language_name_for` z adaptera llama.cpp;
- odbudowano wheel `tlumacz-0.40.0-py3-none-any.whl` po zmianach;
- pełny pytest: **340 passed**; Ruff, mypy i compileall: **PASS**;
- test zasobów wheel oraz 4 testy specjalnego trybu TranslateGemma: **5 passed**;
- rzeczywisty adapter Apertium nadal potwierdza `en→pl` i `en→es`.

## 2026-10-06 — Apertium: archiwizacja, cleanup i discovery pakietów

- zakończono i zweryfikowano pełne archiwum `/home/frs/.config/tlumacz/Apertium/` (`7z t`: `Everything is Ok`, SHA-256 `d4a90e56875a75b0f467e2a28b3c522d87637309b91aaa5c638411dd3f1732d`);
- usunięto z aktywnego magazynu użytkownika pakiety bez skompilowanych artefaktów; źródła pozostają zabezpieczone w archiwum;
- usunięto source-only katalogi z `Aperitium/` po wcześniejszym pełnym archiwum;
- `ApertiumRuntime.language_pairs()` scala teraz wynik CLI z discovery skompilowanych trybów w pakietach użytkownika;
- `data_dir_for_pair()` rozpoznaje, czy `.mode` korzysta z lokalnych ścieżek pakietu, czy z prefiksu katalogu pakietu;
- dodano regresje dla obu wariantów katalogu danych oraz rzeczywistego discovery;
- rzeczywisty adapter potwierdzono dla `en→pl` i `en→es`.

## Unreleased — 2026-10-06 — wybór języka Apertium

- discovery par korzysta wyłącznie z faktycznie skompilowanych trybów `compiled_modes`, więc deklaracja `modes.xml` bez wymaganych artefaktów nie trafia do GUI;
- dodano indeks logicznie dwukierunkowych par Apertium dla mechanizmu wyboru języka;
- cele Apertium są filtrowane zależnie od wybranego źródła, a niezgodny cel jest zerowany;
- brak pary jest prezentowany jako `brak pary` i blokuje selektor celu;
- automatyczne źródło dla tekstowych plików korzysta z istniejącego Lingua `LanguageDetector`;
- bridge korzysta z konfigurowalnego katalogu danych, domyślnie `$HOME/.config/tlumacz/Apertium/`;
- dodano regresje dla discovery, obu kierunków, braku pary, detekcji źródła, katalogu danych i kontraktu QML.
## 2026-10-06 — TranslateGemma: właściwy kontrakt llama.cpp

- zweryfikowano rzeczywisty translategemma-4b-it.Q5_K_M.gguf na izolowanym llama-server z llama.cpp b7976;
- potwierdzono działanie natywnego Jinja z GGUF;
- wykryto i odtworzono problem utraty source_lang_code/target_lang_code przy typed-content;
- adapter LlamaCppAdapter używa teraz chat_template_kwargs w /v1/chat/completions;
- runtime dla chat_template=translategemma uruchamia model przez --jinja, bez nieobsługiwanej nazwy --chat-template translategemma;
- focused regression tests: 3 passed.

## 2026-10-06 — archiwizacja i cleanup artefaktów

- temp/ i .migration-backups/ wyczyszczone;
- usunięto .mimocode/ jako lokalne środowisko @mimo-ai/plugin;
- usunięto src/tlumacz/qml_gui/help.pl.md.corrupt-20261005 jako zwielokrotniony artefakt 70 MiB;
- pełne źródła Aperitium/ zarchiwizowano do backups/Aperitium-sources-full-20261006.7z przed selektywnym odchudzaniem.

---
id: changelog-v4
status: active
meta:
  contentType: Changelog
  category: governance
version: 0.40.0
updated: 2026-10-06
owner: project-maintenance
source: root/CHANGELOG.md
depends_on: [docs/STATUS.md, docs/TODO.md]
expires_when: kolejna wersja wydania lub zmiana polityki changelogu
last_validation: "korelacja changelogu z aktualnym kodem SentinelX 2026-10-06"
---

## 2026-10-06 — kompilacja pozostałych par Apertium

- wymuszono przebudowę dostępnych źródeł par Apertium zamiast polegać wyłącznie na istniejących `.bin`;
- naprawiono `pol-rus` (`a_pprep` → `pprep`), `pl-sk` (brakujący `a_vrb`) i `pl-csb` (brakujący `a_det`);
- `make -B` zakończył się powodzeniem dla tych trzech naprawionych źródeł oraz pozostałych zweryfikowanych par;
- rzeczywiste smoke-testy potwierdziły kierunki `eng-cat`, `eng-deu`, `eng-ita`, `eng-spa`, `en-pt`, `pol-ces`, `pol-rus`, `pol-szl`, `pol-ukr`, `spa-pol`, `pl-csb`, `pl-sk`;
- `pl-csb` zachowuje dwa nierozstrzygnięte duplikaty `pardef` w słowniku;
- `pl-uk` pozostaje legacy source wymagającym `apertium-3.2` w `pkg-config`; nie instalowano brakującej zależności;
- utworzono backup źródeł przed kompilacją: `backups/apertium-pairs-before-compile-20261006-002349.tar.gz`.

## 2026-10-06 — kolejne wykonane pozycje planu naprawy V4

- usunięto 1-sekundowy polling `refreshSkills()` z `ExtrasPage.qml` i dodano test regresyjny;
- usunięto zbędne deklaracje `font.bold: false` z `ExtrasPage.qml`;
- ujednolicono bieżący opis bazowego fontu GUI z `Main.qml` (15 px);
- `uruchom-v4.sh` stał się relokowalny dzięki wyznaczaniu katalogu projektu z własnej lokalizacji;
- dodano lokalny `.gitignore`; lokalna granica Git V4 nie jest tworzona, ponieważ repozytorium synchronizowane z GitHubem znajduje się poza katalogiem V4;
- skorygowano indeks dokumentacji: `docs/BUILD.md` został dodany do `INDEX.yml`, a liczba kanonicznych plików wynosi 472;
- usunięto z runtime `openai`, `PyMuPDF` i `markdown-it-py` po potwierdzeniu braku użycia w aktywnym `src/tests`; clean-wheel metadata nie deklaruje już tych pakietów;
- rozpoczęto rzeczywisty audyt accessibility QML: 4 brakujące nazwy dostępnościowe zostały dodane, a testy keyboard-focus przechodzą;
- potwierdzono obecność rzeczywistych modeli TranslateGemma w `$HOME/Modele` i uruchomiono E2E na `translategemma-4b-it.Q5_K_M.gguf`;
- wycofano omyłkowe lokalne `git init` V4, ponieważ repozytorium synchronizowane z GitHubem znajduje się poza katalogiem V4; lokalny `.gitignore` pozostaje;
- Windows/macOS oznaczono jako przyszły etap, nie bieżący blocker.

## 2026-10-05 — uzupełnienie opisów Apertium, Mozhi Auto i Własnego

- `apertium.description.txt` rozszerzono o zasadę działania backendu regułowego, wymaganie konkretnej pary źródło → cel oraz ograniczenia wynikające z dostępności danych, zależności i licencji poszczególnych par;
- `cloud.mozhi_auto_info.txt` rozszerzono o faktyczny mechanizm równoległego sprawdzania instancji, weryfikacji silnika i języków, tłumaczenia kontrolnego, pomiaru czasu, wyboru najszybszej poprawnej instancji oraz fallbacku;
- `custom.description.txt` rozszerzono o instrukcję konfiguracji zewnętrznego serwera OpenAI-compatible oraz przykłady vLLM i zewnętrznego endpointu;
- treść oparto na aktualnym V4 oraz materiałach V3, bez traktowania historycznych lub nieaktywnych backendów jako aktualnej ścieżki GUI.

## 2026-10-05 — synchronizacja kontraktów testów i i18n

- zaktualizowano regresję QML do aktualnej karty **Pomoc**: dwa selektory ComboBox, język aplikacji i motyw; wybór języka docelowego nie jest duplikowany w Pomocy;
- zaktualizowano testy przełączania plików pomocy PL/EN/DE po zmianie tytułów tematów;
- rozdzielono klucz i18n `ui.user_skills` od `ui.user_skills_directory`, aby usunąć duplikat klucza w słownikach PL/EN/DE.

## 2026-10-05 — stan zweryfikowany względem aktualnego kodu

Najnowsze wpisy GUI są historią kolejnych zmian. Podczas korelacji wykryto, że część wcześniejszych wpisów dotyczących Apertium opisuje stan pośredni, który został później cofnięty. Aktualny `TranslationPage.qml` nadal trzyma pola językowe Apertium w tym samym `RowLayout` co przyciski sterowania i pokazuje je jako pola tylko do odczytu. Ten fakt jest opisany również w `docs/technical-docs/QML_GUI_LAYOUT.md`, `docs/technical-docs/QML_GUI_TRANSLATION_CARD_SPEC.md` i `docs/STATUS.md`.


## Unreleased — 2026-10-05

### GUI — niezależne akcje backendów po tłumaczeniu i informacja Mozhi
- **llama.cpp**: osobny checkbox restartu serwera;
- **Apertium**: osobny checkbox restartu usługi;
- **Chmura**: osobny checkbox ponownego połączenia z serwerem;
- ustawienia restartu/reconnectu są przechowywane niezależnie, a stara wspólna flaga jest migrowana przy odczycie konfiguracji;
- po wybraniu profilu **Mozhi** pod selectorami pojawia się informacyjne pole opisujące działanie trybu `auto`.

### GUI — wybór języków Apertium w zakładce Serwer
- zamieniono nieedytowalne pola tekstowe języka źródłowego i docelowego na kontrolki `ComboBox`;
- źródło korzysta z `bridge.apertiumSourceLanguages`, a cel z `bridge.targetLanguages`;
- wybór źródła i celu jest przekazywany do odpowiednich metod bridge.

### GUI — przypisanie ustawień zachowania do właściwego backendu
- usunięto checkboxy zachowania backendu z ogólnej karty **Przełączniki**;
- ustawienia **llama.cpp** są teraz widoczne w sekcji serwera llama.cpp;
- ustawienie restartu **Chmury** jest widoczne w sekcji serwera chmurowego;
- ustawienia czyszczenia cache i restartu **Apertium** są widoczne w sekcji lokalnego serwera Apertium;
- logika bridge i istniejące wartości ustawień pozostały bez zmian.
## Unreleased — 2026-10-05

### GUI — lokalizacja skilli
- dodano lokalizację nagłówków „Skille systemowe” i „Skille użytkownika”;
- dodano lokalizację komunikatu braku skilli użytkownika i podpowiedzi usuwania skilla w PL/EN/DE.

## Unreleased — 2026-10-05

### GUI — dalsza korekta pól Apertium
- przesunięto blok pól językowych o 40 px w lewo;
- w angielskiej lokalizacji etykiety zmieniono na „Lang in” i „Lang out”.

## Unreleased — 2026-10-05

### GUI — korekta pól językowych Apertium
- cofnięto aktywne listy wyboru języków na rzecz nieedytowalnych pól tekstowych;
- zwiększono odstęp między polami językowymi do 24 px;
- w karcie API i serwer zastosowano ten sam sposób prezentacji;
- w angielskiej lokalizacji etykiety używają „Input language” i „Output language”.

## Unreleased — 2026-10-05

### Apertium — aktywne pola wyboru języków
- zamieniono szare, nieaktywne pola Apertium w zakładce **API/Serwer** na aktywne ComboBox;
- język źródłowy jest budowany z kierunków wykrytych w /home/frs/.config/tlumacz/Apertium;
- język docelowy korzysta z tego samego bridge.targetLanguages i bridge.targetLanguage co zakładka **Tłumaczenie**;
- ten sam wybór języków jest dostępny w wierszu Apertium na karcie **Tłumaczenie**;
- dodano zapis wybranego języka źródłowego do settings-v4.json;
- pozostawiono jawny punkt podpięcia przyszłego detektora rozróżniającego pary jednokierunkowe i dwukierunkowe.

## Unreleased — 2026-10-05

### GUI — pełna szerokość przycisków wiersza sterowania
- zwiększono **Tłumacz** i **Anuluj** z 110 px do **130 px**, zgodnie z geometrią pełnego przycisku używaną w karcie;
- lewa pozycja przycisku **Tłumacz** pozostaje bez bocznego marginesu kontenera;
- zachowano 12 px odstępu wyłącznie pomiędzy polami **Język źródłowy** i **Język docelowy** oraz kompaktowanie pionowe 0/2;
- zaktualizowano regresję QML i dokumentację geometrii karty.

## 2026-10-05 — korekta końcowa wiersza sterowania karty Tłumaczenie

- usunięto boczne marginesy 24 px z całego wiersza sterowania;
- przycisk **Tłumacz** nie jest już przesuwany przez margines kontenera;
- przyciski **Tłumacz** i **Anuluj** pozostają w pełnej szerokości 110 px;
- dodano 12 px odstępu wyłącznie pomiędzy blokiem **Język źródłowy** i **Język docelowy**;
- zachowano kompaktowanie pionowe: 0 px marginesu pionowego i 2 px odstępu wiersza;
- zaktualizowano test regresyjny, dokumentację układu i specyfikację karty.

## Unreleased — 2026-10-05

### GUI — korekta końcowa wiersza sterowania
- zwiększono boczne marginesy wiersza **Tłumacz / Anuluj / języki** do 24 px, aby przyciski były w całości wewnątrz karty;
- wyzerowano pionowe marginesy tego wiersza i zmniejszono odstęp między elementami do 2 px;
- dodano test regresyjny wymuszający te ograniczenia geometrii.

## Unreleased — 2026-10-05

### GUI — karta „Tłumaczenie”
- pola ścieżek pliku wejściowego i wyjściowego stały się w pełni elastyczne: rozciągają się do stałego przycisku **Przeglądaj...** zamiast zatrzymywać się na 240 px;
- przyciski **Przeglądaj...** zachowują szerokość 110 px;
- wiersz **Tłumacz / Anuluj / język źródłowy / język docelowy** został wyrównany pionowo; przyciski są ustawione do dołu względem pól językowych i mają wspólną szerokość 110 px z polami językowymi;
- pola formularza otrzymały wspólną wysokość 36 px;
- zmniejszono pionowe odstępy karty do 2 px;
- **Log** i **Podgląd tłumaczenia** zwiększono do jednakowej preferowanej wysokości 220 px.
- dodano regresje QML dla elastycznej szerokości pól plików, wyrównania wiersza akcji oraz powiększenia Logu i Podglądu.

## Unreleased — 2026-10-05

### GUI
- przyciski **Przeglądaj...** zwiększono do 110 px i wyrównano do prawej krawędzi wierszy plików;
- dla Apertium przeniesiono wyłącznie opisane pola **Język źródłowy** i **Język docelowy** do tego samego wiersza co **Tłumacz** i **Anuluj**.

## Unreleased — 2026-10-05

### GUI
- **Pola plików w karcie Tłumaczenie** — skrócono wyłącznie pola pliku wejściowego i wyjściowego do preferowanej/maksymalnej szerokości 240 px; zachowano elastyczne `Layout.fillWidth` dla zwężania przy węższym oknie. Pozostałe elementy karty pozostają bez zmian.

- Karta „Tłumaczenie”: przyciski „Przeglądaj” mają szerokość 96 px, a pola ścieżek zwalniają miejsce tak, aby pełny napis przycisku był widoczny.
## 2026-10-05 — naprawa rzeczywistej struktury GUI Apertium

- potwierdzono root cause rozbieżności: bieżący TranslationPage.qml miał pola Apertium nadal zagnieżdżone w RowLayout sterowania, mimo wcześniejszego opisu dokumentacyjnego;
- wydzielono apertiumLanguageSection poza wiersz przycisków;
- zastosowano rzeczywisty GridLayout z dwiema kolumnami;
- wzmocniono test regresyjny tak, aby sprawdzał strukturę kontenerów, a nie tylko obecność dwóch kolumn;
- wykonano backup przed naprawą: backups/gui-root-cause-20261005/pre-gui-root-cause-fix.tar.gz;
- qmllint dla Main.qml i TranslationPage.qml: PASS;
- test regresyjny struktury Apertium: PASS.

## 2026-10-05 — uruchamianie V4

- dodano `uruchom-v4.sh` jako jednoznaczny launcher źródłowego GUI QML V4;
- launcher ustawia `PYTHONPATH` na katalog `src` i uruchamia `tlumacz.qml_gui.app`;
- launcher ustawia `QML_DISABLE_DISK_CACHE=1`, aby developerskie uruchomienie korzystało bezpośrednio z aktualnych plików QML;
- dodano test kontraktu launchera.

## 2026-10-05 — pełna szerokość przycisków sterowania

- przyciski Tłumacz i Anuluj mają stałą szerokość 110 px i nie mogą zostać ściśnięte przez Layout;
- zaktualizowano kontrakt testowy i dokumentację układu QML.

## 2026-10-05 — zagęszczenie pionowe karty Tłumaczenie

- pasek postępu oraz statystyki czasu i prędkości przeniesiono nad przyciski sterowania;
- zmniejszono odstępy pionowe w górnej części karty;
- zwiększono wysokość pól Log i Podgląd tłumaczenia do 180 px;
- zaktualizowano test kontraktu układu oraz dokumentację QML.

## [Unreleased] — 2026-10-05 — korekta układu Apertium
- Start, Anuluj oraz pola Język wejściowy/Język docelowy ustawiono w jednym wierszu; etykiety są nad polami, a pola mają 120 px szerokości.

## [Unreleased] — 2026-10-05

### GUI
- **TranslationPage / Apertium:** skrócono przyciski „Przeglądaj...” do 80 px, wymuszono elastyczne pola ścieżek oraz zmniejszono Log i Podgląd do jednakowej wysokości 120 px. Układ języków Apertium pozostaje dwukolumnowy z nieedytowalnymi polami wyświetlającymi wybrane języki.

## 2026-10-05 — korekta karty Tłumaczenie dla Apertium

- przyciski **Przeglądaj...** w sekcji plików mają szerokość 90 px, aby oba były widoczne w szerokości okna;
- etykiety pól Apertium zmieniono na **Język źródłowy** i **Język docelowy** z pełną lokalizacją PL/EN/DE;
- pola językowe pozostają nieedytowalne i prezentują tylko wybrane języki;
- wysokość **Log** i **Podglądu tłumaczenia** zmniejszono do wspólnych 140 px;
- dodano testy regresyjne dla szerokości przycisków i geometrii pól.

## 2026-10-05

### Poprawki GUI / konfiguracji
- wybór backendu z karty **API i serwer** jest teraz zapisywany natychmiast po zmianie;
- dodano test regresyjny potwierdzający zapis `llama → apertium` do konfiguracji;
- dodano test runtime potwierdzający, że zmiana `backendType` aktualizuje zależną widoczność QML bez restartu.

## 2026-10-04 — korekta struktury kontrolek Apertium w karcie Tłumaczenie

- wyjęto blok **Język źródłowy / Język docelowy** z `RowLayout` przycisków sterowania;
- blok języków jest teraz osobnym wierszem i wykorzystuje pełną szerokość karty w dwóch równorzędnych kolumnach;
- dodano regresyjny test struktury QML, aby zagnieżdżenie bloku języków w wierszu przycisków nie wróciło.

## 2026-10-04 — korekta kontrolek językowych oraz wysokości Log/Podgląd

- na głównej karcie **Tłumaczenie**, dla Apertium, język źródłowy i docelowy są ustawione w dwóch kolumnach;
- etykiety znajdują się nad odpowiednimi kontrolkami, bez dodatkowego wiersza;
- kontrolki wykorzystują dostępną szerokość swoich kolumn;
- **Log** i **Podgląd tłumaczenia** mają jednakową preferowaną wysokość: 180 px;
- dodano testy regresji dla obu zmian.
## 2026-10-04 — unieważnienie cache QML po edycji GUI

- potwierdzono rozbieżność między aktualnym `ApiPage.qml` na dysku a starym układem widocznym w działającej instancji;
- przyczyną był zachowany przez mechanizm edycji stary znacznik `mtime` plików QML, co mogło pozwolić Qt wykorzystać wcześniejszy cache skompilowanego QML;
- odświeżono `mtime` aktywnych plików `Main.qml`, `ApiPage.qml`, `ExtrasPage.qml`, `TranslationPage.qml` i `HelpPage.qml`;
- przy kolejnym uruchomieniu Qt powinien wykryć pliki jako nowsze i odrzucić nieaktualny cache.

## 2026-10-04 — korekta nagłówka karty „API i serwer”

- główny nagłówek wewnątrz `ApiPage.qml` korzysta teraz z klucza `tab.api_server`, dzięki czemu jest spójny z nazwą zakładki: **API i serwer**;
- usunięto źródło rozbieżności, w którym nagłówek wyświetlał **Ustawienia API**;
- nie zmieniano geometrii `ExtrasPage`: zmierzona wysokość 837 px wynika z rzeczywistych wysokości trzech sekcji i nie była przyczyną problemu;
- test regresji oraz `qmllint` dla `ApiPage.qml` przechodzą.

## 2026-10-04 — wznowienie konfiguracji GUI Apertium

Na podstawie docs/Audyt/CHECKPOINT_GUI_2026-10-04.md wznowiono pracę nad GUI bez odtwarzania jeszcze brakujących funkcji backendowych:
- karta API i serwer otrzymała docelowy układ Apertium: Ustawienia API, Język źródłowy, Język docelowy oraz Apertium — serwer lokalny;
- usunięto drugi wybór serwera z powierzchni Apertium;
- dodano sekcję Uwagi z opisem Apertium;
- na stronie tłumaczenia wybór języka docelowego jest zastępowany dla Apertium informacją o źródle i celu;
- na karcie Przełączniki sekcja Ustawienia LLM znika po wybraniu Apertium, pozostawiając akcje zapisu i przywracania;
- dynamiczne wyznaczanie par językowych i właściwa detekcja pozostają do późniejszego podłączenia zgodnie z planem naprawy funkcji;
- testy: 272 passed; qmllint zmienionych kart: PASS.

## 2026-10-04 — zapis konfiguracji bieżącej GUI

Utrwalono aktualny stan interfejsu po zakończeniu serii korekt:
- karta **API i serwer**: nagłówek **Serwer llama.cpp — lokalny** i wybór **Szablon czatu**;
- karta **Przełączniki**: kolejność **Glosariusz → Umiejętności → Ustawienia LLM**;
- przyciski glosariusza: **Przeglądaj...** i **Dodaj** po 120 px;
- przyciski obsługi skilli: po 180 px;
- Rozmiar bloku i Temperatura: po 120 px;
- ikony aplikacji zależne od motywu: tlumacz-dark.svg / tlumacz-light.svg;
- weryfikacja: **276 passed**.

## 2026-10-04 — korekta układu glosariusza

- przyciski **Przeglądaj...** i **Dodaj** mają teraz identyczną szerokość 120 px;
- pola glosariusza automatycznie wykorzystują pozostałą szerokość wiersza.

## 2026-10-04 — ikony aplikacji

- dodano obsługę dwóch ikon aplikacji zależnych od motywu: **tlumacz-dark.svg** i **tlumacz-light.svg**;
- ikona aktualizuje się po zmianie motywu aplikacji oraz przy zmianie motywu systemowego.

## 2026-10-04 — nagłówek sekcji llama.cpp

- dodano pod separatorem pogrubiony tytuł **Serwer llama.cpp — lokalny** przed kontrolkami serwera.

## 2026-10-04 — korekta karty „API i serwer”

- w sekcji llama.cpp pole **Temperatura** zastąpiono wyborem **Szablon czatu**;
- wybór jest podłączony do istniejącego bridge.setChatTemplate() i korzysta z bridge.chatTemplates;
- dostępne warianty: **jinja**, **chatml**, **TranslateGemma**.

## 2026-10-03 — Korekta karty „Przełączniki”\n\n- przywrócono kolejność sekcji **Glosariusz → Umiejętności → Ustawienia LLM**;\n- usunięto sztuczne prawe marginesy skracające pola **Glosariusz**;\n- ustabilizowano kolumny przycisków: **Przeglądaj 100 px**, **Dodaj 72 px**;\n- zmniejszono przyciski akcji skilli do **180 px**;\n- ujednolicono **Rozmiar bloku** i **Temperaturę** do **120 px**.\n\n## 2026-10-03 — Uporządkowanie drzewa źródłowego V4

- usunięto repozytoryjny symlink `tlumacz -> src/tlumacz` z katalogu głównego;
- jedynym źródłem pakietu pozostaje `src/tlumacz/`, zgodnie z konfiguracją `setuptools`;
- uruchamianie ze źródeł wymaga jawnego `PYTHONPATH=src`;
- zaktualizowano test bootstrapu oraz dokumentację architektury i uruchamiania;
- kopię usuniętego symlinku zachowano w `backups/cleanup-20261003-structure/`.

## 2026-10-03 — Korekta układu zakładki „Przełączniki"

- przeniesiono sekcję przełączników/checkboxów skilli na początek karty, przed glosariusz;
- zachowano separator między głównymi sekcjami oraz wcześniejsze korekty geometrii kontrolek;
- dodano test wymuszający kolejność sekcji;
- weryfikacja: `44 passed`, `qmllint src/tlumacz/qml_gui/ExtrasPage.qml` bez błędów.


## GUI QML — korekta karty „Przełączniki” — 2026-10-03

- zwiększono szerokość przycisku **Przeglądaj** glosariusza do 112 px;
- skrócono pola **Źródło** i **Tłumaczenie** przez zwiększenie ich prawego marginesu;
- zwiększono szerokość **Rozmiaru bloku** do 152 px i wyrównano do niej **Temperaturę**;
- wymuszono regularną wagę fontu na karcie, pozostawiając pogrubienie wyłącznie nagłówkom sekcji;
- dodano separator nad **Ustawieniami LLM**;
- zaktualizowano testy kontraktowe i potwierdzono `43 passed` oraz `qmllint` PASS.

## Zmiana katalogu projektu V4 i czyszczenie plików tymczasowych — 2026-10-01

- Oficjalny katalog projektu V4 zmieniono na `/home/frs/Projekty/tlumacz-v4/`.
- W tym drzewie wykonano rekurencyjny przegląd wszystkich 970 katalogów.
- Przed czyszczeniem znaleziono 513 plików `*.bak*` o łącznym rozmiarze około 2,9 MiB.
- Usunięto wyłącznie pliki `*.bak*`; nie usuwano innych plików ani katalogów.
- Po końcowym czyszczeniu liczba plików `*.bak*` wynosi 0.
- Stary katalog `/home/frs/Projekty/agent-translator-v3/` nie był czyszczony ani modyfikowany.


## GUI QML — uzupełnienie powierzchni Tłumaczenie i Dodatki — 2026-10-02

- Rozszerzono izolowany prototyp Qt Quick/QML o pomiar czasu tłumaczenia, bieżącą i średnią prędkość znaków/s oraz podgląd tłumaczenia.
- Usunięto zbędny element UI automatycznego źródła.
- Dodano listę skilli systemowych i użytkownika z przełączaniem oraz przyciski Odśwież, Importuj skilla i Nowy skill.
- Dodano Rozmiar bloku, Temperaturę, Własny prompt i Pomijane linie (regex).
- Zmiana nie integruje jeszcze tych kontrolek z backendem; pozostają częścią izolowanego prototypu QML.


## 2026-10-02 — migracja głównego GUI do Qt Quick/QML

- Podłączono GUI QML do `TranslationApp` przez `QmlApplicationBridge`.
- Przełączono główny skrypt `tlumacz` na launcher QML.
- Usunięto klasyczne GUI Qt Widgets z `src/tlumacz/qt_gui/`.
- Dodano rzeczywistą obsługę backendu `custom` oraz package-data dla plików QML.
- Pełna regresja projektu po migracji: **230 testów zakończonych powodzeniem**; compileall i Ruff PASS.

## 2026-10-02 — pierwsza korekta aktywnego GUI QML

- usunięto wewnętrzny nagłówek „Tłumacz” oraz „V4 · Qt Quick”;
- odblokowano zmianę rozmiaru okna i dodano pamiętanie pozycji/rozmiaru;
- czas tłumaczenia jest prezentowany jako MM:SS;
- „Dodatki” zmieniono na „Parametry”;
- język aplikacji pokazuje pełne nazwy języków;
- skille pokazują katalogi źródłowe zamiast checkboxów;
- usunięto drugi wybór języka z Pomocy;
- Pomoc i „O programie” pokazują wersję 0.4.0 i właściwą treść pomocy;
- karta API i serwer została pozostawiona do osobnego omówienia geometrii i zachowania.


## 2026-10-03 — lokalizacja GUI QML i pomocy

- domknięto lokalizację aktywnej powierzchni QML w PL/EN/DE;
- zlokalizowano dialogi plików, backendy, glosariusz, ustawienia i komunikaty runtime;
- ujednolicono pomoc użytkownika PL/EN/DE;
- dodano docs/I18N_STATUS.md jako rejestr stanu lokalizacji;
- pełna regresja: 272 passed, compileall PASS, smoke QML offscreen zakończony kontrolowanym kodem 124.


### 2026-10-04

- Korekta GUI Apertium: usunięto duplikację nagłówka „Ustawienia API”, zwężono nieaktywne listy języków i przeniesiono selektor serwera bezpośrednio pod nimi.
- Widok tłumaczenia Apertium pokazuje źródło i cel w nieedytowalnych polach tekstowych w układzie „Język - Źródłowy / Docelowy”.
- Dodano klucze lokalizacyjne dla nowych etykiet.


## 2026-10-05 — typografia karty Tłumaczenie

- zmniejszono bazową czcionkę GUI z 18 px do 17 px;
- tytuły bloków Pliki, Log i Podgląd tłumaczenia zachowują wyróżnienie zgodnie z układem karty.


## Unreleased — 2026-10-05 — karta Pomoc
### GUI
- usunięto z Pomocy duplikat wyboru języka docelowego;
- skrócono pola wyboru języka programu i motywu;
- skompaktowano zakładki tematów Pomocy i wymuszono czytelne łamanie ich nazw do dwóch linii;
- obszar treści Pomocy zachowuje całą dostępną przestrzeń.

- pole wyboru motywu w karcie Pomoc automatycznie dopasowuje szerokość do napisu.

- naprawiono faktyczne przełączanie palety aplikacji po zmianie motywu.

- poprawiono skalowanie pola Motyw: szerokość jest wyliczana na podstawie rzeczywistego wymiaru aktualnego napisu przez `TextMetrics`, z miejscem na elementy ComboBox; zapobiega to obcinaniu dłuższych nazw, szczególnie w English i Deutsch;
- umieszczono logo FRS Systems w prawym górnym obszarze wyskakującego okna „O Programie”; logo nie jest już wyświetlane w głównym oknie.

- poprawiono obsługę wyboru serwera dla PL/EN/DE: GUI przekazuje stabilny identyfikator backendu zamiast przetłumaczonej nazwy;
- tryby Ciemny i Jasny obejmują również własne panele i zaznaczenia zakładek, które wcześniej zawierały stałe jasne kolory.


## 2026-10-05 — skille, przełączniki backendu i kompaktowanie QML

- przywrócono automatyczny wybór skilla po rozszerzeniu ładowanego pliku; pozostałe skille są odznaczane;
- dodano trwałe przechowywanie aktywnych skilli w `AppSettings`;
- dodano do karty „Przełączniki” checkboxy zachowania dla llama.cpp, Chmury i Apertium;
- zmniejszono typografię i odstępy głównych kart QML, aby interfejs był bardziej zwarty i smukły;
- dodano testy regresyjne dla automatycznego wyboru skilla, trwałości skilli i checkboxów backendu;
- dokumentacja QML została uzupełniona.


## 2026-10-05 — testy packaging i lifecycle

- Dodano rzeczywistą weryfikację wheel: build, inspekcja zawartości, instalacja do tymczasowego targetu i import probe.
- Dodano TranslationApp.close() zamykające runtime llama.cpp i SQLite TranslationCache.
- Podpięto QGuiApplication.aboutToQuit do centralnego lifecycle rdzenia.
- Dodano pełny test GUI shutdown obejmujący Qt, SQLite i kontrolowany rzeczywisty LlamaCppRuntimeManager.
- Dodano test release smoke bundlowanego Apertium; test wykrywa obecny brak par językowych.
- Zaktualizowano test QML do aktualnego kontraktu restartLlamaAfterTranslation.


## 2026-10-05 — korekta układu zachowania backendów w GUI

- nagłówek Zachowanie backendu jest nad polem informacyjnym Apertium i Mozhi;
- pola tekstowe wykorzystują wolną wysokość sekcji;
- checkboxy są wyrównane do lewej i znajdują się na dole sekcji;
- dla llama.cpp checkboxy są nad przyciskiem Restart serwera, który pozostaje ostatnim elementem zakładki.


## 2026-10-05 — poprawka blokady ładowania ApiPage.qml

- usunięto zduplikowaną właściwość `Layout.alignment` w checkboxie Apertium;
- dodano test regresyjny zapobiegający ponownemu wystąpieniu duplikatu;
- potwierdzono poprawne ładowanie aplikacji V4 w trybie offscreen.


## 2026-10-05 — korekta pionowego układu zakładki API i serwer

- sekcje llama.cpp, Apertium, Cloud i własna rozciągają się tylko, gdy są widoczne;
- pole mozhiAutoInfo rozciąga się tylko dla profilu Mozhi;
- usunięto źródło pustych przestrzeni powodowanych przez Layout.fillHeight ukrytych elementów; checkboxy pozostają na dole właściwej sekcji.


## 2026-10-05 — zewnętrzne pliki długich treści GUI

- wydzielono długie statyczne treści pól informacyjnych Apertium, Mozhi i Własnego z kodu QML/Python do plików UTF-8;
- dodano osobne wersje PL/EN/DE w `src/tlumacz/qml_gui/texts/<język>/`;
- opis w oknie „O programie” również jest ładowany z pliku tekstowego;
- dodano ładowanie długich treści przez `QmlApplicationBridge.long_text()` oraz testy regresyjne;
- dodano pliki tekstowe do danych pakietu wheel.

## Unreleased — 2026-10-06 — informacyjne języki Apertium

- pola informacyjne źródła i celu na stronie tłumaczenia korzystają z `apertiumSourceLanguageLabel` i `apertiumTargetLanguageLabel`;
- widoczność tych pól nadal jest ograniczona do backendu Apertium;
- mechanizmy wyboru języków pozostałych backendów nie zostały zmienione;
- dodano regresje QML potwierdzające separację kontraktów.
- 2026-10-06: Zainstalowano skompilowaną parę Apertium `eng-pol` w docelowym katalogu użytkownika; poprawiono bazowy katalog runtime dla pakietów językowych i zweryfikowano tłumaczenie `Hello world.` → `@hello #Świat.`.



### 2026-10-06 — naprawa automatycznej detekcji źródła Apertium

- Detekcja dokumentu w GUI pozostaje realizowana przez Lingua.
- Automatycznie wykryty język nie jest już zapisywany jako trwały source_language.
- Apertium wraca do auto przy ładowaniu ustawień, dzięki czemu wcześniejsze spa/en/inne źródło nie blokuje detekcji kolejnego dokumentu.
- Dodano regresję dla dokumentu wielojęzycznego English → French → German: dokument ma zostać rozpoznany jako en, a fr i de mają być pomijane przez zamrożony routing Apertium.


## 2026-10-06 — ponowna walidacja Planu 03

- ponowiono audyt regresji P1/P2 na aktualnym V4;
- focused suite: 128 passed;
- pełny pytest: 367 passed, 0 failed;
- compileall i qmllint: PASS;
- nie potwierdzono nowej regresji produkcyjnej ani potrzeby zmiany kodu;
- odnotowano pojedynczy niestabilny wynik testu TranslateGemma, który nie powtórzył się w izolowanym teście ani w kolejnym pełnym suite.

## 2026-10-06 — restart llama.cpp

- `Restartuj serwer` dla llama.cpp uruchamia serwer także wtedy, gdy nie był wcześniej uruchomiony.
- Dodano test regresyjny dla tego zachowania.

## 2026-10-06 — Plan 04 / ponowny quality gate

- usunięto błędy Ruff w routingu języka i testach QML;
- doprecyzowano typowanie `TranslationOrchestrator` i `TranslationApp`;
- pełny pytest: **369 passed**;
- Ruff, mypy, compileall i qmllint: **PASS**;
- backupy zmian zapisano w katalogach `backups/plan-04-20261006-lint-fix/` i `backups/plan-04-20261006-type-fix/`.

## 2026-10-06 — korekta pobierania parametrów llama.cpp

- potwierdzono rozdzielenie parametrów GUI i technicznego llama.json;
- GUI nadal steruje hostem, portem, GGUF, CPU/GPU, parallel, szablonem czatu i rozmiarem bloku;
- $HOME/.config/tlumacz/llama.json nadal steruje tuningiem llama.cpp;
- naprawiono brak rzeczywistego rozstrzygania threads=auto i threads_batch=auto;
- dodano regresję TDD dla mapowania reguł sprzętowych na argumenty llama-server.

## 2026-10-06 — źródło ścieżki GGUF

- potwierdzono, że ścieżkę GGUF wybiera GUI;
- ścieżka GGUF jest utrwalana w $HOME/.config/tlumacz/config.json;
- usunięto odpowiedzialność llama.json za ścieżkę modelu;
- dodano test potwierdzający rozdzielenie konfiguracji.


## 2026-10-06 — walidacja zależności filtrów

Dodano walidację dependencies z filter.json, sprawdzanie obecności wymaganych JAR-ów i klas oraz status usable=False dla pakietów z brakami. GUI zapisuje brak zależności do Logu i pokazuje modalny komunikat z klikalnymi odnośnikami. QFileSystemWatcher wykrywa również nowe pakiety dodane do magazynu podczas pracy aplikacji.

OpenXML deklaruje wymaganie TwelveMonkeys Common IO dla klas OLE2. Zależności nie pobierano ani nie instalowano automatycznie.


### 2026-10-06 — naprawa ładowania GUI QML
- Naprawiono `Main.qml`, w którym dwa wpisy `Component.onCompleted` powodowały błąd `Property value set multiple times` podczas tworzenia `QQmlApplicationEngine`.
- Zachowano oba zachowania startowe w jednym handlerze: odtwarzanie geometrii okna i uruchomienie kolejki ostrzeżeń zależności filtrów.
- Dodano test regresyjny dla pojedynczego handlera `Component.onCompleted`.


### 2026-10-06 — naprawa ładowania GUI QML
- Naprawiono `Main.qml`, w którym dwa wpisy `Component.onCompleted` powodowały błąd `Property value set multiple times` podczas tworzenia `QQmlApplicationEngine`.
- Zachowano oba zachowania startowe w jednym handlerze: odtwarzanie geometrii okna i uruchomienie kolejki ostrzeżeń zależności filtrów.
- Dodano test regresyjny dla pojedynczego handlera `Component.onCompleted`.


### 2026-10-06 — wskaźnik aktywnej pracy tłumaczenia
- Dodano obracającą się kulkę na początku wiersza z licznikiem czasu w GUI.
- Wskaźnik jest związany z istniejącym `bridge.isTranslating` i nie zmienia logiki tłumaczenia ani kontrolek.
- Dodano regresję QML sprawdzającą położenie wskaźnika i aktywację animacji.

### TPlugin / Filter Engine — 2026-10-06

- Dodano specyfikację formatu .tplugin oraz trzy grupy zależności: bundled przy filtrze, shared deduplikowane podczas instalacji oraz zależności wspólne dla całego Filter Engine.
- Dodano produkcyjną metodologię budowy pluginów Okapi oraz plan wdrożenia TPlugin.
- Dodano kontrakt manifestu, builder, bezpieczny instalator i centralny magazyn shared-libs.
- Java FilterHost obsługuje układ pluginu z lib/ oraz centralnym shared-libs.
- Dodano testy deduplikacji, konfliktów checksum, path traversal i ładowania rzeczywistego OpenXML z TwelveMonkeys.
- Pierwsza migracja OpenXML została zweryfikowana w izolowanym profilu testowym.


## 2026-10-06 — TODO-022j: domknięcie migracji pakietów filtrów Okapi

- zastąpiono wszystkie przejściowe symlinki JAR w `filters/` fizycznymi kopiami;
- przeniesiono zależności `runtime-abstractmarkup`, `runtime-archive`, `runtime-generated-parser-compat` i `runtime-lib-xliff2` do pakietów filtrów, które ich używają; dodatkowo `common-io-3.12.0.jar` i `common-lang-3.12.0.jar` zostały przeniesione do `filters/openxml/`, ponieważ analiza `jdeps` wykazała ich użycie wyłącznie przez OpenXML/TwelveMonkeys;
- usunięto te cztery JAR-y z `src/tlumacz/resources/okapi-runtime/`;
- dodano testy izolacji pakietów i czystości wspólnego runtime;
- zakres migracji: **16 passed** dla dynamicznego loadera, walidacji zależności, separacji runtime, packagingu zasobów i nowych testów 022j;
- pełny suite po zmianie: **413 passed, 2 failed**; oba failure są znanymi, niezależnymi problemami Apertium/QML opisanymi w `docs/TODO.md`;
- TODO-022j zamknięte. TODO-022d/022e pozostają niezależnymi etapami docelowego magazynu użytkownika i loadera pakietów.

- Rozszerzono walidację zależności o centralne shared-libs, w tym wyszukiwanie wymaganych klas Java w bibliotekach współdzielonych.
- OpenXML został zainstalowany w /home/frs/.config/tlumacz/filter-engine/plugins/openxml; FilterHost smoke dla capabilities zakończył się poprawnie.
### 2026-10-06 — wskaźnik pracy QML
- Naprawiono animację kulki wskaźnika tłumaczenia przez zmianę na `NumberAnimation on rotation`.
- Zwiększono rozmiar wskaźnika 2×: 12×12 → 24×24 px.


## 2026-10-06 — reaktywność tematów Pomocy QML

- naprawiono `HelpPage.qml`, w którym model `Repeater` oparty na tablicy tytułów mógł zachować wcześniejsze, niemieckie etykiety po zmianie języka na polski;
- wprowadzono stały model pięciu zakładek oraz reaktywną właściwość `helpTabs.helpTopicTitles`;
- dodano test regresyjny dla kontraktu QML;
- zweryfikowano `qmllint` oraz ładowanie `HelpPage.qml` w trybie offscreen.

### 2026-10-06 — anulowanie llama.cpp
- Naprawiono brak natychmiastowego przerwania aktywnej generacji llama.cpp.
- Anulowanie zatrzymuje należący do aplikacji proces backendu i rozłącza blokujące żądanie HTTP.
- Anulowanie jest raportowane jako stan anulowania, a nie jako błąd backendu.

### Weryfikacja końcowa migracji
- 26 ukierunkowanych testów TPlugin/Registry/FilterHost/build/integration — PASS.
- 9/9 formatów przeszło rzeczywisty extract/merge round-trip na zainstalowanym runtime.
- katalog publikacyjny dist/tplugins/ zawiera 9 nierozpakowanych paczek i SHA256SUMS.


### TPlugin — zarządzanie zależnościami — 2026-10-06

- Dodano rejestr referencji shared-libs/index.json.
- Wdrożono współistnienie wielu wersji shared-libs i konflikt tej samej wersji przy różnym SHA-256.
- Uninstall usuwa referencję, ale nie usuwa biblioteki; GC działa wyłącznie dla artefaktów bez referencji.
- Dodano odbudowę indeksu referencji z aktywnych pluginów.
- Builder generuje inventory.json oraz checksums.json.
- Dodano tools/tplugin/dependencies.py z inventory, validate, rebuild i gc.
- Walidacja 9/9 paczek i testy TPlugin 16/16.


### TPlugin — backend administracyjny i ręczne paczki — 2026-10-06

- Dodano tools/tplugin_admin/ jako niezależny backend do przygotowywania paczek.
- Dodano CLI: init, validate, build, verify, inspect.
- Dodano tplugin-project.json jako administracyjny opis projektu.
- Dodano osobną instrukcję ręcznego tworzenia .tplugin.
- Testy backendu: 8 passed.

## 2026-10-06 — TPlugin: domknięcie backendu administracyjnego

- dodano automatyczny `test-install` z użyciem produkcyjnego instalatora TPlugin w izolowanym, tymczasowym runtime;
- dodano `publish` oraz maszynowo czytelny raport `*.publication.json` zawierający SHA-256 artefaktu i wynik kontroli instalacyjnej;
- rozszerzono testy backendu administracyjnego do **11 przypadków**;
- zamknięto `TODO-TPLUGIN-004`;
- backup: `backups/tplugin-admin-20261006/pre-admin-completion.tar.gz`.
## 2026-10-06 — Security/Lifecycle: SecretStore i centralny shutdown

- Rozszerzono migrację legacy sekretów: wszystkie profile Cloud są przenoszone do SecretStore, zanim bridge zacznie normalnie korzystać z ustawień.
- Po migracji legacy pola `api_key` i `last_local_api_key` są zerowane w stanie ustawień.
- Zapis ustawień przez GUI nie utrwala sekretów w `settings-v4.json`.
- `TranslationApp.close()` zawsze próbuje zamknąć TranslationCache, nawet jeśli zatrzymanie llama.cpp zgłosi wyjątek.
- `TranslationApp.stop_llama()` nie usuwa referencji do runtime, jeśli proces nadal działa po odmowie shutdown z powodu niezgodnej tożsamości procesu.
- Dodano regresje TDD dla sekretów i lifecycle.
- Backup: `backups/SECURITY-LIFECYCLE-PHASE1-2026-10-06.tar.gz`.

## 2026-10-06 — korekty funkcjonalne QML GUI

- Przywrócono systemowe skille `plaintext.md` (TXT) i `pdf.md` (PDF) oraz automatyczny dobór po rozszerzeniu pliku.
- Przyciski „Przywróć domyślne” i „Zapisz ustawienia” są wspólne dla karty Przełączniki, na dole i wyrównane do lewej.
- Własny serwer otrzymał osobne, domyślnie puste pole URL z trwałym zapamiętaniem ostatniej wartości.
- Przełączenie z llama.cpp zatrzymuje serwer i loguje informację; powrót do llama.cpp oczekuje na ręczny restart.
- Po starcie llama.cpp GUI sprawdza `/health` i odświeża adres z aktywnego runtime; port jest przekazywany jawnie do startu serwera.
- Pole klucza Cloud jest wyłączane dla profili niewymagających klucza; Mozhi pokazuje instancję wybraną jawnie albo efektywną instancję trybu `auto`.
- Dodano osobny sygnał `themeChanged`, tooltipy opisowe kart Pomocy oraz zwiększono Log/Podgląd do 300 px.

## 2026-10-06 — Security/Lifecycle: SQLite cleanup gate

- Dodano awaryjny finalizer TranslationCache.__del__ jako zabezpieczenie przed pozostawieniem połączenia SQLite poza normalnym lifecycle.
- Normalny shutdown nadal odbywa się przez TranslationApp.close() → TranslationCache.close().
- Focused suite z -W error::ResourceWarning: **32 passed**.

## 2026-10-07 — Unifikacja konfiguracji GUI

- Ujednolicono trwałe ustawienia GUI: jedynym plikiem ustawień użytkownika jest `$HOME/.config/tlumacz/config.json`.
- Usunięto z bieżącego przepływu `settings-v4.json`; kod GUI nie używa go już jako źródła ani celu zapisu.
- Scalono aktualny stan GUI z `settings-v4.json` do `config.json`, zachowując istniejące klucze konfiguracyjne.
- `AppSettings`, `load_settings()` i `save_settings()` korzystają bezpośrednio z `config.json`; ścieżka GGUF i pozostałe ustawienia są zapisywane w tym samym pliku.
- Wykonano backup kodu i konfiguracji przed migracją.

## 2026-10-07 — korekta QML GUI po ponownej weryfikacji

- Przyciski **Przywróć domyślne** i **Zapisz ustawienia** przeniesiono poza `ScrollView` do stopki karty Przełączniki.
- Naprawiono wybór **TranslateGemma** przez zgodność wartości prezentacyjnej ComboBox z `bridge.chatTemplate`.
- Naprawiono tooltipy zakładek Pomocy przez włączenie hover dla `MouseArea`.
- Naprawiono reaktywność motywu przez jawne bindingi palety `ApplicationWindow` do `bridge.theme`.

## 2026-10-07 — doprecyzowanie unifikacji konfiguracji i walidacji

- Potwierdzono jeden kanoniczny plik ustawień GUI: `$HOME/.config/tlumacz/config.json`.
- `settings-v4.json` pozostaje wyłącznie artefaktem historycznym/backupowym i nie może wrócić do aktywnego przepływu.
- `llama.json` pozostaje osobnym plikiem tuningu technicznego llama.cpp, a nie drugim plikiem ustawień GUI.
- Ukierunkowane testy konfiguracji i GUI: **41 passed**.
- Pełny suite nie został oznaczony jako zielony: jedna próba zakończyła się fatalnym `Aborted` Qt/PySide6 podczas raportowania wcześniejszych failure'ów. W stack trace wystąpiły wątki Filter Engine. Wymaga to osobnego domknięcia diagnostycznego.


## 2026-10-07 — poprawki llama.cpp / TranslateGemma / Markdown

- Automatyczny start zarządzanego llama.cpp po przełączeniu backendu na `llama`, zgodnie z `auto_start_server` zapisanym w kanonicznym `config.json`.
- Naprawiono prezentację/wybór `TranslateGemma` w QML: wartość wewnętrzna `translategemma` jest poprawnie mapowana na wartość widoczną w ComboBox.
- Filtr Markdown zachowuje znaczniki blokowe podczas zapisu, nie wysyła separatorów Markdown ani fenced code do backendu oraz dodano testy regresyjne.
- Potwierdzono timeout llama.cpp na poziomie 300 s w selekcji GUI i adapterze.
- Pełna walidacja QML nadal jest ograniczona przez istniejący crash PySide6/pytest podczas raportowania failure; ukierunkowane testy nowych zmian przechodzą: **2 passed**.


## 2026-10-07 — ponowna naprawa timeoutu llama.cpp

- Zwiększono timeout żądania TranslateGemma/llama.cpp z 300 s do 1800 s oraz timeout startu modelu z 60 s do 300 s.
- Dodano rozpoznawanie stanu HTTP 503 `Loading model`.
- Diagnostyka potwierdziła, że bieżący bundled runtime działa wyłącznie CPU; problem wynika z czasu inferencji, a nie z niedostępności endpointu.
- Dokumentacja odnotowuje również obecność dodatkowych procesów llama.cpp na portach 2782 i 18818.

## 2026-10-07 — rzeczywista korekta widoku Pomoc i przełączania motywu

- Zweryfikowano runtime QML zamiast opierać się wyłącznie na testach źródłowych: aktualne delegaty zakładek Pomocy tworzą rzeczywiste teksty **Na początek**, **Tłumacz dokument**, **Wybierz sposób tłumaczenia**, **Ustawienia i narzędzia**, **Wynik i problemy**.
- W HelpPage.qml tekst zakładki otrzymał jawny z: 2 oraz kolor palette.buttonText dla stanu nieaktywnego; tekst aktywnej zakładki nadal korzysta z palette.highlightedText.
- Dla motywu okna dodano jawne przełączenie koloru całego ApplicationWindow na podstawie bridge.theme; zmiana themeChanged wywołuje aktualizację bez oczekiwania na zmianę motywu systemowego.
- Świeży test runtime offscreen potwierdził: **dark = #202124**, **light = #ffffff** oraz 5 poprawnie wyrenderowanych tytułów zakładek Pomocy.
- qmllint dla Main.qml i HelpPage.qml: **PASS**; compileall dla qml_gui: **PASS**.
- Backup przed zmianą: backups/20261007-003149-help-theme-fix/ oraz automatyczne backupy plików tworzone przez edytor SentinelX.

## 2026-10-07

- Naprawiono błędy tłumaczenia TranslateGemma na CPU wynikające z równoległego wysyłania żądań do llama.cpp: tryb CPU wymusza `effective_translation_parallel=1` oraz `effective_server_parallel=1`.
- Automatyczny restart serwera llama.cpp po tłumaczeniu również używa efektywnej równoległości CPU zamiast surowej wartości z GUI.
- Aktywne `$HOME/.config/tlumacz/config.json` ustawiono na `server_parallel=1` dla bieżącej pracy CPU.
- Dodano regresję sprawdzającą serializację tłumaczenia i slotu serwera w CPU.
- Świeży test runtime CPU: `Hello world.` → `Witaj świecie.`; 46,67 s, `finish_reason=stop`, bez timeoutu.

## 2026-10-07 — poprawka rzeczywistego renderowania zakładek Pomocy

- Usunięto zależność delegatek zakładek Pomocy od map `modelData["title"]`/`modelData["content"]`, która powodowała puste napisy w rzeczywistym QML.
- Zakładki korzystają teraz z jawnych właściwości `helpTopic1Title`–`helpTopic5Title` oraz odpowiadających im treści. Dzięki temu tytuły są bezpośrednio wartościami tekstowymi modelu Repeatera.
- Zweryfikowano rzeczywisty runtime QML: PL: **Na początek**, **Tłumacz dokument**, **Wybierz sposób tłumaczenia**, **Ustawienia i narzędzia**, **Wynik i problemy**; EN: **Getting started**, **Translate a document**, **Choose the translation method**, **Settings and tools**, **Results and problems**.
- Zweryfikowano również zmianę motywu w runtime: **Jasny = #ffffff**, **Ciemny = #202124** bez zmiany motywu systemowego.
- Testy regresyjne QML: **4 passed**; `qmllint` i `compileall`: **PASS**.

## 2026-10-07 — poprawka powiadomienia zmiany motywu

- Znaleziono rzeczywistą przyczynę sytuacji, w której pole **Motyw** pokazywało `Jasny`, ale paleta i tło okna pozostawały w starym schemacie: właściwość `bridge.theme` miała `notify=stateChanged`, podczas gdy `set_theme()` emitowała `themeChanged`.
- Zmieniono sygnał powiadomienia właściwości `theme` na `themeChanged`, dzięki czemu wszystkie bindingi QML zależne od `bridge.theme` są przeliczane natychmiast po wyborze motywu.
- Zweryfikowano runtime offscreen: po `setTheme("light")` kolor okna wynosi `#ffffff`, a po `setTheme("dark")` `#202124`; kolory tekstu nieaktywnych zakładek zmieniają się odpowiednio na `#202124` i `#f1f3f4`.
- Testy regresyjne: **4 passed**; `qmllint`: **PASS**; `compileall`: **PASS**.

## 2026-10-07 — faktyczna korekta dziedziczenia motywu QML

- Wykorzystano istniejącą dokumentację kontraktu GUI dotyczącą palety (`docs/technical-docs/QML_GUI_LAYOUT.md`, `docs/technical-docs/GUI-zbior_praktycznej_wiedzy.md`) i zweryfikowano ją względem rzeczywistego zachowania QML.
- Stwierdzono, że samo ustawienie `ApplicationWindow.palette.*` nie gwarantuje poprawnego użycia palety przez zagnieżdżone strony/komponenty w każdym miejscu GUI. Objawem był ciemny kolor ramy/tła `ApplicationWindow` przy jasnych powierzchniach treści.
- W `HelpPage.qml`, `HelpMarkdownView.qml`, `ApiPage.qml`, `TranslationPage.qml` i `ExtrasPage.qml` odwołania do palety zostały związane jawnie z `ApplicationWindow.window.palette.*`.
- Dzięki temu kolor tekstu, powierzchni, obramowań i zaznaczeń korzysta z palety faktycznie ustawionej na głównym oknie, zamiast z lokalnej palety kontrolki/strony.
- Naprawiono również kontrakt widoczności napisów zakładek Pomocy: ich tekst używa palety głównego `ApplicationWindow`.
- Test regresyjny QML: **5 passed**; `qmllint`: **PASS**; `compileall`: **PASS**.

## 2026-10-07 — korekta raportowania pominiętych fragmentów Markdown

- Naprawiono mechanizm raportowania fragmentów pominiętych przez filtr Markdown.
- Nagłówki Markdown są klasyfikowane jako fragmenty pominięte i nie są wysyłane do backendu tłumaczeniowego.
- Tekst jawnie oznaczony składnią Markdown (m.in. `**...**`, `__...__`, `*...*`, `_..._`, inline code oraz linki) jest klasyfikowany jako pominięty.
- Bloki fenced code, YAML front matter oraz linie metadanych są rejestrowane jako pominięte fragmenty zamiast znikać bez śladu z raportu.
- `DocumentProcessor` pobiera informację o pominiętych fragmentach bezpośrednio z sesji filtra i przekazuje ich rzeczywistą liczbę do GUI.
- Dodano regresję obejmującą nagłówki, znaczniki Markdown, front matter i fenced code oraz weryfikację zachowania dokumentu po zapisie.

## 2026-10-07 — korekta formatowania statystyk GUI

W sekcji statystyk tłumaczenia etykiety „Czas” i „Prędkość tłumaczenia” pozostają w podstawowym rozmiarze i normalnym kroju. Powiększenie oraz pogrubienie dotyczy wyłącznie wartości czasu i prędkości.

## 2026-10-07 — higiena artefaktów `.bak*`

- Dodano `tools/cleanup-bak.sh` do rekurencyjnego usuwania regenerowalnych plików `*.bak*` bez naruszania archiwów backupowych.
- Dodano regresję `tests/test_cleanup_bak.py` sprawdzającą usuwanie plików `*.bak*` również w podkatalogach przy zachowaniu pozostałych plików.
- Usunięto z drzewa projektu **818** istniejących plików `*.bak*`; po operacji pozostało **0** takich plików.
- Rozdzielono operacyjnie regenerowalne kopie `.bak*` od trwałych archiwów rollbacku w `backups/` i `.migration-backups/`.

## 2026-10-07 — PLAN-13: remediacja dokumentacji repozytorium

- Przygotowano aktywny plan `docs/Plany/PLAN-13-REMEDIACJA-DOKUMENTACJI-REPO-2026-10-07.md`.
- Plan obejmuje korelację filesystem ↔ `INDEX.yml`/`INDEX.md`, synchronizację STATUS/BUG/TODO/CHANGELOG, rozdzielenie stanu bieżącego od historii, repo boundary oraz weryfikację dokumentacji technicznej względem aktualnego kodu.
- Wprowadzono zasadę ruchomego baseline'u: przy trwających pracach nad repozytorium każdy etap musi ponownie ustalić stan przed zapisem.
- Udokumentowano aktualną rozbieżność indeksu: 15 istniejących plików poza indeksem i 7 wpisów indeksu bez odpowiadających ścieżek.
- Udokumentowano, że ostatni pełny suite zakończył się `542 passed, 1 failed`, a `PLAN-12` wymaga synchronizacji statusu z niewykonanym rzeczywistym E2E.


## 2026-10-07 — PLAN-13: Etap 1 i korekta statusu PLAN-12

- Odtworzono i zsynchronizowano `docs/INDEX.yml` z żywym filesystemem `docs/`: 494 pliki i 494 wpisy.
- Zweryfikowano 0 brakujących ścieżek, 0 martwych wpisów i 0 duplikatów; YAML przechodzi parser.
- `docs/INDEX.md` zsynchronizowano z aktualną liczbą plików oraz PLAN-12/PLAN-13.
- Usunięto wyłącznie martwe wpisy indeksu; żaden plik dokumentacji nie został usunięty.
- PLAN-12 ma obecnie status `active`, ponieważ rzeczywiste E2E llama.cpp/TranslateGemma pozostaje niewykonanym elementem exit gate.


## 2026-10-07 — PLAN-13: kontrakty pipeline, granica repo i cleanup artefaktów

- Dodano kanoniczny `docs/technical-docs/translation-pipeline-contracts.md`.
- Skorygowano opis produkcyjnego `FilterRegistry` i TPlugin w `functional-capabilities.md`.
- Udokumentowano jawnie lukę wspólnego kontraktu `nested fields` / `complex fields`.
- Ustalono, że rootowe dokumenty audytowe pozostają poza zakresem `INDEX.yml` bez automatycznego przenoszenia.
- Potwierdzono `*.bak* = 0` po cleanupie i zachowano trwałe backupy.


## 2026-10-07 — zamknięcie PLAN-13

- Końcowa korelacja dokumentacji: `docs` 495 plików ↔ `INDEX.yml` 495 wpisów, 0 brakujących, 0 martwych, 0 duplikatów.
- `TODO-DOC-013` zamknięte.
- Nierozstrzygnięty `TODO-PLAN12-001` pozostaje otwarty; pełny suite pozostaje 542/1.


## 2026-10-07 — ograniczenie CPU llama.cpp do budżetu per slot

- potwierdzono host: 8 rdzeni fizycznych / 16 wątków logicznych;
- rozdzielono semantycznie `parallel` od liczby wątków CPU obsługujących pojedynczy slot;
- przywrócono profil V3 `threads=8` i `threads_batch=16`;
- przy `parallel=4` maksymalny budżet odpowiada 8 rdzeniom fizycznym zamiast angażowania 16 wątków do pojedynczego requestu;
- zaktualizowano profil repozytorium i aktywny profil użytkownika `$HOME/.config/tlumacz/llama.json`;
- dodano test kontraktu konfiguracji CPU.

## 2026-10-07 — PLAN-12: weryfikacja poza zakresem Okapi

- Prace nad FilterRegistry/Okapi pozostawiono innemu agentowi.
- Potwierdzono testami regionalne kody językowe xx-YY / xx_YY w language_code_for().
- Zaktualizowano test kontraktu chunk/batch: jeden logiczny chunk = jeden request batchowy.
- Gate ukierunkowany: 35 passed.
- Rzeczywisty E2E TranslateGemma pozostaje otwarty.


## 2026-10-07 — domknięcie rozszerzalności formatów i regresji GUI

- Potwierdzono wdrożenie wspólnego kontraktu filtrów: Okapi jako primary, native jako fallback.
- Potwierdzono wspólny preprocessing `translate/keep` przed backendem.
- Potwierdzono brak potrzeby sztucznej konwersji TXT → XLIFF.
- Dodano korektę regresji `TranslationPage.qml`: czas tłumaczenia jest prezentowany zgodnie z istniejącym kontraktem GUI jako `tr("ui.time") + formatTime(bridge.elapsedSeconds)`.
- Testy ukierunkowane po zmianie: **19 passed**.
- Pełny suite przed poprawką GUI: **563 passed, 1 failed**; przyczyną była wyłącznie niezgodność QML z asercją regresyjną.
- Backup zmienionego QML wykonany przez SentinelX w `backups/20261007-finalization-gui/`.

## [Unreleased] — 2026-10-07 — rozszerzalność backendów

### Backendy
- przebudowano BackendRegistry na rejestr adapterów bez routingu if/elif zależnego od konkretnego backendu;
- dodano rejestrację backendów przez register() i wstrzykiwanie implementacji przez konstruktor;
- dodano BackendCapabilities oraz API capabilities() w rejestrze i BackendService;
- wydzielono backend „Własny” do src/tlumacz/backends/custom/backend.py;
- custom korzysta ze współdzielonego transportu OpenAICompatibleProvider, ale nie jest providerem Cloud;
- dodano test kontraktowy TestBackend potwierdzający możliwość dodania nowego backendu bez zmian w pipeline dokumentowym.

### Weryfikacja
- 18 testów kierunkowych: PASS;
- FilterRegistry/Okapi: bez zmian;
- backup przed zmianą: backups/20261007-backend-extensibility-pre/.

## 2026-10-07 — przywrócenie tuningu V3 backendu llama.cpp

- `threads=8` i `threads_batch=16` przywrócone na podstawie `docs/wdrozenia/rekomendacja-ustawien-llama.cpp.md`.
- `batch_size=2048` i `ubatch_size=512` pozostają zgodne z rekomendacją V3.
- `ctx_size` pozostaje dynamiczne (`auto`) i jest wyliczane z parametrów dokumentu.
- `parallel` nie został wpisany na sztywno; nadal jest przekazywany z GUI.
- Backup wykonano przed zmianą: `backups/20261007-backend-routing-tuning/pre-change.tar.gz` (SHA-256 `d1d479450229a2ad123397795bd3aa151c150a6d5e082e81feb7eac871fb55c2`).

## 2026-10-07 — korekta regresji QML czasu tłumaczenia

- Przywrócono rozdzielenie etykiety `Czas` od wartości czasu w `TranslationPage.qml`. Sama wartość czasu pozostaje wyróżniona, zgodnie z wymaganiem GUI.
- Zmiana jest niezależna od bieżących prac nad API `BackendRequest`.


## 2026-10-07 — GUI: tylko motyw systemowy i link projektu

- Usunięto z interfejsu użytkownika wybór motywu `Systemowy/Jasny/Ciemny`.
- Wymuszono bieżący stan GUI na `system`, również gdy wcześniejsza konfiguracja zawierała `dark` lub `light`.
- Zachowano kod techniczny obsługi zmiany motywu do przyszłego przywrócenia opcji.
- W dialogu **O programie** dodano klikalny link do strony projektu `https://frs777.github.io/tlumacz-v4/zrzuty.html`.
- Backup: `backups/20261007-theme-system-only-project-link/pre-change.tar.gz`.


Weryfikacja tej zmiany: dedykowany zestaw `tests/test_qml_gui.py` — 158 passed; `compileall` i `qmllint` — PASS. Pełny suite wykrył niezależny problem równoległej zmiany `tlumacz.filter_engine.preprocessor`; nie był on powodowany zmianą motywu ani dialogu O programie.


### 2026-10-07 — ograniczenie bindu llama.cpp
- wbudowany serwer `llama.cpp` przyjmuje wyłącznie `127.0.0.1`, `localhost` lub `::1`;
- `0.0.0.0` i adresy LAN są odrzucane również przy uruchamianiu z zapisanej konfiguracji;
- backend `custom` zachowuje możliwość wskazania dowolnego zewnętrznego URL;
- dodano regresję dla adresów niedozwolonych i dozwolonych oraz dla backendu `custom`;
- potwierdzono, że FastAPI nie występuje w aktualnym kodzie aplikacji.

## 2026-10-07 — Apertium bundlowane dane językowe

- przeniesiono 27 kierunków Apertium objętych release scope do
  src/tlumacz/backends/apertium/native_runtime/share/apertium/;
- ustawiono bundlowane dane jako domyślne źródło danych ApertiumRuntime;
- Bridge GUI domyślnie korzysta z tego samego drzewa runtime;
- dodano regresję potwierdzającą wybór bundlowanych danych mimo obecności
  katalogu użytkownika;
- dodano regresję potwierdzającą rozwiązywanie katalogu pary bez systemowego
  PATH;
- ces-pol pozostaje wyłączone z bundlowanego release scope.


## 2026-10-07 — narzędzia paczek Apertium

- Pipeline budowania paczek Apertium przeniesiono poza `src/tlumacz/` do `tools/apertium/package_pipeline.py`.
- Testy i dokumentacja zostały dostosowane do nowej granicy runtime/narzędzia wewnętrzne.
- Dodano instrukcję ręcznego tworzenia paczek w `docs/technical-docs/apertium-paczki-reczne-tworzenie.md`.
## 2026-10-07 — narzędzia autora TPlugin

- dodano tools/tplugin/create.py do generowania minimalnego projektu źródłowego pluginu;
- dodano test regresyjny generatora;
- dodano aktualną specyfikację ręcznego tworzenia TPlugin;
- oznaczono starszą instrukcję ręczną jako zastąpioną, aby nie mieszała aktualnego magazynu /home/frs/.config/filters z historycznym layoutem.


## 2026-10-07 — README EN
- Dodano do `README_en.md` link do strony projektu i strony pobierania: https://frs777.github.io/tlumacz-v4/pobieranie.html.
## 2026-10-07 — dokument kanoniczny tworzenia pluginów Okapi

- docs/technical-docs/tworzenie-pluginow-okapi.md jest kanoniczną instrukcją tworzenia pluginów Okapi z wykorzystaniem narzędzi TPlugin;
- dokument zawiera również audyt statusu java/filter-host/;
- potwierdzono, że właściwy runtime FilterHost znajduje się w src/tlumacz/resources/filter-host/.


## 2026-10-07 — Inicjalizacja profilu użytkownika przy instalacji

- Dodano automatyczne tworzenie $HOME/.config/tlumacz/ podczas instalacji ze źródeł.
- Dodano puste katalogi skills, filters, apertium i logs.
- Wzorce konfiguracji są pobierane z repozytoryjnego config/, a nie z istniejącego profilu użytkownika.
- Ponowna instalacja nie nadpisuje istniejącej konfiguracji użytkownika.

- 2026-10-07: usunięto hardcodowane `/home/frs` z aktywnego kodu magazynu filtrów, launchera i testów; ścieżki użytkownika są wyznaczane przez `$HOME`/`XDG_CONFIG_HOME`.


## 2026-10-08 — naprawa publikacji repozytorium GitHub

- Ustalono, że katalog roboczy `tlumacz-v4` nie posiadał własnego `.git` i był błędnie obejmowany przez nadrzędne repozytorium `/home/frs/Projekty`.
- Zweryfikowano właściwy zdalny adres repozytorium: `https://github.com/frs777/tlumacz-v4.git`.
- Poprawiono adres repozytorium w `pyproject.toml` na `frs777/tlumacz-v4`.
- Przygotowano synchronizację bieżącego programu z gałęzią `main` repozytorium GitHub.

## 2026-10-08 — utworzenie właściwego repozytorium Git V4

- Utworzono lokalne repozytorium Git bezpośrednio w katalogu źródłowym `$HOME/Projekty/tlumacz-v4`.
- Repozytorium nie dziedziczy już stanu Git nadrzędnego katalogu `$HOME/Projekty`.
- Zdefiniowano granicę publikacji w lokalnym `.gitignore`; `config/` i `licenses/` nie są już błędnie wykluczane z repozytorium.
- Zdalne repozytorium pozostaje `https://github.com/frs777/tlumacz-v4.git`.
- Wykonano backup plików dokumentacji i `.gitignore` przed zmianą.
