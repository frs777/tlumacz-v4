## 2026-10-05 — kontrakt testowania struktury QML Apertium

Dla zmian układu TranslationPage.qml testy muszą sprawdzać nie tylko obecność nazw kontrolek, ale także ich relację strukturalną. Sekcja translationControlsSection zawiera sterowanie i zwykły wybór języka docelowego, natomiast apertiumLanguageSection jest osobnym kontenerem z GridLayout { columns: 2 }.

Test regresyjny test_qml_apertium_translation_controls_use_two_columns_with_labels_above pilnuje, aby pola Apertium nie wróciły do RowLayout przycisków.

Dla ręcznej weryfikacji runtime zalecane jest uruchomienie uruchom-v4.sh, który ustawia ścieżkę źródłową V4 i developerskie ustawienia QML opisane niżej.

# Development V4

## Testowanie

Zmiany zachowania realizujemy w cyklu RED -> GREEN -> REFACTOR.

Podstawowy test:

    python -m pytest -q

Quality gates:

    ruff check .
    mypy src
    python -m pytest -q

Instalowanie zależności nie jest częścią bootstrapu. Środowisko zależności będzie przygotowane w odpowiednim etapie migracji.

## Uruchamianie V4 ze źródła

Repozytorium używa układu `src/`. Pakiet źródłowy znajduje się wyłącznie w `src/tlumacz/`; nie ma repozytoryjnego shim-u `tlumacz` w katalogu głównym. Uruchamianie V4 ze źródeł wymaga jawnego wskazania `src`:

```bash
cd /home/frs/Projekty/tlumacz-v4
PYTHONPATH=src python -m tlumacz.qml_gui.app
```

To odpowiada konfiguracji `setuptools` (`where = ["src"]`) i eliminuje podwójną ścieżkę importu.

## Launcher V4

Do uruchamiania V4 z repozytorium używany jest `uruchom-v4.sh`. Launcher wyznacza katalog projektu na podstawie własnej lokalizacji, ustawia `PYTHONPATH` na jego `src` i uruchamia `tlumacz.qml_gui.app`, czyli źródłowy interfejs Qt Quick/QML.

Launcher ustawia również `QML_DISABLE_DISK_CACHE=1`, aby podczas pracy developerskiej QML było ładowane bezpośrednio ze źródeł.

Systemowy `/usr/bin/tlumacz` pozostaje historycznym launcherem V3 i nie jest używany przez launcher V4.
