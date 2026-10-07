# Ręczne tworzenie paczki TPlugin

> Status dokumentu: zastąpiony przez docs/technical-docs/tplugin-specyfikacja-reczne-tworzenie.md. Ten plik pozostaje wyłącznie dla zgodności historycznej.


## Dla kogo jest ta instrukcja

Ta metoda jest przeznaczona dla zaawansowanego użytkownika, autora filtra lub administratora, który chce przygotować .tplugin bez backendu administracyjnego.

Nie jest to najłatwiejsza metoda. Jest celowo dokładna i daje pełną kontrolę nad zawartością paczki.

Backend administracyjny jest wygodniejszy, ale nie jest wymagany.

## 1. Wymagania

Potrzebne są:
- działający filtr Okapi lub inny zgodny runtime;
- JAR entrypointu;
- znane zależności;
- Python 3 do wygenerowania checksumów;
- znajomość struktury TPlugin.

Do instalacji TPlugin przez Tłumacza nadal potrzebna jest JVM/JRE, ponieważ FilterHost uruchamia filtry Java.

## 2. Minimalna struktura

    my-filter/
    ├── plugin.json
    ├── filter/
    │   └── runtime.jar
    ├── inventory.json
    └── checksums.json

plugin.json jest manifestem runtime.

Przykład:

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
        "jar": "filter/runtime.jar"
      }
    }

## 3. Entry point

Pole entrypoint.jar wskazuje JAR, który FilterHost ma uruchomić.

Ścieżka musi znajdować się wewnątrz paczki. Nie należy używać ../runtime.jar, /tmp/runtime.jar ani innych ścieżek wychodzących poza katalog pluginu.

## 4. Zależność bundled — A

Zależność prywatna pozostaje wewnątrz pluginu.

Przykład:

    filter/
    ├── runtime.jar
    └── lib/
        └── helper.jar

Manifest:

    "dependencies": {
      "bundled": [
        {
          "id": "example:helper",
          "version": "1.0.0",
          "file": "filter/lib/helper.jar"
        }
      ],
      "shared": [],
      "engine": []
    }

Ta biblioteka należy wyłącznie do pluginu.

## 5. Zależność shared — B

Biblioteka współdzielona trafia do paczki jako materiał wejściowy instalatora.

Przykład:

    lib-shared/
    └── common-io-3.12.0.jar

Manifest:

    "dependencies": {
      "bundled": [],
      "shared": [
        {
          "id": "com.twelvemonkeys.common:common-io",
          "version": "3.12.0",
          "source": "lib-shared/common-io-3.12.0.jar",
          "file": "lib-shared/common-io-3.12.0.jar"
        }
      ],
      "engine": []
    }

Podczas instalacji biblioteka jest deduplikowana w centralnym:

    $HOME/.config/tlumacz/filter-engine/shared-libs/

Tożsamość stanowi id + version + SHA-256. Ta sama wersja z innym SHA-256 jest konfliktem.

## 6. Entrypoint jako shared

Możliwy jest szczególny przypadek, w którym główny JAR jest traktowany jako shared.

Manifest może wskazywać:

    "entrypoint": {
      "kind": "okapi-filter",
      "jar": "lib-shared/runtime-filter.jar"
    }

oraz:

    "shared": [
      {
        "id": "net.sf.okapi:runtime-example",
        "version": "1.49.0-SNAPSHOT",
        "source": "lib-shared/runtime-filter.jar",
        "file": "lib-shared/runtime-filter.jar"
      }
    ]

Instalator przenosi artefakt do centralnego shared-libs, a FilterHost rozwiązuje entrypoint przez deklarację shared.

## 7. Zależność engine — C

Zależności C są dostarczane przez wspólny Filter Engine.

Przykład:

    "engine": [
      {
        "id": "okapi-filter-host",
        "version": "1.49.0-SNAPSHOT"
      }
    ]

Nie należy kopiować takich bibliotek do pluginu, jeżeli kontrakt Filter Engine definiuje je jako zależność C.

