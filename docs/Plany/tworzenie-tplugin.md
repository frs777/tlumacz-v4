---
id: tworzenie-tplugin
status: active
meta:
  contentType: ProductionMethodology
  category: plans
version: 0.40.0
updated: 2026-10-06
owner: platform-architecture
source: docs/technical-docs/plugin-okapi-filter.md
depends_on:
  - src/tlumacz/filter_engine/
  - docs/technical-docs/plugin-okapi-filter.md
expires_when: zmiana procesu budowy pluginów TPlugin
last_validation: "metodologia zweryfikowana na 9 filtrach Okapi 2026-10-06; build_all.py i testy produkcyjne działają"
---

# Metodologia produkcyjna tworzenia .tplugin

Dokument wewnętrzny produkcyjny. Nie jest instrukcją dla użytkownika końcowego.

## 1. Cel procesu

Celem jest przekształcenie istniejącego filtra Okapi lub własnego filtra Java w powtarzalny i weryfikowalny plugin Tłumacza.

Proces musi obsługiwać:
- oficjalny filtr Okapi;
- fork;
- własną implementację;
- pojedynczy JAR;
- wiele JAR-ów;
- zależności Maven;
- zależności dostarczone lokalnie;
- biblioteki shared;
- biblioteki natywne;
- wymagania konkretnej JVM;
- zasoby poza JAR-em;
- capability systemowe.

## 2. Zasada nadrzędna

Najpierw inventory, potem klasyfikacja zależności, następnie kompilacja i dopiero na końcu pakowanie.

Nie budujemy pluginu tylko dlatego, że pojedynczy JAR uruchamia się lokalnie.

## 3. Workspace

Każdy plugin otrzymuje osobny workspace:

    work/
    └── <filter-id>/
        ├── source/
        ├── upstream/
        ├── build/
        ├── analysis/
        ├── staging/
        └── output/

Produkcja nie modyfikuje bezpośrednio magazynu runtime.

## 4. Pobranie źródła

Źródło musi być przypięte:
- release;
- tag Git;
- commit;
- Maven artifact;
- lokalny artefakt zatwierdzony przez architekta.

Zapisujemy URL, wersję, commit/tag, SHA-256 i datę.

Nie używamy "latest" jako niejawnej wersji produkcyjnej.

## 5. Identyfikacja sposobu dostawy

### Źródła Maven/Gradle

Budujemy z przypiętą wersją i generujemy runtime dependency tree.

### Gotowy JAR

Nie zakładamy samowystarczalności. Analizujemy manifest i bytecode.

### Wiele JAR-ów

Ustalamy entrypoint oraz runtime JAR-y. Testowe i build-time odrzucamy z paczki.

### Wrapper

Wrapper i właściwy filtr analizujemy osobno.

### Zasoby

Kopiujemy zasoby do "resources/" i deklarujemy ich ścieżki.

### Zależności natywne

Opisujemy je osobno według platformy.

## 6. Analiza zależności Java

Minimalny zestaw:

    jar tf filter.jar
    jdeps --recursive filter.jar

Dla Maven:

    mvn dependency:tree -Dscope=runtime

Dla Gradle:

    ./gradlew dependencies --configuration runtimeClasspath

Jeżeli narzędzie nie jest dostępne, nie instalujemy go automatycznie bez zgody. Brak narzędzia jest jawnie odnotowany.

Analiza rozróżnia JDK, Okapi, shared, bundled, test/build-only i optional.

## 7. Wykrycie wymaganych klas

Dla każdej biblioteki ustalamy rzeczywiste odwołania klas.

OpenXML jest wzorcem:

    runtime-openxml
       ↓
    com.twelvemonkeys.io.ole2.CompoundDocument
    com.twelvemonkeys.io.ole2.CorruptDocumentException
       ↓
    common-io

Sam wpis Maven nie jest wystarczającym dowodem użycia.

## 8. Klasyfikacja A/B/C

### A — bundled

Mała, nietypowa, specyficzna dla filtra.

### B — shared

Popularna, powtarzalna, bezpieczna do współdzielenia.

### C — engine

