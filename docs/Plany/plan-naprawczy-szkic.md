# Szkic planu naprawczego — Tłumacz V4
## Data: 2026-10-05
## Dokument wejściowy
adyt-raport-2026-10-05.md

Cel: dostarczyć architektowi oprogramowania uporządkowany szkielet do przygotowania szczegółowego planu naprawczego. Ten dokument nie jest jeszcze instrukcją implementacji.

# Zasady

1. Najpierw blokery release, potem refaktory.
2. Każdy problem naprawiany test-first.
3. Żadnej migracji architektury bez zachowania istniejących kontraktów.
4. Każdy etap ma mieć mierzalny exit gate.
5. Nie usuwać funkcji historycznych bez potwierdzenia macierzy V3/V4.
6. Nie usuwać backupów/artefaktów bez osobnej decyzji.
7. Każda zmiana release'owa kończy się aktualizacją dokumentacji źródeł prawdy.
8. Po każdym etapie: pytest + Ruff + mypy + compileall + qmllint oraz odpowiedni test integracyjny.

# FAZA 0 — zamrożenie baseline

Cel:
- ustalić dokładny stan source;
- ustalić granicę repozytorium;
- ustalić canonical release source;
- oddzielić source/evidence/generated/backup.

Zadania:
- ustalić, czy V4 ma być osobnym repo;
- zdefiniować .gitignore;
- oznaczyć build/temp/cache/backups;
- zidentyfikować aktualny wheel jako artefakt historyczny;
- zamrozić aktualny wynik 297 passed;
- utworzyć macierz funkcja → kod → test → dokumentacja → release status.

Exit:
- jednoznaczny source of truth;
- jednoznaczny release artifact;
- brak niejasności, który Python/pakiet jest V4.

# FAZA 1 — P0: Apertium

Cel:
doprowadzić Apertium do powtarzalnego, relokowalnego runtime.

Zadania:
- odtworzyć właściwe dane językowe;
- ustalić minimalny zakres par na release;
- usunąć hardcoded ścieżki V3 z artefaktów;
- naprawić runtime data directory;
- zweryfikować cg-proc i pozostałe binaria;
- ustalić poprawny model -d;
- zbudować self-contained fixture;
- przetestować relocation;
- przetestować cold start bez starego V3;
- zweryfikować licencje i NOTICE;
- dopiero potem rozszerzać eng-pol.

Test gates:
- runtime discovery > 0;
- każda deklarowana para przechodzi smoke translation;
- brak /home/frs/Projekty/agent-translator-v3 w artefaktach;
- runtime działa z nowej lokalizacji;
- wheel zawiera wymagane dane.

Exit:
Apertium jest samodzielnym, relokowalnym komponentem release.

# FAZA 2 — P0: packaging i release artifact

Cel:
zbudować wheel odpowiadający dokładnie aktualnemu source.

Zadania:
- naprawić build metadata/Git boundary;
- usunąć zależność builda od niepoprawnego nadrzędnego checkoutu;
- zdefiniować version source;
- sprawdzić package-data;
- dodać QML;
- dodać help Markdown;
- dodać SVG;
- dodać Apertium runtime/data;
- zdefiniować manifest release;
- oznaczyć stare wheele jako historical.

Test:
source → build → unzip inspection → clean environment → install → import → CLI → QML smoke.

Exit:
nowy wheel zawiera dokładnie aktywny kod i wszystkie runtime assets.

# FAZA 3 — P1: security i lifecycle

Cel:
zamknąć sekrety i zasoby procesu.

Zadania:
- usunąć local/custom API key z AppSettings JSON;
- rozszerzyć SecretStore;
- zachować migrację starej konfiguracji;
- dodać test braku sekretu w JSON;
- dodać TranslationApp.close();
- zamknąć TranslationCache;
- zatrzymać llama.cpp przy aboutToQuit;
- zweryfikować worker/thread cleanup;
- dodać shutdown regression test.

