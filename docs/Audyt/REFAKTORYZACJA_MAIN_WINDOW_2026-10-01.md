# Refaktoryzacja rdzenia MainWindow — 2026-10-01

## Cel

Pierwszy etap refaktoryzacji ma odłączyć warstwę prezentacji Qt od konkretnych backendów i runtime llama.cpp. Celem nie jest kosmetyczne skrócenie pliku, lecz przesunięcie odpowiedzialności do warstwy aplikacyjnej.

## Stan przed zmianą

MainWindow bezpośrednio tworzył BackendRegistry, budował BackendSelection, konfigurował adapter llama.cpp, zarządzał LlamaCppRuntimeManager oraz składał DocumentTranslationService.

## Wprowadzone rozdzielenie

Dodano:

- BackendService — fasada nad BackendRegistry i aktywnymi backendami V4;
- TranslationApp — rdzeń aplikacyjny odpowiedzialny za składanie usług tłumaczenia i runtime llama.cpp;
- composition root w qt_gui/app.py, który tworzy TranslationApp i przekazuje go do MainWindow.

Przepływ:

MainWindow → TranslationApp → BackendService → BackendRegistry → llama.cpp / Apertium / Cloud

MainWindow nie importuje już bezpośrednio BackendRegistry, BackendSelection, LlamaCppAdapter ani LlamaCppRuntimeManager.

## TDD i weryfikacja

Najpierw dodano test kontraktu rdzenia w tests/test_application_core.py. Początkowy test celowo zakończył się niepowodzeniem z powodu braku modułu BackendService. Następnie zaimplementowano warstwę aplikacyjną i doprowadzono test do GREEN.

Weryfikacja końcowa:

- pytest: 199 passed;
- Ruff: PASS;
- compileall: PASS.

## Co pozostaje

MainWindow nadal zawiera logikę prezentacji, konfiguracji kontrolek, ustawień oraz workera Qt. Istniejące kontrolery aplikacyjne nie zostały jeszcze włączone do głównego przepływu.

Następny etap powinien wydzielić:

1. konfigurację i persistencję;
2. dokumenty;
3. diagnostykę;
4. postęp;
5. pozostały stan operacji tłumaczenia.

Refaktoryzacja nie przywraca FastAPI ani OpenVINO.
