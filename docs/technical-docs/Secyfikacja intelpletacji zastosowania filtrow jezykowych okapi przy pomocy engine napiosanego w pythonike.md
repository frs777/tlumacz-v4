# Specyfikacja implementacji zastosowania filtrów językowych Okapi przy pomocy Engine napisanego w Pythonie

> **Nazwa pliku zgodna z poleceniem użytkownika:** `Secyfikacja intelpletacji zastosowania filtrow jezykowych okapi przy pomocy engine napiosanego w pythonike.md`
>
> Dokument opisuje aktualną implementację Filter Engine V4 i Java/Python Filter Host Bridge. Jest przeznaczony jako specyfikacja odtworzeniowa dla agentów programistycznych.

**Status:** implementacja wykonana i zweryfikowana  
**Zakres:** wyłącznie Filter Engine, adaptery Okapi oraz Java/Python bridge  
**Poza zakresem:** GUI, backendy tłumaczeniowe, Apertium i pozostałe warstwy aplikacji

---

## 1. Cel rozwiązania

Celem jest zastąpienie warstwy aplikacyjnej/runtime Okapi własnym, minimalnym **Python Filter Engine**, przy jednoczesnym zachowaniu istniejących filtrów Okapi napisanych w Javie.

Nie należy interpretować tego rozwiązania jako usunięcia Okapi.

Prawidłowy model jest następujący:

```text
Tłumacz V4
    │
    ▼
Python Filter Engine
    │
    │ JSON Lines / stdin / stdout
    ▼
Java Filter Host
    │
    ▼
istniejące filtry Okapi Java
    │
    ▼
writer Okapi
    │
    ▼
dokument wynikowy
```

Python przejmuje odpowiedzialność za orkiestrację procesu, natomiast Java pozostaje cienką warstwą wykonawczą dla istniejących filtrów Okapi.

### 1.1. Co zostało zastąpione

Zastąpiona została zależność od Okapi jako kompletnej aplikacji/frameworku sterującego procesem.

Nie zastąpiono parserów formatów dokumentów.

Nie przepisano filtrów DOCX, ODT, EPUB, HTML, Markdown ani XLIFF.

Zachowane zostały biblioteki Okapi potrzebne do wykonywania tych filtrów.

### 1.2. Zasada nadrzędna

> **Python jest właścicielem workflow i kontraktu jednostek tłumaczeniowych. Java jest właścicielem wykonywania istniejących filtrów Okapi i writerów.**

---

## 2. Architektura

```text
                    TLUMACZ V4
                        │
                        ▼
              ┌───────────────────┐
              │  Python Filter    │
              │      Engine       │
              └─────────┬─────────┘
                        │
                JSON Lines / stdin
                        │
                        ▼
              ┌───────────────────┐
              │  Java Filter Host │
              │   własny bridge   │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │  Okapi Core +     │
              │  Okapi Filters    │
              └───────────────────┘
```

Przepływ dokumentu:

```text
INPUT
  │
  ▼
FilterRegistry
  │
  ▼
FilterContract
  │
  ▼
filter.open()
  │
  ▼
Java Filter Host
  │
  ▼
Okapi IFilter
  │
  ▼
Event stream
  │
  ▼
TextUnit
  │
  ▼
OkapiUnit[]
  │
  ▼
FilterValidator
  │
  ▼
MarkerValidator
  │
  ▼
backend tłumaczeniowy
  │
  ▼
target map
  │
  ▼
Java Filter Host
  │
  ▼
Okapi TextUnit + target
  │
  ▼
IFilterWriter
  │
  ▼
OUTPUT
```

---

## 3. Struktura modułu

Główny moduł:

```text
src/tlumacz/filter_engine/
```

Kluczowe elementy:

```text
filter_engine/
├── __init__.py
├── lifecycle.py
├── marker_validator.py
├── processor.py
├── protocol.py
├── registry.py
├── validator.py
└── filters/
    ├── __init__.py
    ├── docx.py
    ├── epub.py
    ├── html.py
    ├── markdown.py
    ├── odt.py
    ├── okapi.py
    └── xliff.py
```

Kod Java:

```text
java/filter-host/src/main/java/pl/tlumacz/filterhost/FilterHost.java
```

Druga kopia źródła hosta, pakowana z aplikacją:

```text
src/tlumacz/resources/filter-host/FilterHost.java
```

Launcher:

```text
src/tlumacz/resources/filter-host/run.sh
```

Runtime Okapi:

```text
src/tlumacz/resources/okapi-runtime/
```

---

## 4. Odpowiedzialności poszczególnych warstw

| Warstwa | Odpowiedzialność |
|---|---|
| `DocumentProcessor` | pełny workflow dokumentu |
| `FilterRegistry` | wybór implementacji filtra |
| `FilterLifecycle` | otwarcie, sesja i zamknięcie filtra |
| `FilterValidator` | integralność jednostek i targetów |
| `MarkerValidator` | ochrona inline codes |
| `FilterHostClient` | transport Python ↔ Java |
| `FilterHost` | minimalna warstwa Java |
| Okapi `IFilter` | parsowanie formatu |
| Okapi `TextUnit` | reprezentacja jednostki tłumaczeniowej |
| Okapi `IFilterWriter` | rekonstrukcja dokumentu |
| backend tłumaczeniowy | tłumaczenie tekstu |

Granica odpowiedzialności jest celowa i nie powinna być rozmywana.

---

## 5. DocumentProcessor

Plik:

```text
src/tlumacz/filter_engine/processor.py
```

`DocumentProcessor` jest centralnym orkiestratorem.

### 5.1. Wejście

Proces otrzymuje:

