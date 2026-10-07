# Audyt inżynierski — Tłumacz V4
## Data: 2026-10-05

Zakres: /home/frs/Projekty/tlumacz-v4

Tryb: audyt read-only oraz uruchomienie istniejących testów i kontroli jakości. Nie instalowano ani nie usuwano oprogramowania i nie modyfikowano kodu aplikacji.

# 1. Werdykt

STATUS: NIEGOTOWY DO FINAL RELEASE.

Rdzeń V4 ma dobrą strukturę modułową i wysoki poziom testowania, ale obecny stan nie spełnia jeszcze wymagań produkcyjnego release'u.

Najważniejsze blokery:

1. Apertium runtime nie jest samodzielny ani relokowalny. Bundlowany runtime uruchamia executable, ale nie zawiera danych językowych; discovery zwraca 0 par.
2. Dane Apertium zawierają twarde ścieżki do starego V3: /home/frs/Projekty/agent-translator-v3/...
3. Istniejący wheel 0.40.0 jest niezgodny z aktualnym source: zawiera stare kontrolery i nie zawiera aktywnego qml_gui.
4. Nowy build wheel nie przechodzi z powodu Git ownership w nadrzędnym checkoutcie /home/frs/Projekty.
5. Ruff: 8 błędów w całym zakresie, w tym 1 w kodzie produkcyjnym. Mypy: 2 błędy.
6. Local/custom API key może nadal trafić do settings-v4.json, mimo obecności SecretStore.
7. Brakuje jawnego shutdown TranslationCache i zarządzanego llama.cpp przy zamknięciu GUI.
8. Dokumentacja bieżąca nadal zawiera historyczne wyniki jakości, np. 268 passed i Ruff/mypy PASS.
9. GUI oferuje TXT/PDF jako skille, mimo że nie są aktywnymi filtrami głównego FilterRegistry.
10. Repozytorium ma około 3.9 GB artefaktów, brak własnej historii Git V4 i brak lokalnego .gitignore.
11. Brakuje pełnego E2E TranslateGemma, Windows runtime, pełnego dependency/licence closure i repozytoryjnego CI.
12. W source znajduje się około 70 MB plik help.pl.md.corrupt-20261005.

# 2. Wykonane kontrole

- pytest: 297 passed
- pytest + coverage: 297 passed, około 80% statements
- compileall: PASS
- qmllint: PASS
- Ruff src/tests: FAIL, 8 błędów
- Ruff src: FAIL, 1 błąd
- mypy src: FAIL, 2 błędy
- build wheel: FAIL
- Apertium bundled runtime: 3.9.12
- Apertium default discovery: 0 par
- Apertium z istniejącym drzewem danych: 5 wykrytych wpisów, brak eng-pol
- inspekcja istniejącego wheel 0.40.0
- inspekcja dependency/imports
- inspekcja dokumentacji i repozytorium

# 3. Architektura

Ocena: 7/10.

Aktualny przepływ jest zasadniczo poprawny:

QML → QmlApplicationBridge → TranslationApp → BackendService → DocumentTranslationService → DocumentProcessor → FilterRegistry/FilterLifecycle → TranslationOrchestrator → Backend → validation → write.

Mocne strony:
- wyraźne warstwy domain/application/backends/filter_engine/infrastructure/qml_gui;
- rdzeń aplikacyjny nie zależy od Qt;
- orchestrator nie zna szczegółów dokumentów ani providerów;
- cancellation, cache i validation mają własne komponenty;
- backendy są odseparowane.

Główna słabość:
QmlApplicationBridge ma około 1736 linii i około 60 KB. Odpowiada jednocześnie za presentation state, settings, secrets, skills, glossary, translation lifecycle, backend selection, llama lifecycle, help/i18n i metrics.

Wniosek: bridge jest obecnie God Objectem prezentacyjnym. Docelowo powinien zostać rozdzielony na kompetencje, ale dopiero po zamknięciu blockerów release.

# 4. Python — poprawność, ergonomia i czystość

