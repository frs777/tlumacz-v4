---
id: plan-13-remediacja-dokumentacji-repo-2026-10-07
status: closed
meta:
  contentType: RemediationPlan
  category: documentation-governance
version: 1.0.0
updated: 2026-10-07
owner: project-maintenance
priority: P1
source:
  - docs/Plany/PLAN-11-DOKUMENTACJA-REPO-2026-10-05.md
  - docs/STATUS.md
  - docs/BUG.md
  - docs/TODO.md
  - docs/INDEX.yml
  - aktualny filesystem repozytorium
---
# PLAN-13 — Remediacja dokumentacji repozytorium

> Plan jest wykonywany na żywym repozytorium. Pliki mogą zmienić się między kolejnymi pomiarami; każdy etap musi ponownie ustalić stan bieżący przed zapisem. Nie wolno opierać decyzji o liczbie plików wyłącznie na wcześniejszym snapshotcie.

## Cel

Doprowadzić dokumentację V4 do stanu, w którym bieżący stan projektu, historia, plany, dowody testowe i indeks są rozdzielone oraz wzajemnie zgodne, bez usuwania historii i bez ingerencji w aktywną implementację niezwiązanej z tym planem.

## Zasady nadrzędne

1. `src/` i rzeczywisty runtime są źródłem prawdy dla implementacji.
2. `docs/STATUS.md` opisuje wyłącznie stan bieżący; wyniki historyczne pozostają historyczne.
3. `docs/BUG.md` zawiera aktywne i zamknięte defekty z jednoznacznym statusem.
4. `docs/TODO.md` zawiera wyłącznie zadania nadal otwarte.
5. `docs/CHANGELOG.md` opisuje wykonane zmiany.
6. `docs/INDEX.yml` i `docs/INDEX.md` muszą odpowiadać aktualnemu filesystemowi zgodnie z polityką `docs/AGENTS.md`.
7. Nie usuwać dokumentacji historycznej tylko dlatego, że jest nieaktualna.
8. Nie usuwać ani nie przenosić plików bez wyraźnej zgody użytkownika.
9. `*.bak*` są artefaktami regenerowalnymi i mogą być czyszczone przez `tools/cleanup-bak.sh`; trwałe backupy pozostają nietknięte.
10. Ponieważ nad projektem trwa praca, przed każdym etapem wykonywać ponowny pomiar i po każdym zapisie sprawdzać wynik.

## Stan wejściowy 2026-10-07

W aktualnym pomiarze:

- `docs` zawiera **493 pliki**;
- w `docs` pozostało **0 `*.bak*`** po wdrożonym cleanupie;
- `INDEX.yml` zawiera **485 wpisów `path`**;
- nagłówek `INDEX.yml` nadal deklaruje historyczne `file_count: 479`;
- korelacja filesystem ↔ `INDEX.yml` wykazała **15 plików nieobecnych w indeksie** oraz **7 wpisów wskazujących na nieistniejące ścieżki**;
- istnieje `PLAN-12-TRANSLATEGEMMA-CHUNKOWANIE-JEZYKI-SKIP-2026-10-07.md`, którego indeks nie zawiera;
- nowy niniejszy plan również musi zostać zindeksowany po utworzeniu;
- pełny suite zakończył się **542 passed, 1 failed**; jedyny potwierdzony failure dotyczy kontraktu liczby wywołań `translate_batch` w `test_document_translation_service_uses_structural_markdown_chunks_and_one_batch_request` i musi pozostać jawny w bieżącym statusie;
- `PLAN-12` jest oznaczony jako `WDROŻONY`, ale jego exit gate nadal wymaga rzeczywistego E2E z llama.cpp/TranslateGemma. Ten rozjazd statusu należy skorygować podczas synchronizacji dokumentacji.

### Pliki nieobecne w indeksie — lista kontrolna

