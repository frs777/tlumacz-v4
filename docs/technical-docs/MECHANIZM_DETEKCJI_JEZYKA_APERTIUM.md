# Mechanizm detekcji języka i obsługi Apertium

**Status:** kanoniczna notatka architektoniczna / kontrakt do dalszych zmian  
**Projekt:** Tłumacz  
**Data:** 2026-10-06

## 1. Cel dokumentu

Ten dokument opisuje mechanizm detekcji języka oraz szczególny sposób wykorzystania go przez Apertium.

Jest to dokument referencyjny dla przyszłych zmian kodu. Przed modyfikowaniem `LanguageDetector`, pipeline'u tłumaczenia albo obsługi Apertium należy sprawdzić ten kontrakt.

---

## 2. Dwa niezależne mechanizmy detekcji

Projekt posiada wspólny prymityw detekcji `LanguageDetector` oparty na Lingua, ale **mechanizm routingu języka jest rozdzielony na dwie niezależne ścieżki**.

### 2.1. Mechanizm Apertium

`ApertiumLanguageRouting` realizuje osobny kontrakt:
- najpierw ustala język dokumentu,
- zamraża `source`,
- para `source → target` pozostaje stała,
- detekcja chunkowa służy wyłącznie do decyzji `tłumacz/pomiń`.

### 2.2. Mechanizm pozostałych backendów

`DynamicLanguageRouting` realizuje osobny kontrakt:
- detekcja odbywa się niezależnie dla każdego chunka,
- wykryty `source` jest przekazywany do bieżącego żądania,
- `source` może zmienić się pomiędzy chunkami,
- umożliwia tłumaczenie dokumentów wielojęzycznych.

Nie należy traktować tych ścieżek jako jednego mechanizmu z wyjątkiem dla Apertium. Są to **dwa odrębne kontrakty routingu języka**, korzystające ze wspólnego detektora.

---

## 3. Mechanizm pozostałych backendów

Dla backendów innych niż Apertium obowiązuje dynamiczna detekcja per chunk:

```text
chunk
  ↓
detekcja języka chunku
  ↓
ustalenie source dla tego żądania
  ↓
tłumaczenie
```

Przykład dokumentu:

```text
English
German
Spanish
English
```

może skutkować:

```text
English → source=en → tłumacz
German  → source=de → tłumacz
Spanish → source=es → tłumacz
English → source=en → tłumacz
```

Nie wolno wprowadzać globalnego, jednorazowego `source_language` dla tych backendów tylko dlatego, że Apertium wymaga zamrożenia pary.

## 4. Szczególna zasada Apertium

Apertium działa na podstawie konkretnej pary językowej.

Dla jednego tłumaczenia dokumentu para Apertium musi zostać ustalona przed rozpoczęciem właściwego tłumaczenia i pozostaje stała:

```text
source_language → target_language
```

Przykład:

```text
eng → pol
```

czyli para:

```text
eng-pol
```

### Kluczowa zasada

**Detekcja języka może być wykonywana dla każdego chunka, ale wynik detekcji chunku nie może zmieniać ustalonej pary Apertium.**

Detekcja chunkowa służy wyłącznie do decyzji:

```text
czy ten fragment należy do ustalonego source_language?
```

Jeżeli tak:

```text
TŁUMACZ
```

Jeżeli nie:

```text
POMIŃ
```

---

## 5. Docelowy przepływ Apertium

```text
ZAŁADOWANIE DOKUMENTU
        │
        ▼
wstępna detekcja języka dokumentu
        │
        ▼
ustalenie source_language
        │
        ▼
sprawdzenie dostępnych par Apertium
        │
        ▼
wybór target_language
        │
        ▼
USTALENIE I ZAMROŻENIE PARY
source → target
        │
        ▼
─────────────────────────────────
     przetwarzanie chunków
─────────────────────────────────
        │
        ▼
detekcja języka aktualnego chunku
        │
        ├── chunk == source
        │       │
        │       ▼
        │    tłumacz ustaloną parą
        │
        └── chunk != source
                │
                ▼
             POMIŃ
```

