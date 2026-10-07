## 2026-10-06 — przepływ ustawień tłumaczenia do llama.cpp

Wybór języka docelowego z GUI jest częścią kontraktu llama.cpp. Wybór źródła jest zachowany w bridge i przekazywany do usługi dokumentowej; dla backendów dynamicznych może zostać zastąpiony wynikiem detekcji chunka. Pola pliku wejściowego i wynikowego są przekazywane do usługi dokumentowej, a nie do procesu llama-server, ponieważ serwer otrzymuje tekst do tłumaczenia, nie nazwy plików.

## 2026-10-06 — pełny kontrakt ustawień llama.cpp

W karcie API i serwer sekcja llama.cpp zawiera: adres serwera (domyślnie 127.0.0.1), port 1111–65535 z losowaniem, CPU/GPU, jinja/chatml/TranslateGemma, parallel 1–8 oraz ścieżkę GGUF.

Karta Przełączniki pozostaje właścicielem parametrów workloadu: Rozmiar bloku 500–8000 krok 500 oraz Temperatura 0.0–1.0 krok 0.1.

Wartości są zapisywane przez bridge. Przy uruchamianiu llama.cpp GUI przekazuje je do runtime/adaptera, a techniczne parametry niewystawione w GUI są pobierane z $HOME/.config/tlumacz/llama.json.

## 2026-10-05 — zweryfikowany układ aktywnego GUI

Stan należy czytać z aktualnych plików QML, a nie tylko z historycznych wpisów zmian.

- `TranslationPage.qml`: przyciski **Tłumacz** i **Anuluj** mają obecnie 130 px;
- pola językowe Apertium mają po 110 px i są tylko do odczytu;
- pola Apertium są nadal dziećmi tego samego `RowLayout` co przyciski sterowania;
- `ApiPage.qml`: pola języków Apertium mają po 140 px i są tylko do odczytu;
- karta **Przełączniki** jest przeznaczona dla glosariusza, skilli i ustawień LLM;
- ustawienia zachowania backendów są przypisane do odpowiednich sekcji karty **API i serwer**;
- **Pomoc** korzysta z pięciu tematów Markdown.

Jeżeli changelog opisuje inną geometrię niż aktualny QML, wpis changelogu jest historią, a ten dokument opisuje stan bieżący.

## 2026-10-05 — lokalizacja nagłówków list skilli
- nagłówki „Skille systemowe” i „Skille użytkownika” korzystają z kluczy lokalizacyjnych;
- zlokalizowano również komunikat braku skilli użytkownika oraz podpowiedź usuwania skilla w PL/EN/DE.

## 2026-10-05 — dalsze przesunięcie pól Apertium i skrócenie etykiet EN
- blok pól języka wejściowego i wyjściowego przesunięto o 40 px w lewo przez dodanie prawego marginesu do drugiego pola;
- w angielskiej lokalizacji etykiety zmieniono na krótkie „Lang in” i „Lang out”.

## 2026-10-05 — korekta pól językowych Apertium
- pola języka wejściowego i wyjściowego na karcie Tłumaczenie są polami tekstowymi tylko do odczytu, a nie listami wyboru;
- zwiększono odstęp między tymi polami do 24 px;
- w karcie API i serwer pola Apertium również są nieedytowalnymi polami tekstowymi, z odstępem 24 px między kolumnami;
- w angielskiej lokalizacji stosowane są krótkie etykiety „Input language” i „Output language”.

## 2026-10-05 — korekta końcowa położenia przycisków i odstępu języków

- usunięto boczne marginesy 24 px z całego wiersza **Tłumacz / Anuluj / języki**, ponieważ przesuwały również przycisk **Tłumacz** i zmniejszały dostępną szerokość wiersza;
- przyciski **Tłumacz** i **Anuluj** pozostają zakotwiczone od lewej strony wiersza i mają stałą szerokość **130 px**, zgodną ze wzorcem pełnego przycisku używanym w karcie;
- **Język źródłowy** i **Język docelowy** są odsunięte od siebie o **12 px** wyłącznie na granicy tych dwóch bloków;
- nie dodano odsunięcia bloków językowych od lewej ani prawej krawędzi karty;
- pionowe marginesy wiersza pozostają na **0 px**, a odstęp wiersza na **2 px**, aby zachować kompaktowanie pionowe.

## 2026-10-05 — końcowa korekta wiersza przycisków

- wiersz **Tłumacz / Anuluj / języki** otrzymał marginesy wewnętrzne 24 px od lewej i prawej krawędzi karty, aby przyciski miały pełną widoczną szerokość;
- pionowe marginesy tego wiersza ustawiono na 0, a odstęp między elementami na 2 px;
- zachowano wyrównanie przycisków do dołu względem pól językowych.

## 2026-10-05 — dynamiczna geometria pól plików i wyrównanie wiersza sterowania

- pola **Plik wejściowy** i **Plik wyjściowy** zajmują całą dostępną szerokość pomiędzy etykietą a przyciskiem **Przeglądaj...**; usunięto stałe ograniczenie 240 px;
- przyciski **Przeglądaj...** pozostają stałe na **130 px** i nie są wypychane poza kartę;
- wiersz **Tłumacz / Anuluj / język źródłowy / język docelowy** ma wspólną geometrię: przyciski są wyrównane do dołu, czyli do poziomu pól językowych;
- przyciski akcji mają **130 px**, a pola językowe **110 px**; pola formularza mają wspólną wysokość **36 px**;
- wiersz sterowania ma wewnętrzne marginesy **10 px**, aby przyciski nie przylegały do krawędzi karty;
- pionowe odstępy karty zmniejszono do **2 px**;
- **Log** i **Podgląd tłumaczenia** zwiększono do jednakowej preferowanej wysokości **220 px**, wykorzystując miejsce odzyskane przez kompaktowanie górnej części karty.

Zmiana dotyczy geometrii i responsywności karty **Tłumaczenie**; logika tłumaczenia pozostaje bez zmian.

## 2026-10-05 — korekta wiersza plików i języków Apertium

- przyciski **Przeglądaj...** w sekcji plików mają **110 px** i są umieszczone przy prawej krawędzi wiersza;
- pola plików pozostają ograniczone do **240 px**; pomiędzy polem a przyciskiem znajduje się wyłącznie elastyczne miejsce wyrównujące przycisk do prawej krawędzi;
- dla Apertium **Język źródłowy** i **Język docelowy**, wraz z opisami i polami, zostały przeniesione do tego samego wiersza co **Tłumacz** i **Anuluj**;
- nie przeniesiono żadnych pozostałych sekcji ani elementów.

## 2026-10-05 — skrócenie pól plików i dopasowanie do przycisków

- pola **Plik wejściowy** i **Plik wyjściowy** mają preferowaną oraz maksymalną szerokość **240 px**, czyli znacznie krótszą od wcześniejszego elastycznego pola;
- pola nadal używają `Layout.fillWidth: true` i `Layout.minimumWidth: 0`, więc przy węższym oknie mogą się zmniejszyć zamiast wypychać przyciski poza widoczny obszar;
- przyciski **Przeglądaj...** pozostają bez zmian, z szerokością **96 px**;
- zmiana dotyczy wyłącznie dwóch pól plików w sekcji **Pliki**.

## 2026-10-05 — naprawa rzeczywistej struktury Apertium

