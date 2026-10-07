---
id: report-plan-07-security-lifecycle-2026-10-06
date: 2026-10-06
status: partial
plan: PLAN-07-SECURITY-LIFECYCLE-2026-10-05
---

# Raport realizacji PLAN-07 — Security / Lifecycle

## Zakres

Zrealizowano pierwszą fazę planu dotyczącego:
- izolacji sekretów od settings JSON;
- migracji legacy sekretów;
- centralnego shutdown;
- lifecycle cache SQLite;
- ownership procesu llama.cpp;
- integracji QGuiApplication.aboutToQuit.

## Zmiany kodu

### SecretStore / settings

1. QmlApplicationBridge wykonuje migrację legacy sekretów przed normalnym ładowaniem ustawień.
2. Migracja obejmuje:
   - lokalny klucz legacy api_key / last_local_api_key;
   - wszystkie profile Cloud zawierające legacy api_key.
3. Po migracji legacy pola są zerowane w AppSettings.
4. Zapis przez bridge nie utrwala sekretów w config.json.
5. Istniejący kontrakt SecretStore z plikiem $HOME/.config/tlumacz/.key pozostaje zachowany.

### Lifecycle llama.cpp

1. TranslationApp.stop_llama() nie usuwa referencji do runtime, jeśli proces nadal działa po odmowie shutdown z powodu niezgodnej ProcessIdentity.
2. W takim przypadku zgłaszany jest jawny RuntimeError zamiast cichego pozostawienia orphan process.
3. TranslationApp.close() korzysta z try/finally, dzięki czemu zamknięcie cache jest wykonywane również po błędzie shutdown runtime.
4. QGuiApplication.aboutToQuit nadal prowadzi do centralnego TranslationApp.close().

### SQLite cache

1. TranslationCache.close() pozostaje podstawowym, deterministycznym mechanizmem zamknięcia połączenia.
2. Dodano awaryjny __del__ jako defense-in-depth dla połączeń, które nie zostały zamknięte przez normalny lifecycle.
3. Finalizer nie propaguje wyjątków.

## Testy dodane / rozszerzone

- migracja wszystkich legacy Cloud secrets;
- brak sekretów w config.json po zapisie przez bridge;
- shutdown cache po błędzie runtime;
- zachowanie referencji do runtime przy ownership mismatch;
- cleanup SQLite jako zabezpieczenie lifecycle.

## Walidacja

### PASS

- Focused security/lifecycle suite: **32 passed**.
- Focused suite z -W error::ResourceWarning: **32 passed**.
- Ruff dla zmienionego zakresu przed rozszerzeniem cache lifecycle: **PASS**.
- compileall: **PASS**.
- Kontrola aktywnych llama-server: brak nasłuchującego procesu.
- Kontrola otwartych uchwytów SQLite dla cache: brak aktywnych uchwytów.

### Znane blokery pełnego gate

Pełny pytest nie jest obecnie zielony.

1. Niezależny failure:
   tests/test_document_translation_service.py::test_document_translation_service_applies_skip_patterns_before_backend

   Obserwacja: FilterWithSkippableUnits zwraca jednostkę pomijaną, ale writer HTML otrzymuje niepełny zestaw targetów. Jest to problem istniejącego kontraktu skip-pattern / Filter Engine i nie wynika z bieżących zmian PLAN-07.

2. Pełny przebieg pytest po wcześniejszych failure'ach zakończył się fatalnym abortem procesu Python w wątkach tlumacz-filter podczas raportowania testu. Stack wskazuje na filter_engine/protocol.py w _read_stderr / _read_responses oraz Qt6/PySide6 podczas finalizacji.

3. Mypy dla wskazanych plików GUI/application ujawnił istniejące błędy w zależnych modułach llama_cpp/runtime.py i apertium/runtime.py. Nie są częścią bieżącego zakresu i nie zostały zmienione.

4. Globalny Ruff nadal ma istniejące błędy poza PLAN-07 (m.in. filter_store.py, registry.py, tplugin.py oraz istniejące testy). Nie zostały naprawiane, zgodnie z zasadą planu o niewprowadzaniu zmian poza zakresem.

## Backupy

- SECURITY-LIFECYCLE-BASELINE-2026-10-06.tar.gz
  - pełny baseline projektu;
  - SHA-256: 813d67312c27d03f758a968b2bc23292d1a1a839c2d40a81b1d9d982c4fddf1f
- SECURITY-LIFECYCLE-PHASE1-2026-10-06.tar.gz
- SECURITY-LIFECYCLE-PHASE2-2026-10-06.tar.gz
- SECURITY-LIFECYCLE-DOCS-CHECKPOINT-2026-10-06.tar.gz

## Dokumentacja

Zaktualizowano:
- docs/Plany/PLAN-07-SECURITY-LIFECYCLE-2026-10-05.md
- docs/Plany/PLAN-2026-10-05.md
- docs/STATUS.md
- docs/CHANGELOG.md

## Status PLAN-07

**IMPLEMENTACJA CZĘŚCIOWA — NIE ZAMYKAĆ PLANU.**

Spełnione są główne lokalne wymagania security/lifecycle i focused gate jest zielony. Exit gate całego segmentu wymaga jeszcze rozwiązania niezależnego problemu Filter Engine/skip-pattern, ponownego pełnego pytest bez fatal abort oraz końcowej kontroli orphan processes.


## 2026-10-07 — korekta kontraktu konfiguracji i gate

- Kanoniczny plik trwałej konfiguracji GUI: `$HOME/.config/tlumacz/config.json`.
- `settings-v4.json` nie jest używany przez aktywny kod i nie może być odtwarzany.
- Aktywny katalog `/home/frs/.config/tlumacz/` nie zawiera `settings-v4.json`; istnieje wyłącznie kopia backupowa tego pliku.
- Wykonano backup przed dalszą pracą nad gate: `backups/PLAN-07-GATE-PRECONFIG-2026-10-07.tar.gz`.
- SHA-256 backupu: `1cc4c1d870a45a7146a67bbcf3695210dd4c0c2661d36debb3eed1f81373e972`.
- Świeża pełna walidacja suite została uruchomiona; status gate pozostaje otwarty do czasu otrzymania wyniku oraz końcowej kontroli ResourceWarning/orphan processes.

### Korekta po unifikacji konfiguracji — 2026-10-07

Jedynym aktywnym plikiem trwałych ustawień GUI jest `$HOME/.config/tlumacz/config.json`. `settings-v4.json` został usunięty po migracji i backupie. Klucze API nadal nie są zapisywane w `config.json`; obsługuje je `SecretStore`.
