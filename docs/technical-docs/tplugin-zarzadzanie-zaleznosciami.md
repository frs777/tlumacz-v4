---
id: tplugin-dependency-management
status: active
meta:
  contentType: TechnicalDesign
  category: architecture
version: 1.0
updated: 2026-10-07
owner: filter-engine
source: src/tlumacz/filter_engine/tplugin.py
depends_on:
  - docs/technical-docs/plugin-okapi-filter.md
  - docs/wdrozenia/wdrozenie-tplugin.md
  - docs/TODO.md
expires_when: zmiana kontraktu TPlugin lub magazynu shared-libs
last_validation: "pytest tests/test_tplugin.py: 16 passed; walidacja 9/9 paczek"
---

# System zarządzania zależnościami TPlugin

> **Nadrzędny kontrakt od 2026-10-07:** historyczny model centralnego shared-libs w profilu użytkownika nie obowiązuje. Pakiety użytkownika pozostają bezpośrednio w /home/frs/.config/tlumacz/filters, a wspólne biblioteki runtime są częścią drzewa src/tlumacz/resources/okapi-runtime/lib. Szczegółowa aktualna instrukcja: docs/technical-docs/tplugin-specyfikacja-reczne-tworzenie.md.


## 1. Cel

System zarządza zależnościami filtrów Okapi bez instalowania bibliotek systemowych i bez pobierania zależności podczas instalacji pluginu.

Rozdzielone są cztery odpowiedzialności:

1. manifest deklaruje zależności i ich klasę;
2. shared-libs przechowuje fizyczne artefakty współdzielone;
3. rejestr referencji określa, które pluginy używają konkretnego artefaktu;
4. narzędzia packaging budują inventory, sprawdzają checksumy i przygotowują paczki.

Paczka jest samowystarczalna względem zadeklarowanych zależności A/B. Zależności C należą do wspólnego Filter Engine.

## 2. Klasy zależności

| Klasa | Znaczenie | Miejsce po instalacji |
|---|---|---|
| A — bundled | zależność prywatna pluginu | katalog pluginu |
| B — shared | zależność współdzielona | shared-libs/ |
| C — engine | zależność dostarczana przez Filter Engine | poza paczką |

Klasa B jest identyfikowana przez artifact_id + version + SHA-256.

Ten sam identyfikator i wersja z innym SHA-256 oznaczają konflikt i blokują instalację. Różne wersje tego samego artefaktu mogą współistnieć.

## 3. Tożsamość artefaktu

Kanoniczny klucz ma postać:

    artifact_id@version

Fizyczna nazwa ma postać:

    <artifact_id>--<version>.<suffix>

Identyfikatory Maven są normalizowane do bezpiecznej nazwy pliku przez zamianę : i / na _.

SHA-256 jest dowodem integralności i nie zastępuje wersji.

## 4. Rejestr referencji

Runtime posiada:

    $HOME/.config/tlumacz/filter-engine/shared-libs/index.json

Przykład:

    {
      "version": 1,
      "artifacts": {
        "net.sf.okapi:runtime-html@1.49.0-SNAPSHOT": {
          "id": "net.sf.okapi:runtime-html",
          "version": "1.49.0-SNAPSHOT",
          "file": "net.sf.okapi_runtime-html--1.49.0-SNAPSHOT.jar",
          "sha256": "...",
          "references": ["epub", "html", "markdown"]
        }
      }
    }

Źródłem prawdy o wymaganiach pluginu pozostaje plugin.json. index.json jest indeksem runtime i może zostać odbudowany.

## 5. Lifecycle

### Instalacja

    .tplugin
      ↓
    bezpieczna ekstrakcja
      ↓
    manifest + entrypoint
      ↓
    walidacja zależności
      ↓
    shared-libs: deduplikacja po id/version/SHA-256
      ↓
    plugin rozpakowany
      ↓
    rejestr referencji

Instalator nie pobiera bibliotek z internetu.

### Aktualizacja

Przed aktualizacją wykonywany jest backup. Nowy manifest może wskazywać inną wersję shared library. Stara referencja jest usuwana, a nowa rejestrowana.

### Odinstalowanie

Uninstall usuwa plugin i jego referencje, ale nie usuwa automatycznie shared-libs. Pozwala to wykonać rollback bez ponownego pozyskiwania zależności.

### Rollback

Rollback przywraca plugin z backupu oraz ponownie rejestruje jego shared dependencies.

### Garbage collection

