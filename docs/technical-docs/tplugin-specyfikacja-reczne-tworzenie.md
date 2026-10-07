---
id: tplugin-specyfikacja-reczne-tworzenie
status: active
meta:
  contentType: HowTo
  category: technical
version: 0.40.0
updated: 2026-10-07
owner: platform-architecture
source:
  - src/tlumacz/filter_engine/tplugin.py
  - src/tlumacz/filter_engine/filter_store.py
  - src/tlumacz/filter_engine/registry.py
  - tools/tplugin/
  - tools/tplugin_admin/
depends_on:
  - docs/technical-docs/plugin-okapi-filter.md
  - docs/technical-docs/tplugin-zarzadzanie-zaleznosciami.md
expires_when: zmiana kontraktu formatu TPlugin
last_validation: "pytest tests/test_tplugin.py tests/test_tplugin_admin.py tests/test_tplugin_create.py"
---

# Specyfikacja i ręczne tworzenie TPlugin

## 1. Aktualny kontrakt

TPlugin jest artefaktem transportowym, a nie trwałym runtime aplikacji.

Jedyny trwały magazyn pakietów użytkownika:

    /home/frs/.config/tlumacz/filters/

Jeżeli paczka wymaga rozpakowania, Filter Engine tworzy izolowany runtime pod:

    /tmp/filters/

Po zakończeniu procesu tymczasowy runtime jest usuwany.

Następujące ścieżki są historyczne i nie są aktualnym magazynem:

    $HOME/.config/tlumacz/filter-engine/plugins/
    $HOME/.config/tlumacz/filter-engine/shared-libs/
    dist/tplugins/

Wspólne biblioteki Okapi są częścią drzewa aplikacji:

    src/tlumacz/resources/okapi-runtime/lib/

## 2. Narzędzia

Przygotowanie pluginów pozostaje poza src/tlumacz/.

Generator:

    tools/tplugin/create.py

Budowa:

    tools/tplugin/build.py
    tools/tplugin/build_all.py

Inventory i walidacja zależności:

    tools/tplugin/dependencies.py

Backend administracyjny:

    tools/tplugin_admin/

Backend administracyjny obsługuje:

    init
    validate
    build
    verify
    inspect
    test-install
    publish

Generator szkieletu:

    PYTHONPATH=src:. python3 tools/tplugin/create.py my-filter       --id my-filter       --name "Mój filtr"       --version 1.0.0

Generator tworzy:

    my-filter/
        README.md
        tplugin-project.json
        lib/

Nie buduje paczki, nie instaluje jej i nie pobiera zależności.

## 3. Projekt źródłowy

Minimalna struktura:

    my-filter/
        README.md
        tplugin-project.json
        lib/
            runtime.jar

Przykładowy tplugin-project.json:

    {
      "id": "my-filter",
      "name": "Mój filtr",
      "version": "1.0.0",
      "entrypoint": "lib/runtime.jar",
      "extensions": [".abc"],
      "dependencies": {
        "bundled": [],
        "shared": [],
        "engine": []
      }
    }

tplugin-project.json opisuje proces przygotowania. Nie jest manifestem runtime.

## 4. Manifest runtime plugin.json

Minimalny kontrakt:

    {
      "format": "tplugin",
      "format_version": 1,
      "id": "my-filter",
      "name": "Mój filtr",
      "version": "1.0.0",
      "engine": {
        "min_version": null,
        "max_version": null
      },
      "dependencies": {
        "bundled": [],
        "shared": [],
        "engine": []
      },
      "extensions": [".abc"],
      "entrypoint": {
        "kind": "okapi-filter",
        "jar": "lib/runtime.jar"
      }
    }

TPluginManifest wymaga:

- format = tplugin;
- format_version = 1;
- id;
- name;
- version;
- entrypoint.jar.

## 5. Entry point i bezpieczeństwo ścieżek

entrypoint.jar musi wskazywać plik wewnątrz paczki.

Poprawnie:

    lib/runtime.jar

Niepoprawnie:

    ../runtime.jar
    /tmp/runtime.jar
    /home/user/runtime.jar

Path traversal jest odrzucany przez walidację i bezpieczne rozpakowanie.

## 6. Zależności A/B/C

### A — bundled

Biblioteka prywatna, specyficzna dla pluginu:

    my-filter/
        lib/
            runtime.jar
            helper.jar

Deklaracja:

    "bundled": [
      {
        "id": "example:helper",
        "version": "1.0.0",
        "file": "lib/helper.jar"
      }
    ]

### B — shared

Biblioteka przeznaczona do współdzielenia.

W aktualnym runtime wspólne biblioteki Okapi znajdują się w:

    src/tlumacz/resources/okapi-runtime/lib/

Nie twórz trwałego shared-libs w profilu użytkownika.

Jeżeli proces budowania używa lib-shared jako materiału wejściowego, jest to element artefaktu produkcyjnego, a nie nowy trwały magazyn runtime.

### C — engine

Zależność dostarczana przez wspólny Filter Engine:

    "engine": [
      {
        "id": "okapi-filter-host",
        "version": "1.49.0-SNAPSHOT"
      }
    ]

Nie kopiuj zależności C do pluginu.

## 7. Inventory i checksumy

