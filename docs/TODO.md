## 2026-10-07 — domknięcie starego kontraktu Apertium w CI

- Zaktualizowano workflow CI do aktualnego modelu TAR-only.
- Historyczne asercje wheel o `native_runtime/share/apertium` zostały zastąpione audytem bundlowanego executable i zakazem osadzania danych językowych/paczek TAR w wheel.
- Clean-install smoke CI dostarcza reprezentatywną parę językową z `tests/fixtures/apertium/` do izolowanego magazynu użytkownika. Testy lokalne korzystają domyślnie z `$HOME/.config/tlumacz/apertium`.
- Lokalny odpowiednik gate'u przeszedł: **YAML parse PASS; wheel TAR-only audit PASS; clean-install Apertium TAR smoke PASS**.
- Ten punkt nie wymaga dalszej zmiany kodu produkcyjnego.

## 2026-10-07 — walidacja suite po synchronizacji testów Apertium

- Synchronizacja testów B1–B8 z aktualnym kontraktem Apertium TAR-only została zweryfikowana pełnym suite.
- Wynik: **599 passed in 92.37s**, bez FAIL i SKIP.
- Kod produkcyjny nie wymagał zmian w tej serii synchronizacji.
- TODO-015 pozostaje otwarte jako zadanie wydaniowe/runtime, niezależnie od zielonego suite.

## 2026-10-07 — decyzje porządkujące listę operacyjną

### Apertium — sposób dystrybucji
**Status: USTALONE**

Bundlowany runtime Apertium będzie dostarczany razem z kodem źródłowym aplikacji V4. Ze względu na mały rozmiar artefaktu nie przewiduje się osobnej procedury pobierania runtime'u. Runtime może pozostać bezpośrednio w zasobach aplikacji. Ewentualny inventory licencji/NOTICE/source pozostaje elementem dokumentacji dystrybucyjnej, a nie osobnym mechanizmem instalacji runtime'u.

### Pozostałe punkty listy operacyjnej
Zgodnie z aktualnym stanem projektu pozostałe omawiane punkty tej listy zostały zrealizowane; nie są ponownie otwierane w ramach tego zadania. Dotyczy to w szczególności wycofania FastAPI/OpenVINO, ustaleń bezpieczeństwa API oraz bieżącego zakresu packagingu. `llama.cpp` i ZenDNN pozostają poza zakresem tej pracy.

---

## 2026-10-07 — TODO-011: centralna konfiguracja logowania

**Status: ZAMKNIĘTE — 2026-10-07**

Konfiguracja centralnego logowania została wdrożona:
- centralny logger `tlumacz` zapisuje logi do `$HOME/.config/tlumacz/logs/tlumacz.log`;
- poziom domyślny pozostaje `DEBUG`, ponieważ V4 jest nadal wersją testową;
- format logu jest jednolity i komunikaty aplikacji są prowadzone po polsku;
- logowanie do konsoli pozostaje aktywne podczas uruchamiania GUI;
- sekrety z `.key` są rejestrowane przez warstwę redakcji i nie powinny trafiać do logów;
- redakcja obejmuje pola `api_key`, `Authorization`, tokeny, hasła, sekrety, nagłówki Bearer, parametry zapytań oraz znane wartości sekretów;
- redakcja obejmuje również treść wyjątków i tracebacków;
- nie wyłączono szczegółowego logowania diagnostycznego.

Domknięto systematyczne podłączenie diagnostyki do granic pipeline'u, orkiestracji chunków oraz transportów Cloud, llama.cpp i Apertium. Nie logujemy treści dokumentów, payloadów ani nagłówków autoryzacyjnych; poziom `DEBUG` pozostaje aktywny.

Backup przed zmianą: `backups/20261007-logging-pre/logging-pre.tar.gz`.
SHA-256: `24dc4db8a3e5229a869250228a2b3df68fbc73b232ac3a9843d790cea70e1c93`.

---

## PLAN-14 — pozostały gate runtime KDE

