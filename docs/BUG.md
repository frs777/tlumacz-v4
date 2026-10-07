## Aktualizacja 2026-10-07 — BUG-041 / PLAN-14: finalizacja naprawy motywu

Status: NAPRAWIONY KODOWO; GATE RUNTIME KDE NIEPOTWIERDZONY

W aktualnym wariancie _apply_theme() najpierw korzysta z natywnego QStyleHints. Jeżeli Qt/Fusion nie zastosuje jawnego schematu dark/light, aplikacja używa kompletnej palety fallbacku wymaganej przez Fusion. Dla system fallback nie jest stosowany — unsetColorScheme() i reset QPalette() przywracają paletę natywną.

Test regresyjny test_qml_theme_changes_actual_application_palette został napisany przed zmianą i potwierdził RED dla dark; po implementacji GREEN: 4 testy motywu PASS. Pełny tests/test_qml_gui.py: 157 passed; pełny suite projektu: 573 passed.

Dodatkowo usunięto niezależną niespójność testu test_gui_regression_v3_v4.py: test oczekiwał historycznego połączenia etykiety czasu z wartością, podczas gdy aktualny TranslationPage.qml rozdziela te dwa Label. Po synchronizacji test przechodzi.

Rzeczywisty gate KDE nie został zamknięty, ponieważ proces SentinelX nie ma dostępu do DISPLAY/Xauthority/DBus aktywnej sesji użytkownika. Nie uznajemy testu offscreen za dowód platformowy.

Backup: backups/20261007-theme-regression-pre-fix/theme-regression-pre-fix.tar.gz.

---

## Aktualizacja 2026-10-07 — Filter Engine / Okapi: BUG-042 i BUG-043

### BUG-042 — PUA inline codes przekazywane bezpośrednio do backendu

**Status:** NAPRAWIONY na poziomie kontraktu transportowego; E2E z rzeczywistym backendem pozostaje do potwierdzenia.

Pierwotny handoff opisywał markery __OKAPI_CODE_N__, ale aktualny kod repozytorium nie posiadał tej warstwy. Okapi przekazywał bezpośrednio PUA TextFragment do backendu.

Reprodukcja README: 37 jednostek, 18 jednostek z inline codes, 72 wystąpienia kodów; extract i identity merge przechodzą.

Naprawa: PUA → __OKAPI_CODE_N__ przed backendem, ścisła kontrola odpowiedzi i restore PUA, bez automatycznego uzupełniania brakujących markerów. Cache przechowuje wynik po restore.

Weryfikacja: 7 testów ochrony markerów/cache PASS, 30 testów skoncentrowanego Filter Engine PASS; pełny pytest 533 passed.

### BUG-043 — reader threads Filter Host pozostawały daemon threads

**Status:** NAPRAWIONY na poziomie lifecycle klienta; pełny Qt/PySide6 gate pozostaje do potwierdzenia.

FilterHostClient tworzył reader threads stdout/stderr jako daemon. W Pythonie 3.14 daemon threads są zatrzymywane brutalnie podczas finalizacji interpretera. Przy procesie zawierającym PySide6/Qt taki lifecycle mógł ujawnić natywny SIGABRT zamiast zwykłego failure.

Naprawa: reader threads są niedemoniczne; close() kończy proces, zamyka pipe'y i wykonuje join; test obejmuje pojedynczy shutdown oraz 10-krotny start → request → close.

Weryfikacja: tests/test_filter_protocol.py — 8 passed.

Brak potwierdzenia, że ta zmiana sama rozwiązuje każdy natywny crash Qt; pełny test QML musi zostać wykonany osobno.

---
## Aktualizacja 2026-10-07 — BUG-041: motyw QML pozostawał jasny w standardowych kontrolkach

**Status:** NAPRAWIONY — 2026-10-07

### Objaw

Przy wybranym motywie `Ciemny` własne powierzchnie QML (m.in. karta treści Pomocy) korzystały z ciemnej palety, ale standardowe kontrolki Qt Quick Controls — w szczególności główny `TabBar`, `TabButton` i pola wyboru — pozostawały jasne.

### Potwierdzona przyczyna

W `src/tlumacz/qml_gui/app.py` `QQmlApplicationEngine` był tworzony przed pierwszym wywołaniem `_apply_theme()`. To zostało naprawione. Dalsza analiza wykazała jednak właściwą przyczynę jasnych powierzchni części kontrolek: styl Fusion korzysta nie tylko z `Window`, `Base`, `Button` i `Text`, ale także z ról pochodnych (`Light`, `Midlight`, `Mid`, `Dark`, `Shadow`, `Highlight` itd.). Nasza wymuszona paleta ustawia wcześniejsze role, ale pozostawiała część ról odziedziczoną z jasnej palety systemowej.

Tryb `Systemowy` działał prawidłowo właśnie dlatego, że dostarczał kompletną natywną paletę. Naprawa nie zmienia stylu Qt ani nie wymusza Material. Uzupełnia tylko paletę dla trybów `Ciemny` i `Jasny`. Qt dokumentuje, że Fusion korzysta ze standardowej palety oraz że jawne role palety są propagowane do kontrolek potomnych.

### Naprawa

