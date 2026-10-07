# Serwery chmurowe / darmowe usługi tłumaczeniowe

**Data researchu:** 2026-09-21  
**Cel:** zebrać darmowe lub bezpłatnie dostępne usługi tłumaczeniowe, które można potencjalnie podłączyć do Tłumacz V3 jako zewnętrzne backendy HTTP.

## 1. Zakres i metodologia

Research wykonano na podstawie:

### Korekta granicy Cloud — 2026-09-26

Ten research opisuje providerów modułu CloudBackend. Mozhi pozostaje
providerem Cloud, a nie osobnym głównym backendem. Szczegółowa migracja granic
modułów znajduje się w `docs/PLAN_MODULARIZACJI_BACKENDOW_2026-09-26.md`.
1. terryyin/translate-python
2. Freed-Wu/translate-shell
3. ManeraKai/simplytranslate
4. mlmdflr/spx-translation
5. RapidFingers/Translator

Źródła:
- https://github.com/terryyin/translate-python
- https://github.com/Freed-Wu/translate-shell
- https://codeberg.org/ManeraKai/simplytranslate
- https://github.com/mlmdflr/spx-translation
- https://github.com/RapidFingers/Translator

### Ważne rozróżnienie

W materiałach występują trzy modele:
1. własne/publiczne API usługi — np. MyMemory;
2. proxy/agregator — np. SimplyTranslate;
3. bezpośrednie wywołanie publicznego endpointu dostawcy bez oficjalnego klucza — część mechanizmów translate-shell.

Nie należy traktować ich jako równoważnych oficjalnym API komercyjnych dostawców.

---

# 2. Szybka tabela

| Usługa | Źródło | Bez klucza | Darmowy dostęp | Model | Ocena stabilności |
|---|---|---:|---:|---|---|
| MyMemory | translate-python | TAK | TAK | public API | dobra |
| LibreTranslate | translate-python / SimplyTranslate | zależy od instancji | TAK / zależy od instancji | REST | dobra dla kontrolowanej instancji |
| SimplyTranslate | SimplyTranslate | często TAK | TAK | proxy REST | zależna od instancji |
| Google przez SimplyTranslate | SimplyTranslate | TAK po stronie klienta | TAK | proxy | zmienna |
| Google przez translate-shell | translate-shell | TAK | TAK | endpoint/scraping | zmienna |
| Bing przez translate-shell | translate-shell | TAK | TAK | endpoint/scraping | zmienna |
| Youdao przez translate-shell | translate-shell | TAK | TAK | endpoint | zmienna |
| Haici przez translate-shell | translate-shell | TAK | TAK | endpoint | zmienna |
| DeepL przez SimplyTranslate | SimplyTranslate | zależy od instancji | zależy od instancji | proxy | zmienna |
| DeepL API Free / Developer | oficjalne API | NIE | TAK, z kluczem | oficjalne API | dobra |
| Microsoft Translator | translate-python | NIE | zależy od oferty | oficjalne API | dobra |
| Yandex Translate | translate-python | NIE | zależy od konta/oferty | oficjalne API | dobra |
| SPX Translation | SPX | niepotwierdzone | aplikacja korzysta z Google/DeepL | aplikacja | nie jest serwerem API |
| RapidFingers | RapidFingers | niepewne | historyczne | aplikacja | historyczna/problemowa |

**Pierwsze kandydaty do testu V3:** MyMemory, konfigurowalne publiczne instancje SimplyTranslate oraz LibreTranslate. Google/Bing/Youdao/Haici przez translate-shell traktować jako eksperymentalne.

---

# 3. MyMemory

## Charakter

translate-python używa MyMemory jako domyślnego providera i pokazuje użycie bez klucza. Projekt opisuje integrację z Translated MyMemory API.

Źródło:
https://github.com/terryyin/translate-python

## Logika połączenia

    V3
      ↓
    MyMemory API
      ↓
    translation

Parametry logiczne:
- tekst,
- source language,
- target language.

translate-python dzieli tekst na fragmenty do maksymalnie 1000 znaków przed przekazaniem do providera.

## Autoryzacja

W pokazanym użyciu:
- brak klucza,
- brak secret_access_key.

## Ograniczenia

Przed integracją trzeba sprawdzić aktualne:
- limity,
- rate limit,
- limit znaków,
- dostępne pary,
- warunki darmowego użycia,
- politykę danych.

**Status: kandydat do prototypu.**

---

# 4. LibreTranslate

LibreTranslate jest open-source'owym REST API MT. translate-python posiada provider libre.

Może działać jako:
- publiczna instancja,
- własny serwer.

Dla V3 interesują nas publiczne, darmowe instancje.

## Typowy interfejs

    POST /translate
    Content-Type: application/json

    {
      "q": "Hello world",
      "source": "en",
      "target": "pl",
      "format": "text"
    }

Typowa odpowiedź:

    {
      "translatedText": "Witaj świecie"
    }

Dokładna autoryzacja i limity zależą od instancji.

## Ważne

Nie zakładać:

    LibreTranslate = zawsze bez klucza

Poprawne założenie:

    LibreTranslate = REST + konkretna instancja + konkretne limity/autoryzacja

**Status: bardzo dobry kandydat na konfigurowalny backend.**

---

# 5. SimplyTranslate

SimplyTranslate jest agregatorem/proxy dla różnych usług tłumaczeniowych.

W materiałach występują m.in.:
- Google,
- LibreTranslate,
- DeepL,
- ICIBA.

## API

Udokumentowany w znalezionych materiałach endpoint:

    GET /api/translate/

Parametry:
- engine,
- from,
- to,
- text.

Przykład:

    https://simplytranslate.org/api/translate/?engine=google&from=en&to=es&text=Hello

Odpowiedź zawiera m.in.:

    {
      "translated-text": "Hola"
    }

Źródło przykładowego wywołania:
https://notes.billmill.org/programming/open_APIs/simply_translate.html

## Instancje

SimplyTranslate jest uruchamiany przez różnych operatorów.

