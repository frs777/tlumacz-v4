---
id: kompendium-wiedzy-projektu-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 1.0.0
updated: 2026-10-07
owner: project-documentation
source: src/tlumacz/, docs/, /home/frs/Projekty/agent-translator-v3/docs/, /home/frs/Projekty/agent-translator-v3/tlumacz/
depends_on: [docs/ARCHITECTURE.md, docs/STATUS.md, docs/technical-docs/translation-pipeline-contracts.md, docs/technical-docs/plugin-okapi-filter.md, docs/technical-docs/apertium-pair-packages.md]
expires_when: zmiana architektury V4 lub aktywnego kontraktu backendów, filtrów albo GUI
last_validation: "inspekcja kodu i dokumentacji SentinelX 2026-10-07; pytest 599 passed in 99.93s; compileall PASS; mypy PASS; qmllint PASS; Ruff: 2 istniejące błędy w tests/test_tplugin_create.py"
---

# Tłumacz V4 — rozszerzone kompendium wiedzy technicznej

## 1. Cel i zakres

Niniejszy dokument jest skonsolidowanym kompendium wiedzy o aktualnym Tłumaczu V4. Łączy informacje z bieżącego kodu źródłowego, aktualnej dokumentacji V4 oraz materiałów V3 wykorzystanych jako źródło doświadczeń projektowych.

Zasada nadrzędna: opisujemy tylko rozwiązania istniejące w aktualnym V4. Materiały V3 służą do wyjaśnienia genezy decyzji, wzorców, benchmarków i doświadczeń, ale nie są podstawą do deklarowania funkcji, których V4 obecnie nie implementuje.

## 2. Model produktu

Tłumacz V4 jest desktopową aplikacją do tłumaczenia dokumentów. Jej zasadniczą cechą jest oddzielenie prezentacji, orkiestracji aplikacyjnej, backendu tłumaczeniowego, przygotowania i rekonstrukcji dokumentu oraz infrastruktury lokalnej.

Aktywne klasy backendów:
- llama — lokalny serwer llama.cpp;
- cloud — usługi zewnętrzne z rejestrem providerów;
- apertium — lokalny, regułowy backend Apertium;
- custom — własny lokalny lub zdalny serwer OpenAI-compatible.

TranslateGemma nie jest backendem. Jest specjalnym trybem/modelowym obsługiwanym przez adapter llama.cpp.

## 3. Założenia architektoniczne

### Stabilne kontrakty
domain/contracts.py definiuje wspólne kontrakty. Backend nie powinien być rozpoznawany przez rozbudowane warunki zależne od nazwy. BackendRegistry udostępnia możliwości backendu, a konfiguracja specyficzna dla implementacji jest przekazywana jako BackendConfiguration.

### Composition root
TranslationApp jest composition rootem warstwy aplikacyjnej. Składa BackendService, BackendController, DocumentTranslationService, FilterRegistry, TranslationCache i lifecycle llama.cpp. Warstwa aplikacyjna nie zależy od Qt.

### Separacja dokumentu od MT
Backend otrzymuje jednostki tekstowe, a nie odpowiedzialność za format dokumentu. Filtr otwiera dokument, ekstraktuje jednostki, zachowuje metadane, odbiera wyniki i rekonstruuje dokument.

### Walidacja
Walidacja jest elementem kontraktu. Jednostki, markery, wyniki backendu i cele zapisu są sprawdzane na kolejnych granicach pipeline'u.

## 4. Struktura kodu

| Obszar | Rola |
|---|---|
| application/ | przypadki użycia, orkiestracja, routing języka, cache, executor |
| backends/llama_cpp/ | adapter i lifecycle llama.cpp |
| backends/cloud/ | providerzy Cloud, router i Mozhi |
| backends/apertium/ | adapter, runtime, języki i pakiety Apertium |
| backends/custom/ | backend własnego serwera OpenAI-compatible |
| domain/ | stabilne kontrakty i błędy domenowe |
| filter_engine/ | ekstrakcja, rekonstrukcja, registry, lifecycle, Okapi |
| documents/ | wewnętrzna obsługa XLIFF 2.0 |
| preprocessing/ | preflight i klasyfikacja KEEP/TRANSLATE |
| infrastructure/ | logowanie i magazyn sekretów |
| qml_gui/ | Qt Quick/QML i bridge |
| skills/ | wbudowane skille tłumaczeniowe |
| i18n.py | lokalizacja PL/EN/DE |
| language_detector.py | wspólny prymityw detekcji języka |
| user_config.py | inicjalizacja konfiguracji użytkownika |

## 5. Pipeline tłumaczenia dokumentu

plik wejściowy → Preprocessor.preflight() → FilterRegistry.for_path() → FilterLifecycle → extract() → walidacja jednostek → classify_units() → KEEP/TRANSLATE → TranslationOrchestrator → ChunkPlanner → cache/TranslationExecutor → backend → ResultValidator → restore markerów → FilterValidator → writer → plik wynikowy.

### Preprocessor
TRANSLATE może wejść do backendu. KEEP nie jest przekazywane do backendu i wraca 1:1. Puste jednostki są KEEP. Wzorce pomijania są kompilowane centralnie.

