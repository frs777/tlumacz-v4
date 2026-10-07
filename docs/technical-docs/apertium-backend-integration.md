## Aktualny model magazynu paczek — TAR-only

Magazyn użytkownika $HOME/.config/tlumacz/apertium/ przechowuje wyłącznie paczki .tar oraz ich zewnętrzne pliki .tar.sha256. Aplikacja nie tworzy trwałej kopii rozpakowanej. Podczas inicjalizacji runtime weryfikuje archiwa i materializuje ich zawartość w tymczasowym katalogu roboczym poza magazynem; ścieżka tego katalogu jest przekazywana do Apertium jako APERTIUM_DATADIR/-d.

---
id: apertium-backend-integration
status: active
meta:
  contentType: Guide
  category: technical
version: 0.3.0
updated: 2026-10-06
owner: translation-backend
source:
  - src/tlumacz/backends/apertium/
  - src/tlumacz/application/
  - src/tlumacz/filter_engine/
  - src/tlumacz/qml_gui/
depends_on:
  - docs/ARCHITECTURE.md
  - docs/technical-docs/functional-capabilities.md
  - docs/STATUS.md
expires_when: zmiana kontraktu backendu Apertium albo aktywnego pipeline'u dokumentowego
last_validation: "inspekcja kodu SentinelX 2026-10-04; pytest 268 passed"
---

# Integracja backendu Apertium — V4

## 1. Aktualny kontrakt

Apertium jest aktywnym backendem V4. Jest niezależny od Qt i Cloud oraz nie jest zarządzanym serwerem llama.cpp.

Aktywna ścieżka ma postać:

QmlApplicationBridge → TranslationApp / BackendService → backend Apertium → Filter Engine → wynik dokumentu.

Backend tłumaczy jednostki tekstowe. Rekonstrukcja dokumentu pozostaje własnością Filter Engine.

## 2. Moduły

`src/tlumacz/backends/apertium/` zawiera m.in.:

- `adapter.py` — uruchomienie i komunikacja z procesem Apertium;
- `backend.py` — kontrakt backendu aplikacyjnego;
- `bundled.py` — lokalizacja dołączonego runtime'u;
- `config.py` — konfiguracja limitów i ścieżek;
- `contract.py` — kontrakty jednostek, wyników i capabilities;
- `errors.py` — klasyfikacja błędów;
- `language_plugins.py` — obsługa danych językowych;
- `languages.py` — mapowanie i budowanie par językowych;
- `runtime.py` — discovery runtime'u i dostępnych par;
- `native_runtime/` — prywatny artefakt runtime'u.

## 3. Integracja z Filter Engine

Apertium otrzymuje jednostki z aktywnego `DocumentProcessor`/Filter Engine. Nie powinien sam parsować DOCX, ODT, HTML, EPUB ani XLIFF.

Aktywne formaty głównego rejestru to DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF 2.0. TXT i PDF nie są obecnie zarejestrowane w głównym `FilterRegistry`.

Wynik Apertium podlega tym samym granicom walidacyjnym dokumentu, w szczególności ochronie markerów i kompletności targetów.

## 4. Runtime i discovery

`ApertiumRuntime` wykrywa dostępny runtime oraz pary językowe na podstawie rzeczywistych danych instalacji. Obecność źródłowych plików danych nie jest sama w sobie dowodem, że para jest gotowa do uruchomienia.

Dla prywatnego runtime'u używane są ścieżki projektu/konfiguracji przewidziane przez `bundled.py` i `runtime.py`. Konkretny katalog danych może być wskazany przez konfigurację runtime'u.

Apertium uruchamia proces dla żądania i nie jest objęty lifecycle'em llama.cpp. GUI nie powinno pokazywać dla Apertium operacji start/stop/restart właściwych dla zarządzanego llama.cpp.

## 5. Języki

Mapowanie języków odbywa się przez `languages.py` i `language_plugins.py`. Discovery uznaje za dostępne wyłącznie kierunki, dla których odpowiadające artefakty binarne wymagane przez `modes.xml` faktycznie istnieją. Sam wpis w `modes.xml` nie wystarcza.

