---
id: wdrozenie-tplugin
status: plan
meta:
  contentType: ImplementationPlan
  category: plans
version: 0.40.0
updated: 2026-10-06
owner: platform-architecture
source: src/tlumacz/filter_engine/
depends_on:
  - docs/technical-docs/plugin-okapi-filter.md
  - docs/Plany/tworzenie-tplugin.md
  - docs/Plany/PLAN-02-FILTER-ENGINE-2026-10-05.md
expires_when: zakończenie pełnego wdrożenia TPlugin i przejście dokumentu do statusu active
last_validation: "9 paczek przygotowanych i zweryfikowanych 2026-10-06; migracja runtime wszystkich filtrów jeszcze nieprzełączona"
---

# Wdrożenie .tplugin w Tłumaczu V4

## 1. Cel

Wdrożenie przeorganizuje istniejący magazyn filtrów tak, aby każdy filtr dokumentowy był pluginem zarządzanym przez wspólny Filter Engine.

Nie tworzymy drugiego silnika tłumaczenia. Zachowujemy:

    Python Filter Engine
        ↓
    FilterRegistry
        ↓
    FilterSession
        ↓
    FilterHost / Java
        ↓
    Okapi filter

.tplugin dostarcza plugin, metadane, runtime filtra i zależności.

## 2. Stan wyjściowy

Repozytorium posiada już:
- FilterStore;
- FilterRegistry;
- FilterSession;
- FilterHost;
- protokół JSON Lines;
- walidator markerów;
- walidator zależności;
- katalog "filters/";
- filtry Okapi i własne adaptery formatów.

Istniejące filtry są materiałem migracyjnym.

## 3. Docelowa struktura

    $HOME/.config/tlumacz/filter-engine/
    ├── plugins/
    ├── shared-libs/
    ├── registry.json
    └── locks/

"filters/" w repozytorium pozostaje źródłem developerskim do czasu zakończenia migracji.

## 4. Etap 1 — kontrakt

Dodać:
- TPluginManifest;
- wersjonowanie formatu;
- walidację manifestu;
- canonical plugin ID;
- walidację zawartości.

## 5. Etap 2 — instalator

Dodać:
- staging;
- bezpieczne rozpakowanie;
- path traversal protection;
- checksum;
- dependency resolution;
- atomowe commitowanie.

## 6. Etap 3 — shared-libs

Dodać SharedLibraryStore z:
- indeksowaniem;
- referencjami;
- SHA-256;
- wersjonowaniem;
- wykrywaniem konfliktów;
- garbage collection.

## 7. Etap 4 — classloader

FilterHost ma otrzymywać:
- własne A;
- rozwiązane B;
- runtime C.

Nie tworzyć globalnego classpath wszystkich pluginów.

## 8. Etap 5 — migracja filtrów

Proponowana kolejność:
1. OpenXML;
2. OpenOffice/ODT;
3. HTML;
4. EPUB;
5. Markdown;
6. JSON/YAML;
7. XLIFF 1.2;
8. XLIFF 2.x.

Kolejność może zostać zmieniona po audycie zależności.

## 9. Etap 6 — produkcja pluginów

Dla każdego:

    inventory
      →
    dependency graph
      →
    A/B/C
      →
    manifest
      →
    build
      →
    validate
      →
    install
      →
    smoke
      →
    round-trip

## 10. Etap 7 — przełączenie źródła runtime

Po migracji aktywnych filtrów:
- FilterStore wskazuje rozpakowane pluginy;
- registry jest generowane z magazynu;
- stare ścieżki ładowania gołych JAR-ów są usuwane;
- .tplugin nie jest przechowywany lokalnie.

## 11. Etap 8 — usunięcie legacy

Dopiero po potwierdzeniu discovery, dependency validation, extract, merge, round-trip, update, uninstall i rollback usuwamy stare ścieżki.

## 12. Status pluginu

Minimalny lifecycle:

    DISCOVERED
    VALID
    INSTALLING
    INSTALLED
    USABLE
    BROKEN
    INCOMPATIBLE
    DISABLED

