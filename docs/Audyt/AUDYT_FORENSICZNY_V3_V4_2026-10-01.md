# Audyt forensyczny migracji V3 → V4

**Data:** 2026-10-01  
**Projekt:** `tlumacz-v4`  
**Tryb:** audyt architektoniczny / forensic  
**Zakres:** czystość kodu, relikty V3, błędy przeniesione przez migrację, spójność architektury V4, aktywne i martwe ścieżki, dokumentacja, testy i środowisko uruchomieniowe.

## 1. Cel audytu

Celem nie jest potwierdzenie, że V4 „działa”, lecz ustalenie, czy V4 jest rzeczywistym przepisaniem i odświeżeniem architektury, czy też zawiera elementy mechanicznie przeniesione z V3.

Założenie migracji:
- V4 ma być nową architekturą;
- aktywne backendy: **llama.cpp, Apertium, Cloud**;
- **FastAPI i OpenVINO miały zostać całkowicie usunięte**;
- nomenklatura miała zostać uporządkowana;
- rozwiązania migracyjne/historyczne nie powinny udawać aktywnej architektury.

## 2. Najważniejszy wynik audytu

### P0 — rozbieżność środowiska uruchomieniowego

W środowisku systemowym znajduje się zainstalowany pakiet:

`/usr/lib/python3.14/site-packages/tlumacz`

w wersji **0.31.2**.

Import wykonany poza właściwym środowiskiem V4 wskazywał właśnie ten pakiet, a nie kod V4.

Globalna instalacja 0.31.2 zawiera relikty V3, m.in.:
- FastAPI,
- OpenVINO,
- stare GUI,
- stare ścieżki Cloud,
- OpenAI SDK.

To jest krytyczna obserwacja, ponieważ tłumaczy objawy, które nie pasują do aktualnego kodu V4, w tym:
- błędy typu `openai.RateLimitError`,
- obecność FastAPI/OpenVINO,
- różnice w GUI,
- rozbieżności między kodem audytowanym w V4 a faktycznie uruchamianym programem.

**Wniosek:** przed dalszym debugowaniem funkcjonalnym trzeba ustalić dokładny launcher, interpreter, `Exec=`, PATH, `sys.executable` i `tlumacz.__file__` używane przez GUI/CLI.

**Nie usuwać globalnego pakietu 0.31.2 bez osobnej decyzji.**

---

# 3. Aktywna architektura V4

W aktywnym `src/tlumacz/backends` znajdują się:

- `apertium/`
- `cloud/`
- `llama_cpp/`
- `__init__.py`

Nie ma aktywnych katalogów:
- `fastapi/`
- `openvino/`

W kodzie produkcyjnym nie znaleziono aktywnych klas/ścieżek:
- `OpenVINOBackend`
- `FastAPIServerManager`
- `fastapi_server`
- `openvino_backend`

Jawne wzmianki FastAPI/OpenVINO w aktywnym V4 są głównie komunikatami informującymi o wycofaniu tych technologii oraz asercjami testów migracyjnych.

**Wniosek:** sam katalog backendów jest zgodny z założeniem V4. Problemem są relikty poza głównym katalogiem oraz środowisko uruchomieniowe.

---

# 4. Relikty V3 i elementy wymagające klasyfikacji

## 4.1. `profile_migration.py` — relikt migracyjny

Plik:

`src/tlumacz/backends/cloud/profile_migration.py`

zawiera:
- `migrate_cloud_profiles(...)`,
- komentarze dotyczące migracji profili V3.

Nie znaleziono produkcyjnego caller'a tej funkcji.

Jest używana przez:
`tests/test_cloud_profile_migration.py`.

### Ocena

To wygląda na **kod jednorazowej migracji V3 pozostawiony w aktywnym drzewie V4**.

Dopuszczalne są tylko dwa stany:
1. migracja danych nadal jest potrzebna — wtedy kod powinien być jawnie wydzielonym narzędziem migracyjnym;
2. migracja została zakończona — kod powinien zostać usunięty.

Nie powinien pozostawać jako nieokreślona część backendu Cloud.

**Priorytet: P1.**

---

## 4.2. `SecretStore` — sierota architektoniczna

Plik:

`src/tlumacz/infrastructure/secrets.py`

zawiera `SecretStore`, ale nie znaleziono produkcyjnych callerów.

Jest wykorzystywany w testach.

