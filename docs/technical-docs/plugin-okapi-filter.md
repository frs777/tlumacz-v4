---
id: plugin-okapi-filter
status: active
meta:
  contentType: TechnicalDesign
  category: technical
version: 0.40.0
updated: 2026-10-07
owner: platform-architecture
source: src/tlumacz/filter_engine/
depends_on:
  - docs/Plany/PLAN-02-FILTER-ENGINE-2026-10-05.md
  - src/tlumacz/filter_engine/protocol.py
  - src/tlumacz/filter_engine/filter_store.py
expires_when: zastąpienie formatu TPlugin nową wersją kontraktu pakietów filtrów
last_validation: "9 paczek .tplugin zbudowanych 2026-10-06; 14 testów TPlugin/FilterHost; smoke capabilities 9/9"
---

# .tplugin — format i architektura pluginów filtrów Okapi

> **Nadrzędny kontrakt od 2026-10-07:** trwałym magazynem pakietów użytkownika jest /home/frs/.config/tlumacz/filters, runtime tymczasowy powstaje pod /tmp/filters, a wspólne biblioteki aplikacji znajdują się w src/tlumacz/resources/okapi-runtime/lib. Starsze sekcje opisujące filter-engine/plugins, trwałe shared-libs i dist/tplugins mają znaczenie historyczne; aktualny opis znajduje się w sekcji „2026-10-07 — nowy kontrakt magazynu” oraz w docs/technical-docs/tplugin-specyfikacja-reczne-tworzenie.md.


## 1. Cel

.tplugin jest docelowym formatem dystrybucyjnym dla pluginów filtrów dokumentowych Tłumacza V4. Filtry Okapi traktujemy jako bazę technologiczną: wykorzystujemy istniejące filtry, konfiguracje i biblioteki Java, ale lifecycle, zależności, bezpieczeństwo, instalację i rejestr pluginów kontroluje Tłumacz.

Plugin opisuje format, implementację filtra, zależności JAR, zasoby, kompatybilność oraz integralność artefaktów.

.tplugin jest paczką instalacyjną. Po instalacji nie przechowujemy jej jako ZIP-a. Paczka jest rozpakowywana do magazynu pluginów i z tej rozpakowanej postaci wykonywana.

## 2. Trzy grupy zależności

| Grupa | Zasada | Miejsce wykonawcze |
|---|---|---|
| A — stałe przy filtrze | małe, nietypowe, specyficzne | katalog pluginu |
| B — współdzielone | popularne, używane przez wiele filtrów | centralny shared-libs |
| C — stałe dla całego systemu | część kontraktu wspólnego runtime | kod/runtime Filter Engine |

Klasyfikacja jest decyzją architektoniczną, nie wynikiem samej nazwy artefaktu.

### 2.1. Grupa A — biblioteka stała przy filtrze

Do grupy A trafia biblioteka, gdy jest mała, nietypowa, używana przez jeden filtr lub bardzo małą grupę filtrów, silnie związana z wersją filtra albo gdy izolacja wersji jest ważniejsza od oszczędności miejsca.

Biblioteka znajduje się w katalogu pluginu, np. "lib/", i jest ładowana wyłącznie dla tego pluginu.

### 2.2. Grupa B — biblioteka współdzielona

Do grupy B trafia biblioteka używana przez wiele filtrów, relatywnie duża lub często powtarzająca się, o stabilnym API i możliwa do bezpiecznego współdzielenia.

Każdy .tplugin nadal zawiera deklarację i kopię biblioteki, której wymaga. Podczas instalacji kopia jest źródłem instalacyjnym i trafia do centralnego:

"$HOME/.config/tlumacz/filter-engine/shared-libs/"

Jeżeli identyczna biblioteka już istnieje, nie kopiujemy jej ponownie.

Jeżeli istnieje inna wersja, nie wolno jej bezwarunkowo nadpisać. Należy porównać identyfikator, wersję, SHA-256 i kompatybilność. Dopuszczalne jest współistnienie kilku wersji tylko wtedy, gdy classloader potrafi bezpiecznie je izolować.

### 2.3. Grupa C — biblioteki stałe dla całego Filter Engine

To elementy wspólnego kontraktu, a nie zależności pojedynczego filtra. Mogą tu należeć wspólne klasy runtime, podstawowe biblioteki Okapi wymagane przez wszystkie aktywne ścieżki oraz elementy wymagane przez wspólny Java FilterHost.

Plugin nie kopiuje grupy C. Manifest deklaruje wymagania engine, a instalator sprawdza ich spełnienie.