Dlatego:

    instancja A != instancja B

Mogą różnić się:
- dostępnością,
- limitami,
- wersją,
- engine'ami,
- rate limitingiem,
- polityką prywatności.

## Publiczna instancja znaleziona w researchu

Operator Her.st dokumentuje:

    https://trap.her.st/api/translate/

Parametry:
- engine — wymagany,
- from — opcjonalny,
- to — wymagany,
- text — wymagany.

Według strony operatora obsługiwane engine'y obejmują:
- google,
- libre,
- DeepL,
- ICIBA.

Przykład:

    curl "https://trap.her.st/api/translate/?engine=google&from=en&to=es&text=Hello"

Źródło:
https://her.st/public-services/

**Status: wysoki priorytet researchu/prototypu.**

---

# 6. Google przez SimplyTranslate

To nie jest oficjalne Google Cloud Translation API.

Model:

    Tłumacz V3
       ↓
    SimplyTranslate
       ↓
    Google Translate

Konfiguracja:

    base_url = https://<instancja-simplytranslate>
    engine = google
    from = <source>
    to = <target>
    text = <text>

Zalety:
- brak własnego klucza Google,
- prosty HTTP,
- możliwość zmiany instancji.

Ryzyka:
- zależność od operatora,
- brak SLA Google Cloud,
- możliwe limity,
- możliwość wyłączenia instancji,
- zmiana backendu.

**Status: dobry fallback eksperymentalny.**

---

# 7. Google przez translate-shell

translate-shell deklaruje obsługę Google jako online translator.

Przykład:

    trans --translators=google,bing,haici,stardict crush

Python API projektu pokazuje również translator=google.

Źródło:
https://github.com/Freed-Wu/translate-shell

To nie jest oficjalny Google Cloud API adapter.

Nie zakładać:
- stabilnego endpointu,
- gwarantowanego rate limitu,
- SLA,
- bezterminowej kompatybilności.

**Status: eksperymentalny.**

---

# 8. Bing przez translate-shell

translate-shell deklaruje obsługę Bing:

    trans --translators=bing

Mechanizm nie jest tym samym co oficjalny Microsoft Azure Translator API z kluczem.

Zaleta:
- brak własnego klucza w tym trybie.

Ryzyka:
- zmiany po stronie serwisu,
- blokady,
- rate limiting,
- brak oficjalnego kontraktu API.

**Status: eksperymentalny.**

---

# 9. Youdao

translate-shell wymienia Youdao jako online translator:

    youdaozhiyun

Przykład:

    trans --translators=youdaozhiyun

Nie traktować tego jako równoważnego z oficjalnym komercyjnym API.

Szczególnie interesujące jako dodatkowa opcja dla chińskiego.

**Status: eksperymentalny / do weryfikacji.**

---

# 10. Haici

translate-shell deklaruje również:

    haici

Brak wystarczających danych w dostępnym researchu, aby zagwarantować:
- aktualność endpointu,
- limity,
- pełny zakres języków,
- politykę prywatności.

**Status: eksperymentalny / do weryfikacji.**

---

# 11. DeepL

## DeepL przez translate-python

translate-python posiada provider deepl.

Dokumentacja rozróżnia DeepL free API i DeepL pro API. Wymagany jest secret_access_key.

Przykładowa konfiguracja projektu:

    Translator(
        provider="deepl",
        to_lang="pl",
        secret_access_key="<KEY>",
        pro=True,
    )

Parametr pro=True dotyczy wariantu Pro i nie powinien być kopiowany do konfiguracji Free bez weryfikacji aktualnej dokumentacji.

**Status: darmowy plan z kluczem API; limit jest ograniczony.**

## DeepL przez SimplyTranslate

Możliwy model:

    V3 → SimplyTranslate → DeepL

Brak klucza po stronie V3 może być możliwy, ale zależy od konkretnej instancji.

**Status: interesujący do testu.**

---

## Oficjalny DeepL API Free / Developer

DeepL nadal dokumentuje bezpłatny dostęp API dla ograniczonego użycia. Aktualne materiały DeepL podają limit **500 000 znaków miesięcznie** dla DeepL API Free. Jednocześnie DeepL zaznacza, że plan API Free **nie jest już dostępny do zakupu**; trzeba więc odróżnić istniejący dostęp do API Free od aktualnie oferowanego modelu API Developer.

Dla V3 istotne są:
- oficjalny REST API,
- wymagany klucz API,
- endpoint Free rozpoznawany po kluczu z sufiksem :fx,
- ograniczony darmowy limit,
- konieczność obsługi 429 Too Many Requests.

**Status: warto obsłużyć jako opcjonalny backend wymagający klucza; nie traktować jako bezkluczowej usługi.**

## Oficjalny DeepL CLI

Repozytorium:

https://github.com/DeepL/deepl-cli

deepl-cli jest oficjalnym narzędziem DeepL, a nie osobnym serwerem tłumaczeniowym. CLI korzysta z oficjalnego API i wymaga klucza API. Dokumentacja CLI rozpoznaje klucze Free po sufiksie :fx i kieruje je do api-free.deepl.com.

Dla V3 nie ma sensu traktować CLI jako głównego adaptera HTTP. Jest natomiast użyteczne jako:
- narzędzie diagnostyczne,
- referencyjny klient oficjalnego API,
- opcjonalny fallback przez subprocess.

Aktualna wersja CLI 2.x wymaga Node.js 24.15.0 lub nowszego.

**Status: narzędzie pomocnicze / referencyjne, nie osobny backend chmurowy.**

## DLX (dawniej DeepLX) — self-hosted

Repozytorium:

https://github.com/OwO-Network/DLX

DLX jest niezależnym projektem open source i **nie jest produktem ani oficjalnym projektem DeepL**. Jest to serwer API napisany w Go, uruchamiany lokalnie lub na własnym serwerze. Udostępnia prosty endpoint HTTP na porcie 1188.

Przykładowe żądanie:

    POST http://localhost:1188/translate
    Content-Type: application/json

    {
      "text": "Hello, world!",
      "source_lang": "EN",
      "target_lang": "ZH"
    }