- [ ] Uruchomić Tłumacz w rzeczywistej sesji KDE UID 1000 i sprawdzić system, dark, light oraz powrót do system.
- [ ] Potwierdzić zmianę palety widzianą przez Fusion/Qt Quick Controls po zmianie schematu KDE.
- [ ] Po wykonaniu gate'u zdecydować, czy fallback pozostaje wymagany na tej platformie.
- [ ] Dopiero po tym zamknąć BUG-041/PLAN-14.

Kod i testy są obecnie zweryfikowane lokalnie; brak zamknięcia dotyczy wyłącznie platformowego gate'u GUI.

---

## 2026-10-07 — TODO-OKAPI-REGISTRY-001

**Status: ZAMKNIĘTE**

Implementacja zasad `instrukcja-okapi.md` dla primary/fallback w FilterRegistry.

- [x] native fallback rejestrowany przed discovery;
- [x] discovery TPlugin nie filtruje suffixów zajętych przez native;
- [x] Okapi może przejąć suffix native;
- [x] plugin z mieszanym zestawem suffixów rejestruje wszystkie rozszerzenia;
- [x] Markdown pozostaje na natywnej ścieżce tekstowej i nie jest przejmowany przez plugin Okapi;
- [x] test regresyjny native → Okapi;
- [x] dokumentacja zaktualizowana;
- [x] backup wykonany;
- [x] gate registry 17/17 PASS;
- [x] skoncentrowany gate Okapi/TPlugin 47/47 PASS.

---

## 2026-10-07 — Filter Engine / Okapi: diagnostyka i naprawa kontraktu markerów

### TODO-FILTER-ENGINE-042 — E2E markerów z rzeczywistym backendem
**Status:** OTWARTE — infrastruktura backendu niedostępna w sesji 2026-10-07

- [x] zreprodukować Okapi extract na README z dużą liczbą inline codes;
- [x] potwierdzić poprawność PUA przed backendem;
- [x] wprowadzić ochronę PUA → __OKAPI_CODE_N__;
- [x] dodać ścisły restore z kontrolą kolejności/tożsamości;
- [x] dodać regresje identity, brakującego, zduplikowanego i przestawionego markera;
- [ ] wykonać rzeczywisty MASKED REQUEST → RAW RESPONSE na aktywnym backendzie;
- [ ] zweryfikować cache ON/OFF z rzeczywistym backendem.

### TODO-FILTER-ENGINE-043 — pełny gate lifecycle Qt/PySide6
**Status:** OTWARTE — wymaga świeżego przebiegu pełnego suite Qt

- [x] zmienić reader threads Filter Host z daemon na non-daemon;
- [x] dodać regresję wielokrotnego start → request → close;
- [ ] wykonać pełny tests/test_qml_gui.py;
- [ ] potwierdzić brak SIGABRT, aktywnych tlumacz-filter-* i ResourceWarning.

---
## 2026-10-07 — izolacja sekretów profili Cloud

- Naprawiono regresję testową wynikającą z użycia różnych magazynów sekretów podczas rekonstrukcji bridge'a.
- Kontrakt testów: jeżeli test zapisuje sekrety do tymczasowego `SecretStore`, każda rekonstruowana instancja musi otrzymać ten sam `secret_path`; testy nie mogą czytać rzeczywistego magazynu użytkownika.
- Produkcyjny `bridge.py` nie wymaga zmiany dla tego przypadku.
- Regresje rozszerzono o niezależne wpisy `SERVICE/ChatGPT`, `SERVICE/Codex` i `SERVICE/local` oraz brak sekretów/`api_key` w JSON po zapisie.
- Skoncentrowana walidacja: **14 passed**; pełna suite pytest pozostaje w toku.

## 2026-10-07 — zamknięcie diagnostyki `settings-v4.json` / skip-pattern

- Aktywny V4 używa wyłącznie `$HOME/.config/tlumacz/config.json`.
- Historyczny `build/lib/tlumacz/qml_gui/config.py` został zsynchronizowany ze źródłem, aby artefakt build nie odtwarzał `settings-v4.json`.
- Regresja `test_document_translation_service_applies_skip_patterns_before_backend` została wzmocniona o kontrolę końcowego HTML.

## 2026-10-07 — kontrakt konfiguracji GUI

