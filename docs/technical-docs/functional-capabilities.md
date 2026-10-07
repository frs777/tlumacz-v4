---
id: functional-capabilities-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: project-documentation
source:
  - src/tlumacz/application/
  - src/tlumacz/backends/
  - src/tlumacz/filter_engine/
  - src/tlumacz/qml_gui/
  - src/tlumacz/i18n.py
depends_on:
  - docs/STATUS.md
  - docs/ARCHITECTURE.md
  - docs/RETIRED_FUNCTIONALITY.md
expires_when: zmiana aktywnego kontraktu aplikacji, backendów, Filter Engine lub GUI
last_validation: "inspekcja kodu SentinelX 2026-10-04; ponowna weryfikacja pytest 268 passed"
---

## 2026-10-05 — stan zweryfikowany po aktualizacji GUI

Macierz nadal opisuje funkcje obecne w kodzie. Potwierdzono, że ustawienia zachowania backendów są obecnie przypisane do ich sekcji w `ApiPage.qml`, a `ExtrasPage.qml` pozostaje miejscem dla glosariusza, skilli i ustawień LLM.

W aktualnym `TranslationPage.qml` pola Apertium są tylko do odczytu i znajdują się w tym samym `RowLayout` co przyciski sterowania. Wcześniejsze opisy wydzielonego wiersza są historyczne i nie powinny być traktowane jako stan wdrożony.

# Macierz funkcjonalna Tłumacza V4

Dokument opisuje funkcje, które są **rzeczywiście obecne w kodzie V4**, również te, które wcześniej nie miały osobnego opisu projektowego. Nie jest to lista funkcji historycznego V3.

## 1. Rdzeń tłumaczenia dokumentów

Aktywny przepływ implementacji:

`TranslationApp` → wybór backendu → `DocumentTranslationService` → `DocumentProcessor` → filtr formatu → `TranslationOrchestrator` → `ChunkPlanner` / `PromptBuilder` / `TranslationExecutor` / `TranslationCache` / `ResultValidator` → zapis dokumentu.

### TranslationApp

`src/tlumacz/application/translation_app.py` jest composition rootem warstwy aplikacyjnej. Odpowiada m.in. za:

- rejestrację filtrów dokumentowych;
- wybór backendu;
- budowę usługi tłumaczenia;
- współdzielenie cache tłumaczeń;
- uruchamianie, restart i zatrzymywanie zarządzanego llama.cpp;
- czyszczenie cache po żądaniu GUI.

### TranslationOrchestrator

Orkiestrator:

- dzieli jednostki na fragmenty przez `ChunkPlanner`;
- buduje prompt systemowy przez `PromptBuilder`;
- odczytuje cache przed wywołaniem backendu;
- wykonuje brakujące tłumaczenia przez `TranslationExecutor`;
- zachowuje kolejność jednostek;
- waliduje wynik przez `ResultValidator`;
- zapisuje poprawne wyniki do cache;
- respektuje `CancellationToken`.

Backend pozostaje wykonawcą tłumaczenia. Nie jest właścicielem rekonstrukcji dokumentu.

## 2. Obsługa dokumentów i konwersja

V4 nie traktuje konwersji dokumentu jako niezależnego „konwertera do XLIFF”. Aktywny model to **Filter Engine + sesja filtra + jednostki tłumaczeniowe + rekonstrukcja**.

`FilterRegistry` korzysta z jednego trwałego magazynu pakietów `$HOME/.config/tlumacz/filters` (lub `TLUMACZ_FILTER_STORE`). Pakiety `.tplugin` są rozpakowywane wyłącznie do tymczasowego `/tmp/filters/`; nie istnieje trwały runtime `filter-engine/plugins`. Manifest `plugin.json` jest rozwiązywany leniwie dopiero przy `for_path()`.

