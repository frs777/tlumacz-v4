## 2026-10-07 — aktualizacja statystyk czasu i prędkości

- wartości czasu i prędkości są wyświetlane o 1 px większym fontem niż `uiBaseFontSize` i są pogrubione;
- GUI pokazuje **jedną bieżącą prędkość** w znakach/s; nie używa już formatu `bieżąca/średnia` (`0/0`);
- właściwość `averageSpeed` może pozostać dostępna w bridge'u do obliczeń/diagnostyki, ale nie jest prezentowana w tym wierszu.

## 2026-10-05 — stan rzeczywisty kontra historyczne wymagania

Aktualny `TranslationPage.qml` jest źródłem prawdy dla geometrii wdrożonej w GUI. W bieżącym kodzie przyciski **Tłumacz** i **Anuluj** mają po 130 px. Dla Apertium pola **Język źródłowy** i **Język docelowy** mają po 110 px, są tylko do odczytu i nadal znajdują się w tym samym `RowLayout` co przyciski sterowania.

Jeżeli wcześniejsze punkty tej specyfikacji wymagają osobnego wiersza języków Apertium, jest to wymaganie docelowe, a nie opis obecnego wdrożenia. Nie należy oznaczać tego jako wykonane bez zmiany kodu i testu struktury QML.

Pola plików i podgląd należy weryfikować z aktualnym `TranslationPage.qml`, ponieważ historyczne wpisy changelogu zawierają kilka kolejnych korekt szerokości i wysokości.

## 2026-10-05 — pola językowe Apertium: prezentacja, nie wybór
- karta Tłumaczenie pokazuje język wejściowy i wyjściowy Apertium w nieedytowalnych polach tekstowych;
- pola nie otwierają listy i nie zmieniają ustawień bezpośrednio z tej powierzchni;
- odstęp poziomy między blokami językowymi wynosi 24 px;
- przyszły mechanizm rozpoznawania kierunków par Apertium pozostaje osobnym punktem podpięcia i nie jest częścią tej zmiany.

## 2026-10-05 — aktywne wybory języków Apertium

- pola **Język źródłowy** i **Język docelowy** w wierszu karty są aktywnymi ComboBox, a nie polami tylko do odczytu;
- **Język docelowy** korzysta z tego samego bridge.targetLanguages i bieżącego bridge.targetLanguage co pozostałe miejsca wyboru języka docelowego;
- **Język źródłowy** korzysta z bridge.apertiumSourceLanguages, budowanego na podstawie kierunków zadeklarowanych w $HOME/.config/tlumacz/apertium;
- ten sam mechanizm jest używany w sekcji Apertium zakładki **API/Serwer**, aby oba miejsca sterowały jednym stanem bridge;
- obecna detekcja zbiera zadeklarowane kierunki z modes.xml; rozróżnienie par jednokierunkowych i dwukierunkowych jest celowo pozostawione jako następny etap i ma zostać podłączone w oznaczonym punkcie bridge.

## 2026-10-05 — końcowa korekta geometrii wiersza sterowania

- wiersz sterowania nie ma bocznych marginesów;
- **Tłumacz** i **Anuluj** mają szerokość 130 px; ich lewa pozycja pozostaje zakotwiczona bez bocznego marginesu kontenera;
- blok **Język docelowy** ma `Layout.leftMargin: 12`, tworząc odstęp 12 px pomiędzy dwoma blokami językowymi Apertium;
- brak dodatkowego odsunięcia języków od krawędzi karty;
- wiersz zachowuje `Layout.topMargin: 0`, `Layout.bottomMargin: 0` i `spacing: 2`.

## 2026-10-05 — korekta marginesów wiersza akcji

Wiersz **Tłumacz / Anuluj / język źródłowy / język docelowy** ma 24 px marginesu od obu bocznych krawędzi karty, 0 px marginesu pionowego i odstęp 2 px między elementami. Ma to zapewnić pełną widoczność przycisków oraz bardziej zwarty układ pionowy.

## 2026-10-05 — aktualna geometria responsywna karty