Wariant architektoniczny dla V3:

    V3 → DLX → usługa tłumaczeniowa

Z punktu widzenia V3 jest to ciekawy adapter, ponieważ API jest proste i nie wymaga klucza po stronie samego V3. Nie należy jednak klasyfikować DLX jako „darmowej chmury” — użytkownik musi sam uruchomić i utrzymywać serwer, a sposób działania zależy od zewnętrznej usługi tłumaczeniowej wykorzystywanej przez DLX.

**Status: opcjonalny backend self-hosted; osobna kategoria od publicznych usług chmurowych.**

---

# 12. Microsoft Translator API

translate-python posiada provider microsoft.

Wymagane są:
- secret_access_key,
- opcjonalnie region.

Nie jest to bezkluczowy publiczny endpoint.

Może istnieć darmowy poziom zależny od aktualnej oferty Microsoft, ale przed użyciem trzeba zweryfikować bieżące warunki.

**Status: poza podstawową listą bezkluczowych usług.**

---

# 13. Yandex Translate

translate-python posiada provider yandex.

Dokumentacja wymienia:
- API key,
- IAM token,
- folder_id.

Przykład:

    Translator(
        provider="yandex",
        to_lang="pl",
        secret_access_key="your_api_key",
        folder_id="your_folder_id",
    )

Nie jest to bezkluczowy publiczny endpoint.

Dodatkowo historyczny projekt RapidFingers ma issue #68 opisujące problem z Yandex API po zmianach po stronie API:

https://github.com/RapidFingers/Translator/issues/68

**Status: nie używać jako bezkluczowego backendu.**

---

# 14. SPX Translation

Repozytorium:

https://github.com/mlmdflr/spx-translation

opisuje się jako agregator Google + DeepL.

Jest to aplikacja Electron/TypeScript/Vue. README wskazuje użycie biblioteki google-translate-api.

Repozytorium nie daje w dostępnych materiałach potwierdzonego publicznego API serwerowego typu:

    POST /translate

Dlatego SPX nie jest wpisywany jako serwer do bezpośredniej integracji.

Warto zachować repo jako źródło:
- sposobu integracji Google,
- sposobu agregacji Google/DeepL,
- użytej biblioteki.

**Status: materiał researchowy, nie endpoint.**

---

# 15. RapidFingers Translator

Repozytorium:

https://github.com/RapidFingers/Translator

jest aplikacją desktopową dla Elementary OS.

W materiałach występuje historyczna integracja z Yandex Translate. Issue #68 opisuje, że Yandex API przestało działać.

Nie ma wystarczającej podstawy, aby traktować ten projekt jako aktualny, stabilny serwer.

**Status: materiał historyczny.**

---

# 16. Kandydaci dla V3

## Tier A — warto zrobić adapter

### MyMemory

    auth: none
    type: public translation API
    adapter: HTTP

Największa zaleta: prosty bezkluczowy fallback.

### SimplyTranslate

    auth: zależne od instancji
    type: proxy/agregator
    adapter: HTTP GET

Największa zaleta: jeden adapter może dać kilka engine'ów.

### LibreTranslate

    auth: zależne od instancji
    type: REST MT
    adapter: HTTP POST

Największa zaleta: prosty standardowy interfejs.

---

# 17. Tier B — eksperymentalne

- Google przez SimplyTranslate
- DeepL przez SimplyTranslate
- Google przez translate-shell
- Bing przez translate-shell
- Youdao
- Haici

Wspólna cecha: większa zależność od nieoficjalnych lub publicznych endpointów.

---

# 18. Tier C — konto/klucz

- DeepL API Free
- Microsoft Translator
- Yandex Translate

To nadal kwalifikuje się do kryterium „darmowe”, jeśli konto/klucz jest bezpłatny. Wymaganie klucza nie oznacza automatycznie usługi płatnej. DeepL API Free pozwala na 500 000 znaków miesięcznie, ale plan nie jest już dostępny do zakupu dla nowych subskrypcji.

Mogą mieć darmowe poziomy lub bezpłatne limity, ale nie są bezkluczowymi usługami.

# 19. Tier D — self-hosted

- DLX (dawniej DeepLX)

To nie jest publiczna chmura. V3 łączy się z własnym serwerem DLX przez HTTP, a użytkownik ponosi koszt i odpowiedzialność za jego uruchomienie.

---

# 19. Wnioski z analizy kodu dodatkowych projektów

## DLX

Kod DLX pokazuje dobre wzorce adaptera: normalizację kodów językowych, limity wejścia, timeout, ponowne użycie klienta HTTP, klasyfikację błędów 429/403/503/504 oraz walidację odpowiedzi. To warto przejąć do V3. Nie ma natomiast podstaw, aby traktować mechanizm DLX jako algorytm poprawiający jakość samego modelu tłumaczeniowego.

Źródło: https://github.com/OwO-Network/DLX/blob/main/translate/translate.go

## PDF

Wskazany simit22/pdf-translator jest prostym CLI: ekstrakcja PDF → Google Translation API → PDF. Samo repozytorium nie pokazuje zaawansowanego mechanizmu poprawy jakości semantycznej. Dla V3 ważny jest jednak wzorzec: dokumentu nie należy traktować jako jednego dużego stringa. Warto zachować bloki, nagłówki, podpisy, tabele i elementy nietłumaczalne, a dopiero potem wykonywać tłumaczenie i rekonstrukcję.

Źródło: https://github.com/simit22/pdf-translator

## EPUB

Xuepoo/agent-book-translate wykorzystuje checkpointy SQLite dla chunków, retry API, bezpieczne resume, walidację przed zapisem oraz kontrolę poprawności wynikowego EPUB i wycieków struktur JSON. To bardzo dobry wzorzec dla długich dokumentów: stabilny chunk → tłumaczenie → walidacja → checkpoint → następny chunk.

Źródło: https://github.com/Xuepoo/agent-book-translate

