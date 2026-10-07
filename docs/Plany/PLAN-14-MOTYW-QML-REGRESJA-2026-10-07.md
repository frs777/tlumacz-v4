# PLAN-14 — bezpieczna remediacja regresji motywu QML/Qt — 2026-10-07

> **Dla wykonawcy:** realizować etapami. Nie wprowadzać kolejnego workaroundu motywu przed wykonaniem charakterystyki obecnego runtime. Każdy etap kodowy musi przejść TDD: RED → GREEN → REFACTOR. Po każdym większym etapie wykonać backup i aktualizować dokumentację.

**Cel:** usunąć rzeczywistą regresję przełączania motywu GUI bez naruszenia istniejącego kontraktu QML, ustawień, ikon, stylu Fusion i pozostałych funkcji aplikacji.

**Architektura:** Najpierw ustalić, gdzie ginie zmiana motywu: KDE/platforma → QGuiApplication/QPalette → Fusion/Qt Quick Controls → QML. Dopiero po wskazaniu konkretnej warstwy zmienić minimalny element. Preferowany jest natywny mechanizm Qt i rzeczywista paleta platformy; ręczna paleta może być użyta wyłącznie jako udowodniony fallback, jeśli natywny mechanizm nie zapewnia wymaganego kontraktu w środowisku projektu.

**Technologie:** Python 3, PySide6/Qt 6, Qt Quick/QML, Fusion, pytest, qmllint, SentinelX.

**Zakres:** `src/tlumacz/qml_gui/app.py`, `Main.qml`, `bridge.py`, istniejące testy QML oraz `docs/technical-docs/QML_GUI_DESIGN.md`, `docs/BUG.md`, `docs/STATUS.md`, `docs/TODO.md`, `docs/CHANGELOG.md`.

## Twarde zasady bezpieczeństwa

- Nie zmieniać backendów, konfiguracji tłumaczenia, bridge poza kontraktem motywu ani lifecycle rdzenia.
- Nie wymuszać Material/Basic ani innego stylu tylko po to, aby uzyskać ciemny/jasny wygląd.
- Nie usuwać istniejących testów.
- Nie zmieniać zachowania `Systemowy`, dopóki pomiar nie wykaże, że obecna implementacja je psuje.
- Nie przywracać ręcznej palety „na ślepo”.
- Nie traktować offscreen/Xvfb jako dowodu zachowania platformowego na KDE.
- Każda zmiana kodu musi mieć regresję pisaną przed implementacją.
- Przed dużą zmianą kodu wykonać pełny backup.
- Po zmianie kodu uzupełnić dokumentację i odświeżyć indeks dokumentacji.
- Przy współbieżnej pracy innych agentów ponownie sprawdzić aktualny stan plików przed każdym zapisem.

## Stan wyjściowy i znane ryzyko

Bieżący launcher tworzy `QGuiApplication`, następnie `QmlApplicationBridge`, wykonuje `setColorScheme()/unsetColorScheme()`, a dopiero później tworzy `QQmlApplicationEngine`. `Main.qml` korzysta z `palette.window` bez lokalnego definiowania pełnej palety.

Dokumentacja jest niespójna: `QML_GUI_DESIGN.md` opisuje `QStyleHints` jako mechanizm aktualny, ale `BUG.md` zawiera historyczny opis ręcznej palety jako naprawy. Najpierw ustalić stan runtime, potem uporządkować dokumentację.

## Kryterium akceptacji

Dla `system`, `dark`, `light`:
- aplikacja pokazuje właściwy schemat kolorów;
- standardowe kontrolki Qt Quick Controls i powierzchnie QML korzystają z właściwej palety;
- zmiana motywu nie zmienia wyłącznie ikony;
- persystencja ustawienia działa po restarcie;
- brak błędów QML i crashy Qt.

---

## Etap 1 — inwentaryzacja i baseline bez zmian kodu

**Pliki:** tylko odczyt.

- [ ] Zebrać aktualny diff roboczy i listę procesów/agentów pracujących nad repozytorium.
- [ ] Potwierdzić aktualność `app.py`, `Main.qml` i `bridge.py`.
- [ ] Przejrzeć istniejące testy motywu i rozdzielić testy kodowe od rzeczywistego runtime QML.
- [ ] Zidentyfikować wszystkie użycia `theme`, `palette`, `QStyleHints`, `setColorScheme`, `Fusion` i ikon motywu.
- [ ] Zanotować świeży baseline testów.

**Gate:** jeśli pliki zmienią się podczas inwentaryzacji, powtórzyć etap na aktualnym stanie.

