---
id: plan-migracji-v4
status: historical
meta:
  contentType: MigrationPlan
  category: plans
version: 0.40.0
updated: 2026-09-30
owner: platform-architecture
source:
  - docs/INDEX.md
  - docs/audits/audyt-2026-09-30.md
  - docs/PLAN_MODULARIZACJI_BACKENDOW_2026-09-26.md
  - docs/ARCHITEKTURA_WLASNEGO_SILNIKA_FILTROW_V4_2026-09-26.md
  - docs/MIGRACJA_CHAT_V4_2026-09-26.md
  - docs/plans/2026-09-29-python-filter-engine.md
  - docs/technical-docs/apertium-backend-integration.md
  - docs/RESEARCH_MECHANIZM_OKAPI_2026-09-25.md
  - docs/wdrozenia/PLAN_OKAPI_2026-09-23.md
  - docs/STATUS.md
  - docs/TODO.md
  - docs/BUG.md
depends_on: [docs/AGENTS.md, docs/INDEX.md]
expires_when: zakończenie migracji V3 → V4 albo zastąpienie planu zaakceptowanym ADR-em
---

# STATUS DOKUMENTU: HISTORYCZNY PLAN MIGRACJI

> Migracja V3 → V4 została wykonana. Ten plik zachowuje plan i decyzje historyczne; nie należy traktować go jako bieżącej instrukcji implementacyjnej. Aktualny stan projektu opisuje `docs/STATUS.md`, a aktywną architekturę `docs/ARCHITECTURE.md`. FastAPI/OpenVINO pozostają wycofane.

# PLAN MIGRACJI V3 → V4

## 1. Cel i zakres

Migracja odbywa się do:

`/home/frs/Projekty/tlumacz-v4/`

V3:

`/home/frs/Projekty/agent-translator-v3/`

pozostaje **nienaruszony**. V4 powstaje jako niezależny projekt. Nie wykonujemy migracji „w miejscu” i nie kopiujemy całego repozytorium.

Wersja końcowa: **0.40.0**.

Cele:
1. usunięcie wszystkich błędów wykazanych w audycie 2026-09-30;
2. usunięcie FastAPI i OpenVINO;
3. modularizacja backendów zgodnie z planem z 2026-09-26;
4. rozbicie `MainWindow` i `Translator`;
5. usunięcie regresji i legacy;
6. odchudzenie oraz optymalizacja po ustabilizowaniu architektury;
7. Apertium jako runtime dołączony do aplikacji;
8. własny Filter Engine V4 z kontrolowanym runtime'em filtrów;
9. kompletny, testowalny packaging 0.40.0.

## 2. Zasady nadrzędne

### 2.1. V3 jest źródłem referencyjnym, nie bazą do modyfikacji

- żadnych zmian w V3;
- żadnego usuwania plików V3;
- żadnego przenoszenia plików V3 przez `mv`;
- żadnego „przygotowywania” V3 pod migrację;
- żadnych nowych zależności instalowanych do V3;
- V3 pozostaje możliwy do uruchomienia i porównania.

Migracja oznacza **selektywną rekonstrukcję V4**, a nie mechaniczne kopiowanie.

### 2.2. Nie przenosimy regresji

Nie przenosić bez uzasadnienia:
- FastAPI;
- OpenVINO;
- ich managerów/workerów;
- starych ścieżek kompatybilności;
- prywatnych zależności GUI;
- martwego kodu;
- starych adapterów zastąpionych przez V4;
- niepotrzebnych singletonów.

### 2.3. Architektura

V4 pozostaje **modularnym monolitem desktopowym**.

Nie tworzymy:
- mikroserwisów;
- brokera;
- service mesha;
- osobnych repozytoriów backendów.

Osobny proces jest dopuszczalny wyłącznie dla wymaganych runtime'ów, np. Java/Okapi lub `llama-server`.

## 3. Źródła prawdy

Plan obowiązkowo korzysta z `docs/INDEX.md`.

Hierarchia:
1. niniejszy plan;
2. zaakceptowane ADR-y V4;
3. kontrakty i testy V4;
4. bieżąca dokumentacja V3;
5. audyty/research;
6. archiwum jako materiał historyczny.

`docs/archive/` nie jest automatycznie źródłem bieżących wymagań.

## 4. Ustalenia audytu, które V4 musi zamknąć

### P0 — integralność repozytorium