- pola ścieżek **Plik wejściowy** i **Plik wyjściowy** są elastyczne i rozciągają się do przycisku **Przeglądaj...**;
- przyciski **Przeglądaj...** mają 130 px i pozostają w obrębie karty;
- dla Apertium **Tłumacz**, **Anuluj**, **Język źródłowy** i **Język docelowy** pozostają w jednym wierszu; przyciski są wyrównane do poziomu pól językowych;
- przyciski akcji mają 130 px, pola językowe 110 px, a pola formularza wysokość 36 px;
- górna część karty używa kompaktowych odstępów 2 px;
- Log i Podgląd mają jednakową preferowaną wysokość 220 px.

Ten wpis ma pierwszeństwo przed wcześniejszymi historycznymi wartościami szerokości i wysokości w dalszej części dokumentu.

## 2026-10-05 — wiersz akcji i języków Apertium

Wiersz **Tłumacz / Anuluj** zawiera również dla Apertium oba opisane pola językowe: **Język źródłowy** oraz **Język docelowy**. Każdy opis pozostaje bezpośrednio nad swoim nieedytowalnym polem. Sekcja nie jest już osobnym blokiem poniżej sterowania. Przyciski **Przeglądaj...** mają 110 px i są wyrównane do prawej krawędzi sekcji plików.

## 2026-10-05 — geometria pól plików

W sekcji **Pliki** pola wejściowe i wyjściowe mają `Layout.preferredWidth` oraz `Layout.maximumWidth` ustawione na **240 px**. Zachowują `Layout.fillWidth: true` i `Layout.minimumWidth: 0`, dzięki czemu mogą zwężać się przy ograniczonej szerokości okna. Przyciski **Przeglądaj...** pozostają stałe na **96 px**. Zmiana obejmuje wyłącznie te dwa pola.

# Specyfikacja karty „Tłumaczenie” — GUI QML V4

**Status:** aktywna specyfikacja interfejsu
**Data:** 2026-10-03
**Aplikacja:** **Tłumacz**

Ten dokument jest źródłem prawdy dla układu i kolejności elementów karty **„Tłumaczenie”**. Implementacja QML ma odwzorować poniższą strukturę bez zmiany kolejności elementów.

## 1. Zasada ogólna karty

Karta „Tłumaczenie” składa się z trzech kolejnych sekcji:

1. **Pliki**
2. **Log**
3. **Podgląd tłumaczenia**

Sekcje są **wyraźnie rozdzielone poziomymi liniami**.

Kolejność na ekranie jest pionowa:

    TŁUMACZENIE
    ────────────────────────────────────────────
    Pliki
    ────────────────────────────────────────────
    Plik wejściowy   [ścieżka................] [Przeglądaj]
    Plik wyjściowy  [ścieżka................] [Przeglądaj]
    [Tłumacz] [Anuluj]                 [Język docelowy ▼]
    [██████████████████████████████████]  0% / 100%
    Czas 00:00     Prędkość tłumaczenia 0/0     znaki/s
    ────────────────────────────────────────────
    Log:
    [okienko komunikatów logu]
    ────────────────────────────────────────────
    Podgląd tłumaczenia:
    [okienko podglądu przetłumaczonego pliku]

Schemat jest poglądowy. Ostateczne rozmiary kontrolek mają wynikać z projektu QMS, ale **kolejność i podział na sekcje są wiążące**.

---

# 2. Sekcja „Pliki”

Sekcja znajduje się na samej górze karty.

## 2.1 Plik wejściowy

W jednym wierszu, od lewej do prawej:

1. napis **„Plik wejściowy”**;
2. pasek/pole pokazujące położenie wybranego pliku;
3. przycisk **„Przeglądaj”**.

Pole ścieżki jest elementem prezentującym aktualny plik wejściowy i nie powinno być zastępowane samym napisem lub pustą dekoracją.

Przycisk **„Przeglądaj”** ma być w całości widoczny i otwierać wybór pliku wejściowego i rzeczywiście aktualizować pole ścieżki.

## 2.2 Plik wyjściowy

Bezpośrednio pod wierszem pliku wejściowego:

1. napis **„Plik wyjściowy”**;
2. pasek/pole pokazujące położenie pliku wyjściowego;
3. przycisk **„Przeglądaj”**.

Przycisk ma być w całości widoczny i funkcjonalnie połączony z wyborem ścieżki pliku wyjściowego.

## 2.3 Sterowanie tłumaczeniem i język