USABLE oznacza:
- manifest poprawny;
- checksum poprawny;
- engine kompatybilny;
- wszystkie zależności obecne;
- wymagane klasy dostępne;
- FilterHost może wystartować.

## 13. Integracja z istniejącym popupem zależności

Istniejący FilterDependencyValidator pozostaje.

Przepływ:

    install/update
          ↓
    dependency validation
          ↓
    missing dependency
          ↓
    log + GUI popup
          ↓
    plugin != USABLE

Dla kompletnego pluginu brak ostrzeżeń o bibliotekach shared, ponieważ są dostarczone w paczce i instalowane lokalnie.

## 14. Migracja OpenXML

OpenXML jest pierwszym wzorcem:

    runtime-openxml
          +
    common-io

Procedura:
1. ustalić dokładną wersję;
2. potwierdzić klasy TwelveMonkeys;
3. potwierdzić licencję;
4. zaklasyfikować common-io jako shared;
5. przygotować openxml.tplugin;
6. zainstalować do profilu testowego;
7. uruchomić DOCX/XLSX/PPTX;
8. potwierdzić round-trip;
9. przełączyć registry.

## 15. Macierz testów

| Obszar | Test |
|---|---|
| discovery | plugin znaleziony |
| manifest | schema |
| checksum | poprawny/błędny |
| engine | zgodna/niezgodna wersja |
| A | obecna/brak |
| B | nowa/istniejąca/konflikt |
| C | obecna/brak |
| classloader | izolacja |
| extract | wejście |
| merge | target |
| markers | 1:1 |
| Unicode | test |
| empty units | brak pustych requestów |
| round-trip | fingerprint |
| lifecycle | start/close |
| cancel | brak procesu |
| update | atomowo |
| rollback | działa |
| uninstall | brak uszkodzeń innych pluginów |

## 16. Bezpieczeństwo

Instalator:
- rozpakowuje wyłącznie do staging;
- odrzuca ../;
- odrzuca ścieżki absolutne;
- ogranicza rozmiar i liczbę plików;
- weryfikuje checksum;
- nie wykonuje skryptów;
- nie wykonuje makr dokumentów;
- usuwa staging po błędzie;
- aktywuje plugin atomowo.

## 17. Backup

Przed pierwszą migracją produkcyjnego magazynu filtrów wykonujemy pełny backup:

    backups/tplugin-migration-YYYYMMDD/

Backup obejmuje:
- obecny filters/;
- konfigurację Filter Engine;
- registry;
- shared-libs;
- manifesty.

Każdy etap musi być odwracalny.

## 18. Narzędzia

Pierwsza wersja narzędzi:

    tools/tplugin/
    ├── inspect_filter.py
    ├── dependency_inventory.py
    ├── classify.py
    ├── build.py
    ├── validate.py
    ├── install.py
    └── smoke.py

Narzędzia mają korzystać z tych samych klas domenowych co runtime.

## 19. Kryteria zakończenia

Wdrożenie jest zakończone dopiero, gdy:
1. każdy aktywny filtr ma .tplugin;
2. każdy plugin jest rozpakowany;
3. brak aktywnej ścieżki ładowania gołego JAR-a;
4. shared-libs są deduplikowane;
5. konflikty wersji są obsługiwane;
6. plugin bez zależności nie jest USABLE;
7. GUI raportuje brak zależności;
8. FilterHost ładuje właściwy classpath;
9. round-trip aktywnych formatów przechodzi;
10. update/uninstall/rollback przechodzą;
11. dokumentacja i indeks są zaktualizowane.

## 20. Ryzyka

Największe ryzyka:
- konflikt wersji Java;
- globalny classpath;
- biblioteki natywne;
- niepełny dependency tree;
- błędna klasyfikacja shared;
- brak izolacji;
- path traversal;
- nieatomowa aktualizacja;
- przedwczesne usunięcie shared-liba;
- rozjazd manifestu z JAR.

