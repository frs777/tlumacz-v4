---
id: plan-12-translategemma-chunkowanie-jezyki-skip-2026-10-07
status: active
meta:
  contentType: RemediationPlan
  category: translation-pipeline
version: 1.0.0
updated: 2026-10-07
priority: P0
---

# PLAN-12 — Naprawa kontraktu TranslateGemma: kody językowe, chunkowanie i pomijanie

## 1. Cel

Przywrócić w V4 semantykę tłumaczenia dokumentów znaną z V3 bez cofania architektury V4.

Zakres:
- poprawne source_lang_code i target_lang_code dla TranslateGemma;
- chunk jako jednostka transportowa/modelowa, a nie tylko grupa jednostek logicznych;
- skip wykonywany przed backendem, z zachowaniem pominiętego tekstu 1:1;
- walidacja i rekonstrukcja bez utraty struktury.

Plan jest naprawczy. Nie wdraża zmian w kodzie.

## 2. Ustalenia z V3

V3: preprocess.py i markdown/chunker.py realizują ochronę → keep/translate → grupowanie strukturalne → limit chunk_size → jedno wywołanie _translate_chunk dla fragmentu translate → walidację placeholderów → restore.

Chunkowanie V3 nie jest prostym cięciem tekstu. Uwzględnia:
- YAML front matter;
- nagłówki i granice akapitów;
- próg 60% zajętości przed rozpoczęciem nowego nagłówka;
- twardy podział bardzo długiej linii;
- atomowość placeholderów;
- brak uniwersalnego flushowania na separatorze ---.

V3 ma skip_patterns oraz _effective_skip_patterns(). Domyślne wzorce obejmują m.in. ---, name:, license:, author:, metadata:, version:, tags:, created:, updated:. Pasująca treść jest kopiowana bez wysyłania do modelu.

V3 dodatkowo chroni fenced code, inline code, tagi i URL. Placeholdery są walidowane przed restore.

## 3. Ustalenia z V4

V4 ma poprawny podział architektoniczny Filter → Unit → ChunkPlanner → TranslationOrchestrator → Backend → Writer.

Defekt znajduje się między plannerem a executorem:

1 chunk → wiele PlannedUnit → TranslationExecutor → osobne translate(unit.source) → osobne requesty.

Potwierdzony przypadek diagnostyczny:

905 znaków do tłumaczenia → 17 jednostek → 1 logiczny chunk przy chunk_size=4000 → 17 requestów HTTP/inferencji.

Zatem obecnie chunk != request.

## 4. Ocena kodów językowych TranslateGemma

Oficjalny kontrakt TranslateGemma wymaga source_lang_code i target_lang_code. Dokumentacja modelu dopuszcza ISO 639-1 Alpha-2 oraz obsługiwane warianty regionalne ISO 639-1 + ISO 3166-1. Kod nieobsługiwany przez model powoduje błąd szablonu. Źródło zewnętrzne: model card google/translategemma-4b-it.

V4 ma prawidłowy kierunek odpowiedzialności:

LanguageDetector → LlamaCppLanguageRouting → source_language → LlamaCppAdapter.

Adapter nie wykonuje drugiej detekcji. target_language pochodzi z GUI i jest normalizowany przez language_code_for().

Dodatkowa luka: language_code_for() rozpoznaje nazwę języka i podstawowy kod, ale nie normalizuje regionalnego wariantu typu en-US/en_US do obsługiwanego kodu. Przy takim wejściu zwraca auto, a adapter TranslateGemma następnie odrzuca je jako nieobsługiwane. Należy to objąć testem i naprawić bez utraty informacji regionalnej.

Problem wymagający formalizacji: obecna mapa zawiera Montenegrin → cnr. cnr jest kodem używanym dla czarnogórskiego, ale nie jest ISO 639-1 Alpha-2. Nie wolno więc uznać całej mapy za zgodną z deklaracją ISO 639-1. Nie należy jednak usuwać cnr bez sprawdzenia faktycznego tokenizer/chat template konkretnego GGUF.

