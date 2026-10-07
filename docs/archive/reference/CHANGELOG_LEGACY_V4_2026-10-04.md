---
id: changelog-legacy-v4-2026-10-04
status: historical
meta:
  contentType: Changelog
  category: archive
version: 0.40.0
updated: 2026-10-05
owner: project-documentation
source: docs/CHANGELOG.md before 2026-10-05
depends_on: [docs/CHANGELOG.md]
expires_when: zastąpienie pełnej historii jednym kanonicznym changelogiem
last_validation: "przeniesienie starego changelogu po scaleniu źródła root 2026-10-05"
---

## [Unreleased] — 2026-10-04 — synchronizacja rdzenia, TranslateGemma i GUI

### Rdzeń / backendy
- `TranslationApp` zachowuje zarządzany runtime llama.cpp oraz otrzymał jawny restart z zachowaniem konfiguracji runtime;
- tryb `TranslateGemma` w llama.cpp korzysta z izolowanego detektora Lingua i kodów ISO 639-1, bez zmiany standardowego `/chat/completions`;
- starsze klucze `api_key` profili Cloud są przy odczycie przenoszone do `SecretStore`, a nowe profile nie wymagają zapisu sekretu w JSON;
- usunięto nieużywane kontrolery GUI; `BackendController` pozostaje aktywny.

Weryfikacja: **268 passed**, compileall — PASS, qmllint — PASS.

## [Unreleased] — 2026-10-03 — korekta czcionki, pola Rozmiar bloku i przycisków skilli

### GUI / karta „Przełączniki”
- zachowano czcionkę kontrolek karty na **15 px**; korekta dotyczyła **stylu**, nie zmniejszenia rozmiaru;
- zwiększono pole **Rozmiar bloku** z 100 px do **140 px**, tak aby bez obcinania mieściło wartości czterocyfrowe;
- przyciski **Importuj skilla...**, **Utwórz skilla...** i **Odśwież** mają wspólną szerokość **210 px**;
- szerokość przycisków pozostaje identyczna; przyciski i pozostałe kontrolki mają 15 px, natomiast **tytuły sekcji są pogrubione**, a pozostały tekst nie jest pogrubiony.

Weryfikacja: tests/test_qml_gui.py — **42 passed**; compileall — PASS.
## [Unreleased] — 2026-10-03

### GUI / karta „Przełączniki”
- Skrócono pola glosariusza tak, aby **ścieżka + Przeglądaj** oraz **Źródło + Tłumaczenie + Dodaj** mieściły się w szerokości karty.
- Skrócono lokalizowany placeholder ścieżki do **Plik glosariusza (.csv)** / odpowiedników EN i DE.
- Rozdzielono umiejętności na dwa równoległe podpola: systemowe i użytkownika.
- Zachowano przycisk **×** przy każdym skillu użytkownika.
- Zmniejszono czcionkę kontrolek do 15 px i dodano separatory zapobiegające zlewaniu się sekcji.
- Utrzymano przewijanie pionowe zamiast poszerzania karty.

## [Unreleased] — 2026-10-03 — losowanie portu i szerokość pola obliczeń

### GUI / karta „API i serwer”
- wyrównano szerokość pola **Obliczenia serwera** do pola **Port** (140 px);
- dodano obok pola Port przycisk **„Losuj port”**;
- przycisk korzysta z istniejącego mechanizmu `randomServerPort()` i losuje port z zakresu 1111–65535.

## [Unreleased] — 2026-10-03 — kolejność karty „API i serwer”

- Ustawiono separator po wyborze **Serwer** jako stały element karty, niezależnie od wybranego backendu.
- Zachowano wymaganą kolejność składników llama.cpp: **Port → Obliczenia serwera → Temperatura → Wątki (parallel) → Model → Restartuj serwer**.
- Dodano regresję struktury QML sprawdzającą kolejność i obecność stałego separatora.

## [Unreleased] — 2026-10-03 — typografia GUI

- Ustawiono bazowy rozmiar czcionki całego okna QML na 18 px.

## [Unreleased] — 2026-10-03 — finalizacja GUI