### Chunking i batch
chunk_size jest limitem planera w znakach. Dla TranslateGemma jeden batch odpowiada jednemu logicznemu chunkowi i jednemu source. Odpowiedź musi zachować wszystkie markery dokładnie raz i w tej samej kolejności. Po dwóch nieudanych prób batchu następuje fallback jednostkowy.

### Executor
TranslationExecutor wykonuje jednostki z ograniczoną współbieżnością.

### Cache
TranslationCache używa SQLite. Klucz uwzględnia m.in. tekst, prompt, skill, model, temperaturę i source language.


## 5A. Indeks etapów pipeline

| ID | Etap | Implementacja | Opis |
|---|---|---|---|
| P0 | Wejście | `DocumentTranslationService` | Przyjęcie ścieżki i parametrów tłumaczenia |
| P1 | Preflight | `Preprocessor.preflight()` | Wstępna walidacja i przygotowanie dokumentu |
| P2 | Wybór filtra | `FilterRegistry.for_path()` | Dobór aktywnego filtra po rozszerzeniu |
| P3 | Ekstrakcja | `FilterLifecycle.extract()` | Zamiana dokumentu na jednostki tłumaczeniowe |
| P4 | Walidacja jednostek | `FilterValidator` / kontrakty domenowe | Sprawdzenie poprawności jednostek i metadanych |
| P5 | Klasyfikacja | `Preprocessor.classify_units()` | Podział na KEEP i TRANSLATE |
| P6 | Ochrona treści | filtry / marker protection | Ochrona inline codes i elementów nietłumaczalnych |
| P7 | Planowanie | `ChunkPlanner` | Budowa logicznych chunków/batchy |
| P8 | Cache | `TranslationCache` | Odczyt wcześniej uzyskanych wyników |
| P9 | Wykonanie | `TranslationExecutor` | Ograniczona współbieżność jednostek |
| P10 | Backend | `BackendRegistry` + adapter | Wykonanie tłumaczenia przez wybrany backend |
| P11 | Walidacja wyniku | `ResultValidator` / `MarkerValidator` | Kontrola odpowiedzi i markerów |
| P12 | Restore | warstwa filtra | Przywrócenie chronionych elementów |
| P13 | Rekonstrukcja | aktywny filtr | Wstawienie wyników do struktury dokumentu |
| P14 | Zapis | writer filtra | Utworzenie dokumentu wynikowego |
| P15 | Raportowanie | warstwa aplikacyjna/GUI | Przekazanie postępu, statystyk i błędów |

## 5B. Schemat głównego przepływu tekstu

```text
[P0 Plik wejściowy]
        │
        ▼
[P1 Preflight]
        │
        ▼
[P2 FilterRegistry]
        │
        ▼
[P3 Ekstrakcja]
        │
        ▼
[P4 Walidacja jednostek]
        │
        ▼
[P5 KEEP / TRANSLATE]
        │
        ├────────────── KEEP ──────────────┐
        │                                  │
        ▼                                  │
[P6 Ochrona markerów]                     │
        │                                  │
        ▼                                  │
[P7 ChunkPlanner]                          │
        │                                  │
        ▼                                  │
[P8 Cache] ───── hit ─────────────────────┤
        │ miss                             │
        ▼                                  │
[P9 TranslationExecutor]                   │
        │                                  │
        ▼                                  │
[P10 Backend]                              │
        │                                  │
        ▼                                  │
[P11 Walidacja wyniku]                     │
        │                                  │
        ▼                                  │
[P12 Restore] ◄────────────────────────────┘
        │
        ▼
[P13 Rekonstrukcja]
        │
        ▼
[P14 Zapis]
        │
        ▼
[P15 Wynik / raport]
```

**Odniesienie:** szczegóły każdego etapu znajdują się w sekcjach 5, 6, 12–21, 24–27 oraz 38 tego dokumentu. Kontrakty graniczne opisuje `docs/technical-docs/translation-pipeline-contracts.md`.

## 5C. Przepływ z rozgałęzieniem backendu

```text
                         ┌─ llama.cpp ──► TranslateGemma / model lokalny
                         │
[P7 Chunk] ─► [P10 Backend] ├─ Cloud ─────► provider / Mozhi
                         │
                         ├─ Apertium ──► zamrożona para source→target
                         │
                         └─ Własny ────► OpenAI-compatible server
```

**Odniesienia:** llama.cpp — §7–8; Cloud/Mozhi — §9–10; Apertium — §11; Własny — §6 oraz dokumentacja backendu custom; wspólny kontrakt — §3 i `translation-pipeline-contracts.md`.

## 5D. Przepływ dokumentu przez Filter Engine

```text
plik
 │
 ▼
FilterRegistry.for_path()
 │
 ├─ native Markdown ───────► MarkdownFilter
 ├─ native Plain Text ─────► PlainTextFilter
 ├─ native HTML/XHTML ─────► HtmlFilter
 │
 └─ Okapi ─► TPlugin ─► Java Filter Host ─► OkapiFilter
                                      │
                                      ▼
                              jednostki + metadane
                                      │
                                      ▼
                              pipeline tłumaczenia
                                      │
                                      ▼
                              rekonstrukcja + zapis
```

