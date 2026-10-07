# Raport końcowy migracji V3 → V4

**Projekt:** Tłumacz  
**Migracja:** V3 → V4  
**Wersja docelowa:** 0.40.0  
**Data raportu:** 2026-09-30  
**Oficjalny katalog projektu:** `$HOME/Projekty/tlumacz-v4`  
**Stan migracji:** zakończony cykl migracyjny / lokalny handoff freeze  
**Stan wydania:** Release Candidate Linux; finalne wydanie 0.40.0 pozostaje otwarte

---

## 1. Cel raportu

Ten dokument jest końcowym podsumowaniem całego cyklu migracji Tłumacza z V3 do V4.

Raport opisuje:

- dlaczego migracja została wykonana w formie nowej architektury V4;
- co zostało przebudowane;
- jak przebiegały kolejne fazy;
- które elementy zostały zakończone i zweryfikowane;
- jakie problemy wystąpiły podczas migracji;
- które problemy zostały rozwiązane;
- które problemy pozostały otwarte;
- dlaczego część elementów nie została domknięta;
- jaki jest rzeczywisty stan końcowy projektu;
- jakie są warunki przejścia z Release Candidate do finalnego wydania.

Raport nie przedstawia Release Candidate jako finalnego wydania. Jest to istotne rozróżnienie: **migracja V3 → V4 osiągnęła stan lokalnego handoff freeze, natomiast proces wydaniowy 0.40.0 nie został jeszcze formalnie zamknięty.**

---

# 2. Punkt wyjścia — V3

Migracja nie była zwykłym podniesieniem wersji istniejącego projektu.

V3 posiadał działającą aplikację desktopową, lokalny backend llama.cpp, backend Cloud, warstwę dokumentową oraz szereg starszych i odłączonych ścieżek technologicznych. Jednocześnie audyt ujawnił problemy architektoniczne, zależności pomiędzy warstwami, niejednoznaczny stan części runtime'ów oraz problemy z packagingiem.

Szczególnie istotne było to, że V3 zawierał również lokalne elementy nieujęte jednoznacznie w historii Git. Dlatego przyjęto zasadę:

> V3 jest źródłem referencyjnym, ale nie jest bazą do modyfikowania podczas migracji.

W praktyce oznaczało to budowę V4 jako niezależnego drzewa zamiast mechanicznego kopiowania repozytorium.

V3 pozostał osobnym drzewem i nie był przygotowywany poprzez usuwanie, przenoszenie ani modyfikowanie plików na potrzeby migracji.

---

# 3. Założenia architektoniczne V4

Najważniejszą decyzją było odejście od monolitycznej struktury V3 i zbudowanie V4 jako modularnego monolitu desktopowego.

Docelowy podział został oparty o:

```text
GUI / Composition Root
        |
        v
Application / Use Cases
        |
        +-----------------------+
        |                       |
        v                       v
Document Pipeline         Translation Port
        |                       |
        v                       v
Filter Engine             Backend Registry
        |                  /       |       \
        v                 /        |        \
Filter Runtime       LlamaCpp     Cloud     Apertium
        |
        +--> Python filters
        |
        +--> Java Filter Host -> Okapi
```

W efekcie V4 został podzielony na:

- kontrakty domenowe;
- warstwę aplikacyjną;
- niezależne backendy;
- Filter Engine;
- usługi dokumentowe;
- infrastrukturę;
- kontrolery GUI;
- kontrolowane runtime'y;
- testy jednostkowe, kontraktowe, integracyjne i E2E.

Najważniejszą zasadą było ograniczenie zależności pomiędzy warstwami. Backend nie powinien wiedzieć, czy tłumaczy DOCX, EPUB czy Markdown. GUI nie powinno znać szczegółów providera. Filter Engine nie powinien znać konkretnego backendu.

---

# 4. Przebieg migracji — podsumowanie faz

## Faza 0 — baseline V3

Na początku wykonano inwentaryzację V3.

Zebrano m.in.:

- stan Git;
- pliki śledzone i nieśledzone;
- runtime'y;
- testy;
- entrypointy;
- zależności;
- obszary wymagające rekonstrukcji w V4.