## Kontekst, terminologia i spójność

Najcenniejszy wzorzec z narzędzi EPUB to pamięć dokumentu: styl, terminologia, nazwy własne, kontekst rozdziału, poprzedni fragment i wcześniej zatwierdzone tłumaczenia. W V3 warto mieć TranslationContext z polami: document_style, glossary, named_entities, chapter_context, previous_translation i translation_memory. Dodatkowym etapem może być consistency check po rozdziale lub dokumencie.

## Polyglot — wiele języków równolegle

Specious/polyglot jest cienką warstwą nad translate-shell. Pozwala ustawić wiele języków docelowych i wykonywać tłumaczenia równolegle. Nie poprawia jakości pojedynczego tłumaczenia, ale pokazuje dobry model dla V3: jeden TranslationJob może mieć wiele targetów, a każdy target powinien mieć niezależny cache, retry i ograniczenie współbieżności.

Źródło: https://github.com/specious/polyglot

## Priorytetowe mechanizmy dla V3

1. Semantic chunking zamiast cięcia wyłącznie po liczbie znaków.
2. Glossary i translation memory.
3. Kontekst dokumentu/rozdziału oraz poprzedni fragment.
4. Ochrona placeholderów, tagów, URL-i, nazw własnych i kodu.
5. Walidacja struktury i wyniku po każdym chunku.
6. Retry/backoff oraz checkpoint/resume.
7. Drugi przebieg kontroli spójności terminologicznej.
8. Dla PDF: zachowanie bloków i geometrii podczas rekonstrukcji.
9. Dla EPUB: zachowanie XHTML/CSS/TOC i tłumaczenie tylko dozwolonych węzłów.
10. Dla wielu języków: równoległość ograniczana per provider.

Najważniejszy wniosek: poprawę jakości uzyskamy przede wszystkim przez lepszy pipeline wokół silnika tłumaczeniowego, a nie przez samo dodawanie kolejnych endpointów.

---

# 20. ccMesh — gateway dla chmurowych modeli AI

Repozytorium:

https://github.com/VkRainB/ccMesh

ccMesh nie jest silnikiem tłumaczeniowym ani własnym modelem MT. Jest lokalnym gatewayem/proxy dla chmurowych modeli AI i usług kompatybilnych z API, m.in. OpenAI, Claude i Codex.

## Model działania

    Tłumacz V3
          ↓
        ccMesh
          ↓
    ┌─────┼─────────┐
    │     │         │
  OpenAI Claude   Codex
    │     │         │
    └─────┴─────────┘
          ↓
       model cloud

Projekt obsługuje m.in.:
- wiele endpointów,
- mapowanie modelu wejściowego na model wyjściowy,
- rotację endpointów,
- failover,
- circuit breaker,
- testy dostępności,
- monitoring requestów i tokenów,
- konwersję protokołów między interfejsami API,
- obsługę długich requestów/streamingu.

## Znaczenie dla V3

ccMesh może być użyte jako opcjonalna warstwa pomiędzy V3 a chmurowym LLM:

    CloudLLMProvider
          ↓
        ccMesh
          ↓
    OpenAI / Claude / Codex / inne API

Nie powinien być mieszany z warstwą tłumaczeniową ani z XLIFF. Odpowiada za transport, routing i obsługę upstreamów, natomiast V3 powinien odpowiadać za:
- ekstrakcję treści,
- XLIFF,
- segmentację semantyczną,
- kontekst tłumaczenia,
- walidację,
- rekonstrukcję dokumentu.

## Szczególnie interesujące mechanizmy

Warto przeanalizować w V3 jako wzorce:
- endpoint health check,
- failover,
- circuit breaker,
- retry/backoff,
- timeouty,
- routing model → endpoint,
- ujednolicony interfejs dla różnych protokołów,
- kontrolę wielkości requestu.

W kontekście dużych bloków kontekstowych istotne jest również rozdzielenie limitu gatewaya od limitu samego modelu/provider API. ccMesh nie rozwiązuje problemu semantycznej segmentacji dokumentu.

## Klasyfikacja

ccMesh należy traktować jako:

    Tier E — gateway / infrastruktura dla chmurowych LLM

Nie jest:
- osobnym modelem tłumaczeniowym,
- bezpłatnym silnikiem MT,
- zamiennikiem DeepL/Google/LibreTranslate,
- rozwiązaniem problemu jakości tłumaczenia.

Jego wartość dla V3 polega na możliwości ujednolicenia dostępu do kilku chmurowych modeli i zastosowania failover/routingu bez zmiany warstwy translacji.

**Status: materiał architektoniczny + opcjonalny gateway dla Cloud LLM.**

Źródło:
https://github.com/VkRainB/ccMesh

---

# 21. Interfejs backendu V3

Warto ujednolicić wszystkie cloud providers:

    class CloudTranslationProvider:
        name: str

        def translate(
            self,
            text: str,
            source_lang: str,
            target_lang: str,
        ) -> TranslationResult:
            ...

Wynik:

    TranslationResult(
        text,
        provider,
        source_lang,
        target_lang,
        detected_lang,
        raw_response,
    )

Format konkretnego providera nie powinien przedostać się do core translation engine.

---

# 22. Konfiguracja instancji

Dla proxy/agregatorów preferowany jest model:

    cloud_providers:
      simplytranslate:
        enabled: true
        base_url: "https://..."
        engine: "google"
        timeout: 20

      libretranslate:
        enabled: true
        base_url: "https://..."
        api_key: null

      mymemory:
        enabled: true
        timeout: 20

Dzięki temu użytkownik może zmienić publiczną instancję bez zmiany kodu.

---

# 23. Fallback chain

Darmowe usługi mogą być czasowo niedostępne.

Przykład:

    Cloud router
         ↓
    MyMemory
         ↓ fail
    SimplyTranslate / Google
         ↓ fail
    LibreTranslate
         ↓ fail
    local llama.cpp

Nie należy automatycznie zmieniać providera po błędzie jakościowym, jeżeli użytkownik wybrał konkretny silnik.