## 8. Inventory

inventory.json jest raportem zawartości. Zawiera identyfikator, nazwę i wersję pluginu, klasy A/B/C, zależności oraz SHA-256.

Można przygotować inventory narzędziem:

    PYTHONPATH=src python3 tools/tplugin/dependencies.py inventory <katalog-pluginu>

lub z gotowej paczki:

    PYTHONPATH=src python3 tools/tplugin/dependencies.py inventory <plugin.tplugin>

## 9. Checksumy

checksums.json musi zawierać SHA-256 plików paczki.

Można wygenerować je Pythonem:

    python3 - <<'PY'
    import hashlib
    import json
    from pathlib import Path

    root = Path("my-filter")
    result = {}

    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "checksums.json":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            result[str(path.relative_to(root))] = digest

    (root / "checksums.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    PY

Nie umieszczaj checksums.json w samym wykazie checksumów.

## 10. ZIP i rozszerzenie .tplugin

.tplugin jest archiwum ZIP.

Nazwa:

    my-filter-1.0.0.tplugin

Najbezpieczniej zachować strukturę wygenerowaną przez TPluginBuilder jako wzorzec.

Przykładowo:

    my-filter-1.0.0.tplugin
    └── my-filter/
        ├── plugin.json
        ├── inventory.json
        ├── checksums.json
        └── filter/
            └── runtime.jar

## 11. Walidacja gotowej paczki

Przed publikacją:

    PYTHONPATH=src python3 tools/tplugin/dependencies.py validate my-filter-1.0.0.tplugin

Następnie:

    PYTHONPATH=src python3 tools/tplugin/dependencies.py inventory my-filter-1.0.0.tplugin

Walidacja musi zakończyć się sukcesem.

## 12. Test instalacyjny

Paczki nie należy testować wyłącznie przez rozpakowanie ZIP.

Należy wykonać:
1. instalację do pustego katalogu runtime;
2. wykrycie pluginu;
3. walidację entrypointu;
4. uruchomienie FilterHost;
5. extract;
6. merge;
7. round-trip dokumentu.

Dla filtra dokumentowego trzeba sprawdzić rzeczywisty dokument, a nie tylko obecność JAR-a.

## 13. Diagnostyka

### Brak entrypointu

Sprawdź plugin.json, entrypoint.jar i rzeczywistą ścieżkę JAR-a.

### Brak shared dependency

Sprawdź dependencies.shared[].id, dependencies.shared[].version, dependencies.shared[].file oraz obecność pliku w paczce.

### Konflikt checksumu

Jeżeli istnieje artifact_id + version, ale SHA-256 różni się od już zainstalowanej biblioteki, instalacja musi zostać odrzucona. Nie należy ręcznie nadpisywać istniejącego shared JAR-a.

### Problem z wersjami

Dwie wersje mogą współistnieć:

    artifact@1.49
    artifact@1.50

To nie jest konflikt. Konfliktem jest ta sama wersja z innym binarnym artefaktem.

## 14. Ręczny workflow autora filtra

    1. przygotuj JAR
    2. utwórz strukturę pluginu
    3. napisz plugin.json
    4. sklasyfikuj A/B/C
    5. umieść wymagane JAR-y
    6. wygeneruj inventory.json
    7. wygeneruj checksums.json
    8. utwórz ZIP
    9. zmień rozszerzenie na .tplugin
   10. uruchom validate
   11. zainstaluj do testowego runtime
   12. wykonaj extract/merge/round-trip
   13. dopiero wtedy publikuj

## 15. Zasada bezpieczeństwa

Nie należy publikować paczki tylko dlatego, że FilterHost potrafi znaleźć jej główny JAR.

Poprawna paczka musi mieć:
- poprawny manifest;
- poprawny entrypoint;
- jawne zależności;
- poprawną klasyfikację A/B/C;
- inventory;
- checksumy;
- pozytywną walidację;
- pozytywny test rzeczywistego działania filtra.