- blok **Język źródłowy / Język docelowy** został faktycznie wydzielony z RowLayout sterowania;
- dodano osobną sekcję apertiumLanguageSection;
- sekcja używa rzeczywistego GridLayout z **2 kolumnami**;
- każda kolumna zawiera etykietę nad nieedytowalnym polem języka;
- zwykły wybór języka docelowego pozostaje w translationControlsSection tylko dla backendów innych niż Apertium;
- test regresyjny sprawdza teraz relację strukturalną między sekcją sterowania i sekcją Apertium, a nie tylko liczbę wystąpień kontrolek;
- weryfikacja runtime potwierdza, że przy backendType = apertium pola są dziećmi GridLayout w apertiumLanguageSection.

Backup przed zmianą: backups/gui-root-cause-20261005/pre-gui-root-cause-fix.tar.gz; SHA-256: b5c328b8492bc98d1bedcab596e9fd465ab2a11383fb09b451910d58bca181da2.

Pełny research przyczynowy i dowody diagnostyczne zapisano w bledy-gui-przyczyny-rozwiazanie.md.

## 2026-10-05 — pełna szerokość przycisków sterowania

- przyciski **Tłumacz** i **Anuluj** w sekcji sterowania otrzymały stałą szerokość 110 px;
- dla obu przycisków ustawiono jednocześnie `minimumWidth`, `preferredWidth` i `maximumWidth`, aby Layout nie ściskał ich przy dostępnej szerokości wiersza;
- zmiana zabezpiecza pełne wyświetlanie przycisków obok pól językowych Apertium i selektora języka docelowego.

## 2026-10-05 — zagęszczenie pionowe karty „Tłumaczenie”

- układ karty został ściśnięty pionowo: główny ColumnLayout używa odstępu **4 px**, a siatka plików **4 px** między wierszami;
- kolejność elementów w części roboczej zmieniono na **Pliki → Postęp → Statystyki → Sterowanie → Log → Podgląd tłumaczenia**;
- pasek postępu i czasy/statystyki znajdują się teraz **nad przyciskami Tłumacz/Anuluj**;
- odstępy wewnętrzne sekcji postępu, statystyk i sterowania zmniejszono do **3 px**;
- **Log** i **Podgląd tłumaczenia** zwiększono z 120 px do **180 px**, wykorzystując miejsce odzyskane przez zagęszczenie górnej części karty;
- dla Apertium pola języka wejściowego i docelowego pozostają w wierszu sterowania;
- zmiana dotyczy geometrii i kolejności prezentacji, bez zmiany logiki tłumaczenia.

## 2026-10-05 — korekta geometrii karty Tłumaczenie dla Apertium

- przyciski **Przeglądaj...** w sekcji plików mają stałą szerokość **96 px**, dzięki czemu pozostają widoczne po prawej stronie okna;
- na powierzchni Apertium etykiety języków brzmią **Język źródłowy** i **Język docelowy**; dla EN/DE używane są odpowiednie tłumaczenia;
- pola językowe są nieedytowalne i pokazują wyłącznie aktualnie wybrane języki;
- **Log** i **Podgląd tłumaczenia** mają jednakową wysokość **140 px**, aby zmieścić oba pola w dostępnej wysokości okna;
- zmiana dotyczy wyłącznie geometrii i prezentacji karty **Tłumaczenie** dla Apertium; mechanizm wyboru języków i backendu pozostaje bez zmian.

## 2026-10-05 — zapis wyboru backendu z GUI

- wybór backendu w karcie **API i serwer** jest zapisywany do aktywnej konfiguracji natychmiast po zmianie;
- przełączenie na **Apertium** zapisuje `backend_type: "apertium"`, dzięki czemu ponowne uruchomienie nie wraca automatycznie do poprzedniego backendu;
- zmiana stanu runtime nadal emituje `stateChanged`, więc widoczność kontrolek zależnych od `bridge.backendType` pozostaje aktualizowana bez restartu.

## 2026-10-04 — korekta struktury wiersza kontrolek Apertium

- w karcie **Tłumaczenie** blok **Język źródłowy / Język docelowy** jest osobnym wierszem pod wierszem przycisków sterowania;
- blok Apertium nie jest zagnieżdżony w `RowLayout` przycisków, dzięki czemu dwie kolumny językowe mogą wykorzystać pełną szerokość karty;
- etykiety pozostają nad odpowiadającymi im polami, a oba pola znajdują się w jednym wierszu.

## 2026-10-04 — korekta kontrolek językowych i geometrii Log/Podgląd

- na głównej karcie **Tłumaczenie**, dla Apertium, **Język źródłowy** i **Język docelowy** są prezentowane w dwóch równorzędnych kolumnach;
- etykieta znajduje się bezpośrednio nad odpowiednią kontrolką;
- obie kontrolki pozostają w jednym wierszu i wykorzystują dostępną szerokość;
- odstęp pomiędzy etykietą a kontrolką wynosi 3 px, aby ograniczyć wysokość sekcji;
- okna **Log** i **Podgląd tłumaczenia** mają jednakową preferowaną wysokość **180 px**.

## 2026-10-04 — korekta głównego nagłówka karty „API i serwer”

Pierwszy pogrubiony nagłówek wewnątrz `ApiPage.qml` brzmi **API i serwer** i korzysta z tego samego klucza lokalizacyjnego co zakładka (`tab.api_server`). Dla Apertium nie jest to osobny nagłówek „Ustawienia API”.

## 2026-10-04 — aktualny układ Apertium po wznowieniu prac

Aktualna karta Apertium w ApiPage.qml ma strukturę:
1. Ustawienia API;
2. Język źródłowy;
3. Język docelowy;
4. jedyny wybór Serwer, którego pozycja dla Apertium brzmi Apertium — serwer lokalny;
5. separator;
6. Uwagi;
7. nieedytowalny opis ograniczeń Apertium.

Na stronie tłumaczenia dla Apertium zwykły wybór języka docelowego jest zastępowany dwoma informacjami: źródło i cel. Na karcie Przełączniki sekcja Ustawienia LLM jest ukrywana dla Apertium.

Listy par językowych są na tym etapie powierzchnią GUI i nie są jeszcze podłączone do dynamicznego runtime Apertium; jest to świadomie odłożony etap integracji funkcji.

# Konfiguracja bieżąca GUI — 2026-10-04

Poniższy zapis jest aktualnym punktem odniesienia dla układu GUI V4. Opisuje stan po ostatnich korektach interfejsu i ma pierwszeństwo przed starszymi wpisami historycznymi w tym pliku.

## Zakładki

1. **Tłumaczenie**
2. **API i serwer**
3. **Przełączniki**
4. **Pomoc**

## Karta „API i serwer”

Dla backendu llama.cpp kolejność jest:

**Ustawienia API → Adres URL serwera → Klucz API → Serwer → separator → nagłówek „Serwer llama.cpp — lokalny” → Port → Obliczenia serwera → Szablon czatu → Wątki (parallel) → Model → Restartuj serwer**

- nagłówek **Serwer llama.cpp — lokalny** jest pogrubiony i znajduje się bezpośrednio pod separatorem;
- kontrolki Port, Obliczenia serwera, Szablon czatu i Wątki mają szerokość 140 px;
- **Temperatura nie jest już kontrolką tej karty** — została zastąpiona przez **Szablon czatu**;
- Szablon czatu korzysta z istniejącego bridge.chatTemplates / bridge.setChatTemplate() i udostępnia: **jinja**, **chatml**, **TranslateGemma**.

## Karta „Przełączniki”

Kolejność sekcji:

**Glosariusz → Umiejętności → Ustawienia LLM**