Następny wiersz zawiera:

- przycisk **„Tłumacz”**;
- przycisk **„Anuluj”**;
- pole wyboru **„Język docelowy”**.

Elementy mają być rzeczywistymi kontrolkami połączonymi z funkcjami aplikacji:

- **Tłumacz** uruchamia tłumaczenie aktualnie wybranego dokumentu;
- **Anuluj** anuluje aktywne tłumaczenie;
- **Język docelowy** zmienia język docelowy używany przez tłumaczenie.

Pole wyboru języka ma pozostać w tym wierszu, a nie zostać przeniesione do osobnej sekcji.

## 2.4 Pasek postępu

Pod sterowaniem tłumaczeniem znajduje się pasek postępu.

Wymagania:

- pokazuje postęp tłumaczenia;
- podczas aktywnego tłumaczenia pokazuje **wartość procentową**;
- wartość procentowa jest aktualizowana przez rzeczywisty stan procesu;
- nie jest to wyłącznie element dekoracyjny.

Docelowo należy zachować czytelne powiązanie:

    postęp procesu → wartość procentowa → pasek postępu

## 2.5 Czas i prędkość tłumaczenia

Bezpośrednio pod paskiem postępu znajduje się wiersz statystyk.

Kolejność elementów:

1. napis **„Czas”**;
2. wartość czasu, początkowo **„00:00”**;
3. napis **„Prędkość tłumaczenia”**;
4. wartość prędkości, początkowo **„0/0”**;
5. napis **„znaki/s”**.

Układ logiczny:

    Czas 00:00     Prędkość tłumaczenia 0/0     znaki/s

Wartości muszą być aktualizowane przez rzeczywisty proces tłumaczenia.

---

# 3. Pozioma linia rozdzielająca

Po zakończeniu sekcji „Pliki” musi znajdować się **pozioma linia**.

Linia jest separatorem wizualnym i ma jednoznacznie oddzielać:

    PLIKI
    ────────────────────────────────────────────
    LOG

Nie należy zastępować jej wyłącznie większym odstępem.

---

# 4. Sekcja „Log:”

Sekcja znajduje się pod separatorem.

Nagłówek:

**„Log:”**

Pod nagłówkiem znajduje się jedno większe okienko przeznaczone do wyświetlania komunikatów logu.

Wymagania:

- okienko jest rzeczywiście podłączone do logów aplikacji;
- komunikaty są dopisywane/aktualizowane podczas działania programu;
- użytkownik może obserwować przebieg operacji;
- prezentacja logów ma zostać odwzorowana funkcjonalnie na rozwiązaniu używanym w **V3**;
- nie należy tworzyć pozornego pola tekstowego, które nie odbiera komunikatów runtime.

Szczegóły wizualne prezentacji logów należy ustalić na podstawie istniejącego GUI V3, a nie wymyślać nowego formatu.

---

# 5. Pozioma linia rozdzielająca

Po sekcji „Log:” musi znajdować się kolejna **pozioma linia**.

Układ:

    LOG
    [okienko logu]
    ────────────────────────────────────────────
    PODGLĄD TŁUMACZENIA

---

# 6. Sekcja „Podgląd tłumaczenia:”

Nagłówek:

**„Podgląd tłumaczenia:”**

Pod nagłówkiem znajduje się większe okienko podglądu.

Okienko ma służyć do wyświetlania **przetłumaczonej treści pliku**.

Wymagania:

- podgląd jest podłączony do rzeczywistego wyniku tłumaczenia;
- podczas tłumaczenia może prezentować aktualnie dostępny wynik, jeżeli backend udostępnia taki stan;
- po zakończeniu tłumaczenia ma umożliwić użytkownikowi obejrzenie przetłumaczonego dokumentu;
- nie może być wyłącznie statycznym polem tekstowym demonstracyjnym.

---

# 7. Pełna kolejność elementów

Implementacja karty musi zachować dokładnie następującą kolejność:

    Tłumaczenie

    SEKCJA: Pliki
    ──────────────────────────────────────────────
    Plik wejściowy      [położenie pliku] [Przeglądaj]
    Plik wyjściowy      [położenie pliku] [Przeglądaj]

    [Tłumacz] [Anuluj]                 [Język docelowy]

    [pasek postępu ................................] XX%

    Czas 00:00     Prędkość tłumaczenia 0/0     znaki/s
    ──────────────────────────────────────────────

    SEKCJA: Log:
    [okienko komunikatów logu]
    ──────────────────────────────────────────────

    SEKCJA: Podgląd tłumaczenia:
    [okienko podglądu przetłumaczonego pliku]