Aktywne wejściowe pluginy Okapi to EPUB, JSON, OpenOffice, OpenXML i YAML. HTML oraz Markdown są natywne i nie uruchamiają Okapi. XLIFF jest wewnętrzną warstwą dokumentową (`src/tlumacz/documents/xliff.py`), a nie wejściowym filtrem rejestru.

TXT i PDF pozostają poza aktywnym rejestrem.

Filter Engine:

1. rozpoznaje filtr po rozszerzeniu;
2. otwiera sesję;
3. ekstraktuje jednostki;
4. waliduje jednostki;
5. sprawdza markery przed tłumaczeniem;
6. tłumaczy jednostki;
7. ponownie sprawdza markery;
8. waliduje kompletność targetów;
9. zapisuje wynik przez właściwy filtr.

### TXT i PDF

W aktualnym V4 **TXT i PDF nie są zarejestrowane w `build_filter_registry()`** i nie mają aktywnego filtra w bieżącym `DocumentProcessor`. Obecność plików skilli `src/tlumacz/skills/plaintext.md` i `pdf.md` nie jest dowodem aktywnej obsługi formatu.

Dokumentacja użytkowa nie powinna przedstawiać TXT/PDF jako obecnie obsługiwanych przez główny przepływ V4 bez osobnego potwierdzenia implementacji.

## 3. Język źródłowy

V4 ma dwa odrębne kontrakty źródła:

- standardowy przepływ backendu zachowuje `source_language="auto"` jako wartość kontraktową;
- dedykowany tryb TranslateGemma wykonuje rzeczywistą detekcję przez Lingua przed requestem i zamienia wynik na kod ISO 639-1.

`src/tlumacz/language_detector.py` jest świadomie ograniczony do trybu `chat_template="translategemma"`. Nie jest globalnym detektorem używanym przez Cloud, Apertium ani standardowy llama.cpp.

Detekcja TG:
1. tworzy jeden współdzielony model Lingua dla instancji `LlamaCppAdapter`;
2. wykonuje detekcję dla tekstu przekazywanego do tłumaczenia;
3. zwraca kod ISO 639-1, np. `en` albo `pl`;
4. kod źródłowy jest używany w kontrakcie/promptcie TranslateGemma;
5. język docelowy jest normalizowany przez `language_code_for()` i nie może zostać błędnie zamieniony na `auto`.

Zależność: `lingua-language-detector>=2.1.1`.



Aktywny lokalny backend:

- `LlamaCppAdapter`;
- `LlamaCppRuntimeManager`;
- konfiguracja adresu, klucza, modelu, timeoutu, temperatury, szablonu czatu i równoległości;
- zarządzanie procesem llama-server;
- health-check;
- identyfikacja własności zarządzanego procesu;
- start, stop i restart.

GUI może automatycznie wykonać akcje po poprawnym zakończeniu tłumaczenia, jeżeli ustawienia tego wymagają. `cache_clear_after_translation` wywołuje `TranslationApp.clear_translation_cache()` i czyści `TranslationCache`. `restart_llama_after_translation` wywołuje kontrolowany `STOP → START` aktywnego llama.cpp przez `QmlApplicationBridge._restart_llama_from_gui()`, z aktualną konfiguracją GUI (GGUF, host, port, compute mode, parallel, chat template, chunk size). Ta sama funkcja jest używana przez ręczny restart serwera. Dla Apertium dostępny jest `restart_apertium_after_translation`, a dla Chmury `reconnect_cloud_after_translation`. Kolejność wspólnych akcji to: czyszczenie cache, następnie restart/reconnect właściwy dla backendu.

### TranslateGemma

`translategemma` jest specjalnym trybem szablonu czatu dla llama.cpp. Nie jest osobnym backendem V4 i nie oznacza reaktywacji historycznej ścieżki FastAPI/OpenVINO.

W tym trybie `LlamaCppAdapter`:

