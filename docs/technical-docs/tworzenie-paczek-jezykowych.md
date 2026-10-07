# Tworzenie paczek językowych Apertium

## 1. Przeznaczenie

Paczka językowa Apertium jest niezależnym artefaktem dystrybucyjnym jednego kierunku tłumaczenia. Narzędzia służące do jej przygotowania są wewnętrznymi narzędziami projektu i znajdują się w `tools/apertium/`; nie są częścią runtime aplikacji.

Pełna implementacja kontraktu instalacji znajduje się w `src/tlumacz/backends/apertium/packages.py`.

## 2. Narzędzia projektu

### `tools/apertium/package_pairs.py`

CLI automatyzujące cały proces:

- wybór lokalnego źródła pary,
- opcjonalne pobranie brakującego repozytorium z GitHub,
- opcjonalne uruchomienie istniejącego `Aperitium/apertium-get.py`,
- wykrycie kompletnych kierunków,
- budowę osobnej paczki dla każdego kierunku,
- generowanie sum SHA-256,
- opcjonalne oczyszczenie źródła z materiałów developerskich.

### `tools/apertium/package_pipeline.py`

Biblioteka pomocnicza CLI. Udostępnia:

- `discover_packagable_pairs()` — wykrywanie kompletnych kierunków,
- `build_all_packagable_packages()` — budowanie paczek,
- `clean_runtime_tree()` — oczyszczanie źródła.

### `src/tlumacz/backends/apertium/packages.py`

To nie jest narzędzie budowania poza aplikacją. Jest to aktywny moduł backendu zawierający kontrakt paczki, builder, installer i weryfikację checksum. Nie należy go usuwać ani przenosić do `tools/` bez zmiany architektury runtime.

## 3. Warunek kompletności pary

`package_pipeline.py` analizuje `modes.xml` źródła. Kierunek jest pakowalny, gdy:

1. nazwa kierunku pasuje do `source-target`, gdzie oba identyfikatory mają 2–3 małe litery;
2. mode ma `install="yes"`, chyba że użyto `--include-unmarked`;
3. wszystkie pliki wskazane przez elementy `<file>` istnieją w źródle;
4. istnieje `modes/<pair>.mode`.

Przy braku kompletnych danych kierunek nie jest pakowany.

## 4. Format paczki

Nazwa artefaktu:

```text
apertium-eng-pol-1.0.0.tar
```

Archiwum jest niekompresowanym TAR.

Katalog główny archiwum:

```text
apertium-eng-pol/
```

Przykładowa zawartość:

```text
apertium-eng-pol/
├── manifest.json
├── checksums.json
├── COPYING lub LICENSE lub LICENSE.txt
├── modes.xml
├── modes/
│   └── eng-pol.mode
└── eng-pol.*
```

Builder kopiuje wyłącznie pliki wskazane przez mode dla danego kierunku, a `modes.xml` ogranicza do jednego mode.

## 5. Rzeczywisty manifest

Builder zapisuje manifest zgodny z `ApertiumPairPackageManifest`:

```json
{
  "format": "apertium-pair",
  "format_version": 1,
  "id": "apertium-eng-pol",
  "name": "apertium-eng-pol",
  "version": "1.0.0",
  "pair": "eng-pol",
  "source": "eng",
  "target": "pol"
}
```

`id` musi mieć postać `apertium-<pair>`, a `pair` musi zawierać dokładnie jeden separator `-`.

## 6. Licencja

Builder wymaga znalezienia rzeczywistego pliku licencji. Automatycznie rozpoznaje:

```text
COPYING
LICENSE
LICENSE.txt
```

Można również przekazać konkretny plik przez parametr `license_source` przy bezpośrednim użyciu buildera.

Licencji nie wolno zgadywać. Jeżeli builder nie znajdzie pliku licencji, budowanie kończy się błędem.

## 7. Przenośność mode

Builder normalizuje absolutny katalog źródłowy w pliku `.mode`, aby paczka nie zawierała ścieżek z maszyny budującej.

Po przygotowaniu paczki należy dodatkowo sprawdzić, czy mode nie zawiera innych nieprzenośnych ścieżek.

## 8. Checksumy

Wewnątrz paczki znajduje się `checksums.json` zawierający SHA-256 wszystkich plików paczki poza samym `checksums.json`.

Obok TAR tworzony jest:

```text
apertium-eng-pol-1.0.0.tar.sha256
```

CLI dodatkowo tworzy zbiorczy:

```text
$HOME/.config/tlumacz/apertium/SHA256SUMS
```

## 9. Najprostsze użycie narzędzia

Jeżeli repozytorium źródłowe pary znajduje się już w `Aperitium/apertium-eng-pol`:

```bash
python3 tools/apertium/package_pairs.py eng-pol --output $HOME/.config/tlumacz/apertium --version 1.0.0
```

Jeżeli przed pakowaniem trzeba uruchomić istniejący mechanizm kompilacji:

```bash
python3 tools/apertium/package_pairs.py eng-pol --compile --output $HOME/.config/tlumacz/apertium --version 1.0.0
```

