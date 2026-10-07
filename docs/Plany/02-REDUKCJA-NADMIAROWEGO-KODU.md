---
id: plan-02-redukcja-nadmiarowego-kodu
status: closed
meta:
  contentType: ImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-04
owner: project-maintenance
source: docs/Audyt/AUDYT_FORENSICZNY_V3_V4_2026-10-01.md
depends_on: [docs/Plany/00-BASELINE-MAPA-PARYTETU-V3-V4.md, docs/Plany/01-RESTORE-BRAKUJACE-FUNKCJE.md]
expires_when: potwierdzone relikty i martwe ścieżki są usunięte lub wydzielone
last_validation: "plan przygotowany 2026-10-04"
---

# PLAN 02 — usunięcie nadmiarowego i martwego kodu

## Zasada

Najpierw funkcjonalność, potem zero-reference, dopiero potem usunięcie. Nie usuwać kodu tylko dlatego, że wygląda na stary.

## 1. profile_migration.py

1. Znaleźć wszystkie produkcyjne callery.
2. Znaleźć testy i dokumentację.
3. Ustalić, czy migracja profili jest jeszcze wykonywana.
4. Jeśli jest potrzebna, wydzielić ją jako jawne narzędzie migracyjne poza aktywną logiką backendu.
5. Jeśli zakończona, usunąć kod i test chroniący wyłącznie historyczną ścieżkę.
6. Wykonać zero-reference scan.
7. Zapisać decyzję.

## 2. SecretStore

Nie usuwać automatycznie.

1. Prześledzić wszystkie importy.
2. Prześledzić faktyczny przepływ kluczy Cloud.
3. Porównać z kontraktem izolacji sekretów.
4. Wybrać WIRE-IN, REPLACE albo DROP na podstawie dowodu.
5. Jeśli WIRE-IN, podłączyć do rzeczywistego flow.
6. Jeśli DROP, usunąć dopiero po potwierdzeniu braku konsumentów.

## 3. Kontrolery GUI

Dla BackendController, TranslationController, DocumentController, SettingsController, DiagnosticsController i ProgressController:
1. inventory callerów;
2. sprawdzić użycie przez aktualny QML bridge;
3. rozdzielić kod aktywny od test-only;
4. podłączyć kontroler, jeżeli jest właściwym kontraktem;
5. usunąć tylko wtedy, gdy jest udowodnionym dead code.

Nie usuwać kontrolera tylko dlatego, że bridge ma własną logikę.

## 4. DocumentProcessor._unit_parts()

Potwierdzić brak callerów statycznych, dynamicznych, testowych i dokumentacyjnych. Dopiero wtedy usunąć.

## 5. Backupy i artefakty

Zidentyfikować *.bak.*, __pycache__, .pytest_cache, .mypy_cache, .ruff_cache i temp staging. Dla każdego ustalić regenerowalność i znaczenie dla rollbacku. Nie usuwać jedynego backupu potrzebnego do odzyskania pracy.

## Zero-reference gate

Przed każdym usunięciem sprawdzić:
importy, nazwy, ścieżki, konfigurację, testy, dokumentację, entrypointy i stringi dynamiczne.

## Czego nie usuwać bez osobnej decyzji

Nie usuwać globalnego V3, historycznych dokumentów V3, aktywnego Cloud/DLX, Apertium, QML GUI ani zasobów runtime.

## Kryterium wyjścia

Brak potwierdzonych martwych ścieżek w aktywnym runtime, brak aktywnego kodu migracyjnego bez właściciela i brak usuniętych funkcji aktywnych. Testy muszą pozostać zielone.
## Raport wykonania — 2026-10-04

### 1. `profile_migration.py` — ZAMKNIĘTE / USUNIĘTE

Zero-reference scan wykazał brak aktywnych callerów produkcyjnych i brak użycia przez aktualny przepływ konfiguracji. Pozostały wyłącznie historyczne wzmianki w audytach/raportach oraz sam Plan 02.

Usunięto:
- `src/tlumacz/backends/cloud/profile_migration.py`;
- `tests/test_cloud_profile_migration.py`;
- eksport `migrate_cloud_profiles` z `src/tlumacz/backends/cloud/__init__.py`.

Backup przed redukcją: `backups/plan-02-20261004/pre-cleanup-inventory.tar.gz`, SHA-256 `3f89cd16ed55e5b2d7b84d3ba05ba69388dfa10a18f69e90ea14a9f45a1e4995`.

Weryfikacja po usunięciu: **31 passed** w skoncentrowanym suite Cloud/GUI oraz późniejszy pełny suite V4.

### 2. `SecretStore` — NIE USUWAĆ

`SecretStore` ma własne testy bezpieczeństwa i pozostaje potencjalnym kontraktem izolacji sekretów. Nie znaleziono potwierdzonego produkcyjnego konsumenta, więc zgodnie z zasadą planu nie wykonano DROP. Punkt pozostaje otwarty do decyzji WIRE-IN/REPLACE/DROP.

### 3. Kontrolery GUI — ZAMKNIĘTE / ODDZIELONO KOD AKTYWNY OD DEAD CODE

Zero-reference scan wykazał, że aktywnym kontrolerem w `TranslationApp` pozostaje `BackendController`, używany przy wyborze backendu. `TranslationController`, `DocumentController`, `SettingsController`, `DiagnosticsController` i `ProgressController` nie miały aktywnych callerów poza własnymi testami oraz wcześniejszymi, nieużywanymi instancjami w `TranslationApp`.

Usunięto pięć nieużywanych kontrolerów, ich testy kontraktowe oraz nieużywane pola/importy z `TranslationApp`. `BackendController` pozostawiono.

Po zmianie pełny suite V4: **265 passed**.

### 4. `DocumentProcessor._unit_parts()` — ZAMKNIĘTE / USUNIĘTE

Skan repozytorium potwierdził brak callerów produkcyjnych i testowych. Usunięto metodę oraz nieużywany import `Any`. Istniejący suite `FilterRegistry`/`DocumentProcessor`/filtrów: **30 passed**; pełny suite V4 po zmianie: **278 passed**.

### 5. Backupy i artefakty

Wykonano inventory artefaktów: **3031** plików `*.bak.*`/`*.pyc` w drzewie projektu. Nie wykonano masowego kasowania; część backupów jest potrzebna do rollbacku trwającej migracji. Cleanup artefaktów pozostaje osobnym zadaniem po zakończeniu aktywnych planów.

## Raport — SecretStore WIRE-IN — 2026-10-04

`SecretStore` został podłączony do aktywnego `QmlApplicationBridge`. Klucze Cloud są odseparowane od JSON i przechowywane jako `SERVICE/<usługa>` w prywatnym `.key` z prawami 600. Starsze profile zawierające `api_key` są przy odczycie migrowane do magazynu.

Backup: `backups/plan-02-20261004/pre-secretstore-wire-in.tar.gz`, SHA-256 `aad209a0ccefb3da3ab9e82848effd65e73b959913320b649ff6f6acdb55c289`.

Regresja SecretStore/GUI: **4 passed**; pełny suite po zmianie: **279 passed**.
