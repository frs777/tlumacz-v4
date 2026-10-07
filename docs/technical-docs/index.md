---
id: technical-docs-index
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.2
updated: 2026-10-07
owner: technical-documentation
source: src/tlumacz/
depends_on: [docs/AGENTS.md, docs/INDEX.md, docs/INDEX.yml, docs/STATUS.md]
expires_when: zmiana struktury dokumentacji technicznej
last_validation: "inspekcja kodu i dokumentacji SentinelX 2026-10-07; kontrakty pipeline i rejestr TPlugin"
---

## 2026-10-05 — mapa techniczna po korelacji z kodem

Najważniejsze aktualne punkty wejścia techniczne:

- `docs/ARCHITECTURE.md` — granice warstw i przepływ dokumentu;
- `docs/technical-docs/functional-capabilities.md` — funkcje potwierdzone w kodzie;
- `docs/technical-docs/models.md` — aktywne backendy i wycofane ścieżki;
- `docs/technical-docs/server-management.md` — lifecycle llama.cpp;
- `docs/wdrozenia/llama-cpp-runtime.md` — dołączony runtime llama.cpp, wybór instancji systemowej i procedura podmiany własną kompilacją;
- `docs/technical-docs/cloud-translation.md` — providerzy Cloud i zasady sekretów;
- `docs/technical-docs/apertium-backend-integration.md` — Apertium i mapowanie języków;
- `docs/technical-docs/QML_GUI_DESIGN.md` i `docs/technical-docs/QML_GUI_LAYOUT.md` — aktualne GUI QML;
- `docs/technical-docs/QML_GUI_TRANSLATION_CARD_SPEC.md` — kontrakt karty Tłumaczenie;
- `docs/STATUS.md` i `docs/TODO.md` — stan i otwarte zadania.

Źródłem prawdy dla zachowania jest aktualny kod i testy. Dokumenty historyczne służą jako dowód przebiegu zmian i nie zastępują opisu bieżącego stanu.

# Tłumacz V4 — dokumentacja techniczna

To jest mapa **aktualnej implementacji V4**. Dokumenty migracyjne, historyczne i archiwalne nie są źródłem bieżącej architektury.

## Źródła prawdy

- `docs/STATUS.md` — bieżący stan projektu.
- `docs/BUG.md` — aktywne defekty i ryzyka.
- `docs/ARCHITECTURE.md` — aktualny model architektury.
- `docs/RETIRED_FUNCTIONALITY.md` — funkcje i technologie wycofane.
- `docs/INDEX.md` / `docs/INDEX.yml` — inwentaryzacja dokumentacji.
- `src/tlumacz/` — implementacja.

## Aktywna architektura

```text
QML GUI
  ↓
application
  ↓
DocumentTranslationService / TranslationOrchestrator
  ↓
Filter Engine
  ↓
llama.cpp / Cloud / Apertium
```

## Aktywne dokumenty techniczne

### Funkcje i pipeline

- `functional-capabilities.md` — macierz funkcji obecnych w kodzie;
- `translation-pipeline-contracts.md` — kanoniczne kontrakty chunk/batch/request, skip, języków, inline codes, lifecycle i jawnej luki nested/complex fields;
- `xliff-pipeline.md` — filtr XLIFF 2.0;
- `apertium-backend-integration.md` — backend Apertium;
- `apertium-pair-packages.md` — architektura i pipeline paczek Apertium;
- `apertium-paczki-reczne-tworzenie.md` — ręczne tworzenie i weryfikacja pojedynczej paczki;
- `tworzenie-paczek-jezykowych.md` — pełna specyfikacja i użycie wewnętrznych narzędzi do seryjnego tworzenia paczek;
- `paczki-jezykowe-specyfikacja.md` — pełny kontrakt paczki językowej (plik w katalogu głównym projektu);
- `cloud-translation.md` — CloudRouter i providerzy;
- `models.md` — aktywne backendy i modele;
- `server-management.md` — lifecycle llama.cpp;
- `user-guide.md` — aktualna powierzchnia użytkownika.

### GUI

- `docs/technical-docs/QML_GUI_DESIGN.md`;
- `GUI-zbior_praktycznej_wiedzy.md` — kompendium połączeń GUI QML → bridge → konfiguracja → runtime → testy;
- `docs/technical-docs/QML_GUI_LAYOUT.md`;
- `docs/technical-docs/QML_GUI_TRANSLATION_CARD_SPEC.md`.

## Dokumenty historyczne

Materiały migracyjne V3 → V4, stare plany refaktoryzacji i historyczne instrukcje Windows zostały przeniesione do `docs/archive/`. Nie należy traktować ich jako instrukcji implementacyjnych.

