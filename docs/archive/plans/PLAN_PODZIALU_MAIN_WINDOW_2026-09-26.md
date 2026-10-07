# STATUS DOKUMENTU: HISTORYCZNY / SUPERSEDED

> Plan został napisany przed ukończeniem migracji i nie jest aktualną instrukcją dla V4. Zapis „FastAPI/OpenVINO pozostają zachowane” jest historycznym założeniem V3/V4 i jest zastąpiony przez decyzję końcową: **FastAPI i OpenVINO nie są aktywnymi backendami V4 i nie wolno ich reaktywować na podstawie tego dokumentu.**

# [PLAN] [ARCHITEKTURA] [TDD] [NO-DELETE] [NO-INSTALL] [BACKUP-PRZED-DUŻYM-REFAKTOREM]

## Plan rozdzielenia tlumacz/qt_gui/main_window.py

**Data:** 2026-09-26  
**Status:** PLAN — analiza zakończona, implementacja nierozpoczęta  
**Zakres:** przygotowanie bezpiecznego podziału MainWindow.

> Ten dokument jest planem. Nie oznacza zgody na wykonanie refaktoru. Backendów FastAPI/OpenVINO nie usuwamy. Pozostają zachowane i poza aktywną ścieżką migracji, jeżeli nie zostanie podjęta osobna decyzja.

---

## 1. Oznaczenia i zasady

- [P0] — blokada bezpieczeństwa/architektury.
- [P1] — wymagane przed zakończeniem etapu.
- [P2] — ważne, ale może zostać wykonane później.
- [SAFE] — zachować istniejące zachowanie.
- [TDD] — najpierw test regresyjny, potem implementacja.
- [BACKUP] — backup przed dużym refaktorem.
- [NO-DELETE] — niczego nie usuwać tylko dlatego, że nie jest migrowane.
- [NO-INSTALL] — nie instalować ani usuwać zależności bez osobnej zgody.
- [DOCS] — po każdym wykonanym etapie aktualizować dokumentację.
- [VERIFY] — etap kończy się świeżą weryfikacją.

### Zasady nadrzędne

1. MainWindow ma docelowo być przede wszystkim kompozytorem GUI i właścicielem widoku.
2. Logika domenowa, konfiguracja, lifecycle backendu i lifecycle tłumaczenia nie powinny mieszkać w jednym oknie.
3. Nie zmieniać kontraktów Translator, BackendManager, ServerManager ani istniejących backendów tylko po to, aby ułatwić refaktor.
4. Każde wydzielenie odpowiedzialności musi mieć test zabezpieczający zachowanie.
5. Nie wykonywać big-bang refaktoru.
6. Nie łączyć dużego podziału GUI ze zmianą zachowania tłumaczenia.
7. Przy dużej zmianie wykonać backup przed modyfikacją.

---

## 2. Stan obecny

Analiza pliku wykazała:

- klasa MainWindow: około 2387 linii,
- ponad 60 metod,
- wiele niezależnych odpowiedzialności w jednym obiekcie,
- współdzielony stan pomiędzy GUI, konfiguracją, backendami i tłumaczeniem.

Najważniejsze pola współdzielonego stanu:

- self._settings,
- self._backend_manager,
- self._server_manager,
- pola widgetów,
- self._loading,
- self._switching_backend,
- self._pending_backend_start,
- self._thread.

To oznacza, że problemem nie jest tylko rozmiar pliku. Problemem jest sprzężenie stanu i efektów ubocznych.

---

## 3. Zidentyfikowane odpowiedzialności

### A. Budowa i prezentacja GUI

Metody:

- _build_ui
- _build_files_group
- _build_api_group
- _build_server_group
- _build_other_group
- _build_glossary_group
- _build_skills_group
- _build_help_tab
- _show_about_dialog
- _refresh_ui_texts
- _update_server_fields_visibility

### B. Konfiguracja

Metody:

- _active_api_key
- _build_config
- _collect_settings
- _load_settings_into_ui
- _build_config_updates

To jest jeden z najważniejszych obszarów do wydzielenia, ponieważ obsługuje jednocześnie GUI, AppSettings, TranslatorConfig, profile Cloud i ustawienia lokalne.

### C. Lifecycle backendów

Metody:

- _create_backend_manager
- _build_server_config
- _on_server_started
- _on_server_stopped
- _start_selected_backend
- _on_server_error
- _on_operation_finished
- _on_backend_loading
- _show_loading_dialog
- _close_loading_dialog
- _set_backend_controls_enabled
- _on_model_changed
- _on_restart_server
- _maybe_restart_after_translation
- _ensure_server_after_cancel