Rzeczywisty GUI flow nadal pobiera `api_key` z `QLineEdit` i przekazuje go do `BackendSelection`.

### Problem

Istnieje zaprojektowana warstwa sekretów, ale rzeczywisty przepływ jej nie używa.

Powstaje rozjazd:
- architektura deklarowana: centralny SecretStore,
- architektura faktyczna: klucz przechodzi przez GUI.

**Priorytet: P1.**

---

## 4.3. Orphan controllers

Istnieją kontrolery:
- `BackendController`
- `TranslationController`
- `DocumentController`
- `SettingsController`
- `DiagnosticsController`
- `ProgressController`

Mają testy, ale aktualny `MainWindow` nie używa ich jako rzeczywistej warstwy orkiestracyjnej.

`main_window.py` bezpośrednio zarządza m.in.:
- backendem,
- tłumaczeniem,
- progressem,
- ustawieniami,
- runtime llama.cpp,
- filtrami.

### Problem

GUI nie jest cienką warstwą prezentacji. Wiele odpowiedzialności jest skupionych w jednym miejscu.

To sugeruje, że część kontrolerów może być pozostałością po wcześniejszym projekcie architektonicznym albo nieukończonym refaktorem.

**Priorytet: P1.**

---

## 4.4. `DocumentProcessor._unit_parts()` — martwy kod

Metoda `DocumentProcessor._unit_parts()` nie ma znalezionych wywołań w repozytorium.

To jednoznaczny kandydat do usunięcia po potwierdzeniu, że nie jest używana dynamicznie.

**Priorytet: P2.**

---

## 4.5. Backupy obok kodu

W `src/` i `tests/` znajdują się pliki `*.bak.*`, m.in. backupy:
- `backend_registry.py`,
- `providers.py`,
- `main_window.py`,
- `test_cloud_providers_v3_compat.py`,
- `test_gui_surface_parity.py`.

Backupy nie powinny znajdować się obok kodu produkcyjnego.

### Ustalona lokalizacja backupów

Właściwa lokalizacja wskazana dla projektu:

`/home/frs/Projekty/agent-translator-v3/backups`

W przyszłych działaniach backupy należy kierować tam, o ile zakres operacji tego wymaga.

Dodatkowo w repo występują artefakty:
- `__pycache__`,
- `.pytest_cache`,
- `.mypy_cache`,
- `.ruff_cache`.

To są artefakty robocze, nie kod projektu.

**Priorytet: P2.**

---

# 5. Dokumentacja zawierająca relikty lub niespójności V3/V4

## 5.1. Niespójność dotycząca FastAPI/OpenVINO

Dokument:

`docs/reports/FAZA_10_LEGACY_REMOVAL_2026-09-30.md`

deklaruje brak aktywnych FastAPI/OpenVINO.

Jednocześnie:

`docs/technical-docs/index.md`

opisuje FastAPI/OpenVINO jako tymczasowo pozostające w kodzie jako odłączone ścieżki regresyjne.

`docs/technical-docs/server-management.md`

mówi o zachowaniu ich w GUI jako rekordów konfiguracji regresyjnej.

`docs/technical-docs/models.md`

opisuje odłączone ścieżki FastAPI/Transformers oraz OpenVINO/TranslateGemma INT8.

### Wniosek

Dokumentacja nie ma jednej, jednoznacznej klasyfikacji statusu tych technologii.

Jeżeli FastAPI/OpenVINO zostały usunięte z V4, dokumentacja powinna:
- oznaczyć materiały jako historyczne/migracyjne,
- nie przedstawiać ich jako elementów architektury V4,
- wskazać, gdzie znajduje się dowód decyzji migracyjnej.

---

## 5.2. `windows-exe-build.md`

Dokument nadal wymienia:
- `fastapi`,
- `uvicorn`,
- `openvino`,
- `openvino_genai`.

Jeżeli V4 nie dostarcza tych komponentów, dokument jest niespójny z aktualną architekturą.

**Priorytet: P1/P2 zależnie od tego, czy dokument opisuje aktywny proces build.**

---

## 5.3. Dokumentacja TranslateGemma

Nadal istnieje:

`docs/technical-docs/TRANSLATEGEMMA_GOOGLE_CLOUD.md`

z opisem lokalnego serwera FastAPI + Transformers.