- `$HOME/.config/tlumacz/config.json` jest jedynym aktywnym plikiem trwałej konfiguracji GUI.
- `settings-v4.json` jest historycznym plikiem legacy i nie należy go tworzyć, odtwarzać ani traktować jako źródła ustawień.
- Unifikacja konfiguracji jest wdrożona w aktywnym kodzie `AppSettings` / `load_settings()` / `save_settings()`.

## 2026-10-06 — llama.cpp: karta referencyjna i automatyzacja buildów

- [ ] Przygotować kartę referencyjną dla każdego dedykowanego buildu llama.cpp: sprzęt, system, CPU/GPU, instrukcje, kompilator, commit, CMake, runtime i benchmarki.
- [ ] Przygotować skrypt automatycznego zebrania parametrów sprzętu CPU/GPU/RAM/VRAM/systemu.
- [ ] Przygotować skrypt generujący kartę referencyjną z wykrytych parametrów.
- [ ] Przygotować skrypt automatyzujący kompilację llama.cpp w dwóch trybach: `dedykowany` oraz `dystrybucyjny`.
- [ ] Tryb dystrybucyjny ma używać bardziej ogólnych parametrów, bez optymalizacji pod konkretny CPU/GPU.
- [ ] Tryb dedykowany może wykorzystywać `GGML_NATIVE` i optymalizacje konkretnego sprzętu.
- [ ] Dodać automatyczne benchmarki `/health`, latency, chunk 1000/2000/4000 znaków, `parallel=1/4`, CPU/RAM/VRAM i hash artefaktów.
- [ ] Przygotować osobne artefakty bundled dla Windows/macOS, jeżeli zapadnie decyzja o ich dystrybucji.
- [ ] Do czasu przygotowania ogólnych artefaktów: inne Linux x86_64 oraz Windows/macOS używają runtime'u systemowego.


### TODO-LLAMA-PACKAGING — platformowy tag wheel dla dołączonego ELF
**Status:** OTWARTE — wykryte 2026-10-06

Wheel zawierający dołączony `llama-server` Linux x86_64 jest obecnie budowany jako `py3-none-any`. To błędnie sugeruje brak zależności platformowej; specyfikacja wheel przewiduje osobne tagi platformowe, a dokumentacja PyPA wskazuje, że wheel może być platformowy także wtedy, gdy zawiera natywny executable uruchamiany jako subprocess.

Przed wydaniem należy rozdzielić artefakty platformowe albo wymusić poprawny tag Linux x86_64 dla artefaktu zawierającego bundled llama.cpp. Nie należy oznaczać obecnego wheel jako wydania produkcyjnego dla wielu platform.
### TODO-LLAMA-RUNTIME — dołączony runtime llama.cpp
**Status:** ZAKOŃCZONE — 2026-10-06

- Zweryfikowano istniejący build `build-tlumacz-translation` zamiast ponownej kompilacji; build odpowiada rekomendowanemu profilowi CPU-native.
- Dołączono runtime Linux x86_64 wraz z kompatybilnymi bibliotekami `llama/ggml/mtmd`.
- Aplikacja domyślnie używa runtime'u dołączonego; ustawienie `runtime.source=system` zachowuje możliwość użycia instalacji systemowej.
- Dodano TDD dla wyboru runtime'u, profilu tuningu i zasobów pakietu.
- Dodano instrukcję ręcznej podmiany runtime'u własną kompilacją.
- Narzut runtime'u: około 23,2 MB przed kompresją.
- Walidacja: 17 testów konfiguracji/zasobów + świeży start `/health` + rzeczywiste TranslateGemma PL→EN.

## 2026-10-06 — etap 3: rozdzielenie implementacji filtrów od wspólnego runtime