## 21. Decyzja

Przyjmujemy:

".tplugin jest formatem dystrybucyjnym, rozpakowany plugin jest formatem wykonawczym, shared-libs są fizycznie deduplikowane po instalacji, a biblioteki grupy C należą do wspólnego Filter Engine."

To jest podstawa implementacji.

## 22. Stan pilota OpenXML — 2026-10-06

Pierwszy plugin został zbudowany i zainstalowany do rzeczywistego magazynu użytkownika:

    /home/frs/.config/tlumacz/filter-engine/plugins/openxml/

Biblioteka shared została zainstalowana jako:

    /home/frs/.config/tlumacz/filter-engine/shared-libs/com.twelvemonkeys.common_common-io--3.12.0.jar

W pluginie nie pozostał katalog lib-shared. Oryginalna paczka .tplugin nie jest przechowywana w magazynie runtime.

Smoke FilterHost dla OpenXML zakończył się poprawnie: capabilities zwróciło filtr openxml, nazwę OpenXML Filter oraz MIME text/xml.

Pozostałe filtry nie zostały jeszcze przełączone do tego magazynu jako jedynego źródła runtime.


## 23. Stan przygotowania wszystkich aktualnych filtrów — 2026-10-06

Etap produkcji paczek został zakończony dla wszystkich dziewięciu filtrów obecnych w repozytorium:

| Plugin | Paczka | Instalacja testowa | FilterHost capabilities |
|---|---|---|---|
| epub | GOTOWA | PASS | PASS |
| html | GOTOWA | PASS | PASS |
| json | GOTOWA | PASS | PASS |
| markdown | GOTOWA | PASS | PASS |
| openoffice | GOTOWA | PASS | PASS |
| openxml | GOTOWA | PASS | PASS |
| xliff | GOTOWA | PASS | PASS |
| xliff2 | GOTOWA | PASS | PASS |
| yaml | GOTOWA | PASS | PASS |

Artefakty znajdują się w build/tplugins/. Są to paczki transportowe, nie magazyn runtime.

### Zweryfikowany model instalacji

Każdy .tplugin został zainstalowany do pustego profilu testowego przez TPluginInstaller. Po instalacji:

- plugin znajduje się wyłącznie jako rozpakowany katalog w plugins/;
- biblioteki B są w shared-libs/;
- lib-shared nie pozostaje w katalogu pluginu;
- archiwum .tplugin nie jest kopiowane do runtime;
- FilterHost ładuje JAR-y A oraz rozwiązane B;
- entrypoint może pochodzić z lib-shared, jeżeli jest deklarowany jako shared dependency.

### Ważne rozdzielenie etapów

Przygotowanie paczek nie oznacza jeszcze przełączenia całej aplikacji na nowy magazyn. Aktualny etap kończy się na gotowych artefaktach i dowodzie, że można je zainstalować i uruchomić. Kolejny etap to migracja FilterStore/FilterRegistry na rozpakowane pluginy jako jedyne źródło wykonawcze, a następnie E2E extract/merge/round-trip dla każdego formatu.

### Korekta launcher'a FilterHost

Podczas smoke znaleziono błąd w java/filter-host/run.sh: launcher wskazywał historyczną ścieżkę java/filter-host/FilterLoader.java, której nie było w repozytorium. Launcher został poprawiony i korzysta teraz z aktualnego źródła src/tlumacz/resources/filter-host/. Dodano regresję testową.

## 24. Migracja runtime — zakończona 2026-10-06

Migracja wykonawcza została przełączona na TPlugin.

FilterStore.default() wskazuje obecnie /home/frs/.config/tlumacz/filters/.

FilterRegistry:
- odkrywa rozpakowane pluginy po plugin.json;
- nie inicjalizuje filtrów przy starcie;
- mapuje rozszerzenia zadeklarowane w manifeście;
- tworzy adapter Okapi dopiero dla wybranego dokumentu;
- pozostawia możliwość ręcznego nadpisania automatycznej rejestracji w testach/integracjach.