Rozróżniać:

### Transport failure
- timeout,
- DNS,
- HTTP 5xx,
- rate limit.

### Provider failure
- nieobsługiwana para,
- invalid request.

### Quality failure
- pusty wynik,
- uszkodzone placeholdery,
- zły język.

Automatyczny fallback jest najbardziej uzasadniony dla dwóch pierwszych kategorii.

---

# 24. Rate limiting

Każdy darmowy backend powinien mieć lokalny limiter.

Minimalne dane:

    provider
    requests/minute
    characters/request
    characters/day
    concurrency
    cooldown

Jeżeli limit jest nieznany, zapisać:

    unknown

a nie:

    unlimited

Szczególnie ważne dla publicznych instancji SimplyTranslate i LibreTranslate.

---

# 25. Cache

Darmowe API powinny być używane razem z cache.

Klucz minimalny:

    provider
    source_lang
    target_lang
    source_text

Dla usług zależnych od wersji można dodać:

    engine
    provider_version

Cache ogranicza:
- rate limiting,
- czas,
- obciążenie publicznych instancji,
- powtarzanie identycznych tłumaczeń.

---

# 26. Prywatność

Cloud backend oznacza wysłanie tekstu poza komputer.

Dla każdego providera warto mieć:

    privacy_level:
      local
      public-api
      third-party-proxy

Przykłady:

MyMemory:
    public-api

SimplyTranslate:
    third-party-proxy

Google przez SimplyTranslate:
    third-party-proxy → Google

Żaden z tych wariantów nie jest offline.

---

# 27. Normalizacja języków

Backend powinien mieć wspólną warstwę:

    V3 language code
           ↓
    provider adapter
           ↓
    provider-specific code

Trzeba uwzględnić różnice typu:
- zh-CN / zh-cn / zh,
- he / iw,
- pt / pt-BR.

Mapowanie powinno być w adapterze, nie w core.

---

# 28. Chunking dla API

Nie zakładać, że każdy provider przyjmuje dowolny tekst.

Adapter powinien znać:

    max_chars
    max_bytes
    max_requests
    rate_limit

Jeżeli limit nie jest znany, stosować bezpieczny limit konfiguracyjny.

Pipeline:

    document
      ↓
    existing V3 segmentation
      ↓
    cloud adapter chunking
      ↓
    API
      ↓
    merge
      ↓
    validation

Nie zastępować istniejącego chunkingu dokumentów przypadkowym limitem API.

---

# 29. Walidacja odpowiedzi

Każdy cloud backend powinien przejść przez wspólny validator:

1. HTTP status;
2. JSON/schema;
3. niepusty tekst;
4. zachowanie placeholderów;
5. brak nieoczekiwanego HTML;
6. sensowna długość;
7. język wynikowy;
8. brak komunikatu błędu w polu tekstowym.

Dopiero potem wynik trafia do TranslationResult.

---

# 30. Minimalny test providera

### Test 1 — prosty tekst

    Hello world.
    →
    Witaj świecie.

### Test 2 — autodetection

    source_lang = auto

### Test 3 — Markdown

    # Hello

    **Important** text.

### Test 4 — placeholder

    Hello {name}, your balance is {{balance}}.

### Test 5 — Unicode

    Zażółć gęślą jaźń.

### Test 6 — błędy sieci

- timeout,
- 429,
- 500.

### Test 7 — nieobsługiwana para

Provider powinien zwrócić kontrolowany błąd.

---

# 31. Bezpieczeństwo

## Nie logować

- API keys,
- pełnego tekstu dokumentu,
- pełnych odpowiedzi cloud API.

## Logować

- provider,
- engine,
- source/target,
- czas,
- HTTP status,
- rozmiar requestu,
- rozmiar response,
- retry count.

## Timeout

Każdy request musi mieć timeout.

Brak timeoutu może zablokować pipeline dokumentu.

---

# 32. Architektura docelowa

    CloudTranslationManager
              │
      ┌───────┼────────┐
      │       │        │
    MyMemory  Simply  LibreTranslate
                │
          ┌─────┼─────┐
          │     │     │
        Google DeepL ICIBA

Dodatkowo eksperymentalnie:

    Google/Bing/Youdao/Haici
              ↑
        translate-shell

Core nie powinien wiedzieć, czy provider działa:
- bezpośrednio,
- przez proxy,
- przez scraping.

Ma widzieć jednolity interfejs.

---

# 33. Priorytety wdrożeniowe

## P0

1. MyMemory.
2. Konfigurowalny LibreTranslate.
3. Konfigurowalny SimplyTranslate.
4. Cache.
5. Timeout/retry.
6. Walidacja odpowiedzi.

## P1

1. Wybór engine SimplyTranslate.
2. Google przez SimplyTranslate.
3. DeepL przez SimplyTranslate.
4. Provider health check.
5. rate limiter.

## P2

1. Google przez translate-shell mechanism.
2. Bing przez translate-shell.
3. Youdao.
4. Haici.
5. automatyczny fallback.

## P3

- Microsoft Free tier,
- DeepL Free API,
- Yandex,
- kolejne agregatory.

---

# 34. Co nie jest aktywnym backendem

### SPX Translation

Powód:
- aplikacja agregująca,
- brak potwierdzonego publicznego API serwerowego.

### RapidFingers Translator

Powód:
- stara integracja,
- historyczny problem z Yandex API,
- brak podstaw do uznania za aktualny serwer.

Oba projekty pozostają źródłami researchu.

---

# 35. Najważniejsze obserwacje

1. Najcenniejsza jest warstwa adapterów, nie pojedynczy serwer.
2. SimplyTranslate może dać wiele engine'ów przez jeden protokół.
3. MyMemory jest interesujący jako prosty bezkluczowy fallback.
4. LibreTranslate jest dobrym kandydatem, ale trzeba konfigurować konkretną instancję.
5. Google/Bing przez translate-shell są użyteczne eksperymentalnie, ale nie powinny być traktowane jak oficjalne API.
6. DeepL/Yandex/Microsoft mają inne wymagania autoryzacyjne i nie powinny być mieszane z bezkluczowymi usługami.
7. Publiczne instancje są współdzielone — cache i rate limiting są obowiązkowe.
8. ccMesh jest interesującym wzorcem gatewaya dla chmurowych LLM, ale nie zastępuje backendu tłumaczeniowego.
9. Cloud backend powinien być opcjonalny; llama.cpp pozostaje lokalnym fallbackiem.

