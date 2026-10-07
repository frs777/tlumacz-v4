## 2026-10-07 — detekcja dokumentowa źródła i statystyki czasu/prędkości

### Detekcja języka llama.cpp

`LlamaCppLanguageRouting.resolve_chunk_source()` wykonuje detekcję dla bieżącej jednostki/chunka. Dla `source_language=auto` wynik detekcji jest przypisywany tej jednostce, a `ChunkPlanner` wymusza granicę przy zmianie kodu źródłowego. Dzięki temu ścieżka llama.cpp zachowuje obsługę dokumentów wielojęzycznych znaną z V3. Proste cytaty `"..."` są wyłączane z próbki detekcyjnej.

Przed detekcją usuwane są fragmenty zamknięte w prostych podwójnych cudzysłowach `"..."`. Cytat w obcym języku nie może więc zmienić języka źródłowego dokumentu. Cytat nadal pozostaje w materiale wejściowym przeznaczonym do tłumaczenia; jest wyłączony wyłącznie z próbki językowej.

Dla dokumentu około 2 tys. znaków, jednego języka i `chunk_size=4000` poprawna detekcja każdej jednostki powinna zwrócić ten sam kod źródłowy, więc planner nie ma podstaw do dzielenia dokumentu z powodu zmiany języka. Podział może nadal wynikać z rzeczywistego przekroczenia budżetu znaków lub innych jawnych reguł strukturalnych planera.

### Statystyki GUI

W `TranslationPage.qml` wartości czasu i bieżącej prędkości są wizualnie wyróżnione przez `uiBaseFontSize + 1` oraz `font.bold: true`. Prędkość jest prezentowana jako jedna wartość `currentSpeed` w znakach/s. `averageSpeed` pozostaje właściwością bridge'a do obliczeń/diagnostyki, ale nie jest łączona z `currentSpeed` w formacie `current/average` na powierzchni GUI.

## 2026-10-07 — jeden mechanizm lifecycle llama.cpp

W GUI wszystkie żądania startu/restartu llama.cpp przechodzą przez `QmlApplicationBridge._request_llama_server()`. Mechanizm przyjmuje opcjonalny callback `on_ready`, dlatego klient może zgłosić potrzebę uruchomienia serwera bez wykonywania pracy zależnej od serwera przed jego faktyczną gotowością.

Przepływ „Tłumacz” wykorzystuje ten kontrakt: jeżeli llama.cpp nie działa, rejestruje kontynuację tłumaczenia i kończy bieżące wywołanie. Po zakończeniu operacji serwera callback uruchamia właściwy etap tłumaczenia. Dzięki temu sygnał uruchomienia llama.cpp nie jest mylony z rozpoczęciem tłumaczenia.

Ten sam mechanizm obsługuje autostart, zmianę backendu, ręczny restart oraz restart po tłumaczeniu. Bezpośrednie wywołanie `TranslationApp.start_llama()` znajduje się tylko wewnątrz kolejki operacji serwera.

## 2026-10-07 — pomiar bazowej inferencji aktywnego llama.cpp

Bezpośredni request do aktywnego `127.0.0.1:29710/completion`, z tym samym kontraktem ręcznie renderowanego promptu TranslateGemma, został wykonany na CPU:

- tekst źródłowy: `Hello world.`;
- `max_tokens=32`;
- prompt: 35 tokenów wejściowych;
- wynik: `Witaj świecie.`;
- czas całego requestu: około `15,49 s`;
- ewaluacja promptu: `8,16 s`, około `4,29 tokena/s`;
- generowanie: `7,01 s`, około `0,57 tokena/s`;
- wygenerowano 5 tokenów;
- `finish_reason/stop`: poprawny EOS.

To potwierdza, że aktywna inferencja TranslateGemma na CPU jest sama w sobie wolna. Dodatkowo każdy z 17 osobnych requestów dla badanego dokumentu ponosi osobny koszt ewaluacji promptu. Wielokrotne requesty są więc mnożnikiem istniejącego kosztu CPU, a nie jedyną przyczyną opóźnienia.

Test większego pojedynczego requestu został wcześniej przerwany po 60 s bez odpowiedzi. Nie traktujemy tego jako timeoutu aplikacji, lecz jako dodatkowy dowód, że czas pojedynczej inferencji dla większego wejścia może przekraczać minutę.

Wniosek: dalsza optymalizacja powinna najpierw ograniczyć liczbę requestów przez agregację jednostek jednego chunka. Dopiero potem należy osobno badać parametry inferencji CPU i presję pamięci/swapu. Nie należy uznawać samego `chunk_size` za mechanizm kontroli liczby requestów.

## 2026-10-07 — diagnostyka rzeczywistej wydajności TranslateGemma na CPU

Diagnostyka została wykonana na żywym hoście przez SentinelX. Analiza dotyczy wyłącznie aktywnego runtime'u Tłumacza na porcie `29710`; wyłączona/historyczna binarka llama.cpp v3 nie jest traktowana jako przyczyna tego problemu.

### Stan runtime'u

- aktywny proces GUI: `python3 -m tlumacz.qml_gui.app`;
- aktywny serwer Tłumacza: bundled `src/tlumacz/backends/llama_cpp/native/linux-x86_64/llama-server`;
- endpoint: `http://127.0.0.1:29710`;
- model: `translategemma-4b-it.Q5_K_M.gguf`;
- tryb: CPU (`--n-gpu-layers 0`);
- runtime rzeczywiście działa z `--parallel 1`;
- `/health` zwraca `{"status":"ok"}`;
- `/slots` zwraca jeden slot i w stanie bezczynności `is_processing=false`.

### Presja pamięci

W chwili diagnostyki host miał około `15 GiB` RAM, z czego około `5,0 GiB` było dostępne, oraz około `34 GiB` zajętego swapu z `47 GiB`. Oznacza to istotną presję pamięci. Jest to czynnik wydajnościowy, ale nie jedyna przyczyna długiego tłumaczenia.

### Najważniejsze ustalenie: `chunk_size` nie jest liczbą requestów

Dla rzeczywistego pliku:

`pliki testowe/test_2000/test_2000_chars.md`

- rozmiar dokumentu: `2228` znaków;
- MarkdownFilter wyodrębnia `17` jednostek tłumaczeniowych;
- łączna liczba znaków wysyłanych do tłumaczenia: `905`;
- `ChunkPlanner(max_chars=4000)` tworzy z tych jednostek **1 chunk zawierający wszystkie 17 jednostek**.

Jednak `TranslationExecutor.execute()` przyjmuje listę jednostek i wywołuje `translate(...)` osobno dla każdej jednostki. W efekcie jeden logiczny chunk nie oznacza jednego żądania do llama.cpp:

`17 jednostek → 1 chunk → 17 osobnych requestów HTTP → 17 osobnych inferencji TranslateGemma`.

To jest potwierdzony defekt architektoniczny przepływu. Samo zwiększanie `chunk_size` nie naprawi tego problemu, ponieważ planner grupuje jednostki, ale executor nie agreguje ich do jednego requestu.

### Dlaczego „znaków/s” jest bardzo małe

W CPU TranslateGemma koszt nie jest liniowy w sensie „jeden znak = stały czas”. Model generuje tokeny autoregresyjnie, a każde żądanie ponosi również koszt własnego promptu. Dlatego wiele małych requestów powoduje powtarzanie narzutu promptu i inicjalizacji generacji. Dodatkowo przy wysokiej presji swapu każda inferencja może zostać jeszcze spowolniona przez pamięć wirtualną.

Obecna metryka `znaki/s` jest więc wskaźnikiem przepustowości całego przepływu dokumentowego, a nie „czasu potrzebnego na jeden znak”. Nie należy interpretować jej jako stałego kosztu pojedynczego znaku.

### Stan konfiguracji podczas diagnostyki

Aktywny `$HOME/.config/tlumacz/config.json` zawiera:

- `server_port=29710`;
- `server_compute_mode=cpu`;
- `server_chat_template=translategemma`;
- `server_parallel=4` jako wartość GUI, ale efektywny runtime CPU jest uruchamiany z `--parallel 1`;
- `chunk_size=4000`;
- `auto_start_server=true`;
- `restart_llama_after_translation=true`.

### Wniosek diagnostyczny

Główny znaleziony problem przepływu nie polega na tym, że `chunk_size` jest za mały. Problem polega na rozjechaniu kontraktu **„chunk” vs „request”**: filtr produkuje jednostki, planner grupuje je do chunków, lecz executor nadal wysyła każdą jednostkę osobno. Dla CPU TranslateGemma jest to szczególnie kosztowne.

Kolejna zmiana powinna być zaprojektowana jako osobny etap: **agregacja jednostek jednego chunka do jednego requestu llama.cpp**, z zachowaniem mapowania wyników na oryginalne jednostki, walidacji, cache i dokładnego zapisu Markdown. Przed implementacją wymagane są testy RED → GREEN oraz backup.

### Dowody SentinelX z 2026-10-07

- `llama-server` Tłumacza: port `29710`, CPU, `--parallel 1`;
- `/health`: `{"status":"ok"}`;
- `/slots`: jeden slot, bezczynny po zakończeniu bieżącej pracy;
- RAM: około `15 GiB` użyte, `5,0 GiB` dostępne;
- swap: około `34 GiB` użyte z `47 GiB`;
- dokument testowy: `2228` B, `40` linii;
- filtr: `17` jednostek / `905` znaków;
- planner: `1` chunk / `17` jednostek / `905` znaków.