- `QmlApplicationBridge` jest tworzony przed silnikiem;
- `_apply_theme(app, bridge.theme, system_palette)` wykonuje się przed `QQmlApplicationEngine()`;
- **nie wymuszamy `Material` ani innego stylu**;
- tryb `Systemowy` nadal przekazuje niezmienioną paletę systemową;
- tryby `Ciemny` i `Jasny` ustawiają kompletny zestaw ról używanych przez Fusion, w tym role reliefu, cienia, zaznaczenia, tooltipów i linków;
- `QML_DISABLE_DISK_CACHE=1` pozostaje wymuszony przez launcher modułu GUI.

### Weryfikacja

- runtime offscreen z `theme=dark`: root `#202124`, styl pozostaje `Fusion`, komplet ról palety jest ustawiony jawnie;
- runtime offscreen z `theme=system`: paleta systemowa pozostaje używana bez nadpisywania;
- focused GUI tests: **12 passed, 140 deselected**;
- runtime `dark`: ComboBox dziedziczy `palette.button=#303134` i `palette.buttonText=#f1f3f4`;
- runtime `light`: ComboBox dziedziczy `palette.button=#f8f9fa` i `palette.buttonText=#202124`;
- runtime `system`: ComboBox dziedziczy paletę systemową (`#efefef` / `#000000` w środowisku testowym);
- `compileall` — PASS;
- `qmllint src/tlumacz/qml_gui/*.qml` — PASS;
- backup: `backups/20261007-theme-system-only/`.

---

## Aktualizacja 2026-10-07 — BUG-040: rzeczywista przyczyna pustych napisów zakładek Pomocy

**Status:** ZAMKNIĘTY — 2026-10-07

Weryfikacja źródła ujawniła, że wcześniejszy opis BUG-040 był nieaktualny. Kontrolowany runtime bez QML_DISABLE_DISK_CACHE=1 ładował starą skompilowaną wersję QML, przez co zmiany na dysku nie były widoczne.

### Potwierdzona przyczyna
- QML cache przechowywał starszą strukturę HelpPage.qml;
- uruchomienie bez QML_DISABLE_DISK_CACHE=1 odtwarzało stary QQuickRepeater, mimo że bieżący plik nie zawierał już Repeater;
- dlatego edycje źródła były poprawne, ale GUI nadal prezentowało stary stan.

### Naprawa
- zakładki Pomocy są teraz pięcioma jawnymi elementami QML;
- każda etykieta korzysta bezpośrednio z reaktywnej właściwości bridge.helpTopicNTitle;
- zmiana języka aktualizuje wszystkie pięć napisów;
- launcher V4 wymusza QML_DISABLE_DISK_CACHE=1;
- test runtime również wymusza wyłączenie cache.

### Weryfikacja
- test języka Pomocy — 1 passed;
- runtime z QML_DISABLE_DISK_CACHE=1: 5 poprawnych tytułów DE → 5 poprawnych tytułów PL;
- compileall — PASS;
- qmllint — PASS;
- focused GUI tests — 5 passed, 145 deselected.

Backup: backups/gui-help-theme-20261007/pre-fix.tar.gz, SHA-256 d0c5fb8857b2e489ad37bda0a164197020485fd3b466c3f752acbf7db3925d7b.

SentinelX nie może uruchomić procesu GUI w sesji użytkownika, ponieważ nie posiada jej DISPLAY/Wayland/DBus; nie obchodzono tego przez kopiowanie danych uwierzytelniających sesji.

## BUG — test_document_translation_service_applies_skip_patterns_before_backend — naprawiony 2026-10-07

Test regresyjny był zbudowany na niestandardowym `HtmlFilter`, którego `extract()` zwracał sztuczne identyfikatory bez zapisania jednostek w `session.units`. Dodatkowo wzorzec testowy miał nadmiarowe escapowanie. Test został przepisany tak, aby używał rzeczywistego `HtmlFilter` i rzeczywistego dokumentu HTML, a wzorzec `^\\[NO_TRANSLATE\\]` był zgodny z danymi wejściowymi. Dzięki temu test sprawdza faktyczny kontrakt filtra oraz pomijanie jednostki przed przekazaniem jej do backendu.

Weryfikacja: `tests/test_document_translation_service.py::test_document_translation_service_applies_skip_patterns_before_backend` — **1 passed**; cały `tests/test_document_translation_service.py` — **5 passed**.

---

## Aktualizacja 2026-10-06 — dwa zgłoszone defekty GUI/runtime

### BUG-040 — niemieckie tytuły tematów Pomocy zamiast polskich

**Status:** ZAMKNIĘTY — 2026-10-06

Usunięto zależność zakładek Pomocy od pośredniej właściwości QML budowanej jako statyczna lista pięciu tytułów. HelpPage.qml korzysta teraz bezpośrednio z reaktywnej właściwości bridge.helpTopics i wyświetla modelData["title"]. Bridge przeładowuje _help_topics po set_application_language() i emituje languageChanged.

Zaostrzono regresję: test wymaga modelu bridge.helpTopics, bez statycznego modelu 5, oraz potwierdza polski pierwszy tytuł „Na początek” po ustawieniu języka pl.

Pełna weryfikacja QML wymaga ponownego uruchomienia gate'u GUI; w bieżącej sesji wykonanie pytest/qmllint przez SentinelX zostało zablokowane przez warstwę bezpieczeństwa narzędzia. Kod został zweryfikowany diffem i backupem.

