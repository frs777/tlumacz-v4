## Aktualny model magazynu paczek — TAR-only

Magazyn użytkownika $HOME/.config/tlumacz/apertium/ przechowuje wyłącznie paczki .tar oraz ich zewnętrzne pliki .tar.sha256. Aplikacja nie tworzy trwałej kopii rozpakowanej. Podczas inicjalizacji runtime weryfikuje archiwa i materializuje ich zawartość w tymczasowym katalogu roboczym poza magazynem; ścieżka tego katalogu jest przekazywana do Apertium jako APERTIUM_DATADIR/-d.

# Paczki par językowych Apertium

**Status:** obowiązujący kontrakt formatu i pipeline'u  
**Data audytu:** 2026-10-06  
**Format dystrybucyjny:** niekompresowany `.tar`  
**Magazyn runtime:** `$HOME/.config/tlumacz/apertium/`

## 1. Model dystrybucji
## 1.1. Magazyn użytkownika i sposób użycia przez aplikację

Docelowy magazyn artefaktów dystrybucyjnych to:

    $HOME/.config/tlumacz/apertium/
    ├── apertium-eng-pol-1.0.0.tar
    ├── apertium-eng-pol-1.0.0.tar.sha256
    ├── apertium-eng-pol/
    └── ...

Archiwa .tar są właściwym formatem dystrybucyjnym. Aplikacja nie uruchamia
TAR bezpośrednio: przed discovery sprawdza SHA-256 całego archiwum, a następnie
rozpakowuje brakujące paczki do tego samego magazynu. Rozpakowane katalogi są
wewnętrzną postacią roboczą używaną przez ApertiumRuntime; nie zastępują
artefaktów .tar.

Stary katalog $HOME/.config/tlumacz/apertium/ nie jest używany; właściwym magazynem jest $HOME/.config/tlumacz/apertium/.


**Jedna paczka = jeden kierunek tłumaczenia.**

Jeżeli źródłowy projekt Apertium obsługuje dwa kierunki, np. `eng-spa` i `spa-eng`, powstają dwa niezależne artefakty:

```text
apertium-eng-spa-1.0.0.tar
apertium-spa-eng-1.0.0.tar
```

Nie tworzymy wspólnej paczki zawierającej kilka kierunków.

Tar jest kontenerem transportowym, nie mechanizmem kompresji. Paczki są tworzone jako zwykły, niekompresowany tar.

## 2. Zawartość paczki

Paczka zawiera wyłącznie dane potrzebne przez wybrany tryb:

```text
apertium-eng-spa-1.0.0.tar
└── apertium-eng-spa/
    ├── manifest.json
    ├── checksums.json
    ├── COPYING
    ├── modes.xml
    ├── modes/
    │   └── eng-spa.mode
    ├── eng-spa.automorf.bin
    ├── eng-spa.prob
    ├── eng-spa.autobil.bin
    ├── eng-spa.t1x.bin
    ├── ...
    └── pliki źródłowe transferu wymagane przez mode
```

Builder **filtruje `modes.xml` do jednego wybranego trybu**. Nie przenosi definicji pozostałych kierunków.

Do paczki nie trafiają:

- `.git/`;
- `dev/`;
- `test/`;
- `eval/`;
- cache kompilacji;
- `Makefile`, `configure`, `autom4te.cache`;
- źródłowe słowniki i inne pliki niewskazane przez wybrany mode;
- dane innego kierunku.

Pliki źródłowe `.t1x`, `.t2x`, `.t3x` są zachowywane **tylko wtedy, gdy wybrany mode odwołuje się do nich bezpośrednio**. Nie jest to przypadkowe pozostawienie źródeł: runtime Apertium wykorzystuje te pliki razem z odpowiadającymi binariami.

## 3. Manifest i checksum

`manifest.json` identyfikuje dokładnie jeden kierunek:

```json
{
  "format": "apertium-pair",
  "format_version": 1,
  "id": "apertium-eng-spa",
  "name": "apertium-eng-spa",
  "version": "1.0.0",
  "pair": "eng-spa",
  "source": "eng",
  "target": "spa"
}
```