Popularność biblioteki sama w sobie nie kwalifikuje jej do grupy C.

## 3. Dlaczego shared biblioteka jest dołączona do każdej paczki

Dystrybucyjnie plugin ma być samowystarczalny. Host pluginów nie musi znać globalnego stanu maszyny.

Dlatego paczka zawiera kopię biblioteki shared, np. w "lib-shared/". Instalator po weryfikacji przenosi ją do centralnego magazynu, jeżeli nie ma jej tam jeszcze w zgodnej postaci.

Daje to:
- instalację offline;
- kompletność paczki;
- możliwość weryfikacji checksum;
- brak pobierania Maven podczas instalacji;
- brak fizycznego duplikatu w runtime.

## 4. Brak przechowywania spakowanych pluginów

.tplugin jest artefaktem transportowym.

Po instalacji:
1. weryfikujemy paczkę;
2. tworzymy staging;
3. rozpakowujemy ją;
4. walidujemy manifest;
5. rozwiązujemy zależności;
6. atomowo przenosimy plugin do magazynu;
7. usuwamy staging;
8. nie zachowujemy oryginalnego .tplugin.

Źródłem wykonawczym jest wyłącznie rozpakowany plugin.

## 5. Docelowy magazyn

Przykładowo:

    $HOME/.config/tlumacz/filter-engine/
    ├── plugins/
    │   ├── openxml/
    │   │   ├── plugin.json
    │   │   ├── filter.json
    │   │   ├── lib/
    │   │   ├── lib-shared/
    │   │   ├── resources/
    │   │   └── checksums.json
    │   └── ...
    ├── shared-libs/
    ├── registry.json
    └── locks/

Istniejący FilterStore pozostaje punktem integracji. Docelowo wskazuje katalog "plugins/".

## 6. Struktura .tplugin

Przykładowy plugin OpenXML:

    openxml.tplugin
    └── openxml/
        ├── plugin.json
        ├── filter.json
        ├── lib/
        │   └── runtime-openxml-1.49.0-SNAPSHOT.jar
        ├── lib-shared/
        │   └── common-io-....jar
        ├── resources/
        └── checksums.json

Wewnętrzny katalog musi odpowiadać "plugin.id".

## 7. Manifest plugin.json

Minimalny kontrakt:

    {
      "format": "tplugin",
      "format_version": 1,
      "id": "openxml",
      "name": "Okapi OpenXML",
      "version": "1.0.0",
      "engine": {
        "min_version": "0.40.0",
        "max_version": null
      },
      "filter": {
        "filter_config": "filter.json",
        "extensions": [".docx", ".xlsx", ".pptx"]
      },
      "dependencies": {
        "bundled": [],
        "shared": [],
        "engine": []
      },
      "entrypoint": {
        "kind": "okapi-filter",
        "jar": "lib/runtime-openxml-1.49.0-SNAPSHOT.jar"
      }
    }

W finalnym kontrakcie dochodzą: licencja, źródło artefaktu, SHA-256, kompatybilność JVM i wymagania systemowe.

## 8. Opis zależności

Każda biblioteka ma stabilny identyfikator logiczny, coordinates, wersję, checksum, wymagane klasy i scope.

Przykład:

    {
      "id": "twelvemonkeys-common-io",
      "coordinates": "com.twelvemonkeys.common:common-io",
      "version": "3.x",
      "sha256": "...",
      "class_requirements": [
        "com.twelvemonkeys.io.ole2.CompoundDocument",
        "com.twelvemonkeys.io.ole2.CorruptDocumentException"
      ],
      "scope": "shared",
      "source": {
        "url": "https://central.sonatype.com/artifact/com.twelvemonkeys.common/common-io"
      }
    }

## 9. Rozwiązywanie zależności

Instalator nie ufa samej nazwie JAR-a.

Dla każdej zależności:
1. odczytuje manifest;
2. sprawdza scope;
3. sprawdza SHA-256;
4. dla shared sprawdza centralny magazyn;
5. porównuje wersję;
6. sprawdza wymagane klasy;
7. sprawdza kompatybilność JVM;
8. dopiero wtedy zatwierdza instalację.

Brak wymaganej klasy jest błędem nawet wtedy, gdy plik JAR istnieje.

## 10. Izolacja classpath

Nie tworzymy jednego globalnego classpath wszystkich pluginów.