- inicjalizuje `LanguageDetector` tylko dla TranslateGemma;
- wykrywa język źródłowy dla tekstu/chunku i używa kodu ISO 639-1;
- normalizuje język docelowy do kodu ISO 639-1;
- buduje dedykowany prompt TranslateGemma z nazwami i kodami języków;
- korzysta z endpointu `/completions` w aktualnym kontrakcie llama.cpp, ponieważ V3 wykazał ograniczenie natywnego typed-content `/chat/completions` w używanym wariancie runtime;
- zwraca metadane `source_language_code`, `target_language_code` i `chat_template="translategemma"`;
- GUI przekazuje dla lokalnego llama.cpp timeout HTTP **300 s**, ponieważ rzeczywisty chunk TranslateGemma na CPU może przekroczyć wcześniejszy limit 120 s; timeout obejmuje oczekiwanie na cały response `/completions`.

Standardowy tryb llama.cpp pozostaje na `/chat/completions` i nie korzysta z Lingua. Testy regresyjne obejmują detekcję `pl`/`en`, zachowanie kodów w promptcie oraz izolację standardowego kontraktu.

## 5. Backend Cloud

Rejestr domyślny zawiera adaptery:

- OpenAI-compatible;
- DeepL;
- Microsoft;
- MyMemory;
- LibreTranslate;
- DLX.

Cloud posiada:

- `CloudRouter`;
- `CloudProviderRegistry`;
- klasyfikację błędów;
- timeouty;
- kontrakt wspólnego `BackendResult`;
- osobną ścieżkę Mozhi.

### Mozhi

`MozhiProvider` obsługuje:

- wybór konkretnej instancji;
- tryb `auto`, w którym instancje są sondowane pod kątem dostępności silnika;
- silniki DuckDuckGo, Google, DeepL, Yandex, Reverso i MyMemory;
- normalizację kodów językowych dla MyMemory;
- klasyfikację błędów HTTP, sieciowych, timeoutów i niepoprawnej odpowiedzi.

### Własny / custom

Backend `custom` korzysta z tego samego `CloudRouter` co ścieżka Cloud, z własnymi parametrami endpointu, klucza i modelu. Nie jest to trzeci lokalny silnik tłumaczeniowy.

## 6. Backend Apertium

Apertium jest osobnym backendem V4 i korzysta z prywatnego runtime'u.

Kod zawiera:

- kontrakty statusu i capabilities;
- walidację konfiguracji;
- wykrywanie zainstalowanych pakietów danych przez `modes.xml`;
- mapowanie kodów ISO ↔ kodów Apertium;
- budowanie kierunkowej pary, np. `eng-pol`;
- limity czasu i wyjścia;
- rozróżnienie błędu niedostępności, timeoutu, limitu i walidacji;
- health-check;
- obsługę procesu przez adapter.

GUI ogranicza wybór backendu Apertium do parametrów właściwych temu backendowi. Nie uruchamia dla niego lifecycle llama.cpp.

**Ważne:** obecność funkcji mapowania i wykrywania pakietów nie oznacza, że wszystkie pary językowe są gotowe produkcyjnie. Aktualny blocker `eng-pol` pozostaje opisany w `STATUS.md`.

## 7. Cache tłumaczeń

`TranslationCache` używa SQLite i jest współbieżny.

Klucz cache uwzględnia:

- tekst fragmentu;
- prompt systemowy;
- treść skilla;
- model;
- temperaturę.

Cache:

- przechowuje wpisy przez maksymalnie 7 dni;
- automatycznie usuwa starsze wpisy przy inicjalizacji;
- raportuje hit/miss;
- pozwala wyczyścić wpisy;
- pozwala wyzerować statystyki;
- degraduje się do trybu wyłączonego przy błędzie SQLite/systemu plików.

## 8. Anulowanie i postęp

`CancellationToken` jest przekazywany przez warstwę aplikacyjną do orkiestratora, wykonawcy i procesora dokumentów.