V3 ma lokalny kod nieśledzony przez Git, m.in.:
- `tlumacz/filter_engine/`;
- `tlumacz/backends/`;
- `java/`;
- `filtry/`;
- część testów V4.

V4 musi posiadać własny, jednoznaczny manifest źródeł. Nie wolno zakładać, że HEAD V3 jest kompletną reprezentacją funkcjonalności lokalnej.

### P0 — packaging

Obecny packaging V3/V4 nie gwarantuje runtime'u wymaganego przez aktywny Filter Engine.

V4 projektuje packaging od początku:
- jawne artefakty;
- dependency closure;
- licencje/NOTICE;
- runtime Java, jeżeli wymagany;
- Okapi;
- Apertium;
- test z czystego środowiska.

### P1 — inline codes

V4 musi naprawić:
- brak E104 po stronie Java;
- brak pełnej walidacji kolejności;
- możliwość duplikacji/braku markerów;
- BUG-013 dotyczący utraty markerów w Markdown.

Marker nie jest zwykłym tekstem. Jest częścią kontraktu strukturalnego.

### P1 — procesy

V4 nie może zabijać obcego procesu tylko dlatego, że zajmuje port.

Własność procesu musi być potwierdzona przez kombinację:
- PID;
- executable;
- command line;
- parent/process group;
- zapisany identyfikator uruchomionego procesu.

### P1 — backendy

Docelowo tylko:
- LlamaCppBackend;
- CloudBackend;
- ApertiumBackend.

Mozhi jest providerem Cloud.

### P1 — duże klasy

Nie kopiować:
- `MainWindow` jako monolitu;
- `Translator` jako monolitu;
- wielkich metod dokumentowych;
- logiki backendów do GUI.

## 5. Architektura docelowa

```text
GUI / Composition Root
        |
        v
Application / Use Cases
        |
        +-----------------------+
        |                       |
        v                       v
Document Pipeline         Translation Port
        |                       |
        v                       v
Filter Engine             Backend Registry
        |                  /       |       \
        v                 /        |        \
Filter Runtime       LlamaCpp     Cloud     Apertium
        |
        +--> Python filters
        |
        +--> Java Filter Host -> Okapi
```

Docelowe katalogi:

```text
agent-translator-v4/
├── docs/
├── tlumacz/
│   ├── application/
│   │   ├── ports/
│   │   ├── services/
│   │   ├── registry/
│   │   └── errors/
│   ├── backends/
│   │   ├── contract.py
│   │   ├── llama_cpp/
│   │   ├── cloud/
│   │   │   └── providers/mozhi.py
│   │   └── apertium/
│   ├── filter_engine/
│   │   ├── contract.py
│   │   ├── registry.py
│   │   ├── processor.py
│   │   ├── workspace.py
│   │   ├── lifecycle.py
│   │   ├── validation.py
│   │   └── filters/
│   ├── documents/
│   ├── translation/
│   ├── infrastructure/
│   └── qt_gui/
├── java/filter-host/
├── filtry/runtime/
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   ├── regression/
│   └── e2e/
└── packaging/
```

## 6. Kontrakty aplikacyjne

### 6.1. Composition Root

`main.py` odpowiada wyłącznie za:
- zbudowanie konfiguracji;
- utworzenie rejestru;
- złożenie backendów;
- złożenie Filter Engine;
- utworzenie usług aplikacyjnych;
- lifecycle aplikacji;
- uruchomienie GUI.

`main.py` nie może:
- wykonywać HTTP;
- znać szczegółów Mozhi;
- znać CLI Apertium;
- znać API Okapi;
- implementować retry backendów;
- parsować dokumentów;
- implementować logiki tłumaczenia.

### 6.2. TranslationBackend

Minimalny kontrakt:

```text
capabilities()
supported_language_pairs()
health_check()
translate_units(units, context, cancellation)
close()
```

Kontrakt nie zależy od Qt, Okapi, OpenAI SDK ani formatu dokumentu.

Wynik identyfikuje:
- backend;
- status;
- wynik jednostek;
- ostrzeżenia;
- metadane diagnostyczne;
- wersję runtime'u, jeśli dostępna.

### 6.3. Filter Engine

Engine odpowiada za:
1. probe;
2. sesję;
3. workspace;
4. timeout;
5. cancellation;
6. extract;
7. przekazanie targetów;
8. write;
9. validation;
10. close.

Filter odpowiada za szczegóły formatu.

