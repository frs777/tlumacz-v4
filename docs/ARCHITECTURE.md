## 2026-10-06 — kanoniczny opis detekcji języka i ochrony targetu llama.cpp

Dla llama.cpp obowiązuje następujący kontrakt: `LanguageDetector` z `src/tlumacz/language_detector.py` odpowiada wyłącznie za detekcję Lingua; `LlamaCppLanguageRouting` z `src/tlumacz/backends/llama_cpp/language_routing.py` uruchamia tę detekcję osobno dla każdego chunka; `LlamaCppAdapter` nie wykrywa języka, tylko tłumaczy na podstawie gotowych kodów source/target. Język docelowy nie jest wykrywany. Jest wybierany w GUI i przed rozpoczęciem tłumaczenia `QmlApplicationBridge` wymusza niepusty target dla backendu llama.cpp, normalizując pusty stan do `pl`.

Szczegółowy, kanoniczny opis kroków znajduje się również w `docs/INDEX.md`, w sekcji „Kanoniczny mechanizm detekcji języka dla llama.cpp”.

## 2026-10-06 — separacja detekcji języka dla llama.cpp

Detekcja języka jest niezależnym komponentem `src/tlumacz/language_detector.py` opartym na Lingua. Dla ścieżki llama.cpp powstał osobny `src/tlumacz/backends/llama_cpp/language_routing.py`, który korzysta z detektora i ustala kod ISO 639-1 osobno dla każdego chunka. `LlamaCppAdapter` otrzymuje już ustalony `source_language` i odpowiada wyłącznie za tłumaczenie.

`TranslationApp` używa `LlamaCppLanguageRouting` tylko dla backendu `llama`. Backend `cloud` i `custom` nie korzystają z tego routingu; Apertium zachowuje własną strategię. Usunięto ogólny `DynamicLanguageRouting`, który mieszał odpowiedzialność detekcji z routingiem wielu backendów.

## 2026-10-06 — kontrakt tłumaczenia GUI → llama.cpp

TranslateGemma nie jest językiem. Jest specjalnym trybem/modelowym backendu llama.cpp. Język źródłowy i docelowy pochodzą z konfiguracji tłumaczenia GUI. Dla innych backendów niż Apertium `DynamicLanguageRouting` może wykrywać język źródłowy osobno dla każdego chunka; ustawienie źródła z GUI jest fallbackiem. Język docelowy pozostaje jawnie przekazany do `DocumentTranslationService`, następnie `BackendService` i `LlamaCppAdapter`.

Ścieżki pliku wejściowego i wynikowego nie są parametrami `llama-server`. GUI przekazuje je do `DocumentTranslationService.translate_file()`, który pobiera tekst przez Filter Engine, przekazuje chunki do llama.cpp i zapisuje przetworzony dokument pod wskazaną ścieżką wynikową.

## 2026-10-06 — kontrakt wizualny i persystencja ustawień llama.cpp

Karta „API i serwer” dla llama.cpp traktuje pole „Port” jako jedyne źródło portu runtime. QmlApplicationBridge.serverPort zapisuje wartość do AppSettings.server_port, a serverUrl wylicza z bieżącego hosta i tego portu adres http://<host>:<port>/v1.

Pole „Adres URL” pozostaje polem informacyjnym dla llama.cpp: pokazuje bridge.serverUrl, jest nieedytowalne i nie może nadpisać portu ustawionego w kontrolce „Port”. Dla pozostałych backendów zachowuje dotychczasowy tryb edycji bridge.baseUrl. Restart llama.cpp pobiera settings.server_port, więc uruchomienie serwera i adres prezentowany w GUI korzystają z tego samego źródła konfiguracji.

Techniczny server_host nadal istnieje w AppSettings i jest używany przez runtime llama.cpp, ale nie jest prezentowany jako dodatkowy kontroler w tej karcie. Ustawienia pozostają trwałe: AppSettings odtwarza poprzedni stan przy starcie, a Main.qml wywołuje bridge.saveSettings() przy zamknięciu okna.



Zakładka API i serwer jest źródłem ustawień uruchamianego lokalnie llama.cpp. QmlApplicationBridge przekazuje host, port, plik GGUF, tryb CPU/GPU, parallel, szablon czatu oraz rozmiar bloku. Dla llama.cpp adres API jest wyliczany jako http://<host>:<port>/v1, więc zmiana portu automatycznie zmienia endpoint używany przez adapter.

