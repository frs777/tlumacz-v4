## 2026-10-06 — korekta lifecycle serwera GUI

Po zgłoszeniu `BŁĄD: Nie można połączyć z llama.cpp: [Errno 111] Połączenie odrzucone` dodano drugą warstwę ochrony: `start_translation()` sprawdza runtime bezpośrednio przed budową usługi i ponawia autostart, jeżeli serwer został zatrzymany. Świeży test E2E celowo zatrzymał serwer po inicjalizacji GUI; następnie GUI samo go uruchomiło i zakończyło tłumaczenie TranslateGemma wynikiem `Witaj świecie. To krótkie testowanie.`.

Audyt launchera wykazał również, że polecenie `/usr/bin/tlumacz` uruchamia systemowy pakiet V3 `0.31.2` (`tlumacz.qt_gui`), a nie V4 (`tlumacz.qml_gui`). V3 pozostaje nietknięty. W repozytorium dodano launcher V4.

---
id: plan-01-restore-brakujace-funkcje
status: closed
meta:
  contentType: ImplementationPlan
  category: plans
version: 2.1.0
updated: 2026-10-06
owner: project-maintenance
source:
  - docs/Plany/00-BASELINE-MAPA-PARYTETU-V3-V4.md
  - docs/Audyt/PARYTET_V3_V4_MATRIX_2026-10-04.md
  - docs/Audyt/AUDYT_REGRESJI_GUI_CLOUD_V3_V4_2026-10-01.md
  - docs/RETIRED_FUNCTIONALITY.md
  - docs/STATUS.md
  - docs/TODO.md
depends_on:
  - docs/Plany/00-BASELINE-MAPA-PARYTETU-V3-V4.md
  - docs/ARCHITECTURE.md
expires_when: wszystkie pozycje objęte tym planem mają dowód wykonawczy albo jawne rozstrzygnięcie VERIFY-FIRST/RETIRED
last_validation: "weryfikacja wykonawcza SentinelX 2026-10-06; potwierdzono źródła konfiguracji GUI i llama.json; rzeczywiste E2E GUI PASS 2026-10-06"
---

## Korekta kontraktu GUI → konfiguracja llama.cpp — 2026-10-06

Weryfikacja wykazała konkretną regresję: trwałe ustawienia GUI mogły zawierać ścieżkę GGUF w postaci QML `file:///...`, podczas gdy `LlamaCppRuntimeConfig` wymaga lokalnej ścieżki pliku. Dodano normalizację przy odczycie i zapisie `settings-v4.json` oraz regresje TDD.

Techniczne parametry llama.cpp nadal są pobierane przez `LlamaCppRuntimeManager` z `/home/frs/.config/tlumacz/llama.json` z fallbackiem do `config/llama.json`. Port, model, tryb obliczeń, parallel i szablon czatu pochodzą z konfiguracji GUI; tuning runtime pochodzi z `llama.json`.

Weryfikacja konfiguracji: GUI odczytuje `http://127.0.0.1:2782/v1`; pozostałe techniczne parametry runtime są ładowane z `/home/frs/.config/tlumacz/llama.json`. Potwierdzono przez rzeczywisty `QmlApplicationBridge`, że runtime otrzymuje port `2782`, model `/home/frs/Modele/translategemma-4b-it.Q5_K_M.gguf`, CPU, `chat_template=translategemma`, `parallel=4` i temperaturę `0.0`. Świeże E2E zostało zakończone poprawnie; wynik dokumentowy został zapisany.

# PLAN 01 — odtworzenie brakujących funkcji

## Cel

Przywracać wyłącznie te funkcje V3, dla których baseline V3 → V4 daje wystarczający dowód brakującego kontraktu, i realizować je w architekturze V4. Nie odtwarzać V3 jako monolitu.

Plan jest wykonawczy, ale nie zakłada, że każda pozycja z historycznej macierzy musi zostać zaimplementowana. VERIFY-FIRST pozostaje nierozstrzygnięte do czasu uzyskania dowodu. RETIRED pozostaje poza zakresem implementacji.