Do runtime użytkownika zainstalowano dziewięć pluginów oraz centralne shared-libs. FilterHost potwierdził capabilities wszystkich dziewięciu.

## 25. Dystrybucja nierozpakowanych paczek

Do publikacji internetowej przygotowano:

    dist/tplugins/

Zawartość:
- dziewięć plików .tplugin;
- SHA256SUMS.

Ten katalog jest celowo nierozpakowany. Jest przeznaczony do skopiowania na serwer HTTP/GitHub Release/inny hosting plików.

## 26. Granica zakończonej migracji

Migracja formatu i magazynu runtime jest zakończona. Osobnym zadaniem pozostaje pełny test funkcjonalny extract/merge/round-trip każdego formatu oraz macierz aktualizacji, odinstalowania i rollbacku. Nie należy utożsamiać tych testów z samym przełączeniem magazynu.


## 27. Lifecycle pluginów — domknięcie 2026-10-06

Podstawowy cykl życia został wdrożony w TPluginInstaller:

- update(plugin.tplugin) — wymaga istniejącej instalacji, zachowuje poprzedni plugin w rollback/<id>/ i aktywuje nowy po pomyślnym przygotowaniu;
- uninstall(plugin_id) — usuwa wyłącznie wskazany plugin po wykonaniu backupu;
- rollback(plugin_id) — przywraca najnowszy zachowany stan; backup zawiera także wymagane shared-libs, więc przywrócenie nie zależy od bieżącego katalogu pluginu;
- backupy lifecycle są przechowywane poza plugins/, więc nie są wykrywane jako aktywne pluginy przez FilterRegistry;
- shared-libs nie są automatycznie usuwane przy uninstall, aby nie naruszyć możliwości rollbacku; garbage collection pozostaje osobnym rozszerzeniem polityki shared-libs.

Weryfikacja: 12 testów TPlugin PASS, w tym macierz wszystkich 9 publicznych paczek: install → update → uninstall → rollback.

Backup implementacji: backups/tplugin-lifecycle-20261006/pre-lifecycle.tar.gz; SHA-256 b9d14ea5f14b7684270ecc52b00c97f41a95727f0d7933674c3eb0c9eb9179bf.


## 29. System zarządzania zależnościami — 2026-10-06

Wdrożono produkcyjny model referencji shared-libs:

- shared-libs/index.json przechowuje artefakt, wersję, SHA-256 i listę referentów;
- różne wersje tego samego artefaktu mogą współistnieć;
- ten sam id+version z innym SHA-256 jest konfliktem;
- uninstall usuwa referencję, ale pozostawia bibliotekę do GC;
- rollback ponownie rejestruje wymagane shared dependencies;
- rebuild odbudowuje indeks z aktywnych plugin.json;
- GC usuwa wyłącznie artefakty bez referencji;
- builder tworzy inventory.json i checksums.json;
- tools/tplugin/dependencies.py udostępnia inventory, validate, rebuild i gc.

Walidacja wdrożenia: 16/16 testów TPlugin, 9/9 paczek przechodzi walidację checksumów.

## 2026-10-07 — model docelowy po uproszczeniu magazynu

Poprzedni layout `$HOME/.config/tlumacz/filter-engine/` nie jest już używany. Jedynym trwałym magazynem pakietów jest:

```text
/home/frs/.config/tlumacz/filters/
```

Paczki `.tplugin` są rozpakowywane tylko podczas pracy aplikacji do:

```text
/tmp/filters/<katalog-procesu>/
```

Nie istnieją trwałe `plugins/`, `shared-libs/`, `dist/tplugins/` ani `build/tplugins/` jako elementy runtime.

Wspólne biblioteki Okapi znajdują się w:

```text
src/tlumacz/resources/okapi-runtime/lib/
```

XLIFF jest wewnętrzną warstwą dokumentową i znajduje się w `src/tlumacz/documents/xliff.py`; nie jest instalowany jako wejściowy plugin Okapi.