## 2026-10-07 — dokładność pomiaru szybkości tłumaczenia

- Czas tłumaczenia jest mierzony monotonicznie od rozpoczęcia operacji do zakończenia całego dokumentu.
- Szybkość jest liczona na podstawie rzeczywiście przetworzonych znaków źródłowych i czasu trwania operacji/chunka.
- Wcześniej wynik był konwertowany przez int(...). Dla wolnego tłumaczenia CPU wartości poniżej 1 znaku/s były więc obcinane do 0.
- current_speed i average_speed są obecnie wartościami zmiennoprzecinkowymi zaokrąglanymi do dwóch miejsc po przecinku. Dzięki temu np. 39 znaków / 100 s jest raportowane jako 0,39 znaku/s, a nie 0.
- Pomiar szybkości nie jest deklarowany jako szybkość tokenów modelu. Adapter llama.cpp nie streamuje odpowiedzi, więc liczba przetworzonych znaków jest wiarygodnie znana po zakończeniu odpowiedzi/chunka.
- Test regresyjny pokrywa przypadek wolnego CPU, w którym szybkość jest mniejsza niż 1 znak/s.

## 2026-10-06 — lifecycle serwera, adres URL i pomijanie fragmentów

- Start i restart llama.cpp są wykonywane w osobnym `QThread`; wątek QML nie czeka synchronicznie na `wait_for_ready()` ani `stop()`.
- Kontrolka „Adres URL” dla llama.cpp jest aktywna wizualnie i ma `readOnly: true`; użytkownik widzi normalny tekst, ale nie może edytować endpointu. Endpoint wynika z hosta i pola „Port”.
- Wczytanie ustawień nie może już nadpisywać `server_port` wartością wyciągniętą ze starego `base_url`. Źródłem portu llama.cpp jest wyłącznie `settings.server_port`.
- `TranslateGemma` ma osobną wartość prezentacyjną w `bridge.chatTemplate`; wartość wewnętrzna pozostaje `translategemma`, dzięki czemu wybór w `ComboBox` nie wraca do pierwszej pozycji.
- `settings.skip_line_patterns` zostały podłączone do przepływu dokumentowego. Fragment pasujący do dowolnego wzorca regex jest przekazywany do wyniku bez wywołania backendu tłumaczącego.
- Nie traktujemy szybkości jako wiarygodnego pomiaru w trakcie pojedynczego requestu HTTP: adapter llama.cpp nie streamuje odpowiedzi, więc rzeczywista liczba przetłumaczonych znaków jest znana dopiero po zakończeniu odpowiedzi/chunka. Po zakończeniu chunka GUI wylicza znaki/s z rzeczywiście przetworzonych znaków.

## 2026-10-06 — przebieg komunikatów i animowany wskaźnik pracy tłumaczenia

`TranslationPage.qml` używa animowanego wskaźnika `translationWorkOrb` zamiast tekstowego etapu obok czasu i szybkości. Wskaźnik jest widoczny wyłącznie podczas aktywnego tłumaczenia, obraca się na osi oraz płynnie zmienia kolor i skalę. Tekst diagnostyczny pozostaje w Logu.

Bridge otrzymuje z warstwy aplikacyjnej osobne zdarzenia:
- `on_document_info(document_type, total, skipped)` — dokument wczytany, liczba jednostek i fragmentów pominiętych;
- `on_chunk_start(current, total)` — rozpoczęcie rzeczywistego chunka;
- `on_chunk_complete(current, total, characters)` — zakończenie chunka i skumulowana liczba znaków;
- `chunkFailed(current, total, message)` — błąd aktywnego chunka; zdarzenie jest emitowane przed ogólnym `failed`.

Po błędzie bloku GUI ustawia stan błędu, zatrzymuje wskaźnik i dopisuje do Logu komunikat `Błąd bloku X z Y: ...`. Nie emituje podsumowania sukcesu ani nie ustawia postępu na 100%.

Kolejność komunikatów w Logu jest następująca:
1. komunikaty uruchomieniowe, w tym start llama.cpp, jeżeli jest wymagany;
2. `Wybrano skill: ...`;
3. `Gotowy do tłumaczenia.`;
4. `Rozpoczęto tłumaczenie.`;
5. `Wczytano dokument: ...`;
6. `Ominięto ... fragmentów.`;
7. liczba bloków;
8. `Tłumaczenie bloku X z Y...` dla rozpoczętego chunka;
9. przy błędzie: `Błąd bloku X z Y: ...` i zakończenie stanu tłumaczenia;
10. przy sukcesie: podsumowanie liczby bloków, czasu i szybkości w znakach/s;
11. ścieżka zapisanego dokumentu;
12. opcjonalnie akcje końcowe.

`Rozpoczęto tłumaczenie.` jest emitowane wyłącznie przez `QmlApplicationBridge.start_translation()`; worker nie emituje drugiej kopii.

Port lokalnego llama.cpp jest przekazywany z `settings.server_port` przez GUI do `TranslationApp.start_llama()` i dalej do `LlamaCppRuntimeConfig`. W bieżącej konfiguracji V4 portem jest `2782`; nie istnieje w kodzie V4 stała `28783`.

Regresje:
- `test_qml_translation_surface_uses_animated_work_orb_without_text_stage`;
- `test_qml_translation_worker_reports_failed_chunk_without_success_status`;
- `test_qml_bridge_chunk_failure_is_terminal_and_not_success`;
- `test_translation_page_has_animated_work_orb_at_start_of_statistics_row`;
- `test_qml_bridge_translation_messages_are_emitted_in_requested_order`.

---

## 2026-10-06 — lifecycle llama.cpp przed tłumaczeniem

`QmlApplicationBridge.start_translation()` nie zakłada już, że proces uruchomiony podczas inicjalizacji GUI nadal istnieje. Dla backendu `llama` przed `build_translation_service()` wywoływany jest `_maybe_autostart_server()`, a następnie sprawdzany jest aktywny runtime. Jeżeli serwer został zatrzymany, aplikacja uruchamia go ponownie z aktualnych ustawień GUI oraz technicznego tuningu `llama.json`. Dopiero wtedy tworzony jest serwis tłumaczenia.

Ten mechanizm zabezpiecza przed błędem `[Errno 111] Połączenie odrzucone`, który występował, gdy endpoint `http://127.0.0.1:2782/v1` nie miał już procesu nasłuchującego.

Ważne: systemowe `/usr/bin/tlumacz` należy traktować jako launcher V3 `0.31.2`. V4 ma osobny launcher repozytoryjny `uruchom-tlumacz-v4.sh` oraz `Tlumacz-V4.desktop`, aby nie modyfikować V3.

## 2026-10-06 — źródła konfiguracji llama.cpp i normalizacja ścieżki GGUF

Kontrakt konfiguracji lokalnego llama.cpp ma dwie warstwy. `AppSettings` w `$HOME/.config/tlumacz/config.json` przechowuje stan GUI: backend, host, port, ścieżkę GGUF, tryb obliczeń, `chat_template`, `parallel` i autostart. `LlamaCppRuntimeManager` ładuje techniczne ustawienia llama.cpp z `$HOME/.config/tlumacz/llama.json`, a w przypadku braku pliku korzysta z `config/llama.json`.

QML `FileDialog` może przekazać lokalny plik jako `file:///...`. `load_settings()` i `save_settings()` normalizują taką wartość do lokalnej ścieżki systemowej, zanim zostanie użyta przez `TranslationApp.start_llama()`. Dzięki temu runtime nie otrzymuje URL-a Qt zamiast ścieżki GGUF.

Weryfikacja 2026-10-06: rzeczywisty `QmlApplicationBridge` odczytał endpoint GUI `http://127.0.0.1:2782/v1` oraz uruchomił `llama-server` z modelem `/home/frs/Modele/translategemma-4b-it.Q5_K_M.gguf`, CPU, `chat_template=translategemma`, `parallel=4` i temperaturą `0.0`. Techniczne parametry runtime pochodziły z `/home/frs/.config/tlumacz/llama.json`. Test zakończył się sygnałem `translationFinished`, statusem `Tłumaczenie zakończone.` i zapisaniem wyniku Markdown o rozmiarze `2405` B. To jest potwierdzone E2E GUI.

---
id: gui-zbior-praktycznej-wiedzy
status: active
meta:
  contentType: Reference
  category: technical
version: 1.0.0
updated: 2026-10-05
owner: GUI / dokumentacja techniczna
source:
  - src/tlumacz/qml_gui/Main.qml
  - src/tlumacz/qml_gui/TranslationPage.qml
  - src/tlumacz/qml_gui/ApiPage.qml
  - src/tlumacz/qml_gui/ExtrasPage.qml
  - src/tlumacz/qml_gui/HelpPage.qml
  - src/tlumacz/qml_gui/HelpMarkdownView.qml
  - src/tlumacz/qml_gui/bridge.py
  - src/tlumacz/qml_gui/config.py
  - src/tlumacz/qml_gui/app.py
  - tests/test_qml_gui.py
depends_on:
  - docs/AGENTS.md
  - docs/STATUS.md
  - docs/ARCHITECTURE.md
  - docs/technical-docs/QML_GUI_DESIGN.md
  - docs/technical-docs/QML_GUI_LAYOUT.md
  - docs/technical-docs/QML_GUI_TRANSLATION_CARD_SPEC.md
  - docs/technical-docs/functional-capabilities.md