- Uporządkowano Apertium, Chmurę i Własny backend zgodnie z aktualnym kontraktem układu.
- Naprawiono zmianę profilu Chmury i obsługę profilu Mozhi w GUI.
- Skille użytkownika są automatycznie wykrywane, mogą być włączane/wyłączane i usuwane przyciskiem ×.
- „Utwórz skilla” korzysta z niepustego szablonu instrukcji.
- Skrócono kontrolki LLM oraz zwiększono rozmiar tekstu w pozostałych powierzchniach GUI.
- Przeniesiono wybór języka docelowego do Pomocy i poprawiono zawijanie długich nazw zakładek.
- Zmiana motywu jest natychmiast odzwierciedlana w palecie okna.

## [Unreleased] — 2026-10-03

### GUI / karta „API i serwer”
- Przebudowano układ `ApiPage.qml` dla llama.cpp do kolejności: **Ustawienia API → adres URL → klucz API → serwer → separator → port → obliczenia serwera → temperatura → Wątki (parallel) → model GGUF → Restartuj serwer**.
- Usunięto ramkę `GroupBox` i zbędny status/napisy z powierzchni llama.cpp.
- Skrócono kontrolki parametrów liczbowych i wyborów; zwiększono rozmiar tekstu kontrolek do 18 px.
- Pole **Model** korzysta teraz z wyboru pliku GGUF i przycisku **Przeglądaj**.

### Weryfikacja
- Dodano regresję struktury `ApiPage.qml` sprawdzającą kolejność wymaganych elementów i pojedynczy separator.

## 2026-10-03 — naprawa rzeczywistego układu karty „Tłumaczenie”

- usunięto dodatkowy nagłówek „Sterowanie tłumaczeniem”;
- usunięto separatory pomiędzy Sterowaniem, Postępem i Statystykami;
- pozostawiono separatory wyłącznie **Pliki → Log** i **Log → Podgląd tłumaczenia**;
- zachowano Tłumacz/Anuluj po lewej oraz Język docelowy po prawej w jednej linii;
- wymuszono czerwony wygląd przycisku Anuluj;
- wykonano backup `backups/translation-page-qml-expert-20261003/pre-translation-page.tar.gz`.

## 2026-10-03 — dokładna kolejność karty „Tłumaczenie”

- odwzorowano sześć sekcji w ustalonej kolejności;
- dodano separatory i nagłówki sekcji;
- dodano lokalizacje nagłówków PL/EN/DE;
- wykonano backup przed zmianą.

## 2026-10-03 — korekta karty „API i serwer”

- uporządkowano sekcję llama.cpp bez zmiany kolejności głównych kart;
- ścieżka GGUF jest teraz nad parametrami;
- skrócono pola Obliczenia serwera i Szablon czatu;
- przywrócono trzy checkboxy ustawień serwera;
- przycisk **Restartuj serwer** jest pełnoszeroki;
- `settings.model` jest prezentowane jako **Model**;
- dodano jawny status serwera przed akcją restartu;
- wykonano backup przed zmianą.

## 2026-10-03 — końcowa weryfikacja GUI

- pełny pytest: **261 passed**;
- compileall i Ruff: PASS;
- uruchomienie QML offscreen: PASS do kontrolowanego timeoutu;
- persystencja geometrii okna: PASS.
## 2026-10-03 — korekta karty „Przełączniki”

- trzecia karta otrzymała właściwą funkcję pomocniczą zamiast powielania konfiguracji „API i serwer”;
- dodano Glosariusz, Skille i Ustawienia LMM zgodnie z przekazaną specyfikacją;
- dodano języki europejskie oraz własny język docelowy;
- dodano domyślne regexy pomijania;
- Motyw i Język zostały przeniesione do Pomocy;
- poprawiono zapisywanie geometrii okna podczas zmian;
- wykonano backup przed zmianą.


## 2026-10-03 — weryfikacja karty „Serwer i API”