- ścieżkę dokumentu wejściowego,
- ścieżkę dokumentu wynikowego,
- język źródłowy,
- język docelowy,
- callback `translate` lub `translate_many`,
- workspace,
- opcjonalny token anulowania,
- opcjonalny callback postępu.

### 5.2. Algorytm

1. Sprawdź cancellation token.
2. Sprawdź istnienie pliku wejściowego.
3. Utwórz workspace.
4. Wybierz filtr przez `FilterRegistry`.
5. Otwórz sesję przez `FilterLifecycle`.
6. Wykonaj `extract()`.
7. Zweryfikuj jednostki przez `FilterValidator`.
8. Dla każdej jednostki zweryfikuj markery.
9. Przekaż tekst do backendu tłumaczeniowego.
10. Zweryfikuj markery w wyniku.
11. Zweryfikuj kompletność mapy targetów.
12. Wykonaj `write()`.
13. Zamknij sesję.

### 5.3. Pseudokod

```python
source = Path(input_path).resolve()
destination = Path(output_path).resolve()

filter_contract = registry.for_path(source)

with lifecycle.open(
    source,
    source_language=source_language,
    target_language=target_language,
    workspace=workspace,
) as session:

    units = FilterValidator.validate_units(
        filter_contract.extract(session)
    )

    targets = {}

    for unit_id, source_text in units:
        MarkerValidator.validate(source_text)

        translated = translate(source_text).text

        MarkerValidator.validate(translated)

        targets[unit_id] = translated

    FilterValidator.validate_targets(units, targets)

    filter_contract.write(session, targets, destination)
```

W rzeczywistej implementacji istnieje także wariant `translate_many`, postęp oraz cancellation.

---

## 6. FilterRegistry

Plik:

```text
src/tlumacz/filter_engine/registry.py
```

Registry odpowiada wyłącznie za wybór filtra na podstawie rozszerzenia.

Przykładowa zasada:

```text
.docx → filtr DOCX / Okapi
.odt  → filtr ODT / Okapi
.html → filtr HTML / Okapi
.md   → filtr Markdown / Okapi
.epub → filtr EPUB / Okapi
.xlf  → AutoXliffFilter
.xliff → AutoXliffFilter
```

Registry:

- normalizuje rozszerzenia do lowercase,
- wymaga niepustego suffixu,
- odrzuca konflikt rejestracji,
- zwraca obiekt implementujący `FilterContract`.

Registry nie parsuje dokumentów.

### 6.1 Magazyn filtrów

Lokalizacja magazynu filtrów jest oddzielona od samego mechanizmu rejestracji.

Implementacja: src/tlumacz/filter_engine/filter_store.py

`FilterStore` jest prostym obiektem lokalizującym katalog, z którego aplikacja ma korzystać jako magazynu filtrów.

W bieżącej wersji magazynem użytkownika jest `$HOME/.config/tlumacz/filters/` (z uwzględnieniem `XDG_CONFIG_HOME`). Pakiety `.tplugin` są rozpakowywane do tymczasowego `/tmp/filters/`.

`FilterRegistry` otrzymuje ścieżkę magazynu przez parametr `filter_store`, ale sam nie tworzy ani nie przechowuje instancji wszystkich filtrów. Aktywna ścieżka aplikacji rejestruje **fabryki filtrów** przez `register_lazy()`. Fabryka jest wywoływana dopiero przez `FilterRegistry.for_path()` po rozpoznaniu rozszerzenia dokumentu.

Cykl życia jest zatem następujący:

```text
załadowanie/rozpoznanie pliku
        ↓
FilterRegistry.for_path()
        ↓
utworzenie właściwego filtra
        ↓
FilterLifecycle.open()
        ↓
extract → tłumaczenie → merge
        ↓
FilterLifecycle.close()
        ↓
brak referencji do instancji w rejestrze
```

Filtr jest dzięki temu gotowy przed rozpoczęciem tłumaczenia, ale nie jest utrzymywany jako instancja przez cały czas działania aplikacji. Instancja żyje tylko w zakresie przetwarzania danego dokumentu. Dla kolejnego dokumentu może zostać utworzona nowa instancja właściwego formatu.

Ten etap nie jest jeszcze dynamicznym loaderem JAR-ów. Implementacje Java pozostają obecnie w `okapi-runtime`, a `FilterHost` nadal korzysta ze stałego classpath. Kolejny etap ma wprowadzić dynamiczny `ClassLoader`, który będzie pobierał implementację konkretnego filtra z magazynu `filters/`, przy zachowaniu wspólnego runtime Okapi poza magazynem implementacji.


Plik:

```text
src/tlumacz/filter_engine/lifecycle.py
```

Odpowiada za deterministyczne zarządzanie sesją.

Model:

```text
open
  ↓
session
  ↓
extract
  ↓
translation
  ↓
write
  ↓
close
```

Sesja jest używana przez context manager:

```python
with lifecycle.open(...) as session:
    ...
```

Nawet przy wyjątku wykonuje się `close()`.

Nie wolno pozostawiać aktywnej sesji Java/Okapi po zakończeniu dokumentu.

---

## 8. Kontrakt jednostki tłumaczeniowej

Pythonowy Engine operuje na uproszczonym kontrakcie:

```text
unit_id + source
```

czyli logicznie:

```python
[
    ("unit-1", "tekst źródłowy"),
    ("unit-2", "drugi tekst"),
]
```

Adapter Okapi może wewnętrznie przechowywać dodatkowe informacje, w szczególności:

- dane o kodach inline,
- informacje potrzebne do rekonstrukcji,
- dane segmentacji,
- informacje o filtrze i sesji.

