# Runtime llama.cpp dołączony do Tłumacza

**Data aktualizacji:** 2026-10-07  
**Status:** wdrożone dla Linux x86_64  
**Artefakt publikacyjny:** `llama.cpp/llama-server` → `src/tlumacz/backends/llama_cpp/native/linux-x86_64/llama-server`  
**Wersja artefaktu:** `0.4.1-dev`  
**SHA-256:** `5591137082b0a03b4d2c672b4e58522cdda3349f133375c4661a604fccbaaa01`  
**Profil:** uniwersalny Linux x86_64, bez `-march=native` i bez specjalizacji instrukcji CPU

## 1. Cel

Tłumacz nie korzysta już domyślnie z przypadkowego `llama-server` znalezionego w `PATH`. Domyślnym runtime'em jest kompatybilna kompilacja llama.cpp dołączona do pakietu aplikacji.

Jednocześnie zachowana jest możliwość wskazania instancji systemowej przez `$HOME/.config/tlumacz/llama.json`.

## 2. Domyślny profil

Wartości pochodzą z rzeczywistych testów opisanych w:

`docs/wdrozenia/rekomendacja-ustawien-llama.cpp.md`

Profil CPU:

| Parametr | Wartość |
|---|---:|
| threads | auto → fizyczne rdzenie |
| threads-batch | auto → logiczne wątki |
| batch-size | 2048 |
| ubatch-size | 512 |
| ctx-size | 8192 |
| parallel | 1 dla profilu latency; GUI może ustawić 4 dla throughput |
| prompt cache | ON |
| cache reuse | 0/OFF |
| Flash Attention | OFF |
| repack | ON |
| KV K | Q8_0 |
| KV V | F16 |
| TranslateGemma | `--no-jinja` |

`parallel` pozostaje ustawieniem GUI/runtime, ponieważ określa liczbę slotów serwera, a nie liczbę wątków CPU.

## 3. Wybór runtime'u

Plik:

`$HOME/.config/tlumacz/llama.json`

zawiera sekcję:

```json
"runtime": {
  "source": "bundled",
  "executable": "llama-server"
}
```

### Runtime dołączony

`source: "bundled"` — używana jest:

`tlumacz/backends/llama_cpp/native/linux-x86_64/llama-server`

oraz biblioteki współdzielone znajdujące się obok niego. Aplikacja ustawia dla procesu `LD_LIBRARY_PATH` wskazujący katalog dołączonego runtime'u. Dzięki temu proces nie pobiera bibliotek llama.cpp z `/usr/local/lib`.

### Runtime systemowy

Aby użyć instalacji systemowej:

```json
"runtime": {
  "source": "system",
  "executable": "llama-server"
}
```

Wtedy aplikacja rozwiązuje `llama-server` przez `PATH`.

Można też podać pełną ścieżkę:

```json
"runtime": {
  "source": "system",
  "executable": "/opt/llama/bin/llama-server"
}
```

Pełna ścieżka musi wskazywać istniejący plik wykonywalny.

## 4. Jak podmienić dołączoną kompilację własną kompilacją

To jest procedura dla Linux x86_64 i zgodnego ABI.

### 4.1. Zbuduj llama.cpp

Użyj źródeł kompatybilnych z kontraktem aplikacji. Dla profilu Tłumacza zalecane są:

```text
CMAKE_BUILD_TYPE=Release
GGML_NATIVE=ON
GGML_CPU=ON
GGML_CPU_REPACK=ON
GGML_OPENMP=ON
GGML_ZENDNN=OFF
GGML_CUDA=OFF
GGML_VULKAN=OFF
GGML_SYCL=OFF
GGML_OPENCL=OFF
LLAMA_BUILD_SERVER=ON
LLAMA_BUILD_TESTS=OFF
LLAMA_BUILD_EXAMPLES=ON
```

### 4.2. Zatrzymaj aplikację

Nie podmieniaj bibliotek, gdy proces llama-server jest uruchomiony.

### 4.3. Zrób kopię aktualnego runtime'u

W katalogu pakietu aplikacji:

```bash
cd /ścieżka/do/tlumacz
cp -a src/tlumacz/backends/llama_cpp/native/linux-x86_64       /ścieżka/do/backup/linux-x86_64-przed-podmianą
```

### 4.4. Skopiuj runtime

Do katalogu:

```text
src/tlumacz/backends/llama_cpp/native/linux-x86_64/
```

należy skopiować `llama-server` oraz wszystkie biblioteki, od których zależy ten serwer i które pochodzą z tej samej kompilacji.

Nie wolno mieszać `llama-server` z bibliotekami `libllama*`/`libggml*` z innego builda.

Minimalna kontrola:

```bash
LD_LIBRARY_PATH=src/tlumacz/backends/llama_cpp/native/linux-x86_64 \
  src/tlumacz/backends/llama_cpp/native/linux-x86_64/llama-server --version

LD_LIBRARY_PATH=src/tlumacz/backends/llama_cpp/native/linux-x86_64 \
  ldd src/tlumacz/backends/llama_cpp/native/linux-x86_64/llama-server
```

W `ldd` biblioteki `libggml*`, `libllama*` i `libmtmd*` powinny wskazywać na katalog dołączonego runtime'u, a nie na niepasujące kopie systemowe.

### 4.5. Nie zmieniaj konfiguracji aplikacji

Pozostaw:

```json
"runtime": {
  "source": "bundled"
}
```

Własna kompilacja zastępuje wtedy runtime dołączony do aplikacji.

### 4.6. Walidacja

Po podmianie sprawdź:

1. `llama-server --version`;
2. `/health`;
3. `/props`;
4. TranslateGemma PL→EN;
5. TranslateGemma EN→PL;
6. `parallel=1`;
7. `parallel=4`;
8. cache prompt;
9. Q8_0/F16;
10. brak brakujących bibliotek.

## 5. Dlaczego nie należy mieszać bibliotek

`llama-server` jest tylko cienkim wykonywalnym komponentem; właściwa implementacja znajduje się również w bibliotekach `libllama-server-impl.so`, `libllama.so`, `libllama-common.so`, `libggml*.so` i `libmtmd.so`.

Mieszanie wersji może powodować:

- brak symboli ELF przy starcie;
- błędy `cannot open shared object file`;
- niezgodność ABI;
- różne zachowanie parametrów CLI;
- regresje wydajności;
- użycie innego backendu CPU niż zakładany;
- trudne do wykrycia różnice między procesem uruchomionym wcześniej a świeżym procesem.

## 6. Obecny artefakt dołączony

Aktualny bundled runtime zawiera wyłącznie `llama-server`. Nie towarzyszą mu `libllama*`, `libggml*` ani `libmtmd*`.

Binarka jest dynamiczna i korzysta z bibliotek systemowych wymaganych przez ELF, m.in. glibc, libstdc++, libgomp i OpenSSL. Nie zawiera ścieżki RUNPATH do lokalnego katalogu builda.

Weryfikacja 2026-10-07 potwierdziła ELF x86-64, wersję `0.4.1-dev` oraz SHA-256 zgodne z `llama.cpp/README.md`. `readelf -d` wykazał wyłącznie zależności systemowe; nie występują `libllama*`, `libggml*` ani `libmtmd*`.



Sam runtime llama.cpp zwiększa instalację o około **23,2 MB** przed kompresją.

Testowany wheel po dodaniu runtime'u miał około **45,9 MB**. Nie należy utożsamiać tej wartości z samym narzutem llama.cpp, ponieważ wheel zawiera również pozostałe zasoby aplikacji.

Narzut netto należy przyjmować jako około **23 MB** dla Linux x86_64.

## 8. Problemy i ograniczenia

### Platforma

Dołączony runtime jest obecnie przeznaczony wyłącznie dla **Linux x86_64**. Dla innych platform należy dostarczyć osobny build albo wybrać runtime systemowy.

### ABI systemu

Dołączony build nadal korzysta z systemowych bibliotek bazowych, m.in. glibc, libstdc++ i libgomp. Nie jest to całkowicie statyczny binary bundle.

### Zależność od CPU

Poprzedni build używał `GGML_NATIVE=ON` i był zoptymalizowany pod host testowy. Ten artefakt został wycofany z publikacji; aktualny bundled runtime jest buildem dystrybucyjnym.

### Aktualizacja llama.cpp

Aktualizacja aplikacji może aktualizować również dołączony runtime. Własna podmiana wymaga ponownego wykonania po aktualizacji, jeśli pliki pakietu zostaną nadpisane.

### Zgodność konfiguracji

Nie należy kopiować parametrów GPU, CUDA, ZenDNN ani innych specjalizowanych buildów do profilu CPU bez ponownego benchmarku.

### Packaging

Dołączony ELF oznacza, że dystrybucja zawiera komponent platformowy. Artefakty dystrybucyjne należy traktować jako Linux x86_64, a nie jako faktycznie przenośny pakiet Python-only.

## 9. Diagnostyka

Jeżeli aplikacja nie startuje z llama.cpp:

```bash
LD_LIBRARY_PATH=/ścieżka/do/native/linux-x86_64 \
  /ścieżka/do/native/linux-x86_64/llama-server --version

LD_LIBRARY_PATH=/ścieżka/do/native/linux-x86_64 \
  ldd /ścieżka/do/native/linux-x86_64/llama-server | grep -E 'llama|ggml|mtmd|not found'
```

Jeżeli pojawia się:

```text
libggml-*.so: cannot open shared object file
```