## 7.1 Elementy, które muszą być funkcjonalne

| Element | Wymagana funkcja |
|---|---|
| Plik wejściowy | pokazuje aktualną ścieżkę wejściową |
| Przeglądaj przy wejściu | otwiera wybór pliku wejściowego |
| Plik wyjściowy | pokazuje aktualną ścieżkę wyjściową |
| Przeglądaj przy wyjściu | otwiera wybór pliku wyjściowego |
| Tłumacz | uruchamia tłumaczenie |
| Anuluj | zatrzymuje/anuluje aktywne tłumaczenie |
| Język docelowy | ustawia język docelowy |
| Pasek postępu | pokazuje rzeczywisty postęp |
| Procent | pokazuje procentowy postęp procesu |
| Czas | pokazuje rzeczywisty czas |
| Prędkość tłumaczenia | pokazuje rzeczywistą prędkość |
| znaki/s | jednostka prędkości |
| Log | pokazuje rzeczywiste komunikaty runtime |
| Podgląd tłumaczenia | pokazuje rzeczywisty wynik tłumaczenia |

---

# 8. Nazwa aplikacji

Nazwa użytkowa aplikacji w interfejsie ma brzmieć:

**Tłumacz**

Nie należy używać nazwy **„appy.ty”** jako nazwy aplikacji, tytułu okna ani brandingu GUI.

Nazwa techniczna pakietu/entry pointu może pozostać niezależna od nazwy prezentowanej użytkownikowi. Warstwa GUI ma jednak prezentować użytkownikowi nazwę **Tłumacz**.

---

# 9. Reguła implementacyjna

Ta specyfikacja jest punktem odniesienia dla dalszej pracy nad kartą „Tłumaczenie”.

Przed przejściem do kolejnych kart należy doprowadzić kartę „Tłumaczenie” do stanu, w którym:

1. układ elementów odpowiada kolejności opisanej powyżej;
2. sekcje są rozdzielone poziomymi liniami;
3. wszystkie wymienione przyciski i pola są podłączone do rzeczywistych funkcji runtime;
4. log działa zgodnie z funkcjonalnym wzorcem V3;
5. podgląd pokazuje rzeczywisty wynik tłumaczenia;
6. aplikacja prezentuje nazwę **Tłumacz**;
7. nie są dodawane nowe elementy spoza tej specyfikacji bez uzgodnienia.

**Karta „Tłumaczenie” oraz karta „Pomoc” są obecnie przedmiotem implementacji i weryfikacji. Pozostałe karty pozostają na późniejszym etapie.**

# 10. Specyfikacja karty „Pomoc” — 2026-10-03

Kolejność głównych zakładek aplikacji jest wiążąca:

**Tłumaczenie | API i serwer | Serwer i API | Pomoc**

## 10.1 „O programie”

Po prawej stronie nagłówka zakładki **Pomoc** znajduje się przycisk **„O Programie”**. Kliknięcie otwiera wyskakujące okno modalne.

Treść okna:

- **TŁUMACZ**
- **Wersja: X.X.X** — wersja pobierana z wersji aplikacji; aktualnie 0.40.0.
- **Program do tłumaczenia dokumentów z wykorzystaniem AI i graficznego interfejsu Qt.**
- **Obsługuje lokalne i chmurowe backendy tłumaczenia, w tym llama.cpp, Apertium i (w przyszłości) inne.**
- **Licencja MIT**

Treść opisowa ma być lokalizowana przez centralny system i18n, natomiast numer wersji ma pochodzić z tlumacz.__version__.

## 10.2 Pomoc podręczna

Pod nagłówkiem znajduje się pole **Pomoc podręczna**.

Pole pomocy ma własne zakładki tematyczne. Każda zakładka pokazuje osobną sekcję treści.

Źródłem treści są pliki Markdown znajdujące się w src/tlumacz/qml_gui/:

- help.pl.md
- help.en.md
- help.de.md