- zaktualizowano stare testy powierzchni QML, które nadal traktowały trzecią kartę jako „Dodatki/Parametry”;
- pełny pytest: **257 passed**;
- compileall: PASS;
- Ruff: PASS;
- smoke QML offscreen: kontrolowany timeout QML_EXIT:124, bez błędu startu.


## 2026-10-03 — funkcjonalne podłączenie karty „Serwer i API”

- podłączono trzecią kartę QML do AppSettings, TranslationApp i BackendRequest;
- dodano sterowanie portem llama.cpp, losowanie portu, CPU/GPU, GGUF, chat template i parallel 1–8;
- dodano autostart, czyszczenie cache po tłumaczeniu i restart zarządzanego llama.cpp;
- dodano konfigurację Apertium z jawną informacją o procesowym modelu wykonania;
- podłączono profile chmurowe oraz Mozhi z aktualnymi instancjami i silnikami V3;
- ograniczono listę modeli chmurowych do aktualnego kontraktu karty;
- dodano testy kontraktowe bridge, persystencji i akcji runtime;
- wykonano backup: backups/server-api-wiring-20261003/pre-server-api-wiring.tar.gz;
- weryfikacja częściowa: 37 testów GUI QML/regresji + 4 testy TranslationApp — PASS.

## 2026-10-03 — uporządkowanie nazwy karty i głównego układu GUI

- utworzono `docs/technical-docs/QML_GUI_LAYOUT.md` jako szczegółowy opis układu GUI;
- zapisano w nim kartę „Serwer i API” dokładnie według aktualnej specyfikacji, w tym ustawienia llama.cpp, Apertium, chmurowe oraz Mozhi;
- wpisano listę instancji i silników Mozhi znalezioną w V3;
- poprawiono etykietę karty z „Przełączniki” na „Serwer i API” w PL/EN/DE;
- nie kontynuowano dalszego podłączania logiki tej karty przed zapisaniem kontraktu GUI.


## 2026-10-03 — specyfikacja karty Przełączniki: llama.cpp

- zapisano kontrakt UI dla karty „Przełączniki” zależnej od wybranego serwera;
- opisano sekcję „Ustawienia API” oraz „Serwer llama.cpp - lokalny” wraz z zakresami portu i wątków;
- specyfikacja Apertium pozostaje otwarta do czasu podania przez użytkownika jej dokładnych kontrolek.

## 2026-10-03 — podłączenie API i serwera oraz Przełączników

- dodano jawne aliasy QML dla właściwości i slotów karty „API i serwer”;
- dodano jawne aliasy QML dla właściwości i slotów karty „Przełączniki”;
- zachowano istniejący układ kontrolek i ich kolejność — zmiana dotyczy warstwy połączenia QML ↔ bridge;
- test kontraktowy bridge potwierdza wszystkie wymagane właściwości i metody;
- suite: 250 passed.

## 2026-10-03 — finalizacja funkcjonalna kart Tłumaczenie i Pomoc

- podłączono akcje i stan karty Tłumaczenie przez jawne właściwości/metody QML bridge;
- podłączono O Programie oraz pięć tematów Pomocy podręcznej;
- treść Pomocy jest utrzymywana poza QML w plikach Markdown PL/EN/DE;
- dodano test runtime karty Pomoc;
- pełny suite po etapie: 249 passed.

## 2026-10-03 — GUI: Tłumaczenie i Pomoc

- ustawiono nazwę okna aplikacji na **Tłumacz**;
- ustalono kolejność zakładek: Tłumaczenie | API i serwer | Przełączniki | Pomoc;
- przebudowano kartę Tłumaczenie zgodnie z aktywną specyfikacją i kolejnością Pliki → Log → Podgląd tłumaczenia;
- dodano poziome separatory między sekcjami karty Tłumaczenie;
- dodano dialog „O programie” z wersją 0.40.0 i licencją MIT;
- dodano podręczną Pomoc z własnymi zakładkami tematów i plikami treści PL/EN/DE;
- dodano pliki pomocy do package-data.
## 2026-10-03 — GUI QML — integracja funkcjonalna

