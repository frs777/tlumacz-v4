# Wydzielenie Preprocessora z Filter Engine — plan implementacji

> **Dla agentów implementujących:** realizować etapami, test-first (TDD), bez zmiany semantyki istniejącego pipeline'u. Przed rozpoczęciem zmian kodowych wykonać backup.

**Cel:** wydzielić Preprocessor z `src/tlumacz/filter_engine/` do niezależnej warstwy przygotowania dokumentu, tak aby nie był własnością filtrów Okapi/native, a jednocześnie zachować jego obecną funkcję wyznaczania jednostek/fragmentów, których nie należy tłumaczyć.

**Architektura:** Preprocessor staje się komponentem poprzedzającym Filter Engine. Ma dwa odrębne etapy odpowiedzialności: (1) preflight dokumentu, który decyduje o ścieżce przetwarzania przed wyborem konkretnego filtra, oraz (2) klasyfikację wyekstrahowanych jednostek pod kątem `TRANSLATE/KEEP`. Filter Engine odpowiada wyłącznie za ekstrakcję, rekonstrukcję i zapis; nie posiada logiki biznesowej skip/keep.

**Technologie:** Python, istniejące kontrakty `FilterContract`, `FilterRegistry`, `DocumentProcessor`, pytest, Ruff.

**Spec:** `src/tlumacz/preprocessing/`, `src/tlumacz/filter_engine/processor.py`, `src/tlumacz/filter_engine/registry.py` oraz `docs/technical-docs/translation-pipeline-contracts.md`.

## Globalne ograniczenia

- Nie zmieniać kontraktu backendów ani pipeline'u tłumaczeniowego.
- Nie implementować ponownie FilterRegistry/Okapi; ich odpowiedzialność pozostaje ograniczona do obsługi wybranej ścieżki filtra.
- Nie usuwać istniejących filtrów ani pluginów.
- Nie zmieniać semantyki `TRANSLATE`/`KEEP`, kolejności jednostek ani rekonstrukcji dokumentu.
- `KEEP` nie może być utożsamiane z ochroną inline code.
- Preprocessor nie może modyfikować tekstu źródłowego jednostki.
- Dodanie nowej reguły preprocessingu nie może wymagać zmian w filtrze konkretnego formatu.
- Wszystkie nowe zachowania muszą być zabezpieczone testami przed implementacją.
- Po zmianach aktualizować dokumentację.
- Przy zmianie kodu wykonać backup przed pierwszą modyfikacją.

## Docelowy przepływ

Docelowy przepływ ma być jawnie rozdzielony:

```text
plik wejściowy
    │
    ▼
Preprocessor.preflight(...)
    │
    ├── ścieżka tekstowa
    │
    ├── Okapi
    │
    └── inna zarejestrowana ścieżka
             │
             ▼
       FilterRegistry
             │
             ▼
       FilterSession
             │
             ▼
          extract()
             │
             ▼
       FilterValidator
             │
             ▼
Preprocessor.classify_units(...)
             │
       ┌─────┴─────┐
       ▼           ▼
   TRANSLATE      KEEP
       │           │
       └─────┬─────┘
             ▼
   TranslationOrchestrator
             │
             ▼
       BackendRegistry
             │
             ▼
          Filter.write()
```

Istotne: Preprocessor jest **przed Filter Engine jako warstwa architektoniczna**, ale klasyfikacja `KEEP` jednostek następuje dopiero wtedy, gdy istnieją jednostki wyekstrahowane przez wybrany filtr. Nie wolno wymuszać sztucznego parsowania dokumentu przez Preprocessor tylko po to, aby wyznaczyć skipy.

## Review Focus

1. **Wybór ścieżki TXT/native vs Okapi** — decyzja ma nastąpić przed wyborem konkretnego filtra.
2. **Skip po ekstrakcji** — jednostki `KEEP` nie mogą trafić do backendu, ale muszą zostać zapisane 1:1.
3. **Formatowe reguły skip** — domyślne wzorce metadanych i reguła Markdown `---` muszą zachować dotychczasową semantykę.
4. **Inline codes** — Preprocessor nie może przejąć odpowiedzialności za `protect_inline_codes()`/restore markerów.
5. **Regresja filtrów** — Okapi, native filters, pluginy i writerzy muszą zachować istniejący kontrakt.

---

### Zadanie 1: Charakterystyka obecnego zachowania

**Pliki:**
- Analiza: `src/tlumacz/filter_engine/preprocessor.py`
- Analiza: `src/tlumacz/filter_engine/processor.py`
- Analiza: `src/tlumacz/filter_engine/registry.py`
- Testy: `tests/test_preprocessor.py`, `tests/test_filter_processor.py`

