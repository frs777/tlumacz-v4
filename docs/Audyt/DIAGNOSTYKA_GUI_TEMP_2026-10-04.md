---
id: diagnostyka-gui-temp-2026-10-04
status: historical
meta:
  contentType: Diagnostic Note
  category: audit
version: 1.0.0
updated: 2026-10-05
owner: gui-maintenance
source: src/tlumacz/qml_gui/, tests/
depends_on: [docs/STATUS.md, docs/technical-docs/QML_GUI_LAYOUT.md]
expires_when: zastąpienie pełnym raportem diagnostycznym
last_validation: "materiał tymczasowy przeniesiony do archiwum audytowego 2026-10-05"
---

# Tymczasowa notatka diagnostyczna — V4 GUI: zmiany w TranslationPage.qml niewidoczne

**Data:** 2026-10-04  
**Projekt:** Tłumacz V4  
**Status:** DIAGNOSTYKA W TOKU — dokument tymczasowy

## 1. Problem

W aktywnym GUI Tłumacza V4 nie są widoczne ostatnie zmiany w `TranslationPage.qml`, mimo że plik źródłowy został zmodyfikowany i testy regresyjne potwierdzają oczekiwaną strukturę QML.

Dotyczy to przede wszystkim układu sekcji Apertium:
- „Język źródłowy” i „Język docelowy” powinny być dwiema kolumnami,
- etykieta ma znajdować się nad kontrolką,
- oba pola mają być w jednym wierszu,
- blok nie może być zagnieżdżony w wierszu przycisków.

Dodatkowo użytkownik oczekiwał, aby okna Log i Podgląd miały tę samą wysokość.

## 2. Co zostało już poprawione w kodzie

W `src/tlumacz/qml_gui/TranslationPage.qml`:
- blok języków Apertium został przeniesiony poza `RowLayout` przycisków,
- zastosowano `GridLayout` z dwiema kolumnami,
- każda kolumna ma `Label` oraz `TextField`,
- usunięto zbędny nagłówek `translation.language`,
- Log i Podgląd mają `Layout.preferredHeight: 180`.

Dodano testy regresyjne pilnujące:
- dwóch kolumn i dwóch zestawów Label/TextField,
- braku starego `Layout.preferredWidth: 150`,
- prawidłowego umiejscowienia `GridLayout` poza `RowLayout`,
- równej wysokości Log/Podgląd.

Ostatnia pełna weryfikacja przed rozpoczęciem obecnej diagnostyki:
- pytest: **277 passed**,
- `compileall`: PASS,
- `qmllint`: PASS,
- uruchomienie GUI offscreen kończyło się kodem 124 od timeoutu, co było oczekiwane dla działającej aplikacji GUI.

## 3. Hipoteza cache — wykluczona jako główna przyczyna

Sprawdzono:
- brak kopii `TranslationPage.qml` w innych lokalizacjach pod `/home/frs`,
- brak `.qmlc`, `.jsc` i projektowego `qmldir` w repozytorium,
- brak cache QML zawierającego kopię projektu/TranslationPage,
- brak podstaw do stwierdzenia, że Qt ładuje starą kopię pliku projektu.

Wniosek: **nie znaleziono dowodu na cache jako przyczynę.**

## 4. Hipoteza starego launchera / wersji 0.3.2

Istnieje stara instalacja:
- `/usr/bin/tlumacz`,
- systemowy `tlumacz.desktop`,
- stara wersja Qt Widgets 0.3.2/0.31.2.

`/usr/bin/tlumacz` uruchamia stare `tlumacz.qt_gui.app`.

Jednak ta hipoteza została wykluczona dla aktualnie obserwowanego okna.

Użytkownik uruchomił aplikację bezpośrednio poleceniem:
```bash
cd /home/frs/Projekty/tlumacz-v4
PYTHONPATH=src python3 -m tlumacz.qml_gui.app
```

Zaobserwowany proces:
```text
PID 1154285
python3 -m tlumacz.qml_gui.app
```

Drzewo procesu:
```text
yakuake
└── bash
    └── python3 -m tlumacz.qml_gui.app
```

Wniosek: **aktualnie obserwowane okno pochodzi z uruchomionego modułu V4 `tlumacz.qml_gui.app`, a nie ze starego `/usr/bin/tlumacz`.**

## 5. Co pozostaje niewyjaśnione

Skoro:
1. źródłowy QML zawiera poprawkę,
2. testy potwierdzają poprawną strukturę,
3. brak dowodu na cache,
4. aktualny proces uruchamia `tlumacz.qml_gui.app),

to trzeba ustalić, **jaki dokładnie artefakt/plik jest faktycznie ładowany przez ten konkretny proces i jaka ścieżka QML prowadzi do widocznego widoku**.

Do sprawdzenia pozostaje m.in.:
- rzeczywista ścieżka `tlumacz.__file__`,
- rzeczywista ścieżka `tlumacz.qml_gui.app.__file__`,
- `Main.qml` ładowany przez proces,
- sposób ładowania `TranslationPage.qml` przez `Main.qml`/Loader/StackLayout,
- warunki widoczności strony Apertium,
- faktyczny `backendType` w runtime,
- czy widoczny ekran jest rzeczywiście `TranslationPage.qml`.

## 6. Ważna zasada dalszej diagnostyki

Nie należy dalej zmieniać `TranslationPage.qml` w ciemno.

Najpierw trzeba jednoznacznie powiązać:
```text
widoczne okno
    ↓