Docelowo trzeba rozdzielić:
- kody zaakceptowane przez oficjalny kontrakt;
- kody faktycznie obecne w tokenizerze/runtime konkretnego modelu;
- kody zwracane przez Lingua;
- kody dopuszczone w GUI.

V3 miał niebezpieczny fallback ręcznego promptu auto → en. Nie wolno go przywracać. W V4 nieudana detekcja ma prowadzić do jawnej decyzji routingowej, a nie do fałszywego źródła English.

## 5. Docelowy kontrakt chunkowania

Normalna ścieżka musi spełniać:

1 logiczny chunk = 1 request = 1 inferencja.

Wyjątki: kontrolowany retry oraz fallback awaryjny.

Nie kopiować MarkdownChunker z V3 do całego V4. Filter Engine ma pozostać właścicielem struktury dokumentu. Należy przenieść semantykę V3 do warstwy planowania transportu.

Chunk powinien zachować ordered_units, id, source, source_language oraz informacje potrzebne do walidacji markerów i rekonstrukcji.

Transport wielu jednostek wymaga stabilnego protokołu segmentów, np. jawnych identyfikatorów. Nie opierać kontraktu wyłącznie na przypadkowym separatorze tekstowym.

Odpowiedź musi dać jednoznaczne mapowanie segment_id → translated_text.

Walidacja odpowiedzi:
- każdy segment występuje dokładnie raz;
- brak segmentu = błąd;
- duplikat = błąd;
- nieznany segment = błąd;
- kolejność i granice są jednoznaczne;
- markery strukturalne zachowują integralność.

Przy błędzie: retry całego chunka, a dopiero po drugim błędzie kontrolowany fallback per jednostka.

## 6. Docelowy kontrakt skip

Kolejność:

Filter → extract units → skip classification → units_to_translate → ChunkPlanner → backend.

Jednostka skip:
- nie trafia do ChunkPlanner;
- nie trafia do TranslationExecutor;
- nie trafia do llama.cpp;
- pozostaje w mapie rekonstrukcyjnej jako oryginalny tekst.

Skip nie może oznaczać pustego targetu. Prawidłowy model to source bez zmian oraz jawna informacja o pominięciu.

Wzorce należy stosować do rzeczywistego tekstu jednostki przed backendem. Dla Markdown trzeba zachować semantykę V3, ale nie kopiować jego regexów bezpośrednio do innych formatów.

## 7. Plan wdrożenia TDD

### Etap 0 — characterization
- test wykazujący obecny stan: 1 chunk, 17 units, 17 calls;
- test kolejności;
- test cache;
- test skip;
- test source/target;
- test walidacji odpowiedzi.

### Etap 1 — kontrakt językowy
- nazwa → kod;
- kod → kod;
- regionalizacja;
- auto nie może trafić do TranslateGemma;
- nieznany kod jest odrzucany;
- target z GUI pozostaje niezmieniony;
- adapter nie wykonuje drugiej detekcji;
- lista aktywnych kodów jest sprawdzana względem konkretnego tokenizer/runtime.

### Etap 2 — batch
Wprowadzić jawny kontrakt TranslationBatch oraz translate_batch(batch). Nie rozszerzać po cichu istniejącego translate(text, source_language) separatorami.

### Etap 3 — parser odpowiedzi
Osobny parser z testami dla: brak segmentu, duplikat, nieznany segment, zmieniony ID, tekst poza segmentami i poprawna odpowiedź.

### Etap 4 — orchestrator/executor
Zmienić przepływ chunk → for unit → executor na chunk → batch executor → map[id, result].

### Etap 5 — skip
Test A=translate, B=skip, C=translate. Backend ma dostać tylko A i C; writer ma zwrócić A translated, B original, C translated.

### Etap 6 — cache
Sprawdzić mieszany przypadek hit/miss/hit bez utraty mapowania i bez dodatkowych requestów.

### Etap 7 — fallback
Poprawna odpowiedź: jeden request. Błędna odpowiedź: jeden retry batch. Dopiero kolejny błąd: fallback per unit.