Jeżeli brakujące repozytorium ma zostać pobrane z GitHub:

```bash
python3 tools/apertium/package_pairs.py eng-pol --download --compile --output $HOME/.config/tlumacz/apertium --version 1.0.0
```

Jeżeli trzeba uwzględnić kompletne mode bez `install="yes"`:

```bash
python3 tools/apertium/package_pairs.py eng-pol --include-unmarked --output $HOME/.config/tlumacz/apertium --version 1.0.0
```

Opcjonalne oczyszczenie źródła po udanym pakowaniu:

```bash
python3 tools/apertium/package_pairs.py eng-pol --compile --clean-runtime --output $HOME/.config/tlumacz/apertium --version 1.0.0
```

`--clean-runtime` należy stosować ostrożnie, ponieważ usuwa ze źródła pliki uznane za zbędne względem zachowanych danych runtime.

## 10. Praca z lokalnym katalogiem źródłowym

Można ominąć wyszukiwanie `Aperitium/apertium-<pair>` i wskazać katalog bezpośrednio:

```bash
python3 tools/apertium/package_pairs.py \
  --source /ścieżka/do/apertium-eng-pol \
  --output $HOME/.config/tlumacz/apertium \
  --version 1.0.0
```

W tym trybie nie trzeba podawać pozycyjnego identyfikatora pary. Para jest wykrywana z `modes.xml`.

## 11. Pakowanie wielu kierunków z jednego źródła

Jeżeli jedno źródło zawiera kilka kompletnych kierunków, pipeline wykrywa je wszystkie i tworzy osobny TAR dla każdego z nich.

Przykładowo:

```text
jedno źródło
   ├── eng-pol
   └── pol-eng
        ↓
   apertium-eng-pol-1.0.0.tar
   apertium-pol-eng-1.0.0.tar
```

Zasada pozostaje: **jeden kierunek = jeden plugin = jeden TAR**.

## 12. Weryfikacja po budowaniu

Najpierw sprawdź artefakt:

```bash
tar -tf $HOME/.config/tlumacz/apertium/apertium-eng-pol-1.0.0.tar
sha256sum -c $HOME/.config/tlumacz/apertium/apertium-eng-pol-1.0.0.tar.sha256
```

Sprawdź również przenośność mode:

```bash
tar -xf $HOME/.config/tlumacz/apertium/apertium-eng-pol-1.0.0.tar -C /tmp
```

oraz wyszukaj niepożądane ścieżki absolutne w rozpakowanym katalogu.

Najważniejszym testem jest jednak instalacja przez rzeczywisty `ApertiumPairPackageInstaller` i ponowne wykrycie pary przez discovery. Samo utworzenie poprawnego TAR nie dowodzi poprawności paczki runtime.

## 13. Instalacja i walidacja runtime

Installer:

1. wymaga zewnętrznego `.tar.sha256`;
2. sprawdza SHA-256 całego TAR;
3. bezpiecznie rozpakowuje archiwum;
4. wymaga dokładnie jednego katalogu głównego;
5. waliduje manifest;
6. sprawdza zgodność nazwy katalogu z manifestem;
7. sprawdza `checksums.json`;
8. wymaga właściwego `modes/<pair>.mode` i `modes.xml`;
9. instaluje pakiet do magazynu Apertium;
10. kopiuje mode do wspólnego katalogu `modes/`.

Installer odrzuca m.in. niebezpieczne ścieżki TAR oraz dowiązania symboliczne i twarde.

## 14. Aktualny magazyn paczek

Docelowy magazyn użytkownika:

```text
$HOME/.config/tlumacz/apertium/
```

Gotowe artefakty dystrybucyjne projektu są przechowywane w:

```text
$HOME/.config/tlumacz/apertium/
```

## 15. Procedura ręczna

Jeżeli automatyczne narzędzie nie jest używane, kolejność jest następująca:

```text
1. przygotuj skompilowane dane jednej pary
2. sprawdź modes.xml
3. sprawdź modes/<pair>.mode
4. wybierz rzeczywisty plik licencji
5. utwórz katalog apertium-<pair>
6. skopiuj wyłącznie dane wymagane przez mode
7. ogranicz modes.xml do jednego kierunku
8. usuń ścieżki absolutne zależne od maszyny budującej
9. utwórz manifest zgodny z kontraktem
10. utwórz checksums.json
11. utwórz niekompresowany TAR
12. utwórz .tar.sha256
13. zweryfikuj TAR i checksumy
14. wykonaj instalację testową
15. wykonaj discovery
```

Procedura automatyczna z `tools/apertium/package_pairs.py` realizuje większość tych czynności i jest zalecaną metodą dla seryjnego przygotowywania paczek.

## 16. Aktualny stan projektu

Projekt posiada przygotowane osobne paczki językowe w katalogu `$HOME/.config/tlumacz/apertium/`. Dokumentacja techniczna procesu znajduje się w `docs/technical-docs/apertium-pair-packages.md` oraz w niniejszym pliku.