- dodano lokalizowany bridge `QmlApplicationBridge.tr()` dla tekstów PL/EN/DE;
- podłączono statyczne teksty czterech stron QML do kanonicznego systemu i18n;
- rozdzielono konfigurację klucza lokalnego llama.cpp od profili Cloud;
- przełączanie profili Cloud ładuje właściwy provider, endpoint, model i klucz API;
- stan przycisku llama.cpp korzysta z rzeczywistej właściwości `llamaServerRunning`;
- dodano regresje GUI/QML; weryfikacja etapu: **28 passed**.

## 2026-10-01 — P1 — dekompozycja MainWindow i trwałość ścieżek

- wydzielono `BackendPresenter`, `SettingsPresenter`, `DocumentPresenter`, `ProgressPresenter` i `TranslationWorker`;
- `MainWindow` zmniejszono z 819 do 579 linii;
- `TranslationApp` posiada kontrolery backendu, ustawień, dokumentu, postępu i diagnostyki;
- dodano `last_input_path` i `last_output_path` do `AppSettings`;
- potwierdzono round-trip ścieżek wejścia, wyjścia i GGUF;
- pełny suite: 205 passed; Ruff i compileall: PASS.

## 2026-10-01 — P0 launcher V4

- usunięto niejednoznaczność uruchamiania V4 ze źródła przez repozytoryjny shim `tlumacz -> src/tlumacz`;
- `python -m tlumacz --version` z katalogu projektu rozwiązuje V4 `0.40.0` bez `PYTHONPATH`;
- dodano testy regresyjne bootstrapu V3/V4;
- potwierdzono pełny suite: 201 passed, Ruff PASS, compileall PASS;
- globalny pakiet V3 `0.31.2` nie był modyfikowany.

## 2026-10-01 — Raport końcowy migracji V3 → V4

- dodano `docs/Raport_koncowy_migracji_v3-v4.md`;
- podsumowano przebieg faz 0–13, sukcesy, napotkane problemy i rozwiązane blokady;
- udokumentowano pozostające blokery finalnego release: Apertium `eng-pol`, Windows runtime, dependency closure i audyt licencji;
- potwierdzono stan lokalnego handoff freeze oraz Linux Release Candidate 0.40.0;
- potwierdzono, że V3 pozostaje nienaruszonym źródłem referencyjnym i że nie wykonano publikacji do GitHub.

## 2026-09-30 — Faza 13 — finalny handoff i freeze

- zamknięto lokalny handoff freeze dla bieżącego Release Candidate 0.40.0;
- udokumentowano artefakt, SHA-256, blokery F11/F12 i procedurę dalszego postępowania;
- wykonano backup dokumentacji przed zmianami;
- nie wykonano push do GitHub ani publikacji artefaktu;
- finalny release 0.40.0 pozostaje otwarty przez Apertium eng-pol, Windows oraz dependency/licencje.

## 2026-09-30 — Faza 12 — release 0.40.0 — release candidate

- przygotowano release candidate Linux dla wersji 0.40.0;
- pełny suite: 182 passed;
- compileall, Ruff i mypy: PASS;
- integration/E2E: 19 passed;
- clean install wheel bez zależności: PASS;
- dodano RELEASE_NOTES_0.40.0.md, MIGRATION_NOTES_V3_TO_V4.md i ROLLBACK_0.40.0.md;
- udokumentowano SHA-256 artefaktu: 161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835;
- Faza 12 pozostaje otwarta przez Windows i blokady packagingu Fazy 11;
- osobny słownik nie jest blockerem i nie jest elementem wbudowanego artefaktu.
## 2026-09-30 — Faza 11 — packaging — wznowienie

- staging przeniesiono do lokalnego `./temp`, bez zapisu poza dozwolonym drzewem V4;
- dodano zasoby Okapi i Java Filter Host do pakietu Python;
- dodano bundlowany runtime Apertium do wheel oraz zweryfikowano jego silnik 3.9.12;
- dodano `LICENSE`, `NOTICE` i zestaw tekstów licencyjnych w dystrybucji;
- wheel `tlumacz-0.40.0-py3-none-any.whl` zbudowano i zweryfikowano w clean venv;
- Java Filter Host z wheel przeszedł smoke test;
- pełny suite: 182 passed, Ruff PASS, mypy PASS;
- Faza 11 pozostaje otwarta: brak kompletnego `eng-pol.t1x.bin`, brak Windowsowego runtime'u oraz niedomknięty pełny audyt dependency/licencji.