### Etap 8 — rzeczywiste E2E
Markdown z nagłówkami, front matter, fenced code, inline code, URL, skip, wiele jednostek w jednym chunku, dokument wielojęzyczny i rzeczywisty TranslateGemma CPU.

## 8. Backup

Przed implementacją zmiany należy wykonać backup całego aktualnego drzewa kodu i zapisać SHA-256 archiwum.

Nie zmieniać przy okazji:
- aktywnego GGUF;
- systemowego llama-server PID 2782;
- wyłączonej binarki llama.cpp v3;
- FastAPI/OpenVINO;
- konfiguracji niezwiązanej z planem.

## 9. Exit gate

Języki: prawidłowe i obsługiwane source/target, brak auto → en, brak drugiej detekcji.

Chunkowanie: liczba requestów w normalnym przypadku = liczba chunków, zachowana kolejność, granice semantyczne i markery.

Skip: pominięte jednostki nie są wysyłane do backendu i wracają bez zmian.

E2E: rzeczywisty dokument + rzeczywisty TranslateGemma na CPU + poprawny wynik + liczba requestów zgodna z liczbą chunków.

## 10. Decyzje architektoniczne

1. Nie przywracać V3 jako osobnej ścieżki produkcyjnej.
2. Nie kopiować MarkdownChunker do V4 1:1.
3. Zachować Filter Engine jako właściciela struktury dokumentu.
4. Przenieść do V4 semantykę V3, nie jego monolityczną implementację.
5. ChunkPlanner pozostaje planowaniem transportowym.
6. TranslationExecutor musi otrzymać kontrakt batchowy.
7. TranslateGemma pozostaje specjalnym trybem llama.cpp.
8. Kody językowe muszą być walidowane względem rzeczywistego kontraktu modelu.
9. Skip jest decyzją przed backendem.
10. Fallback jednostkowy jest wyłącznie awaryjny.

## 11. Status

Plan: CZĘŚCIOWO WDROŻONY.
Implementacja została wykonana i zweryfikowana testami ukierunkowanymi. Kryterium końcowe nie jest jeszcze spełnione: pozostaje rzeczywisty E2E z llama.cpp/TranslateGemma oraz zgodność liczby requestów z liczbą chunków.

## 12. Wdrożenie 2026-10-07

Wdrożono plan w V4.

### Batch TranslateGemma

- `TranslationExecutor.execute_batch()` wykonuje cały logiczny chunk jednym wywołaniem callbacku batchowego.
- `TranslationOrchestrator` używa batcha jako ścieżki podstawowej, a istniejące tłumaczenie jednostkowe pozostaje ścieżką awaryjną.
- `LlamaCppAdapter.translate_batch()` buduje jeden request TranslateGemma z markerami `⟦TG_SEG_N⟧`.
- Parser odpowiedzi wymaga wszystkich markerów dokładnie raz i w kolejności.
- Po uszkodzeniu protokołu batch jest ponawiany raz z instrukcją naprawczą.
- Jeżeli batch nadal jest niepoprawny, orchestrator wykonuje kontrolowany fallback jednostkowy.

### Chunkowanie strukturalne

- `ChunkPlanner` obsługuje metadane strukturalne jednostek.
- Nagłówek rozpoczyna nowy chunk, jeżeli poprzedni chunk osiągnął co najmniej 60% budżetu — zgodnie z mechanizmem V3.
- Zmiana języka źródłowego wymusza granicę chunka, aby jeden request TranslateGemma nie mieszał kodów źródłowych.
- `MarkdownFilter` przekazuje do planera typ jednostki (`heading` / `paragraph`).
- Dla Markdown zachowana jest kolejność oraz grupowanie treści pod jednym requestem.

### Pomijanie

- Markdown nie tworzy jednostek dla YAML front matter.
- Linie metadanych `name:`, `license:`, `author:`, `metadata:`, `version:`, `tags:`, `created:`, `updated:` są pomijane przed backendem.
- Bloki kodu i linie składniowe nadal są wyłączane przez filtr.
- Pominięte treści pozostają w źródłowym dokumencie i są zapisywane bez modyfikacji przez writer.