Anulowanie jest sprawdzane:

- przed rozpoczęciem;
- przed kolejnymi partiami;
- przed jednostkami dokumentu;
- podczas wykonywania przepływu aplikacyjnego.

`TranslationExecutor` stosuje ograniczoną pulę wątków i zachowuje kolejność wyników względem wejścia.

Bridge QML udostępnia postęp, czas, prędkość bieżącą i średnią oraz stan tłumaczenia bez pośrednictwa osobnego `ProgressController`.

## 9. Walidacja wyniku i integralność dokumentu

V4 posiada dwie istotne granice walidacyjne:

- `ResultValidator` — sprawdza wynik backendu, w tym zgodność deklarowanych języków;
- `FilterValidator` + `MarkerValidator` — pilnują jednostek, kompletności targetów i markerów dokumentowych.

W przypadku utraty lub zmiany markerów wynik nie powinien zostać zaakceptowany do rekonstrukcji.

## 10. GUI QML

Aktywna warstwa prezentacji znajduje się w `src/tlumacz/qml_gui/`.

`QmlApplicationBridge` wystawia do QML m.in.:

- wybór backendu;
- profile Cloud i Mozhi;
- parametry llama.cpp;
- ścieżkę GGUF;
- ustawienia tłumaczenia;
- wybór języka docelowego;
- pliki wejścia/wyjścia;
- postęp, czas, prędkość, log i podgląd;
- glosariusz;
- skille systemowe i użytkownika;
- ustawienia i ich reset;
- motyw;
- język aplikacji;
- pomoc i „O programie”;
- start/anulowanie tłumaczenia;
- restart runtime'u llama.cpp.

QML jest warstwą prezentacji. Logika tłumaczenia pozostaje w warstwie aplikacyjnej.

## 11. Glosariusz i skille

Bridge obsługuje:

- ścieżkę glosariusza;
- status glosariusza;
- dodawanie wpisu;
- odświeżanie skilli;
- import skilla;
- usuwanie skilla;
- zapis szablonu skilla.

GUI rozdziela skille systemowe i użytkownika.

Nie należy utożsamiać samej obecności plików `src/tlumacz/skills/*.md` z backendem dokumentowym. Są to zasoby instrukcji używane przez warstwę promptowania/GUI.

## 12. Ustawienia i trwałość

Trwałość ustawień jest obsługiwana przez `AppSettings`/warstwę konfiguracji oraz `QmlApplicationBridge`; usunięte kontrolery `SettingsController`, `DocumentController`, `TranslationController`, `ProgressController` i `DiagnosticsController` nie należą do aktywnego runtime.

W aktualnej powierzchni GUI występują m.in.:

- backend;
- profil Cloud;
- endpoint i klucz;
- GGUF;
- tryb obliczeń;
- szablon czatu;
- równoległość;
- rozmiar fragmentu;
- temperatura;
- prompt;
- wzorce pomijania;
- glosariusz;
- motyw;
- język aplikacji;
- język docelowy;
- ustawienia autostartu/cache/restartu.

## 13. Lokalizacja

V4 ma aktywny system i18n dla PL/EN/DE, z przełączaniem języka aplikacji w runtime. QML korzysta z lokalizowanych etykiet oraz osobnych plików pomocy Markdown `help.<język>.md`.

## 14. Funkcje wycofane

Nie są częścią aktywnego V4:

- FastAPI + Transformers;
- OpenVINO jako backend;
- TranslateGemma INT8 jako osobny runtime/backend;
- V3 `BackendManager` jako model orkiestracji;
- klasyczne `src/tlumacz/qt_gui/`.

Szczegółowy rejestr: `docs/RETIRED_FUNCTIONALITY.md`.

## 15. Zasada interpretacji dokumentacji

Jeżeli starszy dokument mówi inaczej niż aktualny kod V4, za źródło prawdy uznaje się kod i zweryfikowany test. Dokument historyczny pozostaje materiałem dowodowym, a nie instrukcją.

