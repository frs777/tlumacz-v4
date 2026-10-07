# Handoff techniczny — Filter Engine / Okapi

**Projekt:** Tłumacz
**Obszar:** V4 Filter Engine / Okapi / Markdown / inline codes
**Priorytet:** wysoki — problem blokuje pełną walidację
**Status:** diagnostyka rozpoczęta, root cause nie jest jeszcze potwierdzony

---

## 1. Cel przekazania

Należy zdiagnozować dwa powiązane z Filter Engine problemy:

1. **utrata markerów inline podczas przepływu Okapi → Python → backend → Python → Okapi,**
2. **natywny `SIGABRT` procesu Pythona podczas pracy/kończenia wątków `tlumacz-filter-*` z udziałem Qt/PySide6.**

Nie należy zakładać z góry, że oba problemy mają wspólną przyczynę.

---

## 2. Problem A — utrata markerów inline

### Objaw

Podczas tłumaczenia dokumentu Markdown Filter Engine kończy operację:

```text
FilterEngineError:
Backend zmodyfikował lub zgubił markery inline Filter Engine.

Stan markerów:
__OKAPI_CODE_0__=0,
__OKAPI_CODE_1__=0
```

Wartości `0` oznaczają, że w odpowiedzi przekazanej do `restore()` wymagane markery nie występują.

---

## 3. Przykład reprodukcyjny

Problem został zaobserwowany podczas tłumaczenia:

```text
reprodukcyjny plik README z dużą liczbą inline-code
```

Dokument ma szczególnie dużo inline-code:

- około 3328 bajtów,
- 67 linii,
- ponad 3300 znaków backtick.

Jest więc dobrym przypadkiem testowym dla obsługi kodów inline.

---

## 4. Aktualny przepływ

Istotna ścieżka wygląda następująco:

```text
Okapi Markdown Filter
        │
        ▼
ITextUnit / TextFragment
        │
        ▼
Okapi inline codes
        │
        ▼
PUA representation
        │
        ▼
_protect_filter_inline_codes()
        │
        ▼
__OKAPI_CODE_0__
__OKAPI_CODE_1__
        │
        ▼
_translate_chunk()
        │
        ▼
backend tłumaczeniowy
        │
        ▼
response
        │
        ▼
restore()
        │
        X
FilterEngineError
```

Kluczowe jest ustalenie, **na którym dokładnie odcinku marker przestaje istnieć**.

---

## 5. Co jest potwierdzone

### 5.1. Okapi używa inline codes

Inline code nie jest zwykłym tekstem. Okapi reprezentuje kody inline jako element struktury `TextFragment`.

### 5.2. Tłumacz wykonuje dodatkową konwersję

Kod projektu zamienia rozpoznane reprezentacje PUA na markery:

```text
__OKAPI_CODE_0__
__OKAPI_CODE_1__
...
```

Mechanizm znajduje się w warstwie Pythonowej Filter Engine.

### 5.3. `restore()` wymaga integralności markerów

Po otrzymaniu odpowiedzi wykonywana jest kontrola liczby markerów.

Oczekiwany jest dokładnie taki sam zestaw markerów, jaki został wygenerowany przed tłumaczeniem.

Brak markera powoduje wyjątek zamiast publikowania uszkodzonego dokumentu.

To zachowanie należy traktować jako **mechanizm bezpieczeństwa**, a nie jako źródło pierwotnego problemu.

### 5.4. Wyjątek następuje przed `apply()`

Na podstawie dotychczasowego debugowania błąd powstaje w Pythonowej warstwie `restore()`.

Nie ma dowodu, że:

- writer Okapi,
- zapis dokumentu,
- `apply()`

są przyczyną tego konkretnego wyjątku.

Nie należy więc rozpoczynać naprawy od writerów Markdown.

---

## 6. Najważniejsze pytanie diagnostyczne

Potrzebujemy odpowiedzi na jedno konkretne pytanie:

> Czy marker `__OKAPI_CODE_N__` jest już uszkodzony przed wysłaniem tekstu do backendu, czy backend zwraca odpowiedź bez tego markera?

Należy zarejestrować dla **jednej konkretnej jednostki**:

```text
SOURCE
MASKED
REQUEST
RAW RESPONSE
RESTORE RESULT
```

Przykładowo:

```text
SOURCE:
tekst `foo` dalszy tekst

MASKED:
tekst __OKAPI_CODE_0__ dalszy tekst

REQUEST:
[dokładny tekst przekazany backendowi]

RAW RESPONSE:
[dokładna odpowiedź backendu]

EXPECTED MARKERS:
__OKAPI_CODE_0__

ACTUAL COUNTS:
__OKAPI_CODE_0__ = 0
```

Bez tego nie należy przypisywać winy ani Okapi, ani backendowi.

---

## 7. Hipotezy

### H1 — backend usuwa marker

**Aktualnie najbardziej prawdopodobna hipoteza.**

Marker:

```text
__OKAPI_CODE_0__
```

jest dla modelu/MT zwykłym ciągiem tekstowym.

Nie ma formalnej gwarancji, że backend:

- zachowa marker,
- nie zmieni jego pisowni,
- nie usunie go,
- nie powtórzy go,
- nie przestawi go.

Trzeba jednak potwierdzić to surowym request/response.

### H2 — `_protect_filter_inline_codes()` błędnie rozpoznaje kody

Możliwa hipoteza.

Należy sprawdzić rzeczywisty `TextFragment` oraz wynik konwersji:

```text
PUA → __OKAPI_CODE_N__
```

dla problematycznej jednostki.

### H3 — `_translate_chunk()` modyfikuje wynik

Należy zbadać wspólną warstwę tłumaczenia niezależnie od konkretnego backendu.

Szczególnie:

- przygotowanie promptu,
- normalizację odpowiedzi,
- usuwanie dodatkowego tekstu,
- trimming,
- parser odpowiedzi,
- cache.

### H4 — cache zwraca odpowiedź bez markerów

Należy wykonać reprodukcję:

```text
cache = OFF
```

i porównać z:

```text
cache = ON
```

Jeżeli problem występuje wyłącznie przy cache, należy przenieść diagnostykę do warstwy cache.

### H5 — problem po stronie Okapi Markdown Filter

Obecnie **brak dowodu**.

Należy najpierw sprawdzić, czy `TextFragment` przekazywany do `_protect_filter_inline_codes()` zawiera poprawne inline codes.

Jeżeli tak, sam Markdown Filter nie powinien być uznany za winnego tylko dlatego, że dokument zawiera Markdown.

---

## 8. Minimalny eksperyment rozstrzygający

Przed modyfikacją produkcyjnego kodu należy wykonać następujące testy.

### Test A — identity backend

Backend powinien zwrócić dokładnie:

```text
input == output
```

Jeżeli:

```text
protect()
→ identity
→ restore()
```

przechodzi, mechanizm protect/restore jest zasadniczo spójny.

### Test B — kontrolowana transformacja

Dla:

```text
Hello __OKAPI_CODE_0__ world
```

backend powinien zwrócić:

```text
Cześć __OKAPI_CODE_0__ świecie
```

Marker pozostaje nietknięty.

Jeżeli `restore()` przejdzie, potwierdzamy poprawność podstawowego kontraktu.

### Test C — rzeczywisty backend

Zapisać:

```text
request
response
marker counts
```

i porównać.

### Test D — wszystkie aktywne backendy

Porównać:

```text
masked request
raw response
```

dla tych samych danych.

Nie porównywać na tym etapie całych dokumentów — interesuje nas wyłącznie integralność markerów.

### Test E — cache OFF

Wykluczyć wpływ cache.

---

## 9. Ważne ograniczenie diagnostyczne

Nie należy wykonywać poprawki typu:

```python
if marker_missing:
    odtwórz_marker()
```