### Kody językowe

- `language_code_for()` obsługuje kody podstawowe oraz składniowo poprawne warianty regionalne `xx-YY` i `xx_YY`, normalizując je do `xx-YY`.
- `auto` nie jest wysyłane do TranslateGemma.
- Batch TranslateGemma wymaga jednego kodu źródłowego dla wszystkich jednostek w batchu.
- Dokumentacja upstream TranslateGemma określa 2K tokenów całkowitego kontekstu i zaleca dzielenie długich tekstów na akapity. Implementacja V4 pozostawia limit znaków jako parametr planera; limit ten nie jest utożsamiany z dokładnym limitem tokenów modelu.

### Backup

Backup przed rozpoczęciem zmian:

`backups/20261007-plan12-pre-implementation/pre-change.tar.gz`

SHA-256:
`34001509a41fec28de51820e9df48660359abc912c80444aca0613ce11265710`

### Weryfikacja

- testy ukierunkowane: `42 passed in 4.19s`;
- `ruff check` zmienionych modułów: `All checks passed!`;
- `python3 -m py_compile` zmienionych modułów: PASS;
- rzeczywisty E2E z llama.cpp/TranslateGemma nie został wykonany przez agenta; musi zostać wykonany na rzeczywistym środowisku użytkownika.
## 13. Uzupełnienie planu — wspólna warstwa preprocessingu V3 → V4

### 13.1 Cel

Odtworzyć w V4 semantykę preprocessingu z V3: decyzja translate/keep ma być podejmowana przed backendem, a nie przez konkretny filtr. Nie rozwiązywać tego przez dalsze rozszerzanie MarkdownFilter ani OkapiFilter.

Filtr pozostaje odpowiedzialny za ekstrakcję i rekonstrukcję struktury formatu. Wspólny preprocessing odpowiada za klasyfikację fragmentu, ochronę treści wymagającej zachowania 1:1 oraz przekazanie tylko treści przeznaczonej do tłumaczenia do dalszego pipeline'u.

### 13.2 Odpowiedzialność agentów

- Agent główny: @AI Software Architect — kontrakt architektoniczny i integracja z PLAN-12.
- Implementacja: @Python — kod preprocessingu i integracja.
- Testy: istniejący agent TDD — RED → GREEN → refactor.
- Diagnostyka hosta, backup i E2E: @SentinelX.
- Nie tworzyć nowego agenta ani osobnej odpowiedzialności dla Markdown.

### 13.3 Docelowy kontrakt

DOKUMENT → PREPROCESSOR → FILTER ENGINE → UNITS → SKIP/KEEP → CHUNK PLANNER → TRANSLATION BATCH → WRITER

Minimalny kontrakt:
- translate — fragment trafia do planowania i backendu;
- keep — fragment nie trafia do backendu i zachowuje oryginalną treść;
- kolejność pozostaje jednoznaczna;
- keep nie jest reprezentowane pustym targetem;
- rekonstrukcja zachowuje keep dokładnie 1:1;
- klasyfikacja nie usuwa ani nie modyfikuje treści;
- kontrakt jest wspólny dla Markdown, Okapi i innych aktywnych filtrów.

### 13.4 Referencja V3

Jako źródło semantyki wykorzystać agent-translator-v3/tlumacz/preprocess.py. Przenieść zachowanie, nie kod 1:1:
- skip_patterns i ich kompilację;
- klasyfikację keep/translate;
- zachowanie kolejności;
- ochronę treści, których nie wolno tłumaczyć;
- atomowość chronionych fragmentów;
- przygotowanie danych dla dalszego chunkowania;
- brak wysyłania keep do modelu.

Nie kopiować MarkdownChunker z V3 do całego V4. Zachować rozdział Filter → Unit → ChunkPlanner → Orchestrator → Backend.

### 13.5 Etap A — audyt V4