Pozytywy:
- typowanie;
- dataclasses;
- jawne kontrakty domenowe;
- osobne klasy błędów;
- Filter Engine z lifecycle;
- CancellationToken;
- ResultValidator i MarkerValidator;
- TranslationCache;
- kontrola własności procesu llama.

Problemy:
- Ruff src zgłasza E501 w qml_gui/app.py, linia 68;
- mypy zgłasza problemy z callbackiem lambda w qml_gui/app.py;
- w bridge jest dużo powtarzalnych aliasów snake_case/camelCase;
- odpowiedzialności bridge są zbyt szerokie;
- lifecycle cache nie jest zamykany;
- application shutdown nie jest spięty z runtime cleanup.

# 5. Cache i lifecycle

TranslationCache posiada metodę close(), ale TranslationApp nie posiada centralnego close() i qml_gui/app.py nie podpina cleanupu do QGuiApplication.aboutToQuit.

W testach wystąpiło 46 ostrzeżeń ResourceWarning, w tym unclosed sqlite3.Connection.

To jest realny problem lifecycle, nie tylko problem estetyki testów.

Dodatkowe ryzyko: zarządzany llama.cpp ma start/stop/restart, ale brak jawnego stop_llama przy zamknięciu aplikacji.

Priorytet: P1.

# 6. Sekrety

Cloud profile są częściowo poprawnie migrowane do SecretStore.

Problem dotyczy local/custom.

AppSettings nadal posiada pola api_key i last_local_api_key. Bridge wpisuje local API key do settings, a save_settings serializuje cały dataclass.

W efekcie lokalny klucz może zostać zapisany w:
$HOME/.config/tlumacz/settings-v4.json

To jest sprzeczne z celem SecretStore.

Priorytet: P1 security/privacy.

Potrzebny jest osobny test: zapis local/custom key → odczyt JSON → brak sekretu → ponowny start → sekret dostępny wyłącznie przez SecretStore.

# 7. Backendy

## llama.cpp

Stan: wdrożony.

Obecne:
- start/stop/restart;
- health;
- ownership check;
- GGUF;
- compute mode;
- parallel;
- chat template;
- TranslateGemma special mode;
- cancellation.

Brak pełnego E2E z rzeczywistym modelem TranslateGemma.

Status: częściowo zamknięty; kontrakty są testowane, ale release gate E2E nie jest zamknięty.

## Cloud

Stan: wdrożony.

Provider registry obejmuje OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate, DLX i Mozhi.

Architektura router/provider jest poprawna. Brakuje pełnego live E2E wszystkich ścieżek.

## Custom

Stan: wdrożony przez CloudRouter.

Nie jest osobnym runtime.

# 8. Apertium — krytyczny obszar

Bundlowany runtime znajduje się w:
src/tlumacz/backends/apertium/native_runtime/

Executable zgłasza Apertium 3.9.12.

Jednocześnie native_runtime/share/apertium nie zawiera kompletnego zestawu danych językowych. Discovery domyślnego runtime zwraca 0 par.

Istniejące dane są w:
Aperitium/.prefix/share/apertium/

Po użyciu tego katalogu wykryto tylko 5 wpisów:
spa-gener, spa-morph, spa-tagger, spa-pol, pol-spa.

Nie wykryto eng-pol.

Dodatkowo w co najmniej pięciu plikach mode występują twarde ścieżki:
 /home/frs/Projekty/agent-translator-v3/...

Próba uruchomienia spa-pol wykazała:
- brak cg-proc;
- odwołania do ścieżek V3;
- brak wymaganych artefaktów transfer/t1x/t2x/t3x;
- brak relokowalności.

Wniosek:
Apertium wymaga pełnego runtime reconstruction i packaging repair. Nie wystarczy dopisanie pojedynczej pary językowej.

Priorytet: P0.

# 9. Filter Engine i funkcje

Aktywny registry obejmuje:
- DOCX
- ODT
- HTML/XHTML
- Markdown
- EPUB
- XLIFF

To jest spójne z aktualnym build_filter_registry().

