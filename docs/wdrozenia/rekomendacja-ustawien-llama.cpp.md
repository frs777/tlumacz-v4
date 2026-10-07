# Rekomendacja ustawień llama.cpp dla Tłumacz V4

**Data:** 2026-10-06  
**Zakres:** odzyskanie tuningu llama.cpp utraconego podczas migracji V3 → V4  
**Źródła:** `agent-translator-v3/docs`, `tlumacz-v4/docs`, `/home/frs/Projekty/llama.cpp`  
**Host testowy:** AMD Ryzen 7 5825U, 8 rdzeni / 16 wątków, x86_64  
**Model referencyjny V3:** TranslateGemma 4B IT Q5_K_M  
**Profil V3:** CPU-only, `ctx=8192`, `parallel=1`, ręcznie renderowany prompt TranslateGemma (`--no-jinja`)

## 1. Wniosek wykonawczy

Tuning V3 nie zaginął całkowicie: jego najważniejsze wartości znajdują się w artefaktach testowych i dokumentacji historycznej.

Dla lokalnego CPU profilu referencyjnego Tłumacza rekomenduję:

| Parametr | Rekomendacja | Status |
|---|---:|---|
| `--threads` | **8** | potwierdzone testami V3 |
| `--threads-batch` | **16** | potwierdzone testami V3 |
| `--batch-size` | **2048** | potwierdzone testami V3 |
| `--ubatch-size` | **512** | potwierdzone testami V3 |
| `--ctx-size` | **8192** jako profil referencyjny | potwierdzone środowiskiem V3; V4 ma już dynamiczne auto-ctx |
| `--parallel` | **1** dla latency / jakości profilu bazowego | potwierdzone testami V3 |
| `--parallel` | **4** dla kontrolowanego throughputu | potwierdzone screeningiem V3 |
| `--cache-prompt` | **ON** | potwierdzone testem identycznego prefixu |
| `--cache-reuse` | **OFF/N/A** | aktualny build zgłasza brak wsparcia dla tego kontekstu |
| `--jinja` | **OFF** dla ręcznie renderowanego TranslateGemma | potwierdzone kontraktem V3 |
| `--flash-attn` | **OFF dla CPU-native profilu bazowego** | wymaga zamrożenia na aktualnym buildzie; nie należy przenosić ustawień GPU |
| KV K | **Q8_0 jako kandydat** | V3 wykazał przewagę nad F16/F16, ale wymaga ponownej walidacji |
| KV V | **F16** | para `Q8_0/F16` była kontrolowanym A/B |
| `--repack` | **ON** | zgodne z istniejącymi zoptymalizowanymi buildami |
| NUMA | brak wymuszenia | pojedynczy socket |
| polling/priority | wartości domyślne | brak dowodu na korzyść dla profilu tłumaczeniowego |

Najważniejsza decyzja architektoniczna V4 jest prawidłowa: techniczny tuning llama.cpp powinien być oddzielony od ustawień użytkownika i dostarczany przez `$HOME/.config/tlumacz/llama.json`. V4 posiada już mechanizm `threads=auto` / `threads-batch=auto`; wartości jawne powinny pozostać nadrzędne.

## 2. Dowody z testów V3

### T1 — threads / threads-batch

Seria na TranslateGemma 4B Q5_K_M, CPU-native, `ctx=8192`, `parallel=1`:

- `threads=8`
- `threads-batch` testowane: 1, 2, 4, 6, 8, 12, 16
- dla `threads-batch=16`: PP 41,636 tok/s, TG 6,591 tok/s
- estymowany czas 512+128 tokenów: **31,72 s**, najlepszy w tej serii
- decyzja V3: **8/16** jako kandydat referencyjny.

Wniosek: nie wolno zastępować obu wartości jednym `threads=16`. Decode i prefill mają inną charakterystykę.

### T2 — batch / ubatch

Po poprawieniu runnera wykonano właściwy benchmark:

| batch | ubatch | PP tok/s | TG tok/s | czas 512+128 |
|---:|---:|---:|---:|---:|
| 512 | 128 | 40,008 | 5,688 | 35,30 s |
| 1024 | 256 | 38,132 | 5,440 | 36,96 s |
| 2048 | 512 | 40,532 | 5,592 | 35,52 s |
| 4096 | 1024 | 40,806 | 5,626 | 35,30 s |