Jednak backend tłumaczeniowy nie musi znać wewnętrznego modelu Okapi.

---

## 9. FilterValidator

Plik:

```text
src/tlumacz/filter_engine/validator.py
```

Walidacja odbywa się na granicy Engine ↔ filtr.

### 9.1. Walidacja jednostek

Sprawdzane jest:

- jednostka musi mieć ID,
- ID musi być niepuste,
- source musi być typu `str`,
- ID nie mogą się powtarzać.

### 9.2. Walidacja targetów

Po tłumaczeniu:

```text
expected = IDs wyekstrahowanych jednostek
actual   = IDs otrzymanych targetów
```

Zbiory muszą być identyczne.

Błąd występuje, jeżeli:

- brakuje targetu,
- istnieje nadmiarowy target,
- target ma niepoprawny typ.

Silnik nie pozwala wygenerować dokumentu z częściowym lub niespójnym mapowaniem.

---

## 10. MarkerValidator

Plik:

```text
src/tlumacz/filter_engine/marker_validator.py
```

Okapi używa inline codes, które są reprezentowane w tekście przez specjalne znaki PUA.

Własny kontrakt Engine rozpoznaje:

```text
U+E101 — marker otwierający
U+E102 — marker zamykający
U+E103 — marker izolowany
```

Indeks kodu jest reprezentowany przez znak od:

```text
U+E110
```

### 10.1. Reguła

Marker zajmuje dwa znaki:

```text
marker_type + marker_index
```

### 10.2. Walidacja

Silnik sprawdza:

1. czy marker ma znak indeksu,
2. czy indeks jest nieujemny,
3. czy przy podanej tabeli kodów indeks mieści się w zakresie,
4. czy niedozwolony znak PUA nie pojawia się jako zwykły tekst.

### 10.3. Dlaczego jest to konieczne

Jeżeli backend MT usunie lub zmieni inline code, writer Okapi może wygenerować dokument uszkodzony strukturalnie.

Dlatego walidacja wykonywana jest:

- przed tłumaczeniem,
- po tłumaczeniu.

---

## 11. Java/Python Bridge

Bridge nie wykorzystuje:

- JNI,
- JPype,
- Py4J,
- PyJNIus,
- HTTP,
- REST,
- gRPC.

Zastosowany mechanizm to:

```text
Python subprocess
      │
      ├── stdin  → JSON Lines
      ├── stdout ← JSON Lines
      └── stderr ← diagnostyka
```

Python uruchamia długowieczny proces Java.

Nie uruchamia nowej JVM dla każdej jednostki.

---

## 12. FilterHostClient

Plik:

```text
src/tlumacz/filter_engine/protocol.py
```

`FilterHostClient`:

- uruchamia proces,
- wysyła JSON,
- odbiera JSON,
- obsługuje timeout,
- czyta stderr,
- wykrywa zakończenie procesu,
- klasyfikuje błędy,
- pilnuje `request_id`,
- pilnuje wersji protokołu.

Proces posiada osobne wątki czytające stdout i stderr.

Dzięki temu diagnostyka Java nie miesza się z protokołem stdout.

---

## 13. Protokół JSON Lines

Wersja protokołu:

```text
protocol_version = 1
```

### 13.1. Żądanie

Minimalny format:

```json
{
  "protocol_version": 1,
  "request_id": "abc123",
  "operation": "extract",
  "payload": {}
}
```

### 13.2. Odpowiedź sukcesu

```json
{
  "protocol_version": 1,
  "request_id": "abc123",
  "ok": true,
  "result": {}
}
```

### 13.3. Odpowiedź błędu

```json
{
  "protocol_version": 1,
  "request_id": "abc123",
  "ok": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Opis błędu",
    "retryable": false
  }
}
```

### 13.4. Zasady

Python musi sprawdzić:

- wersję protokołu,
- `request_id`,
- pole `ok`,
- strukturę `error`.

Nie wolno uznawać dowolnego tekstu stdout za poprawną odpowiedź.

---

## 14. Operacje Filter Host

Host udostępnia m.in.:

```text
hello
version
health
capabilities
extract
merge
```

Dla właściwego workflow najważniejsze są:

```text
extract
merge
```

Architektura celowo rozdziela ekstrakcję i scalanie.

---

## 15. Dlaczego extract i merge są rozdzielone

Nie należy przechowywać całego strumienia eventów Okapi po stronie Pythona.

Zamiast:

```text
Java → wszystkie Eventy → Python → wszystkie Eventy → Java
```

stosowany jest model:

```text
Java
  ↓
extract
  ↓
translation units
  ↓
Python
  ↓
translation
  ↓
target map
  ↓
Java
  ↓
merge
  ↓
writer
```

Zasada:

> Java odpowiada za strukturę dokumentu, Python za workflow tłumaczenia.

---

## 16. Extract — szczegółowa zasada

Java otrzymuje informacje o:

- filtrze,
- pliku wejściowym,
- języku źródłowym,
- języku docelowym,
- workspace.

Host wybiera odpowiednią klasę Okapi.

Następnie:

```text
RawDocument
   ↓
IFilter
   ↓
Event stream
   ↓
TEXT_UNIT
   ↓
TextUnit
   ↓
source
   ↓
OkapiUnit
```

Interesujące dla Engine są przede wszystkim eventy typu `TEXT_UNIT`.

Pozostałe eventy pozostają wewnętrzną odpowiedzialnością Java/Okapi.

---

## 17. Filtry Okapi wykorzystywane przez Host

Runtime zawiera istniejące filtry m.in. dla:

- OpenXML / DOCX,
- OpenOffice / ODT,
- EPUB,
- HTML,
- Markdown,
- XLIFF 1.2,
- XLIFF 2.x,
- JSON,
- YAML,
- archiwów,
- abstract markup.