Problem TXT/PDF:
GUI posiada skill options TXT i PDF oraz logikę automatycznego wyboru tych skilli, ale FilterRegistry ich nie rejestruje.

To tworzy fałszywą affordance w GUI.

Priorytet: P1.

# 10. QML — poprawność

Pliki:
- Main.qml
- TranslationPage.qml
- ApiPage.qml
- ExtrasPage.qml
- HelpPage.qml
- HelpMarkdownView.qml

qmllint: PASS.

Pozytywy:
- ColumnLayout/RowLayout/GridLayout/StackLayout;
- Layout.fillWidth;
- Layout.preferredWidth;
- czytelna struktura kart;
- logika tłumaczenia pozostaje poza QML;
- MarkdownText w HelpMarkdownView jest jawnie ustawione.

Problemy:
1. TranslationPage używa dla Apertium nierównych marginesów 24/40 przy polach 110 px.
2. Main.qml ma bazowy font 15 px, podczas gdy aktualna dokumentacja opisuje 17 px.
3. ExtrasPage ma wiele powtarzających się font.bold: false i nierówną indentację.
4. ExtrasPage posiada Timer 1000 ms wywołujący refreshSkills().
5. refreshSkills() nie skanuje katalogu; tylko tworzy katalog i emituje skillsChanged. Timer powoduje więc niepotrzebną reevaluację UI.
6. Część layoutów używa wielu arbitralnych fixed widths: 110/120/130/140/180/360.
7. Custom taby Help są implementowane Rectangle + MouseArea zamiast semantycznego control pattern, co pogarsza potencjalną accessibility i keyboard navigation.

Ocena QML:
- poprawność techniczna: 8/10;
- maintainability: 6/10;
- ergonomia: 6.5/10.

# 11. Testy

297 testów przechodzi.

Coverage:
- 4104 statements;
- 807 missed;
- około 80%.

Największe luki:
- qml_gui/bridge.py około 73%;
- qml_gui/app.py około 66%;
- Apertium languages około 41%;
- Cloud Mozhi około 59%;
- backend registry około 61%;
- TranslationApp około 75%.

Brakuje przede wszystkim testów:
- clean wheel install;
- wheel content;
- relocation;
- Apertium self-contained;
- shutdown;
- local/custom secret isolation;
- real TranslateGemma;
- complete format support matrix.

# 12. Packaging i deployment

Build:
python -m build --wheel --no-isolation
FAIL z powodu Git ownership w /home/frs/Projekty.

Istniejący wheel:
temp/wheel/tlumacz-0.40.0-py3-none-any.whl

jest niezgodny z aktualnym source. Inspekcja wykazała stare kontrolery oraz brak qml_gui/QML.

Wniosek:
nie wolno używać obecnego wheel jako dowodu aktualnego release.

Dodatkowy problem:
app.py oczekuje tlumacz-dark.svg i tlumacz-light.svg, a HelpPage oczekuje frsststems_logo_full.svg. Packaging nie ma zamkniętego testu obecności tych assetów.

Wymagany gate:
source → wheel → clean install → assets check → CLI smoke → QML smoke.

# 13. Launcher i środowisko

uruchom-v4.sh ma twardą ścieżkę /home/frs/Projekty/tlumacz-v4, więc nie jest przenośnym launcherem.

W source checkout:
PYTHONPATH=src python -m tlumacz --version
zwraca 0.40.0.

Bez PYTHONPATH środowisko globalne ładuje /usr/lib/python3.14/site-packages/tlumacz, co zwiększa ryzyko pomylenia V3/V4.

Wniosek:
release musi być testowany w izolowanym środowisku instalacyjnym, a nie na globalnym Pythonie.

# 14. Zależności

Aktualne bezpośrednie zależności:
- openai
- PySide6
- PyMuPDF
- markdown-it-py
- lxml
- lingua-language-detector

Import audit source:
- openai: 0 importów;
- PyMuPDF/fitz: 0 importów;
- markdown_it: 0 importów;
- lxml: używane;
- lingua: używane.