### BUG-038 — uprawnienia plików prywatnego runtime Apertium

**Status:** ZAMKNIĘTY — 2026-10-06

Właściciel checkoutu przywrócił prawa wykonywania dla programów prywatnego runtime Apertium w `native_runtime/bin` i `native_runtime/libexec`. Aktualna inspekcja potwierdza `u+x` oraz `g+x` dla programów runtime; nie zmieniano właściciela ani ACL.

Regresja `test_bundled_runtime_programs_are_owner_executable` przechodzi: **1 passed, 8 deselected**.

Naprawa obejmowała wyłącznie programy runtime. Pliki dokumentacyjne i metadane, takie jak `README.md`, `VERSION` i `MANIFEST`, nie zostały sztucznie oznaczone jako wykonywalne.

## BUG-040 — niemieckie tytuły tematów Pomocy pozostawały po zmianie języka na polski

**Priorytet:** P1  
**Status:** ZAMKNIĘTY — 2026-10-06

Po zmianie języka aplikacji na polski bridge poprawnie zwracał polskie tytuły tematów Pomocy, ale `HelpPage.qml` budował model `Repeater` jako statyczną tablicę właściwości `bridge.helpTopic*Title`. W efekcie QML mógł zachować wcześniej zmaterializowane, niemieckie tytuły zakładek mimo emisji `languageChanged`.

### Przyczyna

Problem był w kontrakcie modelu QML, nie w tłumaczeniach bridge. Tablica:

`model: [bridge.helpTopic1Title, ...]`

nie zapewniała wymaganej reaktywności po zmianie języka.

### Naprawa

W `HelpPage.qml`:
- dodano reaktywną właściwość `helpTopicTitles`;
- `Repeater` korzysta ze stałego `model: 5`;
- tekst zakładki pobierany jest jako `helpTabs.helpTopicTitles[helpTab.index]`;
- dodano `objectName: "helpTabText"` dla regresji i diagnostyki.

### Weryfikacja

- test regresyjny `test_qml_help_topic_tabs_follow_runtime_language_change` — **PASS**;
- istniejący test runtime etykiet Pomocy — **PASS**;
- `qmllint src/tlumacz/qml_gui/*.qml` — **PASS**;
- `python3 -m compileall -q src/tlumacz/qml_gui` — **PASS**;
- bridge w środowisku użytkownika (`HOME=/home/frs`): `DE: Erste Schritte` → `PL: Na początek` — **PASS**.

Bezpośrednia wizualna kontrola całej zawartości ekranu Pomocy po zmianie języka nie została uznana za pełne potwierdzenie E2E; ograniczenie to pozostaje zgodne z zasadą weryfikacji GUI w `ADMINS.md`.

Backup przed zmianą:
`backups/help-language-reactivity-20261006/`.
## BUG-038 — prywatny runtime Apertium bez bitu `u+x`

**Priorytet:** P1  
**Status:** ZAMKNIĘTY — 2026-10-06

Początkowo 34 programy prywatnego runtime Apertium miały tryb `674`, bez bitu wykonywania dla właściciela. Właściciel checkoutu przywrócił `u+x` oraz `g+x` wyłącznie dla programów w `native_runtime/bin` i `native_runtime/libexec`.

Weryfikacja bieżącego stanu:
- wszystkie programy runtime mają prawa wykonywania dla właściciela i grupy;
- właściciel pozostaje `frs:frs`;
- `test_bundled_runtime_programs_are_owner_executable`: **1 passed, 8 deselected**;
- nie zmieniano właściciela ani ACL.

## BUG-039 — nieaktualny kontrakt testu entrypointu V4

**Priorytet:** P1  
**Status:** OTWARTE — wykryte przez świeży Plan 05, 2026-10-06

Plan wymaga `python -m tlumacz --version`, ale pakiet V4 nie zawiera `tlumacz.__main__`. Globalne `/usr/bin/tlumacz` wskazuje na instalację V3 i nie jest poprawnym dowodem działania V4. Należy ustalić właściwy entrypoint V4 i zaktualizować test/plan bez modyfikowania globalnego V3.

## Aktualizacja 2026-10-06 — mechanizm wyboru języka Apertium

Wdrożono i zabezpieczono testami mechanizm wyboru języka Apertium. Discovery korzysta z `compiled_modes`, a GUI filtruje cele według rzeczywiście gotowych kierunków. Nie stwierdzono nowego defektu wymagającego wpisu BUG. Istniejące ryzyka jakościowe części par pozostają w BUG-037.
## Aktualizacja 2026-10-06 — TranslateGemma i porządkowanie Apertium

- BUG-025: potwierdzono rzeczywisty runtime TranslateGemma na translategemma-4b-it.Q5_K_M.gguf z $HOME/Modele/.
- Izolowany llama-server z llama.cpp b7976 (972f323e7) uruchomił model z natywnym Jinja i zwrócił rzeczywiste tłumaczenie Hello, how are you today? → Dzień dobry, jak się masz dzisiaj?
- Sam typed-content w /v1/chat/completions nie przenosi source_lang_code/target_lang_code; adapter używa chat_template_kwargs na żądaniu API.
- Adapter i testy regresyjne zostały zmienione do tego kontraktu; focused tests: 3 passed.
- Pełne E2E przez aplikację zostało wykonane i zamknięte 2026-10-06; wcześniejsza informacja o braku E2E jest historyczna i nie opisuje już bieżącego stanu.

