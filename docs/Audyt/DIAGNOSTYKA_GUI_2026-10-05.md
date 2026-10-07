---
id: diagnostyka-gui-2026-10-05
status: evidence
meta:
  contentType: Diagnostic Report
  category: audit
version: 1.0.0
updated: 2026-10-05
owner: gui-maintenance
source: src/tlumacz/qml_gui/, tests/
depends_on: [docs/technical-docs/QML_GUI_LAYOUT.md, docs/technical-docs/QML_GUI_TRANSLATION_CARD_SPEC.md, docs/STATUS.md]
expires_when: kolejna pełna diagnostyka runtime GUI
last_validation: "raport przeniesiony do docs i sklasyfikowany SentinelX 2026-10-05"
---

# Głęboki research przyczyn problemu GUI V4 — raport przyczynowy i plan naprawy

**Data:** 2026-10-05  
**Projekt:** Tłumacz V4  
**Zakres:** przyczyny rozbieżności pomiędzy deklarowanym układem GUI a układem faktycznie widocznym w runtime  
**Raport wykonany przed naprawą kodu**

## 1. Cel badania

Celem było ustalenie rzeczywistej przyczyny sytuacji, w której użytkownik widzi w GUI układ inny niż oczekiwany, mimo że źródłowy QML był wcześniej uznany za poprawiony.

Zgodnie z poleceniem użytkownika z dalszego badania wyłączono jako przyczyny hipotezy wymienione w:

`TEMP_DIAGNOSTYKA_GUI_2026-10-04.md`

W szczególności nie traktowano jako głównej przyczyny:
- cache QML,
- starego launchera/systemowego `tlumacz`,
- samego systemowego GUI V3.

Nie użyto tych hipotez jako wyjaśnienia badanego objawu.

## 2. Źródła i metody

Badanie obejmowało cztery niezależne warstwy:

1. **Kod źródłowy V4**
   - `src/tlumacz/qml_gui/app.py`
   - `src/tlumacz/qml_gui/Main.qml`
   - `src/tlumacz/qml_gui/TranslationPage.qml`
   - `tests/test_qml_gui.py`
   - `pyproject.toml`

2. **Rzeczywisty runtime**
   - `importlib.util.find_spec()`
   - `tlumacz.__file__`
   - `tlumacz.qml_gui.app.__file__`
   - rzeczywisty `QML_FILE`
   - `QQmlApplicationEngine.importPathList()`
   - drzewo obiektów QML po załadowaniu `Main.qml`
   - pozycje, rozmiary i widoczność elementów GUI po ustawieniu backendu Apertium.

3. **Historia/artefakty projektu**
   - kopie `TranslationPage.qml` w backupach,
   - znaczniki czasu,
   - stan repozytorium,
   - zgodność treści dokumentacji z bieżącym plikiem.

4. **Research zewnętrzny**
   - oficjalna dokumentacja Python 3.14 dotycząca import systemu i `site`,
   - oficjalna dokumentacja pytest dotycząca `src` layout, `pythonpath` i `import-mode`,
   - oficjalna dokumentacja Qt dotycząca `GridLayout`, `RowLayout` i rozwiązywania importów QML,
   - niezależne wyszukiwanie Exa, Parallel Search, Keenable i Tavily.

## 3. Najważniejsze ustalenie

### Przyczyna nie znajduje się w cache ani w tym, że QML ładuje niewłaściwy plik.

Runtime został bezpośrednio sprawdzony.

Przy uruchomieniu:

```
QT_QPA_PLATFORM=offscreen
PYTHONPATH=/home/frs/Projekty/tlumacz-v4/src
python3 ...
```

Python zaimportował:

```
/home/frs/Projekty/tlumacz-v4/src/tlumacz/__init__.py
/home/frs/Projekty/tlumacz-v4/src/tlumacz/qml_gui/app.py
```

Aplikacja wskazała:

```
/home/frs/Projekty/tlumacz-v4/src/tlumacz/qml_gui/Main.qml
```

Po załadowaniu `Main.qml` drzewo obiektów QML zawierało rzeczywisty komponent:

```
TranslationPage_QMLTYPE_50
```

a wewnątrz niego:
- `progressSection`,
- `statisticsSection`,
- `translationControlsSection`,
- `translateButton`,
- `cancelButton`,
- dwa `QQuickColumnLayout` dla pól Apertium,
- dwa pola `TextField` Apertium,
- Log,
- Podgląd.