---

# 36. Stan researchu

| Projekt | Wartość dla V3 | Wniosek |
|---|---|---|
| translate-python | wysoka | źródło providerów i prostego interfejsu |
| translate-shell | wysoka | wiele bezkluczowych mechanizmów, część niestabilna |
| SimplyTranslate | bardzo wysoka | interesujący agregator/proxy |
| SPX Translation | średnia | przykład agregatora Google + DeepL |
| RapidFingers Translator | niska | głównie wartość historyczna |
| ccMesh | wysoka dla Cloud LLM | gateway/proxy infrastrukturalny, nie silnik MT |
| Crow Translate / Mozhi | bardzo wysoka | publiczne instancje Mozhi + opcjonalny bezpośredni LibreTranslate |

---

# 37. Zastrzeżenia

Ten dokument jest researchem, nie listą gwarantowanych publicznych SLA.

„Darmowe” oznacza:
- brak opłaty w zakresie opisanym przez źródło,
- albo publiczny dostęp bez klucza,
- albo darmowy tier wymagający klucza.

Nie oznacza:
- nieograniczonego użycia,
- gwarantowanej dostępności,
- gwarantowanej jakości,
- gwarantowanego braku blokad,
- gwarantowanego braku zmian endpointu.

Przed dodaniem providera do V3 należy wykonać aktualny smoke test.

---

# 38. Źródła

- https://github.com/terryyin/translate-python
- https://github.com/Freed-Wu/translate-shell
- https://codeberg.org/ManeraKai/simplytranslate
- https://github.com/mlmdflr/spx-translation
- https://github.com/RapidFingers/Translator
- https://github.com/RapidFingers/Translator/issues/68
- https://github.com/VkRainB/ccMesh
- https://invent.kde.org/office/crow-translate
- https://github.com/KDE/crow-translate
- https://github.com/crow-translate/QOnlineTranslator
- https://codeberg.org/aryak/mozhi
- https://her.st/public-services/
- https://notes.billmill.org/programming/open_APIs/simply_translate.html

## Główne ustalenia ze źródeł

translate-python potwierdza providerów:
- MyMemory,
- Microsoft,
- DeepL,
- LibreTranslate,
- Yandex.

translate-shell potwierdza online translators:
- Google,
- Bing,
- Youdao,
- Haici.

SPX opisuje agregację:
- Google,
- DeepL.

RapidFingers dostarcza przede wszystkim historycznego materiału o integracji Yandex.

---

# 39. Następny krok

Przed implementacją warto przygotować Cloud Provider Probe:

    GET/POST
       ↓
    health check
       ↓
    simple translation
       ↓
    placeholder test
       ↓
    Unicode test
       ↓
    language-pair test
       ↓
    rate-limit observation
       ↓
    latency
       ↓
    result

Dopiero wyniki probe powinny decydować, które darmowe serwery rzeczywiście trafiają do V3.

**Nie zakładać dostępności na podstawie samego README projektu.**

---

# 40. Crow Translate / Mozhi — publiczne serwery i endpointy

## Cel audytu

Przeanalizowano aktualny kod Crow Translate z repozytorium KDE pod kątem wyciągnięcia rzeczywistych URL-i serwerów używanych przez aplikację.

Źródła kodu:
- https://invent.kde.org/office/crow-translate
- https://github.com/KDE/crow-translate
- https://github.com/crow-translate/QOnlineTranslator

Crow Translate 4.x używa warstwy **Mozhi** jako agregatora/proxy dla silników tłumaczeniowych. README aktualnej wersji opisuje wiele silników dostarczanych przez Mozhi, a kod `MozhiTranslationProvider` domyślnie wskazuje instancję `https://mozhi.aryak.me`. citeturn0search1turn0search9

## Rzeczywiste URL-e instancji Mozhi znalezione w kodzie

Kod `src/instancepinger.cpp` zawiera następującą listę publicznych instancji, które Crow może sprawdzać i spośród których może wybrać najszybszą:

| # | URL | Rola |
|---:|---|---|
| 1 | `https://mozhi.aryak.me` | domyślna instancja |
| 2 | `https://translate.bus-hit.me` | publiczna instancja Mozhi |
| 3 | `https://nyc1.mz.ggtyler.dev` | publiczna instancja Mozhi |
| 4 | `https://translate.projectsegfau.lt` | publiczna instancja Mozhi |
| 5 | `https://translate.nerdvpn.de` | publiczna instancja Mozhi |
| 6 | `https://mozhi.ducks.party` | publiczna instancja Mozhi |
| 7 | `https://mozhi.frontendfriendly.xyz` | publiczna instancja Mozhi |
| 8 | `https://mozhi.pussthecat.org` | publiczna instancja Mozhi |
| 9 | `https://mo.zorby.top` | publiczna instancja Mozhi |
| 10 | `https://mozhi.adminforge.de` | publiczna instancja Mozhi |
| 11 | `https://translate.privacyredirect.com` | publiczna instancja Mozhi |
| 12 | `https://mozhi.canine.tools` | publiczna instancja Mozhi |
| 13 | `https://mozhi.gitro.xyz` | publiczna instancja Mozhi |

**Ważne:** powyższe URL-e są wyciągnięte bezpośrednio z aktualnego kodu Crow Translate. Nie oznacza to, że wszystkie instancje są obecnie dostępne lub że mają identyczną konfigurację silników.

## Endpoint tłumaczenia używany przez Crow

Dla zwykłego trybu Mozhi kod `OnlineTranslator::requestTranslate()` buduje:

    GET <INSTANCE>/api/translate