**Odniesienia:** Filter Engine — §12; Okapi/Java — §13; TPlugin — §14; ochrona inline codes — §15; formaty natywne — §16–19.

## 5E. Przepływ markerów inline codes

```text
PUA Okapi
   │
   ▼
__OKAPI_CODE_N__
   │
   ▼
prompt / backend
   │
   ▼
odpowiedź
   │
   ▼
MarkerValidator
   │
   ├─ OK ─────► restore PUA
   └─ błąd ───► retry / fallback jednostkowy
```

**Odniesienie:** §15 oraz kontrakty pipeline'u.

## 6. Backend Registry i rozszerzalność

BackendRegistry przechowuje backendy i ich możliwości. BackendCapabilities pozwala pytać o możliwości bez znajomości implementacji.

Backend Własny znajduje się w backends/custom/backend.py. Jest niezależnym backendem dla serwerów OpenAI-compatible i współdzieli transport z Cloud bez bycia providerem Cloud.

## 7. Llama.cpp

Lokalny backend zarządza procesem llama-server. V4 uruchamia, zatrzymuje, restartuje i sprawdza gotowość serwera przez HTTP /health.

Runtime jest domyślnie bundlowany. Konfiguracja techniczna to $HOME/.config/tlumacz/llama.json, a szablon repozytorium to config/llama.json.

Aktualne wartości bazowe:
- threads=8;
- threads_batch=16;
- batch_size=2048;
- ubatch_size=512;
- ctx_size=auto;
- prompt cache włączony;
- cache_reuse=0;
- Flash Attention off;
- repack on;
- NUMA auto;
- GPU layers auto;
- unified KV auto;
- KV K=q8_0, V=f16 w profilu automatycznym.

Są to wartości startowe, nie uniwersalne optimum.

### TranslateGemma
TranslateGemma jest trybem llama.cpp. Aktualna ścieżka używa ręcznie renderowanego promptu i /completions. Source i target muszą być jednoznaczne; auto nie trafia do adaptera.

## 8. Strojenie llama.cpp

Obowiązuje: baseline → jedna hipoteza → pomiar → zmiana → pomiar → regresja.

### CPU
Nie zwiększać threads do maksimum bez pomiaru. Doświadczenia V3 wskazywały, że ograniczeniem może być pamięć lub charakter obciążenia.

Procedura:
1. zmierz 1/2/4/8 threads;
2. oddziel prompt processing od generation;
3. mierz czas całego dokumentu;
4. sprawdź RAM;
5. wybierz konfigurację dającą najlepszy wynik praktyczny.

### GPU
gpu_layers=auto jest punktem startowym. Przy ręcznym strojeniu zwiększaj offload do granicy pamięci i mierz stabilność oraz czas ładowania.

### Parallel
parallel oznacza liczbę slotów serwera. CPU llama.cpp działa seryjnie, GPU może używać skonfigurowanego poziomu równoległości. Benchmark V3 pokazał, że np=4 zwiększał throughput, ale także opóźnienie pojedynczego requestu.

### Batch, ubatch, KV, Flash Attention
Punkt startowy to batch_size=2048 i ubatch_size=512. Zmiany wykonuj pojedynczo. Profil KV używa q8_0 dla K i f16 dla V. Mocniejszą kompresję oceniaj razem z jakością i kompletnością. Flash Attention pozostaje off bez benchmarku.

mmap pozostawiaj domyślnie. no-mmap stosuj tylko przy konkretnym problemie. mlock stosuj tylko przy wystarczającym RAM. no-warmup oceniaj przez całkowity czas operacji.

## 9. Cloud

Cloud składa się z CloudProviderRegistry, CloudRouter, wspólnego kontraktu providera, adapterów transportowych i SecretStore.

Aktualny zestaw obejmuje transport OpenAI-compatible oraz adaptery DeepL, Microsoft, MyMemory, LibreTranslate, DLX i Mozhi.

Sekrety nie należą do profili JSON.

Pomiary V4 wykazały, że lokalny koszt konstrukcji routera, rejestru i serializacji jest mały wobec RTT usługi zewnętrznej. Health-check Cloud jest lokalnym HealthCheckResult.ok("cloud") i nie generuje ukrytego ruchu sieciowego.

## 10. Mozhi

Tryb auto Mozhi:
1. sprawdza znane instancje;
2. weryfikuje API;
3. sprawdza silnik i języki;
4. wykonuje kontrolne tłumaczenie;
5. mierzy odpowiedź;
6. odrzuca błędne lub puste odpowiedzi;
7. wybiera najszybszą poprawną instancję;
8. przy braku poprawnej instancji używa instancji awaryjnej.

Ręcznie wskazana instancja omija automatyczny wybór.

## 11. Apertium

Apertium jest lokalnym backendem regułowym. Korzysta z danych językowych i reguł, a nie z modelu LLM. Jest deterministyczne, małe i zależne od konkretnej pary.