Istotnym odkryciem był niekompletny stan V3 z punktu widzenia samego Git. Dlatego nie przyjęto założenia, że HEAD V3 reprezentuje całą funkcjonalność znajdującą się lokalnie.

Faza zakończyła się utworzeniem baseline'u migracyjnego i tabeli decyzji V3 → V4.

Dodatkowo pełny suite V3 nie mógł być traktowany jako prosty baseline wykonawczy, ponieważ środowisko nie posiadało zależności `lingua`. Zdecydowano, aby nie instalować nowych zależności do V3 tylko po to, aby sztucznie zmieniać jego środowisko referencyjne.

**Wynik: zakończona.**

---

## Faza 1 — bootstrap V4

Utworzono od podstaw strukturę V4:

- pakiety aplikacyjne;
- domenę;
- backendy;
- dokumenty;
- Filter Engine;
- infrastrukturę;
- interfejsy;
- `pyproject.toml`;
- entrypoint;
- dokumentację;
- pierwszy zestaw testów.

Podstawowym kryterium było uruchomienie V4 bez importowania kodu V3.

**Wynik: zakończona.**

---

## Faza 2 — kontrakty

Wydzielono jawne kontrakty:

- `BackendResult`;
- `TranslationBackend`;
- `FilterContract`;
- `DocumentContract`;
- `InlineCode`;
- `HealthCheckResult`;
- `Session`;
- `Workspace`;
- błędy domenowe;
- `CancellationToken`.

Pozwoliło to odseparować warstwę aplikacyjną od konkretnych implementacji.

Weryfikacja końcowa fazy: **11 testów zakończonych sukcesem**.

**Wynik: zakończona.**

---

## Faza 3 — Filter Engine

Była to jedna z najważniejszych części migracji.

Powstały:

- registry filtrów;
- processor;
- workspace;
- lifecycle;
- validator;
- marker validator;
- Java Filter Host;
- wersjonowany protokół JSON Lines;
- adaptery dokumentowe;
- kontrolowany runtime Okapi.

Obsłużono:

- DOCX;
- ODT;
- HTML/XHTML;
- Markdown;
- EPUB;
- XLIFF.

Dla formatów wykonano testy round-trip, walidację strukturalną, testy Unicode, błędnych danych oraz anulowania.

W trakcie tej fazy wykryto również regresję dotyczącą markerów Unicode. Poprzednia logika traktowała zbyt szeroki zakres znaków Unicode jako potencjalne markery. W szczególności zwykłe emoji mogły zostać błędnie zakwalifikowane jako markery.

Regresję naprawiono poprzez ograniczenie rozpoznawania do właściwego zakresu Private Use Area oraz dodano test regresyjny.

Filter Engine otrzymał również własny Java Filter Host zamiast bezpośredniego sprzęgania aplikacji z JVM.

**Wynik: zakończona i zweryfikowana.**

---

## Faza 4 — LlamaCppBackend

Llama.cpp został wyprowadzony z logiki aplikacyjnej do niezależnego adaptera.

Dodano:

- adapter backendu;
- runtime manager;
- kontrolę własności procesu;
- timeouty;
- cancellation;
- health-check;
- contract suite;
- E2E.

Szczególnie istotne było rozwiązanie problemu własności procesu. V4 nie powinien zabijać obcego procesu tylko dlatego, że korzysta z tego samego portu.

Weryfikacja obejmowała rzeczywisty llama-server i smoke translation.

**Wynik: zakończona.**

---

## Faza 5 — Cloud

Warstwę Cloud przebudowano do postaci routera/provider layer.

Powstały:

- `CloudRouter`;
- interfejs providera;
- migracja profili;
- MozhiProvider;
- timeouty;
- klasyfikacja błędów;
- izolacja sekretów;
- testy kontraktowe.

Błędy Cloud zostały rozdzielone na klasy, m.in.:

- configuration;
- authentication;
- rate limit;
- timeout;
- network;
- HTTP;
- invalid response;
- provider;
- unknown.