### Glosariusz

- wiersz pliku: elastyczny pasek ścieżki + **Przeglądaj...** o stałej szerokości **120 px**;
- drugi wiersz: elastyczne pola **Źródło** i **Tłumaczenie** + **Dodaj** o stałej szerokości **120 px**;
- pola tekstowe wykorzystują pozostałą szerokość, dzięki czemu oba wiersze mają wspólną prawą krawędź;
- tekst przycisków jest w całości widoczny.

### Umiejętności

- dwa równoległe pola: **Skille systemowe** i **Skille użytkownika**;
- przyciski **Importuj skilla...**, **Utwórz skilla...** i **Odśwież** mają po **180 px**;
- użytkownik może usuwać własne skille przyciskiem **×**.

### Ustawienia LLM

- **Rozmiar bloku**: 120 px;
- **Temperatura**: 120 px;
- zakres Rozmiaru bloku: 500–8000, krok 500;
- zakres Temperatury: 0.0–1.0, krok 0.1;
- pola tekstowe promptu i wzorców pomijania są elastyczne.

## Typografia

- na karcie „Przełączniki” kontrolki mają 15 px;
- nagłówki sekcji **Glosariusz**, **Umiejętności** i **Ustawienia LLM** są pogrubione;
- pozostałe elementy tej karty nie są pogrubione.

## Ikona aplikacji

- src/tlumacz/tlumacz-dark.svg — motyw ciemny;
- src/tlumacz/tlumacz-light.svg — motyw jasny;
- launcher ustawia ikonę przez QGuiApplication.setWindowIcon();
- dla motywu **Systemowy** wybór zależy od bieżącej palety systemowej;
- zmiana palety systemowej lub motywu aplikacji aktualizuje ikonę bez restartu.

## Stan weryfikacji

- pełny pytest: **276 passed**;
- qmllint dla Main.qml, ApiPage.qml i ExtrasPage.qml: bez błędów.

---

## 2026-10-04 — szerokości przycisków glosariusza

W sekcji **Glosariusz** przyciski akcji mają stałą szerokość **120 px**. Dotyczy to zarówno **Przeglądaj...**, jak i **Dodaj**. Pola tekstowe zajmują pozostałą szerokość wiersza, dzięki czemu oba wiersze kończą się na tej samej krawędzi, a pełny napis przycisku pozostaje widoczny.

## 2026-10-04 — ikona aplikacji zgodna z motywem

Ikona aplikacji zmienia się razem z aktywnym motywem: **tlumacz-dark.svg** dla ciemnego i **tlumacz-light.svg** dla jasnego. Przy motywie **Systemowy** używana jest jasność bieżącej palety systemowej; zmiana palety aktualizuje ikonę automatycznie.

## 2026-10-04 — nagłówek sekcji llama.cpp na karcie „API i serwer”

Bezpośrednio pod separatorem w sekcji llama.cpp dodano pogrubiony nagłówek **Serwer llama.cpp — lokalny**, przed kontrolkami Port, Obliczenia serwera, Szablon czatu, Wątki (parallel) i Model.

## 2026-10-04 — Szablon czatu zamiast Temperatury na karcie „API i serwer”

W sekcji llama.cpp karty **API i serwer** kontrolka **Temperatura** została zastąpiona polem wyboru **Szablon czatu**. Pole korzysta z istniejącego kontraktu bridge.chatTemplates / bridge.setChatTemplate() i udostępnia trzy wartości: **jinja**, **chatml** oraz **TranslateGemma**. Zmiana dotyczy wyłącznie powierzchni GUI; istniejąca obsługa server_chat_template pozostaje bez zmian.

## 2026-10-03 — uproszczenie karty „Przełączniki”\n\nKolejność sekcji karty została przywrócona do **Glosariusz → Umiejętności → Ustawienia LLM**. Wiersze glosariusza nie używają już sztucznych prawych marginesów; pola tekstowe zajmują dostępną szerokość, a przyciski akcji mają własne stałe kolumny. **Przeglądaj** ma 100 px, **Dodaj** 72 px. Trzy przyciski obsługi skilli mają po 180 px. Kontrolki **Rozmiar bloku** i **Temperatura** mają wspólną szerokość 120 px.\n\n## Korekta kolejności karty „Przełączniki” — 2026-10-03

Sekcja przełączników/checkboxów (`settings.skills_group`) jest umieszczona na początku karty „Przełączniki”, przed sekcją glosariusza. Dzięki temu elementy służące do włączania/wyłączania skilli są dostępne od razu po wejściu do zakładki. Pozostała hierarchia sekcji pozostaje: **Przełączniki → Glosariusz → Ustawienia LLM**.

Weryfikacja: `44 passed`; `qmllint src/tlumacz/qml_gui/ExtrasPage.qml` bez błędów.


## 2026-10-03 — korekta geometrii karty „Przełączniki”

W karcie **Przełączniki** kontrolki formularza mają **15 px**, a karta wymusza normalną wagę fontu; pogrubienie pozostaje wyłącznie na nagłówkach **Glosariusz**, **Umiejętności** i **Ustawienia LLM**. Przycisk **Przeglądaj** w wierszu glosariusza ma **112 px** i nie powinien być obcinany. Pola **Źródło** i **Tłumaczenie** mają zwiększony prawy margines do **57 px**, co skraca każde pole o około 19 px względem poprzedniego układu i wyrównuje je z górnym wierszem.

Pole **Rozmiar bloku** ma szerokość **152 px**, a **Temperatura** została wyrównana do tej samej szerokości, aby bezpiecznie mieścić wartości czterocyfrowe oraz zachować wspólną geometrię kontrolek liczbowych. Nad sekcją **Ustawienia LLM** znajduje się stały separator poziomy `llmSectionSeparator`. Przyciski **Importuj skilla...**, **Utwórz skilla...** i **Odśwież** zachowują wspólną szerokość **210 px**.
## 2026-10-03 — karta „Przełączniki”: stabilny układ glosariusza i umiejętności

Karta **Przełączniki** została uporządkowana pod kątem szerokości okna. W sekcji **Glosariusz** pole ścieżki i przycisk **Przeglądaj** mieszczą się w jednym wierszu, a pola **Źródło**, **Tłumaczenie** i **Dodaj** w drugim. Tekst podpowiedzi ścieżki został skrócony do formy **Plik glosariusza (.csv)**.

Sekcja **Umiejętności** jest oddzielona od glosariusza linią i zawiera dwa równoległe podpola: **Skille systemowe** oraz **Skille użytkownika**. Skille użytkownika pozostają obok systemowych i przy każdym znajduje się przycisk **×** do usunięcia. Przyciski importu, tworzenia i odświeżania są poniżej tych dwóch kolumn.

Czcionki kontrolek karty zostały zmniejszone do 15 px, aby zapobiec nachodzeniu elementów. Parametry LLM mają krótkie pola, a pola tekstowe używają zawijania tekstu. Karta pozostaje przewijana pionowo zamiast rozszerzać się wszerz.

## 2026-10-03 — port: wyrównanie szerokości i losowanie

W karcie **API i serwer** dla llama.cpp pole **Obliczenia serwera** ma tę samą szerokość co pole **Port** (140 px). Obok pola Port znajduje się przycisk **„Losuj port”**, który losuje nowy numer portu z zakresu 1111–65535.

## 2026-10-03 — korekta kolejności karty „API i serwer”