Aktualny magazyn użytkownika zawiera 28 artefaktów kierunków, m.in. bn-en, en-bn, eng-cat, cat-eng, eng-deu, deu-eng, eng-ita, ita-eng, eng-spa, spa-eng, en-pt, pt-en, pl-csb, csb-pl, pl-sk, sk-pl, pol-ces, ces-pol, pol-rus, rus-pol, pol-szl, szl-pol, pol-ukr, ukr-pol, pol-spa, spa-pol oraz eng-pol.

### TAR-only
Trwałym artefaktem jest .tar wraz z .tar.sha256 w $HOME/.config/tlumacz/apertium/. Dane są materializowane tymczasowo.

### Routing
Apertium ustala source dokumentu, wybiera target, zamraża parę source → target, a detekcję chunkową wykorzystuje tylko do decyzji tłumacz/pomiń. Inny język chunku pozostaje bez zmian.

### Pakietowanie
repozytorium Apertium → kompilacja → walidacja → .tar + .sha256 → magazyn użytkownika → materializacja tymczasowa → runtime.

## 12. Filter Engine

Najważniejsze komponenty: FilterRegistry, FilterLifecycle, DocumentProcessor, FilterValidator, MarkerValidator, FilterHostClient, FilterStore, TPlugin i OkapiFilter.

Registry stosuje lazy instancjonowanie. Plugin Okapi może przejąć rozszerzenie native fallback.

Aktywne ścieżki natywne:
- Markdown: .md, .markdown;
- Plain Text: .txt, .text, .log;
- HTML/XHTML: .html, .htm, .xhtml.

Aktywne pakiety Okapi:
- EPUB;
- JSON;
- OpenOffice;
- OpenXML;
- YAML.

XLIFF nie jest filtrem wejściowym FilterRegistry.

## 13. Okapi i Java Filter Host

Okapi jest izolowane jako komponent runtime. Python komunikuje się z Java Filter Host przez wersjonowany JSON Lines. Cold-start JVM jest kosztem jednorazowym; po rozgrzaniu IPC jest małym kosztem.

## 14. TPlugin

.tplugin jest formatem dystrybucyjnym pluginu filtra. Aktualny magazyn pakietów to $HOME/.config/tlumacz/filters. Pakiet jest artefaktem transportowym, a runtime może zostać rozpakowany do /tmp/filters/. Wspólne JAR-y Okapi znajdują się w src/tlumacz/resources/okapi-runtime/lib/.

Manifest opisuje format, wersję, identyfikator, rozszerzenia, wersję engine, zależności i entrypoint. Integralność i kompatybilność muszą być sprawdzane przed użyciem.

## 15. Ochrona inline codes

Przed backendem generatywnym reprezentacja PUA Okapi jest zamieniana na markery ASCII __OKAPI_CODE_N__. Po odpowiedzi markery są walidowane i przywracane.

Wymagana jest zgodność liczby, tożsamości i kolejności. Brakujący lub dodatkowy marker jest błędem. Nie stosuje się automatycznego dopisywania markerów.

## 16. Markdown

Markdown korzysta z natywnego MarkdownFilter, bez Okapi.

protect → split → translate → restore

Filtr zachowuje strukturę Markdown, w tym bloki kodu i elementy nietłumaczalne.

## 17. HTML i lxml

HTML ma natywny filtr z deterministycznym mapowaniem slotów tekstowych i nie uruchamia Java Filter Host.

lxml zapewnia parsery XML/HTML i XPath oraz jest używane jako infrastruktura przetwarzania struktur dokumentowych.

## 18. Plain Text

Plain Text obsługuje .txt, .text i .log. Niepuste linie są jednostkami tłumaczeniowymi. Puste linie i kolejność są zachowywane.

## 19. EPUB, ODT, DOCX i struktury

V4 posiada EpubFilter, OdtFilter, DocxFilter i OkapiFilter. Dla formatów strukturalnych najważniejsze są stabilne identyfikatory, metadane, ochrona elementów nietłumaczalnych, rekonstrukcja i walidacja.

## 20. XLIFF 2.0

src/tlumacz/documents/xliff.py implementuje wewnętrzną obsługę XLIFF 2.0. XLIFF nie jest filtrem wejściowym FilterRegistry.

## 21. Detekcja języka

Wspólnym prymitywem jest LanguageDetector oparty na Lingua.

DynamicLanguageRouting analizuje każdy chunk niezależnie i może zmieniać source. ApertiumLanguageRouting ustala source dokumentu i zamraża parę. Rozdzielenie pozwala obsługiwać dokumenty wielojęzyczne bez naruszania kontraktu Apertium.

## 22. Skille

Skille są elementem pipeline'u promptowego. Jeden skill powinien odpowiadać jednemu problemowi. Instrukcje powinny być jednoznaczne. Nie należy wkładać całej dokumentacji projektu do promptu. Placeholdery powinny być chronione technicznie.

## 23. Glosariusz

Glosariusz jest opcjonalnym elementem kontekstu. Zalecane są glosariusze tematyczne zamiast ogromnego globalnego słownika. Konfiguracja posiada limit wpisów i narzut promptowy.

## 24. GUI QML

Aktywne GUI znajduje się w qml_gui/. Główne elementy to Main.qml, TranslationPage.qml, ApiPage.qml, ExtrasPage.qml, HelpPage.qml, HelpMarkdownView.qml, QmlApplicationBridge i qml_gui/app.py.