Istnieją również:
- `TRANSLATEGEMMA_ONNX_DESKTOP_GUIDE.md`
- `TRANSLATEGEMMA_OPENVINO_AMD_GUIDE.md`

Nie należy ich automatycznie usuwać. Mogą być wartościowymi materiałami historycznymi.

Powinny jednak zostać wyraźnie oznaczone jako:
- historyczne,
- nieaktywne w V4,
- dokumentujące decyzję/eksperyment/migrację.

---

## 5.4. Dokumentacja archiwalna

`docs/archive/plans/PLAN_IMPLEMENTACJI_OPENVINO.md`

jest planem historycznym.

Pozostawienie go w archiwum jest sensowne, ale nie powinien być indeksowany jako aktualna ścieżka implementacyjna.

---

# 6. Konfiguracja — relikt `config/config.json`

Repo zawiera:

`config/config.json`

ze starszą strukturą obejmującą m.in.:
- `backend`,
- `llama`,
- usługi chmurowe,
- profile.

Aktualny V4 używa innego mechanizmu:
`$HOME/.config/tlumacz/settings-v4.json`

Nie znaleziono aktywnego kodu V4, który czyta `config/config.json`.

### Wniosek

`config/config.json` należy sklasyfikować jako:
- fixture/template,
- historyczną konfigurację,
- albo usunąć.

Nie powinien wyglądać jak aktywne źródło konfiguracji V4.

**Priorytet: P1/P2.**

---

# 7. Testy migracyjne zależne od V3

## 7.1. `test_gui_surface_parity.py`

Test odwołuje się bezpośrednio do:

`/home/frs/Projekty/agent-translator-v3/tlumacz/qt_gui/main_window.py`

### Problem

V4 jest zależne od:
- żywego repozytorium V3,
- konkretnej ścieżki filesystemu,
- aktualnego stanu V3.

To nie jest stabilny baseline.

### Docelowo

Baseline V3 powinien być:
- zamrożonym fixture,
- snapshotem,
- artefaktem migracyjnym,
- albo jawnie wersjonowanym materiałem porównawczym.

Nie powinien zależeć od obecności repo V3 na dysku.

**Priorytet: P1.**

---

## 7.2. `test_cloud_providers_v3_compat.py`

Test suite o tej nazwie utrzymuje model „V3 compatibility”.

Sama kompatybilność może być potrzebna, ale przy migracji typu „przepisać architekturę” należy rozdzielić:
- testy kontraktu V4,
- testy kompatybilności/migracji danych.

Docelowe testy backendów powinny przede wszystkim opisywać kontrakt V4, a nie traktować V3 jako bieżącego modelu architektury.

**Priorytet: P2.**

---

# 8. Ustawienia, które mogą być martwe lub pozorne

`AppSettings` zawiera m.in.:
- `model`,
- `cloud_profiles`,
- `server_chat_template`,
- `language`.

Nie wszystkie mają potwierdzony wpływ na aktywny przepływ GUI.

## 8.1. `server_chat_template`

GUI pokazuje opcje m.in.:
- „Natywny Jinja”,
- „ChatML”,
- „TranslateGemma”.

Nie znaleziono spójnego przekazania tej wartości do `LlamaCppRuntimeConfig`.

To może oznaczać **pozorną funkcję GUI**: użytkownik zmienia ustawienie, ale nie ma ono pełnego efektu wykonawczego.

## 8.2. Opcje automatyzacji runtime

GUI zawiera ustawienia:
- automatyczny start llama.cpp,
- czyszczenie cache po tłumaczeniu,
- restart procesu po tłumaczeniu.

Nie znaleziono odpowiadających operacji wykonywanych po zakończeniu tłumaczenia.

### Wniosek

Należy wykonać osobny audyt „setting → consumer → efekt”.

**Priorytet: P1.**

---

# 9. Zależność `openai`

`pyproject.toml` deklaruje:

`openai>=1.0`

Aktywny V4 Cloud używa jednak `urllib`, a nie OpenAI SDK.

Nie znaleziono aktywnych importów OpenAI SDK w V4.

### Wniosek

Zależność wygląda na potencjalny relikt.

Nie należy jej usuwać bez potwierdzenia:
- czy jest wymagana przez inne narzędzie,
- czy ma być transportem kompatybilnościowym,
- czy pozostała po V3.

Jest to szczególnie istotne ze względu na globalną instalację 0.31.2, która faktycznie korzystała z OpenAI SDK.

**Priorytet: P2.**