Separator bezpośrednio po wyborze **Serwer** jest elementem stałym karty, niezależnie od wybranego backendu. Dzięki temu kolejność powierzchni jest zawsze zgodna z kontraktem: **Ustawienia API → Adres URL serwera → Klucz API → Serwer → linia podziału → składniki backendu → Restartuj serwer**. Dla llama.cpp składniki po separatorze pozostają w kolejności: **Port → Obliczenia serwera → Temperatura → Wątki (parallel) → Model → Restartuj serwer**.

`ApiPage.qml` nie ukrywa już tej linii podziału zależnie od backendu.

## 2026-10-03 — globalny rozmiar czcionki GUI

`ApplicationWindow` ma bazowy rozmiar czcionki 15 px. Karty tłumaczenia, API i Pomocy używają zwartej typografii oraz mniejszych odstępów, aby zachować gęstość zbliżoną do klasycznego GUI Qt; większy rozmiar pozostaje tylko tam, gdzie jest potrzebny do hierarchii nagłówków.

## 2026-10-03 — końcowa korekta kart „API i serwer”, „Przełączniki” i „Pomoc”

### API i serwer
- zachowano hierarchię **Ustawienia API → Adres URL serwera → Klucz API → Serwer**;
- llama.cpp: separator, Port, Obliczenia serwera, Temperatura, Wątki (parallel), Model GGUF i pełnoszeroki Restartuj serwer na dole;
- Apertium: bez lokalnych separatorów, nagłówek Apertium, krótki nieedytowalny wykryty język źródłowy oraz biały panel objaśniający ograniczenia backendu;
- Chmura: Dostawca ma krótkie pole; wybór Mozhi pokazuje listy Silnik i Instancja;
- Własny: Typ serwera i nieedytowalny Model są po separatorze;
- kontrolki API używają zwiększonej czcionki.

### Przełączniki
- skille wbudowane i użytkownika są układane w jednej siatce, dzięki czemu skille użytkownika zajmują sąsiednie komórki zamiast osobnego bloku pod systemowymi;
- przy każdym skillu użytkownika znajduje się przycisk **×**;
- katalog użytkownika jest odświeżany automatycznie;
- **Utwórz skilla** otwiera niepusty szablon instrukcji, który można zapisać do katalogu użytkownika;
- Rozmiar bloku i Temperatura mają krótkie kontrolki;
- licznik glossariusza prezentuje liczbę jako **Lini**.

### Pomoc
- wybór języka docelowego znajduje się w karcie Pomoc;
- długie nazwy zakładek Pomocy są zawijane do dwóch linii i elidowane dopiero po przekroczeniu dostępnej wysokości;
- zmiana motywu jest stosowana natychmiast przez właściwość palety okna.

## 2026-10-03 — nowy układ karty „API i serwer” — Ustawienia API

Dla aktywnej karty **API i serwer** kontrakt układu został doprecyzowany. Dla llama.cpp kolejność elementów jest stała:

1. **Ustawienia API**
2. **Adres URL serwera** — pole na pełną szerokość
3. **Klucz API** — pole na pełną szerokość, zamaskowane
4. **Serwer** — wybór backendu
5. **Linia podziału**
6. **Port** — krótki wybór liczbowy
7. **Obliczenia serwera** — krótki wybór
8. **Temperatura** — krótki wybór
9. **Wątki (parallel)** — krótki wybór
10. **Model** — pasek wyboru pliku GGUF + **Przeglądaj**
11. **Restartuj serwer** — przycisk przez całą szerokość, na samym dole karty

W tym układzie nie używa się dodatkowych ramek GroupBox ani osobnych nagłówków dla sekcji llama.cpp. Kontrolki parametrów mają krótką szerokość, a etykiety i pola używają większej czcionki GUI.

Backup przed zmianą: `backups/api-page-settings-20261003/pre-api-page-20261003-100204.tar.gz` (SHA-256: `adf7afd82dce7871be45e73ae01e538adc314519bdf6dc72468ec35b5a31d8e6`).

`ApiPage.qml` został dostosowany do powyższego kontraktu; zachowano osobne powierzchnie dla Apertium, Chmury i Własnego backendu.

## 2026-10-03 — korekta rzeczywistego układu karty „Tłumaczenie” przez QML-expert

`TranslationPage.qml` został skorygowany zgodnie z aktywną specyfikacją karty. W obrębie sekcji **Pliki** nie ma już sztucznych separatorów ani dodatkowych nagłówków dla Sterowania, Postępu i Statystyk. Pozostają dokładnie dwa separatory: **Pliki → Log** oraz **Log → Podgląd tłumaczenia**. Wiersz sterowania zachowuje **Tłumacz + Anuluj po lewej** i **Język docelowy po prawej**. Przycisk **Anuluj** ma jawne czerwone tło.

Backup: `backups/translation-page-qml-expert-20261003/pre-translation-page.tar.gz`.

# Układ GUI — Tłumacz V4

## 2026-10-03 — dokładna kolejność karty „Tłumaczenie”

Karta ma kolejność: **Pliki → Sterowanie tłumaczeniem → Postęp → Statystyki → Log → Podgląd tłumaczenia**. Każda sekcja jest oddzielona poziomą linią. W sterowaniu przyciski **Tłumacz** i **Anuluj** pozostają po lewej, **Anuluj** jest czerwony, a **Język docelowy** znajduje się po prawej w tej samej linii.

Backup: `backups/translation-page-order-20261003/pre-translation-page-order.tar.gz` (SHA-256: `71111cccc110cf1317de486a87c218c721a6e300cc4cb2394575bb2c06aac98b`).

## 2026-10-03 — korekta karty „API i serwer”

Karta zachowuje kolejność **Backend → Połączenie → Cloud → llama.cpp → Apertium → Własny**. W sekcji llama.cpp ścieżka do modelu GGUF jest pokazana przed parametrami. Pola **Obliczenia serwera** i **Szablon czatu** mają skróconą szerokość, a na dole znajdują się status serwera, trzy opcje automatyzacji oraz pełnoszeroki przycisk **Restartuj serwer**. Etykieta `settings.model` oznacza teraz **Model**, a nie drugi „Typ serwera”.

## 1. Status dokumentu

Ten dokument jest głównym opisem **układu GUI aplikacji Tłumacz**. Opisuje kolejność zakładek, zawartość poszczególnych kart oraz dokładny układ elementów wymagany przed dalszym podłączaniem logiki.

**Nazwa aplikacji:** Tłumacz

**Podstawowa kolejność zakładek:**

1. Tłumaczenie
2. API i serwer
3. Przełączniki
4. Pomoc

 > Klucz lokalizacyjny pozostaje technicznie `tab.switches`; aktualna etykieta użytkowa to **Przełączniki**.

---

# 2. Karta „Tłumaczenie”

## Sekcja „Pliki”

### 1. Plik wejściowy

- napis **„Plik wejściowy”**
- pole / pasek ze ścieżką pliku
- przycisk **„Przeglądaj”**

### 2. Plik wyjściowy

- napis **„Plik wyjściowy”**
- pole / pasek ze ścieżką pliku
- przycisk **„Przeglądaj”**

### 3. Sterowanie tłumaczeniem

W jednym wierszu:

- przycisk **„Tłumacz”**
- przycisk **„Anuluj”**
- wybór **„Język docelowy”**

### 4. Postęp

- poziomy pasek postępu
- procent postępu widoczny przy pasku / w jego bezpośrednim sąsiedztwie

### 5. Statystyki

Widoczne:

- **Czas:** `00:00`
- **Prędkość tłumaczenia:** `0/0`
- **znaki/s**

