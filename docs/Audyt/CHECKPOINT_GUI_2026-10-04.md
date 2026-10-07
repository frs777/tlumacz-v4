---
id: checkpoint-gui-v4-2026-10-04
status: evidence
meta:
  contentType: Checkpoint
  category: audit
version: 0.40.0
updated: 2026-10-04
owner: project-maintenance
source: src/tlumacz/qml_gui/
depends_on: [docs/STATUS.md, docs/technical-docs/QML_GUI_LAYOUT.md, docs/technical-docs/QML_GUI_DESIGN.md]
expires_when: zastąpienie przez nowszy checkpoint GUI
last_validation: "inspekcja dokumentacji SentinelX 2026-10-04"
---

# CHECKPOINT — aktualny stan GUI V4 i zakres dalszej pracy

Data: 2026-10-04
Projekt: /home/frs/Projekty/tlumacz-v4/

## Cel

Ten plik jest punktem powrotu dla dalszych prac nad GUI po serii wcześniejszych audytów.

Nie rozpoczynamy nowego pełnego audytu projektu. W projekcie istnieją już m.in.:
- docs/Audyt/RAPORT_KONCOWY_AUDYTU_2026-10-01.md
- docs/Audyt/AUDYT_REGRESJI_GUI_CLOUD_V3_V4_2026-10-01.md
- docs/Audyt/AUDYT_FORENSICZNY_V3_V4_2026-10-01.md
- docs/Audyt/AUDYT_KODU_2026-10-01.md
- docs/Audyt/AUDYT_DOKUMENTACJI_2026-10-01.md
- docs/Audyt/AUDYT_LICENCYJNY_OKAPI_LINGUA_APERTIUM_2026-09-28.md
- docs/Audyt/RAPORT_NAPRAWY_GUI_CLOUD_2026-10-01.md
- dokumenty dotyczące refaktoryzacji GUI i Main Window.

Niniejszy checkpoint nie zastępuje tych dokumentów.

## Decyzja robocza

Na obecnym etapie kończymy konfigurację i układ GUI, natomiast nie podłączamy jeszcze brakujących funkcji backendowych ani nie odtwarzamy na własną rękę funkcji utraconych podczas migracji 0.3.2 -> 0.4.0.

Po zakończeniu konfiguracji GUI nastąpi przegląd istniejących audytów i przygotowanie planu naprawy/regresji funkcjonalnych.

Dzięki temu obecny wygląd GUI będzie zabezpieczonym punktem odniesienia, a późniejsze podłączanie funkcji będzie wykonywane według jednego uzgodnionego planu, zamiast kolejnych doraźnych poprawek.

## Aktualny stan GUI

### Extras / Przełączniki

Ustalony układ:
- kolejność sekcji: Glosariusz -> Umiejętności -> Ustawienia LLM;
- nagłówki sekcji są pogrubione;
- Przeglądaj... — 120 px;
- Dodaj — 120 px;
- przyciski skilli — 180 px;
- Rozmiar bloku — 120 px;
- Temperatura — 120 px;
- pola tekstowe glosariusza są elastyczne;
- bez sztucznych prawych marginesów;
- separatory pozostają zgodne z ustalonym układem;
- po wybraniu Apertium sekcja Ustawienia LLM ma znikać, a na dole pozostają Przywróć domyślne i Zapisz ustawienia.

### API i serwer — llama.cpp

Obowiązuje ustalony kierunek:
- na górze pogrubiony tytuł API i Serwer;
- konfiguracja API;
- wybór serwera;
- dla llama.cpp separator;
- pogrubiony tytuł Serwer llama.cpp — lokalny;
- istniejący wybór Szablon czatu zamiast wcześniejszej temperatury;
- obsługiwane wartości: jinja, chatml, TranslateGemma (wewnętrznie translategemma);
- backend posiada już set_chat_template().

### Ikona aplikacji

Istnieją:
- src/tlumacz/tlumacz-dark.svg
- src/tlumacz/tlumacz-light.svg

Ustalono automatyczny dobór ikony:
- motyw ciemny -> tlumacz-dark.svg;
- motyw jasny -> tlumacz-light.svg;
- motyw systemowy -> dobór na podstawie palety systemowej;
- zmiana motywu w trakcie działania aktualizuje ikonę.

### Apertium — specyfikacja GUI

Na samej górze ma być pogrubiony tytuł API i Serwer.

Dla Apertium ma istnieć jedno pole Serwer, a jego pozycja ma brzmieć Apertium — serwer lokalny. Wybór odnosi się do ustawienia globalnego serwera, nie do osobnej konfiguracji tylko tej karty.

Po wybraniu Apertium:

Ustawienia API

- Język źródłowy + ComboBox;
- Język docelowy + ComboBox;
- Serwer: + ComboBox.

Listy języków mają docelowo wynikać z rzeczywiście dostępnych par Apertium, a nie ze statycznej listy.