Bridge QML odczytuje plik odpowiadający aktualnemu językowi aplikacji i rozdziela jego sekcje według nagłówków ##.

Zmiana języka aplikacji przełącza również treść zakładek Pomocy.

Minimalny zestaw tematów obecnej wersji:

1. Wprowadzenie
2. Tłumaczenie dokumentu
3. Backendy tłumaczenia
4. Parametry i pliki
5. Log i podgląd

Treść może być rozwijana w plikach pomocy bez umieszczania długich bloków tekstu bezpośrednio w QML.

## 10.3 Wymagania funkcjonalne

| Element | Wymagana funkcja |
|---|---|
| O programie | otwiera modalne okno informacji o programie |
| Wersja | pobierana z rzeczywistej wersji aplikacji |
| Pomoc podręczna | wyświetla treść z pliku pomocy |
| Zakładki tematów | przełączają niezależne sekcje pomocy |
| Język | przełącza plik pomocy zgodnie z językiem aplikacji |
| Brak pliku językowego | używa bezpiecznego fallbacku PL zamiast blokować GUI |

## 10.4 Zasada implementacyjna

Karta „Pomoc” nie może wrócić do jednego dużego pola help.body zaszytego w i18n.py jako głównego źródła treści. Centralne i18n pozostaje źródłem krótkich etykiet UI i treści dialogu „O programie”; rozbudowana pomoc podręczna należy do plików Markdown.


# 11. Specyfikacja karty „Serwer i API” — ustawienia zależne od wybranego serwera

Karta **„Serwer i API”** ma prezentować ustawienia indywidualne zależnie od wybranego serwera/backendu. Po zmianie typu serwera widoczny zestaw ustawień ma odpowiadać wybranemu backendowi.

## 11.1 A. llama.cpp

### Sekcja „Ustawienia API”

Kolejność elementów:

1. napis **„Adres URL”** + pasek z adresem serwera;
   - adres jest nieedytowalny poza ostatnim wpisem / końcowym elementem adresu zgodnie z konfiguracją serwera;
2. napis **„Klucz API”** + zamaskowane pole klucza API;
3. napis **„Typ serwera”** + pole wyboru zawierające:
   - **„llama.cpp”**
   - **„Apertium”**
   - **„Chmura”**
   - puste pole edytowalne.

### Sekcja „Serwer llama.cpp - lokalny”

Kolejność elementów:

1. napis **„Port:”** + edytowalny pasek liczbowy;
   - zakres: **1111–99999**;
   - strzałki zmieniają wartość o **1**;
   - przycisk **„Losowy”** losuje port z tego zakresu;
2. napis **„Obliczenia serwera:”** + pole wyboru:
   - **„CPU”**
   - **„GPU”**;
3. napis **„Model:”** + pole wyboru pliku + przycisk **„Przeglądaj”**;
4. napis **„Szablon czatu:”** + pole wyboru:
   - **„janji”**
   - **„chatml”**
   - **„TranslateGemma”**;
5. napis **„Wątki (pararell)”** + edytowalny pasek liczbowy;
   - zakres: **1–8**;
6. checkbox **„Uruchamiaj serwer razem z programem”**;
7. checkbox **„Czyść bufor po każdym tłumaczeniu”**;
8. checkbox **„Restart procesu po tłumaczeniu”**;
9. przycisk **„Restart serwera”**.

Wszystkie wymienione kontrolki mają być rzeczywiście podłączone do stanu i operacji backendu llama.cpp. Zakresy liczbowe i działanie przycisku „Losowy” są częścią kontraktu funkcjonalnego, a nie wyłącznie ograniczeniem wizualnym.

## 11.2 B. Apertium

**Specyfikacja Apertium nie została jeszcze podana. Nie należy jej uzupełniać na podstawie domysłów ani wiedzy ogólnej.**

Po otrzymaniu dalszego opisu należy dopisać go tutaj z zachowaniem podanej przez użytkownika kolejności i nazw kontrolek.


## 2026-10-05 — brak duplikacji wyboru języka docelowego w Pomocy
- karta Pomoc nie zawiera osobnego wyboru języka docelowego; wybór należy do powierzchni Tłumaczenie;
- język programu pozostaje interaktywnym wyborem lokalizacji.
