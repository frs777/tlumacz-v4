# Zakładki „Tłumaczenie” i „Pomoc” — plan implementacji

> **Dla wykonawcy:** implementować etapami test-first; po każdej zmianie uruchomić test skupiony, a przed zakończeniem pełną weryfikację.

**Cel:** Doprowadzić zakładki „Tłumaczenie” i „Pomoc” do funkcjonalnego stanu zgodnego ze specyfikacją, z poprawną kolejnością czterech zakładek i nazwą aplikacji „Tłumacz”.

**Architektura:** QML pozostaje warstwą prezentacji. `QmlApplicationBridge` dostarcza akcje, stan tłumaczenia i treść pomocy z plików Markdown. Karta Pomoc używa własnego `TabBar`/\`StackLayout`, a „O programie” otwiera modalny dialog.

**Tech Stack:** PySide6, Qt Quick/QML, pytest, centralne `tlumacz.i18n`.

**Spec:** `docs/technical-docs/QML_GUI_TRANSLATION_CARD_SPEC.md`

## Globalne ograniczenia

- Nazwa prezentowana użytkownikowi: **Tłumacz**.
- Kolejność zakładek: **Tłumaczenie | API i serwer | Przełączniki | Pomoc**.
- Zakładki „Tłumaczenie” i „Pomoc” muszą być funkcjonalne przed przejściem do pozostałych kart.
- Pomoc ma korzystać z pliku/plików pomocy, a nie z długiego tekstu zaszytego w QML.
- Nie dodawać nowych elementów do karty „Tłumaczenie” poza zaakceptowaną specyfikacją.
- Po zmianach aktualizować dokumentację.
- Backup wykonany przed zmianą: `backups/help-translation-tabs-20261003-0207/pre-help-translation.tar.gz`.

## Review Focus

- Otworzenie „O programie” i dokładna treść dialogu.
- Zmiana języka aplikacji i odświeżenie treści zakładki Pomoc.
- Brak pliku pomocy / niepełna sekcja nie może wywrócić całego GUI.
- Anulowanie tłumaczenia musi pozostać aktywne wyłącznie podczas pracy.
- Postęp, czas, prędkość, log i podgląd muszą nadal korzystać z rzeczywistego stanu bridge.

---

### Zadanie 1: Testy kontraktowe zakładek i Pomocy

**Pliki:**
- Test: `tests/test_qml_gui.py`
- Test: `tests/test_gui_regression_v3_v4.py`

- [ ] Napisać testy RED sprawdzające:
  - tytuł okna `Tłumacz`;
  - kolejność etykiet zakładek;
  - obecność przycisku „O programie” po prawej stronie;
  - dialog z wersją `0.40.0`, opisem i licencją MIT;
  - własny `TabBar` pomocy i źródło treści z pliku;
  - zachowanie kontraktu karty „Tłumaczenie”: separatory, kolejność sekcji i kontrole.
- [ ] Uruchomić testy skupione i potwierdzić RED.

### Zadanie 2: Pliki treści Pomocy i bridge

**Pliki:**
- Utworzyć: `src/tlumacz/qml_gui/help.pl.md`
- Utworzyć: `src/tlumacz/qml_gui/help.en.md`
- Utworzyć: `src/tlumacz/qml_gui/help.de.md`
- Modyfikować: `src/tlumacz/qml_gui/bridge.py`
- Modyfikować: `src/tlumacz/__init__.py` tylko jeśli będzie potrzebne eksportowanie wersji; preferować istniejące `__version__`.

- [ ] Dodać parser sekcji Markdown oparty o nagłówki `##`.
- [ ] Udostępnić w bridge nazwę i treść tematów pomocy jako `QVariantList`.
- [ ] Udostępnić wersję aplikacji przez istniejące `tlumacz.__version__`.
- [ ] Nie wprowadzać zależności zewnętrznych.

### Zadanie 3: Implementacja zakładki Pomoc

**Pliki:**
- Modyfikować: `src/tlumacz/qml_gui/HelpPage.qml`
- Modyfikować: `src/tlumacz/i18n.py` tylko dla etykiet UI/dialogu.

