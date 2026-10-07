# Uniwersalna binarka llama.cpp dla x86_64

## Artefakt

- Plik: `llama-server`
- Ścieżka: `llama.cpp/llama-server`
- Wersja: `0.4.1-dev`
- Platforma: Linux x86_64
- Kompilator: GNU 16.2.1
- Rozmiar: 19 001 176 bajtów
- SHA-256: `5591137082b0a03b4d2c672b4e58522cdda3349f133375c4661a604fccbaaa01`

## Cel kompilacji

Jest to wariant przeznaczony do publikacji w repozytorium GitHub jako binarka możliwie niezależna od konkretnego procesora. Nie używa optymalizacji `-march=native` ani instrukcji wymagających AVX/AVX2/AVX-512, FMA, F16C, BMI2 lub SSE4.2.

Ustawienia kompilacji CPU:

- `GGML_NATIVE=OFF`
- `GGML_SSE42=OFF`
- `GGML_AVX=OFF`
- `GGML_AVX2=OFF`
- `GGML_AVX_VNNI=OFF`
- `GGML_AVX512=OFF`
- `GGML_AVX512_VBMI=OFF`
- `GGML_AVX512_VNNI=OFF`
- `GGML_AVX512_BF16=OFF`
- `GGML_BMI2=OFF`
- `GGML_FMA=OFF`
- `GGML_F16C=OFF`
- `GGML_CPU_ALL_VARIANTS=OFF`
- `GGML_BACKEND_DL=OFF`

Kompilacja używa `-march=x86-64 -mtune=generic`.

## Zakres

Binarka jest przeznaczona dla systemów Linux x86_64 i nie jest optymalizowana pod konkretny procesor. Oznacza to mniejszą wydajność niż binarka skompilowana z `-march=native`, ale większą przenośność sprzętową.

Nie jest to binarka statyczna. Korzysta z bibliotek systemowych, m.in. `glibc`, `libstdc++`, `libgomp` oraz OpenSSL. Zatem „uniwersalność” dotyczy przede wszystkim zestawu instrukcji CPU, a nie wszystkich możliwych dystrybucji Linux bez względu na ich biblioteki systemowe.

## Źródło

Kompilacja została wykonana ze źródeł znajdujących się na hoście w:

`<katalog-źródeł-llama.cpp>`

Artefakt został skopiowany do projektu V4, ale źródła llama.cpp nie zostały skopiowane do tego katalogu.

## Weryfikacja

Potwierdzono:

- format ELF 64-bit x86-64,
- uruchomienie `llama-server --version`,
- wersję `0.4.1-dev`,
- brak ustawienia `GGML_NATIVE`,
- wyłączenie rozszerzeń CPU wymienionych powyżej,
- brak bibliotek `ggml` jako osobnych zależności dynamicznych.

Data kompilacji: 2026-10-07.

## Zależności względem starego pakietu `native/linux-x86_64`

Wykonano porównanie z `src/tlumacz/backends/llama_cpp/native/linux-x86_64`.

Stary `llama-server` jest dynamicznie zależny od bibliotek llama/GGML:
`libllama-server-impl.so`, `libllama-common.so.0`, `libmtmd.so.0`,
`libllama.so.0`, `libggml.so.0`, `libggml-cpu.so.0` i `libggml-base.so.0`.
Jego `RUNPATH` wskazuje dodatkowo na katalog builda poza repozytorium.

Uniwersalny `llama-server` z tego katalogu `llama.cpp/` nie ma żadnej z tych
zależności w `NEEDED`; kod llama/GGML został włączony do binarki. Dlatego
kopiowanie starych bibliotek do pakietu byłoby błędem: byłyby to biblioteki
związane ze starą kompilacją, a nie zależności nowej binarki.

Nowa binarka wymaga wyłącznie bibliotek systemowych wykazanych przez `ldd`,
m.in. `libgomp`, OpenSSL, `libstdc++`, `glibc`, zlib, Brotli i zstd.
