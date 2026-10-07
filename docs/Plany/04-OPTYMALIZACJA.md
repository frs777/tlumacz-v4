---
id: plan-04-optymalizacja-v4
status: closed
meta:
  contentType: ImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-04
owner: project-maintenance
source: docs/STATUS.md
depends_on: [docs/Plany/00-BASELINE-MAPA-PARYTETU-V3-V4.md, docs/Plany/01-RESTORE-BRAKUJACE-FUNKCJE.md, docs/Plany/02-REDUKCJA-NADMIAROWEGO-KODU.md, docs/Plany/03-NAPRAWA-REGRESJI.md]
expires_when: każda optymalizacja ma pomiar i zachowuje kontrakt
last_validation: "quality gate zamknięty 2026-10-04; 268 passed; Ruff/mypy/compileall/qmllint PASS"
---

# PLAN 04 — optymalizacja po odzyskaniu funkcji

## Zasada

Każda optymalizacja musi mieć:
baseline → hipoteza → pomiar → zmiana → pomiar → regresja.

Nie optymalizować intuicyjnie i nie zmieniać semantyki tłumaczenia dla benchmarku.

## 1. Pipeline tłumaczenia

Audyt wskazał do weryfikacji przepływ:
DocumentProcessor → jednostka → TranslationOrchestrator → ChunkPlanner → TranslationExecutor.

Nie klasyfikować go jako bug bez pomiaru.

Zmierz:
- liczbę inicjalizacji orchestratora;
- liczbę planów chunków;
- liczbę requestów backendu;
- cache hit/miss;
- równoległość;
- czas per dokument i per jednostka.

Dopiero na podstawie danych zaprojektować zmianę.

## 2. Llama.cpp

Zbudować baseline latency, throughput, CPU, parallel, batch, warm-up, cache i restart cost. Zmieniać jeden parametr na eksperyment. Nie mnożyć wariantów CPU bez dowodu zysku.

## 3. Cloud

Zmierz niepotrzebne inicjalizacje routera, health-checki, odczyty profili, serializację konfiguracji i rozmiary requestów. Nie dodawać automatycznego fallbacku.

## 4. Filter Engine

Zmierz extraction, marker protection, Filter Host IPC, reconstruction i validation. Sprawdź powtarzane kosztowne operacje. Nie usuwać walidacji wyłącznie dla szybkości.

## 5. QML

Zmierz startup, liczbę obiektów, koszt bindingów, odświeżanie skills, ładowanie pomocy i sygnały bridge. Nie usuwać funkcji UI w ramach optymalizacji.

## 6. Python

Po stabilizacji ograniczyć zbędne kopiowanie i powtarzalne mapowania, zachować typy i kontrakty. Każdy refaktor ma test funkcjonalny.

## Quality gate

Po każdej zmianie:
- affected unit tests;
- contract tests;
- regression tests;
- compileall;
- Ruff;
- mypy;
- benchmark.

Dla GUI dodatkowo QML smoke i qmllint, jeżeli dostępny.

## Kryterium wyjścia

Akceptacja tylko wtedy, gdy funkcja pozostaje zgodna, pomiar wykazuje poprawę lub redukcję złożoności, nie wzrasta liczba regresji, testy są zielone i istotna zmiana jest udokumentowana.
## Raport — optymalizacja DocumentTranslationService — 2026-10-04

### Hipoteza

`DocumentTranslationService.translate_file()` wywoływał `TranslationOrchestrator.translate_units()` osobno dla każdej jednostki dokumentu. Powodowało to wielokrotną inicjalizację prompt buildera, planowania chunków, executora i walidacji zamiast jednego przebiegu dokumentu.

### Baseline

Kontrolowany benchmark: 200 jednostek Markdown, `max_chars=1000`, `max_workers=1`, backend stub.

- `orchestrator_calls=200`;
- `backend_calls=200`;
- czas: **0,048947 s**.

### Zmiana

Dodano batchowy kontrakt `translate_many` do `DocumentProcessor`. `DocumentTranslationService` przekazuje wszystkie jednostki niepuste do jednego `TranslationOrchestrator.translate_units()`, a następnie zachowuje istniejącą walidację markerów, kontrolę wyników, kolejność jednostek i raportowanie postępu.

Bezpośredni kontrakt `translate(text)` pozostaje dostępny dla istniejących użytkowników `DocumentProcessor`.

