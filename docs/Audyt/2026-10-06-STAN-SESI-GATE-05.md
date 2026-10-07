# Stan projektu — sesja 2026-10-06

## Projekt
- Repozytorium: `/home/frs/Projekty/tlumacz-v4`
- Projekt: Tłumacz V4.
- Język dokumentacji i pracy: polski.
- Zasada: po zmianach aktualizować dokumentację; przy dużych zmianach wykonywać backup.

## Aktualny status
Projekt pozostaje w stanie **Release Candidate**, a nie finalnego wydania. Plan 05 pozostaje zamknięty jako gate dokumentacyjno-odbiorczy, ale świeża walidacja wykazała blocker środowiskowo-uprawnieńowy dotyczący prywatnego runtime Apertium oraz osobny problem kontraktu testu entrypointu.

## Świeży gate Planu 05 — 2026-10-06
### Testy
- pełny pytest: **373 passed, 1 failed**.
- jedyny failure:
  `tests/test_apertium_runtime.py::test_bundled_runtime_programs_are_owner_executable`.
- test wykrywa 34 pliki prywatnego runtime Apertium bez bitu `u+x`; tryb obserwowany: `674`.
- lokalizacja: `src/tlumacz/backends/apertium/native_runtime/bin/` oraz `libexec/`.
- próba nadania `u+x` z używanej sesji SentinelX nie mogła zostać wykonana z powodu uprawnień/ACL. Nie zmieniano właściciela ani ACL i nie obchodzono ograniczeń.

### Statyczne gate'y
- Ruff: **PASS**.
- mypy: **PASS**, 0 błędów w 67 plikach źródłowych.
- compileall: **PASS**.
- qmllint: **PASS** dla 6 plików QML.
- macierz backendów/dokumentów/GUI/packagingu: **181 passed**.
- launcher `uruchom-tlumacz-v4.sh`: składnia i bit wykonywania **PASS**.

### Entry point / packaging
- `python -m tlumacz --version`: **FAIL**, brak `tlumacz.__main__`.
- `pyproject.toml` deklaruje:
  `tlumacz = "tlumacz.qml_gui.app:main"`.
- `src/tlumacz/qml_gui/app.py` posiada `main()` oraz blok `if __name__ == "__main__"`.
- globalny `/usr/bin/tlumacz` wskazuje na globalną instalację V3 i nie jest wiarygodnym testem V4.
- clean-wheel build nie został ukończony z powodu Git `dubious ownership` dla `/home/frs/Projekty`.
- nie wykonywano destrukcyjnych zmian w nadrzędnym katalogu repozytoriów.

## Otwarte blokery / TODO
### BUG-038
Prywatny runtime Apertium zawiera 34 programy bez bitu wykonywania właściciela. P1, otwarte.
Docelowo należy przywrócić `u+x` tym plikom i ponowić gate. Nie obchodzić ACL/uprawnień ani nie zmieniać właściciela bez właściwych uprawnień.

### BUG-039
Kontrakt testu entrypointu V4 jest niespójny z aktualnym sposobem uruchamiania pakietu: `python -m tlumacz --version` nie działa, podczas gdy script entrypoint w `pyproject.toml` wskazuje na `tlumacz.qml_gui.app:main`. Należy ustalić kanoniczny entrypoint V4 i odpowiednio zweryfikować test.

### TODO-021
Powtórzyć clean-wheel build w środowisku z prawidłową własnością repozytorium/Git.

## Potwierdzone wcześniejsze ustalenia
### Plan 02
- usunięto TranslationController, SettingsController, DocumentController, ProgressController, DiagnosticsController.
- zachowano BackendController.
- usunięto `src/tlumacz/backends/cloud/profile_migration.py` i test.
- usunięto `DocumentProcessor._unit_parts()`.
- SecretStore pozostaje aktywny.
- entrypoint `pyproject.toml`: `tlumacz = "tlumacz.qml_gui.app:main"`.
- plan zakończony; historycznie 363 passed, compileall/qmllint PASS.