- [x] **TODO-022i** — wykonano analizę rzeczywistych JAR-ów i rozdzielono implementacje aktywnych filtrów od classpathu wspólnego Java Filter Host; implementacje znajdują się fizycznie w `filters/<nazwa>/`, a launcher nie dodaje już całego `okapi-runtime/*` do classpathu rodzica.
- [x] **TODO-022i.a** — ustalono zależności wewnętrzne: EPUB→archive; HTML→abstractmarkup; JSON→generated-parser-compat; Markdown→HTML/YAML/generated-parser-compat; OpenXML→abstractmarkup; XLIFF2→XLIFF/lib-xliff2; YAML→generated-parser-compat.
- [x] **TODO-022i.b** — wydzielono zależności specyficzne dla Markdown (`flexmark*`) z `okapi-runtime/lib` do pakietu Markdown.
- [x] **TODO-022i.c** — dodano obsługę kontekstowego `ClassLoader` dla konfiguracji Okapi, aby zależności dynamicznie konfigurowane przez `ThreadSafeFilterConfigurationMapper` były ładowane z pakietu filtra bez globalnego classpathu.
- [x] **TODO-022i.d** — uzupełniono zależność OpenXML `com.twelvemonkeys.io.ole2` przez dołączenie lokalnego `common-io-3.12.0.jar`; descriptor wskazuje `com.twelvemonkeys.common:common-io:3.12.0`, a walidator potwierdza obecność wymaganych klas.
- [x] **TODO-022j** — ZAMKNIĘTE 2026-10-06. Wszystkie JAR-y pakietów filtrów są fizyczne, bez symlinków; `okapi-runtime` zawiera wyłącznie wspólny runtime; testy izolacji i dynamicznego loadera przechodzą.

`backups/okapi-runtime-split-20261006/pre-split.tar.gz` — SHA-256 `1085f98edcd58c6cee816571cce626452c80b3807b51ffe2e5b8b52561d5e9c2`.

Aktualny pełny gate po domknięciu 022j: **413 passed, 2 failed**. Dwa failure dotyczą niezależnie bitu wykonywania prywatnego runtime Apertium oraz lokalizacji języka QML; nie są regresjami etapu Okapi. TODO-022j jest zamknięte; pozostałe zadania 022d/022e dotyczą osobno docelowego magazynu użytkownika i loadera pakietów.

## 2026-10-06 — etapowanie dynamicznego ładowania filtrów

- [x] **TODO-022f** — `FilterRegistry.register_lazy()` i lazy instancjonowanie filtrów; fabryka jest wywoływana dopiero po rozpoznaniu rozszerzenia dokumentu.
- [x] **TODO-022g** — cykl życia instancji filtra ograniczony do sesji dokumentu; po `close()` rejestr nie utrzymuje instancji.
- [x] **TODO-022h** — przygotowano Java Filter Host do dynamicznego ładowania konkretnego filtra z magazynu `filters/` przez izolowany `ClassLoader`; descriptor i JAR-y pakietu są ładowane dopiero przy użyciu.
- [x] **TODO-022i** — rozdzielono w `okapi-runtime` wspólny runtime od implementacji filtrów i zależności specyficznych; analiza zależności została wykonana przed migracją.
- [ ] **TODO-022j** — po analizie zależności zastąpić przejściowe symlinki rzeczywistymi pakietami filtrów w jedynym magazynie `filters/`; dopiero wtedy usunąć odpowiednie implementacje z `okapi-runtime` za wyraźną zgodą.


## 2026-10-06 — magazyn filtrów użytkownika

- [x] TODO-022a — wprowadzono `FilterStore` jako warstwę lokalizacji magazynu filtrów;
- [x] TODO-022b — domyślny magazyn użytkownika wskazuje `$HOME/.config/tlumacz/filters/` (z uwzględnieniem `XDG_CONFIG_HOME`);
- [x] TODO-022c — przygotowano i aktywowano docelową lokalizację `/home/frs/.config/tlumacz/filters/`;
- [x] TODO-022d — domyślny magazyn przełączono na `$HOME/.config/tlumacz/filters`; pakiety `.tplugin` są odkrywane z tego magazynu i rozpakowywane do tymczasowego `/tmp/filters/`;
- [x] TODO-022e — wdrożono loader pakietów TPlugin dostarczanych przez użytkownika; trwały runtime `filter-engine/plugins` nie jest używany.

`/home/frs/.config/filters/` jest pozostałością po błędnej migracji i nie jest używany przez aktywny kod. Usunięcie tego katalogu pozostaje operacją porządkową zależną od uprawnień hosta.