expires_when: zmiana kontraktu aktywnego GUI QML, bridge albo sposobu persystencji konfiguracji
last_validation: "weryfikacja źródeł SentinelX 2026-10-05; potwierdzono aktualny układ Apertium i unikalność kluczy i18n; bez bezpośredniej weryfikacji widocznego okna"
---

# Tłumacz V4 — GUI: zbiór praktycznej wiedzy

## 1. Po co istnieje ten dokument

Ten dokument jest **kompendium wiedzy o rzeczywistym GUI QML V4**.

Ma odpowiedzieć na pytanie:

> **Jeżeli za kilka miesięcy ktoś otworzy projekt i będzie chciał wiedzieć, gdzie jest podpięta konkretna kontrolka, funkcja albo zachowanie GUI, to gdzie ma wejść i co ma przeczytać?**

Dokument opisuje przede wszystkim **powiązania**, a nie sam wygląd:

**kontrolka QML → właściwość/akcja bridge → stan konfiguracji → metoda aplikacyjna/backend → efekt/persystencja → test regresyjny**.

Nie traktować tego dokumentu jako zastępstwa dla kodu. Jeżeli kod, test i starsza dokumentacja są sprzeczne, pierwszeństwo ma aktualny kod i świeży wynik weryfikacji.

### Poziomy pewności używane w dokumencie

- **POTWIERDZONE KODEM** — bezpośrednio widoczne w aktualnym źródle.
- **POTWIERDZONE TESTEM** — istnieje test kontraktowy sprawdzający dane powiązanie.
- **NIEZWERYFIKOWANE RUNTIME** — kod istnieje, ale w tej dokumentacji nie potwierdzono bezpośrednio wyglądu na ekranie użytkownika.
- **OTWARTE / DO ZROBIENIA** — kod lub dokumentacja wskazuje brakującą funkcję albo świadomie pozostawiony etap.

---

# 2. Mapa GUI w jednym miejscu

Aktywny launcher QML:

`src/tlumacz/qml_gui/app.py`

Ładowany plik:

`src/tlumacz/qml_gui/Main.qml`

Główny most:

`src/tlumacz/qml_gui/bridge.py`

Konfiguracja trwała używana przez ten bridge:

`src/tlumacz/qml_gui/config.py`

Główne strony:

| Zakładka | QML | Główna odpowiedzialność |
|---|---|---|
| Tłumaczenie | `TranslationPage.qml` | pliki, język, start/anulowanie, postęp, log, podgląd |
| API i serwer | `ApiPage.qml` | wybór backendu i konfiguracja właściwa dla wybranego backendu |
| Przełączniki | `ExtrasPage.qml` | glosariusz, skille, parametry LLM i akcje ustawień |
| Pomoc | `HelpPage.qml` | pomoc, język aplikacji, motyw, „O programie” |

Komponent pomocniczy:

`HelpMarkdownView.qml` — wyświetlanie Markdown pomocy w trybie tylko do odczytu.

---

# 3. Najważniejsza zasada: GUI backendowe jest warunkowe

## 3.1 Gdzie jest wybierany serwer

W `ApiPage.qml` znajduje się wybór backendu.

Bridge wystawia:

- `bridge.backendTypes`;
- `bridge.backendType`;
- `bridge.setBackendTypeIndex(index)`;
- `bridge.setBackendType(value)`.

Stabilne ID backendów:

| Indeks | ID wewnętrzne | Etykieta GUI |
|---:|---|---|
| 0 | `llama` | llama.cpp |
| 1 | `apertium` | Apertium — serwer lokalny |
| 2 | `cloud` | Chmura |
| 3 | `custom` | Własny |

**Ważne:** logika aplikacyjna ma pracować na stabilnym ID, nie na polskiej/angielskiej nazwie widocznej w GUI.

Implementacja wyboru:

- `ApiPage.qml` → `onActivated: bridge.setBackendTypeIndex(currentIndex)`;
- `bridge.py` → `set_backend_type_index()`;
- `bridge.py` → `_set_backend_type_value()`.

Test kontraktowy:

`test_qml_backend_selection_uses_stable_ids_for_all_languages`.

---

# 4. Widoczność sekcji zależnych od backendu

To jest obecnie jedna z najważniejszych zasad GUI.

## 4.1 llama.cpp

W `ApiPage.qml`:

`visible: is("llama")`

Pokazywane są:

- separator;
- nagłówek serwera llama.cpp;
- port;
- losowanie portu;
- tryb obliczeń;
- szablon czatu;
- równoległość;
- model GGUF;
- zachowanie backendu llama.cpp;
- przycisk restartu serwera.

## 4.2 Apertium

W `ApiPage.qml`:

`visible: is("apertium")`

Pokazywane są:

- **pole wyboru języka źródłowego** — `ComboBox` oparty na `bridge.apertiumSourceLanguages`;
- **pole wyboru języka docelowego** — `ComboBox` oparty na `bridge.targetLanguages`;
- separator;
- wybór serwera Apertium;
- uwagi/opis Apertium;
- zachowanie backendu Apertium.

Zmiana języka źródłowego wywołuje `bridge.setSourceLanguage(currentText)`, a zmiana języka docelowego `bridge.setTargetLanguage(currentText)`. Aktualne etykiety początkowe są wyznaczane przez `bridge.sourceLanguageLabel` i `bridge.targetLanguageLabel`.

Ogólny selector serwera z początku strony jest dla Apertium ukryty, a Apertium ma własny selector w swojej sekcji.

## 4.3 Chmura

W `ApiPage.qml`:

`visible: is("cloud")`

Pokazywane są:

- provider/profil Cloud;
- dla Mozhi dodatkowo silnik;
- dla Mozhi dodatkowo instancja;
- zachowanie backendu Chmura.

## 4.4 Własny

W `ApiPage.qml`:

`visible: is("custom")`

Pokazywany jest opis backendu Własny.

GUI nie udaje, że zarządza procesem lokalnym dla backendu Własny.

## 4.5 Dlaczego to jest ważne

Kontrolka należąca do konkretnego backendu **nie powinna być przenoszona do ogólnej sekcji tylko dlatego, że technicznie używa tej samej właściwości bridge**.

Aktualny wzorzec jest:

> wybierz backend → pokaż tylko jego powierzchnię konfiguracji.

To jest kontrakt UX i powinno być traktowane jako regresja, jeżeli kontrolka backendowa zacznie pojawiać się przy niewłaściwym backendzie.

---

# 5. Checkboxy zachowania backendów

## 5.1 llama.cpp

W `ApiPage.qml`:

`objectName: "llamaBackendBehavior"`

Zawiera:

- **Automatycznie uruchamiaj serwer**;
- **Czyść cache po tłumaczeniu**;
- **Restart serwera llama.cpp po tłumaczeniu**.

Powiązania:

| GUI | Bridge |
|---|---|
| `autoStartServer` | `bridge.autoStartServer` / `setAutoStartServer()` |
| `cacheClearAfterTranslation` | `bridge.cacheClearAfterTranslation` / `setCacheClearAfterTranslation()` |
| `restartLlamaAfterTranslation` | `bridge.restartLlamaAfterTranslation` / `setRestartLlamaAfterTranslation()` |

Restart llama.cpp działa wyłącznie dla zarządzanego przez aplikację runtime'u llama.cpp.

## 5.2 Chmura

W `ApiPage.qml`:

`objectName: "cloudBackendBehavior"`

Widoczny tylko przy Cloud.

Zawiera:

- **Ponowne połączenie z serwerem chmurowym po tłumaczeniu**.

Powiązania:

| GUI | Bridge |
|---|---|
| `reconnectCloudAfterTranslation` | `bridge.reconnectCloudAfterTranslation` / `setReconnectCloudAfterTranslation()` |

Po wykonaniu tłumaczenia warstwa Cloud jest odświeżana. Ponieważ aktywne adaptery Cloud wykonują żądania HTTP bez trwałego połączenia utrzymywanego przez GUI, kolejne żądanie zestawia nowe połączenie.

## 5.3 Apertium

W `ApiPage.qml`:

`objectName: "apertiumBackendBehavior"`

Widoczny tylko przy Apertium.

Zawiera:

- **Czyść cache po tłumaczeniu**;
- **Restart usługi Apertium po tłumaczeniu**.

Powiązania:

| GUI | Bridge |
|---|---|
| `cacheClearAfterTranslation` | `bridge.cacheClearAfterTranslation` / `setCacheClearAfterTranslation()` |
| `restartApertiumAfterTranslation` | `bridge.restartApertiumAfterTranslation` / `setRestartApertiumAfterTranslation()` |

Restart usługi odświeża instancję backendu Apertium przed kolejnym użyciem. Aktualny adapter Apertium uruchamia proces tłumaczenia osobno dla żądania, więc nie jest to restart jednego stale działającego procesu serwera.

### Ważne zastrzeżenie

Checkboxy restartu/reconnectu są teraz **niezależne per backend**:

- `settings.restart_llama_after_translation`;
- `settings.restart_apertium_after_translation`;
- `settings.reconnect_cloud_after_translation`.

Wspólne pozostaje tylko **Czyść cache po tłumaczeniu**.

Stara wspólna flaga `restart_after_translation` jest przy odczycie konfiguracji migrowana do odpowiedniego nowego pola na podstawie zapisanego typu backendu.

Test rozmieszczenia:

`test_qml_backend_option_checkboxes_are_bound_to_each_backend_section`.

### Aktualny układ pionowy akcji backendu