Minimalny `FilterContract`:

```text
probe(input)
open(input, session)
extract(session)
apply_targets(session, targets)
write(session, output)
validate(session, output)
close(session)
capabilities()
```

### 6.4. DocumentContract

Jednostka zawiera co najmniej:
- stabilne ID;
- source;
- target;
- język źródłowy/docelowy;
- kolejność;
- inline codes;
- lokalizację;
- translatability;
- source hash;
- session ID.

## 7. Inline codes — kontrakt krytyczny

Nie wolno traktować markerów jako zwykłego tekstu.

Walidator musi wykrywać:
- brak kodu;
- nadmiar kodu;
- duplikat;
- zmianę kolejności;
- zmianę typu;
- nieprawidłowe zagnieżdżenie;
- marker zmieniony przez backend;
- E101;
- E102;
- E103;
- E104.

Obowiązkowe regresje:
1. pojedynczy marker;
2. wiele markerów;
3. zagnieżdżenie;
4. brak;
5. duplikat;
6. zamiana kolejności;
7. marker zmodyfikowany;
8. marker usunięty;
9. tekst przed/po;
10. marker na początku/końcu;
11. pusty segment;
12. Unicode;
13. Markdown backticks/inline code.

BUG-013 musi być odtworzony w V4 i rozbity na etapy:

```text
source
→ detected codes
→ masked
→ request
→ raw response
→ marker count
→ restore
```

Nie uznawać problemu za zamknięty bez dowodu, na którym etapie marker jest tracony.

## 8. Backendy

### 8.1. LlamaCppBackend

Moduł zawiera:
- klienta transportowego;
- runtime/server manager;
- konfigurację;
- health-check;
- timeout;
- cancellation;
- process ownership;
- cleanup.

Własność procesu potwierdzać przez PID + executable + command line + parent/process group/session.

Port zajęty przez obcy proces nie może prowadzić do `SIGTERM/SIGKILL`.

### 8.2. CloudBackend

Cloud jest routerem/provider layer.

Odpowiada za:
- profile;
- wybór providera;
- timeouty;
- limity;
- klasyfikację błędów;
- izolację sekretów;
- jawny brak automatycznego fallbacku do innego providera.

GUI nie może korzystać z prywatnego `_backend_manager._config`.

### 8.3. Mozhi

Mozhi pozostaje providerem wewnątrz Cloud.

Discovery, health-check, normalizacja kodów i błędy należą do Cloud/provider layer.

### 8.4. Apertium

Docelowo:

```text
ApertiumConfig
ApertiumRuntime
ApertiumAdapter
ApertiumBackend
```

Wymagania:
- subprocess bez `shell=True`;
- timeout;
- cancellation;
- discovery runtime;
- discovery par;
- kontrola executable;
- zachowanie unit ID;
- zachowanie markerów;
- kontrolowane błędy.

Runtime Apertium jest częścią dystrybucji V4, jeżeli przejdzie dependency/licensing inventory. Dane językowe pozostają osobnymi pakietami/wtyczkami.

Dla każdej pary należy zweryfikować:
- `apertium`;
- `lt-proc`;
- `cg-proc`/`vislcg3`, jeśli wymagane;
- `hfst-proc`, jeśli wymagane;
- mono-dictionary;
- pair data;
- modes;
- ABI;
- prefix;
- licencję.

## 9. Usunięcie FastAPI i OpenVINO

Nie migrujemy ich do V4.

Usunąć po przejęciu wymaganych funkcji:
- klasy;
- managerów;
- workerów;
- konfigurację;
- registry;
- GUI;
- testy;
- zależności;
- importy;
- feature flags;
- dokumentację aktywną.

Wykonać zero-reference scan dla:
`fastapi`, `FastAPIServerManager`, `fastapi_server`, `openvino`, `openvino_backend`, `TranslateGemma INT8`.

Po zakończeniu nie mogą istnieć aktywne referencje.

## 10. Rozbicie Translator

Nie kopiować monolitycznego `Translator`.

Wydzielić:
- `TranslationOrchestrator`;
- `ChunkPlanner`;
- `TranslationExecutor`;
- `TranslationCache`;
- `PromptBuilder`;
- `LanguageResolver`;
- `TranslationResultValidator`;
- `BackendSelectionService`;
- `DocumentTranslationService`.

Translator/Orchestrator nie może jednocześnie zarządzać PDF, XML, backendami, promptami, cache i procesami.