## 2026-09-30 — Faza 11 — packaging — start

- rozpoczęto dependency closure dla artefaktu V4;
- wykonano backup przed zmianami: `.migration-backups/pre-packaging-phase11-20260930.tar.gz`;
- dodano do V4 kontrolowany runtime Okapi z V3 (`filtry/runtime`, 42 pliki, 22 MiB);
- wykryto blokadę budowania wheel przez `setuptools`/Git i własność repozytorium nadrzędnego;
- wykryto dodatkową blokadę budowania danych Apertium w stagingu `/tmp` z powodu uprawnień;
- Faza 11 pozostaje otwarta i zablokowana; nie oznaczono jej kryterium jako spełnionego.

## 2026-09-30 — Faza 10

- zamknięto Faza 10 — legacy removal po audycie zero-reference;
- potwierdzono brak FastAPI/OpenVINO w aktywnym kodzie, testach i konfiguracji V4;
- usunięto niespójność dokumentacji faz 9–10 w planie migracji;
- zaktualizowano STATUS i TODO;
- weryfikacja: 180 testów, Ruff i mypy — PASS.

# CHANGELOG V4

## 2026-09-30

### Faza 4 — LlamaCppBackend
- dodano adapter llama.cpp OpenAI-compatible;
- dodano health-check endpointu `/v1/models`;
- pełny suite V4: 61 passed.

### Faza 4 — LlamaCppBackend
- dodano runtime manager;
- dodano walidację własności procesu.

### Faza 4 — LlamaCppBackend
- dodano jawne timeouty startup/shutdown i readiness probe.

### Faza 4 — LlamaCppBackend
- zamknięto health-check, contract suite i E2E;
- rzeczywisty llama-server + model Jan-v3.5-4B-Q4_K_XL przeszedł smoke translation;
- pełny suite V4: 77 passed.

### Faza 4 — LlamaCppBackend
- domknięto cancellation przez V4 CancellationToken.

### Faza 5 — Cloud
- dodano CloudRouter i CloudRoute.

### Faza 5 — Cloud
- dodano runtime-checkable CloudProvider.

### Faza 5 — Cloud
- dodano migrację profili chmurowych V3 → V4 bez przenoszenia kluczy API.

### Faza 5 — Cloud
- dodano MozhiProvider i obsługę automatycznego wyboru instancji.

### Faza 5 — Cloud
- dodano test i egzekwowanie timeoutu requestu HTTP.

### Faza 5 — Cloud
- zamknięto klasyfikację błędów, izolację sekretów i contract tests.

### Faza 6 — Apertium
- dodano prywatny runtime Apertium 3.9.12 i discovery bez instalacji systemowej.

### Faza 6 — Apertium
- uzupełniono adapter Apertium zgodny z TranslationBackend.

### Faza 3
- dodano izolowany Java Filter Host;
- dodano wersjonowany klient JSON Lines;
- dodano filtr DOCX/OpenXML;
- dodano test round-trip DOCX przez Filter Engine;
- zamknięto wszystkie punkty Fazy 3.
- pełny suite V4: 58 passed.

## 2026-10-01 — Audyt inżynierski i naprawa jakościowa

- dodano raport audytu dokumentacji: docs/Audyt/AUDYT_DOKUMENTACJI_2026-10-01.md;
- dodano raport audytu kodu: docs/Audyt/AUDYT_KODU_2026-10-01.md;
- dodano plan naprawczy: docs/Plany/PLAN_NAPRAWCZY_AUDYT_2026-10-01.md;
- dodano raport bieżącej weryfikacji: docs/Testy/AUDYT_TESTY_2026-10-01.md;
- wykonano backup: .migration-backups/pre-audit-repair-20261001.tar.gz;
- naprawiono błędy Ruff;
- wyłączono regenerowalne artefakty z Ruff;
- ujednolicono aktywne ścieżki V4;
- zweryfikowano CLI na świeżym środowisku z wheel;
- potwierdzono blokadę Apertium eng-pol przez cas_sp.

