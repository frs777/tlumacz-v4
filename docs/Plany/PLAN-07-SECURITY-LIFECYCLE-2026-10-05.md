---
id: plan-07-security-lifecycle-2026-10-05
status: active
meta:
  contentType: ModuleImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-05
owner: platform-architecture
priority: P1
depends_on: [docs/Plany/PLAN-2026-10-05.md]
last_validation: "audyt 2026-10-05"
---
# PLAN-06 — Konfiguracja, sekrety, cache i lifecycle

## 1. Oczekiwany rezultat
Zapewnić, że konfiguracja nie ujawnia sekretów, a wszystkie zasoby aplikacji mają jeden deterministyczny lifecycle.

## 2. Zakres odpowiedzialności
AppSettings; SecretStore; sekrety lokalne, Custom i Cloud przechowywane przez SecretStore w pliku .key w katalogu konfiguracyjnym użytkownika; TranslationCache SQLite; llama runtime; workers; QGuiApplication.aboutToQuit; reset/migration.

## 3. Schemat budowy
```text
```text
QML
 ↓
Bridge
 ├─ SettingsService
 ├─ SecretStore
 └─ Runtime lifecycle
       ├─ Cache
       └─ llama.cpp
```
```

## 4. Połączenia z innymi modułami
Core używa cache przez kontrakt. GUI wywołuje lifecycle przez Application. Packaging nie zapisuje sekretów.

## 5. Szczegółowy plan wdrożenia
1. Test snapshot settings bez sekretu.
2. Test migracji legacy key → SecretStore.
3. Test restartu i odczytu sekretu.
4. Characterization cache open/close.
5. Centralne close aplikacji.
6. aboutToQuit binding.
7. Test procesu llama + SQLite + Qt event loop.
8. Sprawdzić ResourceWarning i orphan processes.

## 6. Wymagania i zależności
Qt oficjalnie udostępnia aboutToQuit jako miejsce na ostatnie cleanup. Nie wykonywać interakcji użytkownika w tym stanie.

## 7. Szczegóły integracji
Shutdown musi być idempotentny. Błąd zamykania jednego zasobu nie może uniemożliwić próby zamknięcia pozostałych.

## 8. Exit gate
Zero sekretów w settings JSON; brak unclosed sqlite; brak orphan llama; pełny shutdown test green; migracja legacy zachowana.

## 9. Zasady
Nie zmieniać innych modułów tylko po to, aby uprościć implementację tego modułu. Każda zmiana kontraktu wymaga aktualizacji testów, dokumentacji i głównego PLAN-2026-10-05.md.
## 2026-10-06 — realizacja fazy Security/Lifecycle

### Zrealizowane
- [x] SecretStore pozostaje jedynym miejscem trwałego przechowywania kluczy usługowych (`$HOME/.config/tlumacz/.key`).
- [x] Legacy `api_key` / `last_local_api_key` jest migrowane do SecretStore przed dalszym ładowaniem GUI.
- [x] Migracja obejmuje wszystkie profile Cloud, a nie tylko aktualnie wybrany profil.
- [x] Po migracji legacy pola sekretów są usuwane z `AppSettings` przed zapisem.
- [x] Zapis ustawień przez bridge nie utrwala kluczy API w `config.json` (kanoniczny plik trwałej konfiguracji GUI).
- [x] Centralny `TranslationApp.close()` zamyka cache nawet wtedy, gdy zamykanie runtime zgłosi błąd.
- [x] `TranslationApp.stop_llama()` nie porzuca referencji do procesu, którego tożsamość nie zgadza się z zapisanym ownership identity.
- [x] `QGuiApplication.aboutToQuit` jest podpięte do centralnego `TranslationApp.close()`.
- [x] Dodano regresje TDD dla migracji sekretów, braku wycieku do settings JSON, odporności shutdown oraz ochrony przed zapomnieniem niezarządzanego procesu.

### Weryfikacja fazy
- Focused suite: **30 passed**.
- Ruff dla zmienionego zakresu: **PASS**.
- Backup fazy: `backups/SECURITY-LIFECYCLE-PHASE1-2026-10-06.tar.gz`.
- Backup baseline: `backups/SECURITY-LIFECYCLE-BASELINE-2026-10-06.tar.gz`.

### Pozostały gate
Pełny suite projektu oraz kontrola ResourceWarning/orphan processes pozostają wymagane przed oznaczeniem PLAN-07 jako zakończonego.

### 2026-10-06 — dodatkowa ochrona lifecycle SQLite
- [x] TranslationCache otrzymał awaryjny finalizer __del__ jako defense-in-depth; normalnym mechanizmem pozostaje jawne close() z TranslationApp.close().
- [x] Focused suite uruchomiony z -W error::ResourceWarning: **32 passed**; brak nieobsłużonych ResourceWarning w tym zakresie.
- [ ] Pełny suite nadal nie jest green: osobny, wcześniejszy failure test_document_translation_service_applies_skip_patterns_before_backend występuje poza zakresem PLAN-07; pełny przebieg kończył się również fatalnym abortem w wątku Filter Engine po wielu testach.


## 2026-10-07 — dochodzenie `settings-v4.json` i regresja skip-pattern

- Ustalono, że aktywny kod V4 (`src/tlumacz/qml_gui/config.py`) używa wyłącznie `$HOME/.config/tlumacz/config.json`.
- `settings-v4.json` został utworzony o **00:09:15**, natomiast aktualny proces V4 uruchomił się dopiero o **00:25:51**. W aktywnym `src/` nie ma kodu zapisującego ten plik.
- Repozytorium zawierało jednak historyczny `build/lib/tlumacz/qml_gui/config.py`, w którym `CONFIG_PATH` nadal wskazywał `settings-v4.json`. To jest pozostałość starego artefaktu budowania i może przywracać legacy kontrakt, jeśli zostanie uruchomiony stary artefakt zamiast `src/`.
- Hipoteza o restarcie jest zgodna z chronologią: uruchomiony wcześniej proces mógł mieć w pamięci starą implementację i zapisać legacy plik podczas restartu. Nie ma dowodu, że aktualny kod V4 generuje go podczas restartu.
- Usunięto aktualnie obecny `$HOME/.config/tlumacz/settings-v4.json`; jedynym aktywnym plikiem pozostaje `config.json`.
- Test `test_document_translation_service_applies_skip_patterns_before_backend` przechodził już w izolacji i w całym pliku `tests/test_document_translation_service.py` (5/5). Wzmocniono regresję o weryfikację końcowego HTML: pominięty fragment pozostaje niezmieniony, a pozostałe dwa są przetłumaczone.
- Backup przed zmianą: `backups/PLAN-07-SKIP-PATTERN-BEFORE-2026-10-07.tar.gz`, SHA-256 `da848a3ae5b6adfe8265798e54f01188f93557b4f10becde4d97d58cccf734b9`.