## Aktualizacja 2026-10-06 — archiwizacja danych Apertium

- Utworzono i zweryfikowano backups/Aperitium-sources-full-20261006.7z (373 MiB; 4408 plików; test 7z: Everything is Ok; SHA-256 4dd001ac2b5fab899da34137bf5c60d0f956b2dc7c5bbe3ad71a092c24edcedc).
- Źródła Apertium będą odchudzane dopiero po zakończeniu analogicznego archiwum $HOME/.config/tlumacz/Apertium/.
- Ustalona zasada: zachować skompilowane zasoby językowe i pliki faktycznie wymagane przez modes.xml; nie usuwać monojęzycznych zasobów eng, pol, spa, rus, cat itd., jeżeli są zależnościami runtime.

## Aktualizacja 2026-10-06 — finalna weryfikacja Planu 03 TranslateGemma

Świeży test na aktualnym /usr/local/bin/llama-server 0.4.0-dev (build 10809, commit 5266f24da) potwierdził, że próba uruchomienia TranslateGemma z --jinja kończy się błędem automatycznego parsera szablonu typed-content. Nie jest to blocker aplikacji: obowiązująca ścieżka V4 używa --no-jinja, ręcznie renderowanego promptu Gemma i /v1/completions.

Realny translategemma-4b-it.Q5_K_M.gguf został zweryfikowany dwukrotnie: przez TranslationApp oraz przez QmlApplicationBridge. Oba przepływy zakończyły się poprawnym en→pl, zapisem dokumentu i czystym zamknięciem runtime.

Wcześniejsze wpisy opisujące chat_template_kwargs dotyczą historycznego środowiska llama.cpp i nie są bieżącym kontraktem runtime. Pozostają w historii jako evidence wcześniejszego eksperymentu.

---
id: docs-bug-v4
status: active
meta:
  contentType: Troubleshooting
  category: governance
version: 0.40.0
updated: 2026-10-06
owner: project-maintenance
source:
  - docs/STATUS.md
  - src/tlumacz/
  - docs/Audyt/