Część wspólnego kontraktu Filter Engine.

Decyzja musi być zapisana w manifestach i inventory.

## 9. Kontrola konfliktów

Budujemy macierz:

| biblioteka | plugin | wersja | SHA-256 | scope |
|---|---|---|---|---|
| common-io | openxml | X | Y | shared |

Następnie porównujemy z istniejącym shared-libs.

Przypadki:
1. brak — instalacja;
2. identyczny SHA — reuse;
3. inna wersja kompatybilna — tylko przy izolacji;
4. konflikt — blokada;
5. checksum niezgodny — blokada.

Nigdy nie wykonujemy bezwarunkowego "copy and overwrite".

## 10. Manifest

Manifest musi opisać:
- format i jego wersję;
- ID, nazwę i wersję pluginu;
- kompatybilność engine;
- filter configuration;
- rozszerzenia i MIME;
- entrypoint;
- A/B/C;
- checksumy;
- licencje;
- źródło upstream;
- wymagania JVM;
- native/system requirements.

## 11. Test izolowanego filtra

Przed pakowaniem uruchamiamy:
1. hello;
2. version;
3. health;
4. capabilities;
5. extract;
6. merge;
7. lifecycle;
8. Unicode;
9. inline codes;
10. puste jednostki;
11. powtarzające się ID;
12. dokument minimalny;
13. dokument uszkodzony;
14. dokument reprezentatywny;
15. round-trip.

## 12. Testy zależności

Celowo wykonujemy warianty:
- pełny zestaw;
- brak A;
- brak B;
- brak C;
- błędny checksum;
- brak wymaganego class;
- konflikt wersji.

Każdy wariant musi kończyć się przewidywalnym komunikatem diagnostycznym.

## 13. Budowa .tplugin

Proces:

    inventory
      ↓
    classification
      ↓
    staging
      ↓
    manifest
      ↓
    runtime
      ↓
    bundled A
      ↓
    shared B
      ↓
    resources
      ↓
    checksums
      ↓
    structural validation
      ↓
    runtime smoke
      ↓
    .tplugin

Archiwum wynikowe jest artefaktem dystrybucyjnym.

## 14. Test instalacji

Instalujemy do pustego profilu testowego i sprawdzamy:
- registry;
- plugin directory;
- shared-libs;
- brak archiwum po instalacji;
- brak duplikatu shared JAR;
- poprawny classloader;
- status USABLE.

Następnie instalujemy drugi plugin wymagający tej samej biblioteki. Oczekujemy jednej kopii fizycznej i dwóch referencji logicznych.

## 15. Update i rollback

Testujemy:
- update A→B;
- B→A;
- przerwanie instalacji;
- uszkodzony plugin;
- brak zależności;
- konflikt shared;
- rollback.

Instalacja musi być atomowa.

## 16. Skrypty wspomagające

Docelowy zestaw:

    tools/tplugin/
    ├── inspect_filter.py
    ├── dependency_inventory.py
    ├── classify.py
    ├── build.py
    ├── validate.py
    ├── install.py
    ├── audit.py
    └── README.md

Python jest preferowany dla orkiestracji. Java może dostarczać małe narzędzia analizy bytecode/classpath, ale nie powinna dublować instalatora.

## 17. Brak automatycznego pobierania przy instalacji

Instalator .tplugin nie pobiera brakujących bibliotek z Internetu.

Paczka produkcyjna musi być kompletna. Pobieranie i weryfikacja zależności należą do procesu produkcji pluginu.

## 18. Kryteria publikacji

Plugin publikujemy dopiero po:
- zamknięciu inventory;
- audycie licencji;
- zamknięciu dependency graph;
- smoke;
- round-trip;
- testach konfliktów;
- checksum;
- walidacji manifestu;
- potwierdzeniu JVM;
- zapisaniu źródła upstream.

## 19. Reguła końcowa

Nie publikujemy JAR-a "bo działa lokalnie". Publikujemy powtarzalny, opisany i zweryfikowany plugin.


## 20. Zrealizowany proces dla wszystkich aktualnych filtrów Okapi — 2026-10-06