Techniczne ustawienia runtime pozostają poza GUI w $HOME/.config/tlumacz/llama.json (fallback: config/llama.json). Runtime odczytuje m.in. threads, threads_batch, batch_size, ubatch_size, ctx_size, prompt cache, cache_reuse, Flash Attention, repack, NUMA, GPU layers, KV unified i polling. Wartość auto jest rozstrzygana zgodnie z profilem llama.json; rozmiar kontekstu jest wyliczany z rozmiaru bloku i sekcji ctx_size.

Przy starcie zarządzanego serwera TranslationApp oczekuje na GET /health i uznaje serwer za gotowy dopiero po HTTP 200. Zapobiega to wysyłaniu pierwszego requestu podczas ładowania modelu i eliminuje wyścig powodujący chwilowe Connection refused.

## 2026-10-06 — obowiązujący runtime TranslateGemma

Na aktualnym runtime llama-server 0.4.0-dev (build 10809, commit 5266f24da) ścieżka TranslateGemma V4 używa --no-jinja oraz ręcznie renderowanego promptu Gemma przez /v1/completions. Jest to świadomy kontrakt kompatybilności bieżącego runtime, a nie osobny backend.

Natywny Jinja z wcześniejszego środowiska llama.cpp pozostaje wynikiem historycznym. W bieżącym runtime uruchomienie modelu TranslateGemma z --jinja kończy się błędem automatycznego parsera szablonu, ponieważ modelowy template wymaga typed-content. Nie należy utożsamiać tego z brakiem obsługi TranslateGemma przez aplikację: aktualny kontrakt --no-jinja + /v1/completions został zweryfikowany na realnym GGUF.

LlamaCppLanguageRouting nadal ustala ISO source per chunk, LlamaCppAdapter normalizuje source/target i buduje prompt, a wynik przechodzi wspólny ResultValidator i pipeline dokumentowy.

---
id: architecture-v4
status: active
meta:
  contentType: Architecture
  category: governance
version: 0.40.0
updated: 2026-10-05
owner: platform-architecture
source:
  - src/tlumacz/application/
  - src/tlumacz/backends/
  - src/tlumacz/filter_engine/
  - src/tlumacz/qml_gui/