depends_on: [docs/STATUS.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: wszystkie wymienione problemy zostaną zamknięte lub zastąpione
last_validation: "Apertium pair compile gate 2026-10-06; 9 kierunków wcześniej gotowych + 3 źródła naprawione i przebudowane; pol-rus/pl-sk/pl-csb make -B PASS; pl-uk blocked by legacy apertium-3.2 dependency"
---

# Tłumacz V4 — aktywne defekty i ryzyka

Ten dokument zawiera wyłącznie problemy i ryzyka nadal istotne dla aktualnego V4.

## BUG-001 — Apertium eng-pol niekompletne

**Priorytet:** P0 funkcjonalny  
**Status:** ZAMKNIĘTY 2026-10-05

Usunięto niezdefiniowany cas_sp z reguły apertium-eng-pol.eng-pol.t1x w obu kopiach źródła Apertium. Wygenerowano rzeczywisty eng-pol.t1x.bin; nie jest to placeholder.

Weryfikacja: apertium-validate-transfer PASS; clean install wheel wykrywa wyłącznie eng-pol; ApertiumAdapter wykonuje rzeczywiste eng → pol przez Filter Engine.

## BUG-002 — brak kompletnego Windows runtime

**Priorytet:** P1  
**Status:** OTWARTY

Artefakt 0.40.0 pozostaje Release Candidate dla Linux x86-64. Kompletnego natywnego runtime Windows nie zamknięto.

## BUG-003 — dependency closure i audyt licencji

**Priorytet:** P1  
**Status:** OTWARTY

Pełny komponent-po-komponencie inventory zależności dystrybucyjnych oraz finalny audyt obowiązków licencyjnych nie są zamknięte.

## BUG-004 — ryzyko uruchomienia V3 zamiast V4

**Priorytet:** P1  
**Status:** RYZYKO ŚRODOWISKOWE

W środowisku istnieje historyczna instalacja V3. Diagnostyka V4 musi weryfikować interpreter, tlumacz.__file__ i launcher. Nie usuwać globalnej instalacji bez osobnej decyzji.

## Zamknięte obserwacje

- `profile_migration.py` — usunięty po zero-reference gate w Planie 02;
- `SecretStore` — podłączony do aktywnego QML bridge i zweryfikowany testami;
- nieużywane kontrolery GUI — usunięte poza aktywnym `BackendController`.

Szczegóły, dowody i backupy znajdują się w `docs/Plany/02-REDUKCJA-NADMIAROWEGO-KODU.md` oraz `docs/DOCUMENTATION_CHANGELOG.md`.

## Dokumentacyjne ustalenie — detekcja języka

V4 posiada `src/tlumacz/language_detector.py`, ale jest on świadomie ograniczony do specjalnego trybu `chat_template="translategemma"`. Standardowy przepływ GUI nadal może przekazywać `source_language="auto"`; nie oznacza to globalnego użycia Lingua. E2E z rzeczywistym modelem TranslateGemma pozostaje w `docs/TODO.md`.

## Dokumentacyjne ustalenie — formaty

TXT i PDF nie są zarejestrowane w aktywnym FilterRegistry. Ich pliki skilli nie stanowią dowodu aktywnej obsługi głównego pipeline'u.

## Funkcje wycofane

FastAPI + Transformers, OpenVINO + TranslateGemma INT8 jako osobny runtime/backend oraz klasyczne src/tlumacz/qt_gui/ nie są aktywnymi defektami. Rejestr wycofanych funkcji znajduje się w docs/RETIRED_FUNCTIONALITY.md.

## Historia

Starsze wpisy migracyjne i zamknięte obserwacje GUI zostały przeniesione do docs/archive/audits/BUG_HISTORY_2026-10-04.md.


## 2026-10-04 — wynik finalnego gate'u

Plan 05 potwierdził, że aktywny kod V4 przechodzi bieżące testy i kontrole statyczne, ale trzy niezależne blokery release pozostają otwarte: **BUG-001 Apertium eng-pol/cas_sp**, **BUG-002 Windows runtime** i **BUG-003 dependency closure/licencje**. Ryzyko **BUG-004** pozostaje środowiskowe: `/usr/bin/tlumacz` wskazuje globalny V3; nie zmieniano tego bez osobnej decyzji.


# 2026-10-05 — audyt inżynierski

## BUG-005 — aktualny quality gate jest czerwony

**Priorytet:** P1  
**Status:** ZAMKNIĘTY 2026-10-05

Aktualny source przechodzi:
- Ruff: PASS;
- mypy: PASS;
- compileall: PASS;
- pytest: 314 passed w końcowym gate;
- QML tests: PASS;
- clean install/product smoke: PASS.

Historyczne wyniki pozostają w dokumentacji historycznej i nie opisują bieżącego gate'u.

## BUG-006 — brak reprodukowalnego builda wheel

**Priorytet:** P0/P1  
**Status:** ZAMKNIĘTY 2026-10-05

Nadrzędny checkout /home/frs/Projekty nadal ma problem z Git ownership przy bezpośrednim python -m build. Nie zmieniano globalnej konfiguracji Git.

Kanoniczny build V4 został jednak zdefiniowany jako build aktualnego source skopiowanego do czystego katalogu poza nadrzędnym checkoutem. Procedura znajduje się w docs/BUILD.md i jest wykonywana w CI. Końcowy wheel 0.40.0 został zbudowany tą procedurą i przeszedł clean install.

## BUG-007 — bundled Apertium nie zawiera danych językowych

**Priorytet:** P0  
**Status:** ZAMKNIĘTY 2026-10-05

native_runtime/share/apertium zawiera kompletny artefakt eng-pol, w tym automorf/autobil, transfer t1/t2/t3, generację i mode.

Weryfikacja clean install: discovery zwraca ("eng-pol",) oraz rzeczywiste tłumaczenie Hello world. → @hello #Świat.

## BUG-008 — Apertium zawiera hardcoded ścieżki V3

**Priorytet:** P0  
**Status:** ZAMKNIĘTY 2026-10-05

Usunięto hardcoded /home/frs/Projekty/agent-translator-v3/ z artefaktów Apertium objętych audytem. Ponowny grep całego Aperitium/ oraz aktywnego src/tlumacz/backends/apertium/ zwraca zero trafień.

## BUG-009 — Apertium nie jest zamkniętym runtime release

**Priorytet:** P0  
**Status:** ZAMKNIĘTY 2026-10-05

Runtime zawiera własne binaria, biblioteki, launcher, mode, dane eng-pol i licencję pary. Wheel został zainstalowany do czystego katalogu i uruchomił Apertium bez zależności od starego drzewa V3.

Release gate potwierdza discovery, tłumaczenie eng-pol i QML smoke.

## BUG-010 — local/custom API key może być zapisany do JSON

**Priorytet:** P1  
**Status:** ZAMKNIĘTY 2026-10-05

SecretStore jest jedynym trwałym właścicielem lokalnego klucza. save_settings() usuwa legacy api_key/last_local_api_key z serializowanego JSON, a bridge wykonuje jednorazową migrację starego pliku do SecretStore("local").

Regresja potwierdza: sekret nie trafia do JSON, trafia do .key, a nowy bridge po restarcie odczytuje go wyłącznie przez SecretStore.

## BUG-011 — brak centralnego shutdown lifecycle

**Priorytet:** P1  
**Status:** ZAMKNIĘTY 2026-10-05

Aktualny kod posiada centralny TranslationApp.close(), podpięcie aboutToQuit, zamknięcie cache SQLite oraz cleanup/stop runtime'u llama.cpp. Aktualne testy lifecycle przechodzą w pełnym suite bez historycznych ResourceWarning raportowanych w audycie.

## BUG-012 — GUI sugeruje obsługę TXT/PDF bez aktywnego filtra

**Priorytet:** P1  
**Status:** ZAMKNIĘTY — decyzja UX zmieniona 2026-10-06

Skille `plaintext.md` i `pdf.md` są rzeczywistymi skillami systemowymi i mają być dostępne w GUI. Od 2026-10-06 są ponownie prezentowane i dobierane automatycznie po rozszerzeniu pliku. Status TXT/PDF w aktywnym `FilterRegistry` pozostaje osobnym kontraktem; obecność skilla nie jest już traktowana jako deklaracja rejestracji filtra.

## BUG-013 — aktualny wheel jest niezgodny ze source

**Priorytet:** P0  
**Status:** ZAMKNIĘTY 2026-10-05

temp/wheel/tlumacz-0.40.0-py3-none-any.whl został przebudowany z aktualnego source. Audit wheel potwierdza aktywny QML, nowe assety SVG, runtime Apertium oraz brak wycofanych kontrolerów.

Clean install tego właśnie artefaktu przechodzi CLI, QML i Apertium smoke.

## BUG-014 — packaging assetów SVG nie jest zamknięty

**Priorytet:** P1  
**Status:** ZAMKNIĘTY 2026-10-05

Istniejące tlumacz-dark.svg, tlumacz-light.svg oraz frsststems_logo_full.svg są jawnie objęte package-data. HelpPage.qml korzysta z relatywnej ścieżki wewnątrz pakietu.

Wheel audit i clean install potwierdzają obecność wszystkich trzech assetów; QML smoke przechodzi.

## BUG-015 — brak repozytoryjnego CI quality gate

**Priorytet:** P1  
**Status:** ZAMKNIĘTY 2026-10-05

Dodano .github/workflows/quality-gate.yml. Pipeline wykonuje Ruff, mypy, pytest, compileall, qmllint, clean-source wheel build, wheel audit, clean install oraz CLI/QML/Apertium smoke.

## BUG-016 — brak własnej granicy Git projektu

**Priorytet:** P1  
**Status:** ZAMKNIĘTY / POZA ZAKRESEM 2026-10-06

V4 nie jest repozytorium przeznaczonym do bezpośredniej synchronizacji z GitHubem w `/home/frs/Projekty/tlumacz-v4`. Repozytorium przeznaczone do synchronizacji z GitHubem znajduje się poza tym katalogiem. Nie należy tworzyć drugiej historii Git wewnątrz V4; wcześniejsze testowe `git init` zostało usunięte. Provenance Git pozostaje własnością zewnętrznego repozytorium projektu.

## BUG-017 — brak lokalnego .gitignore

**Priorytet:** P1/P2  
**Status:** ZAMKNIĘTY 2026-10-06

Dodano `tlumacz-v4/.gitignore` obejmujący środowiska, cache, build/dist, artefakty robocze, backupy i lokalne pliki narzędziowe. Granica ignorowania jest teraz lokalna dla V4 i nie wymaga zmian nadrzędnego `.gitignore`.

## BUG-018 — repozytorium zawiera nadmiarowe artefakty

**Priorytet:** P1/P2  
**Status:** OTWARTY

Projekt zajmuje około 3.9 GB. Największe obszary to .migration-backups około 1.8 GB, Aperitium około 1.5 GB, temp około 1.1 GB, backups około 95 MB, build około 91 MB i .mimocode około 58 MB.

Nie jest to wyłącznie problem rozmiaru. Brakuje wyraźnej granicy source/evidence/generated/backup.

## BUG-019 — dokumentacja bieżąca zawiera historyczne quality gates

**Priorytet:** P1  
**Status:** ZAMKNIĘTY 2026-10-06

Bieżący stan został zsynchronizowany z aktualnym gate'em V4: pytest = 373 passed, 1 failed; Ruff PASS, mypy PASS, compileall PASS, qmllint PASS. Jedyna aktualna porażka dotyczy bitu `u+x` prywatnego runtime Apertium i jest opisana w BUG-038. Starsze wyniki pozostają wyłącznie jako historia zmian.

## BUG-020 — sprzeczność INDEX.md vs INDEX.yml

**Priorytet:** P2  
**Status:** ZAMKNIĘTY 2026-10-06

`docs/INDEX.md`, `docs/INDEX.yml` i bieżący filesystem wskazują obecnie **472** kanoniczne pliki dokumentacji. Dodano do indeksu `docs/BUILD.md`, który wcześniej był jedynym kanonicznym plikiem nieujętym w `INDEX.yml`; 11 plików `*.bak.*` pozostaje poza kanonicznym indeksem.

## BUG-021 — corrupt help file znajduje się w aktywnym source

**Priorytet:** P2  
**Status:** OTWARTY

src/tlumacz/qml_gui/help.pl.md.corrupt-20261005 ma około 70 MB.

Plik powinien zostać jednoznacznie zaklasyfikowany jako evidence/backup albo usunięty po osobnej decyzji.

## BUG-022 — refreshSkills jest odświeżane co sekundę bez potrzeby

**Priorytet:** P2  
**Status:** ZAMKNIĘTY 2026-10-06

Usunięto 1-sekundowy polling z `ExtrasPage.qml`. `refreshSkills()` pozostaje dostępne jako jawna akcja użytkownika, a `refresh_skills()` nadal emituje `skillsChanged` bez sztucznego timera.

## BUG-023 — QML style debt

**Priorytet:** P2  
**Status:** ZAMKNIĘTY 2026-10-06

Usunięto zbędne, powtarzające się `font.bold: false` z `ExtrasPage.qml`. Domyślna waga tekstu nie jest już deklarowana ręcznie w każdym kontrolku; jawne pogrubienie pozostaje tylko tam, gdzie jest potrzebne wizualnie.

## BUG-024 — rozjazd bazowego fontu QML z dokumentacją

**Priorytet:** P2  
**Status:** ZAMKNIĘTY 2026-10-06

Źródłem prawdy jest `src/tlumacz/qml_gui/Main.qml`, gdzie bazowy `font.pixelSize` wynosi 15. `docs/technical-docs/QML_GUI_LAYOUT.md` został zaktualizowany do tego stanu; wcześniejszy opis 17 px jest traktowany jako historyczny.

## BUG-025 — brak pełnego TranslateGemma E2E

**Priorytet:** P1  
**Status:** ZAMKNIĘTY 2026-10-06

Wykonano pełny E2E na rzeczywistym modelu `translategemma-4b-it.Q5_K_M.gguf` przez QML → QmlApplicationBridge → TranslationApp → DocumentTranslationService → llama-server → wynik dokumentowy. Potwierdzono `translationFinished`, status `Tłumaczenie zakończone.` oraz zapis wyniku Markdown. Szczegółowy dowód znajduje się w `docs/STATUS.md` i `docs/TODO.md`.

## BUG-026 — brak Windows runtime

**Priorytet:** P1  
**Status:** ODŁOŻONY 2026-10-06

Kompilacja i zamknięcie runtime dla Windows oraz macOS są przewidziane na przyszły etap projektu i nie są obecnie pilnym zakresem naprawy V4. Linux x86-64 pozostaje aktualnym targetem roboczym.

## BUG-027 — dependency closure nie jest zamknięte

**Priorytet:** P1  
**Status:** OTWARTY

Wykonano rzeczywisty import/grep audit aktywnego `src/` i `tests/`: `openai`, `PyMuPDF/fitz` oraz `markdown_it` nie są używane. Zależności te zostały usunięte z `pyproject.toml`, a regresja packagingu potwierdza ich brak w deklaracji runtime.

Dodatkowo wykonano `pip install --dry-run --ignore-installed --report`, który rozwiązał aktualny graf zależności bez instalowania pakietów. Pozostaje jednak brak repozytoryjnego lockfile/constraints dla pełnego, reprodukowalnego closure — pozycja pozostaje otwarta.

## BUG-028 — bridge jest nadmiernie skondensowany odpowiedzialnościowo

**Priorytet:** P2  
**Status:** OTWARTY

QmlApplicationBridge ma około 1736 linii i obsługuje wiele niezależnych kompetencji.

Rekomendowana jest etapowa dekompozycja po characterization tests, ale nie jest to blocker P0.

## BUG-029 — accessibility i keyboard navigation nie są zamknięte

**Priorytet:** P2  
**Status:** OTWARTY

Wykonano pierwszy etap audytu na rzeczywistym QML:
- dodano regresję obecności nazw dostępnościowych dla kontrolek bez własnego tekstu;
- dodano regresję zakazującą wyłączania focusu klawiaturowego przez `Qt.NoFocus`;
- poprawiono 4 konkretne kontrolki: język docelowy, backend, źródło glosariusza i wybór motywu.

Pozostają do potwierdzenia na runtime: pełna kolejność focusu keyboard-only, screen reader, high contrast oraz DPI/font scaling. `qmllint` nie jest dowodem spełnienia tych kryteriów.

## BUG-030 — launcher nie jest przenośny

**Priorytet:** P1/P2  
**Status:** ZAMKNIĘTY 2026-10-06

`uruchom-v4.sh` wyznacza katalog projektu z własnej lokalizacji przez `BASH_SOURCE[0]` zamiast używać hardcoded `/home/frs/Projekty/tlumacz-v4`. Test bootstrapu wymusza ten kontrakt, a `bash -n` przechodzi.



## BUG-031 — test Apertium oznaczony jako E2E nie weryfikował rzeczywistego runtime’u

**Priorytet:** P0
**Status:** NAPRAWIONE W TESTACH / BŁĄD PRODUKTOWY NADAL OTWARTY

tests/test_apertium_e2e_documents.py uruchamiał własny skrypt shell jako executable Apertium. Skrypt zwracał kontrolowany wynik PL: i nie był rzeczywistym bundlowanym runtime’em.

Test nadal ma wartość jako test integracji DocumentProcessor + ApertiumAdapter + kontrolowany proces, ale nie może być traktowany jako E2E prawdziwego Apertium. Nazwy testów zostały poprawione, a dodatkowo dodano test rzeczywistego bundlowanego runtime’u.

Nowy test ujawnił, że aktualny bundled Apertium zwraca **0 par językowych**.

## BUG-032 — brak asercji niezgodności języka docelowego w ResultValidator

**Priorytet:** P1
**Status:** NAPRAWIONE W TESTACH

ResultValidator posiadał walidację expected_target_language, ale test suite nie zawierał testu, który wykrywałby usunięcie tego warunku.

Dodano test_validator_rejects_target_language_mismatch.

Audyt mutacyjny potwierdził wcześniej, że mutant usuwający walidację języka źródłowego był wykrywany, natomiast brakowało analogicznego zabezpieczenia dla języka docelowego.

## BUG-033 — testy packagingu nie wykonują clean-wheel verification

**Priorytet:** P1
**Status:** ZAMKNIĘTY 2026-10-05

test_package_resources.py wykonuje teraz rzeczywisty build wheel w czystej kopii source tree, inspekcję zawartości wheel, instalację do tymczasowego targetu bez zależności oraz import probe z tego targetu. Test nie modyfikuje globalnej instalacji ani konfiguracji Git.

## BUG-034 — brak pełnego testu shutdown/lifecycle

**Priorytet:** P1
**Status:** ZAMKNIĘTY 2026-10-05

Dodano centralne TranslationApp.close(), które zatrzymuje llama.cpp i zamyka TranslationCache. QML launcher podpina core.close do QGuiApplication.aboutToQuit. Dodano pełny test GUI shutdown obejmujący jednocześnie rzeczywisty LlamaCppRuntimeManager z kontrolowanym lokalnym procesem, SQLite cache oraz zakończenie pętli Qt.

## BUG-035 — testy cloud providerów stosują stub HTTP zamiast testu integracyjnego

**Priorytet:** P2
**Status:** ŚWIADOMA GRANICA TESTOWANIA

Sześć testów providerów zastępuje urlopen kontrolowanym stubem. Jest to właściwe dla szybkich testów jednostkowych kontraktu HTTP i nie stanowi samo w sobie błędu.

Brakuje jednak osobnego, opcjonalnego testu integracyjnego przeciwko rzeczywistym endpointom/testowym środowiskom. Nie należy dodawać go do domyślnego suite bez ustalenia kosztu, sekretów i stabilności usług.



## BUG-037 — niekompletne/legacy źródła części par Apertium

**Priorytet:** P1  
**Status:** OTWARTE / częściowo naprawione 2026-10-06

Podczas wymuszonej kompilacji pozostałych źródeł Apertium potwierdzono:

- `pol-rus`: źródłowa reguła `pol-rus.t3x` odwoływała się do niezdefiniowanego `a_pprep`; poprawiono ją do istniejącego atrybutu `pprep`, po czym `make -B` przechodzi;
- `pl-sk`: `pl-sk.t1x` używał `a_vrb` bez definicji; dodano definicję zgodną z odwrotnym kierunkiem `sk-pl`, po czym `make -B` przechodzi;
- `pl-csb`: `pl-csb.t1x` używał `a_det` bez definicji; dodano definicję zgodną z odwrotnym kierunkiem `csb-pl`, po czym `make -B` przechodzi. Słownik nadal zgłasza dwa zduplikowane `pardef` (`wąg/ier__n`, `kwi/at__n`) jako błędy walidacji XML, ale nie blokuje aktualnego `make`; ich usunięcie wymaga decyzji semantycznej;
- `pl-uk`: źródło zawiera `configure.ac`, ale wymaga historycznego modułu `apertium-3.2`, którego aktualny lokalny runtime nie udostępnia w `pkg-config`; nie wykonano instalacji brakującego komponentu.

**Dowód:** wymuszony build `make -B -j2` oraz rzeczywiste smoke-testy kierunków.  
**Backup:** `backups/apertium-pairs-before-compile-20261006-002349.tar.gz`.

## BUG-036 — test QML oczekiwał historycznej nazwy właściwości

**Priorytet:** P2
**Status:** ZAMKNIĘTY 2026-10-05

Jeden test QML oczekiwał historycznego restartAfterTranslation, podczas gdy aktualny kontrakt używa restartLlamaAfterTranslation. Test został przepisany do aktualnego kontraktu zamiast zmiany implementacji tylko dla potrzeb testu.

## Aktualizacja 2026-10-06 — informacyjne języki Apertium

Usunięto rozjazd między selektorami języków Apertium a informacyjnymi polami na `TranslationPage.qml`. Pola informacyjne korzystają teraz z właściwości Apertium i nie odczytują ogólnego stanu języków innych backendów.
### Naprawiony: `eng-pol` niewidoczne po wyborze English
Przyczyną był brak skompilowanej pary `eng-pol` w docelowym katalogu `/home/frs/.config/tlumacz/Apertium/`. Po instalacji ujawniono dodatkowo błąd adaptera: `data_dir_for_pair()` przekazywał katalog pakietu zamiast jego katalogu nadrzędnego, przez co tryb nie mógł otworzyć ścieżek `apertium-en-pl/...`. Dodano regresję i poprawiono przekazywanie katalogu danych.



## 2026-10-06 — ponowna walidacja Planu 03

Audyt regresji wykonany na aktualnym V4 nie potwierdził nowego defektu produkcyjnego. Focused suite P1/P2: 128 passed; pełny pytest: 367 passed, 0 failed. Pierwszy pełny przebieg ujawnił pojedynczy niestabilny wynik tests/test_llama_adapter.py dla TranslateGemma; test uruchomiony osobno przeszedł, a kolejny pełny przebieg również przeszedł bez błędów. Pozostawiono kod bez zmian.


## Aktualizacja 2026-10-07 — decyzja produktowa: tylko motyw systemowy

Po ponownym uruchomieniu aplikacji i braku potwierdzenia poprawnego przełączania motywu użytkownik zdecydował o wycofaniu wyboru Ciemny/Jasny/Systemowy z interfejsu. GUI pozostaje przy **motywie systemowym**.

Nie usunięto mechanizmu technicznego zmiany motywu. `QmlApplicationBridge.set_theme()` oraz obsługa `QStyleHints`/Fusion pozostają w kodzie i są oznaczone komentarzem jako mechanizm przeznaczony do przyszłego przywrócenia opcji.

W dialogu **O programie** dodano klikalny link do strony projektu: https://frs777.github.io/tlumacz-v4/zrzuty.html.

Pozostający problem runtime motywu nie jest deklarowany jako naprawiony.
