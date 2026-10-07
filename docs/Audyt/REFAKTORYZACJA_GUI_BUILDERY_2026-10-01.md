# Audyt techniczny — dekompozycja builderów GUI

**Data:** 2026-10-01  
**Zakres:** Tłumacz V4, warstwa `qt_gui`  
**Etap:** P1 — dalsza dekompozycja `MainWindow`

## Cel

Usunięcie budowy czterech zakładek Qt z `MainWindow` bez zmiany aktywnej powierzchni GUI, callbacków i kontraktów aplikacyjnych.

## Zmiana architektoniczna

Dodano `src/tlumacz/qt_gui/view_builders.py` z funkcjami:

- `build_translation_tab()`;
- `build_api_tab()`;
- `build_extras_tab()`;
- `build_help_tab()`.

`MainWindow` pozostał właścicielem stanu okna, prezenterów, workera i operacji aplikacyjnych. Buildery są warstwą konstrukcji widoku Qt i korzystają z callbacków udostępnianych przez okno.

## Zakres zachowany

- cztery zakładki: Tłumaczenie, API i serwer, Dodatki, Pomoc;
- nazwy obiektów Qt wymagane przez test parytetu;
- konfiguracja Cloud/Apertium/llama.cpp;
- ustawienia dokumentów, glosariusza i umiejętności;
- obsługa pomocy i dialogu „O programie”.

Nie zmieniano logiki backendów ani przepływu tłumaczenia.

## TDD

1. Dodano test kontraktowy `tests/test_gui_view_builders.py`.
2. Pierwszy przebieg po dodaniu importu nowego modułu był RED: `ImportError` dla `view_builders`.
3. Zaimplementowano buildery i podłączono je do `MainWindow`.
4. Test przeszedł GREEN.
5. Test parytetu został dostosowany do nowej granicy modułowej.

## Weryfikacja końcowa

- **pytest:** 206 passed;
- **Ruff:** PASS;
- **compileall:** PASS;
- `MainWindow`: 579 → **253 linii**;
- `view_builders.py`: **354 linii**.

## Backup

`/home/frs/Projekty/agent-translator-v3/backups/tlumacz-v4-tab-builders-20261001/pre-tab-builders.tar.gz`

## Następne kroki

- integracja `DiagnosticsController` w aktywnej ścieżce GUI;
- audyt parytetu funkcjonalnego V3/V4 dla Własny, DLX, Apertium i TranslateGemma;
- pełny round-trip ustawień `AppSettings` po dalszych zmianach.