## Etap 2 — charakterystyka rzeczywistego Qt/KDE

Przygotować jednorazowy test diagnostyczny uruchamiany w rzeczywistej sesji użytkownika; nie dodawać go do produkcji.

Rejestrować dla `system`, `dark`, `light`:
- `QGuiApplication.platformName()`;
- nazwę stylu;
- `styleHints().colorScheme()`;
- `Window`, `Base`, `Text`, `Button`, `ButtonText`, `Highlight`, `HighlightedText`;
- moment utworzenia `QQmlApplicationEngine`;
- `paletteChanged`;
- paletę faktycznie widzianą przez kontrolkę Fusion.

Jeżeli sesja pozwala, wykonać pomiar przed i po rzeczywistej zmianie schematu KDE.

**Gate decyzyjny:**
- **A:** QGuiApplication ma nową paletę, ale QML/Fusion jej nie używa → naprawić warstwę QML/Fusion.
- **B:** `setColorScheme()` nie zmienia palety → nie udawać, że mechanizm działa; zbadać platformę i przygotować minimalny fallback.
- **C:** `system` działa, a `dark/light` nie → rozdzielić kontrakt systemowy od jawnego wymuszania.
- **D:** proces nie działa w sesji KDE → nie wyciągać wniosku o GUI z takiego testu.

## Etap 3 — RED: test regresyjny przed zmianą

Dodać do istniejącego zestawu testów QML GUI minimalne testy:
- `test_theme_system_uses_platform_palette`;
- `test_theme_dark_changes_actual_application_palette`;
- `test_theme_light_changes_actual_application_palette`;
- `test_theme_change_does_not_only_change_icon` — tylko jeżeli objaw jest reprodukowalny.

Testować wynik widoczny dla aplikacji/QML, a nie samo wywołanie `setColorScheme()`.

Uruchomić nowe testy przed zmianą produkcyjną i potwierdzić RED.

**Gate:** test przechodzący przed poprawką nie jest regresją i musi zostać poprawiony.

## Etap 4 — backup przed zmianą kodu

Wykonać backup:
- `src/tlumacz/qml_gui/`;
- odpowiadających testów;
- `docs/technical-docs/QML_GUI_DESIGN.md`;
- `docs/BUG.md`;
- `docs/STATUS.md`;
- `docs/TODO.md`;
- `docs/CHANGELOG.md`.

Proponowana lokalizacja: `backups/20261007-theme-regression-pre-fix/`.

Zapisać SHA-256 archiwum i zakres backupu w dokumentacji.

## Etap 5 — GREEN: minimalna naprawa

Implementować wyłącznie wariant wynikający z Etapu 2.

### Preferencja 1 — natywny Qt
Jeżeli runtime potwierdzi skuteczność mechanizmu:
- zachować `system = unsetColorScheme()`;
- zachować ustawianie schematu przed `QQmlApplicationEngine`;
- nie dodawać lokalnej pełnej palety;
- zapewnić dziedziczenie palety przez QML.

### Preferencja 2 — minimalny fallback
Jeżeli środowisko Qt/KDE nie dostarcza wymaganej jawnej palety przez `QStyleHints`:
- nie zmieniać `Systemowy`;
- wydzielić fallback wyłącznie dla `dark/light`;
- stosować kompletną paletę wymaganą przez Fusion, nie pojedyncze role;
- nie mieszać fallbacku z paletą systemową;
- nie zmieniać innych właściwości QML.

Każdy wariant musi przejść nowe regresje.

## Etap 6 — REFACTOR i pełna walidacja

- [ ] usunąć wyłącznie zbędny kod diagnostyczny;
- [ ] nie wykonywać niezwiązanych refaktorów;
- [ ] uruchomić testy QML GUI;
- [ ] `python3 -m compileall -q src tests`;
- [ ] `qmllint src/tlumacz/qml_gui/*.qml`;
- [ ] pełny `pytest`;
- [ ] sprawdzić nowe warningi i crashy.

## Etap 7 — rzeczywisty gate GUI w sesji KDE

Sprawdzić:
1. `system`;
2. `dark`;
3. `light`;
4. powrót do `system`;
5. restart i odtworzenie zapisanego wyboru;
6. zmianę systemowego motywu KDE przy `system`, jeśli można ją wykonać bez zakłócania pracy użytkownika.

Zweryfikować co najmniej TabBar, TabButton, ComboBox, pola tekstowe, tło okna i powierzchnie Pomocy.

**Gate:** runtime KDE jest rozstrzygający dla zachowania platformowego; offscreen/Xvfb jest tylko testem pomocniczym.