Przykładowe mapowanie logiczne:

```text
openxml   → OpenXMLFilter
openoffice → OpenOfficeFilter
epub      → EpubFilter
html      → HtmlFilter
markdown  → MarkdownFilter
xliff     → XLIFFFilter
xliff2    → XLIFF2Filter
```

Nazwy klas należy weryfikować względem wersji runtime Okapi używanej przez repozytorium.

---

## 18. Merge — szczegółowa zasada

Po tłumaczeniu Python posiada:

```python
{
    "unit-1": "Witaj",
    "unit-2": "To jest drugi tekst"
}
```

Host ponownie otwiera dokument przez odpowiedni filtr.

Dla każdego `TextUnit`:

1. ustala ID,
2. znajduje odpowiadający target,
3. tworzy targetowy fragment,
4. zachowuje wymagane informacje inline,
5. przekazuje event do writer'a Okapi.

Writer Okapi odtwarza format dokumentu.

Python nie rekonstruuje DOCX/ODT/EPUB ręcznie.

---

## 19. XLIFF 1.2 i XLIFF 2.x

Dla rozszerzeń:

```text
.xlf
.xliff
```

stosowany jest `AutoXliffFilter`.

Wybór następuje na podstawie XML namespace/version.

Przykładowo:

```xml
<xliff version="1.2">
```

oznacza XLIFF 1.2.

Natomiast:

```xml
<xliff version="2.0">
```

oznacza XLIFF 2.x.

Nie należy zakładać, że samo rozszerzenie wystarcza do rozróżnienia wersji.

---

## 20. Specyfika XLIFF 2.x podczas merge

W XLIFF 2.x target musi zachować strukturę segmentów.

Niepoprawne jest bezwarunkowe tworzenie niesegmentowanego targetu przez zwykłe `setTargetContent()`, jeżeli writer wymaga targetu segmentowanego.

Aktualna implementacja tworzy target z zachowaniem segmentacji, m.in. przez:

```text
unit.createTarget(targetLocale, true, 4)
```

i ustawia coded text w odpowiednim `TextContainer`.

Jeżeli source TextUnit posiada więcej niż jeden segment i implementacja nie ma bezpiecznej reprezentacji targetu, host zwraca błąd:

```text
SEGMENTATION_REQUIRED
```

zamiast generować potencjalnie uszkodzony XLIFF.

---

## 21. Duplikujące się TextUnit ID

Dokument może zawierać wiele jednostek o tym samym ID.

Przykład:

```text
1
1
1
```

Python wymaga unikalnych kluczy, dlatego adapter nadaje identyfikatory sesyjne:

```text
1
1::2
1::3
```

Pierwsze wystąpienie zachowuje oryginalne ID.

Kolejne otrzymują sufiks occurrence.

Podczas `merge` Java prowadzi ten sam licznik:

```text
ID 1, occurrence 1 → target 1
ID 1, occurrence 2 → target 1::2
ID 1, occurrence 3 → target 1::3
```

Mapowanie jest przez to deterministyczne.

---

## 22. Dlaczego nie przekazujemy całego modelu Okapi do Python

Okapi posiada bogaty model:

- Event,
- TextUnit,
- TextContainer,
- TextPart,
- Code,
- Segment,
- writer,
- filter state.

Nie jest celem kopiowanie tego modelu 1:1 do Pythona.

Python powinien otrzymać minimalną informację potrzebną do tłumaczenia:

```text
ID + tekst źródłowy
```

Java zachowuje informacje niezbędne do rekonstrukcji dokumentu.

Jest to jeden z głównych powodów zastosowania bridge.

---

## 23. Runtime Java

Runtime znajduje się w:

```text
src/tlumacz/resources/okapi-runtime/
```

Kluczowe artefakty:

```text
okapi-core-1.49.0-SNAPSHOT.jar
runtime-openxml-1.49.0-SNAPSHOT.jar
runtime-openoffice-1.49.0-SNAPSHOT.jar
runtime-epub-1.49.0-SNAPSHOT.jar
runtime-html-1.49.0-SNAPSHOT.jar
runtime-xliff-1.49.0-SNAPSHOT.jar
runtime-xliff2-1.49.0-SNAPSHOT.jar
runtime-json-1.49.0-SNAPSHOT.jar
runtime-yaml-1.49.0-SNAPSHOT.jar
runtime-abstractmarkup-1.49.0-local.jar
runtime-archive-1.49.0-local.jar
runtime-generated-parser-compat-1.48.jar
runtime-lib-xliff2-1.49.0-local.jar
```

W `lib/` znajdują się zależności pomocnicze.

---

## 24. Zależności pomocnicze Java

Aktualny runtime zawiera m.in.:

```text
common-io-3.12.0.jar
common-lang-3.12.0.jar

jackson-annotations-2.18.0.jar
jackson-core-2.18.0.jar
jackson-databind-2.18.0.jar

icu4j-75.1.jar

slf4j-api-2.0.16.jar

jericho-html-3.4.jar

stax2-api-4.2.2.jar
woodstox-core-7.0.0.jar

snakeyaml-engine-2.8.jar
```

Dla Markdown obecne są biblioteki Flexmark 0.64.8, w tym:

```text
flexmark
flexmark-ext-admonition
flexmark-ext-escaped-character
flexmark-ext-gfm-strikethrough
flexmark-ext-tables
flexmark-ext-yaml-front-matter
flexmark-util-*
```

Nie należy dodawać tych zależności do Pythona. Są one zależnościami runtime Java.

---

## 25. Zależności Python