---

## Weryfikacja źródłowa 2026-10-04

Zweryfikowano bezpośrednio:

- `TranslationApp.build_filter_registry()`;
- `DocumentProcessor.process()`;
- `QmlApplicationBridge.start_translation()`;
- `BackendRegistry.ACTIVE_BACKENDS`;
- `CloudProviderRegistry`;
- `MozhiProvider`;
- `TranslationCache`;
- `TranslationOrchestrator`;
- `ApertiumLanguagePlugin` i mapowanie języków;
- `src/tlumacz/language_detector.py` jest aktywny wyłącznie dla `chat_template="translategemma"`; poza tym trybem nie jest używany;
- brak rejestracji filtrów TXT/PDF w aktywnym rejestrze.


### Integralność startu QML — `Main.qml`
`ApplicationWindow` w `Main.qml` posiada jeden handler `Component.onCompleted`. Handler wykonuje oba wymagane działania startowe: przywraca zapisaną pozycję okna (`settingsWindowX`/`settingsWindowY`) oraz uruchamia `showNextFilterDependencyWarning()`. Nie należy dodawać drugiego `Component.onCompleted` w tym samym obiekcie; kolejne operacje startowe należy dopisywać do istniejącego handlera.

Regresja jest chroniona testem `test_qml_main_has_single_component_on_completed_handler`. Walidacja składni QML wykonywana przez `qmllint` nie zgłasza błędów.


### Integralność startu QML — `Main.qml`
`ApplicationWindow` w `Main.qml` posiada jeden handler `Component.onCompleted`. Handler wykonuje oba wymagane działania startowe: przywraca zapisaną pozycję okna (`settingsWindowX`/`settingsWindowY`) oraz uruchamia `showNextFilterDependencyWarning()`. Nie należy dodawać drugiego `Component.onCompleted` w tym samym obiekcie; kolejne operacje startowe należy dopisywać do istniejącego handlera.

Regresja jest chroniona testem `test_qml_main_has_single_component_on_completed_handler`. Walidacja składni QML wykonywana przez `qmllint` nie zgłasza błędów.


### Wskaźnik aktywnego tłumaczenia
Podczas tłumaczenia `TranslationPage.qml` pokazuje animowany wskaźnik aktywnej pracy `translationWorkOrb`: obrót, pulsowanie i zmianę koloru. Szczegóły diagnostyczne pozostają w Logu; tekstowy `translationStageIndicator` nie jest już używany.

Bridge wystawia `translationStage`, `translationBlockCurrent` i `translationBlockTotal`. Źródłem danych są callbacki `on_document_info`, `on_chunk_start` i `on_chunk_complete` z warstwy aplikacyjnej. Prędkość jest liczona w znakach/s na podstawie skumulowanej liczby znaków źródłowych ukończonych bloków.


### Anulowanie lokalnego tłumaczenia llama.cpp
Przycisk „Anuluj” nie ogranicza się do ustawienia kooperacyjnego tokenu anulowania. Dla aktywnego lokalnego runtime llama.cpp wywoływane jest natychmiastowe zatrzymanie procesu należącego do aplikacji, dzięki czemu blokujące oczekiwanie adaptera HTTP zostaje przerwane bez oczekiwania na timeout. Worker raportuje ten przypadek jako anulowanie, a nie błąd tłumaczenia.


## 2026-10-07 — korekta kontraktu rejestru filtrów

Bieżąca implementacja `build_filter_registry()` tworzy `FilterRegistry` oparty o magazyn TPlugin, a nie statyczną listę klas filtrów. Produkcyjne pluginy są odkrywane z `$HOME/.config/tlumacz/filters/` lub ścieżki `TLUMACZ_FILTER_STORE`. Szczegółowy kontrakt znajduje się w `docs/technical-docs/translation-pipeline-contracts.md`.
