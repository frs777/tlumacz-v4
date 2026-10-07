---
id: cloud-translation-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-01
owner: cloud-runtime
source: src/tlumacz/backends/cloud/
depends_on: [docs/ARCHITECTURE.md, docs/STATUS.md]
expires_when: zmiana kontraktu CloudRouter/providerów
last_validation: "audyt GUI/Cloud V3 → V4 2026-10-01"
---

## 2026-10-05 — aktualny stan Cloud i sekretów

Cloud jest aktywnym backendem. Rejestr domyślny obejmuje OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate, Mozhi i DLX.

QML bridge posiada `SecretStore` i przy odczycie obsługuje migrację starszego `api_key` z profilu do magazynu sekretów. Nowe profile nie powinny zapisywać klucza w zwykłym JSON ustawień.

W dokumentacji nie zapisujemy rzeczywistych kluczy, tokenów ani danych uwierzytelniających. `custom` korzysta z CloudRouter, ale reprezentuje zewnętrzny serwer wskazany przez użytkownika.

# Tłumaczenie w chmurze — Tłumacz V4

Cloud jest aktywnym backendem V4. Orkiestracja odbywa się przez CloudRouter i rejestr providerów; dokumentacja nie opiera się na historycznym V3 BackendManager.

## Aktywne adaptery

W aktualnym kodzie znajdują się adaptery:

- OpenAI-compatible
- DeepL
- Microsoft Translator
- MyMemory
- LibreTranslate
- DLX
- Mozhi jako osobny adapter/provider

Dokładne klasy i kontrakty znajdują się w `src/tlumacz/backends/cloud/`.

## Konfiguracja

Konfiguracja profili Cloud jest częścią mechanizmu V4. Sekrety nie powinny być zapisywane w dokumentacji ani w repozytorium.

## Wycofane ścieżki

FastAPI/Transformers i OpenVINO nie są częścią Cloud ani aktywnej architektury V4. Stare dokumenty opisujące `BackendManager` lub historyczne serwery V3 są materiałem migracyjnym.

## Weryfikacja

Providerzy posiadają testy kontraktowe/kompatybilnościowe. Przy zmianie adaptera aktualizować odpowiedni test i dokumentację.

## Aktualizacja 2026-10-01

SimplyTranslate został wycofany z aktywnej macierzy V4. Połączenie nie zostało skutecznie zestawione; usunięto provider, profil Cloud, ustawienie silnika i test kontraktowy. Historyczne opisy SimplyTranslate pozostają materiałem archiwalnym i nie opisują aktywnej konfiguracji V4.

## 2026-10-06 — walidacja PLAN-05

Zweryfikowano aktywną ścieżkę Cloud/Mozhi względem kodu V4:

- `CloudRouter` pozostaje jedynym punktem wyboru providera; brak automatycznego przełączenia na innego providera.
- Rejestr obejmuje OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate, DLX i Mozhi.
- `Custom` korzysta z istniejącego routera przez provider OpenAI-compatible, bez tworzenia osobnego runtime.
- profile Cloud przechowują konfigurację bez `api_key`; sekret jest zapisywany przez `SecretStore` pod identyfikatorem usługi.
- autodiscovery Mozhi wymaga obecności silnika oraz niepustych list `source_languages` i `target_languages`.
- test live 2026-10-06: `MozhiProvider(base_url="auto", engine="duckduckgo")` przetłumaczył `Hello world` → `Witaj świat`; wybrana instancja: `https://mozhi.aryak.me`.
- timeout i klasyfikacja błędów są pokryte testami; cancellation pozostaje kooperacyjne na granicy orkiestratora/wywołań HTTP i nie implementuje ukrytego retry/fallbacku.

Weryfikacja lokalna: 33 testy Cloud + test Custom — PASS. Pełna suite `tests/` była uruchomiona osobno; globalne problemy jakościowe mypy/Ruff pozostają poza zakresem PLAN-05.