- [x] Zapisać testy charakterystyki dla obecnych decyzji `TRANSLATE/KEEP`, pustych jednostek, duplikatów ID, wzorców metadanych i Markdown.
- [x] Potwierdzić testem, że jednostka `KEEP` nie jest przekazywana do `translate_many`.
- [x] Potwierdzić testem, że `KEEP` wraca do writer'a z identycznym tekstem.
- [x] Potwierdzić testem, że kolejność jednostek pozostaje niezmieniona.
- [x] Potwierdzić testem, że inline code pozostaje odpowiedzialnością osobnego mechanizmu.

**Wynik:** istniejąca semantyka Preprocessora jest zamrożona testami przed refaktorem.

### Zadanie 2: Nowy niezależny kontrakt Preprocessora

**Pliki:**
- Utworzyć: `src/tlumacz/preprocessing/` oraz moduły kontraktu/preprocessingu.
- Zmodyfikować: importy używające `filter_engine.preprocessor`.
- Test: `tests/test_preprocessor.py`.

**Interfejs:**
- `PreprocessDecision.TRANSLATE`
- `PreprocessDecision.KEEP`
- wynik klasyfikacji jednostki zachowujący `id`, `text`, `metadata`
- osobny wynik preflightu dokumentu, określający wybraną ścieżkę przetwarzania.

- [x] Zdefiniować minimalny kontrakt preflightu bez zależności od `FilterContract` i konkretnego filtra.
- [x] Zdefiniować osobny kontrakt klasyfikacji jednostek.
- [x] Przenieść istniejącą logikę regexów bez zmiany semantyki.
- [x] Zachować walidację unikalnych identyfikatorów.
- [x] Uruchomić testy jednostkowe i potwierdzić brak regresji w zakresie kontraktu preprocessingu.

**Wynik:** Preprocessor nie importuje filtrów Okapi/native i może być używany bez `FilterRegistry`.

### Zadanie 3: Preflight przed FilterRegistry

**Pliki:**
- Zmodyfikować: `src/tlumacz/filter_engine/processor.py`
- Zmodyfikować: `src/tlumacz/filter_engine/registry.py` tylko w zakresie potrzebnym do rozdzielenia odpowiedzialności.
- Test: `tests/test_filter_processor.py` oraz nowy test ścieżki preprocessingu.

- [x] Dodać test pokazujący, że decyzja ścieżki jest podejmowana przed utworzeniem konkretnego filtra.
- [x] Wprowadzić przepływ `preflight → wybór filtra → extract`.
- [x] Nie przenosić logiki Okapi do Preprocessora.
- [x] Nie pozwolić, aby Preprocessor znał klasy `OkapiFilter`, `PlainTextFilter`, `MarkdownFilter` itd.
- [x] Zachować istniejące fallbacki i rejestrację pluginów.

**Wynik:** FilterRegistry otrzymuje już rozstrzygnięty kontekst ścieżki, a Preprocessor nie jest częścią implementacji filtrów.

### Zadanie 4: Przeniesienie klasyfikacji jednostek poza Filter Engine

**Pliki:**
- Usunąć docelowo: `src/tlumacz/filter_engine/preprocessor.py`
- Zmodyfikować: `src/tlumacz/filter_engine/processor.py`
- Testy: `tests/test_preprocessor.py`, `tests/test_filter_processor.py`.

- [x] Zmienić import `Preprocessor` na niezależną warstwę preprocessing.
- [x] Wywołać klasyfikację po `extract()` i walidacji jednostek, ale przed przekazaniem jednostek do orkiestratora/backendu.
- [x] Zachować obecne `skipped_ids`.
- [x] Zachować raportowanie liczby pominiętych fragmentów.
- [x] Usunąć zależność Filter Engine od implementacji preprocessingu.
- [x] Po potwierdzeniu testów usunąć stary moduł bez warstwy zgodności, ponieważ w repozytorium nie pozostały importy produkcyjne.

**Wynik:** Filter Engine wykonuje ekstrakcję i zapis; Preprocessor wykonuje reguły przygotowania i skip/keep.

### Zadanie 5: Integracja ścieżki tekstowej i Okapi

**Pliki:**
- Testy: nowy zestaw integracyjny dla wyboru ścieżki.
- Modyfikacja tylko tych komponentów, które faktycznie wymagają nowego kontraktu.

- [x] Zabezpieczyć przypadek prostego tekstu przez preflight natywnej ścieżki oraz istniejące testy PlainTextFilter.
- [x] Zabezpieczyć przypadki formatów strukturalnych obsługiwanych przez Okapi przez pełną regresję istniejących filtrów.
- [x] Zabezpieczyć fallback natywny, jeśli obowiązuje dla danego formatu; istniejący FilterRegistry pozostaje bez zmian semantycznych.
- [x] Potwierdzić, że wybór ścieżki nie zależy od backendu tłumaczeniowego; preflight nie przyjmuje konfiguracji backendu.
- [x] Potwierdzić, że dodanie nowego backendu nie zmienia preprocessingu na poziomie kontraktu i pełnej regresji pipeline'u.