- [ ] **TODO-019** — przywrócić bit `u+x` w 34 plikach prywatnego runtime Apertium; obecna sesja nie może zmienić trybu, ponieważ pliki należą do `frs` i są objęte ACL;
- [ ] **TODO-020** — ustalić i zweryfikować kanoniczny entrypoint V4 dla testu wersji; `python -m tlumacz --version` nie działa, ponieważ brak `tlumacz.__main__`, a `/usr/bin/tlumacz` wskazuje na globalny V3;
- [ ] **TODO-021** — powtórzyć clean-wheel build w środowisku z prawidłową własnością repozytorium/konfiguracją Git, bez zmiany globalnego V3.

Wynik gate: **373 passed, 1 failed**; Ruff/mypy/compileall/qmllint **PASS**; macierz backendów/dokumentów/GUI/packagingu **181 passed**. Projekt pozostaje Release Candidate.

---
## 2026-10-06 — magazyn Apertium po archiwizacji

`TODO-004` pozostaje otwarte jako zadanie kompletności par. Aktywny magazyn użytkownika został jednak zabezpieczony i odchudzony do pakietów z artefaktami binarnymi; źródła usunięte z aktywnego katalogu są dostępne w `backups/tlumacz-user-Apertium-full-20261006.7z`. Dalsza kompilacja brakujących par może być wykonywana z archiwum lub z zachowanych źródeł `Aperitium/`, bez ponownego pobierania danych.

Dodatkowo naprawiono runtime discovery pakietów użytkownika oraz dodano regresje TDD; rzeczywisty adapter potwierdzono dla `eng-pol` i `eng-spa`.

---
id: todo-v4
status: active
meta:
  contentType: TaskList
  category: governance
version: 0.40.0
updated: 2026-10-06
owner: project-maintenance
source:
  - src/tlumacz/
  - docs/STATUS.md
  - docs/BUG.md
depends_on:
  - docs/ARCHITECTURE.md
  - docs/Audyt/AUDYT_FINALNY_GATE_2026-10-04.md
expires_when: zamknięcie bieżących zadań Release Candidate 0.40.0
last_validation: "pełny pytest 373 passed, 1 failed; TranslateGemma GUI E2E PASS; round-trip 28 passed; macierz backendów/dokumentów/GUI/packagingu 181 passed, 2026-10-06"
---

# Tłumacz V4 — aktywne TODO

## 2026-10-07 — zmiana magazynu filtrów

**Status:** WDROŻONE

- Magazyn użytkownika: `/home/frs/.config/tlumacz/filters`.
- Runtime rozpakowanych paczek: `/tmp/filters/`, wyłącznie tymczasowo.
- Wspólne JAR-y Okapi: `src/tlumacz/resources/okapi-runtime/lib/`.
- XLIFF 2.0: `src/tlumacz/documents/xliff.py`, poza `FilterRegistry`.
- Nie używać ponownie `filter-engine/plugins`, `filter-engine/shared-libs`, `dist/tplugins` ani `build/tplugins`.


Ten dokument zawiera wyłącznie zadania nadal otwarte. Zamknięte prace pozostają w planach, audytach i changelogu.

## Zrealizowane 2026-10-06 — wybór języka Apertium

- [x] aktywne ComboBoxy źródła i celu w GUI Apertium;
- [x] discovery tylko faktycznie skompilowanych kierunków;
- [x] indeks logicznie dwukierunkowych par dla wyboru GUI;
- [x] filtrowanie celu względem źródła;
- [x] zerowanie niezgodnego celu po zmianie źródła;
- [x] stan `brak pary` i blokada selektora celu;
- [x] automatyczna detekcja tekstowego źródła przez istniejący Lingua `LanguageDetector`;
- [x] testy jednostkowe, bridge i QML.

## Zrealizowane 2026-10-06 — Plan 01 / rzeczywiste E2E Apertium

- [x] bundlowany runtime Apertium ustawia jawny APERTIUM_DATADIR;
- [x] detekcja Lingua en jest zgodna z konfiguracją źródła Apertium eng;
- [x] rzeczywisty przepływ aplikacyjny TranslationApp → Apertium dla eng → pol;
- [x] regresje TDD oraz pełny suite V4: 363 passed.

## P0 — blokery przed final release

### TODO-001 — dependency closure i licencje
**Status:** OTWARTE