### D. Lifecycle tłumaczenia

Metody:

- _on_translate
- _on_cancel
- _on_progress
- _on_finished
- _on_failed
- _clear_finished_thread

TranslationThread już istnieje w worker.py i nie należy budować drugiego mechanizmu workerów.

### E. Pliki i podgląd

Metody:

- _browse_file
- _browse_directory
- _on_browse_input
- _on_browse_output
- _on_browse_model
- _show_preview

### F. Skille

Metody:

- _reload_skills
- _on_refresh_skills
- _on_import_skill
- _on_new_skill
- _enabled_skill_names
- _skip_pattern_list
- _on_skills_changed
- _auto_select_skill_for_input

### G. Glosariusz

Metody:

- _refresh_glossary_count
- _on_glossary_path_edited
- _on_add_glossary_entry
- _on_browse_glossary

### H. Mozhi

Osobny worker MozhiHealthWorker oraz:

- _on_cloud_model_changed
- _on_mozhi_instance_changed
- _on_mozhi_engine_changed
- _start_mozhi_health_check
- _on_mozhi_health_finished

### I. Runtime GUI

- logowanie do widoku,
- timer i elapsed time,
- spinner,
- idle/running state,
- język,
- motyw,
- closeEvent.

---

## 4. Docelowe granice modułów

Nie tworzyć kilkunastu mikromodułów. Pierwszy refaktor powinien zakończyć się około 5–7 sensownymi granicami.

### 4.1 MainWindow

Rola docelowa:

- kompozycja okna,
- połączenie sygnałów,
- delegowanie zdarzeń,
- podstawowy stan widoku,
- lifecycle Qt.

Cel orientacyjny: około 500–900 linii, ale liczba linii NIE jest kryterium akceptacji.

### 4.2 translation_controller.py

Odpowiedzialność:

- start tłumaczenia,
- utworzenie TranslationThread,
- progress/log/finished/failed,
- cancel,
- cleanup,
- walidacja ścieżek na poziomie GUI.

Nie zna szczegółów layoutu zakładek.

### 4.3 backend_controller.py

Odpowiedzialność:

- start/stop/restart,
- przełączanie backendów,
- pending backend,
- loading/error,
- recovery po anulowaniu.

Wykorzystuje istniejący BackendManager i ServerManager.

### 4.4 settings_controller.py

Odpowiedzialność:

- mapowanie GUI ↔ AppSettings,
- mapowanie GUI ↔ TranslatorConfig,
- zapis/odczyt ustawień,
- aktywny klucz API,
- profile Cloud,
- konfiguracja backend-specific.

To powinno ograniczyć bezpośrednie modyfikacje self._settings w callbackach.

### 4.5 settings_panels.py lub backend_settings_widget.py

Odpowiedzialność:

- budowa grup API/serwera/dodatków,
- widgety zależne od backendu,
- widoczność pól.

Nie zapisuje konfiguracji i nie uruchamia backendów.

### 4.6 skills_controller.py

Odpowiedzialność:

- discovery,
- import,
- new,
- refresh,
- aktywne skille,
- automatyczny wybór skilla.

Wykorzystuje istniejący tlumacz/skill.py.

### 4.7 mozhi_controller.py

Odpowiedzialność:

- health-check,
- wybór instancji,
- wybór silnika,
- bezpieczne zastosowanie wyniku.

MozhiHealthWorker może zostać przeniesiony razem z kontrolerem.

---

## 5. Backendy, których NIE usuwamy

### [NO-DELETE] FastAPI

Zachować:

- konfigurację,
- manager,
- worker,
- zależności kodowe,
- pola GUI,
- rekord konfiguracji.

Brak migracji do aktywnej ścieżki nie oznacza usunięcia.

### [NO-DELETE] OpenVINO

Zachować:

- konfigurację,
- lazy import,
- backend,
- worker,
- pola GUI,
- rekord konfiguracji.

Nie podłączać go automatycznie do aktywnego lifecycle tylko dlatego, że refaktor porządkuje MainWindow.

### [NO-REWRITE] BackendManager

Najpierw odseparować konsumenta. Nie przepisywać managera bez osobnej decyzji.

### [NO-REWRITE] worker.py

Istniejący mechanizm TranslationThread i anulowania pozostawić jako źródło prawdy.

---

## 6. Kolejność implementacji

### ETAP 0 — zabezpieczenie

**[P0] [BACKUP] [TDD] [DOCS]**