bez ustalenia jego pozycji.

Samo odtworzenie liczby markerów może stworzyć dokument formalnie poprawny pod względem liczby kodów, ale semantycznie błędny.

Przykład:

```text
A __OKAPI_CODE_0__ B
```

nie jest równoważne:

```text
__OKAPI_CODE_0__ A B
```

Integralność wymaga co najmniej:

- identyfikacji wszystkich kodów,
- zachowania ich tożsamości,
- zachowania poprawnej kolejności,
- zachowania relacji z tekstem.

---

## 10. Problem B — `SIGABRT` Filter Engine / Qt

Drugi problem jest odrębny.

Pełna suite testów dochodziła do około:

```text
171 passed
```

po czym proces kończył się:

```text
Fatal Python error: Aborted
```

Stos wskazywał na:

```text
libQt6Core.so.6
PySide6.QtCore
shiboken6
```

a aktywne wątki obejmowały:

```text
tlumacz-filter-*
```

w:

```text
filter_engine/protocol.py
```

szczególnie:

```text
_read_stderr()
_read_responses()
```

---

## 11. Znaczenie crasha

To nie jest zwykłe:

```text
pytest FAIL
```

Proces Pythona kończy się natywnym:

```text
SIGABRT
```

To oznacza, że należy zbadać lifecycle:

```text
Filter Engine start
        ↓
reader threads
        ↓
response/stderr readers
        ↓
shutdown
        ↓
Qt/PySide6 object destruction
        ↓
thread destruction
```

Szczególnie podejrzana jest kolejność niszczenia:

```text
QObject
QThread
Python wrapper
thread target
stderr/stdout reader
```

---

## 12. Co sprawdzić w `protocol.py`

Należy przeanalizować:

```text
_read_stderr()
_read_responses()
```

oraz:

- kto uruchamia wątki,
- kto je zatrzymuje,
- czy mają jawny `stop_event`,
- czy wszystkie są `join()`owane,
- czy subprocess jest zamykany przed wątkami czy odwrotnie,
- czy stdout/stderr mogą zostać zamknięte podczas odczytu,
- czy wyjątek z reader thread może pozostać nieobsłużony,
- czy obiekt Qt jest niszczony zanim reader thread zakończy pracę,
- czy `__del__` może uruchamiać cleanup w niewłaściwym momencie.

---

## 13. Nie łączyć automatycznie obu problemów

Aktualny stan dowodów nie pozwala stwierdzić:

```text
utrata markerów = SIGABRT
```

To mogą być:

- dwa niezależne defekty,
- dwa objawy tego samego błędnego lifecycle,
- błąd danych powodujący wyjątek, który następnie ujawnia wadliwy cleanup.

Trzeba to rozstrzygnąć eksperymentalnie.

---

## 14. Kryteria zakończenia pracy

### Integralność markerów

- [ ] reprodukcja problemu,
- [ ] zapis SOURCE,
- [ ] zapis MASKED,
- [ ] zapis REQUEST,
- [ ] zapis RAW RESPONSE,
- [ ] jednoznaczne wskazanie miejsca utraty markera,
- [ ] test regresyjny,
- [ ] poprawka,
- [ ] test identity backend,
- [ ] test rzeczywistego backendu,
- [ ] test z cache ON/OFF.

### Lifecycle

- [ ] reprodukcja `SIGABRT`,
- [ ] backtrace,
- [ ] identyfikacja kolejności zamykania Filter Engine,
- [ ] poprawka lifecycle,
- [ ] regresja shutdown,
- [ ] wielokrotny start/stop,
- [ ] brak aktywnych `tlumacz-filter-*` po zakończeniu,
- [ ] brak `ResourceWarning`,
- [ ] brak natywnego `SIGABRT`.

### Walidacja

- [ ] skoncentrowane testy Filter Engine,
- [ ] testy dokumentowe,
- [ ] pełna suite,
- [ ] `compileall`,
- [ ] brak regresji Qt/QML,
- [ ] aktualizacja dokumentacji.

