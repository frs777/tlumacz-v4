# Audyt regresji GUI i backendów Cloud V3 → V4 — 2026-10-01

## Zakres

Porównano:
- źródło referencyjne V3: `/home/frs/Projekty/agent-translator-v3/tlumacz`;
- aktualne źródło V4: `/home/frs/Projekty/tlumacz-v4/src/tlumacz`;
- dokumentację V3 i V4;
- dokument `docs/wdrozenia/serwery-chmurowe.md`;
- indeksy V3/V4;
- zrzuty `API i serwer-chmura.png` oraz `API i serwer-chmura-nowa.png`;
- testy backendów Cloud i GUI.

## Ustalone niezgodności przed naprawą

### R-01 — brak warstwy Qt GUI w V4 — KRYTYCZNE

W V4 pod `src/tlumacz` nie istnieje `qt_gui/`, `MainWindow`, `app.py`, `worker.py` ani `backend_manager.py`. Występują wyłącznie kontrolery aplikacyjne niezależne od Qt.

Dokument `FAZA_9_GUI_COMPLETE_2026-09-30.md` opisuje brak PySide6 jako kryterium izolacji, ale dokumentacja migracyjna jednocześnie stanowi, że `MainWindow` pozostaje UI boundary i ma zostać rozbite na kontrolery. W efekcie kontrolery zostały zamknięte bez odtworzenia samego GUI.

To nie jest zgodne z celem aplikacji desktopowej.

### R-02 — utrata implementacji providerów Cloud — KRYTYCZNE

V3 `tlumacz/cloud_providers.py` zawiera implementacje:
- MyMemory;
- LibreTranslate;
- SimplyTranslate;
- DLX/OneShot;
- DeepL API;
- Microsoft Translator;
- wspólny `translate_cloud()`;
- transport JSON/HTTP;
- obsługę limitów i dzielenia UTF-8;
- opcjonalny transport pycurl dla DLX.

V4 `backends/cloud/provider.py` zawiera wyłącznie protokół `CloudProvider`, a `backends/cloud/` posiada obecnie implementację Mozhi, router, migrację profili i klasy błędów.

Oznacza to regresję funkcjonalną: kontrakt został przeniesiony, ale implementacje providerów nie zostały przeniesione.

### R-03 — utrata konfiguracji Cloud

V3 `tlumacz/config/cloud_models.json` definiuje 12 profili:
Cohere, ChatGPT, Codex, Gemini Flash, Gemini Flash Lite, DeepSeek, DeepL API Free, LibreTranslate, SimplyTranslate, MyMemory, Microsoft Translator i Mozhi.

V4 nie posiada odpowiadającego źródła konfiguracji providerów Cloud w `src/tlumacz`.

### R-04 — utrata warstwy Mozhi GUI

Zrzut referencyjny `API i serwer-chmura-nowa.png` pokazuje w sekcji „Serwer zewnętrzny – chmura”:
- Model: Mozhi;
- Serwer Mozhi: Automatyczny;
- Silnik Mozhi: DuckDuckGo;
- Restart procesu po tłumaczeniu.

Starszy zrzut `API i serwer-chmura.png` pokazuje jedynie model Gemini 3.5 Flash i nie pokazuje pól Mozhi.

V3 posiada już odpowiednie pola i logikę `server_mozhi_instance`, `server_mozhi_engine` oraz health-check w workerach. V4 nie posiada GUI, więc funkcja jest całkowicie niedostępna.

### R-05 — dwa backendy zostały prawidłowo wycofane z architektury, ale nie można wycofać całego GUI

Dokumentacja migracji V4 jednoznacznie określa:
- FastAPI → brak w V4;
- OpenVINO → brak w V4.

To nie oznacza usunięcia Qt GUI. Z GUI należy usunąć rekordy i pola specyficzne dla FastAPI/OpenVINO, ale zachować aktywne ścieżki:
- llama.cpp;
- Cloud;
- Apertium.

### R-06 — niespójność dokumentacji

V4 dokumentuje `tlumacz/qt_gui/main_window.py`, `tlumacz/qt_gui/backend_manager.py` i `tlumacz/qt_gui/worker.py` jako elementy architektury, mimo że te pliki nie istnieją w aktualnym `src/tlumacz`.

Jest to błąd dokumentacji wynikający z zamknięcia Fazy 9 na poziomie kontrolerów zamiast kompletnej migracji interfejsu.

## Wniosek architektoniczny

Migracja GUI/Cloud została wykonana **częściowo i regresywnie**: przeniesiono kontrakty i część logiki domenowej, ale nie przeniesiono kompletnego runtime'u GUI ani implementacji providerów Cloud.

Naprawa musi być wykonana jako kontrolowane odtworzenie funkcjonalności V3 w architekturze V4, a nie przez bezpośrednie kopiowanie starego monolitu.

## Zasada naprawy

V3 pozostaje źródłem zachowania funkcjonalnego. V4 pozostaje właścicielem architektury.

Docelowo:

```
Qt GUI
  ↓
kontrolery aplikacyjne
  ↓
porty / rejestr backendów
  ├── LlamaCppBackend
  ├── CloudBackend
  │    ├── OpenAI-compatible
  │    ├── DeepL
  │    ├── Microsoft
  │    ├── MyMemory
  │    ├── LibreTranslate
  │    ├── SimplyTranslate
  │    ├── Mozhi
  │    └── DLX
  └── ApertiumBackend
```

FastAPI i OpenVINO pozostają poza aktywnym rejestrem.

## Backup

Przed rozpoczęciem naprawy wykonano:

`.migration-backups/pre-gui-cloud-repair-20261001.tar.gz`

## Status

Audyt regresji zakończony. Naprawa funkcjonalna rozpoczęta po zapisaniu tego raportu.