Proces został wykonany dla dziewięciu filtrów obecnych w magazynie projektu. Zamiast ręcznie przygotowywać dziewięć paczek, zastosowano jeden inventory w tools/tplugin/build_all.py.

Etapy wykonania:

1. odczytano filter.json i rzeczywiste JAR-y każdego filtra;
2. porównano SHA-256 JAR-ów i wykryto duplikaty;
3. ustalono klasyfikację A/B/C;
4. wyodrębniono biblioteki shared do deklaracji manifestu;
5. zbudowano osobny staging każdego pluginu;
6. wygenerowano plugin.json i checksums.json;
7. zbudowano dziewięć artefaktów .tplugin;
8. zainstalowano wszystkie paczki do pustego profilu testowego;
9. potwierdzono brak archiwów .tplugin po instalacji;
10. uruchomiono FilterHost na rozpakowanych pluginach;
11. sprawdzono capabilities wszystkich dziewięciu filtrów.

Ważna zasada wynikająca z tego inventory: shared nie oznacza „wszystko co jest duże”. Biblioteka trafia do B, gdy uzasadnia to powtarzalność i możliwość bezpiecznego współdzielenia. Biblioteki specyficzne dla Markdown, w tym rodzina Flexmark, pozostają obecnie przy tym pluginie. Mogą zostać awansowane do shared-libs po pojawieniu się kolejnych pluginów, które rzeczywiście ich wymagają.

## 21. Reprodukowalny build

Jedynym punktem wejścia do budowania całego aktualnego zestawu jest:

    PYTHONPATH=src python3 tools/tplugin/build_all.py build/tplugins

Zmiana źródła JAR-a, klasyfikacji albo wersji shared musi być wykonana w inventory, a następnie ponownie przejść testy i smoke. Nie należy ręcznie modyfikować gotowych .tplugin.

## 22. Kryterium gotowości paczki

Paczka jest gotowa do przekazania do procesu publikacji, gdy:

- manifest jest poprawny;
- entrypoint istnieje;
- wszystkie JAR-y są sklasyfikowane;
- checksums.json obejmuje zawartość;
- shared dependencies mają id, wersję i ścieżkę;
- instalacja do pustego profilu kończy się sukcesem;
- brak .tplugin pozostaje w runtime;
- FilterHost potrafi załadować plugin;
- capabilities są poprawne.

Pełne testy round-trip dokumentów oraz audyt licencyjny pozostają osobnymi kryteriami publikacji i nie są zastępowane przez capability smoke.

## 23. Przypadek entrypoint będącego shared dependency

Jeżeli główny JAR filtra jest biblioteką shared, nie należy tworzyć drugiej kopii tylko po to, aby spełnić pole entrypoint. W manifeście entrypoint.jar może wskazywać lib-shared/<jar>, a ten sam plik jest deklarowany w dependencies.shared.

Builder pakuje go w lib-shared. Instalator przenosi go do centralnego shared-libs, usuwa kopię pluginową i FilterHost rozwiązuje entrypoint przez shared dependency.

Przypadek został zweryfikowany dla HTML, XLIFF 1.2 i YAML.

## 24. Zasada dystrybucji

Artefakty przeznaczone do publikacji muszą pozostać nierozpakowane. Aktualny katalog publikacyjny to dist/tplugins/.

Nie należy publikować katalogu $HOME/.config/tlumacz/filter-engine/plugins/ jako paczki dystrybucyjnej. Jest to runtime po instalacji, natomiast .tplugin jest formatem transportowym.

## Zastąpienie modelu instalacyjnego — 2026-10-07

Plan dotyczący trwałego runtime `$HOME/.config/tlumacz/filter-engine/plugins/`, centralnego `shared-libs/` oraz publikacji do `dist/tplugins/` jest historyczny i został zastąpiony prostszym kontraktem:

- trwałe pakiety: `/home/frs/.config/tlumacz/filters/`;
- rozpakowanie: `/tmp/filters/` tylko na czas pracy;
- wspólne biblioteki: `src/tlumacz/resources/okapi-runtime/lib/`;
- XLIFF poza wejściowym FilterRegistry.