Dodatkowe T2e potwierdziło `2048/512`: PP 40,885 tok/s, TG 6,083 tok/s, estymowany czas **33,57 s**.

`4096/1024` nie dawało istotnej przewagi, a zwiększało RSS o około 65,5 MB względem 2048/512.

**Decyzja:** `2048/512`.

### T4 — KV cache

Kontrolowane A/B:

| K/V | FA | PP512 | TG128 |
|---|---|---:|---:|
| F16/F16 | off | 40,408 | 6,522 |
| Q8_0/F16 | off | **41,934** | **6,598** |
| Q8_0/Q8_0 | on | 42,611 | 6,679 |

Q8_0/F16 względem F16/F16 dało około +3,8% PP, +1,2% TG i -3,8% TTFR.

To jest jednak **kandydat**, nie bezwarunkowo zamrożona wartość produkcyjna, ponieważ późniejsza walidacja musi być wykonana dokładnie na buildzie używanym przez V4.

### T5 — prompt cache

Test identycznego promptu w jednym procesie wykazał duży spadek kosztu kolejnych prompt-eval po włączeniu cache. Log potwierdził redukcję z 371 tokenów do 5 tokenów dla kolejnych requestów.

**Decyzja:** prompt cache **włączony**.

`cache-reuse=256` nie jest rekomendowany: aktualny runtime zgłasza `cache_reuse is not supported by this context`.

### T6 — parallel

Wyniki:

- `parallel=1`: PP 39,641 / TG 4,861
- `parallel=2`: PP 37,404 / TG 9,502
- `parallel=4`: PP 39,261 / TG 15,113
- `parallel=8`: tylko screening 1-run

**Decyzja:** `parallel=1` jako profil latency; `parallel=4` jako kontrolowany profil throughputu. Nie należy utożsamiać `parallel` z liczbą wątków CPU.

## 3. Co wynika z dokumentacji llama.cpp

Aktualny lokalny `llama-server` obsługuje m.in.:

- `--threads`
- `--threads-batch`
- `--ctx-size`
- `--batch-size`
- `--ubatch-size`
- `--flash-attn on|off|auto`
- `--cache-prompt`
- `--cache-reuse`
- `--parallel`
- `--repack`
- `--numa`
- `--poll`
- `--prio`

Istotne jest, że obecny upstream ma domyślnie `batch=2048` i `ubatch=512`, więc wartości odzyskane z V3 są również zgodne z bieżącym kontraktem CLI.

Dokumentacja upstream zaleca dobierać `--threads` do fizycznych rdzeni dla generacji oraz rozważać wyższą liczbę wątków dla batch processing. Jest to zgodne z wynikiem V3: 8 fizycznych rdzeni → `threads=8`, 16 logicznych wątków → `threads-batch=16`.

## 4. Build dedykowany dla Tłumacza

Nie modyfikowano istniejących buildów:

- `build/`
- `build-zendnn/`
- `build-optimus-cpu/`

Uruchomiono przygotowanie osobnego:

`/home/frs/Projekty/llama.cpp/build-tlumacz-translation`

z parametrami:

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

### Uzasadnienie

To jest profil **CPU-native**, odpowiadający fizycznemu Ryzen 7 5825U. Nie należy włączać ZendNN tylko dlatego, że historycznie istniał `build-zendnn`: V3 nie dostarcza wystarczającego dowodu, że ZendNN jest lepszy dla aktualnego workloadu, a lokalny `build-optimus-cpu` już działa jako CPU-native bez ZendNN.

`GGML_CPU_REPACK=ON` pozostaje włączone, ponieważ wszystkie istniejące zoptymalizowane buildy lokalne mają ten parametr aktywny.

**Status kompilacji:** zadanie kompilacji dedykowanego builda zostało uruchomione asynchronicznie. Wynik końcowy należy potwierdzić przed podmianą runtime w V4. Istniejące buildy pozostają nienaruszone.

## 5. Rekomendowany profil dla V4

### Profil latency / tłumaczenie pojedynczego segmentu

```text
--ctx-size 8192
--threads 8
--threads-batch 16
--batch-size 2048
--ubatch-size 512
--parallel 1
--no-jinja
--cache-prompt
--repack
```

KV:

```text
--cache-type-k q8_0
--cache-type-v f16
```