### Przykład

Dokument:

```text
English paragraph 1
English paragraph 2
German paragraph
Spanish paragraph
English paragraph 3
```

Wstępna detekcja ustala:

```text
source = en
target = pl
pair   = eng-pol
```

Następnie:

```text
English paragraph 1 → TŁUMACZ
English paragraph 2 → TŁUMACZ
German paragraph    → POMIŃ
Spanish paragraph   → POMIŃ
English paragraph 3 → TŁUMACZ
```

Nigdy nie wykonujemy:

```text
German → zmiana pary Apertium
Spanish → zmiana pary Apertium
```

---

## 6. Dlaczego potrzebna jest detekcja wstępna

Wstępna detekcja przy ładowaniu dokumentu jest potrzebna Apertium do ustalenia, jaka para językowa ma być używana.

Apertium nie powinno dowiadywać się o nowej parze językowej podczas przetwarzania kolejnych chunków.

W szczególności nie należy dopuścić do:

```text
chunk 1 → en → eng-pol
chunk 2 → de → de-pol
chunk 3 → es → es-pol
```

To oznaczałoby zmianę zarówno języka wejściowego, jak i potencjalnie języka wyjściowego w ramach jednego tłumaczenia.

---

## 7. Mapowanie kodów językowych

Wspólny detektor może zwracać kody ISO 639-1, np.:

```text
en
pl
es
de
```

Apertium może natomiast identyfikować pary własnymi kodami, np.:

```text
eng-pol
eng-spa
spa-eng
```

Dlatego warstwa Apertium musi posiadać jawne mapowanie:

```text
wynik LanguageDetector
        ↓
znormalizowany kod języka
        ↓
kod języka Apertium
        ↓
sprawdzenie dostępnych par
```

Nie należy mieszać kodu ISO zwracanego przez detektor z identyfikatorem pary Apertium.

---

## 8. Różnica między wyborem pary a detekcją chunku

To są dwie odrębne decyzje.

### Decyzja dokumentowa — raz

```text
Jaki język źródłowy ma dokument?
Jaka para Apertium jest dostępna?
Jaki target wybiera użytkownik?
```

Wynik:

```text
source = en
target = pl
pair = eng-pol
```

### Decyzja chunkowa — dla każdego fragmentu

```text
Czy aktualny chunk jest w języku en?
```

Wynik:

```text
tak  → tłumacz
nie → pomiń
```

Detekcja chunkowa **nie może nadpisywać**:

```text
source_language
target_language
apertium_pair
```

---

## 9. Zachowanie dokumentów wielojęzycznych

Dokument wielojęzyczny nie jest dla Apertium powodem do zmiany pary.

Języki inne niż ustalony język źródłowy są traktowane jako fragmenty nieprzeznaczone do tłumaczenia przez aktualną operację.

Preferowane zachowanie:

```text
source chunk → przetłumacz
other-language chunk → pozostaw bez zmian
```

Nie należy:
- automatycznie szukać nowej pary dla każdego chunku,
- zmieniać targetu,
- tworzyć kilku niezależnych operacji Apertium bez jawnej decyzji użytkownika.

---

## 10. Relacja z LibreTranslate i innymi backendami

LibreTranslate oraz inne backendy dynamiczne korzystają z `DynamicLanguageRouting` i mogą zmieniać `source` pomiędzy chunkami.

Apertium korzysta z `ApertiumLanguageRouting` i nie może zmieniać zamrożonej pary.

Schemat:

```text
                    LanguageDetector
                           │
              ┌────────────┴────────────┐
              │                         │
       DynamicLanguageRouting     ApertiumLanguageRouting
              │                         │
       detekcja per chunk       detekcja dokumentu
              │                         │
       source może się           source/target
         zmieniać                 zamrożone
              │                         │
          tłumacz              detekcja chunku
                                        │
                                ┌───────┴───────┐
                              zgodny          inny
                                │               │
                             tłumacz          pomiń
```

Rozdzielenie zachowuje obsługę dokumentów wielojęzycznych dla backendów dynamicznych bez naruszania wymogu stałej pary Apertium.