GC usuwa wyłącznie artefakty bez referencji.

Bezpieczny podgląd:

    PYTHONPATH=src python3 tools/tplugin/dependencies.py gc $HOME/.config/tlumacz/filter-engine --dry-run

Usuwanie następuje dopiero bez --dry-run.

## 6. Izolacja classloaderów

Współistnienie wersji nie oznacza jednego wspólnego classpath.

shared-libs rozwiązuje fizyczne przechowywanie i deduplikację, natomiast FilterHost utrzymuje izolację pluginów i dobiera zależności dla konkretnego pluginu.

W efekcie runtime-html w wersji 1.49 i 1.50 może istnieć równocześnie. Konflikt tej samej wersji z innym SHA-256 jest błędem integralności.

## 7. Inventory

Każda budowana paczka zawiera inventory.json.

Inventory opisuje:

- identyfikator, nazwę i wersję pluginu;
- liczbę zależności A/B/C;
- zależności z id, version, file i source;
- SHA-256 plików;
- SHA-256 zależności plikowych;
- listę plików artefaktu.

## 8. checksums.json

Builder tworzy checksums.json dla wszystkich plików paczki z wyjątkiem samego pliku checksumów.

Walidator:

1. bezpiecznie rozpakowuje archiwum;
2. odnajduje plugin.json;
3. odczytuje checksums.json;
4. odrzuca path traversal;
5. oblicza SHA-256;
6. blokuje paczkę przy różnicy checksumu.

## 9. Narzędzia

- tools/tplugin/build.py — pojedynczy plugin;
- tools/tplugin/build_all.py — cały zestaw filtrów;
- tools/tplugin/dependencies.py — inventory, validate, rebuild i GC.

Polecenia:

    inventory <plugin|archive>
    validate <archive>
    rebuild <runtime-root>
    gc <runtime-root> --dry-run
    gc <runtime-root>

## 10. Proces publikacji

    źródło pluginu
       ↓
    manifest + A/B/C
       ↓
    builder
       ↓
    inventory.json
       ↓
    checksums.json
       ↓
    .tplugin
       ↓
    validate
       ↓
    test instalacyjny w pustym runtime
       ↓
    capability / extract / merge / round-trip
       ↓
    publikacja

Publikacja jest dozwolona dopiero po walidacji checksumów i teście instalacyjnym.

## 11. Polityka konfliktów

| Sytuacja | Decyzja |
|---|---|
| ten sam id+version, ten sam SHA-256 | deduplikacja |
| ten sam id+version, różny SHA-256 | błąd i blokada |
| ten sam id, różne wersje | współistnienie |
| uninstall przy innych referentach | biblioteka pozostaje |
| uninstall ostatniego referenta | biblioteka pozostaje do GC |
| GC artefaktu z referencją | niedozwolone |
| brak rejestru | rebuild z plugin.json |

## 12. Bezpieczeństwo

System zachowuje:

- ochronę ZIP/TAR przed path traversal;
- checksum przy współdzieleniu;
- atomowy zapis index.json;
- brak pobierania zależności w instalatorze;
- backup przed lifecycle update/uninstall/rollback;
- GC tylko dla artefaktów bez referencji.

## 13. Dowody wdrożenia 2026-10-06

- tests/test_tplugin.py: 16 passed;
- walidacja paczek: 9/9;
- builder zbiorczy wygenerował 9/9 paczek;
- inventory.json jest generowany przez builder;
- runtime otrzymał rejestr referencji dla aktywnych pluginów;
- gc --dry-run wykazał 0 artefaktów do usunięcia.

Backup kodu i dokumentacji:

    backups/tplugin-dependency-management-20261006/pre-dependency-management.tar.gz
    SHA-256: 824b01584ff6649d724bb53164dceee93bbb133953ba7132a1e704184c170815

Backup runtime przed odbudową rejestru:

    backups/tplugin-dependency-management-20261006/runtime-before-reference-index.tar.gz
    SHA-256: cddcc98dc981a331386d5e9802629acc449ddc233ef469e97a168eeaf214c233

## 14. Granice systemu

Ta faza nie obejmuje:

- automatycznego pobierania zależności z Maven Central;
- semver range resolution;
- automatycznej analizy transitive dependencies z JAR manifestów;
- podpisu kryptograficznego paczek;
- automatycznego dowodzenia kompatybilności API pomiędzy wersjami Okapi.

Nie są one potrzebne do bezpiecznego zarządzania obecnym zestawem 9 pluginów.