`build_language_pair_index()` buduje indeks logicznie dwukierunkowy: dostępność `pol-eng` pozwala GUI rozpatrywać zarówno `pl → en`, jak i `en → pl`. To jest warstwa wyboru GUI; nie zmienia rzeczywistego kierunku wykonywanego przez Apertium.

Dla Apertium GUI korzysta z istniejącego `LanguageDetector`/Lingua. Gdy użytkownik ma ustawione automatyczne źródło i ładuje tekstowy dokument, bridge wykrywa język, ogranicza go do kodów obsługiwanych przez Apertium i ustawia wykryty kod jako bieżące źródło. Dla formatów binarnych lub gdy detekcja nie daje kodu obsługiwanego przez Apertium pozostaje ręczny wybór źródła.

Lista celów jest zawsze wyliczana względem bieżącego źródła. Przy zmianie źródła niezgodny cel jest zerowany. Jeżeli dla źródła nie ma gotowej pary, GUI pokazuje `brak pary` i blokuje ComboBox. Bridge dodatkowo odrzuca próbę rozpoczęcia tłumaczenia z nieprawidłowym źródłem lub celem.

## 6. Integracja z GUI

`ApiPage.qml` udostępnia osobną powierzchnię Apertium:

- źródło: `bridge.apertiumSourceLanguages`;
- cel: `bridge.apertiumTargetLanguages`;
- etykieta celu: `bridge.apertiumTargetLanguageLabel`;
- stan aktywności celu: `bridge.apertiumTargetSelectionEnabled`;
- wykryte źródło: `bridge.detectedSourceLanguage`.

Bridge i runtime domyślnie korzystają z magazynu paczek użytkownika
$HOME/.config/tlumacz/apertium/. Bundlowany native_runtime/ zawiera wyłącznie
wykonywalny runtime Apertium; pary językowe są dystrybuowane jako niezależne
archiwa .tar zgodne z docs/technical-docs/paczki-jezykowe-specyfikacja.md.

Przed discovery aplikacja weryfikuje zewnętrzny .tar.sha256 i instaluje
brakujące archiwa do magazynu użytkownika. Testy i kontrolowane scenariusze
mogą nadal przekazać data_dir jawnie.

QML pozostaje warstwą prezentacji. Indeksowanie par, walidacja kierunku i wybór dostępnych celów są realizowane po stronie Python/domain.



## 7. Bramka gotowości runtime

Discovery nie uznaje pary za gotową wyłącznie na podstawie obecności plików danych i wpisu w `modes.xml`. Dla każdego trybu sprawdzane są również programy wymienione w elementach `program`.

Kontrakt gotowej pary jest następujący:

1. wymagane pliki danych istnieją;
2. wymagany plik `.mode` istnieje;
3. wszystkie programy pipeline'u są dostępne w prywatnym `native_runtime/bin/` albo w systemowym `PATH`;
4. smoke wykonawczy nie ujawnia awarii procesu ani pustego wyniku dla deklarowanej pary;
5. do publicznego indeksu trafiają wyłącznie nazwy odpowiadające rzeczywistemu kierunkowi `source-target`, a nie tryby pomocnicze.

ApertiumRuntime.language_pairs() korzysta z tego samego filtra co GUI discovery. Dzięki temu adapter nie może zaakceptować trybu pomocniczego ani pary, dla której runtime nie posiada wymaganych narzędzi.

### Stan 2026-10-06

Z 28 przygotowanych paczek:

- **27 READY** — po uzupełnieniu prywatnego runtime o `cg-proc`, `libcg3.so.1`, `lsx-proc`, `apertium-anaphora` i `libsqlite3.so.0`;
- **1 EXCLUDED** — `ces-pol`.

`ces-pol` nie jest oznaczone jako READY: dostarczony model `ces-pol.prob` powoduje wewnętrzną asercję `apertium-tagger` (`PerceptronSpec::StackValue`) dla części zwykłych czeskich wejść i może zakończyć proces SIGABRT. Próba retrainingu modelu nie usunęła problemu. Para pozostaje poza release scope do czasu uzyskania zgodnego modelu taggera.