---

# 10. Cloud — nomenklatura

Aktualnie `provider="openai"` może oznaczać transport/protokół OpenAI-compatible, również dla usług innych niż OpenAI.

Przykładowo model/usługa może być Gemini, Cohere lub DeepSeek, ale warstwa techniczna jest określana jako `openai`.

### Problem

Semantycznie miesza:
- dostawcę usługi,
- protokół transportowy,
- model.

### Docelowy model

Rozdzielić:
- `service/provider`,
- `transport/protocol`,
- `model`,
- `endpoint`.

Nie jest to samo w sobie błąd wykonawczy, ale jest to problem nomenklatury i utrudnia dalszy rozwój.

**Priorytet: P1/P2.**

---

# 11. Microsoft Translator — potwierdzony problem kontraktu

Aktywny `MicrosoftProvider` używa:
- `api-version=2026-06-06`,
- schematu `inputs/targets`,
- nagłówka `Ocp-Apim-Subscription-Key`.

Model konfiguracji nie zawiera jednak regionu.

Dokumentacja Microsoft wskazuje, że dla zasobów multi-service/regionalnych wymagany jest również:

`Ocp-Apim-Subscription-Region`

Dla globalnego single-service może być opcjonalny.

### Wniosek

Model V4 nie rozróżnia wystarczająco:
- klucza,
- endpointu,
- regionu,
- typu zasobu.

To jest **potencjalnie aktywny błąd wykonawczy** zależny od rodzaju zasobu Microsoft.

Nie wykonywano realnego requestu.

**Priorytet: P1.**

---

# 12. Gemini — przestarzały katalog modeli

V4 zawiera:
- `gemini-3.5-flash`,
- `gemini-3.5-flash-lite`.

Aktualna dokumentacja Google klasyfikuje tę generację jako starszą/legacy, podczas gdy nowsza generacja Flash jest dostępna pod nowszymi nazwami modeli.

### Wniosek

Nie jest to dowód błędu samego V4, ale katalog modeli powinien zostać zweryfikowany i oddzielony od kodu transportowego.

**Priorytet: P2.**

---

# 13. Przepływ tłumaczenia — kandydat na błąd architektoniczny

Obserwowany przepływ wygląda w przybliżeniu:

`DocumentProcessor → units → dla każdej jednostki → TranslationOrchestrator([jedna jednostka]) → ChunkPlanner → TranslationExecutor`

Orchestrator wygląda więc na wywoływany osobno dla pojedynczej jednostki dokumentu.

### Potencjalne skutki

- chunking może działać na zbyt małym zakresie;
- batchowanie może być niemożliwe;
- cache może mieć inną semantykę niż zamierzona;
- `max_workers` może nie obejmować całego dokumentu;
- orchestrator może być niepotrzebnie inicjalizowany wielokrotnie.

Nie jest to jeszcze zaklasyfikowane jako potwierdzony bug.

**Następny krok:** prześledzić kontrakty `DocumentProcessor`, `TranslationOrchestrator`, `ChunkPlanner` i `TranslationExecutor` oraz odpowiadające testy.

**Priorytet: P1 — do weryfikacji.**

---

# 14. Progress bar

`self.progress.setRange(0, 0)` jest poprawnym trybem Qt dla postępu nieznanego — pasek działa wtedy jako indeterminate/marquee.

To tłumaczy zachowanie:
- przesuwanie się wskaźnika,
- dojście do końca,
- powrót i ponowne przesuwanie.

Nie jest to samo w sobie błąd Qt.

Wprowadzony później callback progresu próbuje przełączać UI na postęp deterministyczny.

### Ważne

Zmiany progress zostały potraktowane jako rozwiązanie prowizoryczne i nie powinny być uznawane za zamknięcie problemu Cloud bez ustalenia root cause.

---

# 15. Cloud RateLimitError — istotna obserwacja forensyczna

Użytkownik zgłosił błąd:

`RateLimitError: Error code: 429 ... generativelanguage.googleapis.com/generate_content_free_tier_requests ... model: gemini-3.5-flash`

Aktualny V4:
- nie używa OpenAI SDK do Cloud,
- używa `urllib`,
- nie powinien generować wyjątku `openai.RateLimitError`.

W połączeniu z odkryciem globalnego `tlumacz 0.31.2` jest to silny dowód, że zgłoszony wyjątek pochodził z innego środowiska/kodu niż aktualny aktywny Cloud V4.