- **llama.cpp**: checkboxy zachowania są wyrównane do lewej i znajdują się na dole sekcji; przycisk **Restart serwera** znajduje się bezpośrednio pod nimi, na samym dole zakładki;
- **Apertium**: nagłówek **Zachowanie backendu** znajduje się nad polem informacyjnym, a pole tekstowe rozciąga się na pozostałą wysokość sekcji; checkboxy są wyrównane do lewej i pozostają na dole;
- **Chmura/Mozhi**: nagłówek **Zachowanie backendu** znajduje się nad informacją o trybie `auto`; pole tekstowe może wykorzystać pozostałą wysokość sekcji, a checkbox ponownego połączenia jest wyrównany do lewej i znajduje się na dole.

Układ wykorzystuje `ColumnLayout`, `Layout.fillHeight` i `Layout.alignment`, dzięki czemu obszar informacyjny przejmuje wolną przestrzeń, a kontrolki akcji pozostają przy dolnej krawędzi.

---

# 6. Zakładka „Tłumaczenie”

Plik:

`src/tlumacz/qml_gui/TranslationPage.qml`

## 6.1 Plik wejściowy

Kontrolka:

- `TextField` z `bridge.inputPath`;
- przycisk **Przeglądaj...**;
- `FileDialog`.

Akcja:

`bridge.setInputPath(selectedFile)`

Bridge:

`set_input_path()`

Dodatkowy efekt:

`set_input_path()` uruchamia automatyczny wybór skilla na podstawie rozszerzenia pliku.

Czyli przepływ:

**wybór pliku → `set_input_path()` → `_auto_select_skill_for_input()` → aktualizacja aktywnych skilli.**

To jest istotne: wybór pliku nie jest wyłącznie zmianą tekstu w polu.

## 6.2 Plik wyjściowy

Kontrolka:

- `TextField` z `bridge.outputPath`;
- przycisk **Przeglądaj...**;
- `FileDialog.SaveFile`.

Akcja:

`bridge.setOutputPath(selectedFile)`.

Jeżeli ścieżka wyjściowa nie była wcześniej ustawiona, `set_input_path()` może wyprowadzić ją automatycznie na podstawie nazwy pliku wejściowego i języka docelowego.

## 6.3 Język docelowy

Dla zwykłych backendów:

- `ComboBox`;
- model: `bridge.targetLanguages`;
- wartość: `bridge.targetLanguage`;
- etykieta: `bridge.targetLanguageLabel`;
- zmiana: `bridge.setTargetLanguage(currentText)`.

Ważne: bridge normalizuje etykietę lokalizowaną do kodu języka.

## 6.4 Apertium w zakładce Tłumaczenie — stan rzeczywisty

**Stan aktualnego kodu, potwierdzony bezpośrednio w `TranslationPage.qml`:** pola Apertium są nadal umieszczone w tym samym `RowLayout` co przyciski **Tłumacz** i **Anuluj**.

GUI pokazuje:

- **Język źródłowy** — `TextField`, `readOnly: true`;
- **Język docelowy** — `TextField`, `readOnly: true`.

Powiązania:

- `bridge.sourceLanguageLabel`;
- `bridge.targetLanguageLabel`.

Nie ma obecnie bezpośredniego, użytkownikowego wyboru języka źródłowego Apertium na karcie **Tłumaczenie**. Nie ma tam `ComboBox` opartego na `bridge.apertiumSourceLanguages`.

Bridge posiada jednak mechanizm przygotowany pod wykrywanie źródeł:

- `_apertium_source_options()`;
- `apertiumSourceLanguages`;
- `set_source_language()` / `setSourceLanguage()`.

`_apertium_source_options()` korzysta z `discover_supported_pairs(Path.home() / ".config" / "tlumacz" / "Apertium")`, więc warstwa bridge potrafi zbudować listę wykrytych kodów źródłowych. **Sam aktualny QML nie udostępnia tej listy jako kontrolki wyboru.**

To rozróżnienie jest ważne: **mechanizm w bridge istnieje, ale bezpośredni selector źródła w bieżącym GUI nie istnieje.**

### Położenie pól

Pola językowe są obecnie częścią `translationControlsSection`, czyli tego samego wiersza, w którym znajdują się przyciski sterowania. Wcześniejsze wpisy opisujące osobny wiersz języków są historyczne i nie powinny być traktowane jako stan wdrożony.

Jeżeli docelowym wymaganiem będzie osobny wiersz językowy, jest to nadal zadanie do wykonania w `TranslationPage.qml`.

## 6.5 Przyciski Tłumacz / Anuluj

`TranslationPage.qml`:

- `translateButton`;
- `cancelButton`.

Tłumacz:

`bridge.startTranslation()`.

Anuluj:

`bridge.cancelTranslation()`.

Stan aktywności:

- Tłumacz jest wyłączony podczas tłumaczenia;
- Anuluj jest aktywny podczas tłumaczenia.

## 6.6 Start tłumaczenia — pełny łańcuch

Najważniejszy przepływ:

**QML**

→ `bridge.startTranslation()`

**Bridge**

→ sprawdzenie pliku wejściowego/wyjściowego

→ `_selection()`

→ `core.backend_controller.select(backend)`

→ `core.select_backend(BackendRequest(...))`

→ `core.build_translation_service(...)`

→ worker w osobnym `QThread`

→ usługa tłumaczenia.

Dla backendu:

- llama.cpp: request zawiera m.in. model GGUF, tryb obliczeń, szablon czatu i równoległość;
- cloud: używany jest wybrany profil/provider;
- Mozhi: do requestu trafiają wybrana instancja i silnik;
- Apertium: tworzony jest `BackendRequest(backend="apertium")`;
- custom: używany jest `CloudRouter` przez kontrakt custom.

## 6.7 Postęp

Bridge wystawia:

- `progress`;
- `elapsed_seconds`;
- `current_speed`;
- `average_speed`;
- `is_translating`;
- `status_text`.

Postęp aktualizuje:

`_on_progress(current, total)`.

Czas i średnia prędkość są aktualizowane przez timer.

## 6.8 Log

QML:

`bridge.logText`.

Bridge przechowuje:

`_log_text`.

Zmiana emituje:

`logChanged`.

## 6.9 Podgląd

QML:

`bridge.previewText`.

Po zakończeniu tłumaczenia:

`_on_finished()`

wywołuje:

`_preview_for_output(path)`.

Dla tekstowych formatów preview czyta fragment wyniku; dla pozostałych formatów pokazuje ścieżkę wyniku.

---

# 7. Zakładka „API i serwer”

Plik:

`src/tlumacz/qml_gui/ApiPage.qml`

To jest główna powierzchnia konfiguracji backendu.

## 7.1 Wspólne pola

Dla backendów innych niż Apertium:

- adres bazowy;
- klucz API;
- wybór serwera.

Powiązania:

| Kontrolka | Bridge |
|---|---|
| Base URL | `baseUrl` / `setBaseUrl()` |
| API key | `apiKey` / `setApiKey()` |
| Server | `backendType` / `setBackendTypeIndex()` |

Dla Mozhi:

- URL i API key są wyłączone;
- URL prezentuje `auto`;
- konfiguracja Mozhi jest sterowana osobno.

## 7.2 Układ pionowy sekcji backendu

Każda sekcja backendu (`llama.cpp`, Apertium, Cloud i własny) ma `Layout.fillHeight: visible`.

Dzięki temu tylko aktualnie widoczna sekcja otrzymuje rozciąganą wysokość. Ukryte sekcje nie mogą przejmować wolnego miejsca i tworzyć pustych obszarów pomiędzy wspólnymi polami a konfiguracją aktywnego backendu.

Dla Cloud pole `mozhiAutoInfo` również ma `Layout.fillHeight: visible`. Rozciąga się więc tylko dla profilu Mozhi; dla pozostałych providerów nie zajmuje pustej wysokości.

Wymagania układu:

- checkboxy zachowania backendu pozostają wyrównane do lewej;
- w Apertium pole opisu wykorzystuje wolną wysokość, a checkboxy są na dole sekcji;
- w Cloud/Mozhi pole informacji może wykorzystać wolną wysokość, a checkbox ponownego połączenia pozostaje na dole;
- w llama.cpp pusty element wewnątrz sekcji rozciąga się nad grupą checkboxów, a przycisk restartu pozostaje bezpośrednio pod nimi.

Nie należy dodawać `Layout.fillHeight: true` do ukrytych sekcji ani do niewidocznego `mozhiAutoInfo`, ponieważ powoduje to rozjechanie pionowego układu.

Dla Cloud/Mozhi checkbox ponownego połączenia znajduje się w osobnej grupie na końcu aktywnej sekcji. Dla profilu Mozhi nagłówek „Zachowanie backendu” znajduje się bezpośrednio nad polem `mozhiAutoInfo`; dla pozostałych providerów pusty element rozciągający poprzedza nagłówek i checkbox, dzięki czemu oba pozostają przy dolnej krawędzi zakładki.

---

# 8. Konfiguracja llama.cpp

Widoczność:

`visible: is("llama")`.

## 8.1 Port

GUI:

`SpinBox`

Bridge:

`bridge.serverPort`

Akcja:

`bridge.setServerPort(value)`.

Zakres:

**1111–65535**.

Losowanie:

`bridge.randomServerPort()`.

Bridge używa `random.randint(1111, 65535)`.

### Adres URL serwera

Dla llama.cpp port z `SpinBox` jest źródłem konfiguracji runtime. Bridge udostępnia `bridge.serverUrl`, wyliczany jako `http://<host>:<port>/v1`.