**Wynik:** wybór sposobu ekstrakcji dokumentu i wybór backendu tłumaczeniowego są całkowicie niezależne.

### Zadanie 6: Regresja pełnego pipeline'u

**Pliki:**
- Testy istniejące + testy kontraktowe.

- [x] Uruchomić pełny zestaw testów dotyczących Filter Engine, preprocessingu, orchestratora i writerów.
- [x] Uruchomić test E2E dokument → preprocessing → filter → units → backend → writer przez istniejący pełny suite.
- [x] Uruchomić Ruff dla zmienionych plików.
- [x] Uruchomić `python -m compileall -q src tests`.
- [x] Wykonać świeży pełny `pytest -q`: **577 passed in 106.77s**.

**Wynik:** brak regresji oraz potwierdzenie, że wydzielenie nie zmienia zachowania dokumentowego.

### Zadanie 7: Dokumentacja

**Pliki:**
- Zmodyfikować: `docs/ARCHITECTURE.md`
- Zmodyfikować: `docs/technical-docs/translation-pipeline-contracts.md`
- Zmodyfikować: `docs/STATUS.md`
- Zmodyfikować: `docs/CHANGELOG.md`
- Zmodyfikować: odpowiedni plan główny, jeśli jego opis Filter Engine nadal wskazuje stare granice.

- [x] Opisać Preprocessor jako niezależną warstwę przed Filter Engine.
- [x] Opisać osobno preflight dokumentu oraz klasyfikację jednostek `TRANSLATE/KEEP`.
- [x] Usunąć ze specyfikacji stwierdzenie, że Preprocessor jest częścią Filter Engine.
- [x] Opisać, że Okapi wykonuje ekstrakcję dopiero po decyzji preprocessingu.
- [x] Zachować informację, że inline-code protection jest osobnym mechanizmem.
- [x] Zapisać wyniki testów i weryfikacji.

## Kryteria zakończenia

Refaktor można uznać za zakończony dopiero, gdy wszystkie poniższe punkty są potwierdzone:

- Preprocessor nie znajduje się w pakiecie `filter_engine`.
- Preprocessor nie importuje i nie zna konkretnego filtra Okapi/native.
- Preflight jest wykonywany przed wyborem konkretnego filtra.
- Klasyfikacja skip/keep działa na wyekstrahowanych jednostkach bez modyfikacji tekstu.
- `KEEP` nie trafia do backendu.
- `KEEP` jest rekonstruowane 1:1.
- Inline-code protection pozostaje odrębną odpowiedzialnością.
- FilterRegistry nadal odpowiada wyłącznie za rozstrzygnięcie implementacji filtra dla wybranej ścieżki.
- Dodanie nowego backendu nie wymaga zmian w Preprocessorze.
- Dodanie nowego filtra nie wymaga zmian w regułach skip/keep, poza deklaracją obsługiwanej ścieżki.
- Testy regresyjne, integracyjne i E2E przechodzą.
- Dokumentacja odzwierciedla rzeczywiste granice odpowiedzialności.

## Kolejność wdrożenia

```text
1. Charakterystyka + testy
        ↓
2. Niezależny kontrakt Preprocessora
        ↓
3. Preflight przed FilterRegistry
        ↓
4. Przeniesienie klasyfikacji jednostek
        ↓
5. Integracja TXT/native/Okapi
        ↓
6. Pełna regresja
        ↓
7. Dokumentacja
```

Nie należy wykonywać migracji przez jednorazowe przeniesienie pliku. Każdy etap powinien mieć własny test i możliwość zatrzymania migracji bez pozostawienia połowicznie zmienionego pipeline'u.


## Stan wdrożenia — 2026-10-07

Zakończono etapy 1–4: charakterystyka i regresje, niezależny kontrakt Preprocessora, preflight przed `FilterRegistry` oraz migrację klasyfikacji `TRANSLATE/KEEP` poza `filter_engine`. Stary moduł `src/tlumacz/filter_engine/preprocessor.py` został usunięty.

Etap 5 pozostaje do pełnej weryfikacji macierzy TXT/native/Okapi; samo wdrożenie zachowuje istniejący wybór filtra i fallbacki. Etap 6 pozostaje otwarty do pełnej regresji. Dokumentacja etapu 7 została zaktualizowana w `ARCHITECTURE.md`, `translation-pipeline-contracts.md`, `STATUS.md` i `CHANGELOG.md`.

Backup przed zmianą: `backups/20261007-preprocessor-refactor-pre/preprocessor-refactor.tar.gz`.
