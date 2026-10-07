---
id: server-management-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: runtime-maintenance
source: src/tlumacz/qml_gui/, src/tlumacz/backends/llama_cpp/
depends_on: [docs/ARCHITECTURE.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: zmiana lifecycle llama.cpp
last_validation: "inspekcja dokumentacji SentinelX 2026-10-04"
---

## 2026-10-05 — aktualny lifecycle llama.cpp

`TranslationApp` posiada opcjonalny `LlamaCppRuntimeManager`. Aktywne operacje to `start_llama()`, `stop_llama()` i `restart_llama()`.

Restart odczytuje z aktualnego runtime model GGUF, port, tryb obliczeń, równoległość i szablon czatu. Następnie zatrzymuje stary proces i uruchamia nowy z tym samym zestawem ustawień.

GUI udostępnia stan `llama_server_running` oraz akcję restartu. Cloud i Apertium nie korzystają z tego lifecycle.

# Zarządzanie runtime — Tłumacz V4

## Zakres

Bieżący lokalny runtime dotyczy **llama.cpp / llama-server**. Cloud nie wymaga lokalnego procesu. Apertium ma własny runtime i lifecycle opisany w dokumentacji Apertium.

## Aktywna architektura

```text
Qt GUI / application
    ↓
LlamaCpp backend
    ↓
runtime manager
    ↓
llama-server
```

Szczegóły implementacji należy czytać w `src/tlumacz/backends/llama_cpp/` oraz w aktualnym kodzie GUI.

## Wycofane runtime'y

FastAPI/Transformers oraz stara ścieżka OpenVINO z modelem TranslateGemma INT8 nie są uruchamiane przez V4. Nie należy przywracać ich wpisów do aktywnego wyboru backendu ani dokumentować ich jako wymaganych komponentów runtime.

## Zasada diagnostyki

Jeżeli zachowanie programu wskazuje na FastAPI, OpenVINO albo inne elementy V3, najpierw sprawdź interpreter, `tlumacz.__file__`, środowisko uruchomieniowe i launcher. Audyt 2026-10-01 wykazał globalną instalację Tłumacza 0.31.2 jako źródło takich rozbieżności.

## Weryfikacja

Testy runtime powinny być wykonywane w środowisku zbudowanym z aktualnego V4 wheel/checkoutu. Wynik musi zawierać datę i dokładną komendę.
## 2026-10-06 — wybór runtime'u llama.cpp

Domyślny runtime llama.cpp jest obecnie dostarczany razem z aplikacją dla Linux x86_64. `LlamaCppRuntimeConfig` rozwiązuje wykonywalny `llama-server` z `tlumacz/backends/llama_cpp/native/linux-x86_64/`, a `LlamaCppRuntimeManager` ustawia dla procesu `LD_LIBRARY_PATH` tego samego katalogu, aby `libllama*` i `libggml*` pochodziły z tej samej kompilacji.

Źródłem wyboru jest `$HOME/.config/tlumacz/llama.json`:

- `runtime.source = "bundled"` — runtime dołączony;
- `runtime.source = "system"` — `runtime.executable` przez `PATH` albo pełną ścieżkę.

Szczegółowa procedura podmiany dołączonej kompilacji własnym buildem znajduje się w `docs/wdrozenia/llama-cpp-runtime.md`.

## 2026-10-07 — bundled runtime publikacyjny

Bundled runtime Linux x86_64 w aktualnym drzewie projektu jest publikowany jako pojedyncza binarka `llama-server` w `native/linux-x86_64/`. Nie towarzyszą jej już dołączone biblioteki `libllama*`, `libggml*` ani `libmtmd*`. Binarka pochodzi z `llama.cpp/llama-server` i jest buildem dystrybucyjnym bez `-march=native` oraz bez specjalizacji instrukcji CPU.

Runtime nadal może korzystać z bibliotek systemowych wymaganych przez ELF. `LD_LIBRARY_PATH` może pozostać ustawiany na katalog runtime'u, ale nie jest już mechanizmem dostarczania osobnych bibliotek llama.cpp/GGML.