Dołączenie brakujących narzędzi wykonano wyłącznie do prywatnego runtime; **nie instalowano ani nie usuwano pakietów systemowych**. Licencje GPL-3 dla CG-3 i Apertium Anaphora są obecne w `native_runtime/LICENSES/`, a źródła relokacji opisuje `native_runtime/TOOLS-ADDITIONS.md`.

## 8. Weryfikacja

Weryfikacja po domknięciu runtime/discovery z 2026-10-06:

- pełny zestaw testów Apertium: **48 passed**;
- regresje GUI: **2 passed**;
- relokowany runtime Linux x86_64: potwierdzony;
- wheel zbudowany w czystym staging-tree: **OK**; artefakt `dist/tlumacz-0.40.0-py3-none-any.whl` zawiera uzupełnione narzędzia runtime;
- aktywny katalog użytkownika `$HOME/.config/tlumacz/apertium`: **6 rzeczywistych par** widocznych po filtrze;
- runtime nie zwraca trybów pomocniczych jako par językowych.

Bezpośredni build w istniejącym drzewie nadal może zatrzymać się na ACL starego artefaktu Okapi; nie zmieniano jego właściciela ani uprawnień. Staging-tree jest oficjalnym obejściem tego niezależnego problemu packagingowego.




Weryfikacja po zmianie discovery/runtime z 2026-10-06:

- pełny zestaw testów Apertium: **48 passed**;
- focused discovery/runtime: **13 passed**;
- relokowany runtime Linux x86_64 z PATH=/nonexistent: Apertium 3.9.12 działa;
- pełny smoke 28 paczek: procesy kończą się kodem 0, ale jakościowy gate danych i zależności potwierdza **17 READY / 11 BLOCKED**;
- bundlowane native_runtime/share/apertium: 27 gotowych kierunków;
- smoke bundlowanego runtime'u: 27 READY / 0 FAIL;
- runtime nie zwraca trybów pomocniczych jako par językowych;
- PATH=/nonexistent nie uniemożliwia uruchomienia prywatnego runtime'u.
- runtime nie zwraca już trybów pomocniczych jako par językowych.

Próba budowy wheel zatrzymała się na istniejącym artefakcie Okapi: setuptools zgłosił Operation not permitted dla src/tlumacz/resources/okapi-runtime/okapi-core-1.49.0-SNAPSHOT.jar. Problem nie dotyczy warstwy Apertium i nie został naprawiany w ramach tego planu.


## 9. Docelowe drzewo dystrybucyjne — stan 2026-10-07

Tłumacz
└── src/tlumacz/backends/apertium/
    └── native_runtime/
        ├── bin/apertium
        ├── bin/apertium-*
        ├── lib/
        ├── libexec/
        └── share/apertium/
            ├── modes/
            └── apertium-<para>/

Runtime wykonywalny i dane par są rozdzielone. Adapter korzysta z prywatnego
native_runtime/bin/apertium, natomiast dane kierunków pochodzą z magazynu
$HOME/.config/tlumacz/apertium/, w którym przechowywane są oryginalne artefakty
.tar oraz ich zweryfikowane instalacje. Dzięki temu dodanie jednego kierunku
nie wymaga dostarczania całego zestawu Apertium.

Katalog `Aperitium/` jest magazynem developerskim i nie jest potrzebny do normalnego uruchamiania bundlowanego backendu. Audyt 2026-10-07 potwierdził brak odwołań do `Aperitium/` w aktywnym `src/`. Dwie zależności developerskie pozostają poza `src`: `tools/apertium/package_pairs.py` używa `Aperitium/` jako katalogu źródłowego, a `tests/test_apertium_pair_repairs.py` korzysta z pliku źródłowego z tego drzewa. Usunięcie katalogu jest więc możliwe dopiero po przeniesieniu/zmianie tych dwóch zależności oraz wykonaniu testów i audytu końcowego. Zawartość `Aperitium/` obejmuje źródła, pliki konfiguracji/build oraz skompilowane artefakty; nie należy traktować jej jako części `native_runtime`.