Przygotować pełny inventory komponentów dostarczanych z artefaktem: Python, Java/Okapi, Apertium, lingua-rs oraz pozostałe runtime'y. Dla każdego komponentu ustalić wersję, źródło, licencję i obowiązki NOTICE/source.

### TODO-002 — Windows runtime albo formalna zmiana zakresu
**Status:** ODŁOŻONE

Linux x86-64 pozostaje aktualnym targetem roboczym. Powrót do Windows wymaga osobnego planu runtime/packagingu.

## P1 — zadania przed finalnym gate'em

### TODO-003 — pełne E2E TranslateGemma
**Status:** ZAMKNIĘTE — 2026-10-06

Wykonano pełny przepływ przez rzeczywistą aplikację V4 i rzeczywisty model GGUF: GUI/QML → bridge → TranslationApp → DocumentTranslationService → llama-server `/v1` → odpowiedź → walidacja → wynik dokumentowy. GUI dostarczyło endpoint `http://127.0.0.1:2782/v1`, a techniczne parametry runtime zostały pobrane z `/home/frs/.config/tlumacz/llama.json`.

Dowód: model `/home/frs/Modele/translategemma-4b-it.Q5_K_M.gguf`, CPU, `chat_template=translategemma`, `parallel=4`, temperatura `0.0`, target `pl`; sygnał `translationFinished`; status `Tłumaczenie zakończone.`; zapisany wynik Markdown o rozmiarze `2405` B.

Nie użyto ręcznie hardkodowanego portu testowego ani ręcznego startu `llama-server`.

### TODO-004 — kompletność i jakość pozostałych par Apertium
**Status:** ZAMKNIĘTE — 2026-10-06

Release scope Apertium został domknięty na **27 READY / 1 EXCLUDED** z 28 przygotowanych paczek. `ces-pol` jest jawnie wyłączone z release scope po potwierdzeniu awarii `apertium-tagger` na dostarczonym `ces-pol.prob`; nie jest fałszywie deklarowane jako gotowe. Pozostałe 27 kierunków przechodzi kontrakt runtime gate, a prywatny runtime zawiera wymagane programy pipeline'u.

Szczegóły: `docs/technical-docs/apertium-pair-inventory-20261006.md` oraz `docs/reports/FAZA_6_APERTIUM_RUNTIME_GATE_2026-10-06.md`.

### TODO-005 — finalny round-trip reprezentatywnych dokumentów
**Status:** ZAMKNIĘTE — 2026-10-06

Wykonano macierz round-trip/Unicode/markerów dla aktywnych formatów DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF 2.0: **28 passed**. TXT i PDF nie są aktywnymi formatami `FilterRegistry` V4 i pozostają poza zakresem tego pipeline'u.

## P2 — jakość

### TODO-006 — QML smoke wszystkich głównych stron
**Status:** PLANOWANE

Po zamknięciu blockerów wykonać smoke każdej głównej strony QML na rzeczywistym runtime.

### TODO-007 — dekompozycja QmlApplicationBridge
**Status:** PLANOWANE

Wydzielać odpowiedzialności bridge etapami po characterization tests. Nie zmieniać kontraktu QML bez regresji.

### TODO-008 — accessibility runtime
**Status:** OTWARTE

Dokończyć weryfikację kolejności focusu keyboard-only, screen reader, high contrast oraz DPI/font scaling.

### TODO-009 — decyzja dotycząca `/usr/bin/tlumacz`
**Status:** OTWARTE / DECYZJA UŻYTKOWA

Nie zmieniać globalnego launchera V3 bez osobnej decyzji. Przed ewentualną zmianą wykonać audyt wywołań i przygotować rollback.

## Zasady

- Nie traktować braku testu jako PASS.
- Nie instalować nowych zależności bez uzasadnienia i zgody użytkownika.
- Przy zmianach kodu aktualizować dokumentację i wykonywać backup dla dużych zmian.
- Po zmianach dokumentacji odświeżać `INDEX.md` i `INDEX.yml`.
- Final release następuje dopiero po zamknięciu blockerów P0 i wykonaniu końcowego gate'u.

**Ostatnia aktualizacja:** 2026-10-06.


## 2026-10-06 — walidacja zależności filtrów