Każdy plugin powinien być uruchamiany z classloaderem zbudowanym z:
- bibliotek grupy A;
- rozwiązanych bibliotek grupy B;
- bibliotek grupy C dostarczonych przez wspólny runtime.

Schemat:

    FilterHost JVM
    ├── Engine classpath
    │   └── grupa C
    ├── PluginClassLoader(openxml)
    │   ├── lib/*
    │   └── shared-libs resolved for openxml/*
    └── PluginClassLoader(other)
        └── ...

Celem jest uniknięcie konfliktów wersji. Współdzielenie pliku na dysku nie oznacza współdzielenia globalnej przestrzeni klas.

## 11. Wszystkie główne sytuacje zależności

### 11.1. Biblioteka tylko w pluginie

Instalujemy do "plugin/lib/".

### 11.2. Shared biblioteka nieobecna

Kopiujemy ją do shared-libs.

### 11.3. Shared biblioteka identyczna już istnieje

Nie kopiujemy drugi raz.

### 11.4. Shared biblioteka istnieje w innej wersji

Nie nadpisujemy automatycznie. Rozstrzygamy zgodność i możliwość izolacji.

### 11.5. Dwa pluginy wymagają tej samej wersji

Jedna kopia fizyczna, wiele referencji.

### 11.6. Dwa pluginy wymagają różnych kompatybilnych wersji

Dopuszczamy oba warianty tylko przy bezpiecznej izolacji classloaderów.

### 11.7. Wersje są niekompatybilne

Instalację blokujemy, jeżeli nie ma bezpiecznej izolacji.

### 11.8. Checksum jest błędny

Błąd integralności. Biblioteka nie może zostać użyta.

### 11.9. JAR istnieje, ale brakuje wymaganej klasy

Błąd zależności.

### 11.10. Brakuje zależności engine

Plugin pozostaje nieużyteczny.

### 11.11. Zależność systemowa

Program systemowy jest deklarowany jako capability i sprawdzany osobnym walidatorem.

### 11.12. Zależność natywna JNI

Biblioteki .so, .dll i .dylib mają osobny opis platformowy i nie są traktowane jak zwykły JAR.

### 11.13. Zależność opcjonalna

Manifest musi wskazać "optional": true, a filtr musi poprawnie działać bez tej biblioteki.

### 11.14. Zależność build-time

Nie trafia do .tplugin, jeśli nie jest wymagana w runtime.

## 12. OpenXML jako wzorzec

Aktualny przypadek:

    runtime-openxml-1.49.0-SNAPSHOT.jar
            ↓
    com.twelvemonkeys.common:common-io

common-io nie jest filtrem. Jest biblioteką filtra OpenXML.

Docelowo:

    openxml.tplugin
    ├── filter.json
    ├── lib/
    │   └── runtime-openxml-1.49.0-SNAPSHOT.jar
    └── lib-shared/
        └── common-io-....jar

Po instalacji:
- plugin przechowuje własny runtime;
- shared-libs przechowuje jedną fizyczną kopię common-io;
- registry zapisuje referencję.

## 13. Aktualizacja pluginu

Aktualizacja:
1. nowa paczka trafia do staging;
2. walidowana jest niezależnie;
3. zależności są rozwiązywane;
4. aktywna sesja jest bezpiecznie kończona;
5. katalog pluginu jest atomowo podmieniany;
6. registry jest aktualizowane;
7. stare pliki są usuwane dopiero po sukcesie;
8. shared-libs są sprzątane dopiero po analizie referencji.

Nie aktualizujemy plików aktywnego pluginu "w miejscu".

## 14. Odinstalowanie

Usuwamy plugin, ale nie usuwamy automatycznie shared-libs.

Po odinstalowaniu:
1. skanujemy pozostałe pluginy;
2. liczymy referencje;
3. bibliotekę bez referencji oznaczamy jako orphan;
4. cleanup usuwa ją w kontrolowanym kroku.

## 15. Bezpieczeństwo

.tplugin zawiera wykonywalny kod Java.

Obowiązkowe są:
- checksum;
- źródło artefaktu;
- staging;
- normalizacja ścieżek;
- ochrona przed path traversal;
- limit rozmiaru rozpakowania;
- brak wykonywania skryptów z paczki;
- brak wykonywania makr dokumentu wejściowego.

Docelowo plugin powinien mieć podpis cyfrowy.

## 16. Licencje

Inventory musi obejmować:
- licencję filtra;
- licencje JAR;
- źródła artefaktów;
- NOTICE/COPYING/LICENSE;
- obowiązki redystrybucyjne.

Licencje są częścią procesu publikacji.

## 17. Optymalizacja

Optymalizujemy przede wszystkim:
1. brak duplikacji dużych bibliotek przez shared-libs;
2. małe specyficzne biblioteki przy filtrze;
3. wspólny runtime w module Filter Engine.

Priorytetem pozostają izolacja wersji, powtarzalność, offline, rollback i diagnostyka.

## 18. Zasada końcowa

.tplugin jest paczką źródłowo-samowystarczalną, ale runtime'owo zoptymalizowaną:

    .tplugin
       ↓ instalacja
    staging
       ↓ walidacja
    plugin/
       ├── własne JAR-y
       └── kopie shared
              ↓ deduplikacja
    shared-libs/
       ↓
    FilterHost
       ↓
    TranslationUnit[]

Filtry Okapi są bazą. Tłumacz jest właścicielem lifecycle, zależności, bezpieczeństwa i instalacji.
## 19. Inventory aktualnych filtrów Okapi — 2026-10-06

W repozytorium znajduje się obecnie dziewięć gotowych źródeł filtrów: epub, html, json, markdown, openoffice, openxml, xliff, xliff2, yaml. Wszystkie zostały przekształcone do .tplugin.

| Filtr | Entrypoint | A — przy filtrze | B — shared | C — engine |
|---|---|---|---|---|
| EPUB | runtime-epub | runtime-archive | runtime-abstractmarkup, runtime-html | Okapi Core/FilterHost |
| HTML | runtime-html | — | runtime-abstractmarkup, runtime-html | Okapi Core/FilterHost |
| JSON | runtime-json | — | runtime-generated-parser-compat | Okapi Core/FilterHost |
| OpenOffice | runtime-openoffice | runtime-openoffice | — | Okapi Core/FilterHost |
| OpenXML | runtime-openxml | runtime-openxml | runtime-abstractmarkup, TwelveMonkeys common-io, common-lang | Okapi Core/FilterHost |
| XLIFF 1.2 | runtime-xliff | — | runtime-xliff | Okapi Core/FilterHost |
| XLIFF 2 | runtime-xliff2, runtime-lib-xliff2 | runtime-xliff2, runtime-lib-xliff2 | runtime-xliff | Okapi Core/FilterHost |
| YAML | runtime-yaml | — | runtime-generated-parser-compat, runtime-yaml | Okapi Core/FilterHost |

runtime-xliff i runtime-yaml mogą być jednocześnie entrypointem i biblioteką shared. Jest to dozwolone: entrypoint może wskazywać plik z lib-shared, a FilterHost otrzymuje go przez resolved shared dependencies.

## 20. Artefakty instalacyjne

Budowanie wszystkich filtrów wykonuje:

    PYTHONPATH=src python3 tools/tplugin/build_all.py build/tplugins

Wynikiem są dziewięć paczek:

    build/tplugins/
    ├── epub-1.49.0-SNAPSHOT.tplugin
    ├── html-1.49.0-SNAPSHOT.tplugin
    ├── json-1.49.0-SNAPSHOT.tplugin
    ├── openoffice-1.49.0-SNAPSHOT.tplugin
    ├── openxml-1.49.0-SNAPSHOT.tplugin
    ├── xliff-1.49.0-SNAPSHOT.tplugin
    ├── xliff2-1.49.0-SNAPSHOT.tplugin
    └── yaml-1.49.0-SNAPSHOT.tplugin

Paczki są artefaktami transportowymi. W profilu testowym po instalacji potwierdzono brak jakichkolwiek .tplugin w runtime.

## 21. Zasada klasyfikacji TwelveMonkeys

common-io i common-lang pozostają w grupie B. Nie są częścią kodu filtra OpenXML i nie są osobnymi pluginami. Każdy plugin, który deklaruje te biblioteki jako shared, dostarcza ich kopię w lib-shared, a instalator deduplikuje je po id + version + SHA-256.

common-io jest zewnętrzną biblioteką TwelveMonkeys używaną przez OpenXML; aktualna wersja projektu to 3.12.0. Źródło artefaktu i klasy wymagane przez OpenXML są zapisane w filter.json.

## 22. Weryfikacja całego zestawu

Weryfikacja 2026-10-06:

- TPlugin builder/installer: 7 passed;
- inventory budowania: 3 passed;
- FilterHost launcher: 4 passed;
- łącznie testy ukierunkowane: 14 passed;
- instalacja dziewięciu paczek do pustego profilu testowego: 9/9;
- capabilities FilterHost po instalacji: 9/9;
- brak .tplugin w runtime po instalacji: potwierdzony;
- OpenXML przez java/filter-host/run.sh: PASS.

Smoke test używał wyłącznie rozpakowanego runtime oraz centralnego shared-libs; nie instalował zależności systemowych i nie pobierał ich podczas instalacji.

## 23. Przypadek szczególny: entrypoint w shared-libs

Plugin może mieć entrypoint.jar wskazujący na lib-shared/<jar>. Dotyczy to filtrów, których główny JAR jest jednocześnie biblioteką współdzieloną, np. HTML (runtime-html), XLIFF 1.2 (runtime-xliff) oraz YAML (runtime-yaml).

Podczas instalacji TPluginInstaller:
- waliduje entrypoint względem manifestu;
- instaluje bibliotekę do centralnego shared-libs;
- usuwa lib-shared z katalogu pluginu;
- pozostawia plugin gotowy do uruchomienia bez lokalnej kopii JAR-a.

FilterHost rozwiązuje taki entrypoint przez deklarację dependencies.shared. Nie jest wymagane kopiowanie shared JAR-a do plugins/<id>/lib.

To jest część oficjalnego formatu TPlugin, a nie obejście dla konkretnego filtra.

## 24. Migracja runtime zakończona

Od 2026-10-06 produkcyjny FilterStore wskazuje $HOME/.config/tlumacz/filter-engine/plugins/ i nie wskazuje już repozytoryjnego filters/ jako domyślnego magazynu wykonawczego.

FilterRegistry skanuje rozpakowane plugin.json, odczytuje deklarowane extensions i tworzy OkapiFilter dopiero po rozpoznaniu rozszerzenia. Dla XLIFF 1.2/2 używany jest automatyczny wybór wersji dokumentu.

Repozytoryjne filters/ pozostaje źródłem budowania artefaktów, nie źródłem runtime aplikacji.

## 25. Katalog dystrybucyjny

Nierozpakowane paczki przeznaczone do publikacji internetowej znajdują się w dist/tplugins/.

Katalog zawiera dziewięć plików .tplugin oraz SHA256SUMS. Paczki nie są rozpakowywane w tym katalogu. Po pobraniu użytkownik przekazuje pojedynczą paczkę do instalatora TPlugin.

Pełny runtime instalacyjny pozostaje oddzielony od katalogu dystrybucyjnego.


## Lifecycle TPlugin — 2026-10-06

Warstwa instalacyjna obsługuje podstawowe operacje cyklu życia:

- update istniejącego pluginu z backupem poprzedniej wersji;
- uninstall z zachowaniem stanu do rollbacku;
- rollback do najnowszego zachowanego stanu;
- backup rollbackowy zawiera także shared-libs wymagane przez manifest, ponieważ aktywny plugin po instalacji nie przechowuje już katalogu lib-shared;
- backupy są przechowywane poza plugins/ i nie uczestniczą w discovery.

Shared-libs nie są usuwane podczas uninstall. Jest to świadoma decyzja bezpieczeństwa: zachowanie bibliotek umożliwia rollback bez ryzyka usunięcia zależności używanej przez inny plugin. Garbage collection shared-libs pozostaje osobnym etapem polityki magazynu.

Weryfikacja: 12 testów TPlugin PASS oraz macierz lifecycle wszystkich 9 publicznych paczek PASS.

## 13. Ochrona inline codes na granicy backendu tłumaczeniowego

Okapi TextFragment.getCodedText() używa dwóch znaków PUA dla każdego inline code: znaku typu oraz znaku indeksu kodu. Ta reprezentacja jest poprawna wewnątrz Okapi, ale nie może być traktowana jako bezpieczny protokół transportowy do modelu tłumaczeniowego.

Od 2026-10-07 granica TranslationOrchestrator → backend stosuje następujący kontrakt:

1. przed wysłaniem jednostki protect_inline_codes() zamienia każdą parę PUA na kolejny token ASCII __OKAPI_CODE_N__;
2. backend otrzymuje wyłącznie tekst z tokenami transportowymi;
3. po odpowiedzi restore_inline_codes() wymaga dokładnie tego samego zestawu tokenów, w tej samej kolejności;
4. brak, duplikat albo przestawienie tokenu kończy tłumaczenie błędem InlineCodeProtectionError;
5. dopiero po przywróceniu PUA wynik trafia do ResultValidator, cache i dalszej rekonstrukcji dokumentu.

Nie wolno uzupełniać brakującego markera na podstawie samej liczby kodów. Pozycja i tożsamość kodu są częścią integralności dokumentu.

### 13.1. Cache

Klucz cache pozostaje oparty na oryginalnym tekście z markerami Okapi. Cache przechowuje wynik już po przywróceniu markerów PUA.

### 13.2. Diagnostyka

Dla reprodukcji należy rejestrować osobno:

SOURCE → MASKED REQUEST → RAW RESPONSE → RESTORED RESULT

Brak aktywnego backendu nie może być zastępowany założeniem o jego odpowiedzi. Weryfikacja rzeczywistego request/response pozostaje osobnym gate'em E2E.

## 14. Lifecycle czytników Filter Host

FilterHostClient uruchamia dwa wątki czytające stdout/stderr procesu Java. Są to wątki niedemoniczne. close() kończy proces potomny, czeka na reader threads, zamyka strumienie i wykonuje drugi join().

Nie wolno wracać do daemon=True. Python 3.14 traktuje daemon threads jako zasób zatrzymywany brutalnie przy zamknięciu interpretera, co jest szczególnie niebezpieczne w procesie zawierającym Qt/PySide6.

Regresja obejmuje pojedynczy shutdown oraz 10-krotny cykl start → request → close.
## 15. Implementacja primary/fallback w FilterRegistry — 2026-10-07

Zgodnie z instrukcja-okapi.md kolejność routingu jest następująca:

1. Registry rejestruje native jako fallback.
2. Discovery TPlugin odczytuje wszystkie rozszerzenia zadeklarowane przez plugin.
3. Discovery nie usuwa rozszerzeń tylko dlatego, że wcześniej zarejestrowano native.
4. register_lazy() pozwala discovered pluginowi zastąpić native dla wspólnego suffixu.
5. Rozszerzenia pluginu, które nie kolidują z native, są rejestrowane równocześnie.
6. for_path() zwraca jedną aktywną implementację dla danego suffixu.

Oznacza to, że obecność .txt → PlainTextFilter nie blokuje przyszłego pluginu Okapi deklarującego .txt. Po discovery routing zmienia się automatycznie na .txt → OkapiFilter(plugin_id, ...), bez zmian w pipeline tłumaczenia.

### Markdown

Markdown jest świadomie wyłączony z routingu Okapi. .md i .markdown korzystają bezpośrednio z natywnego MarkdownFilter, ponieważ jest to prosty format tekstowy ze składnią, a dodatkowa warstwa Okapi nie daje tu wymaganej wartości.

Plugin Okapi Markdown został usunięty z aktywnego zestawu filtrów. FilterRegistry dodatkowo przywraca natywną rejestrację Markdown po discovery, aby pozostałość starego pluginu w magazynie runtime nie mogła zmienić routingu.

### Regresje

Pokryto:
- przejęcie .txt przez plugin Okapi;
- plugin deklarujący jednocześnie suffix zajęty przez native i nowy suffix;
- ochronę .md/.markdown przed przejęciem przez plugin Okapi;
- HTML Okapi jako primary;
- zachowanie native fallbacku, gdy pluginu brak.

Gate: tests/test_filter_registry.py — 17 passed.

## 2026-10-07 — nowy kontrakt magazynu

Poprzedni model trwałego `filter-engine/plugins` i `filter-engine/shared-libs` został zastąpiony jednym magazynem użytkownika:

```text
/home/frs/.config/tlumacz/filters/
    *.tplugin
```

`FilterStore.default()` wskazuje wyłącznie `$HOME/.config/tlumacz/filters`. Podczas uruchomienia pakiety są rozpakowywane do izolowanego `/tmp/filters/<katalog-procesu>/`; po zakończeniu procesu runtime tymczasowy jest usuwany. Nie ma drugiej trwałej kopii pluginów.

Wspólne biblioteki Okapi są częścią drzewa aplikacji:

```text
src/tlumacz/resources/okapi-runtime/lib/
```

Java `FilterLoader` rozwiązuje zależności shared z tego katalogu. Pakiety użytkownika zawierają deklarację zależności, ale nie muszą zawierać fizycznej kopii wspólnego JAR-a.

XLIFF nie jest aktywnym filtrem wejściowym. Wewnętrzna implementacja XLIFF 2.0 znajduje się w `src/tlumacz/documents/xliff.py`.

Aktualny aktywny zestaw wejściowych pakietów Okapi: `epub`, `json`, `openoffice`, `openxml`, `yaml`. HTML i Markdown korzystają z natywnych filtrów V4.