## 11. Rozbicie MainWindow

`MainWindow` pozostaje UI boundary.

Wydzielić:
- `TranslationController`;
- `BackendController`;
- `DocumentController`;
- `SettingsController`;
- `ProgressController`;
- `DiagnosticsController`;
- `WindowStateController`.

GUI komunikuje się przez publiczne kontrakty. Zakaz bezpośredniego dostępu do prywatnego stanu managerów.

## 12. Warstwa dokumentowa

Docelowo:

```text
DocumentService
      |
      v
FilterEngine
      |
      +-- Markdown
      +-- HTML/XHTML
      +-- OpenXML/DOCX
      +-- OpenOffice/ODT
      +-- EPUB
      +-- XLIFF
```

PDF pozostaje osobnym pipeline'em, zgodnie z dokumentacją V3.

Backend tłumaczeniowy nie może wiedzieć, czy tekst pochodzi z DOCX, ODT, EPUB czy Markdown.

## 13. Okapi / Java Filter Host

### 13.1. Zasada

Użytkownik V4 nie instaluje ani nie konfiguruje Okapi/Tikal.

Jeżeli filtr wymaga JVM/Okapi, runtime musi być częścią kontrolowanej dystrybucji.

### 13.2. Wersja

Research potwierdza lokalne Okapi 1.48.0 oraz kompilowalne źródła 1.49.0-SNAPSHOT. Nie wolno mieszać tych artefaktów.

Przed release wybieramy jedną wersję i zamykamy dependency closure.

### 13.3. Kolejność filtrów

1. DOCX/OpenXML;
2. ODT/OpenOffice;
3. HTML/XHTML;
4. Markdown;
5. EPUB;
6. pozostałe tylko po wykazaniu potrzeby.

EPUB nie jest uznawany za gotowy tylko na podstawie obecności źródła filtra.

### 13.4. Proces Java

Preferowany wariant V4: osobny Filter Host.

Powody:
- izolacja JVM;
- prostsze cancellation;
- prostszy lifecycle;
- brak natywnego sprzężenia JPype1.

JPype1 pozostaje wariantem odroczonym do osobnego prototypu.

### 13.5. Protokół

Wersjonowany JSON Lines:

```text
protocol_version
request_id
operation
payload
```

Operacje:
- capabilities;
- probe;
- open;
- extract;
- apply_targets;
- write;
- validate;
- cancel;
- close.

Dane plikowe pozostają w kontrolowanym workspace, zamiast być przenoszone jako wielkie komunikaty JSON.

## 14. Packaging

Packaging V4 projektujemy od zera.

Artefakt musi zawierać wszystkie runtime'y wymagane przez aktywną funkcję:
- Python package;
- backendy;
- Filter Engine;
- Java Host;
- JAR-y;
- wymagane JRE/runtime;
- Apertium runtime;
- dane;
- licencje/NOTICE.

Dla każdego filtra powstaje dependency closure:
- entrypoint;
- JAR;
- zależności tranzytywne;
- rozmiar;
- licencja;
- runtime.

Nie wybierać JAR-ów ręcznie po nazwach.

Każdy release artefact przechodzi test:
`build → clean install/extract → runtime discovery → document smoke test → backend smoke test`.

## 15. Konfiguracja V3 → V4

Nie kopiować konfiguracji V3 jako obiektu wewnętrznego.

Wprowadzić:
`V3 config → ConfigMigration → V4 Config`.

Migracja:
- wykrywa wersję;
- waliduje pola;
- ignoruje FastAPI/OpenVINO;
- zachowuje profile Cloud;
- zachowuje llama;
- zachowuje Apertium;
- nie ujawnia sekretów;
- tworzy backup konfiguracji;
- jest idempotentna.

## 16. Testy

Warstwy:

### Unit
Kontrakty, walidacja, registry, konfiguracja, markery, chunking, cache, błędy.

### Contract
Każdy backend:
- capabilities;
- języki;
- normal input;
- empty input;
- timeout;
- cancellation;
- controlled error;
- incomplete result.

### Integration
Filter Engine, Java Host, Apertium, llama-server, Cloud.

### E2E
Każdy aktywny format + reprezentatywny backend.

### Windows
Testy platform-independent oraz osobne testy runtime Windows. Nie używać założeń typu `/usr/share/java` ani `run.sh`.

## 17. Bezpieczeństwo