- [x] TODO-022l — wprowadzić kontrakt dependencies w filter.json oraz walidator wymaganych JAR-ów/klas.
- [x] TODO-022m — oznaczać pakiet z niespełnionymi zależnościami jako usable=False.
- [x] TODO-022n — zgłaszać brak zależności w Logu GUI i modalnym komunikacie z klikalnymi odnośnikami.
- [x] TODO-022o — wykrywać dodanie nowego pakietu filtra w czasie działania aplikacji przez watcher magazynu.
- [x] TODO-022p — zadeklarować i dostarczyć zależność OpenXML TwelveMonkeys Common IO; walidator potwierdza ją jako spełnioną.

### TODO-TPLUGIN-001 — pełna migracja filtrów do .tplugin

**Status:** W TRAKCIE

OpenXML ma już zweryfikowany format .tplugin i ładowanie przez FilterHost w izolowanym profilu. Pozostałe aktywne filtry wymagają inventory zależności, klasyfikacji A/B/C, budowy paczek i migracji runtime.

### TODO-TPLUGIN-002 — shared-libs i konflikt wersji

**Status:** ZAMKNIĘTE — 2026-10-06

Wdrożono kanoniczną tożsamość artefaktu id+version+SHA-256, współistnienie wielu wersji, rejestr referencji shared-libs, odbudowę indeksu, bezpieczny GC oraz zachowanie shared-libs przy uninstall do czasu GC. Potwierdzono 16/16 testów TPlugin.

### TODO-TPLUGIN-003 — narzędzia produkcyjne TPlugin

**Status:** ZAMKNIĘTE — 2026-10-06

Builder generuje inventory.json i checksums.json. Dodano narzędzie tools/tplugin/dependencies.py z poleceniami inventory, validate, rebuild i gc. Walidacja 9/9 paczek oraz test instalacyjny/lifecycle przeszły pomyślnie.


- [x] **TODO-022k** — ZAMKNIĘTE 2026-10-06. Wszystkie 9 dostępnych filtrów Okapi przygotowano jako paczki instalacyjne .tplugin. Dodano deklaratywny inventory i builder zbiorczy w tools/tplugin/build_all.py. Paczki mają manifesty, checksums, klasyfikację A/B/C oraz deklaracje shared-libs. Instalacja 9/9 do pustego profilu i capability smoke 9/9 przeszły pomyślnie.

- [x] **TODO-022l** — ZAMKNIĘTE 2026-10-06 w zakresie migracji runtime. FilterStore/FilterRegistry korzystają z rozpakowanych pluginów .tplugin jako produkcyjnego magazynu; wszystkie 9 pluginów zainstalowano do `/home/frs/.config/tlumacz/filter-engine/plugins`, a shared-libs do `/home/frs/.config/tlumacz/filter-engine/shared-libs`. FilterHost 9/9 odpowiada poprawnie na capabilities.
- [x] **TODO-022m** — ZAMKNIĘTE 2026-10-06. Dodano lifecycle `update()`, `uninstall()` i `rollback()` w TPluginInstaller. Backup poprzedniego stanu jest wykonywany przed zmianą, rollback przywraca także zależności shared wymagane przez manifest, a macierz lifecycle dla wszystkich 9 publicznych paczek `.tplugin` przechodzi. Pełny extract/merge/round-trip 9/9 pozostaje potwierdzony.


### TODO-TPLUGIN-004 — backend administracyjny i ręczne tworzenie paczek

**Status:** ZAMKNIĘTE — 2026-10-06

Utworzono niezależny moduł tools/tplugin_admin/ poza aplikacją Tłumacz. Backend obsługuje init, validate, build, verify, inspect, test-install i publish oraz deleguje pakowanie do TPluginBuilder. Dodano instrukcję ręcznego tworzenia TPlugin dla zaawansowanych użytkowników.

Workflow publish wykonuje walidację projektu, budowę paczki, walidację inventory/checksumów, instalację do tymczasowego runtime, kontrolę layoutu/shared-libs oraz zapis maszynowo czytelnego raportu publikacyjnego z SHA-256 artefaktu.

Weryfikacja: tests/test_tplugin_admin.py — 11 passed. Backup rozszerzenia: backups/tplugin-admin-20261006/pre-admin-completion.tar.gz.