Co najmniej trzy zależności wyglądają na historyczne:
- openai;
- PyMuPDF;
- markdown-it-py.

Nie usuwać automatycznie. Najpierw potwierdzić, czy nie są potrzebne przez planowane lub opcjonalne funkcje.

Brak pełnego lockfile'a obniża reproducibility release.

# 15. Repozytorium

Największe katalogi:
- .migration-backups około 1.8 GB;
- Aperitium około 1.5 GB;
- temp około 1.1 GB;
- glosariusze około 117 MB;
- backups około 95 MB;
- build około 91 MB;
- .mimocode około 58 MB;
- src około 158 MB.

Łącznie około 3.9 GB.

tlumacz-v4 nie ma własnego .gitignore.
Nadrzędny .gitignore praktycznie tylko ignoruje .aider*.

Projekt jest częścią nadrzędnego checkoutu Git i nie ma własnej historii commitów. To utrudnia:
- diff;
- review;
- bisect;
- rollback;
- provenance;
- CI.

Wniosek:
granica repozytorium V4 wymaga formalnego uporządkowania.

# 16. Artefakty

src/tlumacz/qml_gui/help.pl.md.corrupt-20261005 ma około 70 MB.

To powinno być evidence/backup poza aktywnym source albo zostać usunięte po osobnej zgodzie. Nie usuwano go w audycie.

# 17. Dokumentacja

Dokumentacja jest bardzo rozbudowana i ma dobrą strukturę źródeł prawdy.

Problemem jest świeżość.

Aktualnie:
- pytest 297 passed;
- Ruff FAIL;
- mypy FAIL.

W wielu dokumentach nadal występuje:
- 268 passed;
- Ruff PASS;
- mypy PASS.

Historyczne raporty są dopuszczalne, ale STATUS, ARCHITECTURE i aktywne technical docs nie powinny przedstawiać historycznych gate'ów jako bieżących.

Druga sprzeczność:
find docs -type f daje 457 plików.
INDEX.yml podaje file_count 457.
INDEX.md zawiera jednak tekst o 445 wpisach/445 rzeczywistych plikach.

To wymaga synchronizacji.

# 18. CI/CD

Nie znaleziono projektu .github.

Brakuje repozytoryjnego quality gate obejmującego:
- Ruff;
- mypy;
- pytest;
- qmllint;
- build;
- wheel content;
- clean install;
- QML smoke;
- release manifest.

Dokumentacja deklaruje gate'y, ale repo nie wymusza ich automatycznie.

Priorytet: P1.

# 19. Security

Pozytywy:
- SecretStore istnieje;
- cloud migration usuwa api_key z cloud_profiles;
- QML maskuje API key;
- nie wykryto kluczy PEM w source scan.

Problemy:
- local/custom secret może być w JSON;
- Apertium bundluje wiele bibliotek systemowych, więc potrzebny jest pełny supply-chain/licence closure;
- brak dedicated secret persistence test;
- globalny Python nie jest wiarygodnym środowiskiem release.

# 20. Ponytail / nadmiarowość

Najważniejsze kandydatury:
1. QmlApplicationBridge — dekompozycja.
2. openai/PyMuPDF/markdown-it-py — potwierdzić i potencjalnie usunąć.
3. niepotrzebne aliasy snake_case/camelCase — po kontraktowym potwierdzeniu.
4. timer refreshSkills — zastąpić event-driven.
5. powtarzany styling QML — wprowadzić ograniczony system tokenów.

# 21. Ocena

| Obszar | Ocena |
|---|---:|
| Architektura | 7/10 |
| Python | 7/10 |
| Domain/application | 8/10 |
| Filter Engine | 8/10 |
| Backend abstraction | 7.5/10 |
| Apertium | 3/10 |
| llama.cpp | 7.5/10 |
| Cloud | 8/10 |
| QML correctness | 8/10 |
| QML maintainability | 6/10 |
| UX/layout | 6.5/10 |
| Tests | 8.5/10 |
| Coverage | 7.5/10 |
| Packaging | 3/10 |
| Deployment | 4/10 |
| Documentation volume | 9/10 |
| Documentation freshness | 5/10 |
| Repository hygiene | 3/10 |
| Release reproducibility | 3/10 |
| Overall release readiness | 4/10 |