Klucze API zostały odseparowane od zwykłej konfiguracji i nie są częścią artefaktów migracyjnych.

**Wynik: zakończona.**

---

## Faza 6 — Apertium

Apertium otrzymał własny runtime i adapter zgodny z kontraktem V4.

Zrealizowano:

- runtime discovery;
- adapter;
- backend;
- obsługę języków;
- kontrolę timeoutu;
- cancellation;
- health-check;
- kontrakty;
- testy E2E.

Bundlowany silnik Apertium ma wersję **3.9.12** i uruchamia się prawidłowo.

Problem pojawił się dopiero przy przygotowaniu kompletnego artefaktu dystrybucyjnego.

Sam silnik działa, ale bundlowany runtime nie posiada kompletnej pary `eng-pol`.

Próba odtworzenia brakującego artefaktu z materiałów V3 zakończyła się błędem:

```text
Undefined attr-item cas_sp
```

będącym wynikiem działania `apertium-preprocess-transfer`.

Nie wygenerowano sztucznego pliku binarnego i nie zmodyfikowano V3 w celu obejścia problemu.

**Wynik: część wykonawcza zakończona, kompletność dystrybucyjna pozostaje otwarta.**

---

## Faza 7 — Document Services

Warstwa dokumentowa została zbudowana wokół Filter Engine.

Zweryfikowano:

- DOCX;
- ODT;
- HTML/XHTML;
- Markdown;
- EPUB;
- XLIFF.

Każdy aktywny format otrzymał odpowiednie testy i walidację.

Backend tłumaczeniowy został odseparowany od wiedzy o formacie dokumentu.

**Wynik: zakończona.**

---

## Faza 8 — Translator

Monolityczny Translator został rozbity na wyspecjalizowane komponenty:

- `ChunkPlanner`;
- `PromptBuilder`;
- `TranslationExecutor`;
- `TranslationCache`;
- `ResultValidator`;
- `TranslationOrchestrator`;
- `DocumentTranslationService`.

Dzięki temu planowanie chunków, wykonywanie tłumaczeń, cache, walidacja wyników i obsługa dokumentów nie są już jedną odpowiedzialnością.

Weryfikacja całej fazy zakończyła się wynikiem **166 testów**.

**Wynik: zakończona.**

---

## Faza 9 — GUI

GUI zostało odseparowane od logiki aplikacyjnej przez kontrolery:

- `TranslationController`;
- `BackendController`;
- `SettingsController`;
- `DocumentController`;
- `ProgressController`;
- `DiagnosticsController`.

Kontrolery nie importują Qt i nie korzystają z prywatnego stanu backendów.

Wykonano również skan izolacji GUI.

Weryfikacja fazy:

- **180 testów PASS**;
- Ruff PASS;
- mypy PASS;
- brak importów PySide6 w warstwie kontrolerów;
- brak importów V3.

**Wynik: zakończona.**

---

## Faza 10 — legacy removal

Przeprowadzono zero-reference scan dla:

- FastAPI;
- `FastAPIServerManager`;
- `fastapi_server`;
- OpenVINO;
- `openvino_backend`;
- TranslateGemma INT8.

W aktywnym kodzie, testach i konfiguracji V4 nie pozostały aktywne referencje do tych technologii.

Nie zostały one migrowane „na siłę”. Ich funkcje zostały zastąpione przez architekturę V4, a stare ścieżki nie zostały włączone do nowego runtime'u.

Weryfikacja:

- **180 testów PASS**;
- Ruff PASS;
- mypy PASS.

**Wynik: zakończona.**

---

# 5. Packaging — co zostało zrobione

Packaging okazał się najbardziej problematyczną częścią całego cyklu.

Początkowo V4 posiadał launcher Java Filter Host, ale brakowało kompletnego katalogu runtime'u Okapi, do którego launcher się odwoływał.

Runtime został odzyskany z V3 i dodany do V4 w kontrolowany sposób.

Następnie runtime został również włączony do pakietu Python.

Do dystrybucji dodano:

- Okapi runtime;
- Java Filter Host;
- Apertium native runtime;
- `LICENSE`;
- `NOTICE`;
- teksty wymaganych licencji.