## 2026-10-07 — PLAN-13: remediacja dokumentacji repozytorium

### TODO-DOC-013 — synchronizacja dokumentacji z żywym repozytorium
**Status:** ZAMKNIĘTE — 2026-10-07

Plan naprawczy: `docs/Plany/PLAN-13-REMEDIACJA-DOKUMENTACJI-REPO-2026-10-07.md`.

- [x] wykonać ruchomy baseline przed każdym etapem;
- [x] zsynchronizować `INDEX.yml` z rzeczywistym filesystemem;
- [x] zsynchronizować `INDEX.md` z indeksem kanonicznym;
- [x] rozstrzygnąć 16 istniejących plików poza indeksem;
- [x] rozstrzygnąć 5 wpisów dokumentacyjnych bez istniejącego pliku oraz 2 wpisy rootowe poza zakresem indeksu;
- [x] uporządkować STATUS/BUG/TODO względem ostatnich wyników;
- [x] skorygować status PLAN-12 względem niewykonanego E2E;
- [x] uzupełnić dokumentację kontraktów chunk/batch/skip/language;
- [x] formalnie opisać lub oznaczyć lukę dla `nested fields` / `complex fields`;
- [x] ustalić repo boundary i klasyfikację rootowych dokumentów;
- [x] wykonać końcową korelację kod ↔ test ↔ docs ↔ runtime evidence;

### TODO-PLAN12-001 — domknięcie exit gate TranslateGemma batch/E2E
**Status:** OTWARTE

- [ ] wykonać rzeczywisty E2E dokument → aktywny llama.cpp/TranslateGemma → wynik dokumentowy;
- [ ] potwierdzić liczbę requestów zgodną z liczbą logicznych chunków;
- [ ] rozstrzygnąć aktualny failure `test_document_translation_service_uses_structural_markdown_chunks_and_one_batch_request`, który oczekuje dwóch wywołań `translate_batch`, podczas gdy aktualna implementacja wykonuje jeden batch dla chunka;
- [ ] dopiero po spełnieniu wszystkich punktów zmienić status PLAN-12 z `active`.


## 2026-10-07 — motyw systemowy: stan bieżący

- [x] Usunąć z GUI wybór motywu `Systemowy/Jasny/Ciemny`.
- [x] Pozostawić techniczny mechanizm zmiany motywu w kodzie z komentarzem o przyszłym przywróceniu opcji.
- [x] Dodać link do strony projektu w dialogu **O programie**.
- [ ] W przyszłości przywrócić wybór motywu dopiero po potwierdzeniu poprawnego przełączania Qt/Fusion w rzeczywistej sesji KDE.


## Bezpieczeństwo — bind lokalnego llama.cpp
- [x] Ograniczyć wbudowany `llama.cpp` do loopback (`127.0.0.1`, `localhost`, `::1`).
- [x] Zachować dowolne adresy dla backendu `custom`.
- [x] Dodać regresję dla `0.0.0.0` i adresów LAN.

## Aktualizacja 2026-10-07 — Apertium

Migracja architektury bundlowanego runtime została wykonana: 27 kierunków
release scope znajduje się bezpośrednio w native_runtime/share/apertium/,
a runtime i Bridge GUI wybierają to drzewo domyślnie.

Pozostały czynności niezwiązane z samym uruchomieniem:
- przygotowanie końcowego inventory licencji/NOTICE/source dla artefaktu
  dystrybucyjnego;
- cleanup katalogu `Aperitium/`: audyt 2026-10-07 potwierdził brak zależności
  w `src/`, ale wykrył dwie aktywne zależności developerskie —
  `tools/apertium/package_pairs.py` oraz `tests/test_apertium_pair_repairs.py`;
  przed usunięciem katalogu trzeba je przepiąć/usunąć zgodnie z przeznaczeniem,
  zaktualizować dokumentację i wykonać końcową weryfikację.


### TODO — inicjalizacja profilu użytkownika

**Status: ZREALIZOWANE 2026-10-07**

Instalacja ze źródeł tworzy $HOME/.config/tlumacz/ z pustymi katalogami runtime oraz wzorcowymi plikami konfiguracji z repozytoryjnego config/.
