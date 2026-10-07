## Usunięcie duplikatu danych językowych z bundlowanego runtime'u

Dane językowe Apertium nie są już przechowywane drugi raz w `native_runtime/share/apertium/`. Bundlowany runtime zawiera wyłącznie komponenty wykonawcze; paczki językowe są dostarczane jako `.tar` wraz z `.tar.sha256` w `$HOME/.config/tlumacz/apertium/` i materializowane tymczasowo podczas użycia.

## Aktualny model magazynu paczek — TAR-only

Magazyn użytkownika $HOME/.config/tlumacz/apertium/ przechowuje wyłącznie paczki .tar oraz ich zewnętrzne pliki .tar.sha256. Aplikacja nie tworzy trwałej kopii rozpakowanej. Podczas inicjalizacji runtime weryfikuje archiwa i materializuje ich zawartość w tymczasowym katalogu roboczym poza magazynem; ścieżka tego katalogu jest przekazywana do Apertium jako APERTIUM_DATADIR/-d.

# Prywatny runtime Apertium

Runtime jest artefaktem aplikacji dla Linux x86_64 z Apertium 3.9.12.

## Układ

```text
native_runtime/
├── bin/                    # prywatne Apertium i narzędzia pipeline
├── lib/                    # biblioteki runtime'u
├── libexec/apertium-real   # skrypt Apertium 3.9.12
├── launcher/               # źródło małego launchera binarnego
├── LICENSES/               # licencja danych Apertium
├── MANIFEST
└── VERSION
```

Launcher uruchamia prywatny `bash`, ustawia prywatny `PATH` i obsługuje `-d`
kierując proces do katalogu danych konkretnej wtyczki językowej. Dzięki temu
tryby Apertium mogą zawierać ścieżki względne i pozostają relokowalne.

## Dane językowe

Paczki językowe nie są częścią runtime'u. Są osobnymi wtyczkami w:

```text
$HOME/.config/tlumacz/apertium/
```

lub w `${XDG_CONFIG_HOME:-$HOME/.config}/tlumacz/apertium/`.

Tryby wtyczek muszą wskazywać pliki danych względnie względem katalogu
pakietu. Nie wolno zapisywać do nich ścieżek z katalogu źródłowego dewelopera.

## Pochodzenie

Aktualny artefakt został zbudowany lokalnie z Apertium 3.9.12 dostępnego na
maszynie buildowej. `MANIFEST` zapisuje wersję, platformę i zestaw dołączonych
poleceń. Przed wydaniem należy uzupełnić pełny audyt licencji/NOTICE wszystkich
bibliotek i narzędzi znajdujących się w `lib/` i `bin/`.

Runtime nie korzysta z `/usr/bin/apertium`, `/usr/bin/bash` ani innych
systemowych narzędzi Apertium podczas uruchomienia. ELF-y używają systemowego
loadera glibc jako granicy platformy Linux; pozostałe biblioteki Apertium są
dołączone do `lib/`.

## Weryfikacja

Sprawdzone lokalnie:

- `bin/apertium -V` → `Apertium 3.9.12`;
- `PATH=/nonexistent` + `eng-spa` → `Hola Mundo!`;
- relokowany pakiet `eng-spa` działa po skopiowaniu do `/tmp`;
- `-f html` zachowuje strukturę HTML;
- testy backendu i integracji Apertium: `20 passed`.

Nie umieszczaj tutaj niezweryfikowanych binariów. Po zmianie wersji runtime'u
należy odtworzyć manifest, sumy kontrolne, audyt zależności i test relokacji.

## Stan architektury po migracji 2026-10-07

Dane 27 kierunków objętych release scope są teraz bundlowane bezpośrednio w:
src/tlumacz/backends/apertium/native_runtime/share/apertium/

Każdy kierunek ma własny katalog apertium-<para>/, a jego tryb jest dodatkowo
synchronizowany do wspólnego share/apertium/modes/. ces-pol pozostaje poza
bundlowanym release scope z powodu wcześniej potwierdzonej awarii modelu taggera.

Domyślny ApertiumRuntime korzysta z tego katalogu danych. Katalog
$HOME/.config/tlumacz/apertium/ nie jest już automatycznie wybierany przez runtime;
może być użyty wyłącznie przez jawnie przekazaną konfigurację. Bridge GUI
również domyślnie wskazuje dane bundlowane.

Weryfikacja migracji 2026-10-07:
- Apertium 3.9.12 uruchamia się z prywatnego native_runtime/bin/apertium;
- PATH=/nonexistent nie blokuje uruchomienia;
- runtime wykrywa 27 kierunków;
- smoke prywatnego runtime'u: 27 READY / 0 FAIL;
- E2E adaptera en → pl z pustym systemowym PATH: PASS;
- focused testy po migracji: 24 passed.