`checksums.json` zawiera SHA-256 wszystkich plików paczki poza samym `checksums.json`.

Instalator sprawdza również:

- jeden katalog główny;
- zgodność katalogu z manifestem;
- brak ścieżek absolutnych i `..`;
- brak symlinków i hardlinków;
- kompletność checksum;
- obecność `modes.xml` i właściwego `.mode`.

## 4. Kod

Format i instalator:

```text
src/tlumacz/backends/apertium/packages.py
```

Pipeline:

```text
tools/apertium/package_pipeline.py
```

CLI:

```text
tools/apertium/package_pairs.py
```

Testy:

```text
tests/test_apertium_packages.py
tests/test_apertium_package_pipeline.py
```

## 5. Automatyczne przygotowanie paczek

### Z lokalnego checkoutu

```bash
python3 tools/apertium/package_pairs.py   --source /ścieżka/do/apertium-eng-spa   --output $HOME/.config/tlumacz/apertium   --version 1.0.0
```

Jeżeli źródło ma kompletne dwa kierunki, powstaną dwa pliki.

### Pobranie z Internetu i kompilacja

```bash
python3 tools/apertium/package_pairs.py   eng-spa   --download   --compile   --output $HOME/.config/tlumacz/apertium   --version 1.0.0
```

Pipeline:

```text
GitHub
  ↓
git clone apertium-<pair>
  ↓
istniejący apertium-get.py
  ↓
pobranie zależności
  ↓
autoreconf/configure/make
  ↓
wykrycie kompletnych mode
  ↓
wybór każdego kierunku osobno
  ↓
manifest + SHA-256
  ↓
niekompresowany .tar
  ↓
SHA256SUMS
```

Nie zmieniono oryginalnego `Apertium/apertium-get.py`. Dodano warstwę orkiestracji nad nim, aby nie mieszać upstreamowego mechanizmu pobierania/kompilacji z naszym formatem dystrybucyjnym.

### Czyszczenie po spakowaniu

```bash
python3 tools/apertium/package_pairs.py   --source /ścieżka/do/apertium-eng-spa   --output $HOME/.config/tlumacz/apertium   --version 1.0.0   --clean-runtime
```

Opcja usuwa ze źródła materiały, które nie są potrzebne do runtime'u zachowanych, kompletnych kierunków.

**Uwaga:** `--clean-runtime` jest operacją destrukcyjną dla wskazanego katalogu. Przed użyciem na repozytorium źródłowym należy wykonać backup. W praktyce dla dystrybucji Tłumacza stosujemy ją do magazynu runtime `$HOME/.config/tlumacz/apertium/`, a repozytoria źródłowe `Apertium/` zachowujemy do kolejnych kompilacji.

## 6.1. Przenośność pliku `modes/<pair>.mode`

Paczka nie może utrwalać absolutnych ścieżek środowiska budowania. Builder normalizuje argumenty ścieżkowe wygenerowanego `.mode` do nazw plików znajdujących się w katalogu paczki. Dzięki temu paczka zbudowana na jednym hoście może zostać zainstalowana na innym.

Regresja znajduje się w `tests/test_apertium_packages.py` i sprawdza, że absolutny katalog źródłowy nie trafia do artefaktu.

## 6. Wykrywanie gotowych kierunków

`discover_packagable_pairs()` uznaje kierunek za gotowy, jeżeli:

1. mode ma standardową nazwę `source-target`;
2. mode ma `install="yes"`;
3. wszystkie pliki `<file>` z mode istnieją;
4. istnieje odpowiadający `modes/<pair>.mode`.

Tryby pomocnicze, np. `eng-spa-chunker`, nie są traktowane jako osobne pary.

Dla wyjątków, w których upstream nie ustawia `install="yes"`, dostępne jest `include_unmarked=True`. Stosujemy to tylko po ręcznej weryfikacji. Nie jest to obecnie wykorzystywane dla publikowanej pary.

## 7. Pary dwukierunkowe

Jeżeli oba mode są kompletne, builder tworzy dwa artefakty. Nie ma znaczenia, czy pochodzą z jednego repozytorium.

Przykład:

```text
apertium-eng-cat/
    eng-cat  -> apertium-eng-cat-1.0.0.tar
    cat-eng  -> apertium-cat-eng-1.0.0.tar
```

To samo dotyczy wszystkich innych par dwukierunkowych.

## 8. Aktualny audyt 2026-10-06

W lokalnych checkoutach `Apertium/` znaleziono kompletne, już skompilowane kierunki:

| Rodzina | Kierunki |
|---|---|
| Bengali ↔ English | `bn-en`, `en-bn` |
| English ↔ Catalan | `eng-cat`, `cat-eng` |
| English ↔ German | `eng-deu`, `deu-eng` |
| English ↔ Italian | `eng-ita`, `ita-eng` |
| English ↔ Spanish | `eng-spa`, `spa-eng` |
| English ↔ Portuguese | `en-pt`, `pt-en` |
| Polish ↔ Kashubian | `pl-csb`, `csb-pl` |
| Polish ↔ Slovak | `pl-sk`, `sk-pl` |
| Polish ↔ Czech | `pol-ces`, `ces-pol` |
| Polish ↔ Russian | `pol-rus`, `rus-pol` |
| Polish ↔ Silesian | `pol-szl`, `szl-pol` |
| Polish ↔ Ukrainian | `pol-ukr`, `ukr-pol` |
| Polish ↔ Spanish | `pol-spa`, `spa-pol` |
| English → Polish | `eng-pol` |

Łącznie przygotowano **28 publikowalnych kierunków**.

## 9. Gotowe artefakty

Katalog:

```text
$HOME/.config/tlumacz/apertium/
```

zawiera 28 niekompresowanych archiwów:

```text
apertium-bn-en-1.0.0.tar
apertium-en-bn-1.0.0.tar
apertium-cat-eng-1.0.0.tar
apertium-eng-cat-1.0.0.tar
apertium-ces-pol-1.0.0.tar
apertium-pol-ces-1.0.0.tar
apertium-csb-pl-1.0.0.tar
apertium-pl-csb-1.0.0.tar
apertium-deu-eng-1.0.0.tar
apertium-eng-deu-1.0.0.tar
apertium-eng-ita-1.0.0.tar
apertium-ita-eng-1.0.0.tar
apertium-eng-pol-1.0.0.tar
apertium-eng-spa-1.0.0.tar
apertium-spa-eng-1.0.0.tar
apertium-en-pt-1.0.0.tar
apertium-pt-en-1.0.0.tar
apertium-pl-sk-1.0.0.tar
apertium-sk-pl-1.0.0.tar
apertium-pol-rus-1.0.0.tar
apertium-rus-pol-1.0.0.tar
apertium-pol-spa-1.0.0.tar
apertium-spa-pol-1.0.0.tar
apertium-pol-szl-1.0.0.tar
apertium-szl-pol-1.0.0.tar
apertium-pol-ukr-1.0.0.tar
apertium-ukr-pol-1.0.0.tar
```

Każdy ma odpowiadający plik `.sha256`; `SHA256SUMS` zawiera sumy całego zestawu.

## 10. Pary niegotowe

### `pol-eng`

Para została naprawiona i opublikowana jako `apertium-pol-eng-1.0.0.tar`.

Pierwsza blokada wynikała z odwołania do `a_SN` w `apertium-eng-pol.pol-eng.t3x` bez deklaracji tego atrybutu. Dodano `a_SN` z wartością `PDET`. Następnie pełna kompilacja ujawniła brak wygenerowanego `pol-eng.autogen.bin`; bezpośrednie `lt-comp rl` poprawnie wygenerowało ten artefakt mimo ostrzeżeń walidatora o duplikatach `pardef` w słowniku polskim.

Weryfikacja końcowa: `pol-eng.t1x.bin`, `pol-eng.t2x.bin`, `pol-eng.t3x.bin`, `pol-eng.autogen.bin` i pozostałe pliki wymagane przez mode są obecne. Paczka została zainstalowana do czystego magazynu, wykryta jako `pol-eng`, a rzeczywisty runtime Apertium wykonał tłumaczenie testowe `pl → en`.

### `pol-src`