## Etap 8 — dokumentacja

Po zaakceptowanej zmianie:
- [ ] uporządkować `docs/technical-docs/QML_GUI_DESIGN.md`;
- [ ] zamknąć/otworzyć właściwy BUG na podstawie dowodów;
- [ ] zaktualizować `docs/STATUS.md`;
- [ ] zaktualizować `docs/TODO.md`, jeśli pozostaje ograniczenie platformowe;
- [ ] dopisać `docs/CHANGELOG.md`;
- [ ] zaktualizować `docs/DOCUMENTATION_CHANGELOG.md`;
- [ ] odświeżyć `docs/INDEX.md` i `docs/INDEX.yml`.

Nie pozostawić dwóch sprzecznych opisów bieżącego mechanizmu motywu.

## Etap 9 — finalny rollback gate

Przed zamknięciem:
- [ ] sprawdzić pełny diff;
- [ ] potwierdzić ograniczenie zmian do motywu/testów/docs;
- [ ] wykonać świeży pełny suite;
- [ ] wykonać świeży `qmllint` i `compileall`;
- [ ] zweryfikować backup i możliwość odtworzenia;
- [ ] porównać wynik z baseline.

Jeżeli runtime nadal nie potwierdza poprawnego motywu, **nie zamykać defektu**.

### Warunek rollbacku

Jeżeli poprawka naruszy dowolną istniejącą funkcję GUI, testy, konfigurację lub lifecycle:
1. zatrzymać dalsze zmiany;
2. przywrócić ostatni bezpieczny backup;
3. uruchomić baseline;
4. opisać przyczynę odrzucenia wariantu;
5. dopiero potem przygotować kolejny wariant.

## Oczekiwany rezultat

Jeden spójny kontrakt:
- `Systemowy` → rzeczywista paleta/schemat platformy;
- `Ciemny` → faktycznie ciemny Fusion/QML;
- `Jasny` → faktycznie jasny Fusion/QML;

bez regresji pozostałego GUI i bez pozostawienia historycznych opisów jako bieżącej implementacji.

**Status:** W TRAKCIE — etapy 1–6 wykonane; etap 7 (rzeczywisty gate KDE) pozostaje otwarty.


## Dziennik wykonania — 2026-10-07

- Etap 1: baseline ukierunkowany QML GUI: 12 passed przed zmianą; potwierdzono aktualny launcher, bridge i QML.
- Etap 2: ustalono aktywną sesję KDE przez loginctl (sesja 3, KDE, X11, DISPLAY=:0). Bezpośredni pomiar Qt w tej sesji jest blokowany przez brak dostępu SentinelX do Xauthority/DBus użytkownika 1000. Pomiar izolowany Qt potwierdził, że setColorScheme() może pozostać bez wpływu na paletę.
- Etap 3: dodano regresję rzeczywistej palety. RED potwierdzony dla dark: paleta pozostała #efefef.
- Etap 4: wykonano backup pre-fix. SHA-256 archiwum: a1193162b417d8567dcd15eb3edebcc9e93ef9ce026f23a950744d8c50f16c3b.
- Etap 5: wdrożono minimalny fallback pełnej palety Fusion tylko dla dark/light. Systemowy resetuje paletę do natywnej.
- Etap 6: testy motywu 4 passed; tests/test_qml_gui.py 157 passed; pełny suite 573 passed; compileall PASS; qmllint PASS.
- Wykryto i usunięto niezależną niespójność starego testu czasu względem aktualnego TranslationPage.qml; test punktowy po synchronizacji: 1 passed, a następnie pełny suite 573 passed.
- Etap 7: NIEZAMKNIĘTY. Brak potwierdzenia wizualnego i pomiaru palety w rzeczywistej sesji KDE.
- Etap 8: dokumentacja zaktualizowana.
- Etap 9: częściowo wykonany — pełny suite, compileall, qmllint i backup zweryfikowane; pozostaje gate KDE.



## Aktualizacja 2026-10-07 — decyzja produktowa po restarcie GUI

Po ponownym uruchomieniu aplikacji użytkownik zdecydował, że bieżące GUI ma korzystać wyłącznie z motywu systemowego. Selektor `Systemowy/Jasny/Ciemny` został wycofany z interfejsu, ale mechanizm techniczny zmiany motywu pozostaje zachowany do przyszłego przywrócenia.

Etap runtime KDE nadal nie jest uznany za rozwiązany. Plan nie deklaruje naprawy defektu przełączania `dark/light`; zmiana jest świadomym ograniczeniem powierzchni GUI do stabilnego motywu systemowego.
