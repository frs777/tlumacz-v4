---
id: retired-functionality-v4
status: active
meta:
  contentType: Governance
  category: governance
version: 1.0.0
updated: 2026-10-01
owner: project-documentation
source: docs/Audyt/AUDYT_FORENSICZNY_V3_V4_2026-10-01.md
depends_on: [docs/STATUS.md, docs/ARCHITECTURE.md]
expires_when: zmiana decyzji architektonicznej V4
last_validation: "audyt forensyczny i regresji GUI/Cloud 2026-10-01"
---

# Funkcjonalności wycofane z Tłumacza V4

Ten dokument jest **rejestrem wycofanych funkcjonalności**. Jego celem jest zapobieganie sytuacji, w której historyczny dokument V3 zostanie omyłkowo potraktowany jako instrukcja aktywnego V4.

## 1. FastAPI + Transformers — WYCOFANE

**Status:** nieaktywne w V4.

Historyczny lokalny serwer FastAPI/Transformers był ścieżką tłumaczenia V3. Nie został przeniesiony do aktywnej architektury V4. Nie dodawać zależności, entrypointów, konfiguracji ani rekordów GUI dla tej ścieżki.

Powód architektoniczny: V4 ma rozdzielone backendy i runtime'y; aktywny lokalny kierunek to llama.cpp, a pozostałe aktywne kierunki to Cloud i Apertium.

## 2. Stara ścieżka OpenVINO z modelem TranslateGemma INT8 — WYCOFANA

**Status:** nieaktywne w V4.

Historyczna ścieżka uruchomieniowa OpenVINO z modelem TranslateGemma INT8 nie jest aktywna w V4 i nie należy jej reaktywować na podstawie benchmarków, instrukcji instalacji ani starych konfiguracji.

Uwaga: nazwa **TranslateGemma** może nadal występować w V4 jako wartość `server_chat_template` dla llama.cpp. To nie jest to samo co historyczny backend OpenVINO/FastAPI.

## 3. Stare zarządzanie backendami V3 — WYCOFANE JAKO MODEL ARCHITEKTONICZNY

Stary model, w którym `MainWindow`/`BackendManager` bezpośrednio zarządzały historycznymi backendami V3, nie jest docelowym modelem V4.

Aktywna architektura V4 opiera się na warstwach application/domain/backends/filter_engine/infrastructure/interfaces oraz aktywnych backendach llama.cpp, Cloud i Apertium.

Nie przenosić opisów starego `BackendManager` do nowych dokumentów technicznych bez sprawdzenia aktualnego kodu.

## 4. Stare konfiguracje i instrukcje

Historyczne pliki opisujące FastAPI/OpenVINO/TranslateGemma jako serwery V3 mogą pozostać w archiwum lub jako dowód migracji. Muszą być oznaczone jako `historical`/`superseded` w indeksie i nie mogą być wymieniane w indeksach aktywnej dokumentacji.

Dotyczy to w szczególności dokumentów zawierających:

- `FastAPIServerManager`;
- `fastapi_server`;
- `openvino_backend`;
- FastAPI + Transformers;
- OpenVINO + TranslateGemma INT8.

## 5. Jak czytać stare dokumenty

Jeżeli dokument historyczny opisuje wycofaną funkcję:

1. traktuj go jako dowód historyczny, nie instrukcję;
2. sprawdź `docs/RETIRED_FUNCTIONALITY.md`;
3. sprawdź `docs/STATUS.md` i aktualny kod;
4. dopiero potem użyj informacji historycznej do analizy migracji lub regresji.

## 6. Reguła dla przyszłych zmian

Nowy dokument techniczny nie może opisywać wycofanej funkcjonalności jako aktywnej. Jeżeli nazwa jest potrzebna do opisania migracji, regresji albo kompatybilności, należy użyć jawnego oznaczenia `HISTORYCZNE` lub `WYCOFANE`.