# 22. Matrixa wdrożenia

| Funkcja | Stan |
|---|---|
| TranslationOrchestrator | wdrożony/testowany |
| ChunkPlanner | wdrożony/testowany |
| Cancellation | wdrożone/testowane |
| Result/marker validation | wdrożone/testowane |
| TranslationCache | wdrożony, lifecycle do poprawy |
| DOCX | aktywny |
| ODT | aktywny |
| HTML/XHTML | aktywny |
| Markdown | aktywny |
| EPUB | aktywny |
| XLIFF | aktywny |
| TXT | brak aktywnego filtra |
| PDF | brak aktywnego filtra |
| llama.cpp | aktywny |
| TranslateGemma | kontrakt aktywny, brak pełnego E2E |
| Cloud | aktywny |
| Mozhi | aktywny |
| Custom | aktywny przez router |
| Apertium | niezamknięty release |
| Skills | aktywne |
| Glossary | aktywny |
| i18n PL/EN/DE | aktywne |
| Help | aktywna |
| Theme | aktywny |
| Windows | niezamknięty |
| Linux wheel | niezamknięty |
| Clean install gate | brak |
| CI gate | brak |

# 23. Priorytety

P0:
- Apertium runtime/data/relocation;
- aktualny wheel i packaging;
- build reproducibility.

P1:
- local/custom secrets;
- shutdown lifecycle;
- Ruff/mypy;
- TXT/PDF GUI contract;
- dependency/licence closure;
- Windows;
- CI;
- Git boundary;
- documentation current-state sync;
- packaging assets.

P2:
- QML cleanup;
- bridge decomposition;
- spacing/style tokens;
- skills refresh timer;
- accessibility;
- cleanup artefacts.

# 24. Konkluzja

Projekt ma wartościowy i stosunkowo dobrze przetestowany rdzeń. Problem nie leży obecnie przede wszystkim w algorytmie tłumaczenia, lecz w warstwie integracyjnej i release engineering.

Najważniejsza kolejność dalszych prac:
1. release integrity;
2. Apertium;
3. packaging;
4. secrets/lifecycle;
5. quality gates;
6. QML;
7. bridge decomposition;
8. documentation synchronization;
9. CI;
10. final release gate.

Nie rekomenduję rozpoczynania dużego rewrite'u. Najpierw należy usunąć blokery P0/P1 i dopiero potem przeprowadzić kontrolowaną refaktoryzację bridge/QML.


# 25. Audyt wiarygodności testów — 2026-10-05

Przeanalizowano wszystkie 57 modułów testowych znajdujących się w katalogu tests.

Inwentaryzacja:
- 57 plików testowych;
- 289 funkcji testowych wykrytych statycznie;
- 861 instrukcji assert;
- brak pytest.skip/xfail;
- brak klasycznych mocków/interakcyjnych asercji mocków;
- użycie monkeypatch jest skoncentrowane na granicach systemowych: HTTP, środowisko, Qt/offscreen oraz kontrolowane test doubles.

## Wynik audytu mutacyjnego

Wykonano kontrolowane mutacje kodu produkcyjnego i uruchomiono odpowiednie testy.

Wyniki:
- usunięcie walidacji języka źródłowego → test wykrywa błąd;
- usunięcie normalizacji suffixów FilterRegistry → testy wykrywają błąd;
- usunięcie ochrony przed duplikatem suffixu → test wykrywa błąd;
- usunięcie temperatury z klucza cache → test wykrywa błąd;
- zmiana zachowania kolejności TranslationExecutor → test wykrywa błąd;
- brak walidacji języka docelowego w ResultValidator → początkowo brak testu; dodano test regresyjny.

## Najważniejsze znalezisko