Bridge udostępnia stan aplikacji, ustawienia, backendy, lifecycle llama.cpp, skills, glosariusz, pomoc, lokalizację i motyw.

Obsługiwane motywy: systemowy, jasny i ciemny. Dla Fusion tryby jasny i ciemny ustawiają komplet ról palety. Systemowy pozostawia paletę natywną. Material nie jest wymuszany.

System i18n obsługuje PL/EN/DE. Pomoc jest w help.pl.md, help.en.md i help.de.md. Teksty GUI są wydzielane do qml_gui/texts/<język>/.

## 25. Konfiguracja

Główna konfiguracja: $HOME/.config/tlumacz/config.json.
Konfiguracja llama.cpp: $HOME/.config/tlumacz/llama.json.
Sekrety: $HOME/.config/tlumacz/.key.
Paczki Apertium: $HOME/.config/tlumacz/apertium/.
Pluginy filtrów: $HOME/.config/tlumacz/filters/.
Runtime tymczasowy: /tmp/filters/.

Zalecenia:
- lokalny llama.cpp: parallel=1 na CPU, temperatura 0.0, umiarkowany chunk, właściwy skill;
- Apertium: konkretna gotowa para i poprawny checksum;
- Cloud: provider zgodny z API, klucz przez SecretStore;
- Mozhi: auto, gdy priorytetem jest dostępność;
- Własny: Base URL OpenAI-compatible i model udostępniany przez serwer.

## 26. Bezpieczeństwo i logowanie

Sekrety nie należą do JSON. SecretStore współpracuje z redakcją logów.

Centralne logowanie:
- poziom DEBUG;
- redakcja sekretów;
- redakcja nagłówków autoryzacyjnych;
- redakcja parametrów URL;
- brak treści dokumentów i payloadów użytkownika.

## 27. Anulowanie i lifecycle

V4 używa CancellationToken. FilterHostClient używa niedemonicznych reader threads. close() kończy proces potomny, zamyka pipe'y i wykonuje join.

## 28. Optymalizacje potwierdzone

Najważniejsza optymalizacja pipeline'u: batchowanie DocumentTranslationService. Kontrolowany benchmark wykazał 200 → 1 przebiegów orchestratora oraz redukcję czasu 0,048947 s → 0,009530 s, około 80,5%.

Pozostałe bezpieczne optymalizacje to lazy instantiation filtrów oraz rozdzielenie runtime od danych.

## 29. Wnioski z benchmarków

Nie wykazano potrzeby zmiany produkcyjnych parametrów llama.cpp, Cloud, Filter Host IPC ani QML bez dalszego workload-specific benchmarku.

Nie należy usuwać walidacji dla szybkości. Maksymalna liczba threads/slotów nie jest automatycznie najlepsza.

### 29A. Wnioski z analizy katalogów testowych V4 i V3

Analizę wykonano w trybie bliskiego czytania materiału dowodowego: najpierw zmapowano strukturę katalogów i rozdzielono wyniki od planów, logów oraz materiałów archiwalnych, następnie porównano wyniki reprezentatywnych testów V3 z aktualnymi materiałami V4. Wnioski poniżej są transferem doświadczeń testowych, a nie deklaracją, że historyczny wynik V3 jest aktualnym wynikiem V4.

#### 29A.1. V4 — obecny materiał dowodowy

Katalog `docs/Testy` zawiera zarówno świeże wyniki, jak i rozbudowany materiał benchmarkowy llama.cpp. Najważniejsze aktualne klasy dowodów to:

- testy funkcjonalne i regresyjne;
- benchmarki CPU llama.cpp;
- serie A/B parametrów serwera;
- testy `parallel`, batch/ubatch, Flash Attention, KV, cache, mmap, kontekstu i NUMA;
- testy rzeczywistego workloadu Tłumacza;
- testy filtrów i Apertium;
- dane surowe wraz z logami serwera.

W materiałach V4 obowiązuje ważna zasada kwalifikacji: plan, nieukończony przebieg, anomalia albo wynik bez pełnej kontroli nie może być przedstawiany jako benchmark rozstrzygający. Jest to szczególnie widoczne w materiałach dotyczących CPU-native, gdzie niekompletne próby zostały jawnie wyłączone z tabel porównawczych.

#### 29A.2. V3 — najważniejsze doświadczenia jakościowe

Historyczne testy V3 wykazały, że sama szybkość backendu nie jest wystarczającą metryką dla aplikacji dokumentowej. Wynik trzeba oceniać co najmniej według pięciu wymiarów:

1. kompletność treści;
2. zgodność znaczeniowa;
3. poprawność językowa;
4. zachowanie struktury/formatu;
5. oznaki obcięcia, halucynacji lub wycieku protokołu.

W serii testów formatów występowały przypadki, w których wynik był formalnie wygenerowany, ale nie spełniał kryterium kompletności. Szczególnie istotny był HTML: struktura techniczna mogła być zachowana bardzo dobrze, a mimo to końcowa część powtarzającej się treści była pomijana. Wniosek przeniesiony do V4: **integralność dokumentu ma pierwszeństwo przed samym czasem wykonania**.