Powstał artefakt:

```text
tlumacz-0.40.0-py3-none-any.whl
```

Rozmiar:

```text
45 365 709 B
```

SHA-256:

```text
161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835
```

Artefakt przeszedł:

- instalację w czystym środowisku;
- uruchomienie `tlumacz --version`;
- smoke test Java Filter Host;
- smoke test bundlowanego silnika Apertium;
- pełny suite testów;
- analizę Ruff;
- analizę mypy.

---

# 6. Problemy podczas packagingu i ich rozwiązanie

## 6.1. Problem Git — `dubious ownership`

Pierwsza próba budowania wheel została zatrzymana przez:

```text
fatal: detected dubious ownership in repository at '/home/frs/Projekty'
```

Nie zmieniano globalnej konfiguracji Git.

Zamiast tego wykorzystano izolowany staging w lokalnym `./temp` i lokalny kontekst Git potrzebny wyłącznie do budowy artefaktu.

Problem środowiskowy został tym samym obejściem rozwiązany bez modyfikowania globalnych ustawień i bez ingerencji w V3.

---

## 6.2. Problem zapisu do `/tmp`

Pierwsza próba budowy danych Apertium ze źródeł V3 do stagingu w `/tmp` zakończyła się problemem uprawnień podczas czyszczenia kopii roboczej.

Rozwiązaniem było przeniesienie stagingu do:

```text
V4/temp
```

czyli miejsca kontrolowanego w obrębie drzewa projektu.

---

# 7. Co nie poszło i dlaczego

## 7.1. Nie udało się zamknąć kompletnej pary Apertium `eng-pol`

To jest główny techniczny blocker.

Silnik Apertium 3.9.12 działa, ale runtime nie posiada kompletnego zestawu danych językowych dla `eng-pol`.

Brakuje w szczególności:

```text
eng-pol.t1x.bin
```

Próba odtworzenia tego artefaktu z materiałów V3 zakończyła się:

```text
Undefined attr-item cas_sp
```

podczas:

```text
apertium-preprocess-transfer
```

Nie wykonano obejścia polegającego na wygenerowaniu niezweryfikowanego lub sztucznego binarium.

Powód pozostawienia tego problemu otwartego jest prosty: artefakt wydaniowy nie może udawać kompletności runtime'u, którego faktycznie nie posiada.

---

## 7.2. Nie udało się przygotować natywnego runtime'u Windows

Bundlowany runtime Apertium jest artefaktem:

```text
ELF 64-bit / x86-64
```

W V4 nie znaleziono odpowiadających natywnych artefaktów Windows `.exe`/`.dll` dla tego runtime'u.

Znalezione pliki wykonywalne Windows nie stanowiły runtime'u Apertium V4, więc nie zostały potraktowane jako rozwiązanie problemu.

W konsekwencji artefakt 0.40.0 może być obecnie traktowany jako **Release Candidate dla Linux**, a nie jako kompletne wydanie wieloplatformowe.

---

## 7.3. Nie zamknięto pełnego dependency closure

Podstawowa paczka działa w clean install, ale pełny komponent-po-komponencie inventory wszystkich runtime'ów i zależności dystrybucyjnych nie został jeszcze formalnie zamknięty.

Oznacza to, że nie można jeszcze uczciwie zadeklarować kompletnego, wieloplatformowego dependency closure dla finalnego wydania.

---

## 7.4. Nie zamknięto pełnego audytu licencji komponent-po-komponencie

Do artefaktu dodano:

- MIT;
- Apache 2.0;
- licencje ekosystemu Apertium;
- `LICENSE`;
- `NOTICE`;
- pliki licencyjne dystrybucji.

Nie oznacza to jednak automatycznie, że cały inventory licencyjny każdego dołączanego komponentu został formalnie zamknięty na poziomie finalnego release compliance.

Dlatego ten punkt pozostaje osobnym blockerem wydania.

---

# 8. Co świadomie nie zostało zrobione

## FastAPI i OpenVINO

Nie zostały przeniesione do V4 jako aktywne backendy.