1. Sprawdzić Git i aktywne procesy.
2. Nie zatrzymywać długich benchmarków/testów bez zgody.
3. Wykonać backup MainWindow i plików pierwszego dużego refaktoru.
4. Ustalić baseline testów Qt/offscreen.
5. Uzupełnić brakujące testy kontraktowe.
6. Zapisać baseline w dokumentacji.

Warunek wyjścia: istnieje odtwarzalny punkt odniesienia.

### ETAP 1 — konfiguracja

**[P0] [TDD] [SAFE]**

Wydzielić:

- _active_api_key,
- _build_config,
- _collect_settings,
- _load_settings_into_ui,
- _build_config_updates.

Testy obowiązkowe:

- llama → TranslatorConfig,
- Cloud → prawidłowy profil, klucz, model i endpoint,
- przełączanie backendu,
- FastAPI/OpenVINO pozostają rekordami GUI,
- zapis i odczyt ustawień,
- brak wycieku klucza Cloud do konfiguracji lokalnej.

### ETAP 2 — backend lifecycle

**[P0] [TDD] [SAFE] [NO-DELETE]**

Wydzielić BackendController.

Testy:

- llama start/stop/restart,
- Cloud activation,
- llama → Cloud,
- Cloud → llama,
- wybór FastAPI/OpenVINO nie uruchamia odłączonego backendu,
- błąd odblokowuje GUI,
- cancel nie pozostawia serwera w nieznanym stanie.

### ETAP 3 — tłumaczenie

**[P0] [TDD] [SAFE]**

Wydzielić TranslationController.

Zakres:

- start,
- cancel,
- progress,
- success,
- failure,
- cleanup.

TranslationThread pozostaje w worker.py.

### ETAP 4 — panele GUI

**[P1] [SAFE]**

Wydzielić budowę:

- zakładki tłumaczenia,
- API/serwer,
- dodatki,
- pomoc.

Buildery nie zapisują ustawień i nie uruchamiają backendów.

### ETAP 5 — skille i glosariusz

**[P1] [TDD]**

Wydzielić GUI glue code.

Nie przenosić logiki domenowej z skill.py ani glossary.py do GUI.

### ETAP 6 — Mozhi

**[P1] [TDD]**

Wydzielić health-check i worker.

Test krytyczny: wynik starego health-checku nie może nadpisać nowszego wyboru użytkownika.

### ETAP 7 — finalne uproszczenie

**[P2] [SAFE] [VERIFY]**

Dopiero po wcześniejszych etapach:

- usunąć martwe wrappery,
- ograniczyć bezpośredni dostęp do BackendManager._config,
- ograniczyć bezpośrednie modyfikacje _settings,
- uprościć lifecycle,
- ujednolicić nazwy.

Nie wykonywać automatycznego globalnego refaktoru.

---

## 7. Najważniejsze ryzyka

### R1 — współdzielony stan [P0]

Wydzielenie metody bez wydzielenia stanu może tylko przenieść problem.

**Mitigacja:** jawne zależności kontrolerów; unikać przekazywania całego MainWindow.

### R2 — Qt ownership [P0]

QWidget, QObject, QThread, sygnały i deleteLater mają własny lifecycle.

**Mitigacja:** jednoznaczny właściciel każdego kontrolera/worker'a i testy lifecycle.

### R3 — asynchroniczne przełączanie backendu [P0]

_pending_backend_start istnieje dlatego, że zatrzymanie llama jest asynchroniczne.

**Mitigacja:** cały mechanizm w jednym BackendController.

### R4 — konfiguracja Cloud [P0]

Profil zawiera endpoint, klucz, provider, engine i model.

**Mitigacja:** testy profili przed i po wydzieleniu.

### R5 — FastAPI/OpenVINO [P1]

Są w GUI i konfiguracji, ale poza aktywnym BackendManagerem.

**Mitigacja:** zachować dokładnie ten status podczas refaktoru.

### R6 — debug.log [P0]

Raport audytu wskazuje _build_config jako źródło krytycznej regresji: bezwarunkowy zapis do Path.home()/.../debug.log.

**Mitigacja:** naprawić ten problem osobno lub jako pierwszy krok ETAPU 1; nie maskować go samym podziałem modułu.

### R7 — podgląd plików [P1]

_show_preview miesza decyzję o formacie z prezentacją.

**Mitigacja:** docelowo helper zwracający dane do prezentacji.

---

## 8. Kontrakty, które muszą zostać zachowane