### Wniosek

Nie należy teraz „naprawiać retry”, limitów ani Cloud na podstawie tego wyjątku.

Najpierw należy ustalić:
1. jaki interpreter uruchamia GUI;
2. skąd ładowany jest `tlumacz`;
3. jaki launcher jest używany;
4. jaki jest `sys.path`;
5. jaki plik `tlumacz.__file__` jest aktywny;
6. czy GUI V4 i CLI V4 uruchamiają ten sam kod.

To jest P0.

---

# 16. Jakość i czystość repozytorium

## Potwierdzone problemy

| Element | Klasyfikacja | Priorytet |
|---|---|---:|
| Globalny `tlumacz 0.31.2` | środowiskowy relikt V3 | **P0** |
| `profile_migration.py` | relikt migracyjny | **P1** |
| `SecretStore` bez produkcyjnych callerów | osierocona infrastruktura | **P1** |
| Kontrolery nieużywane przez MainWindow | rozjazd architektury | **P1** |
| Test zależny od żywego repo V3 | sprzężenie migracyjne | **P1** |
| Dokumentacja FastAPI/OpenVINO | niespójność statusu | **P1** |
| Microsoft region | brak elementu kontraktu | **P1** |
| `config/config.json` | relikt konfiguracji | **P1/P2** |
| `server_chat_template` | możliwa pozorna funkcja | **P1** |
| ustawienia runtime bez consumerów | możliwy martwy feature | **P1** |
| `openai` dependency | możliwy relikt | **P2** |
| `_unit_parts()` | dead code | **P2** |
| backupy `*.bak.*` w src/tests | zanieczyszczenie drzewa | **P2** |
| cache/pycache | artefakty robocze | **P2** |
| V3 compatibility tests | możliwe utrzymywanie starego kontraktu | **P2** |
| stary katalog Gemini | utrzymanie historycznych modeli | **P2** |

---

# 17. Błędy/ryzyka przeniesione z migracją

## Potwierdzone lub bardzo silnie wskazane

### A. V3 jest nadal obecne jako wykonywany pakiet systemowy

To najpoważniejszy problem migracyjny.

V4 może być poprawne lokalnie, ale użytkownik może uruchamiać V3 0.31.2.

### B. V3 pozostaje zależnością testową V4

`test_gui_surface_parity.py` zależy od żywego repo V3.

### C. V3 pozostaje w aktywnym kodzie jako mechanizm migracyjny

`profile_migration.py`.

### D. Stary model konfiguracji nadal istnieje

`config/config.json`.

### E. Stare pojęcia architektoniczne pozostają w dokumentacji

FastAPI/OpenVINO są miejscami opisane tak, jakby nadal były częścią V4.

### F. Warstwa sekretów nie została rzeczywiście wpięta

Istnieje infrastruktura, ale rzeczywisty GUI flow ją omija.

### G. Część warstw architektonicznych jest osierocona

Kontrolery istnieją, ale główny przepływ GUI ich nie wykorzystuje.

---

# 18. Co nie jest obecnie potwierdzonym błędem

Nie należy obecnie klasyfikować jako potwierdzonego błędu:

- samego wspólnego backendu Cloud dla wielu providerów;
- obecności dokumentów historycznych, jeżeli zostaną poprawnie oznaczone;
- `setRange(0,0)` jako takiego;
- braku FastAPI/OpenVINO w `src/tlumacz/backends`;
- różnic wydajności llama.cpp między wariantami CPU;
- samego istnienia testów kompatybilności V3, jeśli zostaną jasno wydzielone jako migracyjne.

---

# 19. Weryfikacja techniczna wykonana przed tym raportem

Z wcześniejszego audytu:

- pytest: **198 passed** przy `QT_QPA_PLATFORM=offscreen`;
- mypy: **Success: no issues found in 68 source files**;
- Ruff: **All checks passed**;
- compileall: PASS;
- świeże venv + wheel: wersja **0.40.0**;
- Apertium runtime/E2E: **6 passed**;
- pełna wcześniejsza regresja GUI/Cloud: **399 passed, 2 skipped**;
- Cloud regression: **14 passed**.

Jednocześnie bez `QT_QPA_PLATFORM=offscreen` jeden z nowych testów GUI kończył się `SIGABRT` z powodu braku display. To jest problem infrastruktury testu, a nie dowód błędu Cloud.