depends_on: [docs/STATUS.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: zmiana granic warstw lub aktywnego GUI/backendów
last_validation: "Release Candidate gate 2026-10-06; pytest 373 passed, 1 failed; Ruff/mypy/compileall/qmllint PASS; macierz 181 passed; TranslateGemma GUI E2E PASS"
---

## 2026-10-05 — korelacja architektury z aktualnym kodem

`src/tlumacz/qml_gui/` jest aktywną warstwą prezentacji V4. `qml_gui/app.py` uruchamia GUI, `QmlApplicationBridge` udostępnia stan i akcje QML, a `TranslationApp` pozostaje composition rootem warstwy aplikacyjnej.

Aktywne kierunki backendowe to `llama`, `cloud`, `apertium` i `custom`. `custom` korzysta z warstwy CloudRouter, a `translategemma` jest specjalnym `chat_template` dla llama.cpp.

Aktywny `build_filter_registry()` rejestruje DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF. TXT i PDF nie są w tym rejestrze.

Dla llama.cpp `language_detector.py` pozostaje niezależnym detektorem Lingua, a `backends/llama_cpp/language_routing.py` jest jedynym komponentem, który łączy ten detektor z routingiem źródła dla llama.cpp. `LlamaCppAdapter` nie wykonuje detekcji. Cloud, custom i Apertium nie korzystają z routingu llama.cpp.

`SecretStore` jest podłączony do aktywnego QML bridge. Przy migracji starszej konfiguracji `api_key` może zostać przeniesiony do magazynu sekretów.

# Architektura V4

V4 jest niezależną implementacją. Kod V3 nie jest zależnością runtime ani źródłem importów.

## Warstwy

- `domain/` — kontrakty i błędy domenowe.
- `application/` — przypadki użycia, orkiestracja, kontrolery aplikacyjne i lifecycle.
- `backends/` — adaptery providerów tłumaczeniowych.
- `filter_engine/` — registry filtrów, lifecycle sesji, ekstrakcja, walidacja jednostek/markerów i zapis.
- `infrastructure/` — integracje techniczne.
- `qml_gui/` — warstwa prezentacji QML oraz bridge do aplikacji.
- `interfaces/` — interfejsy inne niż aktywny GUI QML.
- `resources/` — zasoby runtime, w tym Java Filter Host i Okapi.

Warstwa aplikacyjna nie zależy od Qt. Backend wykonuje tłumaczenie, ale nie jest właścicielem procesu dokumentowego ani rekonstrukcji.

## Aktywne backendy

Rejestr V4 zawiera:

- `llama` — lokalny llama.cpp;
- `cloud` — router providerów chmurowych;
- `apertium` — lokalny backend Apertium;
- `custom` — własny lokalny lub zdalny endpoint OpenAI-compatible z osobnym adapterem; współdzieli z Cloud wyłącznie transport HTTP.

FastAPI, OpenVINO oraz historyczny model `BackendManager` są wycofane. Zobacz `docs/RETIRED_FUNCTIONALITY.md`.

## Przepływ tłumaczenia dokumentu

```text
QML
 ↓
QmlApplicationBridge
 ↓
TranslationApp
 ↓
BackendSelection + DocumentTranslationService
 ↓
DocumentProcessor
 ↓
FilterRegistry → FilterSession → jednostki
 ↓
TranslationOrchestrator
 ├─ ChunkPlanner
 ├─ PromptBuilder
 ├─ TranslationCache
 ├─ TranslationExecutor
 └─ ResultValidator
 ↓
FilterValidator + MarkerValidator
 ↓
Filter.write()
 ↓
plik wynikowy
```

GUI przekazuje stan i akcje. Nie implementuje logiki tłumaczenia.

## Preprocessor i Filter Engine

Przygotowanie dokumentu jest oddzielone od implementacji filtrów. `src/tlumacz/preprocessing/` wykonuje najpierw `Preprocessor.preflight()`, który wybiera wysokopoziomową ścieżkę natywnego tekstu albo Filter Engine. Dopiero potem `DocumentProcessor` wywołuje `FilterRegistry.for_path()`.

Po `extract()` i walidacji jednostek `Preprocessor.classify_units()` oznacza jednostki jako `TRANSLATE` albo `KEEP`. `KEEP` nie trafia do backendu i wraca do writera z tekstem źródłowym 1:1. Preprocessor nie zna Okapi ani konkretnego filtra i nie odpowiada za ochronę inline-code; ta ochrona pozostaje osobnym mechanizmem.

## Filter Engine i dokumenty

Aktywny rejestr filtrów obejmuje:

| Format | Rozszerzenia | Filtr |
|---|---|---|
| DOCX | `.docx` | `DocxFilter` |
| ODT | `.odt` | `OdtFilter` |
| HTML/XHTML | `.html`, `.htm`, `.xhtml` | `HtmlFilter` |
| Markdown | `.md`, `.markdown` | `MarkdownFilter` |
| EPUB | `.epub` | `EpubFilter` |
| XLIFF 2.0 | `.xlf`, `.xliff` | `XliffFilter` |

TXT i PDF nie są obecnie zarejestrowane w aktywnym `FilterRegistry`; nie należy przedstawiać ich jako obsługiwanych przez główny pipeline bez osobnej implementacji.

Java Filter Host pozostaje izolowanym komponentem runtime dla integracji Okapi. Python komunikuje się z nim przez wersjonowany protokół JSON Lines.

## Język źródłowy

V4 posiada parametr `source_language` oraz izolowany moduł `src/tlumacz/language_detector.py`, który realizuje detekcję Lingua. Dla llama.cpp `src/tlumacz/backends/llama_cpp/language_routing.py` wykonuje detekcję osobno dla każdego chunka i przekazuje wykryty kod ISO 639-1 do adaptera. `LlamaCppAdapter` nie wykonuje detekcji. Cloud i custom nie korzystają z routingu llama.cpp, a Apertium ma własny routing.

W trybie TranslateGemma adapter otrzymuje już ustalony kod źródłowy i docelowy. `auto` nie jest dozwolone w kontrakcie adaptera TranslateGemma.

## llama.cpp

`TranslationApp` zarządza opcjonalnym `LlamaCppRuntimeManager`:

- start;
- stop;
- restart;
- health-check;
- kontrola własności procesu;
- konfiguracja modelu GGUF, portu, trybu obliczeń, równoległości i szablonu czatu.

`translategemma` jest szablonem czatu llama.cpp, a nie osobnym backendem.

## Cloud

`CloudRouter` korzysta z `CloudProviderRegistry`. Aktualne adaptery to OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate i DLX.

Mozhi jest osobnym providerem Cloud i obsługuje wybór instancji oraz silnika.

## Apertium

Apertium ma własny adapter/backend, kontrakt, relokowalny runtime, discovery pakietów językowych i mapowanie kodów ISO. Nie uruchamia lifecycle llama.cpp.

Bundlowana dystrybucja 0.40.0 zawiera zamknięty runtime Apertium 3.9.12 oraz zweryfikowaną parę eng-pol: mode, automorf/autobil, transfer t1/t2/t3 i generację. eng-pol jest kierunkowy; dostępność pary wynika z aktywnych danych runtime.

Weryfikacja release: clean install wheel → discovery eng-pol → rzeczywiste tłumaczenie przez ApertiumAdapter i Filter Engine.

## Cache i anulowanie

`TranslationCache` jest współbieżnym cache SQLite z 7-dniowym TTL. Klucz uwzględnia tekst, prompt, skill, model i temperaturę.

`CancellationToken` jest respektowany przez orkiestrację oraz przetwarzanie dokumentu. `TranslationExecutor` wykonuje jednostki z ograniczoną współbieżnością i zachowuje ich kolejność.

## Aktywne GUI QML

Aktywny entrypoint GUI korzysta z `src/tlumacz/qml_gui/app.py`.

`QmlApplicationBridge` udostępnia QML m.in.:

- backendy i profile Cloud/Mozhi;
- konfigurację llama.cpp;
- pliki wejścia/wyjścia;
- język docelowy;
- postęp, czas, prędkość, log i podgląd;
- glosariusz;
- skille systemowe i użytkownika;
- ustawienia i reset;
- motyw i język aplikacji;
- pomoc;
- start/anulowanie tłumaczenia;
- restart llama.cpp według bieżącej konfiguracji GUI;
- lifecycle llama.cpp: ręczny wybór backendu uruchamia serwer, zmiana na inny backend go zatrzymuje, a autostart przy uruchomieniu programu zależy wyłącznie od checkboxa „Automatyczny start llama.cpp”.

Klasyczne `src/tlumacz/qt_gui/` zostało usunięte po zakończeniu migracji QML.

## Lokalizacja

System i18n obsługuje PL/EN/DE. Pomoc użytkownika jest ładowana z lokalizowanych plików Markdown `help.<język>.md`.

## Bootstrap i dystrybucja

Źródłem pakietu jest wyłącznie `src/tlumacz/`. V3 pozostaje osobnym drzewem referencyjnym.

Dystrybucja 0.40.0 jest przygotowana jako Linux Release Candidate. Szczegóły runtime'u, packagingu i otwartych blockerów znajdują się w `docs/STATUS.md`.

## Dokumenty powiązane

- `docs/technical-docs/functional-capabilities.md` — pełna macierz funkcjonalna kodu;
- `docs/technical-docs/index.md` — mapa dokumentacji technicznej;
- `docs/RETIRED_FUNCTIONALITY.md` — funkcje wycofane;
- `docs/STATUS.md` — bieżący stan projektu.

## 2026-10-06 — pełne rozstrzyganie ustawień auto llama.cpp

Rozdzielenie konfiguracji pozostaje obowiązujące: GUI przekazuje ustawienia operacyjne (host, port, GGUF, CPU/GPU, parallel, szablon czatu i rozmiar bloku), natomiast $HOME/.config/tlumacz/llama.json dostarcza tuning techniczny. Dodano rzeczywiste rozstrzyganie threads=auto według reguły cpu_threads=rdzenie_fizyczne oraz threads_batch=auto według cpu_threads_batch=watki_logiczne. Wartości jawne w llama.json nadal mają pierwszeństwo przed trybem auto.

## 2026-10-06 — własność ścieżki GGUF

Ścieżka do modelu GGUF jest parametrem wybieranym przez GUI. GUI przekazuje wybraną ścieżkę do konfiguracji aplikacji; wartość jest utrwalana w $HOME/.config/tlumacz/config.json. llama.json nie jest źródłem ścieżki modelu — pozostaje źródłem wyłącznie technicznego tuningu llama.cpp.


## 2026-10-07 — integralność chunku i fallback

TranslationOrchestrator traktuje logiczny chunk jako jednostkę transakcyjną. Jeżeli dostępny jest translate_batch, pierwsza nieudana próba batcha nie uruchamia jeszcze fallbacku jednostkowego. Ten sam chunk jest wysyłany ponownie dokładnie raz. Dopiero po dwóch nieudanych próbach całego chunka wykonywane jest tłumaczenie jednostka po jednostce.

Reguły integralności:

- retry dotyczy całego nieudanego chunka, bez częściowego mieszania wyników z prób;
- fallback jednostkowy zachowuje kolejność jednostek;
- wynik bez jednostki nie może zostać zwrócony jako częściowy sukces;
- identyfikatory jednostek muszą być unikalne;
- każdy wynik przechodzi istniejącą walidację języka, pustego wyniku i markerów przed zapisaniem do wyniku końcowego;
- postęp chunka jest raportowany dopiero po przetworzeniu wszystkich jednostek tego chunka.

Celem jest wyeliminowanie cichego pomijania fragmentów oraz ograniczenie przedwczesnego przechodzenia z batcha do kosztownego trybu jednostkowego.


## 2026-10-07 — budżet CPU llama.cpp dla równoległych slotów

Host projektu ma 8 rdzeni fizycznych i 16 wątków logicznych. `parallel` nie jest ustawieniem technicznego tuningu CPU: jego wartość pochodzi z GUI i określa liczbę równoległych slotów/requestów. Dla profilu referencyjnego V3 ustawienia llama.cpp są odzyskane z dokumentacji `docs/wdrozenia/rekomendacja-ustawien-llama.cpp.md`: `threads=8`, `threads_batch=16`, `batch_size=2048`, `ubatch_size=512`. `ctx-size` pozostaje dynamiczny i jest wyliczany z parametrów dokumentu. Wartości jawne w `llama.json` mają pierwszeństwo przed automatycznym rozstrzyganiem runtime.

## 2026-10-07 — rejestr backendów jako rozszerzalny punkt kompozycji

BackendRegistry nie zawiera już routingu typu if backend == ... dla aktywnych implementacji. Backend jest rejestrowany jako adapter w mapie instancji, a wspólna metoda translate() deleguje do zarejestrowanej implementacji. BackendService pobiera aktywne identyfikatory dynamicznie z rejestru.

Wspólny kontrakt domenowy pozostaje TranslationBackend, a BackendCapabilities dostarcza deklaratywny opis możliwości. Rejestr udostępnia capabilities() oraz health_check() niezależnie od konkretnej implementacji.

Nowy backend może zostać przekazany do BackendRegistry przez parametr backends albo dodany metodą register(). Test kontraktowy TestBackend potwierdza, że tłumaczenie i health-check nowej implementacji działają bez zmian w pipeline dokumentowym.

### Backend „Własny”

Backend custom został wydzielony do src/tlumacz/backends/custom/backend.py. Jest przeznaczony dla własnego lokalnego lub zdalnego serwera OpenAI-compatible. Nie jest providerem Cloud. Adapter custom współdzieli wyłącznie OpenAICompatibleProvider jako transport HTTP, ale ma własną konfigurację granicy backendu, walidację endpointu/modelu, health-check i metadane wyniku.

Cloud nadal posiada własny CloudRouter i CloudProviderRegistry. Providerzy Cloud nie są mieszani z backendem custom.

Docelowy przepływ rozszerzalności:

BackendContract
→ BackendRegistry
→ konkretny adapter backendu
→ BackendResult
→ ResultValidator / MarkerValidator
→ Filter.write()

Dodanie backendu nie wymaga zmian w DocumentProcessor, Filter Engine, ChunkPlanner, TranslationOrchestrator, TranslationExecutor ani writerach.


## 2026-10-07 — konfiguracja backendu odseparowana od wspólnego kontraktu

`BackendRequest` i `BackendSelection` zawierają teraz wyłącznie identyfikator backendu oraz `BackendConfiguration`. Wspólny model nie posiada pól takich jak `provider`, `base_url`, `model`, `engine`, `timeout`, `compute_mode`, `chat_template` czy `parallel`.

`BackendConfiguration` jest nieprzezroczystym kontenerem konfiguracji backendu. Konkretna implementacja interpretuje własne klucze na swojej granicy. Dzięki temu dodanie nowego backendu nie wymaga rozszerzania `BackendRequest`, `BackendSelection` ani centralnego pipeline'u o kolejne pola specyficzne dla implementacji.

Aktualny przepływ ma postać:

BackendRequest(backend, configuration)
→ BackendService
→ BackendSelection(backend, configuration)
→ BackendRegistry
→ adapter konkretnego backendu
→ BackendResult

GUI przygotowuje konfigurację dla wybranego backendu, ale nie zmienia kontraktu wspólnego. `custom` otrzymuje własną konfigurację endpointu/modelu, Cloud własną konfigurację providera, a llama.cpp własną konfigurację runtime.

Regresja jest zabezpieczona testami, które wymagają, aby zarówno `BackendRequest`, jak i `BackendSelection` miały wyłącznie pola `backend` i `configuration`.
