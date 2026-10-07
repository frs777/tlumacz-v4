---
id: translation-pipeline-contracts
status: active
meta:
  contentType: Reference
  category: technical
version: 1.0.0
updated: 2026-10-07
owner: technical-documentation
source: src/tlumacz/application/, src/tlumacz/filter_engine/, src/tlumacz/backends/llama_cpp/
depends_on: [docs/ARCHITECTURE.md, docs/STATUS.md, docs/Plany/PLAN-12-TRANSLATEGEMMA-CHUNKOWANIE-JEZYKI-SKIP-2026-10-07.md]
expires_when: zmiana kontraktu TranslationOrchestrator/Filter Engine/llama.cpp
last_validation: "inspekcja kodu SentinelX 2026-10-07"
---

# Kontrakty pipeline tłumaczenia — Tłumacz V4

Ten dokument opisuje wyłącznie kontrakty potwierdzone w aktualnym kodzie. Nie zastępuje dokumentacji historycznej ani nie deklaruje obsługi funkcji, których nie potwierdza implementacja.

## 1. Kolejność pipeline'u

```text
plik wejściowy
→ Preprocessor.preflight()
→ FilterRegistry.for_path()
→ sesja FilterLifecycle
→ extract()
→ walidacja jednostek
→ skip przed backendem
→ TranslationOrchestrator
→ ChunkPlanner
→ cache / batch backend
→ ResultValidator
→ rekonstrukcja przez filtr
```

Sesja filtra jest zamykana deterministycznie przez `FilterSessionContext`. `TranslationApp.close()` zamyka runtime llama.cpp oraz `TranslationCache`.

## 2. Preflight i klasyfikacja jednostek

`Preprocessor` jest niezależną warstwą `src/tlumacz/preprocessing/`. Nie importuje `FilterContract`, `FilterRegistry` ani konkretnego filtra. `preflight()` rozróżnia wysokopoziomową ścieżkę natywnego tekstu od ścieżki Filter Engine, a następnie `DocumentProcessor` dopiero rozwiązuje konkretny filtr przez `FilterRegistry`.

Po `extract()` i walidacji jednostek ten sam komponent wykonuje `classify_units()`. Klasyfikacja nie modyfikuje tekstu źródłowego. `KEEP` jest rekonstruowane 1:1 i nie trafia do backendu; `TRANSLATE` może zostać przekazane do planowania transportu. Ochrona inline-code pozostaje osobnym mechanizmem.

## 3. Skip przed backendem

`DocumentProcessor.process()` najpierw ekstraktuje i waliduje jednostki, następnie oblicza `skipped_ids` na podstawie pustego tekstu i skonfigurowanych wzorców. Jednostki pominięte nie są przekazywane do `translate_many`.

Przy ścieżce batchowej pominięta jednostka jest rekonstruowana 1:1 z tekstu źródłowego. Marker validation jest wykonywany zarówno przed, jak i po obsłudze jednostki.

Filtr Markdown może dodatkowo raportować `session.skipped_fragments`; te fragmenty pozostają poza tłumaczeniem i są zachowywane przy zapisie.

## 4. Chunk → batch → request

`TranslationOrchestrator` tworzy logiczne chunki przez `ChunkPlanner`. Dla backendu wyposażonego w `translate_batch` cały nieobsłużony logiczny chunk jest przekazywany do `TranslationExecutor.execute_batch()`.

Dla TranslateGemma obowiązuje:

- jeden batch = jeden logiczny chunk;
- jeden batch zawiera jeden kod języka źródłowego;
- `LlamaCppAdapter.translate_batch()` buduje jeden request `/completions` z markerami `⟦TG_SEG_N⟧`;
- odpowiedź musi zawierać wszystkie markery dokładnie raz i w tej samej kolejności;
- niepoprawny pierwszy batch jest ponawiany jako cały chunk jeden raz;
- po dwóch nieudanych próbach następuje kontrolowany fallback jednostkowy;
- brakujący lub dodatkowy identyfikator jednostki powoduje błąd zamiast częściowego sukcesu.

To oznacza, że `chunk_size` jest limitem planera w znakach, a nie bezpośrednim ustawieniem liczby requestów ani dokładnym limitem tokenów modelu.

## 5. Kody językowe TranslateGemma

Dla aktywnego trybu `translategemma` adapter wymaga kodu źródłowego i docelowego możliwego do rozpoznania przez `language_code_for()`. `auto` nie może trafić do requestu TranslateGemma.

`LlamaCppLanguageRouting.resolve_document_source()` dla `source_language=auto` detekuje język na podstawie całego dokumentu, po usunięciu fragmentów w podwójnych cudzysłowach. Wynik jest zamrażany dla jednostek dokumentu w bieżącym `TranslationOrchestrator`.

## 6. Ochrona inline codes

Przed granicą backendu `protect_inline_codes()` zamienia reprezentację PUA Okapi na markery ASCII `__OKAPI_CODE_N__`. Po odpowiedzi `restore_inline_codes()` wymaga zgodności liczby, tożsamości i kolejności markerów. Dopiero przywrócony wynik jest walidowany i zapisywany do cache.