Flash Attention: **nie wymuszać ON na CPU-native bez ponownego A/B na aktualnym buildzie**.

### Profil throughput

```text
--threads 8
--threads-batch 16
--batch-size 2048
--ubatch-size 512
--parallel 4
--no-jinja
--cache-prompt
--repack
```

Profil throughput musi mieć osobny benchmark pamięci i latency. Nie powinien zastępować profilu latency.

## 6. Ustawienia, których nie należy obecnie „odzyskiwać” z V3

Nie należy bez dowodu kopiować do V4:

- wartości GPU `n-gpu-layers`,
- CUDA-specific Flash Attention,
- CUDA KV quantization,
- multi-GPU split,
- ZendNN,
- agresywnego `parallel>4`,
- `cache-reuse`,
- arbitralnego `numa`,
- arbitralnych priority/polling,
- starego automatycznego Jinja.

Szczególnie ważne: V4 używa specjalnego `chat_template=translategemma` i ma własny routing języka dla TranslateGemma. Nie należy mylić tego z mechanicznym włączeniem `--jinja`.

## 7. Integracja z V4

V4 ma już właściwy podział odpowiedzialności:

- `config.json` — ustawienia użytkownika/GUI,
- `$HOME/.config/tlumacz/llama.json` — techniczny tuning llama.cpp.

V4 posiada także reguły:

- `threads=auto` → fizyczne rdzenie CPU,
- `threads-batch=auto` → logiczne wątki CPU,
- jawna wartość w `llama.json` ma pierwszeństwo nad auto.

Rekomendacja: zachować ten mechanizm i użyć profilu odzyskanego z V3 jako **domyślnego profilu referencyjnego dla Ryzen 7 5825U**, a nie jako uniwersalnej konfiguracji dla wszystkich komputerów.

## 8. Walidacja po kompilacji

Przed wskazaniem nowego builda jako runtime produkcyjnego należy wykonać:

1. `llama-server --version`.
2. Start z TranslateGemma 4B Q5_K_M.
3. Test `/health`.
4. Test rzeczywistego tłumaczenia PL→EN i EN→PL.
5. Test `--no-jinja` + ręcznie renderowanego promptu.
6. A/B Q8_0/F16 vs F16/F16.
7. A/B Flash Attention off/on na aktualnym CPU buildzie.
8. Test cache prompt na trzech identycznych requestach.
9. Test `parallel=1` oraz `parallel=4`.
10. Test regresyjny GUI V4.

## 9. Stan bezpieczeństwa / narzędzi

Codex Security Cloud został wywołany, ale bieżące konto nie ma dostępu do skanowania Cloud: `access=denied`, brak połączenia GitHub i brak kwalifikowanego workspace. Nie traktuję tego jako dowodu bezpieczeństwa projektu.

SentinelX został użyty do inspekcji hosta, dokumentacji, buildów i uruchomienia kompilacji. Nie wykonywano instalacji ani usuwania pakietów.

## 10. Źródła dowodowe

- V3: `TESTY/llama.cpp/NOCNE_WYNIKI_2026-09-26.md`
- V3: `TESTY/llama.cpp/PLAN_TESTOW_LLAMA_CPP.md`
- V3: `archive/research/llama-cpp-optymalizacja-wydajnosc-research-2026-09-25.md`
- V3: `archive/plans/PLAN_KONFIGURACJI_LLAMA_JSON-implemented-2026-09-28.md`
- V4: `ARCHITECTURE.md`
- upstream/local llama.cpp: `tools/server/README.md`, `common/arg.cpp`

## 11. Konkluzja

Najbardziej wiarygodny odzyskany profil V3 to:

**8 threads / 16 threads-batch / 2048 batch / 512 ubatch / 8192 ctx / parallel 1 / prompt-cache ON / no-jinja / repack ON.**

Dla V4 nie należy przywracać całej historycznej konfiguracji „w ciemno”. Należy przywrócić **potwierdzone wartości**, a ustawienia zależne od sprzętu pozostawić mechanizmowi auto lub ponownie zmierzyć na aktualnym buildzie.

Największym błędem byłoby zastąpienie odzyskanego tuningu jednym globalnym profilem dla wszystkich CPU/GPU. V4 ma już właściwą architekturę do przechowywania profilu technicznego i jego automatycznego doboru.