Projekt wymaga:

```text
Python >= 3.12,<3.15
```

Zależności projektu:

```text
PySide6>=6.5
lxml>=5.0
lingua-language-detector>=2.1.1
```

Dla samego Filter Engine najważniejsze są:

- standardowa biblioteka Pythona,
- `lxml` dla natywnych filtrów Pythonowych, w szczególności HTML.

Zależności developerskie:

```text
pytest>=8.0
ruff>=0.9
mypy>=1.14
```

Bridge nie wymaga:

```text
JPype
Py4J
PyJNIus
JNI
```

---

## 26. Java JDK

Host jest zwykłym procesem Java i wymaga środowiska zawierającego:

```text
java
javac
```

Nie wymaga:

- Spring Boot,
- serwera HTTP,
- kontenera webowego,
- REST,
- gRPC.

Launcher kompiluje/uruchamia `FilterHost.java` z lokalnym classpathem runtime Okapi.

---

## 27. Launcher

Plik:

```text
src/tlumacz/resources/filter-host/run.sh
```

Odpowiada za:

1. znalezienie runtime,
2. przygotowanie classpath,
3. przygotowanie katalogu build,
4. kompilację hosta Java, jeżeli jest potrzebna,
5. uruchomienie `pl.tlumacz.filterhost.FilterHost`.

Domyślny katalog build jest powiązany z cache użytkownika.

Możliwe są zmienne środowiskowe:

```text
TLUMACZ_FILTER_HOST_BUILD_DIR
TLUMACZ_FILTER_HOST_LIB_DIR
```

Nie należy hardkodować ścieżki repozytorium w samym Engine.

---

## 28. Izolacja procesu

Java jest osobnym procesem.

Jeżeli JVM zakończy się błędem, Python może otrzymać:

```text
HOST_EXITED
```

Jeżeli komunikacja zostanie zerwana:

```text
HOST_IO_ERROR
```

Jeżeli przekroczony zostanie timeout:

```text
TIMEOUT
```

Jeżeli wersja protokołu jest niezgodna:

```text
UNSUPPORTED_PROTOCOL
```

Błędy mogą mieć również:

```text
retryable = true/false
```

---

## 29. Timeout i diagnostyka

Pythonowy klient ma konfigurowalny timeout.

Domyślnie:

```text
120 sekund
```

stderr Java jest czytany osobnym wątkiem.

Przechowywany jest ograniczony ogon diagnostyczny, aby przy śmierci hosta komunikat błędu zawierał użyteczne informacje.

Nie należy kierować diagnostyki Java do stdout, ponieważ stdout jest kanałem protokołu JSON Lines.

---

## 30. Workspace

Każda sesja dokumentu posiada workspace.

Workspace może przechowywać:

```text
extract data
target map
artefakty pośrednie
dane sesji
```

Nie należy używać globalnych plików tymczasowych współdzielonych przez wszystkie dokumenty.

Workspace jest elementem izolacji sesji.

---

## 31. Zasada bezpieczeństwa danych

Minimalny przepływ:

```text
plik wejściowy
    ↓
Java/Okapi
    ↓
tekst
    ↓
Python
    ↓
backend tłumaczeniowy
    ↓
target
    ↓
Java/Okapi
    ↓
plik wyjściowy
```

Okapi pozostaje właścicielem struktury dokumentu.

Python nie powinien manipulować strukturą binarną dokumentu, jeżeli istnieje odpowiedni writer Okapi.

---

## 32. Czego nie należy robić podczas dalszego rozwoju

Agent rozwijający ten moduł nie powinien:

1. przepisywać parsera DOCX, jeżeli dostępny jest filtr Okapi;
2. ręcznie modyfikować ZIP/XML dokumentu zamiast używać writer'a;
3. uruchamiać JVM dla każdej jednostki;
4. przenosić całego event streamu Okapi do Pythona;
5. dodawać JNI/JPype tylko po to, aby wywołać filtr;
6. pozwalać backendowi MT modyfikować inline codes;
7. usuwać walidacji targetów;
8. ignorować różnicy XLIFF 1.2/XLIFF 2.x;
9. zakładać unikalności TextUnit ID bez mechanizmu occurrence;
10. traktować Okapi jako głównego orchestratora aplikacji.

---

## 33. Minimalny kontrakt do odtworzenia

Aby odtworzyć rozwiązanie od zera, należy zbudować kolejno:

### Etap A — kontrakty Python

```text
FilterContract
OkapiUnit
FilterRegistry
FilterLifecycle
FilterValidator
MarkerValidator
```

### Etap B — orkiestrator

```text
DocumentProcessor
```

### Etap C — transport

```text
FilterHostClient
JSON Lines protocol
request_id
protocol_version
error model
timeout
stderr reader
```

### Etap D — Java Host

```text
FilterHost
capabilities
extract
merge
```

### Etap E — integracja Okapi

```text
IFilter
RawDocument
Event
TextUnit
TextContainer
IFilterWriter
```

### Etap F — adaptery

```text
DOCX
ODT
HTML
Markdown
EPUB
XLIFF
```

### Etap G — testy round-trip

Dla każdego formatu:

```text
input
  ↓
extract
  ↓
translation
  ↓
merge
  ↓
output
```

i należy sprawdzić, że dokument wynikowy jest prawidłowo rekonstruowany.

---

## 34. Kolejność implementacji dla nowego agenta

Agent odtwarzający rozwiązanie powinien pracować w następującej kolejności:

1. Zidentyfikować wersję Pythona.
2. Zidentyfikować JDK i dostępność `java` oraz `javac`.
3. Zidentyfikować dokładny zestaw JAR-ów Okapi.
4. Zbudować minimalny `FilterHost.java`.
5. Zaimplementować `hello/version/health/capabilities`.
6. Zaimplementować JSON Lines.
7. Zaimplementować Python `FilterHostClient`.
8. Zaimplementować `extract`.
9. Zaimplementować `merge`.
10. Zaimplementować `FilterRegistry`.
11. Zaimplementować lifecycle.
12. Zaimplementować walidatory.
13. Zaimplementować adapter Okapi.
14. Dodać XLIFF auto-detection.
15. Dodać duplicate-ID mapping.
16. Dodać testy round-trip.
17. Dopiero później integrować Engine z wyższymi warstwami aplikacji.

Nie należy zaczynać od GUI.

---

## 35. Testowanie

Testy jednostkowe obejmują m.in.:

- registry,
- lifecycle,
- validator,
- marker validator,
- protocol,
- adapter Okapi.

Testy integracyjne uruchamiają rzeczywisty JVM i runtime Okapi.

Zweryfikowane formaty obejmują:

```text
DOCX
ODT
HTML
Markdown
EPUB
XLIFF 1.2
XLIFF 2.0
duplicate TextUnit IDs
```

Aktualny wynik integracji Filter Engine:

```text
3 testy integracyjne — PASS
```

Weryfikacja lint:

```text
ruff check — PASS
```

W całym projekcie pozostawały dwa niezwiązane z Filter Engine problemy:

1. test uprawnień plików prywatnego runtime Apertium;
2. test QML związany z istniejącą niespójnością językową.

Nie należy przypisywać tych błędów Filter Engine.

---

## 36. Ważne ograniczenie architektoniczne

To rozwiązanie nie oznacza, że Okapi przestało być zależnością.

Prawidłowe stwierdzenie brzmi:

> **Okapi zostało zdegradowane z pozycji głównego frameworku aplikacji do roli biblioteki wykonującej konkretne filtry dokumentowe.**

Pythonowy Engine kontroluje:

- wybór filtra,
- lifecycle,
- ekstrakcję,
- walidację,
- przekazanie tekstu do tłumaczenia,
- walidację wyniku,
- mapowanie targetów,
- merge.

Okapi kontroluje:

- parsowanie konkretnego formatu,
- reprezentację dokumentu,
- inline codes,
- writer,
- rekonstrukcję dokumentu.

---

## 37. Reguła rozszerzania

Dodając nowy format, najpierw należy odpowiedzieć:

> Czy istnieje odpowiedni filtr Okapi?

Jeżeli tak:

```text
Nowy format
    ↓
Okapi Filter
    ↓
adapter FilterContract
    ↓
Registry
```

Nie należy pisać nowego parsera Pythonowego bez potrzeby.

Jeżeli filtr Okapi nie istnieje, dopiero wtedy można rozważyć natywny filtr Pythonowy.

---

## 38. Reguła zmian protokołu

Jeżeli zmieniany jest protokół:

1. zwiększyć `protocol_version`, jeżeli zmiana jest niekompatybilna;
2. zachować `request_id`;
3. zaktualizować Python client;
4. zaktualizować Java Host;
5. zaktualizować testy kontraktowe;
6. zaktualizować dokumentację.

Nie wolno jednostronnie zmienić formatu JSON.

---

## 39. Reguła zmian w Okapi

Nie należy modyfikować bibliotek Okapi tylko po to, aby dopasować je do Engine.

Preferowana kolejność:

```text
Engine adapter
    ↓
bridge
    ↓
Okapi API
```

Zmiana samego runtime Okapi jest dopuszczalna tylko wtedy, gdy wymagają tego konkretne możliwości filtrów i zostanie zweryfikowana kompatybilność całego zestawu JAR-ów.

---

## 40. Reguła dotycząca segmentacji

Segmentacja jest własnością filtra i formatu.

Python nie powinien arbitralnie dzielić TextUnit na segmenty, jeżeli Okapi wymaga zachowania istniejącej struktury.

Szczególnie dotyczy to XLIFF 2.x.

Jeżeli bezpieczny merge nie jest możliwy:

```text
BŁĄD
SEGMENTATION_REQUIRED
```

jest lepszy niż wygenerowanie pozornie poprawnego, lecz semantycznie uszkodzonego dokumentu.

---

## 41. Reguła dotycząca inline codes

Inline code jest częścią danych tłumaczeniowych, ale nie jest zwykłym tekstem.

Dlatego:

```text
source
  ↓
validate markers
  ↓
translation
  ↓
validate markers
  ↓
merge
```

Backend tłumaczeniowy nie może dowolnie usuwać, przesuwać ani tworzyć markerów.

Jeżeli backend wymaga specjalnego sposobu ochrony markerów, należy rozwiązać to na granicy adaptera/backendu, nie przez usunięcie walidacji.

---

## 42. Biblioteki i technologie — podsumowanie

### Python

```text
Python 3.12+
standard library
lxml >= 5.0
pytest >= 8.0      # testy
ruff >= 0.9        # lint
mypy >= 1.14       # typowanie
```

### Java

```text
JDK / java / javac
Okapi Core 1.49.x
Okapi runtime filters
Jackson
ICU4J
SLF4J
Jericho HTML
Woodstox / StAX
SnakeYAML
Flexmark
Common IO
Common Lang
```

### IPC

```text
JSON Lines
stdin
stdout
stderr
subprocess
```

### Brak

```text
JNI
JPype
Py4J
REST
HTTP
gRPC
Spring
```

---

## 43. Ostateczny model mentalny

Najprościej można myśleć o systemie tak:

```text
              PYTHON
┌───────────────────────────────────┐
│                                   │
│  wybierz filtr                    │
│       ↓                           │
│  otwórz sesję                     │
│       ↓                           │
│  pobierz jednostki                │
│       ↓                           │
│  zweryfikuj                       │
│       ↓                           │
│  przetłumacz                      │
│       ↓                           │
│  zweryfikuj                       │
│       ↓                           │
│  przekaż targety                  │
│                                   │
└────────────────┬──────────────────┘
                 │
                 │ JSON Lines
                 ▼
              JAVA
┌───────────────────────────────────┐
│                                   │
│  uruchom filtr Okapi              │
│       ↓                           │
│  czytaj TextUnit                  │
│       ↓                           │
│  zbuduj target                    │
│       ↓                           │
│  writer Okapi                     │
│       ↓                           │
│  odtwórz dokument                 │
│                                   │
└───────────────────────────────────┘
```

### Jedno zdanie definiujące implementację

> **Pythonowy Filter Engine jest niezależnym orkiestratorem konwersji dokumentów, który wybiera filtr, zarządza jego lifecycle, waliduje jednostki i inline codes oraz prowadzi proces tłumaczenia; izolowany Java Filter Host przez JSON Lines udostępnia minimalny interfejs do istniejących filtrów Okapi i ich writerów, wykorzystując lokalnie spakowany zestaw bibliotek Okapi zamiast całej aplikacji Okapi.**

---

## 44. Źródła implementacyjne w repozytorium

Najważniejsze miejsca do audytu lub odtworzenia:

```text
src/tlumacz/filter_engine/
src/tlumacz/filter_engine/filters/okapi.py
src/tlumacz/resources/filter-host/FilterHost.java
src/tlumacz/resources/filter-host/run.sh
src/tlumacz/resources/okapi-runtime/
java/filter-host/src/main/java/pl/tlumacz/filterhost/FilterHost.java
tests/test_okapi_filter.py
tests/test_okapi_runtime_integration.py
tests/fixtures/fake_okapi_filter_host.py
docs/Plany/PLAN-02-FILTER-ENGINE-2026-10-05.md
```

Dokument należy traktować jako opis aktualnej architektury implementacyjnej, a nie jako instrukcję instalowania całego Okapi jako osobnej aplikacji.


## 13. Etap 3 — separacja implementacji filtrów od wspólnego runtime

Stan po wdrożeniu 2026-10-06:

- implementacje `epub`, `html`, `json`, `markdown`, `openoffice`, `openxml`, `xliff`, `xliff2` i `yaml` znajdują się fizycznie w `filters/<nazwa>/`;
- `okapi-runtime/` nie jest już dodawany jako całość do parent classpath Java Filter Host;
- parent classpath launchera zawiera `okapi-core-1.49.0-SNAPSHOT.jar` oraz wspólne biblioteki z `okapi-runtime/lib`;
- `FilterLoader` nadal ładuje JAR-y konkretnego pakietu przez jego własny `URLClassLoader`;
- zależności wewnętrzne filtrów są obecnie przejściowo wskazywane symlinkami, bez tworzenia fizycznych kopii JAR-ów;

### 13.1. Macierz zależności wewnętrznych

| Filtr | Implementacja | Zależności wewnętrzne pakietu |
|---|---|---|
| EPUB | `runtime-epub-*` | `runtime-archive-*` |
| HTML | `runtime-html-*` | `runtime-abstractmarkup-*` |
| JSON | `runtime-json-*` | `runtime-generated-parser-compat-*` |
| OpenOffice | `runtime-openoffice-*` | brak wykrytej zależności Okapi poza core |
| OpenXML | `runtime-openxml-*` | `runtime-abstractmarkup-*` |
| XLIFF | `runtime-xliff-*` | brak wykrytej zależności Okapi poza core |
| XLIFF2 | `runtime-xliff2-*` | `runtime-xliff-*`, `runtime-lib-xliff2-*` |
| YAML | `runtime-yaml-*` | `runtime-generated-parser-compat-*` |

Wspólne biblioteki zewnętrzne pozostają w `okapi-runtime/lib`, m.in. SLF4J, Jericho HTML, SnakeYAML Engine, StAX2 i Woodstox. `flexmark*` jest wyjątkiem, ponieważ analiza wykazała użycie wyłącznie przez filtr Markdown.

### 13.2. Zależność OpenXML — TwelveMonkeys Common IO

Analiza bytecode filtra OpenXML wykazała referencje do `com.twelvemonkeys.io.ole2.CompoundDocument` i `CorruptDocumentException`. Lokalna inwentaryzacja istniejącego runtime Okapi wykazała zgodny artefakt `common-io-3.12.0.jar`. Został on dołączony do `filters/openxml/`, a `filter.json` deklaruje `com.twelvemonkeys.common:common-io:3.12.0`.

Biblioteka nie jest instalowana globalnie ani pobierana podczas uruchamiania aplikacji. Walidator sprawdza jej obecność bezpośrednio w pakiecie OpenXML oraz potwierdza wymagane klasy JVM. Dzięki temu OpenXML jest obecnie oznaczany jako `usable=True`. Pozostałe zależności wewnętrzne Okapi nadal są przejściowo reprezentowane przez symlinki do wspólnego runtime i pozostają objęte TODO-022j.

### 13.3. Następny etap

TODO-022j pozostaje otwarte: należy zastąpić przejściowe symlinki samowystarczalnymi pakietami filtrów oraz wykonać końcową weryfikację wheel/runtime. Dopiero po tej weryfikacji można usuwać pozostałe implementacje i zależności filtrów z `okapi-runtime`.


### 13.4. Kontekstowy ClassLoader Okapi