1. `docs/Plany/PLAN-12-TRANSLATEGEMMA-CHUNKOWANIE-JEZYKI-SKIP-2026-10-07.md`
2. `docs/Plany/PLAN-2026-10-06-paczki-apertium.md`
3. `docs/_inbox/MECHANIZM_DETEKCJI_JEZYKA_APERTIUM.md`
4. `docs/_inbox/plan-wdrozenia-jezyka-Apertium.md`
5. `docs/_inbox/wybor-jezyka-Apertium.md`
6. `docs/wdrozenia/rekomendacja-ustawien-llama.cpp.md`
7. `docs/reports/PLAN-05-CLOUD-MOZHI-2026-10-06.md`
8. `docs/reports/PLAN-07-SECURITY-LIFECYCLE-2026-10-06.md`
9. `docs/superpowers/plans/2026-10-06-tplugin-admin-module.md`
10. `docs/superpowers/plans/2026-10-07-naprawa-izolacji-sekretow-profili-cloud.md`
11. `docs/superpowers/plans/macos-bin-build.md`
12. `docs/technical-docs/Secyfikacja intelpletacji zastosowania filtrow jezykowych okapi przy pomocy engine napiosanego w pythonike.md`
13. `docs/technical-docs/apertium-pair-packages.md`
14. `docs/wdrozenia/karta-referencyjna-llama-sprzet.md`
15. `docs/wdrozenia/llama-cpp-runtime.md`

### Wpisy indeksu wymagające rozstrzygnięcia

- `docs/Plany/PLAN-00-FUNDAMENT-RELEASE-2026-10-05.md`
- `docs/Plany/PLAN-01-RDZEN-DOKUMENTOWY-2026-10-05.md`
- `docs/Plany/PLAN-06-CUSTOM-OPENAI-COMPAT-2026-10-05.md`
- `docs/Plany/PLAN-09-PACKAGING-PLATFORMY-2026-10-05.md`
- `docs/reserge/chatgpt_linux_tailscale_secure_mcp_tunnel.md`
- `Tlumacz-V4.desktop`
- `uruchom-tlumacz-v4.sh`

Te wpisy nie mogą być automatycznie kasowane: najpierw ustalić, czy zostały przeniesione, zastąpione, czy są świadomie poza bieżącym filesystemem.

## Etapy naprawy

### Etap 0 — ruchomy baseline

Przed każdym kolejnym etapem:

- policzyć `docs` i `*.bak*`;
- ponownie wykonać korelację filesystem ↔ `INDEX.yml`;
- sprawdzić ostatnie modyfikacje `STATUS`, `BUG`, `TODO`, `CHANGELOG` i planów;
- odnotować zmianę baseline'u, jeżeli repozytorium zmieniło się w międzyczasie.

### Etap 1 — indeks

- uzupełnić wszystkie rzeczywiście istniejące dokumenty;
- rozstrzygnąć siedem wpisów historycznych/nieistniejących;
- skorygować `file_count`, `status_counts` i `zone_counts` na podstawie faktycznego zbioru;
- wygenerować/synchronizować `INDEX.md` z `INDEX.yml` według istniejącego formatu projektu;
- sprawdzić brak duplikatów ścieżek i brak martwych linków;
- po zapisie wykonać ponowną korelację.

### Rebaseline po Etapie 1 — 2026-10-07

Po synchronizacji indeksu wykonano nowy pomiar na żywym repozytorium:

- `docs` zawiera **494 pliki**;
- `*.bak*` = **0**;
- `INDEX.yml` zawiera **494 wpisy**;
- korelacja filesystem ↔ `INDEX.yml`: **0 brakujących**, **0 martwych**, **0 duplikatów**;
- `INDEX.yml` jest poprawnym YAML; `file_count`, `status_counts` i `zone_counts` są zgodne z wpisami;
- `INDEX.md` został zsynchronizowany z bieżącą liczbą plików i planami PLAN-12/PLAN-13;
- Etap 1 jest **ZAKOŃCZONY**.