### Pomiar po zmianie

Ten sam benchmark:

- `orchestrator_calls=1`;
- `backend_calls=200`;
- czas: **0,009530 s**;
- redukcja czasu w pojedynczym pomiarze: około **80,5%**;
- redukcja liczby przebiegów orchestratora: **200 → 1**.

### Weryfikacja

- testy dokumentowego pipeline'u: **34 passed**;
- pełny suite V4: **266 passed**;
- `compileall`: PASS;
- `git diff --check`: PASS.

Backup przed zmianą: `backups/plan-04-20261004/pre-document-batch-optimization.tar.gz`, SHA-256 `22051e407cb182a3aad11bb89d31605a8a6a7cded204b7aff63ac4519324118d`.

### Zakres dalszy

Nie wykonywano jeszcze optymalizacji llama.cpp, Cloud, Filter Host IPC ani QML bez osobnego baseline. Każda z nich wymaga kolejnego pomiaru zgodnie z zasadą planu.


## Raport — baseline llama.cpp / TranslateGemma — 2026-10-04

### Środowisko

- model: `/home/frs/Modele/translategemma-4b-it.Q5_K_M.gguf`;
- format/kwantyzacja: GGUF, Q5_K_M;
- rozmiar pliku: około 2,83 GB;
- CPU: 8 wątków dla `llama-server` (`-t 8 -tb 8`);
- context: 4096;
- batch: `-b 512`, ubatch: `-ub 256`;
- endpoint: lokalny `127.0.0.1:18080`;
- generowanie przez `/completion`, z ręcznie zbudowanym promptem TranslateGemma;
- `--no-jinja`: modelowy chat template wymaga typowanego contentu i przy automatycznej inicjalizacji parsera llama.cpp zgłasza błąd; ścieżka `/completion` nie wymaga tego parsera.

### Warm-up / pojedynczy request

Kontrolowany request: 61 tokenów promptu, 25 tokenów generowanych.

- warm-up: **4,883 s**;
- prompt: **37,79 tok/s**;
- generacja: **7,36 tok/s**.

### Sekwencyjny baseline — `np=1`

3 kontrolowane requesty po warm-up:

- średni czas requestu: **5,048 s**;
- min: **4,963 s**;
- max: **5,204 s**;
- średnia generacja: **7,12 tok/s**.

### Równoległość — `np=4`

4 requesty równolegle przy `-np 4`:

- czas ścienny: **10,444 s**;
- przepustowość: **0,383 request/s**;
- średnie indywidualne opóźnienie: około **10,34 s**;
- średnia generacja na request: **6,06 tok/s**;
- suma raportowanych prędkości generacji slotów: około **24,23 tok/s**.

W porównaniu z sekwencyjnym `np=1` throughput wzrósł, ale koszt pojedynczego requestu wzrósł ponad 2×. Nie ma podstaw do ustawienia `np=4` jako domyślnego parametru aplikacji.

### Cache

Dla identycznego promptu:

- bez cache: **4,563 s**, `cache_n=0`;
- cache — pierwszy request: **3,291 s**, `cache_n=53`;
- cache — drugi request: **3,285 s**, `cache_n=53`.

Cache ogranicza koszt ponownego przetwarzania promptu, ale nie zmienia istotnie kosztu generacji (~7,3 tok/s). Warto zachować możliwość korzystania z cache przez warstwę backendu.

### Restart / pamięć

- czas od uruchomienia procesu do gotowości HTTP: **~2,04 s**;
- snapshot RSS po gotowości: **~3,03 GB**;
- zużycie pamięci procesu: **~19,2%** wg `ps`.

### Wniosek optymalizacyjny

Baseline nie uzasadnia obecnie zmiany parametrów produkcyjnych. Dla lokalnego tłumaczenia na CPU najważniejszym ograniczeniem jest koszt generacji modelu, nie inicjalizacja serwera. Kolejny eksperyment powinien zmieniać tylko jeden parametr naraz i być porównany z tym baseline'em.


## Raport — baseline Cloud — 2026-10-04

### Zakres

Pomiar wykonano bez używania produkcyjnego endpointu i bez ujawniania sekretu Cloud. Transport OpenAI-compatible został skierowany do lokalnego deterministycznego serwera testowego, dzięki czemu zmierzono koszt routera, providera, serializacji i transportu bez mieszania opóźnienia sieci z kosztem aplikacji.

