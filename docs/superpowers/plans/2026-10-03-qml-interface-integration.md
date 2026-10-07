# Integracja i naprawa GUI QML V4 — plan implementacji

> **Dla agentów:** realizować zadania kolejno w cyklu TDD; po każdym zadaniu uruchomić jego testy i kontrolę QML.

**Cel:** doprowadzić główną warstwę QML do rzeczywistego kontraktu aplikacji V4: lokalizacja ma działać w całym GUI, profile Cloud mają zachowywać własną konfigurację, a kontrolki parametrów mają przekazywać stan do istniejącego rdzenia bez duplikowania logiki domenowej.

**Architektura:** QML pozostaje warstwą prezentacji. `QmlApplicationBridge` jest jedynym mostem akcji i stanu; `TranslationApp`/usługi aplikacyjne pozostają właścicielem tłumaczenia i backendów. Nie reaktywujemy Qt Widgets ani nie dokładamy nowego backendu.

**Technologie:** Python 3, PySide6, Qt Quick/QML, istniejący system `tlumacz.i18n`, pytest.

**Spec:** `docs/technical-docs/QML_GUI_DESIGN.md`

## Ograniczenia

- Językiem źródłowym GUI jest polski; EN/DE są lokalizacjami.
- Aktywne typy GUI: llama.cpp, Apertium, Chmura, Własny.
- QML nie zawiera logiki domenowej.
- Nie instalować ani usuwać zależności.
- Po zmianach dokumentacja musi zostać zaktualizowana.
- Został wykonany backup przed zmianą: `backups/qml-interface-repair-20261003/pre-repair-qml-docs.tar.gz`.

## Zakres

### Zadanie 1 — lokalizacja QML
**Pliki:** `src/tlumacz/qml_gui/bridge.py`, `src/tlumacz/i18n.py`, wszystkie strony QML, testy GUI.

- Dodać most `bridge.tr(key)` korzystający z kanonicznego `tlumacz.i18n.t()`.
- Utrzymać zależność bindingów QML od bieżącego języka, aby zmiana PL/EN/DE odświeżała teksty bez restartu.
- Zastąpić statyczne etykiety i komunikaty w czterech stronach kluczami i18n.
- Uzupełnić brakujący klucz „Parametry” zamiast używać historycznego „Dodatki”.
- Przetestować co najmniej zmianę języka oraz obecność kluczowych tekstów w QML.

### Zadanie 2 — profile Cloud
**Pliki:** `src/tlumacz/qml_gui/bridge.py`, `tests/test_gui_regression_v3_v4.py`.

- Przy zmianie profilu ładować z profilu: provider, endpoint, model/engine oraz zapisany klucz API.
- Przy edycji endpointu/modelu/klucza zapisywać zmianę do aktywnego profilu Cloud, bez współdzielenia sekretów między usługami.
- Zachować istniejące profile, jeśli konfiguracja użytkownika już je posiada.
- Dodać regresję ChatGPT/Codex przy wspólnym providerze `openai`.

### Zadanie 3 — stan serwera w bridge
**Pliki:** `src/tlumacz/qml_gui/bridge.py`, `src/tlumacz/qml_gui/ApiPage.qml`, testy.

- Wystawić jawne `llama_server_running` zamiast wykrywania stanu przez porównanie tekstu statusu.
- Przycisk uruchom/zatrzymaj ma korzystać z tego stanu.
- Po zmianie stanu odświeżać UI sygnałem bridge.
- Nie zmieniać lifecycle `TranslationApp`.

### Zadanie 4 — dokumentacja i walidacja
- Uzupełnić `docs/technical-docs/QML_GUI_DESIGN.md` o faktycznie wdrożone połączenia.
- Dopisać zmianę do `docs/DOCUMENTATION_CHANGELOG.md`.
- Odświeżyć `docs/INDEX.yml` tylko w zakresie zmienionych dokumentów.
- Uruchomić testy QML/GUI, compileall, Ruff oraz pełny suite projektu.
- Sprawdzić `git diff --check` przez narzędzie uruchomione jako właściciel repozytorium, bez zmiany globalnej konfiguracji Git.

## Kryteria akceptacji

- Zmiana języka PL/EN/DE aktualizuje widoczne teksty QML bez restartu.
- Profil Cloud nie dziedziczy sekretu poprzedniego profilu.
- GUI pokazuje prawdziwy stan llama.cpp.
- Istniejące akcje tłumaczenia, anulowania, plików, skilli i ustawień pozostają działające.
- Testy regresyjne przechodzą, a pełna walidacja nie wykazuje nowych błędów.