---

## 15. Czego obecnie NIE zakładać

Nie zakładać bez dowodu, że:

1. winny jest Okapi,
2. winny jest Markdown Filter,
3. winny jest konkretny backend,
4. winny jest cache,
5. należy automatycznie regenerować brakujące markery,
6. problem `SIGABRT` jest tym samym problemem co utrata markerów,
7. należy zmieniać kod writerów.

Najpierw trzeba uzyskać dowód z rzeczywistego przepływu danych.

---

## 16. Najważniejszy następny krok

**Nie zaczynać od przepisywania filtra.**

Najpierw uruchomić kontrolowaną reprodukcję i uzyskać:

```text
ITextUnit.source
        ↓
inline codes
        ↓
masked text
        ↓
request
        ↓
raw response
        ↓
restore()
        ↓
marker counts
```

To powinno jednoznacznie powiedzieć, czy problem leży:

```text
[Okapi]
   ↓
[ochrona kodów]
   ↓
[transport]
   ↓
[backend]
   ↓
[restore]
```

Dopiero na tej podstawie należy przygotować właściwą poprawkę.

---

## Stan przekazania

**Problem jest rzeczywisty i odtworzony.**

**Root cause utraty markerów: jeszcze niepotwierdzony.**

**Root cause `SIGABRT`: jeszcze niepotwierdzony.**

Najbardziej wartościowym wynikiem kolejnego etapu będzie nie kolejny ogólny test suite, lecz **dokładny ślad jednej jednostki od Okapi do backendu i z powrotem**, wraz z analizą lifecycle wątków Filter Engine.

---

## Aktualizacja 2026-10-07 — wyniki kolejnego etapu

### Ustalone

Bieżący kod repozytorium nie zawiera opisanej w pierwotnym handoffie warstwy __OKAPI_CODE_N__. Do tej pory PUA Okapi przechodziły bezpośrednio z TextFragment do backendu. To jest rzeczywista luka kontraktowa na granicy Okapi → backend.

Dla reprodukcyjnego pliku README z dużą liczbą inline-code aktualny Okapi Filter zwracał 37 jednostek, 18 jednostek zawierających inline codes oraz 72 wystąpienia kodów. Reprezentacja PUA była poprawna, a identity → merge zakończyło się poprawnie.

Nie potwierdzono winy Markdown Filter ani writera.

### Wdrożona poprawka

Dodano src/tlumacz/filter_engine/inline_code_protection.py.

Backend otrzymuje teraz markery ASCII __OKAPI_CODE_N__, a po odpowiedzi wykonywana jest ścisła kontrola kompletności, liczby, kolejności i tożsamości każdego markera.

Brakujący, zduplikowany lub przestawiony marker powoduje InlineCodeProtectionError; nie jest wykonywana automatyczna rekonstrukcja markera.

Integracja została wykonana w TranslationOrchestrator, przed cache i walidacją wyniku.

### Lifecycle

FilterHostClient ma teraz niedemoniczne wątki stdout/stderr. Dodano regresję pojedynczego i dziesięciokrotnego start → request → close. Oba reader threads muszą zakończyć się przed powrotem z close().

### Weryfikacja

- test ochrony markerów + orchestrator/cache: 7 passed;
- skoncentrowany Filter Engine: 30 passed;
- protokół Filter Host: 8 passed;
- README reprodukcyjny: extract + identity merge PASS;
- backend llama.cpp podczas tej sesji nie był dostępny (connection refused).

### Pozostały gate

Nie wolno uznać rzeczywistego backendowego request/response za zweryfikowany bez uruchomionego backendu. Po jego udostępnieniu należy wykonać dla jednej jednostki SOURCE → MASKED REQUEST → RAW RESPONSE → RESTORE oraz osobno potwierdzić brak SIGABRT w pełnym przebiegu Qt/PySide6.