To jest bezpośredni dowód, że aktualny plik QML jest ładowany do runtime.

## 4. Rozstrzygający dowód w kodzie

Aktualny `TranslationPage.qml` zawiera dla Apertium:

```qml
RowLayout {
    ...

    Button {
        objectName: "translateButton"
    }

    Button {
        objectName: "cancelButton"
    }

    Item { Layout.fillWidth: true }

    ColumnLayout {
        visible: bridge.backendType === "apertium"
        ...
    }

    ColumnLayout {
        visible: bridge.backendType === "apertium"
        ...
    }

    ...
}
```

Czyli pola Apertium są nadal **wewnątrz tego samego `RowLayout`, co przyciski sterowania**.

Nie jest to `GridLayout` z dwiema kolumnami.

W bieżącym pliku występuje `GridLayout` tylko dla sekcji plików:

```qml
GridLayout {
    columns: 3
    ...
}
```

Nie występuje natomiast osobny `GridLayout` dla pól:
- „Język źródłowy”,
- „Język docelowy”.

## 5. Dlaczego wcześniejsza diagnostyka mogła dać fałszywe poczucie poprawności

W pliku tymczasowym zapisano, że:
- blok Apertium został przeniesiony poza `RowLayout` przycisków,
- zastosowano `GridLayout` z dwiema kolumnami,
- testy regresyjne to potwierdzają.

Bieżący kod nie odpowiada temu opisowi.

Jeszcze ważniejsze: test regresyjny nie sprawdza tego, co deklaruje dokumentacja.

Aktualny test:

```
def test_qml_apertium_translation_controls_use_two_columns_with_labels_above():
    ...
    assert "RowLayout {" in apertium
    assert apertium.count('visible: bridge.backendType === "apertium"') == 2
    assert apertium.count("ColumnLayout {") == 2
    assert apertium.count("Layout.preferredWidth: 120") == 2
```

Ten test potwierdza jedynie obecność dwóch `ColumnLayout` w analizowanym fragmencie.

Nie sprawdza:
- czy te kolumny są dziećmi właściwego kontenera,
- czy kontenerem jest `GridLayout`,
- czy kolumny są poza `RowLayout` przycisków,
- czy etykiety i pola tworzą dwa niezależne pionowe bloki,
- czy ich pozycje są rzeczywiście sąsiadującymi kolumnami,
- czy przyciski i języki są od siebie strukturalnie oddzielone.

Test jest więc **syntaktycznie zgodny z błędną implementacją**.

## 6. Potwierdzenie runtime geometrii

Po załadowaniu aktualnego QML i ustawieniu:

```
backendType = "apertium"
width = 1120
height = 780
```

runtime zwrócił m.in.:

| Element | X | Y | W | H |
|---|---:|---:|---:|---:|
| `translationControlsSection` | 0 | 176 | 1088 | 58 |
| `translateButton` | 0 | 13 | 110 | 32 |
| `cancelButton` | 118 | 17 | 110 | 25 |
| kolumna Apertium 1 | 840 | 0 | 120 | 58 |
| kolumna Apertium 2 | 968 | 0 | 120 | 58 |
| separator | 0 | 240 | 1088 | 1 |

To dokładnie odpowiada obecnej strukturze:

```
RowLayout
 ├── Translate
 ├── Cancel
 ├── spacer
 ├── Apertium source
 └── Apertium target
```

Nie odpowiada natomiast oczekiwanemu układowi:

```
Sterowanie
 ├── Translate
 └── Cancel

Apertium
 ┌──────────────┬──────────────┐
 │ źródłowy     │ docelowy     │
 │ TextField    │ TextField    │
 └──────────────┴──────────────┘
```

## 7. Mechanizm Qt, który potwierdza problem

Oficjalna dokumentacja Qt opisuje `RowLayout` jako układ będący odpowiednikiem `GridLayout` ograniczonym do jednego wiersza.

`GridLayout` jest przeznaczony do dynamicznego rozmieszczania elementów w siatce z właściwościami `rows`, `columns`, `rowSpacing` i `columnSpacing`.

Wniosek:

Jeżeli dwa `ColumnLayout` są dziećmi `RowLayout`, to Qt prawidłowo umieści je jako kolejne elementy tego jednego wiersza. To nie jest błąd Qt. To jest dokładnie zachowanie zadeklarowane przez bieżący QML.