tests/test_apertium_e2e_documents.py używał kontrolowanego skryptu shell zamiast prawdziwego bundled runtime. Test był wartościowy jako test integracyjny pipeline'u z kontrolowanym procesem, ale nazwa E2E była zbyt mocna.

Testy zostały przemianowane, a do test_apertium_runtime.py dodano rzeczywisty release smoke test bundlowanego runtime'u.

Nowy test **wykrywa realny błąd produkcyjny**:
- executable Apertium 3.9.12 istnieje;
- data directory istnieje;
- runtime uruchamia się;
- liczba wykrytych par językowych = 0.

## Ocena pozostałych test doubles

Cloud provider tests używają stubu urlopen. Jest to prawidłowa granica testu jednostkowego protokołu HTTP: testują payload, URL, nagłówki i parsowanie odpowiedzi bez zależności od zewnętrznej sieci.

QML bridge tests patchują metody core, aby izolować zachowanie warstwy prezentacyjnej. Jest to akceptowalne, ale nie zastępuje pełnego GUI/E2E.

DocumentTranslationService posiada jeden test interakcyjny liczący wywołania orchestratora. Jest to uzasadnione jako kontrakt "jeden pass na dokument", ale powinien istnieć również test stanu końcowego dla reprezentatywnego dokumentu.

Packaging tests sprawdzają source tree i deklaracje pyproject, ale nie wykonują clean-wheel install. Jest to osobny blocker opisany jako BUG-033.

## Werdykt testów

Test suite nie wygląda na celowo skonstruowany tak, aby przepuszczać wadliwą implementację. Większość kluczowych testów przeszła próbę kontrolowanych mutacji.

Jednocześnie występował jeden istotny przypadek pozornej ochrony: Apertium "E2E" nie testował realnego runtime. Zostało to skorygowane.

Po korekcie pełny suite:
- 298 passed;
- 1 failed;
- failure jest oczekiwany i prawidłowy: nowy test wykrywa brak par językowych w bundled Apertium.

Stan release pozostaje czerwony z powodu Apertium.


# 26. Implementacja testów packaging i lifecycle — 2026-10-05

Zrealizowano wcześniej wskazane dwa brakujące obszary.

## Packaging

Dodano test test_wheel_builds_and_clean_target_imports_current_package.

Test:
1. tworzy czystą kopię source tree w katalogu tymczasowym;
2. buduje wheel z tej kopii;
3. sprawdza obecność QML, Apertium runtime i FilterHost w wheel;
4. instaluje wheel do tymczasowego targetu z --no-deps;
5. wykonuje import probe z tego targetu.

Test przeszedł: **1 passed**.

Zastosowanie czystej kopii source tree jest celowe: aktualny checkout nadrzędnego Git oraz istniejący katalog build/ mają problemy z ownership/ACL. Test nie omija problemu produkcyjnego — sprawdza rzeczywisty wheel z czystego źródła.

## Lifecycle

Dodano TranslationApp.close():
- zatrzymuje zarządzany llama.cpp;
- zamyka SQLite TranslationCache.

Dodano bind_application_lifecycle() w QML launcherze:
- QGuiApplication.aboutToQuit wywołuje TranslationApp.close().

Dodano pełny test:
test_full_gui_shutdown_closes_cache_and_llama_runtime.

Test wykorzystuje rzeczywisty LlamaCppRuntimeManager z kontrolowanym lokalnym procesem, rzeczywisty SQLite cache oraz prawdziwą pętlę zdarzeń Qt.

Focused verification:
**4 passed** dla packaging/lifecycle.

## Dodatkowe ustalenie testowe

W pełnym suite wykryto również historyczną nazwę właściwości w jednym teście QML. Implementacja używa restartLlamaAfterTranslation; test oczekiwał restartAfterTranslation. Test został zaktualizowany do aktualnego kontraktu.

## Aktualny pełny suite

**306 passed, 1 failed.**

Jedyny pozostały FAIL:
test_bundled_runtime_contains_language_data_for_release

Powód: bundled Apertium 3.9.12 wykrywa 0 par językowych.

To jest rzeczywisty blocker release, a nie problem testu.