### Wyniki

- `CloudProviderRegistry.default()` — 100 inicjalizacji: średnio **0,00154 ms**;
- `BackendRegistry()` — 50 inicjalizacji: średnio **0,0588 ms**;
- OpenAI-compatible przez `CloudRouter` do lokalnego endpointu — 50 requestów: średnio **0,629 ms**, min **0,425 ms**, max **7,007 ms**;
- rozmiar JSON requestu dla kontrolowanego tekstu: **331 B**;
- serializowany przykładowy profil Cloud bez sekretu: **102 B**;
- `load_settings()` na rzeczywistym `settings-v4.json` (1067 B), 100 odczytów: średnio **0,0385 ms**;
- `normalized_cloud_profile()` na tym samym profilu: średnio **0,00059 ms**.

### Health-check

`BackendRegistry.health_check("cloud")` jest obecnie lokalnym `HealthCheckResult.ok("cloud")` i **nie wykonuje requestu sieciowego**. Nie ma więc kosztownego automatycznego health-checku Cloud do optymalizacji; zachowanie to należy zachować, aby health-check nie generował ukrytego ruchu sieciowego.

### Wniosek

Koszt konstrukcji routera/rejestru, odczytu profilu i lokalnej serializacji jest pomijalny względem rzeczywistego requestu sieciowego. Nie ma podstaw do optymalizacji tych ścieżek. Istotnym czynnikiem pozostaje zewnętrzne RTT/provider API, którego nie należy zastępować sztucznym fallbackiem.

Sekret Cloud pozostaje poza profilem JSON i jest przechowywany w `/home/frs/.config/tlumacz/.key` z prawami `0600`.


## Raport — baseline warstwy filtrów — 2026-10-04

### Rzeczywisty proces Java

Kontrolowany lokalny proces uruchomiony przez `java/filter-host/run.sh`.

- pierwszy request `health`: **1,609 s** — obejmuje cold-start procesu JVM/runtime;
- kolejne 20 requestów `health`: średnio **0,460 ms**, mediana **0,372 ms**, min **0,234 ms**, max **1,885 ms**;
- `capabilities`: **~358,9 ms**;
- runtime udostępnia filtry OKAPI, w tym HTML, XLIFF, EPUB, OpenOffice, OpenXML i Markdown.

Wniosek: po uruchomieniu koszt samego JSON Lines IPC jest pomijalny. Potencjalny koszt cold-startu przemawia za utrzymaniem długowiecznego procesu, co już realizuje `FilterHostClient`.

### Filter Engine: extraction → validation → reconstruction

Kontrolowany benchmark V4 na `MarkdownFilter`, 200 jednostkach tekstowych, callbacku translacji typu identity oraz pełnej walidacji markerów:

- input: **13 289 B**;
- output: **13 289 B**;
- 5 przebiegów: **0,00439–0,02139 s**;
- średnio: **0,00796 s** na dokument.

Pomiar obejmuje otwarcie sesji filtra, extraction, walidację jednostek, przetworzenie jednostek, walidację targetów i reconstruction/write. Nie wykazano powtarzalnego kosztu uzasadniającego usuwanie walidacji.

### Wniosek

Nie wprowadzono optymalizacji. Największym wyróżniającym kosztem procesu Java jest cold-start JVM; warstwa IPC po rozgrzaniu nie jest wąskim gardłem. Dokumentowy Filter Engine również nie wykazał bezpiecznej optymalizacji na kontrolowanym workloadzie.


## Raport — baseline QML — 2026-10-04

### Startup

Kontrolowany runtime `QGuiApplication` + `QQmlApplicationEngine` z `Main.qml`, `QT_QPA_PLATFORM=offscreen`.

- 5 uruchomień z wyłączonym cache QML: **0,299–0,311 s** czasu `engine.load()`, średnio około **0,303 s**;
- 5 uruchomień z cache: **0,288–0,309 s**, średnio około **0,298 s**;
- drzewo root obejmuje **1309 obiektów QObject**.

Różnica cold/warm cache jest mała na tym hostcie, więc cache QML nie jest obecnie oczywistym wąskim gardłem.

### Odświeżanie skills i lokalizacja