Repozytorium pozostaje aktywnie rozwijane; ten pomiar obowiązuje wyłącznie jako baseline dla kolejnego etapu i może ulec zmianie przed następnym zapisem.

## Etap 2 — status i historia

- oddzielić bieżące wyniki od historycznych;
- skorygować rozjazd `PLAN-12: WDROŻONY` kontra niewykonany rzeczywisty E2E;
- w `STATUS.md` pozostawić jawnie `542 passed, 1 failed` jako ostatni pełny wynik, dopóki nowszy pełny wynik go nie zastąpi;
- nie przepisywać historycznych wyników jako aktualnych;
- dopisać aktualny stan indeksu i pozostałych blockerów.

### Etap 3 — BUG/TODO

- każdą wykrytą niezgodność przypisać do istniejącego BUG/TODO albo utworzyć nowe zadanie tylko wtedy, gdy nie istnieje odpowiedni rekord;
- nie zamykać zadania na podstawie samego testu jednostkowego, jeżeli plan wymaga E2E;
- usunąć z `TODO` tylko po potwierdzonym spełnieniu kryterium exit gate;
- zachować historię zamkniętych zadań w changelogu/planach.

### Etap 4 — dokumentacja techniczna względem kodu

Zweryfikować na aktualnym kodzie, bez polegania na poprzednim snapshotcie:

- kontrakt `chunk → batch → request`;
- `source_language_code` / `target_language_code` TranslateGemma;
- `skip` przed backendem;
- marker/inline-code protection;
- `nested fields` / `complex fields` — formalny kontrakt, właściciel struktury, rekonstrukcja i testy;
- aktywne formaty względem `FilterRegistry`;
- lifecycle Filter Host, cache i llama.cpp;
- aktualny magazyn pluginów `.tplugin`;
- Apertium runtime i inventory.

Brak opisu w dokumentacji przy potwierdzonej funkcji traktować jako lukę dokumentacyjną, nie jako dowód braku funkcji.

### Etap 5 — repo boundary

Ustalić i zapisać w dokumentacji granicę:

- source;
- test;
- evidence;
- generated/build;
- backup;
- historyczne V3;
- root artifacts.

Rootowe dokumenty `adyt-raport-2026-10-05.md`, `plan-naprawczy-szkic.md` i `handoff-agent-okapi-filter-engine.md` nie mogą być automatycznie przenoszone. Najpierw ustalić ich status i docelową kategorię.

### Etap 6 — higiena generowanych artefaktów

- `*.bak*`: używać `tools/cleanup-bak.sh`;
- `__pycache__`, build artifacts i inne generowane pliki klasyfikować zgodnie z repo boundary;
- nie usuwać evidence ani backupów trwałych;
- aktualizować politykę i dokumentację po zmianie procesu.

### Etap 7 — końcowa korelacja

Warunek zakończenia:

```text
filesystem
    ↕
INDEX.yml
    ↕
INDEX.md
    ↕
STATUS / BUG / TODO / CHANGELOG
    ↕
kod + testy + runtime evidence
```

Każda różnica musi mieć wyjaśnienie w dokumentacji albo zostać naprawiona.

## Kryteria akceptacji

- brak nieobjaśnionych rozbieżności filesystem ↔ indeks;
- wszystkie aktywne plany są indeksowane;
- `STATUS` nie prezentuje starego PASS jako aktualnego;
- `BUG` i `TODO` zgadzają się z rzeczywistym stanem;
- `CHANGELOG` zawiera wykonane zmiany;
- dokumentacja techniczna opisuje potwierdzone kontrakty kodu;
- nested/complex fields mają jawny kontrakt albo jawnie oznaczoną lukę;
- wynik pełnego suite jest aktualny i jednoznaczny;
- historia pozostaje zachowana;
- brak ingerencji w aktywny kod niezwiązanej z remediacją dokumentacji.