Zostały usunięte z aktywnej ścieżki wykonawczej, zgodnie z decyzją architektoniczną migracji.

## Słownik

Słownik nie został wbudowany do artefaktu.

Jest niezależnym zasobem i nie stanowi blokera release. Może zostać dodany później bez przebudowy podstawowej architektury migracji.

## GitHub

Nie wykonano push do GitHub.

Artefakt pozostaje lokalnym artefaktem Release Candidate w drzewie V4.

## Modyfikacja V3

V3 nie został przekształcony w V4 i nie był modyfikowany jako część migracji.

Pozostał osobnym źródłem referencyjnym oraz punktem rollbacku.

---

# 9. Weryfikacja końcowa

Najważniejszy końcowy zestaw bramek dał:

| Kontrola | Wynik |
|---|---|
| pełny pytest | **182 passed** |
| compileall | **PASS** |
| Ruff | **PASS** |
| mypy | **PASS — 60 plików źródłowych** |
| contract suite | **PASS** |
| integration/E2E | **19 passed** |
| clean install wheel | **PASS** |
| `tlumacz --version` | **0.40.0** |
| Java Filter Host z wheel | **PASS** |
| Apertium engine | **3.9.12 — PASS** |
| dokumentacja migracji | **PASS** |
| release notes | **PASS** |
| migration notes | **PASS** |
| rollback procedure | **PASS** |

Najważniejsze jest to, że problemy pozostałe na końcu nie są ukrytymi błędami test suite'u. Są jawnie zidentyfikowanymi brakami dotyczącymi kompletności dystrybucji.

---

# 10. Stan końcowy architektury

Po migracji V4 posiada:

- modularną warstwę aplikacyjną;
- jawne kontrakty;
- niezależne backendy;
- LlamaCppBackend;
- CloudBackend;
- ApertiumBackend;
- Filter Engine;
- Java Filter Host;
- kontrolowany Okapi runtime;
- obsługę DOCX;
- ODT;
- HTML/XHTML;
- Markdown;
- EPUB;
- XLIFF;
- TranslationOrchestrator;
- DocumentTranslationService;
- cache tłumaczeń;
- walidację wyników;
- kontrolę cancellation;
- kontrolery GUI;
- mechanizmy workspace/session;
- packaging Python;
- bundlowane runtime'y;
- dokumentację release i rollback.

Najważniejszą zmianą jakościową nie jest sama liczba nowych plików, ale **rozłączenie odpowiedzialności**, które w V3 były skupione w większych komponentach.

---

# 11. Ocena przebiegu migracji

Migracja przebiegła zgodnie z główną strategią: zamiast przenosić V3 mechanicznie, zrekonstruowano potrzebne funkcje w V4 i zweryfikowano je kontraktami oraz testami.

Największe sukcesy techniczne:

1. V4 powstał jako niezależny projekt.
2. V3 pozostał nienaruszonym źródłem referencyjnym.
3. FastAPI/OpenVINO nie zostały przeniesione do nowego runtime'u.
4. Filter Engine został wydzielony jako osobna warstwa.
5. Runtime Okapi został kontrolowany przez V4.
6. Backendy zostały odseparowane od GUI i logiki dokumentowej.
7. Monolityczny Translator został rozbity.
8. GUI otrzymało warstwę kontrolerów.
9. Packaging Linux osiągnął działający Release Candidate.
10. Całość przeszła końcowy suite **182 testów**.

Największym niedomkniętym obszarem pozostał packaging wieloplatformowy i kompletność części natywnych runtime'ów, a nie sama architektura aplikacji.

---

# 12. Rzeczywisty status projektu po migracji

Stan należy interpretować następująco:

```text
MIGRACJA V3 → V4
        │
        ├── architektura ................. ZAKOŃCZONA
        ├── kontrakty .................... ZAKOŃCZONE
        ├── Filter Engine ................ ZAKOŃCZONY
        ├── backendi ..................... ZAKOŃCZONE
        ├── usługi dokumentowe ........... ZAKOŃCZONE
        ├── translator ................... ZAKOŃCZONY
        ├── GUI .......................... ZAKOŃCZONE
        ├── legacy removal ............... ZAKOŃCZONE
        │
        ├── packaging Linux .............. RC / ZWERYFIKOWANY
        ├── Apertium eng-pol ............. OTWARTE
        ├── Windows runtime .............. OTWARTE
        ├── dependency closure ........... OTWARTE
        └── audyt licencji ............... OTWARTY
```