Testy wykazały też różnicę między błędem modelu a błędem warstwy dokumentowej. Jeżeli ten sam materiał jest kompletny w innych formatach, a jeden format traci treść, należy najpierw badać ścieżkę ekstrakcji, chunkowania, rekonstrukcji i walidacji tego formatu, zamiast automatycznie przypisywać problem modelowi.

#### 29A.3. V3 — lekcje z testów `parallel` i kontekstu

Seria rzeczywistego tłumaczenia dokumentu pokazała:

- `parallel=1` zachowywało kompletność, ale było najwolniejsze;
- `parallel=2` skróciło czas bez obserwowanej degradacji kompletności;
- `parallel=4` dało dalsze skrócenie czasu przy zachowaniu 100% kompletności w badanym workloadzie;
- `parallel=8` dało krótszy czas ścienny, ale zmniejszenie `n_ctx_slot` do 1024 doprowadziło do obcięcia wyników i utraty treści.

Wniosek metodologiczny jest ważniejszy od konkretnej liczby: **nie wolno wybierać konfiguracji równoległości na podstawie czasu bez jednoczesnej kontroli kontekstu, kompletności i jakości wyniku**.

To samo dotyczy `chunk_size`. Historyczny screening wskazywał najlepszy punkt około 500 znaków dla konkretnego workloadu i konkretnego profilu CPU, ale nie stanowi to uniwersalnej wartości dla V4. Wartość powinna być traktowana jako hipoteza workload-specific i potwierdzana pomiarem całego dokumentu.

#### 29A.4. V3 — lekcje z błędów generacji

W testach odnotowano m.in.:

- obcięcie końcowej części dokumentu;
- powtarzalne błędy fleksyjne;
- pozostawienie fragmentów w języku źródłowym;
- halucynowane treści;
- wycieki tokenów protokołu;
- artefakty XML;
- utratę lub zmianę chronionych elementów.

Część tych problemów została później naprawiona lub zastąpiona inną architekturą V4. Nie należy więc przenosić ich do bieżącego backlogu jako aktywnych defektów. Ich wartość dla V4 polega na tym, że definiują **klasy regresji, które należy testować**, nawet jeśli konkretny historyczny bug już nie istnieje.

#### 29A.5. V3/V4 — zasada kwalifikacji wyniku

Każdy eksperyment powinien być klasyfikowany jako:

- **wynik rozstrzygający** — kompletne dane, kontrolowany workload i kryterium jakości;
- **wynik screeningowy** — użyteczny do zawężenia dalszych testów, ale niewystarczający do decyzji produkcyjnej;
- **wynik niekompletny/anomalny** — zapisany dla historii diagnostycznej, niewykorzystywany do porównań;
- **plan/test oczekujący** — nie jest wynikiem.

Dla testów dokumentowych rekomendowana jest wspólna karta oceny:

| Wymiar | Pytanie kontrolne |
|---|---|
| Kompletność | Czy wszystkie jednostki/linie/sekcje wejścia występują w wyniku? |
| Semantyka | Czy wynik rzeczywiście tłumaczy, a nie kopiuje lub dopowiada treść? |
| Język | Czy występują błędy gramatyczne, terminologiczne lub pozostawiony source? |
| Struktura | Czy format, kolejność i chronione elementy zostały zachowane? |
| Integralność techniczna | Czy nie występują markery protokołu, utracone placeholdery, błędne inline codes lub artefakty? |
| Wydajność | Jaki jest czas całego dokumentu i pomocniczo PP/TG, throughput oraz koszt pamięci? |
| Powtarzalność | Czy wynik został potwierdzony powtórzeniami? |

#### 29A.6. Znaczenie dla V4

Do aktualnej metodyki V4 należy przenieść przede wszystkim **sposób prowadzenia eksperymentu**, a nie historyczne wartości parametrów:

`baseline → jedna zmienna → kontrolowany workload → pomiar czasu + jakości + integralności → powtórzenie → decyzja`

Dla dokumentów strukturalnych test wydajnościowy bez testu integralności nie jest kompletnym dowodem. Najkrótszy czas wykonania może oznaczać regresję, jeżeli został osiągnięty przez obcięcie kontekstu albo utratę treści.

## 30. Wykorzystane projekty i biblioteki

| Projekt/biblioteka | Rola |
|---|---|
| PySide6 / Qt Quick / QML | GUI |
| lxml | XML, HTML, XPath |
| Lingua | detekcja języka |
| llama.cpp | lokalny runtime inferencji i HTTP server |
| Apertium | lokalne rule-based MT |
| Okapi Framework | filtry dokumentowe i Java Filter Host |
| SQLite | cache tłumaczeń |

## 31. Doświadczenia V3 wykorzystane w V4

V3 dostarczył materiału porównawczego dla benchmarków llama.cpp, chunkingu, parallel, ochrony placeholderów, XLIFF, prompt engineeringu, glosariuszy, Apertium, filtrów dokumentowych i optymalizacji batchowej.

V4 jest niezależną implementacją i nie importuje kodu V3 w runtime.

## 32. Translate Toolkit — doświadczenie