## 2026-10-01 — naprawa regresji GUI/Cloud V3 → V4

- wykryto brak faktycznej warstwy Qt w V4 mimo istnienia kontrolerów GUI;
- wykryto utratę większości providerów Cloud V3;
- wykryto brak pełnej konfiguracji 12 profili Cloud;
- wykonano backup .migration-backups/pre-gui-cloud-repair-20261001.tar.gz;
- odtworzono GUI Qt jako adapter V4;
- przywrócono aktywne backendy GUI: llama.cpp, Apertium i Cloud;
- przywrócono providerów Cloud: OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate, SimplyTranslate, Mozhi i DLX;
- przywrócono 12 profili Cloud;
- odtworzono pola Mozhi/SimplyTranslate;
- FastAPI/OpenVINO pozostały wycofane;
- dodano regresję GUI i testy kompatybilności Cloud;
- pełny suite: 195 passed;
- Ruff: PASS;
- mypy: PASS;
- wheel 0.40.0 zbudowany poprawnie.

Raport niezgodności: docs/Audyt/AUDYT_REGRESJI_GUI_CLOUD_V3_V4_2026-10-01.md.
Raport naprawy: docs/Audyt/RAPORT_NAPRAWY_GUI_CLOUD_2026-10-01.md.

## 2026-10-01 — domknięcie audytu powierzchni UI

- porównano pełny zestaw objectName V3/V4;
- odtworzono aktywne elementy Dodatki/Pomoc;
- dodano glosariusz, zarządzanie umiejętnościami, język pomocy, O programie oraz output splitter;
- dodano test `tests/test_gui_surface_parity.py`;
- końcowy suite tego etapu: **196 passed**;
- Ruff, mypy, compileall i wheel: PASS.

## 2026-10-01 — zgłoszenie: serwer llama.cpp nie uruchamia się

- **Status:** zgłoszone, nierozpoznana przyczyna.
- **Komponent:** serwer/runtime llama.cpp.
- **Objaw:** serwer llama.cpp nie uruchamia się.
- **Klasyfikacja:** błąd funkcjonalny do reprodukcji i diagnozy.
- **Priorytet:** P1 — blokuje lokalny backend llama.cpp.
- **Przyczyna:** jeszcze nieustalona; nie zakładamy na tym etapie błędu konfiguracji, modelu, parametrów procesu ani środowiska.
- **Następny krok:** zebrać dokładny komunikat/log uruchomienia oraz ustalić, jaki executable, model i konfiguracja są faktycznie używane.


## 2026-10-01 — korekta macierzy Cloud i GUI

- wycofano SimplyTranslate z aktywnego V4: usunięto provider, profil Cloud, ustawienie silnika, kontrolkę GUI i test kontraktowy;
- potwierdzono, że DLX pozostaje wymaganym providerem Cloud i nie jest funkcją wycofaną;
- doprecyzowano wymaganie kategorii **Własny** dla zewnętrznych endpointów API, z edytowalną konfiguracją po jej wybraniu;
- doprecyzowano, że TranslateGemma jest specjalną funkcją/szablonem dla kodów językowych, a nie funkcją automatycznego startu llama.cpp.

## 2026-10-01 — wydzielenie rdzenia aplikacyjnego GUI

- dodano BackendService jako warstwę dostępu do aktywnych backendów;
- dodano TranslationApp jako rdzeń aplikacyjny dla tłumaczenia dokumentów i runtime llama.cpp;
- odłączono MainWindow od bezpośredniego importowania rejestru/backendów i runtime llama.cpp;
- zmieniono qt_gui/app.py na composition root;
- dodano test kontraktu rdzenia: tests/test_application_core.py;
- pełny suite: **199 passed**;
- Ruff: PASS;
- compileall: PASS.