## 8. Drugi niezależny problem — rozjazd runtime Python

Badanie wykazało również realny problem środowiskowy, ale jest on **odrębny od przyczyny obecnego układu QML**.

Bez:

```
PYTHONPATH=/home/frs/Projekty/tlumacz-v4/src
```

interpreter importuje:

```
/usr/lib/python3.14/site-packages/tlumacz/__init__.py
```

i nie znajduje:

```
tlumacz.qml_gui
```

Natomiast z `PYTHONPATH=src` importuje poprawnie V4.

Jest to zgodne z oficjalną dokumentacją pytest/Python: projekt z `src/` nie jest automatycznie importowalny jako lokalny pakiet podczas zwykłego `python3`; `pytest` może mieć własne ustawienie `pythonpath`, ale nie przenosi tego ustawienia do zwykłego uruchomienia aplikacji.

W projekcie `pyproject.toml` już istnieje:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
```

To wyjaśnia, dlaczego testy mogą widzieć lokalny kod, podczas gdy zwykły interpreter bez `PYTHONPATH` może widzieć instalację systemową.

Nie jest to jednak dowód, że aktualny QML runtime ładował stary `TranslationPage.qml`. Bezpośredni test z `PYTHONPATH=src` i drzewem QML wykazał ładowanie bieżącego pliku.

## 9. Dodatkowe odkrycie: stara editable instalacja

W użytkownikowym site-packages istnieje:

```
/home/frs/.local/lib/python3.14/site-packages/__editable__.tlumacz-0.30.0.pth
```

z finderem wskazującym na:

```
/home/frs/Projekty/agent-translator-v3/tlumacz
```

Jest to realny dodatkowy konflikt środowiskowy.

Nie jest to obecnie podstawą naprawy GUI, ponieważ:
- nie zmieniamy tego pliku bez zgody użytkownika,
- bez `PYTHONPATH=src` systemowy `tlumacz` jest wybierany,
- z `PYTHONPATH=src` V4 jest wybierany jednoznacznie,
- QML runtime w kontrolowanym teście załadował bieżący `TranslationPage.qml`.

Ten artefakt należy jednak traktować jako **P1 problem środowiska uruchomieniowego**, który może w przyszłości powodować ponowne rozjazdy wersji.

## 10. Historia backupów

W projekcie znajduje się wiele backupów wcześniejszych wersji `TranslationPage.qml`.

Ich analiza pokazuje, że wcześniejsze wersje rzeczywiście zawierały inne układy, m.in.:
- `translationControlsSection` jako pojedynczy `RowLayout`,
- osobne sekcje sterowania/postępu/statystyk,
- wcześniejsze warianty z separatorami.

Bieżący plik nie jest jednak przypadkową starą kopią z backupu: runtime wskazuje bezpośrednio na:

```
/home/frs/Projekty/tlumacz-v4/src/tlumacz/qml_gui/TranslationPage.qml
```

## 11. Klasyfikacja hipotez

| Hipoteza | Wynik | Dowód |
|---|---|---|
| Cache QML | WYŁĄCZONA | zgodnie z zakresem wykluczonym w notatce; dodatkowo runtime ładuje aktualną strukturę |
| Stary launcher V3 | WYŁĄCZONA dla badanego procesu | kontrolowany runtime używa V4 `qml_gui.app` |
| Qt ładuje inną kopię `TranslationPage.qml` | ODRZUCONA | znaleziono tylko jeden aktywny plik i runtime odtwarza jego strukturę |
| QML import path wskazuje zły moduł | ODRZUCONA dla tego widoku | `TranslationPage` został załadowany jako aktualny komponent |
| QML reaktywność backendu | ODRZUCONA | `backendType = apertium` powoduje widoczność pól |
| Błąd Qt Layout | ODRZUCONA | geometria odpowiada dokładnie bieżącemu `RowLayout` |
| **Błędna struktura bieżącego QML** | **POTWIERDZONA** | pola Apertium są dziećmi `RowLayout` przycisków |
| **Test regresyjny ma zbyt słaby kontrakt** | **POTWIERDZONA** | test akceptuje dwa `ColumnLayout` wewnątrz błędnego `RowLayout` |
| Systemowy/globalny import Pythona | **POTWIERDZONY jako problem środowiska** | bez `PYTHONPATH=src` importuje `/usr/lib/.../tlumacz` |
| Stary editable finder 0.30.0 | **POTWIERDZONY jako dodatkowe ryzyko** | `.pth` wskazuje na V3 |

## 12. Root cause

### Root cause bezpośredni

**Bieżący `TranslationPage.qml` nie implementuje struktury GUI opisanej w dokumentacji diagnostycznej.**

Zamiast oddzielić Apertium od wiersza sterowania, kod nadal umieszcza oba pola Apertium wewnątrz:

```
translationControlsSection
  └── RowLayout