Apertium:
- `eng-pol.t1x.bin` pozostaje zablokowany przez `Undefined attr-item cas_sp`.

Llama.cpp:
- native AVX2 był około 4,1% szybszy od generic;
- dalszy sensowny kierunek to parametry serwera/load, nie kolejne warianty CPU.

---

# 20. Zalecana kolejność dalszego audytu

## P0 — uruchamianie

Ustalić dokładnie:
- launcher GUI,
- desktop entry,
- `Exec=`,
- interpreter,
- `sys.executable`,
- `tlumacz.__file__`,
- PATH,
- aktywne środowisko Python.

Nie zmieniać jeszcze globalnej instalacji.

## P1 — forensic inventory

Sporządzić pełną listę każdego elementu V4 sklasyfikowanego jako:

- aktywny,
- martwy,
- migracyjny,
- historyczny,
- test-only,
- fixture,
- pozorna funkcja,
- błędna architektura,
- uzasadniona kompatybilność.

## P1 — błędy migracyjne

Osobno prześledzić:
- konfigurację,
- Cloud,
- GUI,
- secrets,
- runtime llama.cpp,
- przepływ dokument → jednostki → chunk → backend,
- testy V3/V4.

## P2 — porządki

Dopiero po potwierdzeniu:
- usunąć dead code,
- przenieść/usunąć backupy z drzewa,
- oczyścić zależności,
- uporządkować dokumentację,
- oznaczyć materiały historyczne,
- uporządkować nomenklaturę Cloud.

---

# 21. Zasady dalszej pracy

1. Nie usuwać reliktów przed ich sklasyfikowaniem.
2. Nie wykonywać realnych requestów Cloud podczas diagnostyki architektury.
3. Nie traktować testu przechodzącego jako dowodu poprawnego środowiska uruchomieniowego.
4. Przy zmianach kodu stosować TDD.
5. Przy dużych zmianach wykonywać backup przed zmianą.
6. Backupy kierować do:
   `/home/frs/Projekty/agent-translator-v3/backups`
7. Po zmianach aktualizować dokumentację.
8. Przed deklaracją „naprawione/gotowe” wykonywać świeżą weryfikację.
9. Nie usuwać globalnego `tlumacz 0.31.2` bez osobnej decyzji.

---

# 22. Konkluzja architektoniczna

V4 ma poprawny podstawowy kierunek backendowy: aktywne są llama.cpp, Apertium i Cloud, a FastAPI/OpenVINO nie są już aktywnymi backendami V4.

Jednocześnie migracja nie jest jeszcze czysta architektonicznie.

Najważniejsze pozostałości po V3 to:
- globalnie zainstalowany pakiet 0.31.2,
- kod migracji profili,
- zależność testowa od żywego repo V3,
- stary model konfiguracji,
- historyczne pojęcia w aktywnej dokumentacji,
- osierocona warstwa SecretStore,
- osierocone kontrolery,
- część potencjalnie martwych ustawień,
- potencjalnie stara zależność OpenAI,
- backupy i artefakty robocze w drzewie źródeł.

Najważniejszy wniosek praktyczny:

**Nie należy teraz dalej „naprawiać Cloud” na podstawie zgłoszonego `openai.RateLimitError`. Najpierw trzeba ustalić, czy użytkownik faktycznie uruchamia V4. Obecne dowody wskazują, że przynajmniej część obserwowanego zachowania pochodzi z globalnej instalacji V3 0.31.2.**

Ten dokument jest bazą do dalszego audytu krok po kroku.

## 2026-10-01 — zgłoszenie: serwer llama.cpp nie uruchamia się

- **Status:** zgłoszone, nierozpoznana przyczyna.
- **Komponent:** serwer/runtime llama.cpp.
- **Objaw:** serwer llama.cpp nie uruchamia się.
- **Klasyfikacja:** błąd funkcjonalny do reprodukcji i diagnozy.
- **Priorytet:** P1 — blokuje lokalny backend llama.cpp.
- **Przyczyna:** jeszcze nieustalona; nie zakładamy na tym etapie błędu konfiguracji, modelu, parametrów procesu ani środowiska.
- **Następny krok:** zebrać dokładny komunikat/log uruchomienia oraz ustalić, jaki executable, model i konfiguracja są faktycznie używane.

## 2026-10-01 — nowe zgłoszenie GUI: zakładki i backendy