## Sekcja „Log:”

- osobne okno komunikatów logów
- wzorzec działania i prezentacji logu zgodny z GUI V3

## Sekcja „Podgląd tłumaczenia:”

- osobne okno podglądu przetłumaczonego pliku
- podgląd ma być częścią tej samej karty

## Wymagania układu

- sekcje są oddzielone poziomą linią
- kolejność elementów jest stała
- nazwa aplikacji to **Tłumacz**
- układ ma odpowiadać powyższej kolejności przed podłączaniem dalszej logiki

---

# 3. Karta „API i serwer”

Ta karta jest przeznaczona dla ogólnej konfiguracji API / połączenia i pozostaje oddzielona od konfiguracji pomocniczej karty **„Przełączniki”**.

Aktualny szczegółowy zakres tej karty należy utrzymywać zgodnie z istniejącą implementacją `ApiPage.qml` i kontraktem bridge.

---

# 4. Kontrakt backendów obsługiwany przez kartę „API i serwer”

## Zasada główna

Ustawienia są **indywidualne zależnie od wybranego serwera**.

Po wybraniu typu serwera widoczna część formularza ma odpowiadać temu serwerowi. Nie należy pokazywać użytkownikowi ustawień, które dotyczą innego backendu.

---

## A. llama.cpp

### 1. Sekcja „Ustawienia API”

#### Adres URL

- napis **„Adres URL”** serwera
- pasek z adresem
- adres jest **nieedytowalny poza ostatnim wpisem**

#### Klucz API

- napis **„Klucz API”**
- pole z kluczem
- klucz jest **zamaskowany**

#### Typ serwera

Combo zawierające:

- `llama.cpp`
- `Apertium `
- ` Chmura`
- puste pole edytowalne

---

### 2. Sekcja „Serwer llama.cpp - lokalny”

#### Port

- napis **„Port:”**
- pasek edytowalny
- zakres: **1111–99999**
- strzałki zmieniają wartość co **1**
- przycisk **„Losowy”** losuje port z zakresu 1111–99999

#### Obliczenia serwera

- napis **„Obliczenia serwera:”**
- wybór:
  - `CPU`
  - `GPU`

#### Model

- napis **„Model:”**
- pasek wyboru pliku
- przycisk **„Przeglądaj”**

#### Szablon czatu

- napis **„Szablon czatu:”**
- wybór:
  - `janji`
  - `chatml`
  - `TranslateGemma`

#### Wątki

- napis **„Wątki (pararell)”**
- pasek edytowalny
- zakres: **1–8**

#### Uruchamianie serwera

Checkbox:

- **„Uruchamiaj serwer razem z programem”**

#### Czyszczenie bufora

Checkbox:

- **„Czyść bufor po każdym tłumaczeniu”**

#### Restart procesu

Checkbox:

- **„Restart procesu po tłumaczeniu”**

#### Restart serwera

Przycisk:

- **„Restart serwera”**

---

# 5. B. Apertium

## 1. Sekcja „Tłumacz Apertium”

### Typ serwera

Combo zawierające:

- `llama.cpp`
- `Apertium `
- ` Chmura`
- puste pole edytowalne

### Czyszczenie bufora

Checkbox:

- **„Czyść bufor po każdym tłumaczeniu”**

### Restart procesu

Checkbox:

- **„Restart procesu po tłumaczeniu”**

### Restart procesu

Przycisk:

- **„Restart Procesu”**

### Opis

Pole tekstowe zawierające opis tłumaczenia przy pomocy par językowych oraz informacji o ich ograniczeniu.

Pole jest:

- nieedytowalne
- przeznaczone wyłącznie do informacji dla użytkownika

---

# 6. C. Chmurowe

## 1. Sekcja „Ustawienia API”

### Adres serwera

- napis **„Adres serwera”**
- pasek z adresem
- adres jest **nieedytowalny poza ostatnim wpisem**

### Klucz API

- napis **„Klucz API”**
- pole z kluczem
- klucz jest **zamaskowany**

### Typ serwera

Combo zawierające:

- `llama.cpp`
- `Apertium `
- ` Chmura`
- puste pole edytowalne

---

## 2. Sekcja „Serwer zewnętrzny”

### Model

Combo zawierające:

- `Cohere`
- `ChatGPT`
- `Codex`
- `Gemini Flash`
- `Gemini Flash Lite`
- `DeepSeek`
- `DeepL API Free`
- `MyMemory`
- `Microsoft Translator`
- `Mozhi`

### Zachowanie dla modeli innych niż Mozhi

Gdy **nie wybrano Mozhi**, widoczny jest:

- checkbox **„Restart procesu po tłumaczeniu”**

### Zachowanie dla Mozhi

Gdy **wybrano Mozhi**, dodatkowo widoczne są:

#### Serwis

Combo **„Serwis”**.

Lista ma pochodzić z aktualnego kodu V3 Mozhi.

#### Adres backendu

Combo **„Adres backendu”**.

Pierwsza pozycja:

- **„Auto”**

Znaczenie pozycji **„Auto”**:

> Program sprawdza, który serwer jest dostępny dla wybranego serwisu i wybiera najszybszy.

Pozycja „Auto” jest następnie uzupełniona listą konkretnych backendów Mozhi z V3.

#### Restart procesu

Checkbox:

- **„Restart procesu po tłumaczeniu”**

---

# 7. Mozhi — dane z V3

Źródłem prawdy dla aktualnej listy Mozhi jest kod V3:

`/home/frs/Projekty/agent-translator-v3/tlumacz/mozhi.py`

## Domyślna instancja

`https://mozhi.ducks.party`

## Lista instancji Mozhi

Aktualna lista znaleziona w V3:

1. `https://mozhi.aryak.me`
2. `https://translate.bus-hit.me`
3. `https://nyc1.mz.ggtyler.dev`
4. `https://translate.projectsegfau.lt`
5. `https://translate.nerdvpn.de`
6. `https://mozhi.ducks.party`
7. `https://mozhi.frontendfriendly.xyz`
8. `https://mozhi.pussthecat.org`
9. `https://mo.zorby.top`
10. `https://mozhi.adminforge.de`
11. `https://translate.privacyredirect.com`
12. `https://mozhi.canine.tools`
13. `https://mozhi.gitro.xyz`

## Serwisy / silniki Mozhi

Aktualny kod V3 definiuje sześć silników:

| Nazwa w GUI | ID API |
|---|---|
| DuckDuckGo | `duckduckgo` |
| Google | `google` |
| DeepL | `deepl` |
| Yandex | `yandex` |
| Reverso | `reverso` |
| MyMemory | `mymemory` |

### Ważne rozróżnienie

Starszy dokument badawczy `docs/archive/research/mozhi-endpoints.md` zawiera historyczną listę siedmiu silników, w której występuje również **LibreTranslate**.

Aktualny kod V3 `mozhi.py` ma jednak sześć pozycji i to on jest źródłem prawdy dla aktualnej listy w GUI:

- DuckDuckGo
- Google
- DeepL
- Yandex
- Reverso
- MyMemory

LibreTranslate nie należy dodawać do aktualnej listy GUI tylko na podstawie starszego dokumentu.

---

# 8. Mechanizm „Auto” Mozhi

V3 posiada mechanizm wyboru najszybszej dostępnej instancji.

Powiązane funkcje:

- `probe_instance(instance)`
- `probe_engine(instance, engine)`
- `probe_translation(instance, engine)`
- `_probe_instance_for_engine()`
- `select_fastest_instance(...)`