z parametrami:

    engine=<engine>&from=<source>&to=<target>&text=<text>

Przykładowo dla instancji domyślnej:

    https://mozhi.aryak.me/api/translate

To jest właściwy endpoint, który warto traktować jako wzorzec backendu HTTP dla V3.

## Silniki widoczne w aktualnym kodzie Crow / QOnlineTranslator

Enum `OnlineTranslator::Engine` zawiera:

- Google
- Yandex
- Deepl
- Duckduckgo — komentarz w kodzie wskazuje również nazwę Bing
- LibreTranslate
- MyMemory
- Reverso

Crow nie wywołuje jednak tych usług bezpośrednio w normalnym trybie Mozhi. Nazwa silnika jest przekazywana do instancji Mozhi jako parametr `engine`. README QOnlineTranslator również opisuje obsługę Google, Yandex, Bing, LibreTranslate i Lingva. citeturn1search1

### Wniosek dla V3

Nie należy kopiować tych nazw jako osobnych URL-i serwerów Crow bez dalszego audytu Mozhi. Z kodu Crow można potwierdzić:

    V3 → Mozhi instance → engine → upstream translation service

Natomiast konkretne upstream URL-e Google/Yandex/DeepL/Bing/Reverso/MyMemory powinny być wyciągane z kodu samego **Mozhi**, a nie przypisywane Crow na podstawie samego enumu silników.

## Bezpośredni LibreTranslate

Aktualny kod posiada również tryb `direct` dla LibreTranslate. Wtedy Crow omija endpoint Mozhi i wykonuje:

    POST <INSTANCE>/translate

z JSON-em zawierającym m.in. `q`, `source`, `target`, `format` oraz opcjonalnie `api_key`.

W tym trybie `INSTANCE` jest konfigurowany przez użytkownika — kod Crow nie podaje jednej konkretnej publicznej instancji LibreTranslate jako stałego serwera.

Dlatego do listy publicznych serwerów V3 **nie należy dopisywać arbitralnego URL-a LibreTranslate na podstawie Crow**.

## TTS

Warstwa Mozhi generuje również adresy TTS:

    <INSTANCE>/api/tts

z parametrami `engine`, `lang` i `text`.

Nie jest to endpoint tłumaczenia tekstu, dlatego nie należy traktować go jako osobnego backendu MT.

## LocalAI / chmurowe LLM

Aktualny Crow posiada także osobny backend LocalAI/OpenAI-compatible. Domyślne adresy zapisane w kodzie obejmują m.in.:

- `http://localhost:11434` — Ollama
- `http://localhost:1234` — LM Studio
- `http://localhost:8082` — inny lokalny endpoint OpenAI-compatible
- `https://api.anthropic.com` — Anthropic

Są to jednak **adresy domyślne/configurable backendów LLM**, a nie publiczne serwery MT używane przez warstwę Mozhi. Nie dodaję ich do głównej listy serwerów tłumaczeniowych.

## Znaczenie dla architektury V3

Crow dostarcza bardzo interesujący wzorzec:

    V3
      ↓
    Provider / adapter
      ↓
    konfigurowalna instancja Mozhi
      ↓
    /api/translate
      ↓
    wybrany engine

Najcenniejsze elementy do dalszego researchu V3:

1. lista wielu instancji tego samego gatewaya,
2. automatyczny pomiar opóźnienia instancji,
3. wybór najszybszej instancji,
4. możliwość ręcznego ustawienia instancji,
5. jeden protokół HTTP dla wielu upstreamów,
6. oddzielenie adresu gatewaya od nazwy silnika,
7. możliwość przełączenia LibreTranslate na bezpośredni REST API.

### Status

**Crow Translate / Mozhi: bardzo wartościowe źródło architektoniczne i lista konkretnych publicznych endpointów do dalszego smoke testu.**

Nie należy jednak traktować 13 znalezionych URL-i jako gwarantowanych aktywnych serwerów — są to adresy zapisane w kodzie aktualnej wersji Crow Translate.

---

# Dziennik aktualnych błędów backendów — 2026-09-29

Poniższa sekcja rejestruje **konkretne błędy zaobserwowane podczas testów V3**. Nie są to ogólne założenia ani błędy wywnioskowane z dokumentacji dostawcy.

| Backend | Serwer / endpoint użyty w teście | Status podczas testu | Zwrócony błąd | Retryable | Znaczenie / dalsze działanie |
|---|---|---|---|---|---|
| **LibreTranslate** | `https://libretranslate.com` | niedziała | `HTTP 403` — Cloudflare Error 1010, `browser_signature_banned` | `false` | Żądanie jest blokowane przez Cloudflare na warstwie ochrony usługi. Nie omijać blokady przez podszywanie się pod przeglądarkę. Do ponownego testu potrzebna jest inna instancja lub kontrolowana instancja własna. |
| **SimplyTranslate** | `https://simplytranslate.org/api/translate` | niedziała | `HTTP 404: Not Found` | brak potwierdzenia retry | Aktualnie używany endpoint nie odpowiada oczekiwaną trasą. Traktować jako problem adresu/instancji, a nie jako chwilowe przeciążenie. Wymaga znalezienia i zweryfikowania aktualnej instancji/API. |
| **Gemini Flash** | `https://generativelanguage.googleapis.com/v1beta/openai/` / model `gemini-3.5-flash` | niedziała okresowo | `HTTP 503` — `This model is currently experiencing high demand...` | tymczasowy | Serwer modelu zgłosił chwilowe przeciążenie. Jest to błąd tymczasowy; Flash Lite podczas tego samego okresu działał poprawnie. |
| **ChatGPT** | `https://api.openai.com/v1` / model `chat-latest` | brak kredytów | `HTTP 429` — `insufficient_quota`, `credit_balance_exhausted` | nie jako rozwiązanie | Endpoint OpenAI działa i żądanie dociera do API. Konto nie ma dostępnych kredytów API. Nie jest to błąd konfiguracji endpointu. |

## Szczegóły błędów