Dokumenty są niezaufanym wejściem.

Wymagane:
- workspace per job;
- ograniczenie ścieżek;
- timeout;
- limity rozmiaru;
- ZIP Slip protection;
- ochrona przed bombami dekompresyjnymi;
- brak wykonywania makr;
- bezpieczny zapis;
- cleanup.

Sekrety nie mogą trafić do:
- config.json;
- logów;
- test fixtures;
- dokumentacji;
- promptów;
- artefaktów diagnostycznych.

## 18. Optymalizacja

Optymalizację wykonujemy po stabilizacji architektury.

Kolejność:
1. usunięcie martwego kodu;
2. usunięcie FastAPI/OpenVINO;
3. usunięcie duplikacji;
4. stabilizacja kontraktów;
5. podział odpowiedzialności;
6. profilowanie;
7. optymalizacja bottlenecków.

Mierzyć:
- startup;
- extract;
- translation;
- merge;
- pamięć;
- czas backendu;
- liczba procesów;
- shutdown.

## 19. Zależności

V3 posiada cykl:
`cloud_providers ↔ simplytranslate`.

V4 musi go usunąć:

```text
CloudBackend
    ↓
CloudRouter
    ↓
Provider interfaces
    ↓
MozhiProvider / inni providerzy
```

Provider nie importuje nadrzędnego routera.

## 20. Fazy wykonawcze

### Faza 0 — baseline V3

- [ ] skatalogować produkcyjne pliki V3;
- [ ] skatalogować nieśledzone obszary;
- [ ] skatalogować aktywne entrypointy;
- [ ] skatalogować runtime'y;
- [ ] skatalogować testy;
- [ ] ustalić referencyjną wersję;
- [ ] ustalić baseline testów możliwych bez instalowania nowych zależności.

**Kryterium:** istnieje tabela „źródło V3 → decyzja V4”.

### Faza 1 — bootstrap V4

- [x] utworzyć strukturę katalogów;
- [x] utworzyć nowe `pyproject.toml`;
- [x] ustalić wersję 0.40.0;
- [x] utworzyć entrypoint;
- [x] utworzyć pakiety;
- [x] skonfigurować test runner;
- [x] skonfigurować quality gates;
- [x] utworzyć dokumentację V4.

**Kryterium:** V4 uruchamia się bez importowania V3.

### Faza 2 — kontrakty

- [x] TranslationBackend;
- [x] BackendResult;
- [x] FilterContract;
- [x] DocumentContract;
- [x] InlineCode;
- [x] błędy domenowe;
- [x] cancellation;
- [x] health-check;
- [x] workspace/session.

**Kryterium:** kontrakty mają testy i nie zależą od Qt ani konkretnego providera.

### Faza 3 — Filter Engine


- [x] registry;
- [x] processor;
- [x] workspace;
- [x] lifecycle;
- [x] validator;
- [x] marker validator;
- [x] Filter Host;
- [x] protokół;
- [x] DOCX;
- [x] round-trip.

**Kryterium:** DOCX przechodzi extract → translate stub → merge bez utraty struktury.

### Faza 4 — LlamaCppBackend

- [x] adapter;
- [x] runtime manager;
- [x] process ownership;
- [x] timeout;
- [x] cancellation;
- [x] health-check;
- [x] contract suite;
- [x] E2E.

**Kryterium:** llama.cpp działa bez kodu backendowego w `main.py`.

### Faza 5 — Cloud

- [x] CloudRouter;
- [x] provider interface;
- [x] profile migration;
- [x] Mozhi;
- [x] timeouty;
- [x] klasyfikacja błędów;
- [x] izolacja sekretów;
- [x] contract tests.

**Kryterium:** dodanie providera nie wymaga zmiany `main.py`.

### Faza 6 — Apertium

- [x] runtime;
- [x] adapter;
- [x] backend;
- [x] language plugins;
- [x] dependency inventory;
- [x] licencje;
- [x] contract tests;
- [x] E2E HTML/DOCX;



### Faza 7 — Document Services

Kolejność:
1. DOCX — [x];
2. ODT — [x];
3. HTML/XHTML — [x];
4. Markdown — [x];
5. EPUB — [x];
6. XLIFF — [x];
7. pozostałe formaty tylko po wykazaniu potrzeby — brak dodatkowej potrzeby na tym etapie.