- [ ] Umieścić „O programie” po prawej stronie nagłówka.
- [ ] Dialog ma zawierać:
  - `TŁUMACZ`;
  - `Wersja: 0.40.0`;
  - `Program do tłumaczenia dokumentów z wykorzystaniem AI i graficznego interfejsu Qt.`;
  - `Obsługuje lokalne i chmurowe backendy tłumaczenia, w tym llama.cpp, Apertium i (w przyszłości) inne.`;
  - `Licencja MIT`.
- [ ] Pod nagłówkiem umieścić podręczną pomoc z własnymi zakładkami tematów.
- [ ] Treść tematów pobierać z bridge i aktualnego pliku językowego.
- [ ] Zachować przełączanie języka całej aplikacji.

### Zadanie 4: Implementacja karty „Tłumaczenie” zgodnie ze specyfikacją

**Pliki:**
- Modyfikować: `src/tlumacz/qml_gui/TranslationPage.qml`
- Modyfikować: `src/tlumacz/i18n.py` dla potrzebnych etykiet.

- [ ] Ułożyć kolejność: Pliki → separator → Log → separator → Podgląd tłumaczenia.
- [ ] W sekcji Pliki zachować dokładnie: wejście + Przeglądaj, wyjście + Przeglądaj, Tłumacz + Anuluj + Język docelowy, postęp/procent, Czas + Prędkość tłumaczenia + znaki/s.
- [ ] Przenieść log przed podgląd.
- [ ] Nie dodawać dodatkowej sekcji statusowej poza specyfikacją.
- [ ] Zachować istniejące rzeczywiste bindingi bridge.

### Zadanie 5: Kolejność zakładek i nazewnictwo

**Pliki:**
- Modyfikować: `src/tlumacz/qml_gui/Main.qml`
- Modyfikować: `src/tlumacz/i18n.py`

- [ ] Ustawić tytuł okna na `Tłumacz`.
- [ ] Ustawić kolejność: Tłumaczenie, API i serwer, Przełączniki, Pomoc.
- [ ] Nie implementować jeszcze funkcjonalności kart API/Przełączniki poza zmianą ich etykiet/kolejności.

### Zadanie 6: Dokumentacja i weryfikacja

**Pliki:**
- Modyfikować: `docs/technical-docs/QML_GUI_TRANSLATION_CARD_SPEC.md`
- Modyfikować: `docs/technical-docs/QML_GUI_DESIGN.md`
- Modyfikować: `docs/DOCUMENTATION_CHANGELOG.md`
- Modyfikować: `docs/INDEX.yml`
- Modyfikować: `docs/STATUS.md`
- Modyfikować: `docs/CHANGELOG.md`

- [ ] Opisać źródła treści Pomocy i dialog „O programie”.
- [ ] Opisać aktualną kolejność zakładek.
- [ ] Uruchomić testy skupione.
- [ ] Uruchomić pełny `pytest -q`.
- [ ] Uruchomić `python3 -m compileall -q src`.
- [ ] Uruchomić `ruff check src tests`.
- [ ] Uruchomić `git diff --check`, jeśli repozytorium Git będzie dostępne; w przeciwnym razie wykonać równoważną kontrolę białych znaków na zmienionych plikach.

## Stan wykonania — 2026-10-03

Wykonano zadania 1–6:

- [x] Testy kontraktowe zakładek i Pomocy.
- [x] Pliki treści Pomocy PL/EN/DE oraz bridge.
- [x] Zakładka Pomoc z dialogiem „O Programie” i pięcioma tematami.
- [x] Karta Tłumaczenie zgodna ze specyfikacją.
- [x] Kolejność zakładek i nazwa aplikacji.
- [x] Dokumentacja, testy, compileall i Ruff.

Dodatkowo potwierdzono w runtime QML obecność dialogu „O Programie” oraz pięciu deklaracji TabButton; treść tematów jest dostarczana przez QmlApplicationBridge z plików Markdown.

Finalna weryfikacja: 249 passed; compileall PASS; Ruff PASS; kontrola białych znaków PASS; smoke startu aplikacji QML zakończony kontrolowanym timeoutem 4 s bez błędu inicjalizacji.