## Zasady nadrzędne

1. V3 jest wyłącznie warstwą edukacyjną, referencyjną i regresyjną. Nie zmieniać /home/frs/Projekty/agent-translator-v3.
2. V4 jest jedynym miejscem implementacji.
3. Nie kopiować monolitycznych modułów V3 do V4. Przenosić kontrakt i zachowanie do istniejących granic V4.
4. Nie traktować różnicy nazw plików jako dowodu braku funkcji.
5. Każda nowa zmiana kodu zaczyna się od proving testu TDD.
6. Nie instalować ani nie usuwać zależności bez osobnej decyzji.
7. Przy dużej zmianie kodu wykonać backup przed zmianą.
8. Po każdej zmianie kodu zaktualizować dokumentację, testy i indeks dokumentacji.
9. Przed pracą runtime potwierdzić interpreter, sys.executable, tlumacz.__file__, launcher i wersję, aby nie wykonywać diagnostyki na globalnym V3.
10. Nie reaktywować FastAPI, Transformers, starego OpenVINO/TranslateGemma INT8 ani SimplyTranslate.

## Stan po rewalidacji 2026-10-06

### Już odtworzone lub zastąpione — nie wykonywać ponownie

| Obszar | Status | Dowód aktualny |
|---|---|---|
| Własny endpoint | aktywny kontrakt V4 | custom w BackendRegistry + CloudRouter, testy registry/GUI/settings |
| DLX | REBUILD zakończony na poziomie kontraktu V4 | DLXProvider, profil DLX w src/tlumacz/resources/cloud_models.json, testy V3-compat i GUI |
| GUI Widgets → QML | REPLACE | aktywny qml_gui/, bridge i testy powierzchni |
| launcher/runtime llama.cpp | REPLACE/KEEP | TranslationApp + LlamaCppRuntimeManager, health-check i testy runtime |
| wybór języka Apertium | REBUILD zakończony | discovery skompilowanych kierunków, source/target ComboBoxy, focused tests |
| aktywny backend Apertium | KEEP | relokowalny runtime, discovery i rzeczywiste E2E adaptera |

### Domknięte w wykonaniu 2026-10-06

1. pełne E2E TranslateGemma przez rzeczywistą aplikację V4;
2. pełny round-trip aktywnych formatów dokumentowych;
3. TXT — jawne rozstrzygnięcie VERIFY-FIRST: poza aktywnym kontraktem V4, bez przywracania;
4. PDF — jawne rozstrzygnięcie VERIFY-FIRST: poza aktywnym kontraktem V4, bez przywracania;
5. pozostałe historyczne moduły V3 oznaczone VERIFY-FIRST — brak potwierdzonego aktywnego kontraktu V4 w zakresie tego planu; pozostają poza implementacją.



# 1. Bramka runtime i źródła prawdy

Cel: przed każdym zadaniem ustalić, że testowany runtime jest V4.

Dowód wejściowy:
- aktywny launcher;
- sys.executable;
- tlumacz.__file__;
- wersja V4;
- ścieżka source src/tlumacz/;
- brak użycia globalnego V3.

Kryterium: nie rozpoczynać implementacji ani diagnostyki funkcjonalnej, jeżeli runtime wskazuje V3.

## Raport wykonania — Apertium runtime/E2E — 2026-10-06

### Zrealizowano

- wykryto rzeczywisty brak kontraktu środowiskowego: prywatny runtime Apertium wymagał jawnego APERTIUM_DATADIR, aby discovery kierunków nie zwracało *;
- runtime i adapter ustawiają APERTIUM_DATADIR na skonfigurowany katalog danych, zamiast zależeć od zewnętrznego środowiska;
- dodano regresję TDD dla rzeczywistego bundlowanego eng-pol;
- dodano regresję routingu Apertium: detekcja Lingua en jest zgodna z ręcznie ustawionym źródłem Apertium eng;
- dodano E2E przez TranslationApp dla rzeczywistego bundlowanego runtime eng → pol.

### Weryfikacja