Mechanizm może:

1. sprawdzić dostępność instancji,
2. zmierzyć czas odpowiedzi,
3. przy wybranym silniku sprawdzić dostępność backendu,
4. wykonać test tłumaczenia,
5. wybrać najszybszą dostępną instancję,
6. użyć `DEFAULT_MOZHI_INSTANCE` jako fallbacku.

W V3 wybór „Auto” jest zapisywany jako wartość `auto`.

---

# 9. API Mozhi

V3 korzysta z endpointu:

`/api/translate`

Parametry tłumaczenia:

- `engine`
- `from`
- `to`
- `text`

Przykładowy schemat:

`GET {base_url}/api/translate?engine={engine}&from={source}&to={target}&text={text}`

---

# 10. Pomoc

## Język

po lewej stronie karty Pomoc znajduje sie pole wyboru:

- Polski 
- English
- Douch

## Motyw

na środku karty pomoc znajduje sie pole wyboru:

- Systemowy
- Ciemny
- Jasny

## O Programie

Po prawej stronie karty Pomoc znajduje się przycisk:

- **„O Programie”**

Kliknięcie otwiera popup.

Treść:

```
TŁUMACZ
Wersja: X.X.X
Program do tłumaczenia dokumentów z wykorzystaniem AI i graficznego interfejsu Qt.
Obsługuje lokalne i chmurowe backendy tłumaczenia, w tym llama.cpp, Apertium i (w przyszłości) inne.
Licencja MIT
```

## Pomoc podręczna

Pomoc podręczna ma własne zakładki z tematami pomocy.

Treść tematów jest podłączona do plików pomocy:

- `src/tlumacz/qml_gui/help.pl.md`
- `src/tlumacz/qml_gui/help.en.md`
- `src/tlumacz/qml_gui/help.de.md`

---

# 11. Zasady układu GUI

1. Nazwa aplikacji zawsze: **Tłumacz**.
2. Zakładki główne zachowują ustaloną kolejność.
3. Sekcje kart są rozdzielane poziomą linią, jeżeli specyfikacja karty tego wymaga.
4. Ustawienia zależne od backendu nie mogą być prezentowane jako wspólne ustawienia wszystkich backendów.
5. Dla Mozhi lista serwisów ma wynikać z aktualnego V3, a nie ze starszej dokumentacji.
6. „Auto” Mozhi oznacza automatyczny wybór dostępnej i najszybszej instancji.
7. Dokumentacja GUI jest źródłem kontraktu przed dalszym podłączaniem logiki.
8. Najpierw należy ustalić i zapisać układ karty, a dopiero potem podłączać jej zachowanie.

---

# 12. Mapowanie aktualnych plików QML

| Zakładka | Plik QML |
|---|---|
| Tłumaczenie | `TranslationPage.qml` |
| API i serwer | `ApiPage.qml` |
| Przełączniki | `ExtrasPage.qml` |
| Pomoc | `HelpPage.qml` |
| Główne okno | `Main.qml` |
| Most Python ↔ QML | `bridge.py` |

To mapowanie opisuje stan plików. Nazwa pliku `ExtrasPage.qml` nie jest nazwą użytkową karty.

---

# 13. Zasada dalszych prac

Przed dalszym podłączaniem GUI należy traktować niniejszy dokument jako kontrakt aktualnego układu.

Kolejność prac:

1. zatwierdzony układ GUI,
2. test kontraktu,
3. podłączenie właściwości i kontrolek bridge,
4. obsługa zależności od typu serwera,
5. obsługa Mozhi i mechanizmu „Auto”,
6. testy,
7. aktualizacja dokumentacji.


---

# 12. Stan integracji karty „Przełączniki” — 2026-10-03

Karta trzeciej zakładki jest podłączona do rzeczywistego runtime V4 przez QmlApplicationBridge.

Podłączenie obejmuje:

- AppSettings dla portu, autostartu, cache, restartu oraz ustawień Mozhi;
- TranslationApp dla zarządzania serwerem llama.cpp i cache tłumaczeń;
- BackendRequest dla wyboru backendu podczas tłumaczenia;
- aktywne profile chmurowe zgodne z kontraktem karty;
- aktualne instancje i silniki Mozhi z V3;
- akcje start/restart oraz automatyczny start llama.cpp;
- akcje po zakończeniu tłumaczenia: czyszczenie cache i opcjonalny restart zarządzanego llama.cpp.

## Ograniczenie techniczne portu

Interfejs operacyjny używa zakresu **1111–65535**, ponieważ zakres TCP kończy się na porcie 65535. Historyczny zapis 1111–99999 w specyfikacji został zachowany jako ślad wymagań, ale wartości powyżej 65535 nie mogą zostać użyte do uruchomienia serwera TCP.

## Apertium

Apertium nie posiada trwałego procesu serwera w aktualnym adapterze V4. Każde tłumaczenie uruchamia proces CLI dla danej jednostki. Przycisk „Restart procesu” nie wykonuje więc fikcyjnego restartu; bridge informuje użytkownika o tym modelu wykonania.

## Weryfikacja

Kontrakt bridge i powierzchni QML jest testowany w tests/test_qml_gui.py oraz tests/test_gui_regression_v3_v4.py. Integracja cache i lifecycle runtime jest testowana w tests/test_application_core.py.

---

# 7. Karta „Przełączniki” — dokładny kontrakt UI

## Sekcja „Glosariusz”

1. Pole wyboru pliku z napisem wewnątrz:
   **„Ścieżka do pliku glosariusza w formacie .cvs  (źródło  tłumaczenie)”**
   oraz przycisk **„Przeglądaj”**.
2. Dwa pola tekstowe:
   - **„Źródło”**
   - **„Tłumaczenie”**
   oraz przycisk **„Dodaj”**.
3. Status:
   - **„Brak pliku”**, gdy glosariusz nie jest załadowany;
   - po załadowaniu: **„XXXX - par wyrazów”**, gdzie XXXX jest liczbą niepustych wierszy pliku.

Plik jest traktowany jako CSV/CSV-like z parą źródło,tłumaczenie.

## Sekcja „Skille”

Stałe checkboxy:

- **„Text zwykły - TXT”**
- **„Markdown - md”**
- **„HTML/XHTML”**
- **„DOCX”**
- **„ODT”**
- **„ePUB”**
- **„PDF”**

Skille użytkownika:

- każdy plik skilla umieszczony w /home/frs/.config/tlumacz/skills pojawia się automatycznie w GUI;
- lista jest odświeżana automatycznie oraz ręcznie.

Przyciski:

- **„Importuj skilla...”**
- **„Utwórz skilla...”**
- **„Odśwież”**

## Sekcja „Ustawienia LMM”

- **„Rozmiar bloku:”** — edytowalny SpinBox, 500–8000, krok 500;
- **„Temperatura:”** — edytowalny SpinBox, 0.0–1.0, krok 0.1;
- **„Język docelowy:”** — lista kilkudziesięciu języków europejskich oraz możliwość wpisania własnej wartości;
- **„Własny prompt:”** — edytowalne pole z placeholderem:
  **„Opcjalny własny prompt tłumaczenia (zastępuje systemowy)”**;
- **„Pomijane linie (regex):”** — edytowalne pole z domyślnymi wzorcami:
  ^\s*---\s*$
  oraz
  ^\s*\*(name|license|author|metadata|version|tags|created|updated)\s*