### Plan 03
- zamknięty po naprawie regresji.
- focused P1/P2: 128 passed.
- historycznie pełny pytest: 367 passed, 0 failed.
- compileall/qmllint PASS.
- wcześniejsze Ruff/mypy issues zostały później usunięte w quality gate Planu 04.

### Plan 04
- baseline optymalizacyjny nie wykazał bezpiecznej optymalizacji produkcyjnej wymagającej zmiany parametrów.
- Java cold-start około 1,61 s.
- warm IPC mediana około 0,37 ms/request.
- Markdown 200 jednostek około 7,96 ms/document średnio.
- QML startup około 0,30 s, root około 1309 QObject, refresh skills około 0,0715 ms, zmiana języka około 13,95 ms.
- później naprawiono statyczne błędy Ruff/mypy bez sztucznej optymalizacji.
- najnowszy pełny pytest po tych zmianach: 369 passed.
- Ruff PASS, mypy PASS, compileall PASS, qmllint PASS.

## Apertium
- skompilowana para `eng-pol` znajduje się w `/home/frs/.config/tlumacz/Apertium/apertium-en-pl/`.
- `ApertiumRuntime.data_dir_for_pair()` zostało poprawione tak, aby runtime otrzymywał katalog nadrzędny paczek.
- realna translacja `Hello world.` → `@hello #Świat.` została zweryfikowana.
- detekcja języka GUI Apertium korzysta z Lingua, nie LibreTranslate.
- `source_language` nie jest nadpisywane wynikiem detekcji; wynik Lingua trafia do `detectedSourceLanguage`.
- regresja English → French → German: dokument rozpoznawany jako en, fr/de pomijane przez zamrożony routing Apertium.
- przycisk „Restartuj serwer” llama.cpp uruchamia serwer również wtedy, gdy nie był aktywny; dodano test regresyjny.
- TranslationPage.qml ma informacyjne pola `apertiumSourceLanguageLabel` i `apertiumTargetLanguageLabel`, widoczne tylko dla Apertium.
- długie treści QML zostały wydzielone do plików UTF-8 PL/EN/DE.

## Znane kwestie poza bieżącym gate'em
### BUG-037 — pary Apertium
- pol-rus poprawione.
- pl-sk poprawione.
- pl-csb poprawione, ale duplikaty `pardef` nadal wymagają decyzji semantycznej.
- pl-uk wymaga historycznego `apertium-3.2`.
- nie ruszać bez odpowiedniego planu/zakresu.

### Filter Engine
Historyczny raport `ustawienia.txt` wskazywał błąd:
`FilterEngineError: Backend zmodyfikował lub zgubił markery inline Filter Engine`.
Problem występował przed apply()/writerem Okapi. Hipoteza dotyczy granicy `_translate_chunk()` → backend. Brak dowodu bez przechwycenia masked request/raw response.

## Dokumentacja zaktualizowana podczas gate'u
Zaktualizowano:
- `docs/Plany/05-FINALNY-GATE-I-ODBIOR.md`
- `docs/STATUS.md`
- `docs/TODO.md`
- `docs/BUG.md`
- `docs/CHANGELOG.md`
- `docs/DOCUMENTATION_CHANGELOG.md`

Wykonano backupy tych plików przed edycjami. Nie zmieniano `INDEX.md`/`INDEX.yml`, ponieważ nie dodawano nowych plików dokumentacyjnych w tamtej operacji.

## Ostatnia decyzja
Nie oznaczać projektu jako final release. Najbliższe działania są konkretne:
1. przywrócić prawidłowe `u+x` w 34 plikach prywatnego runtime Apertium w środowisku mającym właściwe uprawnienia;
2. ponowić pełny gate;
3. rozstrzygnąć kanoniczny entrypoint V4 i kontrakt testu;
4. ponowić clean-wheel build przy poprawnej własności Git;
5. dopiero po świeżej weryfikacji rozważyć finalne zatwierdzenie.

## Zasada pracy na dalszą sesję
Nie wykonywać zmian poza zakresem planu. Nie obchodzić uprawnień/ACL. Nie modyfikować V3. Każdą zmianę kodu prowadzić TDD i po zmianie aktualizować dokumentację; przed deklaracją sukcesu wykonać świeżą weryfikację.
