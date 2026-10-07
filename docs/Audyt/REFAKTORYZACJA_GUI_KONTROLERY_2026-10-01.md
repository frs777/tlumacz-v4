# Refaktoryzacja kompetencji GUI — 2026-10-01

## Zakres

Drugi etap dekompozycji `MainWindow` po wydzieleniu rdzenia aplikacyjnego.

## Zmiany

Wydzielono:

- `BackendPresenter` — powierzchnia wyboru backendu i budowa `BackendRequest`;
- `SettingsPresenter` — mapowanie `AppSettings` na kontrolki oraz zapis/reset;
- `DocumentPresenter` — wybór i przygotowanie ścieżek dokumentów;
- `ProgressPresenter` — mapowanie `ProgressController` na `QProgressBar`;
- `TranslationWorker` — wykonanie tłumaczenia dokumentu poza wątkiem GUI.

`TranslationApp` posiada teraz kontrolery backendu, ustawień, dokumentu, postępu i diagnostyki.

## Trwałość konfiguracji

`AppSettings` otrzymał:

- `last_input_path`;
- `last_output_path`.

`server_gguf_path` został zachowany i objęty tym samym testem round-trip. Test GUI sprawdza zapis wszystkich trzech ścieżek do stanu ustawień.

## Efekt architektoniczny

`MainWindow` zmniejszył się z 819 do 579 linii. Nie zawiera już implementacji workera ani logiki wyboru backendu, mapowania ustawień i obsługi ścieżek dokumentów.

Pozostaje do wydzielenia budowa zakładek/widoków oraz pełna integracja diagnostyki.

## Weryfikacja

- testy skoncentrowane GUI/kontrolerów: **15 passed**;
- pełny suite z `QT_QPA_PLATFORM=offscreen`: **205 passed**;
- Ruff: **PASS**;
- compileall: **PASS**.

Nie wykonywano realnych requestów Cloud.

## Backup

Przed rozpoczęciem etapu wykonano:

`/home/frs/Projekty/agent-translator-v3/backups/tlumacz-v4-p1-mainwindow-20261001/pre-p1-state-refactor.tar.gz`

## Następny etap

Dalsze wydzielenie budowy zakładek GUI i integracja `DiagnosticsController`, następnie przejście do funkcji parytetu V3/V4.
