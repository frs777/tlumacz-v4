---
id: plan-03-llama-cpp-translategemma-2026-10-05
status: completed
meta:
  contentType: ModuleImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-06
owner: platform-architecture
priority: P1
depends_on: [docs/Plany/PLAN-2026-10-05.md]
last_validation: "audyt 2026-10-05"
---
# Wykonanie — 2026-10-06

Plan został zweryfikowany na aktualnym source V4 i aktualnym runtime llama-server 0.4.0-dev (build 10809, commit 5266f24da).

### Wyniki punktów wdrożenia

1. Start/stop/restart/health — kontrakty runtime oraz health przechodzą; TranslationApp oczekuje na /health HTTP 200.
2. Kontrakt zwykłego llama.cpp — testy adaptera/kontraktu przechodzą.
3. TranslateGemma en→pl — testy specjalnego trybu przechodzą; realny model zwrócił poprawne tłumaczenie.
4. Lingua per chunk — LlamaCppLanguageRouting wykrywa źródło niezależnie dla każdego chunka; testy routingu przechodzą.
5. Realny GGUF przez aplikację — świeży E2E TranslationApp → DocumentTranslationService → llama-server → TranslateGemma → wynik dokumentowy zakończył się poprawnym wynikiem.
6. Realny przepływ GUI/bridge — świeży E2E QML bridge zakończył się translationFinished, statusem „Tłumaczenie zakończone.” i poprawnym plikiem wynikowym.
7. Cancellation/shutdown — testy lifecycle i cancellation przechodzą; po TranslationApp.close() runtime nie pozostaje pod kontrolą aplikacji.
8. n_ubatch — nie wprowadzono historycznej poprawki z V3. Aktualny profil llama.json pozostaje źródłem ustawień batch_size/ubatch_size; brak dowodu na potrzebę dodatkowej zmiany dla bieżącego release.

### Obowiązujący kontrakt TranslateGemma

Dla aktualnego llama-server 0.4.0-dev stabilna ścieżka aplikacyjna to:

GGUF → llama-server --no-jinja → LlamaCppAdapter → /v1/completions → ręcznie renderowany format Gemma → wynik.

Nie należy przywracać automatycznie ścieżki --jinja + /v1/chat/completions tylko na podstawie wcześniejszych wyników z llama.cpp b7976. Na bieżącym runtime próba uruchomienia TranslateGemma z natywnym Jinja kończy się błędem automatycznego parsera szablonu, ponieważ szablon wymaga typed-content o strukturze TranslateGemma. Obecna ścieżka --no-jinja + /v1/completions została zweryfikowana na rzeczywistym modelu i jest świadomym kontraktem release.

Kody source_language i target_language są nadal normalizowane do ISO 639-1 przez language_code_for(). Detekcja źródła pozostaje odpowiedzialnością LlamaCppLanguageRouting; język docelowy pochodzi z GUI i nie jest wykrywany przez Lingua.

### Weryfikacja 2026-10-06

- focused llama.cpp/TranslateGemma suite: 37 passed;
- focused GUI llama.cpp suite: 43 passed;
- pełny pytest: 379 passed, 2 failed; oba failures są poza zakresem Planu 03 (Apertium u+x, globalny stan języka pomocy QML);
- realny E2E aplikacyjny: PASS;
- realny E2E przez QML bridge: PASS;
- wykonano backup przed pracą: backups/plan-03-pre-restore-20261006-144617/llama-cpp-state.tar.gz;
- SHA-256 backupu: 936772cbc78abca693eeb7bfe2db7575880fb29478ce67c7a435e6342b018e89.

Wniosek: Plan 03 spełnia własny exit gate. Pozostałe dwa failures pełnego suite nie należą do odpowiedzialności llama.cpp/TranslateGemma i nie uzasadniają zmiany kodu tego modułu.

---

# PLAN-04 — llama.cpp i TranslateGemma

## 1. Oczekiwany rezultat
Zapewnić stabilny lokalny backend llama.cpp oraz zamknąć TranslateGemma jako rzeczywistą ścieżkę aplikacyjną.

## 2. Zakres odpowiedzialności
LlamaCppAdapter; LlamaCppRuntimeManager; GGUF; server lifecycle; chat templates; source/target ISO codes; Lingua tylko dla TranslateGemma; cancellation; health.

## 3. Schemat budowy
```text
```text
TranslationApp
  ↓
LlamaCppBackend
  ├─ RuntimeManager → llama-server
  └─ Adapter → HTTP/OpenAI-compatible
                 ↓
        TranslateGemma template
                 ↓
          validated result
```
```

## 4. Połączenia z innymi modułami
Core zna kontrakt. GUI steruje konfiguracją przez bridge. Packaging dostarcza runtime/model contract, ale model GGUF nie musi być częścią wheel.

## 5. Szczegółowy plan wdrożenia
1. Characterization start/stop/restart/health.
2. Test kontraktu zwykłego llama.
3. Test TranslateGemma z jawnie wymuszonym en→pl.
4. Test Lingua detection per chunk.
5. Test realnego GGUF przez pełną aplikację.
6. Zweryfikować cancellation i shutdown.
7. Zbadać historyczny problem n_ubatch tylko w zakresie potrzebnym do stabilności release.
8. Nie zmieniać promptu bez testu regresyjnego.

## 6. Wymagania i zależności
Research upstream wskazuje, że TranslateGemma wymaga poprawnego template i kodów języków; aktualny V4 używa special mode. Problem V3 z n_ubatch jest osobnym tropem i nie może być automatycznie przeniesiony do V4.

## 7. Szczegóły integracji
TranslationGemma pozostaje wariantem llama.cpp, nie osobnym backendem. Wynik przechodzi ResultValidator i zapis dokumentowy.

## 8. Exit gate
Realny model przechodzi GUI → detector → prompt → llama-server → response → validation → document result; shutdown nie zostawia procesu; błędy są klasyfikowane.

## 9. Zasady
Nie zmieniać innych modułów tylko po to, aby uprościć implementację tego modułu. Każda zmiana kontraktu wymaga aktualizacji testów, dokumentacji i głównego PLAN-2026-10-05.md.

## Aktualizacja 2026-10-06 — źródła parametrów llama.cpp

Potwierdzono kontrakt konfiguracji: GUI pozostaje właścicielem parametrów operacyjnych serwera (GGUF, host, port, CPU/GPU, parallel, szablon czatu, rozmiar bloku), a $HOME/.config/tlumacz/llama.json właścicielem tuningu technicznego. Uzupełniono implementację o rzeczywiste rozstrzyganie threads=auto według rdzeni fizycznych oraz threads_batch=auto według wątków logicznych, zgodnie z sekcją auto profilu. Dodano test regresyjny TDD.