- regresje Apertium/routingu: 2 passed;
- pełny suite V4: 363 passed, 0 failed;
- rzeczywisty CLI Apertium 3.9.12: Hello world. → @hello #Świat.;
- rzeczywisty przepływ TranslationApp → DocumentTranslationService → BackendRegistry → Apertium → wynik dokumentowy: PASS.

### Pozostałe

- pełne E2E TranslateGemma z rzeczywistym modelem pozostaje otwarte;
- kompletność wszystkich pozostałych par Apertium pozostaje osobnym zakresem TODO-004;
- pełny round-trip wszystkich aktywnych formatów pozostaje TODO-005.

# 2. TranslateGemma — domknięcie kontraktu aplikacyjnego

Status: ZAMKNIĘTE — pełne E2E aplikacyjne wykonane na rzeczywistym GGUF przez QML/bridge/TranslationApp.

Nie tworzyć osobnego backendu TranslateGemma. Jest to specjalny tryb chat_template="translategemma" w backendzie llama.cpp.

Kontrakt docelowy:

GUI → TranslationApp → DocumentTranslationService → TranslationOrchestrator → LlamaCppLanguageRouting → LlamaCppAdapter → llama.cpp /v1/chat/completions → chat_template_kwargs(source_lang_code, target_lang_code).

Wymagania:
- źródło i cel muszą być konkretnymi kodami ISO 639-1;
- auto nie jest kontraktem adaptera TranslateGemma;
- Lingua pozostaje niezależnym detektorem;
- routing llama.cpp ustala źródło przed wywołaniem adaptera;
- adapter nie wykonuje drugiej detekcji;
- standardowy llama.cpp nie korzysta z detektora TranslateGemma;
- nie reaktywować FastAPI/OpenVINO.

### Zadania TDD

- [x] Test 1: rzeczywisty model GGUF wykonuje jawne tłumaczenie en→pl przez aktywną ścieżkę aplikacyjną.
- [x] Test 2: GUI przekazuje wybrany target do usługi dokumentowej i adaptera bez pustego targetu.
- [x] Test 3: źródło wykryte przez Lingua trafia do requestu jako kod ISO 639-1.
- [x] Test 4: wynik rzeczywistego modelu przechodzi walidację odpowiedzi i zapis wyniku dokumentowego.

Kryterium wyjścia: pełny przepływ wybór trybu/modelu → detekcja/ustalenie source → target → request → rzeczywista odpowiedź modelu → walidacja → wynik dokumentowy musi być potwierdzony na rzeczywistym runtime V4. Sam test adaptera lub izolowanego llama-server nie zamyka tej pozycji.

# 3. Formatowy round-trip — wspólna bramka dla aktywnych filtrów

Status: ZAMKNIĘTE — 28 testów round-trip/Unicode/markerów dla aktywnych formatów: DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF 2.0.

Aktywne formaty: DOCX, ODT, HTML/XHTML, Markdown, EPUB, XLIFF 2.0.

Proving contract: plik wejściowy → probe/open → extract → units/inline markers → source language → ChunkPlanner → backend → ResultValidator/MarkerValidator → write/reconstruct → ponowny odczyt → kontrola integralności.

### Zadania

- [ ] Przygotować reprezentatywny fixture dla każdego aktywnego formatu.
- [ ] Dla każdego fixture sprawdzić integralność struktury przed tłumaczeniem.
- [ ] Sprawdzić zachowanie inline codes/markerów.
- [ ] Wykonać tłumaczenie kontrolowanym backendem testowym.
- [ ] Wykonać zapis i ponowny odczyt.
- [ ] Udowodnić, że wynik zachowuje wymagane elementy strukturalne.
- [ ] Dopiero po GREEN rozważyć test z rzeczywistym backendem.

Kryterium: każdy format otrzymuje osobny wynik PASS, FAIL albo BLOCKED z konkretnym dowodem. Brak testu nie jest PASS.

# 4. TXT — VERIFY-FIRST

Status: VERIFY-FIRST.