Faza 13 została zamknięta jako **lokalny handoff freeze**.

Nie oznacza to, że 0.40.0 jest już finalnym wydaniem.

---

# 13. Warunki zamknięcia wydania 0.40.0

Finalne wydanie powinno zostać oznaczone dopiero po spełnieniu następujących warunków:

### 1. Apertium

Dostarczenie kompletnego i zweryfikowanego `eng-pol`, w tym brakującego artefaktu transferu.

### 2. Windows

Dostarczenie oraz przetestowanie natywnego runtime'u Windows i wszystkich wymaganych zasobów.

### 3. Dependency closure

Formalne zamknięcie inventory wszystkich komponentów dołączanych do artefaktu.

### 4. Licencje

Komponentowy audyt licencji, NOTICE i obowiązków dystrybucyjnych dla finalnego zestawu runtime'ów.

### 5. Ponowna bramka release

Po zamknięciu powyższych punktów należy ponownie wykonać:

- pełny pytest;
- compileall;
- Ruff;
- mypy;
- contract suite;
- integration/E2E;
- clean install;
- smoke test runtime'ów;
- kontrolę artefaktów;
- kontrolę dokumentacji;
- kontrolę rollbacku.

---

# 14. Podsumowanie końcowe

Migracja V3 → V4 została przeprowadzona jako **rzeczywista rekonstrukcja architektury**, a nie zmiana nazwy istniejącego projektu.

Powstał niezależny V4 z nowymi kontraktami, warstwą aplikacyjną, Filter Engine, adapterami backendów, usługami dokumentowymi, kontrolerami GUI i kontrolowanym packagingiem.

Najważniejszy rezultat jest taki, że rdzeń V4 został doprowadzony do stanu, w którym można go testować, instalować i uruchamiać niezależnie od drzewa źródłowego V3. Końcowa weryfikacja potwierdziła **182 przechodzące testy**, poprawność statyczną oraz działający Linux Release Candidate.

Nie wszystko zostało jednak zakończone. Pozostałe problemy dotyczą przede wszystkim **kompletności dystrybucji**, a nie podstawowej architektury:

- brak kompletnej pary Apertium `eng-pol`;
- brak natywnego runtime'u Windows;
- niedomknięte pełne dependency closure;
- niedomknięty komponentowy audyt licencji.

Te problemy zostały pozostawione jawnie, bez tworzenia sztucznych artefaktów i bez oznaczania niepełnego pakietu jako finalnego release.

W konsekwencji końcowy stan projektu należy określić jako:

> **Migracja V3 → V4 — zakończona na poziomie architektury, implementacji i lokalnego handoffu. V4 0.40.0 — Release Candidate dla Linux, finalne wydanie otwarte do czasu zamknięcia blockerów packagingowych.**

---

## 15. Dokumenty źródłowe i uzupełniające

Najważniejsze dokumenty końcowego stanu migracji:

- `docs/PLAN_MIGRACJI-v4.md`
- `docs/MIGRATION_INVENTORY.md`
- `docs/MIGRATION_NOTES_V3_TO_V4.md`
- `docs/release/RELEASE_NOTES_0.40.0.md`
- `docs/release/ROLLBACK_0.40.0.md`
- `docs/STATUS.md`
- `docs/TODO.md`
- `docs/CHANGELOG.md`
- `docs/reports/FAZA_11_PACKAGING_BLOCKED_2026-09-30.md`
- `docs/reports/FAZA_12_RELEASE_2026-09-30.md`
- `docs/reports/FAZA_13_FINAL_HANDOFF_2026-09-30.md`

### Artefakt Release Candidate

`temp/wheel/tlumacz-0.40.0-py3-none-any.whl`

SHA-256:

`161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835`

---

**Koniec raportu.**