1. Tłumaczenie nadal działa poza głównym wątkiem GUI.
2. Cancel pozostaje nieblokujący dla GUI.
3. llama zachowuje obecny lifecycle.
4. Cloud nadal używa profilu konkretnej usługi.
5. Klucze lokalne i Cloud nie mieszają się.
6. FastAPI/OpenVINO nie są usuwane ani przypadkowo aktywowane.
7. Ustawienia są zachowywane przy zamknięciu.
8. Język i motyw nadal działają.
9. Skille zachowują obecny kontrakt.
10. Glosariusz zachowuje obecny kontrakt.
11. Mozhi nie nadpisuje nowszego wyboru użytkownika.
12. Podgląd zachowuje obecne ograniczenia dla formatów binarnych.
13. BackendManager pozostaje źródłem prawdy dla lifecycle backendu.
14. TranslationThread pozostaje źródłem prawdy dla lifecycle tłumaczenia.

---

## 9. Strategia testów

### Przed pierwszym refaktorem [TDD]

Zabezpieczyć:

- konfigurację llama,
- konfigurację Cloud,
- profile i klucze,
- backend switching,
- FastAPI/OpenVINO jako odłączone rekordy,
- translation start/cancel/success/failure,
- save/load settings,
- Mozhi race condition,
- GUI idle/running/error.

### Po każdym etapie [VERIFY]

1. testy modułu,
2. testy zależnych modułów,
3. compileall,
4. git diff --check,
5. odpowiednie testy Qt/offscreen.

### Końcowa weryfikacja

- pełny suite,
- aktywna ścieżka E2E,
- przełączanie backendu,
- cancel,
- pierwsze uruchomienie bez config.json,
- środowisko z niezapisywalnym katalogiem logów,
- potwierdzenie obecności FastAPI/OpenVINO.

---

## 10. Kryteria akceptacji

**[P0] [VERIFY]**

Refaktor uznajemy za zakończony dopiero, gdy:

- MainWindow jest głównie warstwą prezentacji/kompozycji,
- konfiguracja nie jest rozproszona po callbackach,
- lifecycle backendu jest w jednym miejscu,
- lifecycle tłumaczenia jest w jednym miejscu,
- FastAPI/OpenVINO nadal istnieją,
- zmiany zachowania mają testy,
- pełny suite przechodzi,
- git diff --check przechodzi,
- dokumentacja architektury jest aktualna.

Liczba linii nie jest kryterium. Kryterium są granice odpowiedzialności i mniejsze sprzężenie.

---

## 11. Zależności docelowe

MainWindow
→ SettingsController
→ BackendController
→ TranslationController
→ UI panels/builders
→ SkillsController
→ MozhiController

Istniejące moduły domenowe pozostają źródłem prawdy:

- core.py — tłumaczenie,
- worker.py — worker/process lifecycle,
- backend_manager.py — backend abstraction/lifecycle,
- config.py — model i persystencja ustawień,
- skill.py — skille,
- glossary.py — glosariusz.

---

## 12. Decyzje do potwierdzenia przed implementacją

1. Czy SettingsController ma być QObject, czy zwykłą klasą usługową?
2. Czy BackendController ma emitować uproszczony model stanu?
3. Czy TranslationController ma posiadać TranslationThread, czy fabrykę threadów?
4. Czy buildery UI mają tylko budować widgety, czy także udostępniać sygnały?
5. Czy MozhiHealthWorker pozostaje osobno, czy w MozhiController?

Rekomendacja: decyzje te podejmować podczas ETAPU 1 na podstawie testów i rzeczywistych zależności, a nie przez projektowanie abstrakcyjne.

---

## 13. Dokumentacja

Po każdym wykonanym etapie:

- [DOCS] aktualizować docs/STATUS.md,
- [DOCS] aktualizować CHANGELOG.md,
- [DOCS] aktualizować ten plan o status etapu,
- [DOCS] przy zmianie architektury aktualizować dokument migracji V4,
- [COMPOUND] po nieoczywistym rozwiązaniu zapisać trwały wniosek architektoniczny.

---

## 14. Czego plan NIE zakłada

- nie usuwamy FastAPI,
- nie usuwamy OpenVINO,
- nie usuwamy istniejących backendów,
- nie instalujemy nowych zależności,
- nie przepisujemy GUI od zera,
- nie zmieniamy silnika tłumaczenia,
- nie wykonujemy równoległego refaktoru core.py, worker.py i backend_manager.py,
- nie migrujemy wszystkich historycznych ścieżek do V4.

**Cel:** zmniejszyć koncentrację odpowiedzialności w MainWindow, zachowując działające kontrakty i umożliwiając dalszą migrację V4 bez niszczenia istniejących ścieżek.