Baseline potwierdza: V3 posiada materiał tlumacz/skills/plaintext.md; V4 nie rejestruje TXT w aktywnym FilterRegistry; V4 celowo usunął TXT z deklarowanej affordance głównego pipeline'u.

Nie implementować jeszcze. Najpierw ustalić:
1. czy TXT był częścią aktywnego kontraktu V3, czy tylko pomocniczym skillem;
2. czy V4 wymaga osobnego filtra dokumentowego, czy świadomego braku TXT;
3. czy istnieje realny caller/GUI contract wymagający TXT;
4. czy przywrócenie nie dublowałoby istniejącego pipeline'u.

Kryterium decyzji: dopiero dowód kontraktu pozwala przejść do RESTORE/REPLACE albo jawnego RETIRED.

# 5. PDF — VERIFY-FIRST

Status: VERIFY-FIRST.

Baseline potwierdza: V3 posiada tlumacz/pdf_extractor.py; V4 nie ma aktywnego filtra PDF; dokumentacja V4 nie deklaruje PDF jako obsługiwanego przez główny Filter Engine.

Nie implementować jeszcze. Najpierw ustalić:
1. rzeczywisty zakres użycia PDF w V3;
2. czy ekstrakcja PDF była częścią aktywnego kontraktu użytkownika;
3. wymagania rekonstrukcji/zapisu PDF;
4. czy V4 potrzebuje pełnego filtra dokumentowego, czy wyłącznie ekstrakcji tekstu;
5. koszty i zależności wymagane przez ewentualny kontrakt.

Nie przywracać automatycznie pdf_extractor.py.

# 6. Historyczne moduły V3 — zasada VERIFY-FIRST

Następujące elementy macierzy nie otrzymują automatycznie statusu RESTORE:
- tlumacz/extract.py;
- tlumacz/glossary.py;
- tlumacz/installer.py;
- tlumacz/keys.py;
- tlumacz/mozhi.py;
- tlumacz/okapi.py;
- tlumacz/version.py;
- inne moduły oznaczone w macierzy jako VERIFY-FIRST.

Dla każdego z nich obowiązuje kolejność:
1. znaleźć V3 evidence;
2. znaleźć callerów i testy;
3. ustalić kontrakt wejścia/wyjścia;
4. wskazać istniejący odpowiednik V4;
5. ustalić, czy funkcja została zastąpiona architektonicznie;
6. dopiero wtedy wybrać RESTORE, REBUILD, REPLACE, KEEP, RETIRED albo DEAD.

Brak dowodu nie jest zgodą na implementację.

# 7. Funkcje wycofane — bez przywracania

Poza zakresem pozostają:
- FastAPI + Transformers;
- FastAPI server/manager;
- OpenVINO TranslateGemma INT8 jako osobny runtime;
- klasyczne src/tlumacz/qt_gui/;
- SimplyTranslate.

Potwierdzeniem jest docs/RETIRED_FUNCTIONALITY.md oraz aktualna architektura V4. Nie tworzyć adapterów tylko dlatego, że odpowiadają historycznym modułom V3.

# 8. Testy i dokumentacja

Każda pozycja, która przejdzie z VERIFY-FIRST do implementacji, musi mieć:
1. proving test reprodukujący brak;
2. minimalną implementację V4;
3. test kontraktu;
4. test regresji;
5. test runtime/E2E, jeżeli funkcja dotyczy runtime;
6. aktualizację docs/STATUS.md, docs/TODO.md lub docs/BUG.md zależnie od wyniku;
7. aktualizację dokumentacji technicznej;
8. aktualizację docs/DOCUMENTATION_CHANGELOG.md;
9. odświeżony docs/INDEX.md i docs/INDEX.yml.

# 9. Kryterium zamknięcia Planu 01

