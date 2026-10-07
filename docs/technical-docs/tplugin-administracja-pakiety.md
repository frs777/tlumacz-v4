# Backend administracyjny TPlugin

## Cel

Backend administracyjny służy do przygotowywania i kontroli paczek .tplugin. Jest częścią repozytorium projektu, ale nie jest częścią aplikacji Tłumacz.

Kod znajduje się w:

    tools/tplugin_admin/

Aplikacja końcowa nie importuje tego modułu.

## Odpowiedzialności

Backend:
1. tworzy szkielet projektu pluginu;
2. odczytuje deklarację tplugin-project.json;
3. waliduje entrypoint;
4. waliduje klasy zależności A/B/C;
5. blokuje niebezpieczne ścieżki;
6. wywołuje istniejący TPluginBuilder;
7. generuje inventory.json;
8. generuje checksums.json;
9. weryfikuje gotową paczkę;
10. pokazuje inventory.

Backend nie instaluje pluginu w aplikacji, nie instaluje Javy, nie pobiera zależności z internetu, nie modyfikuje runtime użytkownika i nie jest ładowany przez GUI Tłumacza.

## Struktura

    tools/tplugin_admin/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── project.py
    └── backend.py

project.py odpowiada za model projektu i walidację.
backend.py odpowiada za budowanie i walidację archiwów.
cli.py jest interfejsem administracyjnym.
__main__.py pozwala uruchomić moduł przez python -m tools.tplugin_admin.

## Format projektu

Projekt źródłowy ma plik tplugin-project.json. Jest to format administracyjny, a nie manifest runtime. Podczas budowania backend generuje właściwy plugin.json.

Przykład:

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

## CLI

Utworzenie projektu:

    PYTHONPATH=src:. python3 -m tools.tplugin_admin init my-filter \
      --id my-filter --name "Mój filtr" --version 1.0.0

Następnie umieść JAR filtra jako lib/runtime.jar i uruchom validate.

Walidacja:

    PYTHONPATH=src:. python3 -m tools.tplugin_admin validate my-filter

Kod 0 oznacza poprawny projekt, kod 2 błąd walidacji.

Budowanie:

    PYTHONPATH=src:. python3 -m tools.tplugin_admin build my-filter --output dist/

Weryfikacja:

    PYTHONPATH=src:. python3 -m tools.tplugin_admin verify dist/my-filter-1.0.0.tplugin

Inspekcja:

    PYTHONPATH=src:. python3 -m tools.tplugin_admin inspect dist/my-filter-1.0.0.tplugin

## Workflow administracyjny

    init
      ↓
    uzupełnienie JAR-ów
      ↓
    validate
      ↓
    build
      ↓
    verify
      ↓
    inspect
      ↓
    test instalacyjny
      ↓
    extract/merge/round-trip
      ↓
    publikacja

## Testy

Testy backendu znajdują się w tests/test_tplugin_admin.py.

Wdrożenie początkowej wersji: 8 passed. Po rozszerzeniu backendu: 11 passed.

## Test instalacyjny

Backend udostępnia `install_test()`. Narzędzie nie zmienia runtime użytkownika: tworzy tymczasowy magazyn, instaluje do niego paczkę przez produkcyjny `TPluginInstaller` i sprawdza:

- obecność pluginu i `plugin.json`;
- zgodność manifestu z paczką;
- usunięcie tymczasowego `lib-shared` po instalacji;
- poprawność rejestru referencji `shared-libs`;
- liczbę plików wynikającą z inventory.

CLI:

    PYTHONPATH=src:. python3 -m tools.tplugin_admin test-install dist/my-filter-1.0.0.tplugin

Kod 0 oznacza udany test instalacyjny. Kod 2 oznacza niepowodzenie.

## Raport publikacyjny

Polecenie `publish` wykonuje kompletny krok przedpublikacyjny:

    PYTHONPATH=src:. python3 -m tools.tplugin_admin publish my-filter --output dist/

Kolejność:

1. walidacja projektu;
2. budowa `.tplugin`;
3. walidacja inventory i checksumów;
4. instalacja w tymczasowym runtime;
5. weryfikacja layoutu i shared-libs;
6. obliczenie SHA-256 artefaktu;
7. zapis raportu `my-filter-1.0.0.publication.json`.

Raport jest maszynowo czytelny i zawiera status, identyfikację pluginu, SHA-256 paczki, inventory, wynik testu instalacyjnego, liczbę checksumów, ostrzeżenia i błędy. Raport nie jest częścią runtime Tłumacza.

## Stan wdrożenia

Backend administracyjny jest niezależnym narzędziem repozytorium i nie jest importowany przez `src/tlumacz`.

Weryfikacja po rozszerzeniu:
- `tests/test_tplugin_admin.py`: **11 passed**;
- CLI `init → validate → build → verify → inspect` pozostaje obsługiwany;
- dodano CLI `test-install` i `publish`;
- raport publikacyjny jest generowany po udanym teście instalacyjnym.

Backup przed rozszerzeniem:
`backups/tplugin-admin-20261006/pre-admin-completion.tar.gz`
SHA-256: `ed1ee03fffc3307ea19f36bedfcf249cec85c67fe3d998481c1d072a9829bf49`.


## Integracja z testami repozytorium

Ponieważ backend administracyjny znajduje się pod `tools/`, konfiguracja pytest zawiera `pythonpath = ["src", "."]`. Dzięki temu zwykłe `pytest -q` uruchamiane z katalogu repozytorium obejmuje testy backendu bez ręcznego ustawiania `PYTHONPATH`.