### LibreTranslate — 403 / Cloudflare

Zaobserwowano:

    HTTP 403
    Cloudflare Error 1010
    browser_signature_banned
    retryable: false

Dokładny fingerprint klienta blokowany przez Cloudflare nie został ujawniony w odpowiedzi. Z samego komunikatu nie można potwierdzić, czy źródłem blokady jest konkretny nagłówek, biblioteka HTTP czy kombinacja cech żądania.

### SimplyTranslate — 404

Zaobserwowano:

    HTTP 404: Not Found

W tym przypadku nie należy stosować retry jako rozwiązania. Najpierw trzeba zweryfikować aktualny endpoint instancji SimplyTranslate i zgodność trasy z adapterem V3.

### Gemini Flash — 503

Zaobserwowano:

    HTTP 503
    This model is currently experiencing high demand...

Błąd oznacza przeciążenie modelu/usługi. **Gemini Flash Lite działał**, dlatego nie należy traktować całego dostępu Gemini jako niesprawnego.

### ChatGPT — 429 / brak kredytów

Po poprawieniu profilu `ChatGPT` w `$HOME/.config/tlumacz/config.json` żądanie zaczęło docierać do właściwego API OpenAI. API zwróciło:

    HTTP 429
    type: insufficient_quota
    code: credit_balance_exhausted

Wniosek diagnostyczny: konfiguracja endpointu OpenAI jest poprawna; obecnym ograniczeniem jest wyczerpany limit/kredyt API.

## Zasada dokumentowania kolejnych awarii

Dla każdego kolejnego niedziałającego backendu zapisywać:

1. nazwę backendu/providera,
2. URL lub instancję używaną podczas testu,
3. HTTP status,
4. `type` / `code`, jeżeli dostawca je zwraca,
5. krótki komunikat błędu,
6. informację, czy błąd jest retryable,
7. decyzję: naprawa konfiguracji, zmiana instancji, retry/backoff, wymagany klucz/kredyty albo wycofanie backendu.

Nie klasyfikować backendu jako „niedziałający” wyłącznie na podstawie pojedynczego timeoutu lub chwilowego 5xx bez zapisania dokładnej odpowiedzi serwera.


## Migracja SimplyTranslate → SimplyTranslate AI — 2026-09-29

Dotychczasowy endpoint projektu simplytranslate.org/api/translate zwracał HTTP 404. Integrację zmieniono na POST https://api.simplytranslate.ai/translate z JSON-em text/from/to i odpowiedzią w polu result.

Test przez Translator._translate_chunk() zwrócił HTTP 403, Cloudflare Error 1010, browser_signature_banned dla strefy api.simplytranslate.ai. Środowisko Bmax jest blokowane przez warstwę bezpieczeństwa usługi; blokady nie obchodzimy przez podszywanie się pod przeglądarkę.

## Błąd wspólnej warstwy Cloud — 2026-09-29

Podczas debugowania GUI wykryto błąd niezależny od konkretnego providera: wspólna ścieżka OpenAI-compatible tworzyła klienta z `timeout=600 s`, mimo że konfiguracja Cloud przewidywała `cloud_timeout=30 s`. W logu wystąpiły żądania trwające 139,6 s, 317,6 s, 332,5 s i 334,0 s. Oznaczało to, że niektóre próby tłumaczenia mogły przez kilka minut czekać na odpowiedź i kończyć się komunikatem transportowym zamiast kontrolowanym błędem Cloud.

Naprawiono to w `tlumacz/core.py`: dla `backend_type="cloud"` klient OpenAI-compatible respektuje `cloud_timeout`, natomiast lokalny `llama.cpp` zachowuje `600 s`. Dla Cloud zmniejszono również budżet `max_tokens` dla krótkich fragmentów z dotychczasowego minimum `2048` do zakresu `128..1024`, zależnego od długości fragmentu.

Regresja: `tests/test_core.py::test_cloud_openai_compatible_client_uses_cloud_timeout_and_bounded_completion`.

Weryfikacja: `tests/test_core.py tests/test_cloud_providers.py` — **66 passed**; wybrane testy profili Cloud w GUI — **5 passed**; `tests/test_backend_manager.py` — **22 passed**.

## V4 — stan po audycie regresji GUI/Cloud — 2026-10-01

### Aktywne backendy
GUI V4 udostępnia trzy aktywne rodziny backendów: llama.cpp, Apertium i Cloud. FastAPI i OpenVINO są wycofane.

### Providerzy Cloud

| Provider | Adapter V4 | Profil/obsługa |
|---|---:|---|
| OpenAI-compatible | tak | Cohere, ChatGPT, Codex, Gemini Flash, Gemini Flash Lite, DeepSeek |
| DeepL | tak | DeepL API Free |
| Microsoft | tak | Microsoft Translator |
| MyMemory | tak | MyMemory |
| LibreTranslate | tak | LibreTranslate |
| SimplyTranslate | tak | SimplyTranslate + wybór silnika |
| Mozhi | tak | Mozhi + instancja + silnik |
| DLX | tak | DLX/OneShot |

Konfiguracja profili znajduje się w src/tlumacz/resources/cloud_models.json. Klucze API pozostają w konfiguracji użytkownika.

### GUI Cloud
W zakładce API i serwer dla Chmura dostępne są adres URL, klucz API, profil Cloud, instancja i silnik Mozhi, silnik SimplyTranslate oraz opcja restartu procesu po tłumaczeniu. Układ został zweryfikowany względem docs/Zrzuty/API i serwer-chmura-nowa.png z V3.

### Testy regresyjne
- tests/test_cloud_providers_v3_compat.py — 21 passed;
- tests/test_gui_regression_v3_v4.py — 3 passed;
- pełny suite V4 — 195 passed.


## Weryfikacja powierzchni GUI — 2026-10-01

Porównano pełny zestaw aktywnych elementów objectName V3/V4. Elementy FastAPI/OpenVINO zostały świadomie pominięte. Test powierzchni GUI: PASS. Pełny suite po naprawie: 196 passed.
