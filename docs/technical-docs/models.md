---
id: models-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: technical-documentation
source: src/tlumacz/qml_gui/, src/tlumacz/backends/
depends_on: [docs/STATUS.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: zmiana kontraktu backendów lub katalogu modeli
last_validation: "inspekcja dokumentacji SentinelX 2026-10-04"
---

## 2026-10-05 — aktualny kontrakt backendów

Aktualne kierunki wykonania tłumaczenia to **llama.cpp**, **Cloud**, **Apertium** oraz **custom/Własny**. `translategemma` jest wartością `chat_template`, a nie backendem.

Dla llama.cpp aktywny runtime jest zarządzany przez `TranslationApp` i `LlamaCppRuntimeManager`, który obsługuje start, stop i restart. Dla TranslateGemma aktywny adapter korzysta z `LanguageDetector` i kodów ISO 639-1. Standardowy llama.cpp pozostaje przy `/chat/completions`.

Cloud korzysta z `CloudProviderRegistry`. W aktualnym kodzie są OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate, Mozhi i DLX. `custom` jest osobnym backendem i współdzieli z Cloud wyłącznie transport OpenAI-compatible.

Apertium ma własny adapter i runtime. Deklarowane pary językowe są wykrywane z lokalnych danych, ale gotowość konkretnej pary wymaga rzeczywistego testu runtime.

# Modele i backendy tłumaczenia — Tłumacz V4

## Aktywne backendy

V4 ma cztery aktywne kierunki tłumaczenia:

- **llama.cpp** — lokalny runtime llama-server;
- **Cloud** — router providerów usług chmurowych;
- **Apertium** — lokalny backend przez Filter Engine;
- **custom/Własny** — lokalny lub zdalny serwer zgodny z OpenAI API.

## llama.cpp

GUI posiada ustawienie `server_chat_template`, w tym wartość `translategemma`. Jest to wybór formatu promptu dla aktywnego runtime llama.cpp i **nie oznacza przywrócenia dawnego backendu FastAPI/Transformers**.

## Cloud

Cloud jest warstwą adapterów/providerów. Dokumentacja providerów musi opisywać aktualny kontrakt V4, a nie historyczny `BackendManager` V3.

## Apertium

Apertium działa jako osobny backend V4 przez Filter Engine. Kompletność dystrybucyjna pary `eng-pol` pozostaje otwartym blockerem release 0.40.0.

## Wycofane ścieżki

- FastAPI + Transformers jako lokalny serwer tłumaczeniowy — **WYCOFANE**.
- Stara ścieżka OpenVINO z modelem TranslateGemma INT8 — **WYCOFANA**.
- `FastAPIServerManager`, `fastapi_server`, `openvino_backend` — **WYCOFANE**.

Szczegóły, powód wycofania i sposób interpretacji starszych dokumentów: `docs/RETIRED_FUNCTIONALITY.md`.

> **Uwaga:** historyczne benchmarki TranslateGemma/FastAPI/OpenVINO są dowodami V3. Nie są bieżącą macierzą funkcji V4.

## Zasada aktualizacji

Nie dopisujemy modelu lub providera do tej dokumentacji tylko dlatego, że występuje w historycznym V3. Najpierw musi istnieć aktywna implementacja V4 i zweryfikowany przepływ użytkownika.

## 2026-10-07 — rozszerzalny kontrakt backendów i wydzielenie „Własny”

Rejestr backendów został przebudowany z routingu opartego na warunkach po nazwie na rejestr instancji. BackendRegistry.register() przyjmuje implementację backendu udostępniającą wspólny kontrakt TranslationBackend; metoda translate() nie zawiera już gałęzi if backend == ....

Wspólny model możliwości jest reprezentowany przez BackendCapabilities i udostępniany przez BackendRegistry.capabilities(). Obsługiwane są deklaratywnie m.in. tłumaczenie batchowe, anulowanie i health-check; brak deklaracji jest bezpiecznie interpretowany przez adapter.

Backend „Własny” (custom) ma teraz własną granicę modułową w src/tlumacz/backends/custom/backend.py. Jest to lokalny lub zdalny serwer zgodny z OpenAI API. Nie jest providerem Cloud i nie jest rejestrowany jako specjalny przypadek CloudRouter. Współdzieli wyłącznie transport OpenAICompatibleProvider, dzięki czemu nie powstaje drugi klient HTTP.

Dodanie nowego backendu nie wymaga zmian w DocumentProcessor, Filter Engine, ChunkPlanner, TranslationOrchestrator, TranslationExecutor ani writerach. Kontrakt rozszerzalności jest testowany przez TestBackend w tests/test_backend_extensibility.py.


## 2026-10-07 — konfiguracja backendów

Wspólny kontrakt aplikacyjny nie przechowuje już pól zależnych od implementacji. BackendRequest i BackendSelection mają tylko backend oraz BackendConfiguration.

BackendConfiguration przekazuje wartości konfiguracji do granicy konkretnego backendu. Przykładowo:
- Cloud interpretuje provider, base_url, api_key, model, engine i timeout;
- custom interpretuje base_url, api_key, model i timeout;
- llama.cpp interpretuje base_url, api_key, model, timeout, compute_mode, chat_template i parallel;
- Apertium nie wymaga konfiguracji backendowej w tym kontrakcie.

Nowy backend może definiować własny zestaw kluczy bez zmiany wspólnych klas wyboru backendu.