Pole „Adres URL” na karcie „API i serwer” pokazuje `bridge.serverUrl` dla llama.cpp i jest nieedytowalne. Nie jest źródłem portu i nie nadpisuje ustawienia `Port`. Restart llama.cpp pobiera ten sam `settings.server_port`.

Dla backendów innych niż llama.cpp pole pozostaje związane z `bridge.baseUrl` i może być edytowane zgodnie z ich kontraktem.



Model:

`bridge.computeModes`

Obecne wartości:

- `gpu`;
- `cpu`.

Zmiana:

`bridge.setComputeMode(currentText)`.

## 8.3 Szablon czatu

Model:

`bridge.chatTemplates`.

Obecne wartości:

- `jinja`;
- `chatml`;
- `TranslateGemma`.

QML wywołuje:

`bridge.setChatTemplate(currentText)`.

Bridge normalizuje:

- `jinja` → pusty string kontraktowy;
- `chatml` → `chatml`;
- `TranslateGemma` → `translategemma`.

**TranslateGemma nie jest osobnym backendem. Jest specjalnym szablonem/trybem llama.cpp.**

## 8.4 Równoległość

GUI:

`SpinBox`

Bridge:

`bridge.parallel`

Zakres:

**1–8**.

Setter:

`set_parallel()`.

## 8.5 Model GGUF

GUI:

- read-only `TextField`;
- `FileDialog`;
- filtr GGUF.

Akcja:

`bridge.setGgufPath(selectedFile)`.

Bridge przechowuje:

`_gguf_path`.

W persystencji:

`settings.server_gguf_path`.

## 8.6 Restart serwera

Przycisk jest widoczny tylko dla llama:

`visible: is("llama")`.

Akcja:

`bridge.restartServer()`.

Bridge:

`restart_server()`.

Jeżeli runtime nie działa, metoda może uruchomić go; jeżeli działa, wykonuje restart.

---

# 9. Konfiguracja Apertium

Widoczność:

`visible: is("apertium")`.

## 9.1 Źródło

Kontrolka GUI:

`ComboBox` z modelem `bridge.apertiumSourceLanguages`.

Bridge:

`sourceLanguageLabel` — etykieta bieżącego wyboru;
`setSourceLanguage(currentText)` — zapis wyboru.

Źródło danych:

`_apertium_source_options()`.

Ta funkcja:

1. odczytuje wykryte pary Apertium;
2. wyciąga kod źródłowy;
3. mapuje kody Apertium na znane kody językowe;
4. lokalizuje znaną nazwę;
5. zwraca pary `(label, code)`.

## 9.2 Cel

Kontrolka GUI:

`ComboBox` z modelem `bridge.targetLanguages`.

Bridge:

`targetLanguageLabel` — etykieta bieżącego wyboru;
`setTargetLanguage(currentText)` — zmiana języka docelowego.

Źródło kodu celu jest wspólne z globalną listą języków docelowych.

## 9.3 Serwer Apertium

W sekcji Apertium istnieje jeden selector serwera.

Testy pilnują, aby nie pojawiały się dodatkowe niezależne selectory.

## 9.4 Uwagi

GUI pokazuje `apertium.description` jako read-only `TextArea`.

To jest powierzchnia informacyjna, nie konfigurator runtime.

## 9.5 Lifecycle Apertium

Bridge nie używa lifecycle llama.cpp dla Apertium.

`restart_server()` ma osobną gałąź:

> Apertium uruchamia osobny proces dla każdego tłumaczenia; nie ma trwałego procesu do restartu.

To jest istotne przy dalszym rozwijaniu GUI.

---

# 10. Konfiguracja Cloud

Widoczność:

`visible: is("cloud")`.

## 10.1 Profil/provider

GUI:

`bridge.cloudProfiles`.

Zmiana:

`bridge.setCloudProfile(currentText)`.

Bridge ładuje profil przez:

`_load_cloud_profile()`.

## 10.2 Mozhi

Jeżeli:

`bridge.cloudProfile === "Mozhi"`

pojawiają się dwa dodatkowe selectory:

- silnik;
- instancja.

Bridge:

- `mozhiEngines`;
- `mozhiInstances`;
- `setMozhiEngine()`;
- `setMozhiInstance()`.

Dla Mozhi:

- base URL jest ustawiany jako `auto`;
- API key jest pusty;
- pod selectorami silnika i instancji pojawia się informacyjne pole tekstowe opisujące działanie trybu `auto`;
- tryb `auto` równolegle sonduje dostępne instancje, sprawdza wybrany silnik oraz dostępność języków źródłowych i wybiera najszybciej odpowiadającą instancję;
- jeśli żadna instancja nie przejdzie sondowania w limicie czasu, używana jest instancja domyślna.

## 10.3 Wewnętrzny przepływ Cloud

`QmlApplicationBridge._selection()`

→ profil Cloud

→ provider

→ `BackendRequest`

→ `TranslationApp`

→ `CloudRouter`.

Dla custom przepływ również korzysta z `CloudRouter`.

---

# 11. Backend „Własny”

Widoczność:

`visible: is("custom")`.

GUI pokazuje opis.

Bridge przy tłumaczeniu buduje:

`BackendRequest(backend="custom", base_url=..., api_key=..., model=...)`.

Następnie backend jest obsługiwany przez aktywny kontrakt CloudRouter.

**Nie należy dokumentować Własnego jako osobnego lokalnego silnika.**

---

# 12. Zakładka „Przełączniki”

Plik:

`src/tlumacz/qml_gui/ExtrasPage.qml`

Aktualna kolejność:

1. **Glosariusz**
2. **Umiejętności**
3. **Ustawienia LLM**

Checkboxy zachowania backendów **nie należą do tej karty**.

To jest celowa decyzja architektoniczno-UX.

---

# 13. Glosariusz

GUI korzysta z:

- `bridge.glossaryPath`;
- `bridge.glossaryStatus`;
- `bridge.setGlossaryPath()`;
- `bridge.addGlossaryEntry()`.

Przycisk **Przeglądaj...** otwiera dialog pliku.

Przycisk **Dodaj**:

`bridge.addGlossaryEntry(source, translation)`.

Bridge dopisuje wiersz CSV:

`[term, translation]`.

Status jest liczony przez odczyt pliku CSV.

---

# 14. Skille

## 14.1 Skille systemowe

Model:

`bridge.skillOptions`.

Stan:

`bridge.skillEnabled(modelData)`.

Zmiana:

`bridge.setSkillEnabled(modelData, checked)`.

## 14.2 Skille użytkownika

Model:

`bridge.userSkills`.

Każdy skill ma:

- checkbox aktywacji;
- przycisk usunięcia.

Usuwanie:

`bridge.deleteSkill(filename)`.

## 14.3 Import

Przycisk **Importuj skill**:

`skillDialog.open()`

→ `bridge.importSkill(source_path)`.

Bridge kopiuje plik do:

`$HOME/.config/tlumacz/skills`.

## 14.4 Nowy skill

Przycisk **Nowy skill** otwiera dialog szablonu.

Bridge zapisuje plik:

`nowa-umiejetnosc.md`

lub kolejną numerowaną wersję, jeżeli nazwa już istnieje.

## 14.5 Odświeżanie

Przycisk:

`bridge.refreshSkills()`.

Bridge tworzy katalog skilli użytkownika, jeżeli go nie ma, i emituje `skillsChanged`.

## 14.6 Automatyczny wybór skilla

To ważne powiązanie, które łatwo przeoczyć.

Po ustawieniu pliku wejściowego:

`set_input_path()`

→ `_auto_select_skill_for_input()`.

Wbudowane mapowanie obejmuje m.in.:

| Rozszerzenie | Skill |
|---|---|
| txt/text | plaintext.md |
| md/markdown | markdown.md |
| html/htm/xhtml | html.md |
| docx | docx.md |
| odt | odt.md |
| epub | epub.md |
| pdf | pdf.md |

Dla skilli użytkownika bridge czyta front matter i szuka pola `formats:`.

**Ważne:** `plaintext.md` i `pdf.md` są rzeczywistymi skillami systemowymi i są prezentowane przez GUI. Ich automatyczny dobór po rozszerzeniu pliku jest niezależny od osobnego statusu TXT/PDF w aktywnym `FilterRegistry`.

---

# 15. Ustawienia LLM

W `ExtrasPage.qml` sekcja ma:

`visible: bridge.backendType !== "apertium"`.

Czyli dla Apertium jest ukryta.

Zawiera:

- Rozmiar bloku;
- Temperaturę;
- własny prompt;
- wzorce pomijania.

## 15.1 Rozmiar bloku

QML:

`bridge.chunkSize`

→ `bridge.setChunkSize(value)`.

Bridge ogranicza wartość do:

**100–100000**.

Aktualny zakres GUI SpinBox:

**500–8000**.

## 15.2 Temperatura

QML prezentuje wartość w skali dziesiętnej przez dodatkowe przeliczenie:

`bridge.temperature * 10`

oraz z powrotem:

`value / 10`.

Backend bridge ogranicza temperaturę do:

**0.0–1.0**.

### OTWARTE / DO SPRAWDZENIA

W QML `valueFromText()` używa `parseFloat()`, a prezentacja korzysta z `toFixed(1)`.

Nie potwierdzono jeszcze, czy zachowanie z lokalnym separatorem dziesiętnym jest poprawne w każdej lokalizacji.