najpierw sprawdź kompletność katalogu runtime'u i `LD_LIBRARY_PATH`. Nie instaluj automatycznie brakujących bibliotek systemowych.

## 10. Powiązane dokumenty

- `docs/wdrozenia/rekomendacja-ustawien-llama.cpp.md` — źródło wartości tuningu;
- `docs/technical-docs/server-management.md` — lifecycle serwera;
- `config/llama.json` — szablon technicznego profilu;
- `$HOME/.config/tlumacz/llama.json` — aktywny profil użytkownika.

## 11. Zasada utrzymania

Runtime dołączony do aplikacji i runtime systemowy są dwoma świadomie wspieranymi trybami. Domyślny jest runtime dołączony, ponieważ zapewnia powtarzalny zestaw `llama-server + biblioteki` zgodny z testowanym profilem Tłumacza.

## 12. Polityka platformowa

### Linux x86_64 — artefakt publikacyjny

Aktualny bundled runtime przeznaczony do publikacji jest uniwersalnym buildem Linux x86_64. Nie używa `GGML_NATIVE`, `-march=native` ani specjalizacji instrukcji CPU. Jest przeznaczony do możliwie szerokiej zgodności w obrębie x86_64, przy zachowaniu zależności od bibliotek systemowych wymaganych przez ELF.

### Inne systemy Linux

Dla innych platform lub architektur należy używać runtime'u systemowego albo przygotować osobny artefakt platformowy.

### Windows i macOS

Obecny bundled runtime nie obejmuje Windows ani macOS. Dla tych platform należy używać runtime'u dostarczonego przez użytkownika/system.

### Poprzedni build dedykowany

Wcześniejszy bundled runtime był buildem `GGML_NATIVE=ON` zoptymalizowanym pod host testowy. Ten artefakt został wycofany z katalogu publikacyjnego i nie jest już częścią aktualnego bundled runtime.



Należy rozróżnić:

1. **Build dedykowany** — maksymalizuje wydajność na konkretnym sprzęcie. Może używać `GGML_NATIVE` i innych optymalizacji zależnych od hosta.
2. **Build dystrybucyjny** — ma być możliwie szeroko kompatybilny w obrębie deklarowanej platformy. Przy budowaniu paczki należy używać bardziej ogólnych parametrów kompilacji i nie optymalizować binarium pod jeden konkretny procesor lub kartę.
3. **Runtime systemowy** — fallback dla platform i sprzętu, dla których bundled runtime nie został przygotowany.

Nie wolno używać benchmarku builda dedykowanego jako dowodu, że ten sam binarny runtime będzie optymalny na wszystkich komputerach.

## 14. Karta referencyjna sprzętu

Każdy dedykowany build powinien mieć kartę referencyjną:

`docs/wdrozenia/karta-referencyjna-llama-sprzet.md`

Karta ma zawierać sprzęt, system, CPU/GPU, zestaw instrukcji, kompilator, commit llama.cpp, pełne opcje CMake, parametry runtime i wyniki benchmarków.

## 15. Plan automatyzacji

Do TODO należy przygotować skrypty, które automatycznie:

1. wykrywają CPU, rdzenie, wątki i zestaw instrukcji;
2. wykrywają GPU, VRAM i dostępny backend;
3. zapisują wersję systemu, kompilatora, CMake i llama.cpp;
4. generują kartę referencyjną;
5. generują konfigurację CMake dla trybu `dedykowany` lub `dystrybucyjny`;
6. budują llama.cpp;
7. wykonują test `/health`;
8. wykonują benchmarki kontrolne;
9. zapisują wyniki oraz hash artefaktów.

Skrypt nie powinien sam instalować pakietów systemowych bez wyraźnej zgody użytkownika.

## 2026-10-07 — artefakt dystrybucyjny Linux x86_64

Do publikacji projektu stosowana jest uniwersalna binarka `llama.cpp/llama-server` (`0.4.1-dev`), kopiowana do `src/tlumacz/backends/llama_cpp/native/linux-x86_64/llama-server`. Katalog bundled runtime zawiera wyłącznie tę binarkę. Nie należy do niego dodawać `libllama*`, `libggml*` ani `libmtmd*` z lokalnego builda.

Artefakt został przygotowany jako build ogólny dla x86_64: bez `-march=native` i bez włączania wariantów AVX/AVX2/AVX-512/FMA/F16C/BMI2/SSE4.2. Nie jest to build zoptymalizowany pod konkretny procesor. README artefaktu podaje SHA-256 `5591137082b0a03b4d2c672b4e58522cdda3349f133375c4661a604fccbaaa01`.

Dotychczasowy opis runtime'u dedykowanego sprzętowo pozostaje historycznym opisem poprzedniego buildu; nie opisuje aktualnego artefaktu publikacyjnego.