- [ ] @AI Software Architect: wskazać dokładną granicę odpowiedzialności między filtrem a wspólnym preprocesorem.
- [ ] @Python: zinwentaryzować istniejące skip, protect, placeholdery i klasyfikację jednostek w src/tlumacz/.
- [ ] @SentinelX: potwierdzić rzeczywistą ścieżkę produkcyjną Markdown, Okapi i innych aktywnych filtrów.
- [ ] TDD: przygotować characterization tests przed refaktoryzacją.

Kryterium: macierz format → filtr → jednostka → obecny skip/protect → rekonstrukcja.

### 13.6 Etap B — kontrakt Preprocessor

- [ ] TDD: test RED dla translate/keep i zachowania keep 1:1.
- [ ] @AI Software Architect: zdefiniować minimalny kontrakt niezależny od Markdown i backendu.
- [ ] @Python: zaimplementować minimalny preprocessor.
- [ ] TDD: uzyskać GREEN.

Preprocessor nie może przejmować odpowiedzialności ChunkPlanner za limity i granice transportowe.

### 13.7 Etap C — wspólne skip_patterns

- [ ] TDD: regresje dla wzorców V3: ---, name:, license:, author:, metadata:, version:, tags:, created:, updated:.
- [ ] @Python: zaimplementować konfigurację i kompilację wzorców bez kopiowania V3 1:1.
- [ ] TDD: potwierdzić, że dopasowany fragment jest keep, nie trafia do batcha i wraca bez zmian.
- [ ] TDD: potwierdzić, że zwykły tekst pozostaje translate.

Wzorce stosować do rzeczywistego tekstu jednostki. Nie wprowadzać globalnego regexu Markdown do formatów, dla których ta semantyka nie jest właściwa.

### 13.8 Etap D — ochrona treści

- [ ] TDD: testy fenced code, inline code, URL i innych chronionych elementów obecnie obsługiwanych.
- [ ] @AI Software Architect: rozdzielić semantycznie keep od technicznej ochrony placeholderów.
- [ ] @Python: podłączyć ochronę tylko tam, gdzie wymaga jej kontrakt danego formatu.
- [ ] TDD: potwierdzić brak utraty kolejności i duplikacji.

Nie utożsamiać automatycznie keep z placeholderem ochronnym; oba mechanizmy mają być jawnie rozróżnione w modelu danych.

### 13.9 Etap E — integracja z Filter Engine

- [ ] @AI Software Architect: ustalić adapter pomiędzy wynikiem filtra a wspólnym preprocesorem.
- [ ] @Python: podłączyć preprocessing przed ChunkPlanner/TranslationOrchestrator.
- [ ] TDD: test A=translate, B=keep, C=translate dla Markdown, Okapi i co najmniej jednego innego aktywnego formatu.
- [ ] TDD: potwierdzić, że keep nie trafia do TranslationExecutor, translate_batch ani backendu.
- [ ] @SentinelX: sprawdzić rzeczywisty przepływ produkcyjnego FilterRegistry.

### 13.10 Etap F — integracja z chunkowaniem PLAN-12

- [ ] @Python: przekazywać do ChunkPlanner wyłącznie jednostki translate.
- [ ] TDD: potwierdzić, że keep nie zwiększa budżetu transportowego chunka.
- [ ] TDD: potwierdzić kolejność po rekonstrukcji: translate → keep → translate.
- [ ] TDD: potwierdzić, że zmiana source_language nadal wymusza granicę batcha tylko dla jednostek tłumaczonych.
- [ ] @AI Software Architect: potwierdzić, że preprocessing nie przejmuje odpowiedzialności ChunkPlanner.

### 13.11 Etap G — usunięcie lokalnych obejść

Dopiero po GREEN integracji:
- [ ] @Python: usunąć dublujące się mechanizmy skip z filtrów, jeżeli nie zmienia to kontraktu ekstrakcji/reconstruction.
- [ ] TDD: regresja struktury Markdown i Okapi.
- [ ] Nie usuwać parserów, ochrony formatowej ani writerów tylko dlatego, że skip został przeniesiony.
- [ ] @AI Software Architect: zatwierdzić granice odpowiedzialności przed każdym usunięciem.