- przycisk **„Przywróć domyślne”**;
- przycisk **„Zapisz ustawienia”**.

---

# 8. Karta „Pomoc” — ustawienia

Obok przycisku **„O Programie”** znajdują się dwa pola:

### Motyw

- **Systemowy**
- **Ciemny**
- **Jasny**

### Język

- **Polski**
- **English**
- **Deutsch**

Ustawienia te zostały przeniesione z karty „Przełączniki” do „Pomoc”.

---

# 9. Pamiętanie geometrii okna

Aplikacja zapisuje:

- pozycję X/Y;
- szerokość;
- wysokość.

Zapis jest wykonywany:

- po zmianie geometrii z krótkim opóźnieniem;
- ponownie przy zamykaniu aplikacji.

Przy następnym uruchomieniu zapisane wartości są przywracane, jeżeli są dostępne.


# 14. Uruchamianie aktualnego GUI QML

Aktualny kontrakt karty „Tłumaczenie” jest realizowany przez `TranslationPage.qml` i zachowuje kolejność:

1. Pliki — plik wejściowy, plik wyjściowy;
2. Postęp — pasek i procent;
3. Statystyki — czas i prędkość tłumaczenia;
4. Sterowanie — **Tłumacz**, **Anuluj**, **Język docelowy**;
5. **Log:**;
6. **Podgląd tłumaczenia:**.

Postęp oraz statystyki są umieszczone nad przyciskami sterowania, a pionowe odstępy górnej części karty są celowo zmniejszone, aby zwiększyć przestrzeń roboczą Logu i Podglądu.

Podczas weryfikacji 2026-10-03 stwierdzono, że globalny `/usr/bin/tlumacz` wskazuje zainstalowany pakiet `tlumacz` 0.31.2 i stary `tlumacz.qt_gui.app`. Nie jest to aktualny launcher V4 QML.

Aktualny GUI ze źródła uruchamia się z katalogu projektu przez:

```bash
cd /home/frs/Projekty/tlumacz-v4
python -m tlumacz.qml_gui.app
```

Test uruchomienia z katalogu projektu z `PYTHONPATH=src` potwierdza, że import prowadzi do `src/tlumacz/qml_gui/app.py`.

## 2026-10-03 — końcowa korekta GUI API/serwer, Przełączniki i Pomoc

- Uporządkowano cztery warianty backendu: llama.cpp, Apertium, Chmura i Własny.
- Skrócono pola wyboru, usunięto zbędne nagłówki i rozdzielacze oraz zwiększono czcionki na karcie API i serwer.
- Apertium otrzymał krótkie pole języka źródłowego i nieedytowalny opis ograniczeń backendu.
- Chmura obsługuje wybór Dostawcy oraz dodatkowe wybory Mozhi.
- Własny ma kolejność: adres serwera, klucz API, separator, typ serwera, nieedytowalny model.
- Skille użytkownika są automatycznie odświeżane, prezentowane obok skilli systemowych i mogą być usuwane przyciskiem ×.
- Utwórz skilla otwiera edytowalny szablon z instrukcją konstrukcji skilla.
- Język docelowy przeniesiono do Pomocy; Rozmiar bloku i Temperatura skrócono.
- W Pomocy pozostawiono wybór języka aplikacji, dodano wybór języka docelowego i poprawiono układ długich nazw zakładek.
- Motyw korzysta z jawnego SystemPalette dla trybu Systemowy.
- Pole Język docelowy na karcie Tłumaczenie skrócono o około połowę.

Weryfikacja: 265 testów zakończonych powodzeniem, compileall PASS.

## 2026-10-03 — korekta umiejętności użytkownika i kart backendów

W karcie **Przełączniki** przyciski Glosariusza zostały skrócone tak, aby **Przeglądaj** i **Dodaj** były w całości widoczne. Pola Rozmiar bloku i Temperatura mają jednakową szerokość 100 px. Nazwy obszarów **Glosariusz**, **Umiejętności** i **Ustawienia LLM** są pogrubione. Przy każdym skillu użytkownika jest przycisk **✕** do usunięcia.

W karcie **API i serwer** Apertium nie pokazuje pól adresu URL ani klucza API. Pozostają **Serwer** i wykryty język źródłowy w jednym wierszu, następnie separator i duży nieedytowalny panel informacyjny. Dla Mozhi pola adresu i klucza są nieaktywne; instancja ma tryb automatycznego wyboru najszybszej dostępnej instancji. Dla Własnego pozostają separator i duży nieedytowalny opis konfiguracji.

Metoda `newSkill()` w bridge zapisuje teraz niepusty szablon skilla zamiast odwoływać się do nieistniejącej metody.

## 2026-10-03 — dalsze skrócenie wierszy Glosariusza

W karcie **Przełączniki** oba wiersze sekcji **Glosariusz** rezerwują dodatkowe 38 px wolnego miejsca po prawej stronie. Odpowiada to około 10 mm przy typowym zagęszczeniu pikseli i zapobiega obcinaniu przycisków **Przeglądaj** oraz **Dodaj**. W drugim wierszu skrócenie rozkłada się na pola **Źródło** i **Tłumaczenie**, około 5 mm na każde pole.


### Drobna korekta Glosariusza i nagłówków sekcji — 2026-10-03
- Przycisk „Przeglądaj” ma szerokość zapewniającą pełny napis.
- Wiersze Glosariusza zachowują zarezerwowane miejsce na przyciski akcji.
- Nagłówki „Glosariusz”, „Umiejętności” i „Ustawienia LLM” są pogrubione.
- Separator nad sekcją „Umiejętności” pozostaje zachowany.


### Korekta pól Glosariusza i nagłówków — 2026-10-03
- Skrócenie dotyczy wyłącznie pól tekstowych, nie całego wiersza, dzięki czemu przyciski pozostają w pełnej szerokości.
- Pole ścieżki glosariusza ma rezerwę 38 px przed przyciskiem „Przeglądaj”.
- Pola „Źródło” i „Tłumaczenie” mają po 19 px rezerwy przed przyciskiem „Dodaj”.
- Pogrubienie jest ustawione wyłącznie na etykietach tytułów sekcji: Glosariusz, Umiejętności i Ustawienia LLM.


## 2026-10-03 — korekta pól Glosariusza

W karcie **Przełączniki** skrócenie pola ścieżki Glosariusza dotyczy wyłącznie pola tekstowego; wiersz zachowuje pełną szerokość, dzięki czemu przycisk **Przeglądaj** pozostaje pełnowymiarowy. Pogrubienie jest ograniczone do tytułów sekcji **Glosariusz**, **Umiejętności** i **Ustawienia LLM**.


## 2026-10-03 — finalna korekta szerokości pól Glosariusza

W sekcji **Glosariusz** długi pasek ścieżki pozostaje bez zmiany. Pola **Źródło** i **Tłumaczenie** skrócono dodatkowo o 5 mm każde względem poprzedniej wersji, przez zwiększenie ich rezerwy prawego marginesu z 19 px do 38 px. Przycisk **Dodaj** pozostaje pełnowymiarowy. Pogrubienie nadal dotyczy wyłącznie tytułów **Glosariusz**, **Umiejętności** i **Ustawienia LLM**.


## 2026-10-03 — wyrównanie przycisków i typografii sekcji Umiejętności

W karcie **Przełączniki** trzy przyciski akcji skilli (**Importuj skilla...**, **Utwórz skilla...**, **Odśwież**) mają wspólną szerokość 180 px i są wyrównane w jednym wierszu. Podtytuły **Skille systemowe** i **Skille użytkownika** pozostają czcionką normalną; pogrubienie jest zarezerwowane wyłącznie dla głównych tytułów sekcji.