Każdy format musi mieć:
- adapter;
- corpus;
- round-trip;
- fingerprint/structural validation;
- test błędnego inputu;
- cancellation test;
- Unicode test.

PDF pozostaje niezależny.

### Faza 8 — Translator

- [x] ChunkPlanner;
- [x] PromptBuilder;
- [x] TranslationExecutor;
- [x] TranslationCache;
- [x] ResultValidator;
- [x] TranslationOrchestrator;
- [x] DocumentTranslationService;

**Kryterium:** brak pojedynczej metody obsługującej kilka niezależnych domen.

### Faza 9 — GUI

- [x] TranslationController;
- [x] BackendController;
- [x] SettingsController;
- [x] DocumentController;
- [x] ProgressController;
- [x] DiagnosticsController;
- [x] usunięcie prywatnych zależności;
- [x] testy kontraktowe warstwy GUI.

**Kryterium:** GUI nie zna szczegółów providerów.

### Faza 10 — legacy removal

Dopiero po przejęciu funkcji i przejściu testów:
- [x] brak FastAPI;
- [x] brak OpenVINO;
- [x] brak ich konfiguracji;
- [x] brak ich testów;
- [x] brak importów;
- [x] brak zależności;
- [x] brak feature flags;
- [x] brak zastąpionych ścieżek dokumentowych.

**Kryterium:** brak aktywnych referencji do usuniętych technologii w kodzie, testach i konfiguracji V4.

### Faza 11 — packaging

- [ ] dependency closure;
- [ ] licencje;
- [x] NOTICE;
- [x] Java runtime;
- [x] Okapi;
- [ ] Apertium;
- [x] Python package;
- [x] Linux;
- [ ] Windows;
- [x] clean environment;
- [x] smoke test artefaktu;

**Kryterium:** artefakt V4 działa bez drzewa źródłowego V3 i bez lokalnych zasobów deweloperskich.

**Stan 2026-09-30:** wheel `tlumacz-0.40.0-py3-none-any.whl` został zbudowany i zweryfikowany w clean venv. Okapi, Java Filter Host, NOTICE oraz bundlowany runtime Apertium są zawarte w artefakcie. Pozostają: kompletna para Apertium `eng-pol`, Windowsowy runtime natywny oraz pełne zamknięcie dependency/licencji. Kryterium Fazy 11 nie jest jeszcze spełnione.

### Faza 12 — release 0.40.0

- [x] pełny suite — 182 passed;
- [x] compile — compileall PASS;
- [x] static analysis — Ruff PASS, mypy PASS;
- [x] contract suite;
- [x] integration — 19 testów;
- [x] E2E;
- [ ] Windows;
- [ ] packaging — pozostaje otwarte przez blokady Fazy 11;
- [x] dokumentacja;
- [x] CHANGELOG;
- [x] migration notes;
- [x] clean install — Linux, bez zależności, PASS;
- [x] rollback procedure.

Stan 2026-09-30: przygotowano release candidate 0.40.0 dla Linux. Artefakt wheel został zweryfikowany w clean venv. Faza 12 pozostaje otwarta przez wymagania Windows oraz niedomknięte packaging/dependency/licencje z Fazy 11.

Słownik: nie jest blockerem release. Jest osobnym, niewbudowanym zasobem i może zostać dodany później.


Nigdy nie usuwać implementacji przed przejęciem funkcji.

```text
nowy kontrakt
    ↓
nowa implementacja
    ↓
test kontraktowy
    ↓
E2E
    ↓
przejęcie entrypointu
    ↓
usunięcie callerów legacy
    ↓
usunięcie implementacji legacy
    ↓
usunięcie testów legacy
    ↓
usunięcie zależności
    ↓
zero-reference scan
```

## 22. Rollback

Głównym rollbackiem całej migracji jest **pozostawiony, nienaruszony V3**.

Dla modułu V4 rollback oznacza wycofanie niedokończonej zmiany w V4, nie kopiowanie jej z powrotem do V3.

Nie wolno:
- mieszać katalogów V3/V4;
- nadpisywać V3 kodem V4;
- przywracać V3 przez częściowe kopiowanie.

Konfiguracja użytkownika ma własny rollback przez backup wykonywany przed migracją.

## 23. Kryteria ukończenia

### Architektura
- [ ] modularny monolit;
- [ ] main.py jest composition root;
- [ ] backendy są niezależnymi modułami;
- [ ] Filter Engine jest niezależny od backendów;
- [ ] dokumenty są niezależne od providerów;
- [ ] brak cyklu providerów.