---

## 11. Kontrakt implementacyjny

Obowiązują dwa niezależne kontrakty:

### A. Apertium

1. `ApertiumLanguageRouting` ustala `source` na poziomie dokumentu.
2. Para `source → target` jest zamrożona na czas całej operacji.
3. Detekcja per chunk służy wyłącznie do decyzji `tłumacz/pomiń`.
4. Chunk w innym języku pozostaje bez zmian.
5. Wynik detekcji chunku nie może zmienić `source`, `target` ani pary Apertium.

### B. Pozostałe backendy

1. `DynamicLanguageRouting` wykonuje detekcję niezależnie dla każdego chunka.
2. Wykryty `source` jest przekazywany do konkretnego żądania backendu.
3. `source` może zmieniać się pomiędzy chunkami.
4. Dokument wielojęzyczny może zawierać wiele źródeł tłumaczonych w jednej operacji.

### Wspólny kontrakt infrastrukturalny

1. `LanguageDetector` pozostaje wspólnym prymitywem detekcji.
2. Cache tłumaczeń musi uwzględniać `source_language`, ponieważ ten sam tekst może wymagać różnych tłumaczeń dla różnych źródeł.
3. Adapter backendu nie powinien wykonywać drugiej, niezależnej detekcji, jeśli `source` został już ustalony przez właściwy routing.

---

## 12. Stan implementacji

Na dzień 2026-10-06 rozdzielenie zostało wdrożone w warstwie aplikacyjnej:

- `ApertiumLanguageRouting` — osobna ścieżka dokument → zamrożony source → decyzja chunk `tłumacz/pomiń`.
- `DynamicLanguageRouting` — osobna ścieżka dynamiczna per chunk.
- `TranslationOrchestrator` przekazuje wykryty `source` do konkretnego żądania.
- chunk pominięty przez ścieżkę Apertium pozostaje bez zmian.
- cache uwzględnia `source_language`.
- adapter TranslateGemma korzysta z języka przekazanego przez routing zamiast wykonywać własną detekcję.

Pozostaje zachować istniejący kontrakt GUI Apertium dotyczący wyboru dostępnej pary `source → target`; routing nie może samoczynnie zmieniać tej pary podczas przetwarzania dokumentu.



- `STATUS.md` — bieżący stan projektu.
- `CHANGELOG.md` — historia zmian.
- `TODO.md` — aktywne zadania.
- dokumentacja Apertium / V4 Filter Engine — szczegóły integracji Apertium.
- `tlumacz/language_detector.py` — implementacja wspólnego detektora.
- pipeline tłumaczenia — miejsce wykorzystania wyniku detekcji.

**Zasada:** przed zmianą mechanizmu detekcji lub obsługi języka Apertium najpierw porównać implementację z niniejszym dokumentem.


## 13. Detekcja GUI Apertium — Lingua

GUI Apertium używa tego samego LanguageDetector, którego implementacja opiera się na bibliotece **Lingua**. Nie używa LibreTranslate do wstępnej detekcji języka dokumentu.

W trybie automatycznym:
- source_language pozostaje auto,
- Lingua zapisuje wykryty język wyłącznie jako detectedSourceLanguage,
- wykryty język służy do wyznaczenia dostępnych targetów Apertium,
- wykryty język nie jest zapisywany jako nowy source_language,
- dzięki temu kolejny dokument jest ponownie wykrywany od początku.

Ważne: wcześniejsza implementacja nadpisywała source_language wynikiem detekcji, a następnie zapisywała ten wynik w ustawieniach. Powodowało to sytuację, w której np. spa pozostawało źródłem i kolejny dokument angielski nie był ponownie wykrywany. Ten stan został usunięty.

Dla dokumentu:

English
French
German

oczekiwany stan GUI to:

source_language = auto
detectedSourceLanguage = en
target = pl

a podczas tłumaczenia routing Apertium ponownie ustala source dokumentu i zamraża go jako en. Chunky fr i de są następnie pomijane.