### 13.12 Etap H — GUI i raportowanie

- [ ] @Python: przekazać liczbę i reprezentację pominiętych fragmentów do warstwy aplikacyjnej.
- [ ] TDD: regresja Ominięto N fragmentów oparta na wspólnym preprocessingu.
- [ ] TDD: N=0 ma oznaczać rzeczywisty brak keep, nie brak informacji z sesji filtra.
- [ ] @SentinelX: zweryfikować rzeczywiste GUI na dokumencie zawierającym nagłówki i oznaczony tekst.

### 13.13 Etap I — regresja, E2E i dokumentacja

- [ ] TDD: pełna regresja Filter Engine, chunkowania, języków i GUI.
- [ ] @SentinelX: compileall, Ruff, git diff --check i rzeczywisty przepływ produkcyjny.
- [ ] @Python: uzupełnić dokumentację architektury i kontraktów.
- [ ] @AI Software Architect: zaktualizować PLAN-12, STATUS i CHANGELOG.
- [ ] @SentinelX: wykonać rzeczywisty E2E TranslateGemma na CPU i porównać liczbę requestów z liczbą chunków.

### 13.14 Exit gate

Wdrożenie preprocessingu można zamknąć dopiero, gdy:
1. skip/keep działa we wspólnej warstwie przed backendem;
2. Markdown, Okapi i pozostałe aktywne formaty korzystają z tego samego kontraktu;
3. keep nigdy nie trafia do backendu;
4. keep wraca dokładnie 1:1 i zachowuje kolejność;
5. ChunkPlanner planuje wyłącznie translate;
6. GUI raportuje rzeczywistą liczbę pominiętych fragmentów;
7. nie ma lokalnego obejścia dublującego wspólny preprocessing;
8. pełna regresja jest GREEN;
9. rzeczywisty E2E na CPU jest GREEN;
10. dokumentacja opisuje nowy kontrakt bez przedstawiania V3 jako osobnej ścieżki produkcyjnej.

### 13.15 Kolejność wdrożenia

Audyt V4 → kontrakt Preprocessor → skip/keep → ochrona → integracja Filter Engine → ChunkPlanner → usunięcie duplikatów → GUI → pełna regresja → E2E → dokumentacja/exit gate

Nie usuwać istniejących mechanizmów filtrów przed uzyskaniem GREEN dla wspólnego preprocessingu.


## 14. Postęp wdrożenia wspólnego preprocessingu — 2026-10-07

Zrealizowano pierwszy zakres implementacyjny zgodnie z kolejnością PLAN-12:

1. Audyt granicy Filter Engine → preprocessing → backend wykonany na aktualnym kodzie V4 oraz referencyjnym preprocess.py V3.
2. Dodano wspólny kontrakt Preprocessor w src/tlumacz/preprocessing/preprocessor.py.
3. Wprowadzono jawne decyzje TRANSLATE/KEEP; KEEP zachowuje tekst źródłowy 1:1.
4. DocumentProcessor wykonuje klasyfikację po extract i przed ścieżką translate/translate_many.
5. KEEP nie jest przekazywane do backendu także w ścieżce batchowej.
6. Wspólne wzorce metadanych są kompilowane w jednym miejscu; separator --- jest ograniczony do formatu Markdown.
7. Dodano regresje dla klasyfikacji, kolejności, duplikatów ID, zachowania tekstu oraz ścieżek jednostkowej i batchowej.
8. Publiczne API Filter Engine eksportuje Preprocessor, PreprocessedUnit i PreprocessDecision.

Nie wykonano jeszcze Etapu D (pełna wspólna warstwa ochrony struktur formatowych), usuwania lokalnych obejść filtrów, integracji raportowania GUI, pełnej regresji oraz rzeczywistego E2E TranslateGemma CPU.

Stan: PREPROCESSOR CORE WDROŻONY / PLAN-12 NADAL CZĘŚCIOWO WDROŻONY.