### Backendy
- [ ] LlamaCpp działa;
- [ ] Cloud działa;
- [ ] Mozhi jest providerem Cloud;
- [ ] Apertium działa;
- [ ] FastAPI nie istnieje w aktywnym kodzie;
- [ ] OpenVINO nie istnieje w aktywnym kodzie.

### Dokumenty
- [x] DOCX;
- [ ] ODT;
- [ ] HTML/XHTML;
- [ ] Markdown;
- [ ] EPUB po osobnym POC/runtime verification;
- [ ] PDF przez przetestowaną niezależną ścieżkę;
- [x] round-trip;
- [ ] inline validation.

### Bezpieczeństwo
- [ ] brak możliwości zabicia obcego procesu;
- [ ] workspace isolation;
- [ ] timeout/cancel;
- [ ] bezpieczny subprocess;
- [ ] sekrety poza logami;
- [ ] brak shell injection.

### Jakość
- [ ] brak krytycznych F821;
- [ ] pełny suite;
- [ ] regression suite;
- [ ] Windows suite;
- [ ] clean-install test.

### Packaging
- [ ] runtime kompletne;
- [ ] dependency closure;
- [ ] licencje;
- [ ] samowystarczalny artefakt;
- [ ] wersja 0.40.0.

### Dokumentacja
- [ ] V4 INDEX;
- [ ] STATUS;
- [ ] architektura;
- [ ] backend docs;
- [ ] Filter Engine docs;
- [ ] packaging docs;
- [ ] migration notes;
- [ ] CHANGELOG.

## 24. Zakres wyłączony

Nie wykonujemy w tej migracji:
- mikroserwisów;
- migracji aplikacji do Flyte;
- wdrożenia chmurowego desktopu;
- automatycznego fallbacku providerów;
- przebudowy PDF do Filter Engine bez osobnej decyzji;
- dodawania JPype1 bez prototypu;
- instalowania Apertium podczas działania aplikacji;
- instalowania zależności systemowych do V3;
- przepisywania Okapi;
- kopiowania całego V3 do V4.

Flyte nie jest częścią runtime'u Tłumacz V4. Może być rozważony później wyłącznie dla niezależnych zadań benchmarkowych/orkiestracyjnych.

## 25. ADR-y wymagane

Przed implementacją odpowiednich elementów należy utworzyć ADR dla:
1. modularnego monolitu;
2. TranslationBackend;
3. Filter Engine;
4. Java Filter Host vs embedded JVM;
5. wersji Okapi;
6. packagingu runtime;
7. Apertium runtime + language plugins;
8. usunięcia FastAPI/OpenVINO;
9. migracji konfiguracji V3 → V4;
10. release 0.40.0.

## 26. Quality gates

Każdy etap kończy się:

```text
unit tests
→ contract tests
→ integration tests
→ regression tests
→ static analysis
→ diff review
→ documentation update
```

Duże zmiany w V4 wymagają backupu artefaktów roboczych. V3 nie jest modyfikowany.

## 27. Dokumentacja

Po każdej zakończonej fazie aktualizować:
- `docs/STATUS.md`;
- `docs/TODO.md`;
- `docs/BUG.md`, gdy zmienia się status defektu;
- `docs/CHANGELOG.md`;
- dokument techniczny właściwy dla zmiany;
- `docs/INDEX.md` i `docs/INDEX.yml`, gdy zmienia się struktura.

Nie uznawać implementacji za ukończoną bez aktualizacji dokumentacji.

## 28. Definition of Done modułu

Moduł jest gotowy, gdy:
1. ma jedną główną odpowiedzialność;
2. ma publiczny kontrakt;
3. nie zależy od prywatnego stanu innego modułu;
4. ma unit tests;
5. ma contract test, jeśli implementuje port;
6. ma integration test, jeśli używa procesu/zewnętrznego systemu;
7. ma timeout/cancel, jeśli operacja jest długotrwała;
8. ma dokumentację;
9. nie tworzy cyklu zależności;
10. nie pozostawia martwego kodu.

## 29. Matryca migracji

