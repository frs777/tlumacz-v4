---
id: bug-history-2026-10-04
status: historical
meta:
  contentType: Audit
  category: audit
version: 1.0.0
updated: 2026-10-04
owner: project-maintenance
source: docs/BUG.md
depends_on: [docs/STATUS.md]
expires_when: dokumentacja historyczna projektu
last_validation: "wydzielenie historii BUG SentinelX 2026-10-04"
---

# Historia zamkniętych i migracyjnych wpisów BUG

Ten dokument zachowuje historyczne wpisy diagnostyczne wyjęte z aktywnego docs/BUG.md. Nie jest źródłem bieżącego statusu.

## 2026-10-01 — GUI: niewłaściwe zakładki / brak współczesnego backendu

- Status: zgłoszone, do reprodukcji.
- Objaw: w uruchomionym GUI widoczne są niewłaściwe zakładki/backendy; użytkownik zgłasza brak współczesnego backendu oraz obecność dwóch starszych backendów.
- Istotna obserwacja: źródłowy V4 definiuje backendy llama.cpp, Apertium, Chmura, natomiast znalezione stare GUI zawiera rekordy FastAPI (TranslateGemma) i OpenVINO z modelem TranslateGemma INT8.
- Hipoteza: uruchamiane GUI może pochodzić ze starej instalacji V3, ale wymaga to potwierdzenia przez launcher/interpreter/tlumacz.__file__.
- Referencja: GUI V3.2/V3 należy wykorzystać do porównania układu i zachowania interfejsu, bez mechanicznego kopiowania starej architektury backendów.
- Priorytet: P1.


## 2026-10-01 — GUI: brak wyboru Apertium w faktycznie uruchamianym V4

**Priorytet:** P1  
**Status:** OTWARTY / DO REPRODUKCJI

Użytkownik zgłasza, że w faktycznie uruchamianym V4 nie ma opcji wyboru Apertium. Źródłowy V4 `MainWindow` zawiera Apertium, dlatego trzeba ustalić rozbieżność między kodem a uruchomionym pakietem/launcherem. Nie uznajemy obecności wpisu w źródle za dowód dostępności funkcji w runtime.

## 2026-10-01 — Cloud: DLX nie został przeniesiony do V4

**Priorytet:** P1  
**Status:** OTWARTY

DLX jest wymaganym przez użytkownika backendem Cloud i ma pozostać w V4. Brak jego przeniesienia nie jest świadomym wycofaniem funkcji, lecz regresją migracyjną.

## 2026-10-01 — korekta wcześniejszej oceny GUI

Nie traktujemy jako regresji: autodetekcji źródła, ręcznego wskazywania pliku wyjściowego, osobnego języka źródłowego Apertium, Natywnego Jinja, ChatML, automatycznego startu llama.cpp ani zaznaczania/odznaczania skilli. Minimalny praktyczny rozmiar bloku pozostaje 500 znaków; wartości poniżej 500 nie są wymaganiem funkcjonalnym.


## 2026-10-01 — korekta wymagań: Własny endpoint i TranslateGemma

- **Własny endpoint/API:** V4 ma zachować możliwość użycia zewnętrznego serwera zgodnego z API, np. Ollama. Docelowo selector ma zawierać kategorię **Własny**, a po jej wyborze konfiguracja adresu ma być edytowalna.
- **TranslateGemma:** nie klasyfikować tej funkcji jako automatycznego startu llama.cpp. Chodzi o specjalny szablon/funkcję TranslateGemma dla kodów językowych innych niż wcześniejsze warianty.
- **SimplyTranslate:** funkcja zostaje wycofana z aktywnego V4. Połączenie nie zostało skutecznie zestawione ani razu; nie ma uzasadnienia dla dalszego utrzymywania providera, profilu Cloud i ustawienia silnika.


## 2026-10-01 — runtime V3 oraz sprzężenie backendów z MainWindow

### P0 — faktycznie uruchamiany program nie jest V4 — ZAMKNIĘTY

Przed naprawą systemowy `python` importował globalny pakiet V3 0.31.2. Dodanie repozytoryjnego shim-u `tlumacz -> src/tlumacz` rozwiązuje V4 przy uruchamianiu z katalogu projektu bez `PYTHONPATH`.

Weryfikacja: `python -m tlumacz --version` → 0.40.0; import GUI wskazuje V4; bootstrap 4 passed; pełny suite offscreen 201 passed.