Przykład dla eng > pl, eng > spa, eng > de:
- źródłowy: auto, angielski, brak pary;
- docelowy: polski, hiszpański, niemiecki, brak pary.

Języki docelowe zależą od wybranego języka źródłowego. Brak odpowiedniej pary ma być jawnie oznaczany jako brak pary.

Automatyczna detekcja źródła ma następować:
1. przy przełączeniu na Apertium;
2. przy wyborze pliku do tłumaczenia;
3. przy zmianie źródłowego na auto.

Po stronie tłumaczenia, po wybraniu Apertium, zwykły wybór języka ma zniknąć i zostać zastąpiony informacją:
- Język źródłowy: angielski    docelowy: niemiecki;
- albo Język źródłowy: auto    docelowy: angielski.

Przy braku pary oba pola mają pokazywać brak pary.

Ustawienia języka Apertium na karcie API i serwer są informacją wykorzystywaną na stronie tłumaczenia. Apertium pozwala ustawić sztywno źródło i cel zależnie od istniejących par, ale istnienie pary nie gwarantuje jakości tłumaczenia.

Po ustawieniach ma być separator oraz pogrubione Uwagi i pole tekstowe z opisem obsługi par językowych Apertium wraz z przykładami.

Po wybraniu Apertium w zakładce Przełączniki ma zniknąć cała sekcja Ustawienia LLM, a na dole pozostają tylko Przywróć domyślne i Zapisz ustawienia.

## Ważne rozdzielenie GUI od funkcji

Mechanizmu detekcji języka nie należy teraz dorabiać jako przypadkowej logiki QML.

W V3.2 istniał mechanizm Lingua związany z language_detector.py. Jego obecność i kontrakt w V4 należy rozstrzygnąć na podstawie istniejących audytów oraz porównania V3.2/V4.

Na tym etapie GUI konfigurujemy zgodnie z uzgodnioną koncepcją, ale brakujące funkcje pozostawiamy do późniejszego planu naprawy.

Nie tworzymy tymczasowych obejść tylko po to, aby ekran wyglądał na funkcjonalny.

## Pliki GUI

- src/tlumacz/qml_gui/Main.qml
- src/tlumacz/qml_gui/ExtrasPage.qml
- src/tlumacz/qml_gui/ApiPage.qml
- src/tlumacz/qml_gui/HelpPage.qml

Obecny ApiPage.qml posiada osobną gałąź Apertium, ale jej układ nie odpowiada jeszcze w pełni powyższej specyfikacji. Nie należy traktować obecnego kodu jako zakończonej implementacji Apertium.

## Następny etap

### Teraz
1. Dokończyć wyłącznie konfigurację GUI i układ ekranów.
2. Nie odtwarzać jeszcze brakujących funkcji backendowych.
3. Nie zmieniać architektury backendu tylko na potrzeby bieżącego wyglądu.
4. Po zmianach QML wykonać standardową weryfikację projektu.

### Później
Po zakończeniu konfiguracji GUI:
1. przejrzeć wszystkie istniejące audyty;
2. znaleźć istniejący plan naprawy, jeśli już został sporządzony;
3. uzupełnić go tylko o rzeczywiście potwierdzone regresje;
4. ustalić kolejność przywracania funkcji;
5. dopiero wtedy podłączać backend do gotowego GUI.

## Punkt powrotu

Jeżeli dalsze prace zaczną mieszać konfigurację GUI z naprawą funkcjonalności, należy wrócić do tego dokumentu.

> Najpierw doprowadzamy GUI do uzgodnionego stanu wizualnego i interakcyjnego. Funkcje, których brak lub których kontrakt jest niepewny po migracji 0.3.2 -> 0.4.0, naprawiamy dopiero na podstawie przeglądu istniejących audytów i osobnego planu.

Checkpoint nie oznacza, że funkcje zostały uznane za utracone. Oznacza tylko, że ich naprawa zostaje świadomie odseparowana od bieżącej pracy nad GUI.


## Aktualizacja checkpointu — 2026-10-04, wznowienie prac

Wznowiono konfigurację GUI z tego checkpointu.

Wykonane w tej sesji:
- przebudowano powierzchnię Apertium w ApiPage.qml zgodnie z bieżącym kontraktem GUI;
- dodano lokalizowaną nazwę serwera Apertium — serwer lokalny;
- pozostawiono jeden wybór serwera;
- dodano pola Język źródłowy i Język docelowy oraz sekcję Uwagi;
- na TranslationPage.qml dla Apertium zastąpiono zwykły wybór celu informacją o źródle i celu;
- na ExtrasPage.qml ukrywana jest sekcja Ustawienia LLM, a akcje Przywróć domyślne i Zapisz ustawienia pozostają dostępne;
- dynamiczne filtrowanie par Apertium i właściwa detekcja języka nie zostały implementowane — pozostają osobnym etapem integracji funkcji.

Weryfikacja po zmianach:
- suite testów: 272 passed;
- testy GUI/i18n: 57 passed;
- qmllint zmienionych kart: kod wyjścia 0.