## 15. Etap D/E — odseparowanie prostych formatów tekstowych od Okapi — 2026-10-07

Na podstawie decyzji architektonicznej wdrożono zasadę, że Markdown i zwykły tekst nie przechodzą przez Okapi. Okapi pozostaje narzędziem dla formatów, które rzeczywiście wymagają jego strukturalnej rekonstrukcji.

### Wdrożenie

- dodano natywny `PlainTextFilter` dla `.txt`, `.text` i `.log`;
- aktywowano istniejący natywny `HtmlFilter` dla `.html`, `.htm` i `.xhtml`;
- `FilterRegistry` rejestruje natywne filtry HTML, Markdown oraz Plain Text przed odkrywaniem pluginów i nie pozwala pluginowi Okapi nadpisać natywnej ścieżki;
- plugin może nadpisać natywną rejestrację tylko przez jawny mechanizm discovery, ale Markdown pozostaje mapowany na `MarkdownFilter`, a nie `OkapiFilter`;
- Plain Text zachowuje puste linie i układ dokumentu, a tłumaczeniu podlegają wyłącznie niepuste linie;
- dodano regresje potwierdzające brak `OkapiFilter` dla Markdown i Plain Text oraz round-trip TXT.

### Granica decyzji

Nie traktujemy automatycznie każdego tekstowego formatu strukturalnego jako Plain Text. JSON/YAML/CSV i formaty markup wymagają własnego kontraktu strukturalnego; nie wolno zastępować ich naiwnym filtrem liniowym tylko dlatego, że są zapisane jako tekst. Ich dalsza migracja z Okapi jest osobnym etapem, gdy będzie dostępny równoważny filtr natywny.

### Weryfikacja

- `tests/test_filter_registry.py`, `tests/test_filter_processor.py`, `tests/test_preprocessor.py`, `tests/test_markdown_filter.py`: **34 passed**;
- backup etapu: `backups/20261007-plan12-text-filters/pre-text-filter-stage.tar.gz`;
- SHA-256: `265ece839ef2e2534a54ef85aed616ff2af5c482cb2384b1d944b37459a3cdc0`.

Stan: **Markdown + Plain Text omijają Okapi / etap D-E trwa dalej dla pozostałych formatów tekstowych.**


## Korekta architektoniczna — 2026-10-07

Przyjęto zasadę unifikacji: jeżeli dla formatu dostępny jest filtr Okapi, pipeline używa filtra Okapi. Filtr natywny V4 może być użyty wyłącznie jako fallback dla formatu, dla którego odpowiedniego filtra Okapi nie ma.

W związku z tym HTML nie jest traktowany jako format do automatycznego wyjęcia z Okapi. Ostatnia próba uprzywilejowania natywnego HtmlFilter została wycofana. Rejestr ma zachować możliwość wyboru Okapi HTML, gdy plugin jest dostępny.

Markdown i Plain Text pozostają kandydatami do ścieżki natywnej tylko dlatego, że ich potrzeba filtracji Okapi jest do zweryfikowania względem faktycznie dostępnych pluginów. Ostateczny routing ma wynikać z katalogu dostępnych filtrów, a nie z ręcznie utrzymywanej listy wyjątków.


## 16. Weryfikacja po przekazaniu prac Okapi — 2026-10-07

Prace nad FilterRegistry/Okapi zostały przekazane innemu agentowi i nie były modyfikowane w tym etapie.

Poza zakresem Okapi wykonano:
- potwierdzenie kontraktu regionalnych kodów językowych xx-YY / xx_YY testami language_code_for();
- korektę testu dokumentowego chunk/batch: jeden logiczny chunk ma jeden request batchowy;
- ukierunkowany gate preprocessingu, chunkowania, batcha, ochrony inline i detekcji języka: 35 passed.

Nadal otwarty pozostaje rzeczywisty E2E na aktywnym runtime TranslateGemma wraz z porównaniem liczby requestów do liczby logicznych chunków.