aktywny proces
    ↓
moduł Python
    ↓
Main.qml
    ↓
TranslationPage.qml
```

Dopiero po uzyskaniu tego dowodu można wykonywać kolejne zmiany.

## 7. Zakres tej notatki

To jest dokument tymczasowy diagnostyki. Nie zastępuje:
- `docs/STATUS.md`,
- `docs/technical-docs/QML_GUI_LAYOUT.md`,
- `CHANGELOG.md`,
- raportów audytowych.

Po zakończeniu diagnostyki należy zdecydować, czy informacje z tej notatki powinny zostać przeniesione do właściwej dokumentacji, a sam plik tymczasowy usunięty.


## 7. Późniejsze ustalenia — przełączanie backendu `llama → Apertium`

W dalszej diagnostyce ustalono następujący stan implementacji:

- `ApiPage.qml` posiada globalny `ComboBox` wyboru backendu.
- Zmiana wyboru wywołuje `bridge.setBackendType(currentText)`.
- `bridge.backendType` jest właściwością QML typu `str` z sygnałem `stateChanged`.
- `set_backend_type()` poprawnie mapuje Apertium na wartość wewnętrzną `apertium`.
- Po zmianie `_backend_type` wykonywane jest `_notify()`, które emituje `stateChanged`.
- `TranslationPage.qml` używa warunku `bridge.backendType === "apertium"` do pokazania sekcji języków Apertium.
- `backendLabel` w `ApiPage.qml` jest wyliczany na podstawie `bridge.backendType` i dla `apertium` zwraca etykietę Apertium.

### Zapis konfiguracji

`set_backend_type()` zmienia backend w pamięci, ale nie wywołuje `save_settings()`. Zapis do `settings-v4.json` następuje dopiero w `save_settings()`, gdzie wykonywane jest `self.settings.backend_type = self._backend_type`.

Aktywne ustawienia na dysku w czasie diagnostyki wskazywały:
```json
"backend_type": "llama"
```

Nie jest to jednak wystarczające wyjaśnienie braku natychmiastowej zmiany widoku, ponieważ `set_backend_type()` zmienia stan runtime i emituje `stateChanged` bez konieczności wcześniejszego zapisu do pliku.

### Wniosek diagnostyczny

Kod odpowiedzialny za samą zmianę backendu oraz warunek QML wygląda na logicznie spójny. Nadal potrzebny jest test reprodukujący rzeczywiste przełączenie `llama → apertium`, który sprawdzi jednocześnie:

1. zmianę `backendType` w bridge,
2. emisję `stateChanged`,
3. reakcję warunku widoczności w QML.

Na tym etapie nie należy wprowadzać poprawki implementacyjnej wyłącznie na podstawie faktu, że `settings-v4.json` pozostaje przy wartości `llama`.

## 8. Zakres tej notatki

To jest dokument tymczasowy diagnostyki. Nie zastępuje:
- `docs/STATUS.md`,
- `docs/technical-docs/QML_GUI_LAYOUT.md`,
- `CHANGELOG.md`,
- raportów audytowych.

Po zakończeniu diagnostyki należy zdecydować, czy informacje z tej notatki powinny zostać przeniesione do właściwej dokumentacji, a sam plik tymczasowy usunięty.


## 9. Rozwiązanie zastosowane 2026-10-05

Diagnostyka wykazała, że sam mechanizm reaktywności QML działa prawidłowo: zmiana `bridge.backendType` na `apertium` powoduje natychmiastową zmianę właściwości zależnych od tego stanu.

Naprawiono rzeczywistą lukę w przepływie konfiguracji:

- metoda niskiego poziomu `set_backend_type()` pozostaje zmianą stanu runtime i nie zapisuje globalnej konfiguracji;
- adapter QML `setBackendType()`, który jest wywoływany przez `ApiPage.qml`, po zmianie backendu zapisuje `settings.backend_type` do aktywnego pliku konfiguracji;
- dzięki temu wybór Apertium wykonany z GUI jest trwały i nie wraca przy kolejnym uruchomieniu do poprzedniego backendu;
- dodano test runtime potwierdzający aktualizację widoczności QML po przełączeniu backendu;
- dodano test potwierdzający natychmiastowy zapis wyboru backendu przez ścieżkę QML.

Weryfikacja:
- testy regresyjne dotyczące przełączania backendu: **4 passed**;
- pełna suita: **278 passed, 1 istniejący problem środowiska testowego** — test `test_qml_bridge_exposes_translation_state_and_actions` odczytuje domyślną konfigurację z bieżącego środowiska SentinelX, gdzie backend jest ustawiony na `custom`, podczas gdy test oczekuje `llama`;
- `compileall`: PASS;
- `qmllint` dla głównych plików QML: PASS.
