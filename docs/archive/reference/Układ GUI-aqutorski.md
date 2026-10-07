# UKLAD ELEMENTOW GUI

## Tłymaczenie:

### 1. sekcja "Pliki" 

- napis "Plik wejsciowy" pasek polozenia pliku przycisk "przeglądaj"
- napis "Plik wyjsciowy" pasek polozenia pliku przycisk "przeglądaj"
- przycisk "Tłumacz" przycisk "Anuluj"                                            pole wyboru "Język docelowy"
- pasek postempu z procentowa wartoscia wyswietlajaca sie podczas pobierania
- napis "czas" 00:00     napis "Prędkość tłumaczenia"  0/0   napis "znaki/s"

### 2. sekcja "Log:"

- okienko z wyswietlaniem komunikatow logow (patrz v3)

### 3. sekcja "Podglad tłumaczenia:"

- okienko z podgladem przetlumaczonego pliku 





# Serwer i API

Indywidualne ustawienia zaleznie od wybranego serwera
## A. llama.cpp

### 1. sekcja "Ustawienia API"

- napis "Adres URL" serwera pasek z adresem nieedytowalny poza ostatnim wpisem
- napis "Klucz API" zamaskowany klucz api
- napis "Typ serwera" okienko wyboru:  "llama.cpp" | "Apertium " | " Chmura" | puste pole edytowalne

### 2. sekcja "Serwer llama.cpp - lokalny"

- napis "Port:" pasek edytowalny z mozliwoscia pryjecia wartosci od 1111 do 99999 stralki zmioeniajace wartosc co 1  przycisk "Losowy" - losuje liczbe w podanym zakresie
- napis "Obliczenia serwera:" pole wyboru "CPU" | "GPU"
- napis "Model:" pasek wyboru pliku przycisk "Przegladaj"
- napis "Szablon czatu:"  pole wyboru "janji" | "chatml" | "TranslateGemma"
- napis "Wątki (pararell)"  pasek edytowalny z zakresem 1-8
- chekbox nzapis  "Uruchamiaj serwer razem z programem"
- chekbox napis "Czyść bufor po każdym tłumaczeniu"
- chekbox napis "Restart procesu po tłumaczeniu"
- przycisk "Restart serwera"

## B.  Apertium

### 1. sekcja "Tłumacz Apertium "

- napis "Typ serwera" okienko wyboru:  "llama.cpp" | "Apertium " | " Chmura" | puste pole edytowalne
- chekbox napis "Czyść bufor po każdym tłumaczeniu"
- chekbox napis "Restart procesu po tłumaczeniu"
- przycisdk "Restart Procesu"
- pole tekstowe z opisem tlumaczenia  przy p[omocy par jesykowych i o ich ogranioczeniu . nieedytrowalne

## C.  chmurowe

### 1. sekcja "Ustawienia API"

- napis "Adres serwera"  pasek z adresem nieedytowalny poza ostatnim wpisem
- napis "Klucz API" zamaskowany klucz api
- napis "Typ serwera" okienko wyboru:  "llama.cpp" | "Apertium " | " Chmura" | puste pole edytowalne

### 2. sekcja "Serwer zewnetrzny"

- napis "Model" okienko wyboru "Cohere" | "ChatGPT" | "Codex" | "Gemini Flash" | "Gemini Flash Lite" | "DeepSeek" | "DeepL API Free" | "MyMemory" | "Microsoft Translator" | "Mozhi"

    a. opcjalnie nie wybrano mozi 

- checkbox napis "Restart procesu po tłumaczeniu"

     b. wybrano mozii 

- napis "Serwis"  okienko wyboru lista serwisow mozi nie pamietam wsztstkich poszukac w kodzie v3
- napis "Adres backendu" okienko wyboru "Auto" (program sprawdza ktory serwer jest dostempny dla wybranego serwisu i wybiera najszybszy) | i tu lista bakendow mozi tez nie pamietam poszukac w kodzxie v3 
- checkbox napis "Restart procesu po tłumaczeniu"

# Przełaczniki

### 1.  sekcjs "Glosariusz"

- pole wybioerania pliku z napisem w srodku "Ścieżka do pliku glosariusza w formacie .cvs  (zródlo  tłumaczenie)" ,  pzrycisk "Przegladaj" 
- pole tekstowe z napisem w śrosku "Źródło" , pole tekstowe z napisem w śrosku "Tłumaczenie" przycisk "Dodaj"
- napis "Brak pliku" - gdy glosariusz zaladowany podaje  liczbe lini pliku "XXXX - par wyrazow"

### 2. sekcja "Skille"

- checkbox  "Text zwykły - TXT"
- checkbox  "Markdown - md"
- checkbox "HTML/XHTML"
- checkbox "DOCX"
- checkbox "ODT"
- checkbox "ePUB"
- checkbox "PDF"
- inne dodane skile uzytkownika pojawiaja sie automatycznie po ummieszczeniu pliku w odpowiednim folderze /home/frs/.config/tlumacz/skills
- przycisk "Importuj skilla..." przycisk "Utwórz skilla..." przycisk "Odśwież"

### 3. sekcja "Ustawienia  LMM"

- napius "Rozmiar bloku:" edytowalna linia  ze strzalkami  w zakresie od 500 do 8000 ze skokiem co 500
- napis "Temperatura:" edytowalna linia ze strzalkami z wartosciami od 0.0 do 1.0 skok co 0.1
- napis "Jezyk docelowy:"  pole wyboru jesyka Polski | Angielski | Nemiecki | itp kilkasnascie jezykow europejskicj  | puste pole z mozliwosciA WPISANIA JEZYKA 
- napis "Wlasny prompt:" Pole tekstowe edytowalne z Nap[isem wewnatrz "Opcjalny własny prompt tłumaczenia (zastepuje systemowy)
- napis "Pomijane linie (regex): " edytowalna linia tekstowa z wpisanym juz edytowalnym, tekstem "^\s*---\s\*$, ^\s\*(name|license|author|metadata|version|tags|created|updated)\s*"
- Przycisk "Przywróć domyślne"                                                         przycisk "Zapisz ustawienia"

# Pomoc

- przycisk "Język" programu przycisk "Motyw"                                        przycisk "O Programie" (uruchamia wyskakujace okienko)

- tresc okiernka: TŁUMACZ\ Wersja: X.X.X\  Program do tłumaczenia dokumentów z wykorzystaniem AI i graficznego interfejsu Qt. \   Obsługuje lokalne i chmurowe backendy tłumaczenia, w tym llama.cpp, Apertium i (w przyszłości) inne. \ Licencja MIT

- Pole Pomocy podrecznej (powinno zawierac wlasne zakladki z ruznymi tematami pomocy) podłaczone do pliku pompocy .