Inventory powinno identyfikować plugin, wersję, zależności, pliki i SHA-256.

Przykład:

    PYTHONPATH=src python3 tools/tplugin/dependencies.py inventory my-filter

Dla paczki:

    PYTHONPATH=src python3 tools/tplugin/dependencies.py inventory my-filter-1.0.0.tplugin

checksums.json obejmuje pliki pluginu z pominięciem własnego wpisu.

Preferowane jest generowanie checksumów przez TPluginBuilder.

## 8. Budowa

Workflow:

    PYTHONPATH=src:. python3 -m tools.tplugin_admin validate my-filter

    PYTHONPATH=src:. python3 -m tools.tplugin_admin build my-filter --output dist/

    PYTHONPATH=src:. python3 -m tools.tplugin_admin verify dist/my-filter-1.0.0.tplugin

    PYTHONPATH=src:. python3 -m tools.tplugin_admin inspect dist/my-filter-1.0.0.tplugin

Dla testu instalacyjnego:

    PYTHONPATH=src:. python3 -m tools.tplugin_admin test-install dist/my-filter-1.0.0.tplugin

Przed publikacją:

    PYTHONPATH=src:. python3 -m tools.tplugin_admin publish my-filter --output dist/

Dla całego aktualnego zestawu:

    PYTHONPATH=src python3 tools/tplugin/build_all.py build/tplugins

## 9. Ręczne zbudowanie ZIP

Wariant awaryjny:

    my-filter/
        plugin.json
        inventory.json
        checksums.json
        lib/
            runtime.jar
        resources/

Następnie:

    cd staging
    zip -r ../my-filter-1.0.0.tplugin my-filter/

Paczka musi być ZIP-em z rozszerzeniem .tplugin.

Nie dodawaj cache, danych testowych, danych roboczych, nieużywanych JAR-ów ani sekretów.

Po ręcznym ZIP-owaniu obowiązkowo uruchom verify i test-install.

## 10. Test rzeczywistego filtra

Walidacja struktury nie dowodzi działania.

Minimalny smoke:

    FilterHost start
      ↓
    capabilities
      ↓
    open
      ↓
    next
      ↓
    tłumaczenie jednostki
      ↓
    apply
      ↓
    close

Dla filtra dokumentowego wykonaj round-trip:

    dokument wejściowy
      ↓
    extract
      ↓
    tłumaczenie
      ↓
    merge
      ↓
    dokument wynikowy

Sprawdź strukturę, Unicode, inline codes, puste jednostki, powtarzające się ID i reprezentatywny dokument.

## 11. Kryteria publikacji

Plugin może zostać przekazany do publikacji dopiero po:

- zamknięciu inventory;
- zamknięciu klasyfikacji A/B/C;
- poprawnych checksumach;
- walidacji manifestu;
- pozytywnym test-install;
- pozytywnym smoke FilterHost;
- pozytywnym round-trip;
- audycie licencji;
- zapisaniu źródła upstream;
- potwierdzeniu wymagań JVM i systemowych.

Instalator nie pobiera brakujących zależności z Internetu.

## 12. Diagnostyka

Brak entrypointu:
- sprawdź manifest;
- sprawdź ścieżkę JAR-a;
- sprawdź staging;
- sprawdź checksumy.

Brak zależności:
- sprawdź bundled;
- sprawdź shared;
- sprawdź engine;
- sprawdź rzeczywiste pliki;
- sprawdź wymagane klasy;
- sprawdź JVM.

Konflikt SHA-256:
- ta sama identyfikacja logiczna i wersja z innym SHA-256 oznacza konflikt;
- nie nadpisuj biblioteki bez decyzji architektonicznej.

Discovery działa, ale FilterHost nie:
- rozdziel discovery, manifest, classpath, uruchomienie FilterHost, extract i merge.

## 13. Ręczny workflow autora

    1. przygotuj źródło/JAR
    2. wykonaj inventory
    3. utwórz projekt przez tools/tplugin/create.py
    4. umieść entrypoint
    5. uzupełnij tplugin-project.json
    6. sklasyfikuj A/B/C
    7. dodaj wymagane zasoby i JAR-y
    8. uruchom validate
    9. zbuduj .tplugin
    10. uruchom verify
    11. uruchom inspect
    12. uruchom test-install
    13. wykonaj FilterHost smoke
    14. wykonaj round-trip
    15. wykonaj audyt licencji
    16. dopiero wtedy publikuj

## 14. Źródła prawdy

Kod:

    src/tlumacz/filter_engine/tplugin.py
    src/tlumacz/filter_engine/filter_store.py
    src/tlumacz/filter_engine/registry.py

Narzędzia:

    tools/tplugin/create.py
    tools/tplugin/build.py
    tools/tplugin/build_all.py
    tools/tplugin/dependencies.py
    tools/tplugin_admin/

Dokumentacja:

    docs/technical-docs/plugin-okapi-filter.md
    docs/technical-docs/tplugin-zarzadzanie-zaleznosciami.md
    docs/technical-docs/tplugin-specyfikacja-reczne-tworzenie.md
    docs/Plany/tworzenie-tplugin.md

Historyczne opisy starego layoutu runtime nie są źródłem aktualnego kontraktu.