Użytkownik zgłasza, że w GUI są niewłaściwe zakładki oraz brak współczesnego backendu, przy obecności dwóch starszych backendów. Działające GUI V3.2 ma służyć jako referencja układu i funkcjonalności interfejsu.

Weryfikacja źródeł wykazała:
- V4 MainWindow deklaruje zakładki: Tłumaczenie, API i serwer, Dodatki, Pomoc.
- V4 selektor backendu deklaruje: llama.cpp, Apertium, Chmura.
- V3 MainWindow zawiera rekordy: llama.cpp, FastAPI (TranslateGemma), OpenVINO (TranslateGemma INT8), Apertium, Chmura.

Wniosek: jeżeli użytkownik widzi FastAPI/OpenVINO zamiast współczesnego zestawu V4, jest to kolejny silny sygnał, że uruchamiany jest stary pakiet/launcher. GUI V3.2 można wykorzystać do odtworzenia poprawnego UX, ale nie należy przenosić starych backendów do V4.


## 2026-10-01 — potwierdzenie funkcjonalnego parytetu GUI V3.2 → V4 na podstawie zrzutów

Użytkownik doprecyzował, że audyt GUI ma dotyczyć przede wszystkim **dostępu do funkcji i parytetu funkcjonalnego**, a nie różnic wizualnych.

### Ustalona struktura GUI

W obu wersjach występują cztery zakładki:
1. **Tłumaczenie** — funkcjonalnie identyczna.
2. **Serwery / API i serwer** — zakładka interaktywna; jej zawartość zmienia się zależnie od wybranego serwera/backendu.
3. **Dodatki**.
4. **Pomoc**.

### Ekran „Tłumaczenie”

Zrzut docs/Zrzuty/Tłumaczenie.png jest binarnie identyczny w V3 i V4 (SHA-256: 149a9416b366fc9ad6918cbeeef3e7d705a2c2a2dba71b3fbd1850dcba6352d6). Nie ma podstaw do zgłaszania regresji funkcjonalnej tego ekranu na podstawie samego zrzutu.

### Ekran dynamiczny „API i serwer”

Potwierdzone warianty:

- **llama.cpp** — zrzut V3 i V4 jest binarnie identyczny (SHA-256: f8d287cf9bb3c6d3aa977b0b7ac3cd44d3f64141c2511c18f4b2b17345a19cbe).
- **OpenVINO** — zrzut V3 i V4 jest binarnie identyczny (SHA-256: 8b787c8371cc555fcab90acef213ecbe1df14292b1ce10bde60e869040d50ac2). Jest to jednak **relikt backendu V3**; identyczność ekranu nie oznacza, że OpenVINO należy przywracać do architektury V4.
- **FastAPI** — zrzut V3 i V4 jest binarnie identyczny (SHA-256: c5b53b26ab77793d8be28ce4a4a1f839b57763d02de60e8740e58cf1a033e4a3). Analogicznie jest to **relikt backendu V3**, a nie funkcja docelowego V4.
- **Apertium** — wariant obecny w materiałach V3.2; w V4 istnieje osobny zrzut docs/Zrzuty/Apertium.png. Ten ekran wymaga osobnej weryfikacji funkcjonalnej względem V3.2, ale sam fakt obecności Apertium w V4 jest zgodny z docelową architekturą.
- **Chmura** — wariant jest zależny od wybranego modelu/provider-a i może powodować pojawienie się dodatkowych kontrolek/okien wyboru. Jest to istotna różnica funkcjonalna, a nie tylko wizualna.

### Ważne ustalenie dotyczące zrzutów Cloud

Na dysku występuje niespójność nomenklatury plików względem opisu wersji: API i serwer-chmura.png występuje obecnie tylko w katalogu V3, natomiast API i serwer-chmura-nowa.png występuje w obu katalogach i ma identyczny hash (afb1411c7a5c0556297c2366a1be462df5eae24f90246f0c6745f92e17f86d5f). Nie należy więc klasyfikować wariantu Cloud wyłącznie po nazwie pliku. Do dalszego audytu trzeba powiązać zrzut z faktycznie uruchomioną wersją i stanem selektora modelu/provider-a.

### Wniosek dla audytu regresji

Nie należy traktować całego GUI V4 jako regresji. Z dotychczasowych dowodów wynika:

- wspólna struktura czterech zakładek jest zachowana;
- ekran Tłumaczenie jest identyczny;
- trzy historyczne warianty backendowe (llama.cpp/OpenVINO/FastAPI) mają identyczne zrzuty, ale OpenVINO/FastAPI są reliktami V3 i nie powinny być automatycznie przywracane;
- kluczowym miejscem rzeczywistego parytetu jest **dynamiczna zawartość zakładki Serwery**, szczególnie Apertium, llama.cpp oraz Cloud;
- Cloud wymaga porównania funkcji po zmianie modelu/provider-a, ponieważ pojawiają się dodatkowe kontrolki i okna wyboru;
- obserwację użytkownika o regresji V4 należy dalej weryfikować na **działającym GUI**, a nie wyłącznie na statycznych zrzutach.


## 2026-10-01 — korekta ustaleń GUI po doprecyzowaniu funkcji V3.2

- Język źródłowy w głównym tłumaczeniu jest autodetekcją. Plik wyjściowy użytkownik wskazuje samodzielnie. Przy Apertium osobna kontrolka języka źródłowego jest wymagana, ponieważ backend działa na jawnych parach językowych.
- V3.2 posiadał Natywny Jinja i ChatML. Dodatkowo miał specjalną funkcję szablonu TranslateGemma przeznaczoną do pracy z kodami językowymi innymi niż wcześniejsze warianty. Nie należy opisywać tego jako automatycznego startu llama.cpp.
- Przycisk stanu serwera historycznie pełnił zależnie od backendu/stanu role start/stop/restart. W V4 pozostał jako relikt kodu; obecnie nie ma potrzeby utrzymywania tej wieloznacznej funkcji.
- V3.2 zakładał możliwość wpisania własnego adresu i portu zgodnego API, np. lokalnego Ollama. W V4 należy dodać kategorię **Własny**; po jej wybraniu pole adresu/konfiguracji ma stać się edytowalne.
- Użytkownik zgłasza większą regresję: w faktycznie uruchamianym V4 brak opcji wyboru Apertium. Źródłowy V4 MainWindow nadal zawiera Apertium, więc trzeba rozdzielić stan kodu od faktycznie uruchamianego pakietu/launchera.
- DLX nie jest świadomie usuniętym reliktem. Ma pozostać w V4; brak jego przeniesienia klasyfikujemy jako regresję migracyjną.
- SimplyTranslate zostaje **wycofany z V4**. Użytkownik potwierdził, że połączenie nie udało się ani razu; nie ma uzasadnienia dla utrzymywania providera, konfiguracji GUI ani testu kontraktowego tego adaptera.
- Wcześniejsze stwierdzenie o utracie zaznaczania/odznaczania skilli było błędne. Użytkownik potwierdził, że może zaznaczać i odznaczać skille; nie jest to regresja.
- Zakres bloków od 100 znaków nie jest wymaganiem funkcjonalnym. Praktyczne minimum projektu to 500 znaków, ponieważ mniejsze bloki powodują błędy tłumaczenia. Nie traktujemy więc wartości 100 jako utraty funkcji; warto ograniczyć minimum do 500.

### Zaktualizowane punkty regresji do dalszej weryfikacji
1. Apertium — brak opcji wyboru w faktycznie uruchamianym GUI mimo obecności wpisu w źródle V4.
2. DLX — brak przeniesienia do V4; funkcja ma zostać zachowana.
3. Własny adres/port API — należy dodać kategorię **Własny** i możliwość edycji konfiguracji dla tej kategorii.
4. Specjalny szablon TranslateGemma — zachować jego znaczenie dla kodów językowych; nie mylić go z automatycznym startem llama.cpp.
5. Dynamiczne pola Cloud — weryfikować na faktycznie uruchamianym V4 przed dalszymi zmianami.

### Usunięte z aktywnej macierzy
- SimplyTranslate — provider, profil Cloud, ustawienie silnika i test kontraktowy zostały usunięte z aktywnego kodu V4.

### Nie są regresją
- autodetekcja źródła,
- ręczny wybór pliku wyjściowego,
- osobny język źródłowy Apertium,
- Natywny Jinja i ChatML,
- specjalny szablon TranslateGemma dla kodów językowych,
- pozostały kod start/stop/restart jako relikt implementacyjny,
- zaznaczanie/odznaczanie skilli,
- minimum 500 znaków dla bloku jako praktyczne ograniczenie jakościowe.