Exit:
- brak sekretów w settings JSON;
- brak ResourceWarning;
- brak orphan runtime;
- clean shutdown.

# FAZA 4 — P1: quality gates

Cel:
doprowadzić statyczną jakość do zielonego stanu.

Zadania:
- Ruff src;
- Ruff tests;
- mypy;
- usunięcie niepotrzebnych callback lambda;
- uporządkowanie testów;
- wprowadzenie jednego lokalnego command quality gate.

Exit:
- Ruff PASS;
- mypy PASS;
- compileall PASS;
- pytest PASS;
- qmllint PASS.

# FAZA 5 — P1: funkcjonalna macierz formatów

Cel:
usunąć rozjazd między GUI a FilterRegistry.

Opcje architektoniczne:
A. rzeczywiście wdrożyć TXT/PDF;
B. usunąć TXT/PDF z GUI skill affordance;
C. oznaczyć je jako planned/experimental i blokować start.

Zadanie architekta:
wybrać wariant na podstawie docelowej macierzy V4.

Exit:
każdy format widoczny w GUI ma jednoznaczny status i test.

# FAZA 6 — P1: TranslateGemma i integracje

Cel:
zamknąć specjalny tryb jako funkcję release.

Zadania:
- real model fixture;
- language detection;
- prompt contract;
- output validation;
- failure/cancellation;
- performance baseline;
- repeatability.

Exit:
pełny E2E na realnym modelu lub jednoznaczne oznaczenie funkcji jako non-release.

# FAZA 7 — P1: Windows / portability

Cel:
określić rzeczywisty target release.

Zadania:
- decyzja Linux-only vs Linux+Windows;
- jeśli Windows: launcher, paths, process ownership, Qt runtime, Apertium/native dependencies;
- test clean machine/environment;
- no absolute /home paths.

Exit:
documented supported platforms + automated smoke.

# FAZA 8 — P2: QML cleanup

Dopiero po stabilizacji backend/release.

Zadania:
- usunąć 1-second refreshSkills timer;
- przejść na event-driven model;
- ujednolicić spacing;
- ujednolicić control widths;
- naprawić Apertium source/target layout;
- rozstrzygnąć base font 15 vs 17;
- ograniczyć font.bold: false;
- poprawić Help tabs pod keyboard/accessibility;
- przejrzeć focus order;
- przeprowadzić screenshot-based UI audit.

Exit:
- visual baseline;
- keyboard navigation;
- stable narrow/wide layouts;
- no QML warnings.

# FAZA 9 — P2: dekompozycja bridge

Cel:
zmniejszyć sprzężenie bez zmiany zachowania.

Proponowany podział:
- TranslationViewModel;
- BackendSettingsModel;
- ServerRuntimeController;
- SkillsModel;
- GlossaryModel;
- HelpModel;
- SettingsService;
- SecretService.

Metoda:
1. characterization tests;
2. wydzielenie jednej odpowiedzialności;
3. green;
4. następna odpowiedzialność;
5. dopiero na końcu usunięcie aliasów.

Exit:
bridge jest cienką warstwą prezentacyjną.

# FAZA 10 — dependency/licence closure

Zadania:
- potwierdzić użycie openai;
- potwierdzić użycie PyMuPDF;
- potwierdzić użycie markdown-it-py;
- usunąć tylko po potwierdzeniu;
- zbudować lock/constraints strategy;
- inventory bibliotek bundlowanych;
- license mapping;
- NOTICE;
- SBOM, jeżeli wymagany przez release.

Exit:
każda zależność ma ownera, cel, wersję i licencję.

# FAZA 11 — repository hygiene

Zadania:
- wydzielić repo V4;
- ustalić .gitignore;
- source/evidence/generated/backup separation;
- przenieść historyczne buildy;
- wydzielić test environments;
- oznaczyć 70 MB corrupt help jako evidence;
- nie trzymać node_modules/cache/build w source.