To lokalny moduł językowy/źródłowy z trybami morfologicznymi, a nie kompletny kierunek tłumaczenia. Nie tworzymy z niego paczki pary.


## 11. Porządkowanie magazynu runtime

Po przygotowaniu paczek magazyn:

```text
$HOME/.config/tlumacz/apertium/
```

został oczyszczony z materiałów developerskich.

Usunięto m.in.:

- `.git/`;
- `dev/`;
- `test/`;
- `eval/`;
- cache autotools;
- `Makefile*`;
- `configure*`;
- nieużywane źródła słowników;
- nieużywane tryby pomocnicze.

Zachowano tylko artefakty wymagane przez dostępne mode, licencje oraz `modes.xml`.

Backup przed operacją:

```text
backups/apertium-package-pipeline-20261006-205830/Apertium-data.tar
SHA-256:
1d9e77ffe9eaa363d13f6e25ff02958818a1e54bbffb95baa39a6f8d6d898aec
```

## 12. Weryfikacja wszystkich paczek

Wszystkie 27 archiwów zostało:

1. rozpakowanych przez rzeczywisty `ApertiumPairPackageInstaller`;
2. zweryfikowanych pod kątem manifestu i checksum;
3. zainstalowanych do czystego magazynu tymczasowego;
4. wykrytych ponownie przez `discover_supported_pairs()`.

Wynik:

```text
ARCHIVES 27
PAIRS 27
INSTALACJA WSZYSTKICH PACZEK: OK
```

Dodatkowo każda paczka jest niekompresowanym tar.

## 13. Licencje

Builder wymaga `COPYING`, `LICENSE` lub `LICENSE.txt`.

Nie zgadujemy licencji. Jeżeli upstream nie dostarcza jednoznacznej informacji, paczka zostaje zablokowana do publikacji.

Dla przykładu oficjalne repozytoria Apertium potwierdzają licencje dla części przygotowanych rodzin; np. `apertium-bn-en` jest oznaczone jako GPL-2.0, a `apertium-eng-pol` również jako GPL-2.0. Informacje te zostały wykorzystane wyłącznie do weryfikacji źródeł, natomiast sama paczka nadal musi zawierać odpowiedni plik licencyjny. citeturn3search0turn1search3

## 14. Co robić przy dodawaniu nowej pary

```bash
python3 tools/apertium/package_pairs.py   <pair>   --download   --compile   --output $HOME/.config/tlumacz/apertium   --version 1.0.0
```

Po udanej kompilacji narzędzie automatycznie znajdzie wszystkie kompletne kierunki z tego repozytorium. Jeżeli para jest dwukierunkowa, otrzymamy dwa osobne pliki.

Do publikacji sprawdzamy:

```bash
tar -tf $HOME/.config/tlumacz/apertium/apertium-<pair>-1.0.0.tar
sha256sum $HOME/.config/tlumacz/apertium/apertium-<pair>-1.0.0.tar
```

## 15. Zasada projektowa

**Źródło Apertium służy do kompilacji. Paczka Tłumacza służy do dystrybucji runtime.**

Nie mieszamy tych ról:

```text
Apertium/
  pełne repozytoria źródłowe
  ↓
  kompilacja
  ↓
  package_pipeline
  ↓
$HOME/.config/tlumacz/apertium/
  pojedyncze artefakty .tar
  ↓
Internet
  ↓
Tłumacz
  ↓
$HOME/.config/tlumacz/apertium/
```

Dzięki temu można regularnie pobierać nowsze repozytoria Apertium, kompilować je, automatycznie wykrywać oba kierunki i publikować tylko kompletne, zweryfikowane paczki.


## 16. Narzędzia budowania poza runtime

Logika przygotowywania paczek znajduje się wyłącznie w katalogu `tools/apertium/`. `package_pipeline.py` i `package_pairs.py` są narzędziami pomocniczymi używanymi podczas budowania i nie są częścią runtime Tłumacza.

Ręczna procedura przygotowania pojedynczej paczki jest opisana w `docs/technical-docs/apertium-paczki-reczne-tworzenie.md`, a pełny kontrakt w `docs/technical-docs/paczki-jezykowe-specyfikacja.md`.
