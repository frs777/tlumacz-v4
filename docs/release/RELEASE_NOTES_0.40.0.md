## Aktualizacja 2026-10-06 — weryfikacja BUG-038

Wcześniej opisany blocker dotyczący braku `u+x` w prywatnym runtime Apertium został usunięty przez właściciela checkoutu. Programy w `native_runtime/bin` i `native_runtime/libexec` mają obecnie prawa wykonywania dla właściciela i grupy.

Regresja `test_bundled_runtime_programs_are_owner_executable` przechodzi: **1 passed, 8 deselected**. Wcześniejszy opis `373 passed, 1 failed` i BUG-038 jako otwartego blokera jest historycznym stanem przed naprawą.

# Tłumacz V4 — release candidate 0.40.0

## Stan

**Data weryfikacji:** 2026-10-06  
**Status:** **Release Candidate — final release niezatwierdzony**  
**Docelowa platforma bieżącej wersji:** Linux x86-64

Wersja 0.40.0 ma zamknięty główny zakres funkcjonalny V4 i przeszła świeży gate jakości, ale pozostają blokery wydaniowe opisane poniżej.

## Potwierdzone i wykonane

- aktywne GUI QML oraz bridge V4;
- aktywne backendy: `llama`, `cloud`, `apertium`, `custom`;
- rzeczywisty E2E TranslateGemma przez GUI, bridge, TranslationApp, DocumentTranslationService i llama.cpp;
- automatyczny start llama.cpp po wyborze backendu oraz ponowny autostart przed tłumaczeniem, jeżeli runtime został zatrzymany;
- zatrzymywanie llama.cpp przy przełączeniu na inny backend;
- trwała konfiguracja GUI oraz rozdzielenie jej od technicznego `llama.json`;
- wybór źródła/celu Apertium z discovery rzeczywiście skompilowanych par;
- bundlowany runtime Apertium z `APERTIUM_DATADIR`;
- aktywny Filter Engine dla DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF;
- Java Filter Host + istniejące filtry Okapi jako warstwa konwersji dokumentów;
- walidacja jednostek, targetów i markerów inline;
- macierz round-trip aktywnych formatów: **28 passed**;
- macierz backendów/dokumentów/GUI/packagingu: **181 passed**;
- Ruff, mypy, compileall i qmllint: **PASS**.

## Bieżący gate

Pełny pytest: **373 passed, 1 failed**.

Jedyna aktualna porażka dotyczy testu właścicielskiego bitu wykonywania prywatnego runtime Apertium: **34 pliki** w `src/tlumacz/backends/apertium/native_runtime/bin/` i `libexec/` nie mają `u+x`. Bieżąca sesja nie ma uprawnień do zmiany trybu tych plików; nie zmieniano właściciela ani ACL.

## Otwarte blokery przed final release

1. **TODO-019 / BUG-038** — przywrócić `u+x` w 34 plikach runtime Apertium i powtórzyć pełny gate.
2. **TODO-020 / BUG-039** — ustalić kanoniczny entrypoint V4 dla testu wersji; `python -m tlumacz --version` nie jest obecnie poprawnym entrypointem, a `/usr/bin/tlumacz` uruchamia historyczny V3.
3. **TODO-021** — powtórzyć clean-wheel build w środowisku z prawidłową własnością repozytorium/konfiguracją Git.
4. **TODO-001 / BUG-003** — domknąć pełny dependency closure i audyt obowiązków licencyjnych komponent-po-komponencie.

Windows/macOS pozostają zakresem przyszłego etapu, a nie blockerem bieżącego Linux Release Candidate.

## Artefakty i bezpieczeństwo zmian

Zmiany większego zakresu wykonywane w ramach przygotowania 0.40.0 mają odpowiadające im backupy w `backups/`. Dokumentacja bieżącego stanu jest prowadzona w `docs/STATUS.md`, `docs/TODO.md`, `docs/BUG.md` i `docs/CHANGELOG.md`.

## Decyzja

**0.40.0 pozostaje Release Candidate. Nie oznaczać jako final release do czasu zamknięcia aktualnych blockerów P0/P1 i ponownego pełnego gate'u.**