Globalny V3 pozostaje nienaruszony.

### P1 — MainWindow: refaktoryzacja kompetencji rozpoczęta

src/tlumacz/qt_gui/main_window.py ma obecnie **790 linii**. W pierwszym etapie refaktoryzacji usunięto z niego bezpośrednie zależności od BackendRegistry, BackendSelection, adaptera llama.cpp oraz LlamaCppRuntimeManager.

Dodano:
- src/tlumacz/application/backend_service.py — fasada nad rejestrem aktywnych backendów;
- src/tlumacz/application/translation_app.py — rdzeń aplikacyjny składający backendy, tłumaczenie dokumentów i runtime llama.cpp;
- przekazanie rdzenia do MainWindow z composition root w qt_gui/app.py.

MainWindow nadal zawiera logikę prezentacji, konfiguracji kontrolek i worker Qt. Pozostałe kompetencje GUI (ustawienia, dokument, diagnostyka, postęp) wymagają dalszego wydzielenia; istniejące kontrolery nie zostały jeszcze włączone do tego przepływu.

Weryfikacja etapu:
- pełny pytest: **199 passed**;
- Ruff: **PASS**;
- compileall: **PASS**.

Refaktoryzacja jest kontynuowana. Nie oznaczamy BUG-007 jako zamkniętego, dopóki kompetencje MainWindow nie zostaną docelowo rozdzielone.