Translate Toolkit był badany jako kandydat do ODT ↔ XLIFF. Ekstrakcja działała, ale kontrolowany round-trip nie odtworzył oczekiwanej zmiany w ODT. Wniosek: bibliotekę dokumentową trzeba oceniać przez pełny round-trip, nie przez samą deklarowaną listę formatów.

## 33. Licencjonowanie

Kod aplikacji V4 jest dystrybuowany zgodnie z bieżącym packagingiem MIT. Bundlowane komponenty zachowują własne licencje.

Okapi i zależności wymagają właściwych notice. Dla Apertium licencję ustala się dla konkretnego repozytorium, pary i wersji.

Przed release należy zinwentaryzować runtime, przypisać licencję do komponentu i zachować LICENSE/COPYING/NOTICE.

## 34. Packaging i build

pyproject.toml używa setuptools, wymaga Python >=3.12,<3.15, definiuje entrypoint tlumacz = tlumacz.qml_gui.app:main i deklaruje dane QML, Okapi, Apertium, llama.cpp oraz teksty lokalizacyjne.

Wymagania developerskie obejmują pytest, Ruff i mypy. Źródło pakietu to src/.

Podczas pracy w checkout zalecane jest PYTHONPATH=src. Rzeczywisty build pakietu należy testować osobno.

## 35. Testowanie

Zestaw testów obejmuje backendy, Apertium, Cloud, llama.cpp, TranslateGemma, Filter Engine, Okapi, TPlugin, cache, preprocessing, chunk planner, orchestrator, GUI, QML packaging, i18n, logging i E2E.

Świeży pełny test podczas przygotowania kompendium: 599 passed in 99.93s.

compileall, mypy i qmllint zakończyły się PASS. Ruff zgłosił 2 błędy importów w tests/test_tplugin_create.py; nie były naprawiane w ramach kompendium.

## 36. Metodyka rozwoju

Zmiany kodu:
1. test RED;
2. minimalna implementacja;
3. GREEN;
4. testy kierunkowe;
5. pełny gate;
6. dokumentacja.

Optymalizacja:
1. baseline;
2. jedna zmienna;
3. benchmark;
4. analiza jakości;
5. regresja;
6. decyzja.

GUI wymaga dodatkowo qmllint, a problemy wizualne należy potwierdzać na rzeczywistym runtime, gdy jest to możliwe.

## 37. Zalecane konfiguracje

| Scenariusz | Zalecenie |
|---|---|
| CPU, mały RAM | parallel=1, umiarkowany ctx, mały/średni chunk, oszczędny KV |
| CPU, dużo RAM | parallel=1 na start; threads zwiększaj po benchmarku |
| GPU 8 GB | gpu_layers=auto, mały parallel, obserwuj KV |
| GPU 12–24 GB | testuj parallel 2–8 i mierz opóźnienie |
| dokument techniczny | skill + glosariusz tematyczny + temperatura 0 |
| Markdown | MarkdownFilter |
| Plain Text | PlainTextFilter |
| HTML | HtmlFilter |
| DOCX/ODT/EPUB | odpowiedni filtr; dla Okapi sprawdź TPlugin |
| Apertium | konkretna gotowa para |
| Mozhi | auto |
| własny serwer | OpenAI-compatible Base URL + model |

## 38. Diagnostyka

Brak tłumaczenia lokalnego: sprawdź model GGUF, runtime, /health, source/target, tryb modelu i logi.

Brak pary Apertium: sprawdź .tar, .sha256, SHA-256, source-target i kompletność materializacji.

Brak filtra: sprawdź suffix, FilterRegistry, TPlugin, plugin.json, /tmp/filters i wspólne biblioteki.

Błędne markery: odrzuć odpowiedź, ponów zgodnie z kontraktem i użyj fallbacku jednostkowego. Nie dopisuj markerów.

Stary stan GUI: sprawdź QML disk cache, proces, sygnały bridge, qmllint i rzeczywisty runtime.

## 39. Najważniejsze zasady

1. Kod jest źródłem prawdy dla implementacji.
2. STATUS/TODO/BUG opisują bieżący stan.
3. V3 jest źródłem doświadczeń, nie runtime dependency.
4. Backend nie powinien znać formatu dokumentu.
5. Filtr nie powinien znać szczegółów providera.
6. Walidacji nie usuwamy dla pozornego przyspieszenia.
7. Chunkowanie mierzymy na poziomie całego dokumentu.
8. Apertium wymaga konkretnej pary.
9. Dynamiczne backendy mogą zmieniać source per chunk.
10. Sekrety nie trafiają do JSON ani logów.
11. TPlugin jest artefaktem transportowym.
12. Apertium .tar jest trwałym artefaktem danych językowych.
13. TranslateGemma jest trybem llama.cpp.
14. Markdown pozostaje na natywnym filtrze.
15. Optymalizacja wymaga baseline i pomiaru.
16. Zmiana kontraktu wymaga testów i dokumentacji.

## 40. Indeks kompendium z odnośnikami