Materiały FastAPI/OpenVINO/TranslateGemma INT8 pozostają historyczne zgodnie z `docs/RETIRED_FUNCTIONALITY.md`.

## Ważne ograniczenia bieżącego kodu

- brak aktywnego wspólnego detektora Lingua w V4;
- TXT i PDF nie są zarejestrowane w aktywnym `FilterRegistry`;
- `custom` korzysta z CloudRouter;
- `translategemma` jest szablonem czatu llama.cpp, nie backendem;
- klasyczne `src/tlumacz/qt_gui/` zostało usunięte.

## Zasada synchronizacji

Jeżeli dokument techniczny przeczy aktualnemu kodowi lub zweryfikowanemu testowi, pierwszeństwo ma kod i wynik weryfikacji. Każda istotna zmiana dokumentacji wymaga aktualizacji `docs/INDEX.yml` i `docs/DOCUMENTATION_CHANGELOG.md`.


## 2026-10-06 — Filter Engine i bridge Okapi

- `Secyfikacja intelpletacji zastosowania filtrow jezykowych okapi przy pomocy engine napiosanego w pythonike.md` — szczegółowa specyfikacja odtworzeniowa Python Filter Engine + Java/Python Filter Host Bridge, kontraktu JSON Lines, extract/merge, walidacji jednostek i markerów, mapowania ID, XLIFF 1.2/2.x oraz zależności runtime Okapi.


### 2026-10-06 — zarządzanie zależnościami TPlugin

- tplugin-zarzadzanie-zaleznosciami.md — architektura zależności A/B/C, shared-libs, rejestr referencji, checksumy, inventory, GC i proces publikacji.
- tools/tplugin/dependencies.py — narzędzia inventory, validate, rebuild i GC.


### 2026-10-06 — przygotowywanie paczek TPlugin

- tplugin-administracja-pakiety.md — niezależny backend administracyjny i CLI.
- tworzenie-pluginow-okapi/README.md — kanoniczny opis przepływu dokumentowego, Filter Engine, Okapi, preprocessingu, chunkowania, detekcji języka i rekonstrukcji; źródło diagramów: tworzenie-pluginow-okapi/latex/main.tex.
- tplugin-specyfikacja-reczne-tworzenie.md — aktualna specyfikacja formatu i ręcznego tworzenia TPlugin, zgodna z magazynem /home/frs/.config/tlumacz/filters i narzędziami w tools/.
- tplugin-reczne-tworzenie.md — historyczna instrukcja; aktualną wersję zastępuje tplugin-specyfikacja-reczne-tworzenie.md.

### 2026-10-06 — domknięcie backendu administracyjnego TPlugin

- `tplugin-administracja-pakiety.md` — `test-install`, `publish` i raport publikacyjny SHA-256; backend pozostaje poza runtime aplikacji.


### 2026-10-07 — publikacyjny runtime llama.cpp

- `llama.cpp/llama-server` — uniwersalny artefakt Linux x86_64 przeznaczony do publikacji;
- `docs/wdrozenia/llama-cpp-runtime.md` — kontrakt bundled runtime po przejściu na pojedynczą binarkę bez dołączonych bibliotek GGML/Llama.


## 2026-10-07 — rozszerzone kompendium wiedzy projektu

- `kompendium-wiedzy-projektu-v4.md` — skonsolidowany opis aktualnej architektury, pipeline'u, backendów, filtrów, GUI, konfiguracji, bezpieczeństwa, optymalizacji i doświadczeń V3 wykorzystanych w V4;
- `kompendium-wiedzy-projektu-v4.md` jest źródłem treści dla redakcyjnego wydania Word;
- `tlumacz-v4-kompendium-wiedzy (1).docx` — pełne wydanie Word wygenerowane z całej wersji Markdown (610 linii), z wielopoziomowymi nagłówkami, spisem treści, listą schematów, tabelami i blokami schematów;
- dokument został przygotowany na podstawie aktualnego kodu V4, całej bieżącej dokumentacji technicznej oraz wybranych materiałów V3;
- informacje historyczne nie są używane do deklarowania nieistniejących funkcji.


### Aktualizacja 2026-10-07 — analiza testów V4/V3
Kompendium wiedzy zostało rozszerzone o §29A, zawierającą analizę materiałów z `docs/Testy` V4 oraz `docs/TESTY` V3, ze szczególnym naciskiem na kwalifikację dowodów, kompletność dokumentów, integralność struktury, `parallel`/kontekst, klasy regresji oraz metodologię benchmarków.