```

### Root cause testowy

**Test regresyjny został napisany przeciwko zbyt słabemu kontraktowi tekstowemu.**

Test sprawdza liczbę elementów, ale nie sprawdza ich relacji strukturalnej.

W efekcie:
- test przechodzi,
- QML jest formalnie poprawny,
- runtime działa,
- ale układ GUI jest funkcjonalnie niezgodny z wymaganiem.

### Root cause procesu

**Brak testu runtime geometrii/struktury komponentu na granicy QML Layout.**

Test źródłowy nie był wystarczająco silny, aby wykryć, że dwa `ColumnLayout` znalazły się w złym rodzicu.

## 13. Naprawa wynikająca z badania

Naprawa powinna zrobić dokładnie trzy rzeczy:

1. Wydzielić blok Apertium z `RowLayout` przycisków.
2. Zbudować dla niego rzeczywisty `GridLayout` z dwiema kolumnami.
3. Zastąpić test oparty tylko na liczbie `ColumnLayout` testem strukturalnym, który nie dopuści do ponownego zagnieżdżenia bloku Apertium w `RowLayout` sterowania.

Dodatkowo należy zachować test runtime potwierdzający:
- `backendType == "apertium"`,
- widoczność dwóch pól,
- brak zwykłego wyboru języka,
- geometryczne rozmieszczenie pól jako dwóch kolumn.

## 14. Zalecenia środowiskowe — poza bieżącą naprawą

Nie wykonano i nie należy wykonywać bez osobnej zgody:
- instalacji pakietów,
- usuwania pakietów,
- modyfikacji globalnego `site-packages`,
- usuwania starego editable install,
- zmian w konfiguracji systemowego launchera.

Dla V4 bezpieczny launcher powinien jednoznacznie ustawiać:

```
PYTHONPATH=/home/frs/Projekty/tlumacz-v4/src
```

i uruchamiać:

```
python3 -m tlumacz.qml_gui.app
```

Projekt posiada już `uruchom-v4.sh`, który realizuje ten kontrakt.

## 15. Źródła zewnętrzne

### Python / pytest

- Python — Import System:  
  https://docs.python.org/3/reference/import.html
- Python — `site` i pliki `.pth`:  
  https://docs.python.org/3/library/site.html
- pytest — Good Integration Practices:  
  https://docs.pytest.org/en/latest/goodpractices.html
- pytest — `sys.path` / `PYTHONPATH` / import modes:  
  https://docs.pytest.org/en/stable/explanation/pythonpath.html

Kluczowy wniosek ze źródeł: `src` layout wymaga jawnego udostępnienia `src` interpreterowi albo editable install; konfiguracja pytest `pythonpath` dotyczy sesji pytest, nie zwykłego `python3`.

### Qt

- GridLayout QML Type:  
  https://doc.qt.io/qt-6/qml-qtquick-layouts-gridlayout.html
- RowLayout QML Type:  
  https://doc.qt.io/qt-6/qml-qtquick-layouts-rowlayout.html
- Qt Quick Layouts Overview:  
  https://doc.qt.io/qt-6/qtquicklayouts-overview.html
- QML Import Statements:  
  https://doc.qt.io/qt-6/qtqml-syntax-imports.html

Kluczowy wniosek: `RowLayout` jest układem jednorzędowym, natomiast `GridLayout` służy do rozmieszczania elementów w siatce. Bieżąca geometria GUI jest więc naturalnym skutkiem obecnej struktury QML.

## 16. Werdykt

**Przyczyna GUI została ustalona.**

Nie jest nią:
- cache,
- stary launcher,
- niewłaściwa kopia QML,
- brak reaktywności QML,
- błąd Qt.

Jest nią:

> **błędna struktura bieżącego `TranslationPage.qml` oraz zbyt słaby test regresyjny, który tę błędną strukturę przepuszczał.**

Dodatkowo istnieje niezależny problem środowiska Python z systemowym pakietem i starym editable finderem V3. Jest on realny i powinien zostać zabezpieczony przez jednoznaczny launcher/runtime identity, ale nie jest bezpośrednią przyczyną obecnej geometrii Apertium.

---

**Status przed naprawą:** ROOT CAUSE CONFIRMED / FIX PENDING


# 17. Wykonana naprawa — 2026-10-05

Po zapisaniu części badawczej wykonano naprawę zgodnie z ustalonym root cause.

### Zmiana implementacyjna

W src/tlumacz/qml_gui/TranslationPage.qml:
- usunięto pola Apertium z RowLayout sekcji translationControlsSection;
- dodano osobny apertiumLanguageSection;
- dodano GridLayout z columns: 2;
- pozostawiono dwa pionowe bloki ColumnLayout z etykietą nad polem;
- zwykły target language ComboBox pozostaje widoczny wyłącznie dla backendów innych niż Apertium.

### Zmiana testu

W tests/test_qml_gui.py test struktury Apertium został zaostrzony. Teraz sprawdza:
- istnienie osobnej apertiumLanguageSection;
- brak pól Apertium w translationControlsSection;
- obecność GridLayout i columns: 2;
- dokładnie dwa ColumnLayout w sekcji Apertium;
- oba pola językowe i ich wartości;
- nieedytowalność pól.

### Backup

Przed zmianą wykonano:

backups/gui-root-cause-20261005/pre-gui-root-cause-fix.tar.gz

SHA-256:

b5c328b8492bc98d1bedcab596e9fd465ab2a11383fb09b451910d58bca181da2

## 18. Weryfikacja po naprawie

Świeże wyniki:

- test regresyjny Apertium: **1 passed, 59 deselected**;
- qmllint Main.qml + TranslationPage.qml: **PASS**;
- runtime QML z QML_DISABLE_DISK_CACHE=1 i PYTHONPATH=src: **PASS**;
- runtime potwierdził, że pola auto i Polski są dziećmi GridLayout i znajdują się w dwóch kolumnach X=0 oraz X=130 przy szerokości 120 px.

Pełna suita nadal ma jeden istniejący problem środowiskowy:

test_qml_bridge_exposes_translation_state_and_actions oczekuje llama, natomiast aktywna konfiguracja środowiska ma apertium. Nie zmieniano konfiguracji użytkownika w celu sztucznego uzyskania zielonego wyniku.

## 19. Status końcowy

**ROOT CAUSE CONFIRMED**

**FIX IMPLEMENTED**

**FOCUSED REGRESSION: PASS**

**QMLLINT: PASS**

**RUNTIME STRUCTURE: PASS**

**FULL SUITE: 1 KNOWN ENVIRONMENT FAILURE**


# 20. Korekta karty „Tłumaczenie” zgodnie z aktywną specyfikacją — 2026-10-05

Po ponownym sprawdzeniu źródła prawdy dla karty stwierdzono, że wcześniejsza naprawa dotycząca osobnej sekcji Apertium była niezgodna z `docs/technical-docs/QML_GUI_TRANSLATION_CARD_SPEC.md`. Ta specyfikacja wymaga pojedynczego pola `Język docelowy` w wierszu sterowania i nie definiuje osobnej sekcji Apertium na karcie Tłumaczenie.

Karta została więc poprawiona ponownie zgodnie z aktywnym kontraktem:

- Pliki;
- Sterowanie tłumaczeniem;
- Postęp;
- Statystyki;
- separator;
- Log;
- separator;
- Podgląd tłumaczenia.

Usunięto z `TranslationPage.qml` `apertiumLanguageSection` oraz pola `translation.source_language` i `translation.target_language`. Szczegółowe ustawienia Apertium pozostają w `ApiPage.qml`, zgodnie z istniejącą specyfikacją tej karty.

Backup tej korekty:

`backups/translation-card-20261005/pre-card-fix.tar.gz`

SHA-256: `98b923bd5b3988ccebea778bf37fdcbb095ea9c574edec98e69791aaa0f1a3e6`

## 21. Weryfikacja korekty karty

- test kontraktu kolejności karty: **PASS**;
- test dokładnej kolejności sekcji: **PASS**;
- test sterowania Tłumacz/Anuluj/Język docelowy: **PASS**;
- test braku dodatkowej sekcji Apertium na karcie: **PASS**;
- `qmllint` dla `Main.qml` i `TranslationPage.qml`: **PASS**.