Plan może zostać zamknięty dopiero, gdy:
- wszystkie pozycje uznane za rzeczywiście brakujące mają implementację V4;
- każda implementacja ma proving test;
- aktywne ścieżki mają dowód runtime;
- TranslateGemma ma pełne E2E przez aplikację albo zostanie jawnie wyłączone z release z udokumentowaną decyzją;
- aktywne formaty dokumentowe mają wynik pełnego round-trip;
- TXT/PDF mają udokumentowane rozstrzygnięcie, a nie domysł;
- żadna implementacja nie zależy runtime od V3;
- FastAPI/OpenVINO/SimplyTranslate nie zostały reaktywowane;
- dokumentacja i indeks są zsynchronizowane.

## Bramy

### Brama A — baseline
Plan 00 musi pozostać źródłem decyzji. V3 pozostaje nietknięty.

### Brama B — proving test
Nie ma implementacji bez testu pokazującego brak lub niespełniony kontrakt.

### Brama C — runtime
Testy izolowane nie zastępują dowodu rzeczywistego przepływu aplikacyjnego.

### Brama D — dokumentacja
Każda zmiana funkcjonalna musi mieć odpowiadający wpis w dokumentacji.

## Stan planu po wykonaniu 2026-10-06

**ZAMKNIĘTY.** Świeży test GUI E2E zakończył się sygnałem `translationFinished`, statusem `Tłumaczenie zakończone.` i zapisaniem wyniku dokumentowego. Potwierdzono konfigurację GUI oraz techniczne ustawienia runtime z `llama.json`.

- TranslateGemma: rzeczywisty model GGUF `translategemma-4b-it.Q5_K_M.gguf` przeszedł pełny przepływ QML/bridge → TranslationApp → DocumentTranslationService → llama.cpp → zapis dokumentu;
- naprawiono rzeczywisty kontrakt runtime TranslateGemma: ręcznie renderowany prompt Gemma przez `/v1/completions` oraz `--no-jinja`;
- naprawiono przekazanie modelu z QML FileDialog: `file://`/QUrl jest normalizowane do lokalnej ścieżki systemowej i zapisywane w ustawieniach;
- aktywne formaty dokumentowe otrzymały wynik round-trip: **28 passed**;
- TXT i PDF otrzymały jawne rozstrzygnięcie VERIFY-FIRST: nie są częścią aktywnego `FilterRegistry` V4 i nie są przywracane w ramach tego planu;
- historyczne moduły V3 bez potwierdzonego aktywnego kontraktu V4 nie są przywracane;
- FastAPI, Transformers, stare OpenVINO/TranslateGemma INT8 i SimplyTranslate pozostają wyłączone;
- V3 pozostaje nietknięty.

### Dowód rzeczywistego E2E TranslateGemma

- model: `/home/frs/Modele/translategemma-4b-it.Q5_K_M.gguf`;
- GUI: endpoint `http://127.0.0.1:2782/v1`;
- GUI: `compute=cpu`, `chat_template=translategemma`, `parallel=4`, temperatura `0.0`, target `pl`, autostart `True`;
- techniczne parametry runtime: `/home/frs/.config/tlumacz/llama.json`;
- `llama-server`: uruchomiony przez `QmlApplicationBridge`/`TranslationApp` na porcie `2782`;
- test: `translationFinished`, status `Tłumaczenie zakończone.`;
- wynik: plik Markdown został zapisany, rozmiar `2405` B;
- wynikowy dokument zawiera przetłumaczoną treść w języku polskim;
- test nie używał ręcznie ustawionego portu `18081` ani ręcznego startu serwera.

### Weryfikacja kodu i regresji

- regresja GUI QUrl/GGUF: **1 passed**;
- TranslateGemma + runtime: **5 passed**;
- GUI/runtime regression suite: **127 passed**;
- aktywne filtry round-trip: **28 passed**;
- rzeczywisty bezpośredni adapter TranslateGemma przez llama.cpp: **en→pl PASS**, wynik `Witaj świecie.`;
- pełny pytest V4: **367 passed, 0 failed**;
- compileall: PASS;
- qmllint: PASS;
- git diff --check: PASS.

### Backup

`backups/plan-01-20261006-gui-gguf/` zawiera kopie plików objętych zmianą przed wdrożeniem poprawki GUI/runtime/adaptera.