## 7. Aktywne formaty i magazyn pluginów

Produkcyjny `FilterRegistry` korzysta z jednego trwałego magazynu pakietów `$HOME/.config/tlumacz/filters` (lub `TLUMACZ_FILTER_STORE`). Pakiety `.tplugin` są na żądanie rozpakowywane do izolowanego katalogu `/tmp/filters/` i dopiero stamtąd odkrywane przez `plugin.json`. Nie istnieje trwały katalog `filter-engine/plugins`.

Aktywne pakiety wejściowych filtrów Okapi: EPUB, JSON, OpenOffice, OpenXML i YAML. HTML oraz Markdown mają ścieżki natywne; XLIFF nie jest formatem wejściowym FilterRegistry. Wspólne JAR-y Okapi znajdują się wyłącznie w `src/tlumacz/resources/okapi-runtime/lib/`.

`src/tlumacz/documents/xliff.py` zawiera wewnętrzną obsługę XLIFF 2.0. Nie jest ona rejestrowana jako filtr wejściowy.

## 8. Lifecycle cache i Filter Host

`TranslationCache` używa SQLite, posiada jawne `close()` i jest zamykany przez `TranslationApp.close()`.

`FilterHostClient` uruchamia niedemoniczne czytniki stdout/stderr. `close()` kończy proces potomny, zamyka strumienie i wykonuje join czytników. Nie należy przywracać `daemon=True`.

## 9. Nested fields / complex fields — aktualna luka kontraktowa

Aktualny V4 nie posiada w domenowym kontrakcie `FilterContract` osobnego, formalnego pola lub typu opisującego `nested fields` ani `complex fields`. Kod filtrów operuje na jednostkach i metadanych zależnych od formatu; nie istnieje wspólny invariant definiujący semantykę zagnieżdżonych pól.

W konsekwencji dokumentacja nie deklaruje obecnie jednolitego kontraktu dla:

- zagnieżdżonych pól dokumentu;
- pól wielowarstwowych lub wielowartościowych;
- zachowania kolejności i własności dzieci względem pola nadrzędnego;
- mapowania takich struktur przez wszystkie aktywne filtry.

Jest to **jawna luka dokumentacyjno-kontraktowa**, a nie potwierdzenie braku obsługi w każdym konkretnym filtrze. Przed utworzeniem takiego kontraktu wymagany jest osobny zakres testów per format oraz decyzja architektoniczna.


## 2026-10-07 — wspólna warstwa Preprocessor dla skip/keep

DocumentProcessor korzysta z niezależnego `tlumacz.preprocessing.Preprocessor`. Preflight dokumentu jest wykonywany przed `FilterRegistry.for_path()`, a klasyfikacja jednostek `TRANSLATE/KEEP` po ekstrakcji i walidacji, przed przekazaniem danych do TranslationOrchestrator/ChunkPlanner.

Kontrakt:
- PreprocessDecision.TRANSLATE — jednostka może wejść do planowania i backendu;
- PreprocessDecision.KEEP — jednostka nie jest przekazywana do translate ani translate_many;
- tekst KEEP pozostaje identyczny ze źródłem i jest przekazywany do targets w celu rekonstrukcji;
- kolejność jednostek pozostaje niezmieniona;
- puste jednostki są KEEP;
- identyfikatory jednostek są walidowane jako unikalne;
- wzorce są kompilowane w jednej warstwie, a błędny regex kończy preprocessing błędem.

Semantyka wzorców jest ograniczona formatowo: wspólne wzorce metadanych są domyślne, natomiast --- jest domyślnie aktywne tylko dla Markdown. Pozwala to zachować zachowanie V3 bez narzucania składni Markdown innym formatom.

Techniczna ochrona inline code (protect_inline_codes) pozostaje odrębnym mechanizmem. Preprocessor nie utożsamia KEEP z placeholderem ochronnym.

Weryfikacja: tests/test_preprocessor.py + tests/test_filter_processor.py + regresje chunkowania i ochrony inline — 23 passed; Ruff i compileall — PASS.


## 2026-10-07 — natywna ścieżka Markdown i Plain Text bez Okapi

Markdown, zwykły tekst i HTML nie wymagają Okapi do ekstrakcji i rekonstrukcji. `FilterRegistry` kieruje `.md`/`.markdown` do `MarkdownFilter`, `.txt`/`.text`/`.log` do `PlainTextFilter`, a `.html`/`.htm`/`.xhtml` do natywnego `HtmlFilter`. Dzięki temu Java Filter Host i Okapi nie są uruchamiane dla tych formatów.

`PlainTextFilter` zachowuje oryginalne puste linie oraz kolejność linii. Jednostkami tłumaczeniowymi są niepuste linie, a writer odtwarza dokument na podstawie stabilnych identyfikatorów i fingerprintu źródła.

Nie należy rozszerzać tej reguły na JSON, YAML, CSV, XML, HTML ani inne formaty strukturalne wyłącznie na podstawie faktu, że są tekstowe. Dla nich wymagany jest osobny, strukturalny kontrakt filtra.