## Kolejność realizacji

**0 → 1 → 2 → 3 → 4 → 5 → 6 → 7**.

Jeżeli w trakcie pracy zmieni się kod lub dokumentacja, etap 0 należy wykonać ponownie przed kontynuacją. Plan nie zakłada stabilnego snapshotu repozytorium.

## Stan

**AKTYWNY — plan naprawczy przygotowany 2026-10-07.**

## Etap 3 — wynik mapowania BUG/TODO — 2026-10-07

- Niezgodność indeksu została domknięta w `BUG-020`; jego historyczny wpis pozostaje zamknięty, a bieżący indeks ma osobny pomiar 494/494.
- Bieżący failure pełnego suite nie ma istniejącego dedykowanego TODO, dlatego utworzono `TODO-PLAN12-001`. Nie zmieniono testu ani implementacji w ramach remediacji dokumentacji.
- `TODO-DOC-013` pozostaje otwarte dla etapów 4–7; nie zamknięto go po samym uporządkowaniu indeksu.
- `BUG-025` / wcześniejsze `TODO-003` dokumentują historycznie potwierdzony rzeczywisty E2E TranslateGemma. `TODO-PLAN12-001` dotyczy węższego, nowego exit gate PLAN-12: relacji chunk → batch → liczba requestów.

## Etap 4 — wynik korelacji dokumentacja techniczna ↔ kod — 2026-10-07

Potwierdzono w aktualnym kodzie:

- `DocumentProcessor` wykonuje skip przed `translate_many`; pominięte jednostki wracają 1:1;
- `TranslationExecutor.execute_batch()` przekazuje cały logiczny chunk jako jeden batch i odrzuca brakujące/dodatkowe ID;
- `TranslationOrchestrator` wykonuje batch z retry całego chunka, a po dwóch błędach fallback jednostkowy;
- `LlamaCppAdapter.translate_batch()` buduje jeden request TranslateGemma z markerami `⟦TG_SEG_N⟧` i wymaga jednego source code dla całego batcha;
- `LlamaCppLanguageRouting` dla `auto` ustala source na podstawie całego dokumentu i zamraża go w orchestratorze;
- ochrona inline codes PUA → `__OKAPI_CODE_N__` jest wykonywana przed backendem, a restore przed walidacją/cache;
- `TranslationCache.close()` i `TranslationApp.close()` są obecne; Filter Host używa niedemonicznych reader threads;
- produkcyjny `FilterRegistry` odkrywa TPlugin z `$HOME/.config/tlumacz/filters/` / `TLUMACZ_FILTER_STORE`;
- `TXT` i `PDF` nie są aktywnymi filtrami głównego pipeline'u;
- nie istnieje wspólny domenowy kontrakt `nested fields` / `complex fields`. Zapisano tę lukę jawnie w `docs/technical-docs/translation-pipeline-contracts.md`.

Zaktualizowano `docs/technical-docs/functional-capabilities.md` i `docs/technical-docs/index.md`, aby nie przedstawiały statycznych klas filtrów jako równoznacznych z produkcyjną rejestracją TPlugin.

Etap 4 pozostaje **częściowo otwarty** wyłącznie w zakresie dalszego potwierdzenia E2E i ewentualnego projektowania kontraktu nested/complex fields; nie zmieniano kodu produkcyjnego.

## Etap 5 — granica repozytorium — 2026-10-07

Ustalona granica dla tej remediacji:

- `docs/` jest zakresem `INDEX.yml` (`scope: all-files-under-docs`);
- `README.md`, `STATUS.md`, `TODO.md`, `BUG.md`, `CHANGELOG.md` w katalogu głównym są źródłami projektu, ale nie są częścią indeksu dokumentacji `docs/`;
- trzy wykryte dokumenty rootowe `adyt-raport-2026-10-05.md`, `plan-naprawczy-szkic.md` i `handoff-agent-okapi-filter-engine.md` pozostają na miejscu. Nie są automatycznie przenoszone do `docs/`, ponieważ wymagałoby to decyzji migracyjnej i zmiany linków;
- V3, backupy trwałe, evidence i artefakty generowane nie są traktowane jako bieżąca dokumentacja tylko dlatego, że istnieją w drzewie projektu;
- nie usunięto ani nie przeniesiono żadnego pliku źródłowego w ramach etapów 1–5.

Etap 5 jest **ZAKOŃCZONY** na poziomie decyzji klasyfikacyjnej. Ewentualna migracja rootowych dokumentów wymaga osobnego zakresu i nie jest częścią PLAN-13.


### Rebaseline po utworzeniu dokumentu kontraktów — 2026-10-07

Dodanie `docs/technical-docs/translation-pipeline-contracts.md` zmieniło żywy baseline: `docs` = **495 plików**. Dokument został dodany do `INDEX.yml`; `INDEX.md` ma odpowiednio **495** oraz `technical: 20`. Przed Etapem 7 należy ponownie wykonać pełną korelację.


## Etap 6 — artefakty generowane i `*.bak*` — 2026-10-07

- `tools/cleanup-bak.sh` wykonano na całym repozytorium; usunięto **0** plików `*.bak*` w tym przebiegu, ponieważ wcześniejszy cleanup pozostawił stan czysty.
- Po operacji `find . -type f -name '*.bak*'` zwraca **0**.
- `tests/test_cleanup_bak.py`: **1 passed**; `bash -n tools/cleanup-bak.sh`: PASS.
- `__pycache__`/`.pyc`, `build/`, `temp/` oraz `backups/` pozostają rozdzielone od dokumentacji kanonicznej; trwałych backupów nie usuwano.

Etap 6 jest **ZAKOŃCZONY**.

## Etap 7 — końcowa korelacja — ZAKOŃCZONY

Końcowy pomiar po wszystkich zapisach potwierdził:

- `docs` = **495 plików**;
- `INDEX.yml` = **495 wpisów**;
- 0 duplikatów ścieżek;
- 0 brakujących plików względem indeksu;
- 0 martwych wpisów indeksu;
- 0 rozbieżności `size_bytes` dla wpisów posiadających to pole; dla `INDEX.yml` pole `size_bytes` jest świadomie pominięte, ponieważ sam indeks zmienia swój rozmiar przy każdej aktualizacji;
- poprawny YAML;
- `*.bak*` = **0**;
- najnowszy pełny suite: **542 passed, 1 failed**, jawnie pozostawiony jako wynik nie-GREEN;
- aktywne zadania techniczne, w tym `TODO-PLAN12-001`, pozostają w swoich właściwych rejestrach i nie zostały fałszywie zamknięte.

**PLAN-13 jest ZAMKNIĘTY.** Remediacja dokumentacji nie zamyka nierozstrzygniętych defektów kodu ani E2E; te pozostają w BUG/TODO.


## Aktualizacja po fizycznej segregacji — 2026-10-07

Na podstawie bezpośredniego zlecenia użytkownika wykonano fizyczną inwentaryzację i segregację dokumentacji. Dokumenty rozproszone w root `docs/` przeniesiono do właściwych stref: `Audyt/`, `Plany/`, `technical-docs/`, `wdrozenia/`, `release/`, `research/`, `reports/` oraz `archive/`. Materiały z `_inbox/` zostały rozpatrzone; pozostał tam wyłącznie `AGENT.md` sterujący tą strefą. Zaktualizowano odwołania do przeniesionych plików oraz przebudowano `INDEX.yml` i `INDEX.md`.

Bieżący pomiar po segregacji: **510 plików**, **510 wpisów INDEX.yml**, **0 brakujących**, **0 martwych**, **0 duplikatów**, **0 `*.bak*`**.
