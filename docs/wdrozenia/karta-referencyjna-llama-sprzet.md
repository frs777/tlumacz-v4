# Karta referencyjna — kompilacja llama.cpp dla sprzętu

**Status:** wzorzec do przygotowania przed optymalizacją runtime'u  
**Projekt:** Tłumacz V4

## Cel

Karta opisuje sprzęt, dla którego wykonano kompilację i benchmark llama.cpp. Ma zapobiegać traktowaniu builda zoptymalizowanego dla jednego komputera jako uniwersalnego artefaktu dystrybucyjnego.

## 1. Identyfikacja hosta

- system operacyjny:
- architektura:
- dystrybucja / wersja:
- kernel:
- CPU / model CPU:
- rdzenie fizyczne:
- wątki logiczne:
- zestaw instrukcji CPU:
- RAM:
- GPU / model GPU:
- VRAM:
- sterownik GPU:
- backend GPU:
- kompilator:
- CMake:
- llama.cpp / commit:

## 2. Parametry kompilacji

Zapisać pełny zestaw opcji CMake i flag wpływających na ABI, CPU i backendy, w szczególności `CMAKE_BUILD_TYPE`, `GGML_NATIVE`, `GGML_CPU`, `GGML_CPU_REPACK`, `GGML_OPENMP`, backendy GPU, `GGML_ZENDNN` i `LLAMA_BUILD_SERVER`.

## 3. Parametry runtime

Zapisać model GGUF i quantyzację oraz `threads`, `threads-batch`, `batch-size`, `ubatch-size`, `ctx-size`, `parallel`, KV cache K/V, Flash Attention, prompt cache, cache reuse, repack, GPU layers i pozostałe parametry uruchomieniowe.

## 4. Benchmark

| Test | Wynik |
|---|---|
| start `/health` | |
| czas ładowania modelu | |
| krótki tekst | |
| chunk ~1000 znaków | |
| chunk ~2000 znaków | |
| chunk ~4000 znaków | |
| `parallel=1` | |
| `parallel=4` | |
| CPU | |
| RAM | |
| VRAM | |
| tokens/s | |
| błędy / timeouty | |

## 5. Klasyfikacja

- **BUILD DEDYKOWANY** — zoptymalizowany pod konkretny sprzęt; nie używać jako uniwersalnego artefaktu.
- **BUILD DYSTRYBUCYJNY** — ogólne parametry dla określonej klasy platform.
- **SYSTEM RUNTIME** — aplikacja korzysta z llama.cpp dostarczonej przez użytkownika/system.

## 6. Zasada dystrybucji

Dla paczki aplikacji należy preferować bardziej ogólne parametry kompilacji. Nie należy włączać optymalizacji zależnych od konkretnego CPU/GPU tylko dlatego, że poprawiają benchmark na maszynie deweloperskiej.

Dla konkretnego sprzętu można przygotować osobny build dedykowany i osobną kartę referencyjną.