Po załadowaniu rzeczywistego QML:

- 100 × `refresh_skills()`: średnio **0,0715 ms**, min **0,0639 ms**, max **0,3569 ms**;
- sygnał `skillsChanged`: **100/100**;
- zmiana języka aplikacji `pl → en`: **~13,95 ms** wraz z przetworzeniem eventów Qt.

### Bindingi

Nie wykonano sztucznego liczenia bindingów przez introspekcję implementacji QML. Baseline opiera się na rzeczywistym czasie ładowania, liczbie obiektów i kosztach obserwowalnych operacji bridge. Nie ma dowodu, że redukcja liczby bindingów poprawiłaby runtime bez ryzyka regresji UI.

### Wniosek

Nie wprowadzono optymalizacji QML. Startup jest stabilny w okolicach 0,3 s, refresh skills jest pomijalny, a zmiana języka mieści się w skali pojedynczych milisekund. Brak dowodu na bezpieczną redukcję funkcji, bindingów lub sygnałów.


## Finalny quality gate i zamknięcie — 2026-10-04

### Zmiany jakościowe

W trakcie quality gate wykryto i naprawiono wyłącznie problemy statyczne, bez zmiany kontraktu funkcjonalnego:

- usunięto 3 zdublowane właściwości Python/QML w `QmlApplicationBridge` (`parallel`, `temperature`, `theme`);
- dodano jawne adnotacje typów dla pól bridge inicjalizowanych przez `_load_settings()`;
- usunięto zdublowane klucze w PL/EN/DE w `i18n.py`, zachowując wartości skuteczne używane przed zmianą;
- uporządkowano importy i formatowanie zgłoszone przez Ruff;
- dodano testy regresyjne wykrywające duplikaty właściwości i kluczy lokalizacji.

Backup przed zmianami quality gate: `backups/plan-04-20261004/quality-gate/pre-lint-fix.tar.gz`, SHA-256 `d981de654433c7759d8dd064eb333262cff0769223be1d5d8ccbe9486dd64878`.

### Końcowa weryfikacja

- pytest: **268 passed**;
- compileall: **PASS**;
- Ruff: **PASS**;
- mypy: **PASS**;
- qmllint: **PASS**;
- wymagany `git diff --check`: **N/A** — katalog `/home/frs/Projekty/tlumacz-v4` nie zawiera obecnie `.git`;
- kontrola formatowania `ruff format --check` nie została użyta jako gate repozytoryjny, ponieważ wykazuje szeroki istniejący drift formatowania w dziesiątkach plików poza zakresem tej naprawy; `ruff check` pozostaje zielony;
- Cloud secret: `/home/frs/.config/tlumacz/.key`, prawa **0600**.

### Decyzja

Plan 04 zamknięty. Nie wykazano bezpiecznej optymalizacji wymagającej zmiany parametrów produkcyjnych dla llama.cpp, Cloud, Filter Engine/Host ani QML. Zachowano istniejące walidacje, kontrakty i funkcje UI.

E2E TranslateGemma z pełnym rzeczywistym przepływem aplikacji pozostaje osobnym TODO i nie jest warunkiem zamknięcia Planu 04.

## 2026-10-06 — ponowny quality gate po aktualizacji V4

Na aktualnym drzewie V4 ponowiono quality gate Planu 04. Wykryto 4 problemy statyczne i usunięto je bez zmiany kontraktu tłumaczenia:

- uporządkowano importy zgłoszone przez Ruff;
- sformatowano dwa długie fragmenty testu QML;
- doprecyzowano typowanie `TranslationOrchestrator` dla rozstrzygniętego języka źródłowego;
- doprecyzowano typowanie wyboru routingu w `TranslationApp`.

Dla ochrony zmian wykonano backupy przez bezpieczny mechanizm edycji w `backups/plan-04-20261006-lint-fix/` oraz `backups/plan-04-20261006-type-fix/`.

### Wynik

- pełny pytest: **369 passed**;
- Ruff: **PASS**;
- mypy: **PASS** — 0 błędów w 67 plikach źródłowych;
- compileall: **PASS**;
- qmllint: **PASS**.

Zmiany mają charakter jakościowo-typowy i nie zmieniają semantyki tłumaczenia. Plan 04 pozostaje zamknięty; bieżący stan quality gate jest zgodny z kryterium wyjścia.