## Korekta układu API i języków — 2026-10-04

- W widoku **API i Serwer** dla Apertium pozostaje jeden nagłówek „Ustawienia API”.
- Kolejność powierzchni Apertium: język źródłowy, język docelowy, separator, serwer, uwagi.
- Listy wyboru języków Apertium pozostają nieaktywne i mają stałą szerokość 90 px, ograniczoną względem wcześniejszego układu pełnej szerokości.
- Selektor serwera Apertium znajduje się bezpośrednio pod sekcją języków; globalny selektor serwera jest ukryty dla Apertium, aby nie dublować kontrolki.
- W widoku tłumaczenia Apertium języki są prezentowane jako: „Język - Źródłowy: [pole] Docelowy: [pole]”. Oba pola są nieedytowalne.


## 2026-10-05 — TranslationPage / Apertium
- W sekcji plików przyciski „Przeglądaj...” mają stałą szerokość 80 px.
- Pola ścieżek mają `Layout.minimumWidth: 0`, aby GridLayout nie wypychał przycisków poza prawą krawędź.
- Dla Apertium język źródłowy i docelowy są prezentowane w dwóch kolumnach, jako nieedytowalne pola tekstowe.
- Log i Podgląd mają jednakową wysokość 120 px, aby ograniczyć wysokość głównego widoku.
- Zmiana została zweryfikowana przez `qmllint` oraz testy `tests/test_qml_gui.py`; pozostał jeden niezwiązany błąd środowiska testowego dotyczący oczekiwanego domyślnego backendu (`cloud` zamiast `llama`).


## 2026-10-05 — korekta położenia języków Apertium
- Wybór języka źródłowego i docelowego przeniesiono do tego samego wiersza co przyciski **Start** i **Anuluj**.
- Nad polami wyświetlane są odpowiednio etykiety „Język wejściowy” i „Język docelowy”.
- Pola językowe są nieedytowalne i mają stałą szerokość 120 px, dopasowaną do długości napisów.


### Korekta układu sterowania Apertium — 2026-10-05
- Start, Anuluj, Język wejściowy i Język docelowy znajdują się w jednym wierszu.
- Etykiety językowe są nad odpowiadającymi im polami.
- Pola językowe są nieedytowalne i mają 120 px szerokości.


## 2026-10-06 — korekta źródła prawdy typografii karty „Tłumaczenie”

- bazowy rozmiar czcionki głównego okna QML wynosi obecnie **15 px**, zgodnie z `src/tlumacz/qml_gui/Main.qml`;
- kontrolki karty **Przełączniki** również używają 15 px, bez wymuszania `font.bold: false`;
- większe rozmiary pozostają jawne tylko tam, gdzie są elementem hierarchii wizualnej;
- wcześniejszy opis 17 px był historycznym stanem GUI i nie jest już aktualnym kontraktem.


## 2026-10-05 — kompaktowa karta Pomoc
- usunięto z karty Pomoc osobny wybór języka docelowego tłumaczenia; język docelowy pozostaje ustawieniem tłumaczenia, a Pomoc nie dubluje tego wyboru;
- skrócono szerokość wyboru języka programu oraz motywu; wybór języka programu pozostaje interaktywnym ComboBox;
- zakładki tematów Pomocy mają kompaktową wysokość i mniejszy tekst, z łamaniem nazw maksymalnie do dwóch linii;
- obszar treści Pomocy nadal zajmuje całą pozostałą powierzchnię okna.

- wybór motywu w karcie Pomoc dopasowuje szerokość do aktualnie wyświetlanego napisu.

- wybór motywu przełącza rzeczywistą paletę aplikacji dla trybów Systemowy, Ciemny i Jasny.

- pole Motyw w karcie Pomoc korzysta z szerokości tekstu aktualnie wyświetlanej pozycji, mierzonej przez `TextMetrics`, z dodatkowym miejscem na obramowanie i wskaźnik ComboBox; nie ma stałego `preferredWidth`.
- logo frsststems_logo_full.svg jest wyświetlane w prawym górnym obszarze wyskakującego okna „O Programie”, a nie w głównym oknie.

## 2026-10-05 — korekta motywu i wyboru serwera w lokalizacjach

- tryby **Ciemny** i **Jasny** korzystają z palety również dla własnych paneli QML; usunięto twardo zakodowane jasne kolory z panelu serwera własnego oraz zakładek Pomocy;
- zaznaczenie zakładki Pomocy korzysta z `palette.highlight` i `palette.highlightedText`, dzięki czemu pozostaje zgodne z aktywnym motywem;
- wybór serwera na karcie **API i serwer** przekazuje do bridge stabilny identyfikator wynikający z indeksu pozycji, a nie przetłumaczony napis;
- rozwiązanie obowiązuje niezależnie od języka interfejsu **Polski / English / Deutsch** i obejmuje oba selektory serwera, w tym wariant Apertium;
- zmiana języka interfejsu nie zmienia już identyfikatora backendu przekazywanego do logiki aplikacji.


## 2026-10-05 — automatyczny wybór skilla i przełączniki backendu

- po wskazaniu pliku wejściowego QML automatycznie odznacza pozostałe skille i zaznacza skill odpowiadający rozszerzeniu pliku;
- mapowanie obejmuje TXT/TEXT, Markdown, HTML/XHTML, DOCX, ODT, EPUB i PDF;
- skille użytkownika są odczytywane z pola `formats` w frontmatterze i mogą uczestniczyć w automatycznym wyborze;
- lista aktywnych skilli jest częścią `AppSettings` i jest zapisywana razem z ustawieniami GUI;
- karta „Przełączniki” zawiera osobną sekcję zachowania backendu z checkboxami dla llama.cpp, Chmury i Apertium: autostart, czyszczenie cache i restart procesu po tłumaczeniu zgodnie z zakresem backendu;
- typografia i odstępy kart Tłumaczenie/API/Pomoc zostały zmniejszone, aby interfejs był smuklejszy i mniej „widgetowy”.



## 2026-10-05 — zachowanie backendu przy właściwym serwerze

- checkboxy zachowania backendu nie należą do ogólnej karty **Przełączniki**;
- ustawienia dla **llama.cpp** są wyświetlane bezpośrednio w sekcji konfiguracji serwera llama.cpp na karcie **API i Serwer**;
- ustawienie restartu dla **Chmury** jest wyświetlane bezpośrednio w sekcji konfiguracji serwera chmurowego;
- ustawienia czyszczenia cache i restartu dla **Apertium** są wyświetlane bezpośrednio w sekcji konfiguracji lokalnego serwera Apertium;
- karta **Przełączniki** nie zawiera już tych checkboxów.

## 2026-10-07 — korekta rzeczywistego dziedziczenia motywu

Dokumentowany wcześniej kontrakt „wybór motywu przełącza rzeczywistą paletę aplikacji” został doprecyzowany po weryfikacji runtime. Dla zagnieżdżonych stron QML odwołania do kolorów mają korzystać z `ApplicationWindow.window.palette.*`, aby używać dokładnie tej palety, którą ustawia główne okno.

Dotyczy to powierzchni Pomocy oraz pozostałych kart korzystających z `palette.*`. Zapobiega to sytuacji, w której zmienia się tylko tło/dekoracja głównego okna, a treść pozostaje w schemacie jasnym.