Część filtrów Okapi korzysta z `ThreadSafeFilterConfigurationMapper`, który ładuje klasy konfiguracyjne przez `Thread.currentThread().getContextClassLoader()`. Samo odseparowanie JAR-ów od parent classpathu nie wystarczałoby dla takich filtrów.

`FilterLoader` ustawia kontekstowy `ClassLoader` konkretnego pakietu podczas konstrukcji filtra. `FilterHost` aktywuje ten sam loader na czas operacji `open`, `next`, `apply`, `close`, `cancel` oraz legacy `extract`, `merge`, `probe` i `capabilities`. Po operacji poprzedni kontekst wątku jest przywracany.

Dzięki temu implementacja filtra i jego dynamicznie konfigurowane zależności pozostają poza globalnym parent classpathem, a rzeczywiste round-trip EPUB/OpenXML pozostaje zgodne z wcześniejszym zachowaniem.


### 13.5. Walidacja zależności pakietu filtra

Każdy pakiet filtra może deklarować pole dependencies w filter.json. Pojedyncza deklaracja może zawierać nazwę zależności, artifact, wymagane pliki JAR, wymagane klasy JVM oraz odnośniki do źródeł.

Walidator sprawdza zależności w obrębie konkretnego katalogu filters/<nazwa>/ i nie instaluje brakujących bibliotek. Wynik walidacji ma status usable. Pakiet z niespełnioną zależnością jest raportowany jako nieużytkowy.

Warstwa QML uruchamia walidację przy starcie oraz obserwuje magazyn filtrów przez QFileSystemWatcher. Dodanie nowego pakietu lub zmiana jego zawartości powoduje ponowną walidację. Brak zależności jest:
- dopisywany do Logu GUI;
- przekazywany do modalnego komunikatu;
- prezentowany wraz z wymaganymi klasami/JAR-ami;
- uzupełniany o klikalne odnośniki, jeżeli zostały zapisane w deskryptorze.

OpenXML deklaruje obecnie wymaganie TwelveMonkeys Common IO dla klas OLE2. Pakiet zawiera `common-io-3.12.0.jar`, więc walidator potwierdza `usable=True`. Brak tej biblioteki w przyszłej instalacji lub migracji ponownie spowoduje `usable=False`; mechanizm nadal nie pobiera zależności automatycznie.


### 13.6. Rzeczywisty stan magazynu `filters/`

Po zakończeniu etapów lazy-load i dynamicznego Java `FilterLoader` implementacje aktywnych filtrów są fizycznie umieszczone w `filters/<nazwa>/`: `epub`, `html`, `json`, `markdown`, `openoffice`, `openxml`, `xliff`, `xliff2` i `yaml`. Każdy pakiet ma własny `filter.json` z `name` i `entry_class`.

Nie należy utożsamiać tej separacji z pełną migracją całego classpathu. Część zależności nadal pozostaje symlinkami do `src/tlumacz/resources/okapi-runtime`; jest to świadomie stan przejściowy. Fizycznie do pakietów filtrów przeniesiono zależności specyficzne, które zostały zweryfikowane jako należące do danego filtra, w tym zestaw `flexmark*` dla Markdown. OpenXML posiada fizycznie `common-io-3.12.0.jar` oraz deklarację TwelveMonkeys Common IO w descriptorze.

`FilterLoader` ładuje JAR-y konkretnego pakietu przez izolowany `URLClassLoader`, a `FilterHost` aktywuje jego `ClassLoader` jako kontekstowy classloader w operacjach wymagających dynamicznego ładowania konfiguracji Okapi. Parent classpath nie zawiera już całego `okapi-runtime/*` jako implementacji filtrów.

Końcowa zamiana przejściowych symlinków na samowystarczalne pakiety oraz usunięcie zbędnych implementacji/zależności z `okapi-runtime` pozostaje objęte TODO-022j i wymaga osobnej weryfikacji packagingu.


## 2026-10-06 — zamknięcie TODO-022j

Pakiety filtrów w `filters/<nazwa>/` są samowystarczalne względem wcześniej przejściowych zależności wewnętrznych: wszystkie symlinki JAR zostały zastąpione fizycznymi plikami, a `runtime-abstractmarkup`, `runtime-archive`, `runtime-generated-parser-compat`, `runtime-lib-xliff2`, `common-io` i `common-lang` zostały usunięte ze wspólnego `okapi-runtime` i umieszczone przy właściwych konsumentach. `common-io` i `common-lang` znajdują się w `filters/openxml/`, ponieważ analiza `jdeps` potwierdziła ich użycie przez OpenXML/TwelveMonkeys.

Wspólny runtime nie zawiera implementacji filtrów ani wskazanych zależności filtr-specyficznych. Testy architektury wymagają braku symlinków JAR w pakietach oraz braku tych zależności w runtime. TODO-022j uznaje się za zamknięte po przejściu tych testów.

## 2026-10-07 — nadrzędny kontrakt magazynu filtrów

Niniejszy dokument zawiera również historyczne opisy poprzednich etapów migracji. Obowiązujący kontrakt kodu jest prostszy: trwałym magazynem jest `/home/frs/.config/tlumacz/filters`, a `.tplugin` jest rozpakowywany wyłącznie do `/tmp/filters/`. Nie należy ponownie wprowadzać `$HOME/.config/tlumacz/filter-engine/plugins` ani `shared-libs` jako drugiego magazynu.

Wspólne biblioteki znajdują się w `src/tlumacz/resources/okapi-runtime/lib/`. XLIFF 2.0 jest wewnętrzną warstwą dokumentową w `src/tlumacz/documents/xliff.py`, a nie wejściowym filtrem rejestru.
