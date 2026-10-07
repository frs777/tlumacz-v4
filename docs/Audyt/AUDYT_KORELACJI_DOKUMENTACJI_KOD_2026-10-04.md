---
id: audyt-korelacji-dokumentacji-kod-2026-10-04
status: evidence
meta:
  contentType: Audit
  category: audit
version: 1.0.0
updated: 2026-10-04
owner: project-documentation
source:
  - src/tlumacz/qml_gui/bridge.py
  - src/tlumacz/application/translation_app.py
  - src/tlumacz/backends/llama_cpp/adapter.py
  - src/tlumacz/language_detector.py
  - src/tlumacz/backends/cloud/
  - tests/test_qml_gui.py
  - tests/test_translategemma_special_mode.py
depends_on: [docs/AGENTS.md, docs/ARCHITECTURE.md, docs/STATUS.md, docs/technical-docs/functional-capabilities.md]
expires_when: kolejna merytoryczna zmiana aktywnego kontraktu aplikacji, backendów lub GUI
last_validation: "SentinelX 2026-10-04; pytest 268 passed; compileall PASS; qmllint PASS"
---

# Audyt korelacji kodu z dokumentacją — 2026-10-04

## Zakres

Sprawdzono najnowsze zmiany kodu i testów względem dokumentacji aktywnej. Zakres obejmował bridge QML, lifecycle llama.cpp, specjalny tryb TranslateGemma, SecretStore/Cloud, aktywne kontrolery GUI, powierzchnię QML oraz instrukcję uruchamiania.

## Potwierdzone zmiany i pokrycie dokumentacyjne

| Obszar | Dowód w kodzie/testach | Dokumentacja | Stan |
|---|---|---|---|
| Restart llama.cpp | `TranslationApp.restart_llama()` | `ARCHITECTURE.md`, `STATUS.md`, `CHANGELOG.md` | zgodne |
| TranslateGemma | `LlamaCppAdapter`, `LanguageDetector`, test specjalnego trybu | `ARCHITECTURE.md`, `functional-capabilities.md`, podręcznik, TODO | zgodne; E2E aplikacyjne nadal TODO |
| SecretStore | `QmlApplicationBridge`, migracja starszego `api_key` | `STATUS.md`, `TODO.md`, `BUG.md`, `DOCUMENTATION_CHANGELOG.md` | zgodne |
| Kontrolery GUI | aktywny `BackendController`; pozostałe usunięte | `ARCHITECTURE.md`, `functional-capabilities.md`, `TODO.md`, EN/DE | zgodne |
| QML bridge | właściwości i akcje backendu, ustawień, glosariusza, skilli i motywu | `QML_GUI_DESIGN.md`, `QML_GUI_LAYOUT.md`, `STATUS.md` | zgodne |
| Ikony motywu | `tlumacz-dark.svg`, `tlumacz-light.svg`, logika `app.py` | `QML_GUI_DESIGN.md`, `STATUS.md`, audyt GUI | zgodne |
| Uruchamianie V4 | aktywny `qml_gui` | EN/DE `development.md` | zgodne |
| Apertium | aktywny moduł `backends/apertium/` i Filter Engine | `apertium-backend-integration.md`, `ARCHITECTURE.md` | zgodne |

## Znalezione i naprawione rozbieżności

1. Dokumentacja opisywała usunięte kontrolery jako aktywne. Zastąpiono ten opis stanem po cleanupie; `BackendController` pozostaje jedynym zachowanym kontrolerem z tej grupy.
2. Dokumentacja EN/DE wskazywała stare `qt_gui/app.py` i `qt_gui/view_builders.py`. Zaktualizowano architekturę oraz komendy developerskie do `qml_gui`.
3. Opis źródła języka twierdził, że V4 nie ma detektora Lingua. Skorygowano go: `language_detector.py` jest aktywny wyłącznie dla TranslateGemma.
4. Dokument Apertium zawierał nieaktualny model `Translator`/`BackendManager` i historyczne ścieżki. Zastąpiono go aktualnym kontraktem V4.
5. `INDEX.yml` zawierał artefakt backupowy pod `docs/backups/`; usunięto go zgodnie z polityką dokumentacji i odświeżono indeks.

## Weryfikacja końcowa

- pełny pytest: **268 passed**;
- `python3 -m compileall -q src tests`: **PASS**;
- `qmllint src/tlumacz/qml_gui/*.qml`: **PASS**;
- indeks: **444** pliki / **444** wpisy;
- brak missing/orphan w INDEX;
- brak uszkodzonych lokalnych linków Markdown;
- brak backupów technicznych pod `docs/`;
- `docs/_inbox/` pozostaje zgodny z wcześniejszym porządkiem i nie zawiera nowych materiałów poza `AGENT.md`.

## Wniosek

Po wykonanej synchronizacji nie stwierdzono znanej, istotnej rozbieżności między aktualnym kodem a aktywną dokumentacją w zakresie sprawdzonych zmian. Pozostaje znany zakres niedomknięty funkcjonalnie: pełne E2E TranslateGemma przez rzeczywistą aplikację oraz otwarte blokery wydaniowe zapisane w `STATUS.md`/`TODO.md`.