| Sekcja | Temat | Odnośnik w dokumencie |
|---|---|---|
| 1 | Cel i zakres | [§1](#1-cel-i-zakres) |
| 2 | Model produktu | [§2](#2-model-produktu) |
| 3 | Założenia architektoniczne | [§3](#3-założenia-architektoniczne) |
| 4 | Struktura kodu | [§4](#4-struktura-kodu) |
| 5 | Pipeline tłumaczenia | [§5](#5-pipeline-tłumaczenia-dokumentu) |
| 5A | Indeks etapów pipeline | [§5A](#5a-indeks-etapów-pipeline) |
| 5B | Główny przepływ tekstu | [§5B](#5b-schemat-głównego-przepływu-tekstu) |
| 5C | Rozgałęzienie backendów | [§5C](#5c-przepływ-z-rozgałęzieniem-backendu) |
| 5D | Filter Engine | [§5D](#5d-przepływ-dokumentu-przez-filter-engine) |
| 5E | Markery inline codes | [§5E](#5e-przepływ-markerów-inline-codes) |
| 6 | Backend Registry | [§6](#6-backend-registry-i-rozszerzalność) |
| 7–8 | llama.cpp i strojenie | [§7](#7-llamacpp), [§8](#8-strojenie-llamacpp) |
| 9–10 | Cloud i Mozhi | [§9](#9-cloud), [§10](#10-mozhi) |
| 11 | Apertium | [§11](#11-apertium) |
| 12–15 | Filter Engine, Okapi, TPlugin, markery | [§12](#12-filter-engine), [§13](#13-okapi-i-java-filter-host), [§14](#14-tplugin), [§15](#15-ochrona-inline-codes) |
| 16–20 | Formaty dokumentów i XLIFF | [§16](#16-markdown), [§17](#17-html-i-lxml), [§18](#18-plain-text), [§19](#19-epub-odt-docx-i-struktury), [§20](#20-xliff-20) |
| 21–23 | Język, skille, glosariusz | [§21](#21-detekcja-języka), [§22](#22-skille), [§23](#23-glosariusz) |
| 24–27 | GUI, konfiguracja, bezpieczeństwo, lifecycle | [§24](#24-gui-qml), [§25](#25-konfiguracja), [§26](#26-bezpieczeństwo-i-logowanie), [§27](#27-anulowanie-i-lifecycle) |
| 28–29A | Optymalizacja, benchmarki i wnioski z analizy testów | [§28](#28-optymalizacje-potwierdzone), [§29](#29-wnioski-z-benchmarków), [§29A](#29a-wnioski-z-analizy-katalogów-testowych-v4-i-v3) |
| 30–33 | Biblioteki, V3, Translate Toolkit, licencje | [§30](#30-wykorzystane-projekty-i-biblioteki), [§31](#31-doświadczenia-v3-wykorzystane-w-v4), [§32](#32-translate-toolkit--doświadczenie), [§33](#33-licencjonowanie) |
| 34–39 | Build, testy, konfiguracje, diagnostyka, zasady | [§34](#34-packaging-i-build), [§35](#35-testowanie), [§36](#36-metodyka-rozwoju), [§37](#37-zalecane-konfiguracje), [§38](#38-diagnostyka), [§39](#39-najważniejsze-zasady) |
| 41 | Źródła | [§41](#41-źródła) |

### Mapa etapów procesu

Każdy etap P0–P15 z §5A ma opis związany z odpowiednią sekcją. Dla szybkiej nawigacji: **P0–P5 → §5**, **P6 → §15**, **P7–P9 → §5**, **P10 → §6–§11**, **P11 → §15**, **P12–P14 → §12–§20**, **P15 → §24 i §35**.

## 41. Źródła

V4: ARCHITECTURE.md, STATUS.md, TODO.md, BUG.md, CHANGELOG.md, translation-pipeline-contracts.md, plugin-okapi-filter.md, apertium-pair-packages.md, MECHANIZM_DETEKCJI_JEZYKA_APERTIUM.md, functional-capabilities.md, models.md, cloud-translation.md, server-management.md, GUI-zbior_praktycznej_wiedzy.md, user-guide.md, Plan 04.

V3: `docs/TESTY/kompilacja-testow.md`, `docs/TESTY/testy-rodzajow plikow-llama.cpp-10-09-2026.md`, `docs/TESTY/testy-rodzajow-plikow-llama.cpp-19-09-2026.md`, `docs/TESTY/testy-rodzajow plikow-llama.cpp-21-09-2026.md`, `docs/TESTY/problem-html.md`, `docs/TESTY/llama.cpp/PLAN_TESTOW_LLAMA_CPP.md`, `docs/TESTY/llama.cpp/KOMPENDIUM_TESTOW_LLAMA_CPP_2026-09-25.md` oraz wskazane materiały architektoniczne V3 użyte wcześniej do transferu doświadczeń.

Zewnętrzne źródła zweryfikowane:
- https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- https://okapiframework.org/
- https://wiki.apertium.org/wiki/Apertium
- https://github.com/pemistahl/lingua-py
- https://lxml.de/
- https://doc.qt.io/qt-6/qtquickcontrols-fusion.html

Źródła zewnętrzne służyły do potwierdzenia ogólnych właściwości komponentów. Szczegółowy kontrakt Tłumacza wynika z kodu i dokumentacji V4.