Nie należy twierdzić, że obserwowane wcześniej mnożenie temperatury ×100 jest już wyjaśnione przez ten fragment bez reprodukcji runtime.

## 15.3 Własny prompt

QML:

`bridge.systemPrompt`.

Zmiana przy aktywnym focus:

`bridge.setSystemPrompt(text)`.

## 15.4 Wzorce pomijania

QML:

`bridge.skipPatterns`.

Zmiana:

`bridge.setSkipPatterns(text)`.

Bridge przechowuje je jako listę linii w `settings.skip_line_patterns`.

---

# 16. Zakładka „Pomoc”

Plik:

`src/tlumacz/qml_gui/HelpPage.qml`.

## 16.1 Język aplikacji

GUI:

`ComboBox`

model:

- polski;
- angielski;
- niemiecki.

Akcja:

`bridge.setApplicationLanguage(...)`.

Bridge:

1. aktualizuje `settings.language`;
2. wywołuje `set_language()`;
3. ładuje ponownie tematy pomocy;
4. emituje `languageChanged`;
5. emituje `stateChanged`.

## 16.2 Motyw

GUI:

`ComboBox`

wartości:

- system;
- dark;
- light.

Akcja:

`bridge.setTheme(...)`.

Właściwa paleta jest stosowana w:

`src/tlumacz/qml_gui/app.py`

przez:

`_apply_theme()`.

Ikona aplikacji jest wybierana przez:

`_set_application_icon()`.

Pliki ikon:

- `tlumacz-dark.svg`;
- `tlumacz-light.svg`.

## 16.3 „O programie”

`HelpPage.qml` posiada modalny `Dialog`.

Pokazuje:

- logo;
- nazwę programu;
- wersję;
- opis;
- licencję.

Logo:

`frsststems_logo_full.svg`.

Wersja:

`bridge.applicationVersion`.

Opis:

`bridge.aboutText`.

## 16.4 Tematy pomocy

Bridge ładuje pliki pomocy z katalogu QML.

`_load_help_topics(language)`

parsuje nagłówki Markdown i buduje listę tematów.

GUI obecnie prezentuje pięć powierzchni tematycznych przez `StackLayout`.

Treść jest renderowana przez:

`HelpMarkdownView.qml`.

### Reaktywność tematów przy zmianie języka

Nie należy używać bezpośrednio tablicy:

`model: [bridge.helpTopic1Title, ...]`

jako modelu `Repeater`. Taka tablica może zostać zmaterializowana przez QML jako model bez reaktywnego odświeżania elementów po emisji `languageChanged`.

Aktualny kontrakt jest następujący:

- `Repeater` ma stały model `5`;
- `helpTabs.helpTopicTitles` pobiera pięć właściwości tytułów z bridge;
- tekst zakładki korzysta z `helpTabs.helpTopicTitles[helpTab.index]`;
- zmiana `bridge.applicationLanguage` powoduje ponowne obliczenie tytułów;
- treść `HelpMarkdownView` nadal korzysta bezpośrednio z `bridge.helpTopic1Content` ... `bridge.helpTopic5Content`.

Dzięki temu przełączenie **Deutsch → Polski** lub **English → Polski** aktualizuje zarówno tematy zakładek, jak i ich zawartość, zamiast pozostawiać wcześniejsze niemieckie tytuły.

---

# 17. Persystencja konfiguracji

## 17.1 Aktualny magazyn GUI QML

`src/tlumacz/qml_gui/config.py`

definiuje:

`CONFIG_PATH = $HOME/.config/tlumacz/config.json`.

Dataclass:

`AppSettings`.

Obejmuje m.in.:

- backend;
- URL;
- klucz lokalny;
- profile Cloud;
- aktywne skille;
- profil Cloud;
- Mozhi;
- port;
- GGUF;
- ostatni plik wejścia/wyjścia;
- tryb CPU/GPU;
- chat template;
- parallel;
- autostart;
- cache;
- osobne akcje: restart llama.cpp, restart Apertium, ponowne połączenie Cloud;
- chunk size;
- temperaturę;
- język docelowy;
- język źródłowy;
- glosariusz;
- prompt;
- wzorce pomijania;
- motyw;
- język;
- geometrię okna.

## 17.2 Jak GUI zapisuje ustawienia

Najważniejsze wejścia:

- `setBackendTypeIndex()` zapisuje backend;
- wiele setterów aktualizuje stan bridge;
- `saveSettings()` wywołuje `save_settings()`;
- `save_window_state()` zapisuje geometrię okna.

`save_settings()` synchronizuje stan bridge z `AppSettings` i zapisuje JSON.

## 17.3 Ważne: ustawienia nie są jeszcze całkowicie zunifikowane z V3

Istnieje również:

`$HOME/.config/tlumacz/config.json`.

W projekcie pozostaje otwarte zadanie pełnego zunifikowania konfiguracji V3/V4.

### OTWARTE / DO ZROBIENIA

Nie zakładać, że `config.json` i `config.json` są jednym źródłem prawdy.

Dopóki migracja nie zostanie wykonana i zweryfikowana, każdą nową funkcję konfiguracji trzeba świadomie sprawdzić pod kątem:

- gdzie jest odczytywana;
- gdzie jest zapisywana;
- czy stary GUI/runtime ją widzi;
- czy V4 ją widzi;
- czy istnieje migracja;
- czy istnieje test round-trip.

---

# 18. Sekrety Cloud

Bridge posiada:

`SecretStore`.

Domyślna ścieżka:

`$HOME/.config/tlumacz/.key`.

Klucze Cloud nie powinny być dokumentowane jako zwykłe wartości przechowywane jawnie w dokumentacji.

Bridge ma osobny mechanizm:

`_store_active_cloud_profile()`

i:

`_store_local_api_key()`.

### Zasada

Nie wpisywać prawdziwych kluczy API do:

- dokumentacji;
- testów;
- commitów;
- screenshotów;
- przykładów.

---

# 19. Geometria i odpowiedzialność za layout

Najważniejszy plik:

`QML_GUI_LAYOUT.md`.

Aktualne QML korzysta przede wszystkim z:

- `ColumnLayout`;
- `RowLayout`;
- `GridLayout`;
- `StackLayout`;
- `ScrollView`;
- `GroupBox`.

Nie należy wprowadzać konkurencyjnego sterowania geometrią bez sprawdzenia właściciela layoutu.

## Aktualne istotne wartości

### Główne okno

`Main.qml`:

- domyślna szerokość: 1120;
- domyślna wysokość: 780;
- margines główny: 8;
- spacing: 8;
- bazowy font: 15 px.

### Tłumaczenie

- główne spacing: 2;
- pola formularza: 36 px;
- przyciski akcji: 130 px;
- obszar Log: preferowane 220 px;
- obszar Podgląd: preferowane 220 px.

### API

- typowe pola liczbowe: 140 px;
- selector backendu: maks. 360 px;
- pola Apertium: 140 px;
- odstęp kolumn Apertium: 24 px.

### Przełączniki

- akcje skilli: 180 px;
- część kontrolek glosariusza: 120 px;
- kontrolki parametrów LLM: 120 px.

Wartości geometrii są kontraktem UI tylko wtedy, gdy są potwierdzone aktualnym QML i testem.

---

# 20. Lokalizacja tekstów

GUI nie powinno mieć nowych napisów użytkowych zapisanych na stałe w QML, jeżeli istnieje mechanizm i18n.

Typowy wzorzec:

`text: tr("klucz")`.

Bridge:

`tr(key)`

korzysta z aktywnego języka.

Aktualne języki GUI:

- PL;
- EN;
- DE.

### Długie pola informacyjne

Długie, statyczne treści wyświetlane w dużych `TextArea` nie są przechowywane w kodzie Python ani QML. Są przechowywane jako pliki UTF-8:

- `src/tlumacz/qml_gui/texts/pl/`
- `src/tlumacz/qml_gui/texts/en/`
- `src/tlumacz/qml_gui/texts/de/`

Aktualnie wydzielone są:

- `apertium.description.txt` — opis zasady działania backendu regułowego Apertium, w szczególności zależności od konkretnych par źródło → cel i ograniczeń wynikających z danych, zależności oraz licencji par;
- `cloud.mozhi_auto_info.txt` — opis mechanizmu `auto` Mozhi: równoległe sprawdzanie instancji, silnika i języków, tłumaczenie kontrolne, pomiar czasu, wybór najszybszej poprawnej instancji i fallback;
- `custom.description.txt` — instrukcja konfiguracji zewnętrznego serwera OpenAI-compatible wraz z przykładami konfiguracji vLLM i zewnętrznego endpointu;
- `help.about_text.txt` — długi opis w oknie „O programie”.

QML korzysta z `longText("klucz")`, a `QmlApplicationBridge.long_text()` ładuje odpowiedni plik dla aktywnego języka. Pomoc podręczna pozostaje w osobnych plikach `help.pl.md`, `help.en.md` i `help.de.md`.

Pliki tekstowe pól informacyjnych są deklarowane w `pyproject.toml` jako package data, dlatego muszą wejść również do wheel.

### Co trzeba pamiętać

Zmiana tekstu użytkowego wymaga sprawdzenia:

1. `src/tlumacz/i18n.py`;
2. QML;
3. testów lokalizacji;
4. długości tekstu w układzie;
5. pomocy Markdown, jeżeli tekst należy do instrukcji.

Znany problem:

**w `i18n.py` istnieje duplikat klucza wykrywany przez test `test_i18n_dictionaries_have_unique_keys`.**

To jest osobny problem od rozmieszczenia GUI.

---

# 21. Launcher i runtime QML

Aktualny launcher V4:

`/home/frs/Projekty/tlumacz-v4/uruchom-v4.sh`.

Ważne:

- ustawia `PYTHONPATH="$ROOT/src"`;
- wyłącza dyskowy cache QML;
- uruchamia `python3 -m tlumacz.qml_gui.app`.

`app.py` również ustawia:

`QML_DISABLE_DISK_CACHE=1`.

QML jest ładowany przez:

`QML_FILE = Path(__file__).with_name("Main.qml")`.

### Krytyczne ostrzeżenie

Systemowe:

`/usr/bin/tlumacz`

może uruchamiać starszy V3.

Dlatego przy diagnostyce GUI trzeba sprawdzać:

**launcher → interpreter → moduł → Main.qml → proces → ekran.**

Nie wystarczy stwierdzić, że plik QML wygląda poprawnie.

---

# 22. Testy GUI — gdzie szukać regresji

Główny plik:

`tests/test_qml_gui.py`.

Testy obejmują m.in.:

- izolację GUI QML;
- ładowanie QML offscreen;
- stronę Tłumaczenie;
- przyciski plików;
- bridge i stan tłumaczenia;
- auto-wybór skilla;
- rozmieszczenie checkboxów backendów;
- persystencję ustawień;
- persystencję skilli;
- motyw;
- backend selection;
- stronę API;
- Mozhi;
- autostart;
- post-translation actions;
- Apertium;
- sekcję LLM;
- lokalizację;
- pomoc;
- geometrię okna;
- kontrakty QML.

Szczególnie ważne testy dla obecnej architektury backendów:

- `test_qml_backend_option_checkboxes_are_bound_to_each_backend_section`;
- `test_qml_backend_selection_uses_stable_ids_for_all_languages`;
- `test_qml_api_page_matches_final_backend_layout`;
- `test_qml_server_api_surface_contains_runtime_controls`;
- `test_qml_switches_hide_llm_section_for_apertium`;
- `test_qml_apertium_api_page_uses_single_server_selector_and_language_section`;
- `test_qml_apertium_translation_shows_source_and_target_in_selectors` — nazwa historyczna/myląca; aktualne asercje potwierdzają pola `TextField` tylko do odczytu, a nie możliwość wyboru;
- `test_qml_apertium_translation_source_selector_uses_detected_languages` — również nazwa historyczna/myląca; test sprawdza brak modelu `apertiumSourceLanguages` w QML;
- `test_qml_apertium_translation_languages_are_on_action_row` — potwierdza obecny stan: pola językowe są w wierszu sterowania;
- `test_qml_bridge_runs_configured_post_translation_actions`;
- `test_qml_bridge_autostarts_llama_only_when_enabled`.

---

# 23. Co jest obecnie potwierdzone

## Potwierdzone kodem

- cztery główne zakładki GUI;
- warunkowa widoczność konfiguracji backendów;
- stabilne ID backendów;
- bridge QML jako warstwa pomiędzy QML i `TranslationApp`;
- konfiguracja llama.cpp;
- konfiguracja Cloud;
- konfiguracja Mozhi;
- konfiguracja Apertium;
- wykrywanie potencjalnych źródeł Apertium w warstwie bridge;
- custom przez CloudRouter;
- glosariusz;
- skille;
- automatyczny wybór skilla po rozszerzeniu;
- ustawienia LLM;
- motyw;
- język;
- pomoc;
- persystencja `config.json`;
- zapis geometrii okna;
- post-translation actions;
- autostart llama.cpp;
- restart llama.cpp.

## Potwierdzone testami kontraktowymi

Testy `test_qml_gui.py` potwierdzają dużą część struktury i bindingów QML, w szczególności rozmieszczenie backendowych checkboxów, selekcję backendu, powierzchnię Apertium, układ strony Tłumaczenie, persystencję oraz warunkowe sekcje.

---

# 24. Czego ten dokument NIE potwierdza

## 24.1 Faktycznie wyświetlanego ekranu

Kod QML i test offscreen nie są dowodem, że użytkownik aktualnie widzi ten sam ekran.

Na dzień 2026-10-05 nie ma w tej dokumentacji bezpośredniego dowodu typu:

**uruchomione okno V4 → screenshot aktualnie widocznego okna → porównanie z oczekiwanym stanem.**

Dlatego przy zgłoszeniu:

> „na ekranie nadal widzę starą wersję”

należy rozpocząć od weryfikacji runtime, a nie od kolejnej edycji QML.

## 24.2 Pełnej zgodności dwóch magazynów konfiguracji

Nie potwierdzono pełnej unifikacji:

- `$HOME/.config/tlumacz/config.json`;
- `$HOME/.config/tlumacz/config.json`.

To pozostaje osobnym zadaniem.

## 24.3 Niezależnych ustawień checkboxów per backend

Aktualny model ma wspólne flagi.

Rozmieszczenie jest per backend, ale stan jest wspólny.

## 24.4 Pełnej dynamicznej obsługi par Apertium

Bridge potrafi wykrywać potencjalne źródła z dostępnych par, ale aktualny `TranslationPage.qml` pokazuje źródło i cel jako pola `TextField` tylko do odczytu.

Brakuje bezpośredniego wyboru języka źródłowego przez użytkownika. Dynamiczny wybór pary/kierunku, pełna detekcja runtime oraz decyzja o sposobie powiązania źródła i celu nie są jeszcze kompletnym kontraktem GUI.

## 24.5 Poprawności lokalnego wpisywania temperatury

Istnieje miejsce wymagające osobnej weryfikacji dla separatorów dziesiętnych i konwersji wartości.

---

# 25. Lista rzeczy do zrobienia

## P0 / krytyczne dla wiarygodności GUI

1. **Zweryfikować faktycznie wyświetlany runtime QML V4.**
   - uruchomić dokładnie `uruchom-v4.sh`;
   - potwierdzić proces;
   - potwierdzić załadowany `Main.qml`;
   - wykonać bezpośrednią kontrolę widocznego okna.

2. **Nie używać `/usr/bin/tlumacz` jako dowodu działania V4**, dopóki launcher nie zostanie świadomie zmieniony.

## P1 / konfiguracja

3. **Dokończyć unifikację `config.json` i `config.json`.**
   - ustalić jedno źródło prawdy;
   - zdefiniować migrację;
   - zachować istniejące ustawienia użytkownika;
   - dodać round-trip test;
   - zaktualizować dokumentację.

4. **Rozważyć per-backend storage checkboxów.**
   - llama;
   - cloud;
   - apertium;
   - migracja istniejących trzech flag;
   - test niezależności.

## P1 / Apertium

5. **Dokończyć kontrakt dynamicznych par językowych Apertium.**
   - wykrywanie dostępnych par;
   - kierunki jednokierunkowe/dwukierunkowe;
   - poprawne mapowanie ISO;
   - udostępnienie rzeczywistego wyboru źródła w GUI;
   - ustalenie, czy wybór celu ma pozostać globalny czy również zależeć od wykrytej pary;
   - walidacja zgodności z runtime;
   - test GUI + test backendu.

## P2 / LLM

6. **Zweryfikować temperaturę w PL/EN/DE.**
   - separator dziesiętny;
   - wartość wpisywana ręcznie;
   - wartość prezentowana;
   - wartość przekazywana do bridge;
   - wartość zapisywana;
   - wartość używana przez backend.

7. **Sprawdzić, czy wszystkie kontrolki LLM są rzeczywiście potrzebne dla każdego backendu Cloud/custom.**
   Nie przenosić ich automatycznie między kartami bez potwierdzenia kontraktu.

## P2 / dokumentacja i testy

8. Przy każdej zmianie GUI aktualizować ten dokument oraz właściwe dokumenty:
   - `QML_GUI_DESIGN.md`;
   - `QML_GUI_LAYOUT.md`;
   - `QML_GUI_TRANSLATION_CARD_SPEC.md`;
   - `docs/technical-docs/index.md`;
   - `docs/INDEX.yml`;
   - `docs/DOCUMENTATION_CHANGELOG.md`.

9. Przy każdym nowym bindingu GUI dodawać test kontraktowy, jeżeli zachowanie ma znaczenie regresyjne.

---

# 26. Procedura diagnostyczna: „kontrolka nie działa”

Nie zaczynać od zmiany QML.

Sprawdzać kolejno:

1. **Czy kontrolka istnieje w właściwym QML?**
2. **Czy ma poprawne `visible`/warunek backendu?**
3. **Czy binding wskazuje właściwość bridge?**
4. **Czy bridge ma właściwość/slot o tej nazwie?**
5. **Czy slot faktycznie zmienia stan?**
6. **Czy stan jest zapisywany do `AppSettings`?**
7. **Czy stan jest używany przez `TranslationApp`/backend?**
8. **Czy istnieje test tego powiązania?**
9. **Czy uruchomiona aplikacja jest V4?**
10. **Czy użytkownik faktycznie widzi aktualny QML?**

### Minimalna mapa diagnostyczna

```
QML kontrolka
   ↓
binding / onActivated / onToggled / onClicked
   ↓
QmlApplicationBridge
   ↓
AppSettings lub TranslationApp
   ↓
backend / runtime
   ↓
efekt
   ↓
sygnał / właściwość zwrotna
   ↓
QML
```

Jeżeli problem dotyczy tylko wyglądu:

```
QML
 ↓
Layout / anchors / visible / palette
 ↓
uruchomiony Main.qml
 ↓
rzeczywiste okno
```

---

# 27. Procedura dodawania nowej funkcji GUI

Przed implementacją określ:

1. do której zakładki należy funkcja;
2. czy jest globalna czy backendowa;
3. jeżeli backendowa — przy którym backendzie ma być widoczna;
4. kto jest właścicielem stanu;
5. jaka właściwość bridge jest źródłem prawdy;
6. jaki slot zmienia stan;
7. gdzie stan jest zapisywany;
8. jaki komponent aplikacyjny go wykorzystuje;
9. jaki test chroni binding;
10. jaki dokument opisuje kontrakt.

### Reguła backendowa

Jeżeli funkcja dotyczy konkretnego serwera:

> **umieść ją w sekcji tego serwera i ukryj, gdy ten serwer nie jest wybrany.**

Nie przenoś jej do „Przełączników” tylko dlatego, że technicznie używa wspólnej właściwości bridge.

---

# 28. Procedura zmiany GUI

Obowiązuje projektowa zasada:

1. przeczytać cały `ADMINS.md`;
2. ustalić rzeczywiste źródło QML;
3. zlokalizować bridge;
4. znaleźć istniejący test;
5. przy zmianie zachowania: RED → minimalna implementacja → GREEN;
6. zaktualizować dokumentację;
7. uruchomić świeżą weryfikację;
8. przy zmianie wizualnej dodatkowo zweryfikować rzeczywiście uruchomione okno;
9. przed stwierdzeniem „gotowe” sprawdzić cały łańcuch runtime.

Przy dużej zmianie kodu:

**backup przed zmianą.**

---

# 29. Dokumenty powiązane

### Najważniejsze

- `docs/technical-docs/QML_GUI_DESIGN.md` — kierunek, zakres i decyzje GUI;
- `docs/technical-docs/QML_GUI_LAYOUT.md` — szczegółowa historia i geometria layoutu;
- `docs/technical-docs/QML_GUI_TRANSLATION_CARD_SPEC.md` — kontrakt karty Tłumaczenie;
- `docs/technical-docs/functional-capabilities.md` — funkcje obecne w kodzie;
- `docs/technical-docs/server-management.md` — lifecycle llama.cpp;
- `docs/technical-docs/cloud-translation.md` — CloudRouter i providerzy;
- `docs/technical-docs/apertium-backend-integration.md` — Apertium;
- `docs/technical-docs/user-guide.md` — powierzchnia użytkownika;
- `tests/test_qml_gui.py` — kontrakty regresyjne GUI.

### Źródła wykonawcze

- `src/tlumacz/qml_gui/Main.qml`;
- `src/tlumacz/qml_gui/TranslationPage.qml`;
- `src/tlumacz/qml_gui/ApiPage.qml`;
- `src/tlumacz/qml_gui/ExtrasPage.qml`;
- `src/tlumacz/qml_gui/HelpPage.qml`;
- `src/tlumacz/qml_gui/HelpMarkdownView.qml`;
- `src/tlumacz/qml_gui/bridge.py`;
- `src/tlumacz/qml_gui/config.py`;
- `src/tlumacz/qml_gui/app.py`.

---

# 30. Zasada utrzymania tego kompendium

Ten dokument ma być aktualizowany **razem z kontraktem GUI**, a nie dopiero po kilku miesiącach.

Po każdej istotnej zmianie trzeba odpowiedzieć:

- Czy doszedł nowy ekran?
- Czy doszła nowa kontrolka?
- Czy zmienił się właściciel stanu?
- Czy zmienił się binding QML → bridge?
- Czy zmieniła się persystencja?
- Czy zmienił się backend?
- Czy zmieniła się widoczność zależna od backendu?
- Czy zmienił się runtime?
- Czy zmienił się test?
- Czy zmienił się rzeczywisty wygląd?

Jeżeli odpowiedź na którekolwiek z tych pytań brzmi „tak”, odpowiednia część tego dokumentu powinna zostać zaktualizowana.

**Ten plik ma być mapą połączeń GUI, a nie kroniką pojedynczych poprawek.**


## Unifikacja konfiguracji — 2026-10-07

Jedynym trwałym źródłem ustawień GUI jest `$HOME/.config/tlumacz/config.json`. Nie należy tworzyć ani odtwarzać `settings-v4.json`. `AppSettings`, `load_settings()` i `save_settings()` używają `config.json`; techniczny tuning llama.cpp nadal pozostaje w `$HOME/.config/tlumacz/llama.json` zgodnie z jego osobnym kontraktem.

## Kontrakt konfiguracji — 2026-10-07

**Kanoniczny plik ustawień GUI: `$HOME/.config/tlumacz/config.json`.** Nie tworzyć `settings-v4.json` i nie przywracać go do aktywnego kodu. `llama.json` służy wyłącznie do technicznego tuningu llama.cpp. Sekrety API są przechowywane przez `SecretStore`.

Weryfikacja migracji: ukierunkowany zakres testów konfiguracji/GUI **41 passed**. Pełny suite pozostaje otwarty z powodu niezależnego fatalnego `Aborted` Qt/PySide6 po wcześniejszych failure'ach oraz wątków Filter Engine widocznych w stack trace.


## 2026-10-07 — llama.cpp, TranslateGemma i Markdown

- Po przełączeniu backendu na `llama` GUI wywołuje automatyczny start zarządzanego serwera, gdy `auto_start_server` w `config.json` jest włączone. Przycisk „Restartuj serwer” pozostaje operacją ręczną dla restartu.
- QML używa wartości prezentacyjnej `TranslateGemma`; warstwa bridge przechowuje wartość techniczną `translategemma`.
- Filtr Markdown przekazuje do tłumaczenia tekst bez podstawowych znaczników blokowych, zachowując je w wyniku. Linie będące wyłącznie separatorami Markdown oraz fenced code nie są jednostkami tłumaczeniowymi.
- Timeout żądania llama.cpp wynosi 1800 s, co jest istotne szczególnie dla TranslateGemma na CPU i większych fragmentów.


## 2026-10-07 — timeout i gotowość llama.cpp

- `LlamaCppConfig.timeout` wynosi 1800 s dla długiej inferencji TranslateGemma na CPU.
- `LlamaCppRuntimeConfig.startup_timeout` wynosi 300 s; gotowość jest sprawdzana przez `/health`, przy czym HTTP 503 `Loading model` oznacza prawidłowy stan przejściowy podczas ładowania modelu.
- Aktualny bundled `llama-server` projektu nie wykrywa żadnego urządzenia GPU (`--list-devices` zwraca `(none)`), dlatego `server_compute_mode=cpu` oznacza rzeczywiste wykonanie CPU.
- Pomiar diagnostyczny na TranslateGemma 4B Q5_K_M wykazał bardzo niską przepustowość CPU; timeout 300 s nie był wystarczającym limitem dla większych chunków.

## TranslateGemma na CPU — równoległość

Jeżeli `server_compute_mode=cpu`, GUI nie może przekazywać wartości `server_parallel` większej niż 1 do ścieżki tłumaczenia dokumentu ani do uruchamiania/restartu zarządzanego llama.cpp. W `QmlApplicationBridge` służą do tego `effective_translation_parallel` i `effective_server_parallel`. Powodem jest ograniczenie zasobów CPU oraz stabilność slotów llama.cpp: równoległe requesty tego samego modelu mogą powodować timeouty i błędy komunikacji, więc CPU jest celowo serializowane. Tryb GPU zachowuje skonfigurowaną równoległość.


## 2026-10-07 — TranslateGemma: chunkowanie strukturalne i batch

Ścieżka dokumentowa V4 korzysta obecnie z planera świadomego struktury jednostek. Dla Markdown filtr przekazuje typ `heading`/`paragraph`; po osiągnięciu 60% budżetu rozpoczęcie nowego nagłówka zamyka poprzedni chunk. Zmiana wykrytego języka źródłowego również tworzy granicę chunka.

Normalna ścieżka llama.cpp nie wykonuje już osobnego requestu dla każdej jednostki w chunku. `TranslationExecutor.execute_batch()` przekazuje cały chunk do `LlamaCppAdapter.translate_batch()`, który używa markerów `⟦TG_SEG_N⟧`. Odpowiedź jest walidowana pod kątem kompletności, duplikatów i kolejności. Po niepoprawnej odpowiedzi wykonywana jest jedna próba naprawcza; drugi błąd uruchamia kontrolowany fallback jednostkowy.

Markdown nie wysyła do backendu YAML front matter ani linii metadanych `name:`, `license:`, `author:`, `metadata:`, `version:`, `tags:`, `created:`, `updated:`. Bloki kodu i linie składniowe są nadal chronione przez filtr, a writer zachowuje pominięte fragmenty bez zmian.

`language_code_for()` normalizuje podstawowe kody TranslateGemma oraz warianty regionalne `xx-YY`/`xx_YY`. `auto` nie jest prawidłowym kodem dla TranslateGemma i nie jest wysyłane do modelu.

Ważne: limit `chunk_size` w V4 jest limitem znakowym planera, a nie dokładnym limitem tokenów. Oficjalna dokumentacja TranslateGemma podaje 2K tokenów kontekstu i zaleca dzielenie długich dokumentów na akapity. Dlatego rzeczywisty E2E należy jeszcze zweryfikować na aktywnym GGUF i konfiguracji CPU.