V4 posiada \`server_gguf_path\` w \`AppSettings\`, więc GGUF może być zapisany przez „Zapisz ustawienia”. Natomiast \`input_path\` i \`output_path\` nie są obecnie częścią \`AppSettings\`, więc ich trwałość po restarcie nie jest zaimplementowana. Jest to osobny błąd od problemu starego launchera.

Docelowo należy objąć trwałością ścieżki dokumentów oraz potwierdzić testem round-trip konfiguracji GGUF.

## 2026-10-01 — P0 launcher V3/V4 — naprawiony

Problem został potwierdzony i naprawiony na poziomie źródłowego uruchamiania V4. Przy `python -m tlumacz...` bez `PYTHONPATH` interpreter wybierał globalne `/usr/lib/python3.14/site-packages/tlumacz` 0.31.2. V4 korzysta obecnie z repozytoryjnego shim-u `tlumacz -> src/tlumacz`.

Weryfikacja:
- `python -m tlumacz --version` → `0.40.0`;
- `import tlumacz` → V4;
- `import tlumacz.qt_gui.app` → V4;
- testy bootstrapu bez `PYTHONPATH` → 4 passed;
- pełny suite `QT_QPA_PLATFORM=offscreen` → 201 passed.

Globalny V3 pozostaje nienaruszony. Problem budowania wheel związany z `dubious ownership` nadrzędnego drzewa Git pozostaje osobnym zagadnieniem packagingu.


## 2026-10-01 — P1 refaktoryzacja kompetencji GUI — postęp

`MainWindow` nie jest już właścicielem logiki wyboru backendu, ustawień, ścieżek dokumentów, postępu ani implementacji workera tłumaczenia. Kompetencje zostały przeniesione do osobnych prezenterów/komponentu workera.

Stan: **częściowo zamknięty**. Pozostaje rozdzielenie budowy zakładek GUI i diagnostyki.

Bieżąca długość `MainWindow`: **579 linii**. Pełny suite: **205 passed**.

## 2026-10-01 — doprecyzowanie kontraktu GUI na podstawie V3.2 i zrzutów

**Status:** USTALENIA REFERENCYJNE / DO WERYFIKACJI IMPLEMENTACJI

Poniższe ustalenia zastępują wcześniejsze nieprecyzyjne opisy GUI. V3.2 jest wersją referencyjną funkcjonalnie: V4 ma zachować zgodność funkcjonalną z V3.2, przy jednoczesnym usunięciu elementów architektury wycofanych w V4. Nie wolno traktować starego GUI jako źródła do mechanicznego przywracania wycofanych backendów.

### Kontrakt typu serwera

Selector „Typ serwera” ma zawierać dokładnie:

- „llama.cpp”
- „Apertium”
- „Chmura”
- „Własny”

**Apertium jest typem serwera, a nie modelem.** Dla Apertium nie należy budować pola „Model” analogicznego do llama.cpp.

### Kontrakt llama.cpp

Dla „llama.cpp” GUI ma udostępniać:

- **Obliczenia serwera:** „CPU” / „GPU”;
- **Model:** ścieżka do pliku modelu „GGUF”;
- **Szablon czatu:** „jinja” / „chatml” / „translategemma”;
- **Wątki równoległe:** zakres „1–8”;
- konfigurację cyklu życia serwera zgodną z funkcjonalnością V3.2.

„TranslateGemma” nie jest osobnym typem serwera. Jest rodziną/modelowym zastosowaniem oraz wartością specjalnego szablonu czatu „translategemma” dla llama.cpp.

### Kontrakt języka interfejsu

W zakładce „Pomoc” znajduje się wybór „Język / Language”. Zmiana tego wyboru ma przełączać **język całej aplikacji**, a nie tylko zawartość zakładki Pomoc.

### „O programie”

Funkcja **„O programie” już istnieje** w V4. Jej brak na dostarczonym zrzucie nie jest dowodem braku funkcji. Nie można wykonać reprezentatywnego zrzutu tej funkcji w stanie uruchomionego okna w obecnym materiale ekranowym; należy traktować to jako ograniczenie dokumentacji wizualnej, nie jako brak funkcjonalności.

### Wymóg zgodności z V3.2

Przy audycie GUI należy porównywać V4 z rzeczywistym kontraktem funkcjonalnym V3.2, w szczególności z układem i zachowaniem zakładek:

- „Tłumaczenie”
- „API i serwer”
- „Dodatki”
- „Pomoc”

Zrzuty z V3.2 są materiałem referencyjnym funkcjonalnie. Decyzje architektoniczne V4 pozostają nadrzędne wobec historycznych backendów V3, dlatego zgodność oznacza zachowanie wymaganej funkcjonalności, a nie przywracanie FastAPI/OpenVINO.

### Materiał referencyjny z audytu

Zaobserwowane na zrzutach V3.2 elementy obejmują m.in. dynamiczną konfigurację „API i serwer”, konfigurację llama.cpp z GGUF/chat template/parallel, konfigurację Cloud, funkcje glosariusza i skilli, ustawienia bloku/temperatury/języka/motywu/własnego promptu oraz pomoc aplikacji. Konkretne zachowanie V4 należy potwierdzać względem dokumentacji i kodu, a nie projektować od zera.


## 2026-10-01 — checkpoint kontraktu GUI: V3.2 → V4

**Status:** USTALENIA WIĄŻĄCE DLA DALSZEGO AUDYTU

- V3.2 jest wersją referencyjną funkcjonalnie. V4 ma zachować zgodność funkcjonalną z V3.2; migracja architektury V4 nie może być mylona z usuwaniem funkcji GUI.
- „Typ serwera” ma zawierać: **llama.cpp / Apertium / Chmura / Własny**.
- **Apertium jest typem serwera, nie modelem.** Nie należy pokazywać dla Apertium pola modelu llama.cpp.
- Dla llama.cpp: **Obliczenia serwera = CPU/GPU**; **Model = ścieżka/link do pliku GGUF LLM**; **Szablon czatu = jinja/chatml/translategemma**; **Wątki równoległe = 1–8**.
- Wybór języka pomocy w zakładce „Pomoc” zmienia **język całej aplikacji**.
- Przycisk/funkcja **„O programie” już istnieje**. Brak tej funkcji na zrzucie nie może być traktowany jako defekt funkcjonalny, ponieważ nie ma możliwości wykonania reprezentatywnego zrzutu dla uruchomionego programu. Jest to ograniczenie materiału wizualnego.
- Przy dalszym porównaniu GUI należy rozróżniać: **zgodność funkcjonalną z V3.2** od **elementów architektury V3, które są w V4 wycofane**.
- Nie wolno wyciągać wniosków o braku funkcji wyłącznie na podstawie braku elementu na dostarczonym zrzucie, jeżeli dokumentacja/kod potwierdza jego istnienie.

### Zasada prowadzenia dalszego audytu

Każde nowe ustalenie dotyczące GUI ma być zapisywane na bieżąco w dokumentacji projektowej. Konsultacja z użytkownikiem ma dotyczyć wyłącznie rzeczywistej decyzji projektowej, której nie da się rozstrzygnąć z V3.2, dokumentacji, kodu lub materiałów dowodowych.


## 2026-10-02 — korekta powierzchni GUI backendów i postępu

- Przy wyborze **Apertium** GUI nie pokazuje adresu URL/API ani kontrolek właściwych dla llama.cpp.
- Pole języka źródłowego nie jest wybieralne. Dla Apertium jest tylko wskaźnikiem języka; dla pozostałych backendów pozostaje ukryte.
- Przy wyborze **Własny** sekcja serwera pokazuje informację, że serwer należy uruchomić ręcznie, podać jego adres, a dostępne opcje zależą od sposobu uruchomienia serwera.
- Pasek postępu tłumaczenia jest widoczny na zakładce **Tłumaczenie** i pracuje w zakresie 0–100%.
- Etykieta ustawienia Prompt systemowy została zmieniona na **Własny prompt**.
- Aktualna implementacja GUI nadal jest oparta na **PySide6/Qt Widgets**. QML/Qt Quick nie został jeszcze wprowadzony; decyzję o ewentualnej migracji należy podjąć jako osobny etap architektoniczny po zamrożeniu kontraktu GUI.
- Nadal otwartą kwestią jest faktyczne przekazywanie wykrytego języka Apertium z mechanizmu autodetekcji do wskaźnika GUI; obecny kod zachowuje istniejące pole ustawienia jako źródło kompatybilności.


## 2026-10-02 — izolowany prototyp GUI Qt Quick/QML

Utworzono alternatywną warstwę GUI w osobnym katalogu `src/tlumacz/qml_gui/`. Prototyp zawiera osobne strony QML dla:
- Tłumaczenie,
- API i serwer,
- Dodatki,
- Pomoc.

Prototyp nie został podłączony do aktualnego `qt_gui` ani do głównego launchera. Dzięki temu obecne GUI Widgets pozostaje nienaruszone, a QML można rozwijać i porównywać niezależnie. Punkt wejścia testowy to `python3 -m tlumacz.qml_gui.app` z `PYTHONPATH=src`.


## 2026-10-02 — QML: uzupełnienie kontraktu Tłumaczenie i Dodatki

Izolowany prototyp QML został uzupełniony o czas tłumaczenia, bieżącą i średnią prędkość znaków/s, podgląd tłumaczenia, listę skilli systemowych i użytkownika z przełącznikami, zarządzanie skillami, Rozmiar bloku, Temperaturę, Własny prompt oraz Pomijane linie (regex). Element automatycznego źródła usunięto z powierzchni zakładki Tłumaczenie. Integracja z backendem pozostaje poza zakresem tego prototypu.


## 2026-10-02 — zamknięcie migracji GUI Widgets → QML

- Ryzyko równoległego utrzymywania dwóch interfejsów zostało zamknięte przez usunięcie `src/tlumacz/qt_gui/`.
- Główną warstwą prezentacji V4 jest teraz Qt Quick/QML, a komunikacja z rdzeniem odbywa się przez `QmlApplicationBridge`.
- Testy regresji GUI zostały przepisane z zależności od Qt Widgets na kontrakty QML/bridge.
- Pozostaje ryzyko dalszego dopracowania UX i pełnej weryfikacji pakietu instalacyjnego na czystym środowisku; nie jest to już równoległa ścieżka implementacyjna.

## 2026-10-02 — GUI QML: P0/P1 po podłączeniu runtime

### P0 — funkcjonalna korekta powierzchni GUI — W TRAKCIE

Objawy zgłoszone dla aktywnego QML:
- zbędne nagłówki „Tłumacz” i „V4 · Qt Quick”;
- ograniczenie minimalnego rozmiaru okna;
- brak trwałości pozycji/rozmiaru okna;
- prezentacja czasu jako 0:00/nieczytelnego pola czasu;
- kody języków zamiast pełnych nazw;
- checkboxy skilli zamiast informacji o katalogach;
- podwójny wybór języka w Pomocy;
- tekst Pomocy zastępowany treścią dotyczącą konfiguracji serwera;
- nieprawidłowa wersja prezentowana jako V4 zamiast 0.4.0.

Pierwsza fala tych problemów została objęta testami regresyjnymi i poprawiona. Pozostaje wizualny audyt rozmieszczenia kontrolek.

### P1 — karta API i serwer oraz geometria kart — OTWARTE

Układ i zachowanie aktywnej karty **API i serwer** wymagają osobnego omówienia. Nie należy przed tym etapem wykonywać kolejnej szerokiej przebudowy geometrii GUI.