Refaktoryzacja MainWindow pozostaje otwarta: kolejnym etapem jest wydzielenie konfiguracji/persistencji oraz wykorzystanie istniejących kontrolerów aplikacyjnych.


## 2026-10-01 — P1 — wydzielenie builderów widoków GUI

- dodano `src/tlumacz/qt_gui/view_builders.py` z czterema builderami zakładek;
- `MainWindow` zmniejszono z 579 do 253 linii bez zmiany kontraktu powierzchni GUI;
- test parytetu został dostosowany do nowej granicy modułowej;
- dodano test `test_gui_view_builders.py`;
- pełny suite: **206 passed**; Ruff i compileall: **PASS**;
- backup: `/home/frs/Projekty/agent-translator-v3/backups/tlumacz-v4-tab-builders-20261001/pre-tab-builders.tar.gz`.

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

## 2026-10-03

- korekta szerokości pól Glosariusza i parametrów LLM;
- pogrubienie nazw głównych obszarów karty Przełączniki;
- dodanie jawnego kasowania skilli użytkownika;
- uproszczenie powierzchni Apertium i Własnego w karcie API;
- zablokowanie pól URL/klucza dla Mozhi i ustawienie trybu instancji `auto`;
- naprawa `newSkill()` w bridge oraz test regresyjny operacji skilli;
- dodanie lokalizacji `custom.description`.

- skrócono oba wiersze Glosariusza, rezerwując około 10 mm miejsca dla przycisków; w drugim wierszu odpowiada to około 5 mm na pole Źródło i Tłumaczenie.


### 2026-10-03 — mikro-korekta Przełączników
- Poszerzono przycisk „Przeglądaj” w Glosariuszu, aby pełny napis był widoczny.
- Utrzymano miejsce dla przycisków akcji w wierszach Glosariusza.
- Pogrubiono nagłówki Glosariusz, Umiejętności i Ustawienia LLM.


### 2026-10-03 — poprawka mikro-układu Glosariusza
- Cofnięto ściskanie całych wierszy Glosariusza.
- Skrócono wyłącznie pola wejściowe przed przyciskami.
- Pogrubiono tylko tytuły trzech sekcji, bez propagowania pogrubienia na kontrolki wewnątrz.


## [Unreleased] — 2026-10-03 — korekta karty „Przełączniki”

- Przeniesiono rezerwę szerokości z całego wiersza ścieżki Glosariusza na samo pole tekstowe.
- Przycisk **Przeglądaj** zachowuje pełną szerokość kontrolki.
- Pogrubienie ograniczono do tytułów **Glosariusz**, **Umiejętności** i **Ustawienia LLM**.
- Dodano regresję struktury QML dla tej korekty.


## 2026-10-03 — finalna korekta pól Glosariusza w GUI QML

- Długi pasek ścieżki Glosariusza pozostawiono bez zmian.
- Pola **Źródło** i **Tłumaczenie** skrócono dodatkowo o 5 mm każde.
- Przycisk **Dodaj** zachowuje pełną szerokość.
- Pogrubienie pozostaje wyłącznie na tytułach sekcji **Glosariusz**, **Umiejętności** i **Ustawienia LLM**.
- Test kontraktu QML: **42 passed**; `compileall`: **PASS**.


## 2026-10-03 — wyrównanie przycisków skilli i korekta typografii

- Przyciski **Importuj skilla...**, **Utwórz skilla...** i **Odśwież** wyrównano do wspólnej szerokości 180 px.
- Usunięto niezamierzone pogrubienie podtytułów **Skille systemowe** i **Skille użytkownika**.
- Pogrubienie pozostaje wyłącznie na głównych tytułach sekcji.

## 2026-10-03 — typografia karty „Przełączniki”
- poprawiono renderowanie czcionki zgodnie z wymaganiem: pogrubienie jest jawnie zarezerwowane wyłącznie dla trzech głównych tytułów sekcji;
- pozostałe etykiety, pola, przyciski, checkboxy, spinboxy i teksty pomocnicze mają jawnie `font.bold: false`;
- dodano test regresyjny pilnujący tego rozdziału typografii.