| V3 | V4 | Decyzja |
|---|---|---|
| main.py | composition root | przebudować |
| MainWindow | controllers + UI | rozbić |
| Translator | application services | rozbić |
| BackendManager | BackendRegistry + backends | zastąpić |
| llama.cpp | backends/llama_cpp | migrować |
| Cloud | backends/cloud | migrować |
| Mozhi | cloud/providers/mozhi.py | migrować |
| Apertium | backends/apertium | migrować |
| FastAPI | brak | usunąć |
| OpenVINO | brak | usunąć |
| Filter Engine | filter_engine | odbudować/zweryfikować |
| Java Host | java/filter-host | migrować po kontrakcie |
| Okapi runtime | filtry/runtime | dependency closure |
| Markdown | Filter | migrować |
| HTML | Filter | migrować |
| DOCX | OpenXML Filter | migrować |
| ODT | OpenOffice Filter | migrować |
| EPUB | Filter/Python filter | zweryfikować |
| PDF | osobny pipeline | zachować i odchudzić |
| konfiguracja | ConfigMigration | migrować |
| packaging | V4 packaging | zaprojektować od zera |
| testy | unit/contract/integration/e2e | selektywnie migrować + rozszerzyć |
| docs | V4 docs | przepisać jako aktualną dokumentację |

## 30. Ryzyka i zabezpieczenia

| Ryzyko | Skutek | Zabezpieczenie |
|---|---|---|
| przeniesienie regresji | V4 dziedziczy błędy | migration inventory |
| utrata markerów | uszkodzenie formatowania | strukturalny InlineCode validator |
| niedomknięty Okapi runtime | brak działania release | dependency closure + clean install |
| różnica Windows/Linux | release failure | osobne runtime adapters |
| błędna własność procesu | zabicie obcego procesu | process identity contract |
| utrata konfiguracji | reset ustawień | ConfigMigration + backup |
| zbyt duży refactor | trudny rollback | fazy + contract tests |
| pozostawienie legacy | koszt utrzymania | zero-reference gate |
| cykle zależności | trudne zmiany | dependency direction tests |
| EPUB niegotowy | niedziałający format | osobny POC |
| Apertium ABI mismatch | brak tłumaczenia | runtime/version checks |
| niespójna wersja | błędny release | jedno źródło wersji |
| ukryte zależności V3 | runtime failure | clean environment test |

## 31. Ostateczna kolejność

```text
0. V3 baseline / inventory
        ↓
1. V4 bootstrap
        ↓
2. Contracts
        ↓
3. Filter Engine + inline validation
        ↓
4. Java/Okapi host + DOCX
        ↓
5. LlamaCpp
        ↓
6. Cloud + Mozhi
        ↓
7. Apertium
        ↓
8. Document Services
        ↓
9. Translator decomposition
        ↓
10. GUI decomposition
        ↓
11. Remove FastAPI/OpenVINO
        ↓
12. Packaging / runtime closure
        ↓
13. Windows/Linux clean-install
        ↓
14. Full regression + E2E
        ↓
15. Documentation / changelog
        ↓
16. 0.40.0 release candidate
```

Nie zmieniać kolejności bez udokumentowania zależności blokującej.

## 32. Warunek rozpoczęcia implementacji

Przed pierwszą większą zmianą kodu V4 muszą istnieć:
- ten plan;
- inventory V3 → V4;
- lista kontraktów;
- lista ADR-ów;
- baseline testów;
- ustalona struktura repozytorium;
- potwierdzenie, że V3 pozostaje nietknięty.

Pierwszym etapem implementacyjnym jest **Faza 1 — bootstrap V4**, a nie poprawianie V3.

## 33. Status

**STATUS: GOTOWY DO PRZEGLĄDU UŻYTKOWNIKA**

**Wersja docelowa:** 0.40.0  
**Katalog:** `/home/frs/Projekty/tlumacz-v4/`  
**V3:** nienaruszony.

**Następny krok po akceptacji:** wykonanie baseline/inventory V3 → V4 i rozpoczęcie bootstrapu V4.


### Faza 13 — finalny handoff i freeze

- [x] stan migracji udokumentowany;
- [x] aktualny artefakt i SHA-256 udokumentowane;
- [x] otwarte blokery F11/F12 jawnie zapisane;
- [x] zasada braku publikacji do GitHub potwierdzona;
- [x] backup dokumentacji wykonany;
- [x] raport handoff utworzony.

**Kryterium:** lokalny handoff freeze jest kompletny. Nie jest to finalne oznaczenie release 0.40.0; final release pozostaje zależny od zamknięcia Apertium eng-pol, Windows oraz dependency/licencji.