Exit:
repo zawiera tylko rzeczy potrzebne do developmentu/release/evidence zgodnie z polityką projektu.

# FAZA 12 — documentation synchronization

Źródła prawdy:
- STATUS.md;
- ARCHITECTURE.md;
- TODO.md;
- BUG.md;
- CHANGELOG.md;
- functional-capabilities;
- INDEX.md;
- INDEX.yml.

Zadania:
- usunąć historyczne wyniki z bieżących sekcji;
- zachować historyczne raporty jako historyczne;
- poprawić 445 vs 457;
- zaktualizować release blockers;
- dopisać wszystkie potwierdzone bugi;
- zsynchronizować matrix funkcji.

Exit:
kod, testy i dokumentacja opisują ten sam stan.

# FAZA 13 — CI/CD

Minimalny pipeline:
1. repository integrity;
2. dependency install;
3. Ruff;
4. mypy;
5. compileall;
6. pytest;
7. coverage threshold;
8. qmllint;
9. package build;
10. wheel content audit;
11. clean install;
12. CLI smoke;
13. QML smoke;
14. release manifest;
15. artifact checksum.

Exit:
release candidate nie może być zbudowany, jeżeli którykolwiek gate krytyczny jest czerwony.

# FAZA 14 — final release gate

Warunki:
- P0 = 0;
- P1 release blockers = 0;
- test suite green;
- static quality green;
- package reproducible;
- clean install green;
- QML smoke green;
- Apertium self-contained;
- secrets isolated;
- shutdown green;
- docs synchronized;
- supported platforms explicitly declared.

Dopiero wtedy:
- release candidate;
- final audit;
- release notes;
- checksum;
- rollback procedure;
- sign-off.

# Priorytet dla architekta

Najpierw:
P0 Apertium + packaging.

Potem:
P1 security/lifecycle + quality gates + format contract + TranslateGemma + platform.

Dopiero potem:
P2 QML cleanup + bridge decomposition + repo cleanup.

Nie zaczynać od kosmetycznego rewrite'u QML ani od pełnej przebudowy bridge przed zamknięciem P0.


# FAZA 15 — wiarygodność testów i mutation resistance

Cel:
utrzymać test suite jako rzeczywisty mechanizm wykrywania regresji, a nie tylko dowód zgodności implementacji z jej własnymi mockami.

Zadania:
- utrzymać zasadę real implementation > fake > stub > mock;
- dla każdego testu oznaczonego E2E wymagać rzeczywistego runtime'u/artefaktu;
- kontrolowane fake runtime'y oznaczać jednoznacznie jako integration test doubles;
- rozszerzyć mutation testing o walidację kontraktów domenowych;
- dodać target-language validation regression;
- dodać clean-wheel verification po naprawie builda;
- dodać shutdown/lifecycle regression;
- dodać reprezentatywny test stanu końcowego DocumentTranslationService;
- okresowo wykonywać mutation sampling dla krytycznych modułów.

Exit:
- krytyczne mutacje są wykrywane;
- żaden test E2E nie jest w rzeczywistości tylko testem mocka/stuba;
- każdy release blocker ma test reprodukujący jego awarię;
- test suite ma wyraźny podział unit / integration / E2E / release smoke.


# FAZA 16 — zamknięcie testów packaging i lifecycle

Status: WYKONANA.

Zamknięto:
- clean-wheel build/install/import verification;
- centralny shutdown TranslationApp;
- QML aboutToQuit lifecycle binding;
- pełny test cache SQLite + llama.cpp runtime + Qt event loop;
- korektę testu QML oczekującego historycznej nazwy właściwości.

Pozostaje:
- BUG-006 — build z aktualnego nadrzędnego checkoutu Git/ACL;
- BUG-007–009 — brak zamkniętego runtime/data Apertium;
- nowy release smoke test Apertium celowo pozostaje czerwony przy 0 parach językowych.
