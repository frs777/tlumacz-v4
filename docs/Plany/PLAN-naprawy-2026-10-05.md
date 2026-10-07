---
id: plan-naprawy-2026-10-05
status: active
meta:
  contentType: RecoveryPlan
  category: plans
version: 1.0.0
updated: 2026-10-05
owner: platform-architecture
source:
  - docs/BUG.md
  - adyt-raport-2026-10-05.md
  - plan-naprawczy-szkic.md
depends_on: [docs/Plany/PLAN-2026-10-05.md]
expires_when: BUG-001..030 zamknięte albo formalnie wycofane
last_validation: "execution gate 2026-10-06; BUG-001, BUG-005..015, BUG-017, BUG-019, BUG-020, BUG-022..024, BUG-030 verified closed; remaining blockers documented"
---
# PLAN-naprawy-2026-10-05
## Stan wykonania — 2026-10-06

Zamknięte i zweryfikowane w ramach tego planu:
- P0: BUG-001, BUG-006, BUG-007, BUG-008, BUG-009, BUG-013;
- P1 release: BUG-005, BUG-010, BUG-011, BUG-012, BUG-014, BUG-015;
- dalsze pozycje wykonane bezpośrednio na kodzie: BUG-017, BUG-019, BUG-020, BUG-022, BUG-023, BUG-024, BUG-030;
- BUG-027 częściowo wykonany: usunięto potwierdzone nieużywane zależności `openai`, `PyMuPDF`, `markdown-it-py` i zweryfikowano graf resolvera bez instalacji; brak lock/constraints pozostaje otwarty.

Weryfikacja nowych zmian: pełny pytest 319 passed, Ruff PASS, mypy PASS, compileall PASS, qmllint PASS, clean-wheel build PASS. Indeks dokumentacji został doprowadzony do zgodności z filesystemem: 472 kanoniczne pliki, w tym `docs/BUILD.md`.

Pozostają: BUG-002/026 Windows/macOS runtime — odłożone do przyszłego etapu, BUG-003/027 dependency closure/licencje, BUG-004 globalny launcher V3, BUG-018/021 porządkowanie artefaktów wymagające decyzji, BUG-025 rzeczywiste E2E TranslateGemma — wykonywane na modelu z `$HOME/Modele`, oraz BUG-028/029 i pozostałe P2 wskazane niżej. Repozytorium Git do synchronizacji z GitHubem znajduje się poza katalogiem V4; BUG-016 jest poza zakresem lokalnego source tree.
\n## Cel
Zamknąć wszystkie krytyczne i poważne problemy wskazane w docs/BUG.md bez mieszania napraw funkcjonalnych z kosmetycznym refaktorem.

## P0 — obowiązkowe
| BUG | Problem | Segment | Exit |
|---|---|---|---|
| 006 | reprodukowalny build wheel | 00 + 08 | build z aktualnego source |
| 007 | Apertium bez danych | 03 | discovery > 0 + smoke |
| 008 | ścieżki V3 w Apertium | 03 | zero hardcoded V3 |
| 009 | Apertium nie jest zamkniętym runtime | 03 + 08 | relokacja + clean install |
| 013 | wheel niezgodny ze source | 08 | canonical artifact zgodny ze source |
| 001 | eng-pol / cas_sp | 03 | realne eng → pol przez Filter Engine |

BUG-001 ma obecnie P1 w BUG.md, ale dla finalnego release traktujemy go jako P0 funkcjonalny: deklarowana para Apertium musi być rzeczywiście działająca.

Naprawa Apertium: odtworzyć źródła i zależności → ustalić kierunkowość → naprawić cas_sp → wygenerować artefakty transfer → smoke runtime → eng→pol → aktywny Filter Engine. Nie tworzyć placeholderowego .t1x.bin.

## P1 — bezpieczeństwo, jakość i funkcje
### BUG-005 — quality gate
Ruff src/tests, mypy, compileall, pytest, qmllint. Naprawiać tylko błędy potwierdzone w aktualnym source.

### BUG-010 — local/custom API key
SecretStore ma być jedynym właścicielem sekretu. Test zapisu JSON ma potwierdzać brak sekretu; test restartu ma potwierdzać odczyt wyłącznie przez SecretStore.

### BUG-011 — shutdown
Centralne TranslationApp.close(), zamknięcie SQLite, stop llama.cpp, worker cleanup, QML aboutToQuit i test pełnego lifecycle. Uwaga: audyt zawiera opis implementacji, ale BUG.md nadal oznacza problem jako otwarty; przed zmianą statusu trzeba zweryfikować aktualny kod/test.

### BUG-012 — TXT/PDF
Wybrać: A) implementacja filtrów, B) usunięcie affordance, C) planned/experimental z blokadą startu. Do decyzji nie przedstawiać ich jako aktywnych formatów.

### BUG-014 — SVG
Manifest assets + test wheel content + clean install + QML smoke.

### BUG-015 — CI
Ruff → mypy → pytest → compileall → qmllint → build → wheel audit → clean install → CLI/QML smoke.

### BUG-016/017 — granica repo
Ustalić osobne repo V4 i lokalny .gitignore. Migrację wykonać jako osobny, kontrolowany krok z rollbackiem.

### BUG-019/020 — dokumentacja
STATUS/ARCHITECTURE/active technical docs mają aktualne wyniki; historyczne wyniki zostają w historii. INDEX.md = INDEX.yml = filesystem.

### BUG-025 — TranslateGemma
Rzeczywisty GGUF → jawny en→pl → detekcja Lingua → request → response → ResultValidator → zapis dokumentu → cancellation/failure → rzeczywisty przepływ GUI.

### BUG-026 — Windows
Linux-only wymaga formalnej zmiany zakresu. Linux+Windows wymaga natywnego runtime/package/smoke. Nie pozostawiać Windows jako supported bez runtime.

### BUG-027 — dependency closure
Inventory wersji/source/license/NOTICE; potwierdzenie użycia; lock/constraints; usuwanie tylko po dowodzie.

### BUG-004 — V3/V4
Launcher/interpreter provenance test i dokumentacja dokładnej komendy V4. Globalnego V3 nie usuwać bez osobnej decyzji.

### BUG-030 — launcher
Launcher developerski może być lokalny; release launcher musi być relokowalny.

## P2 — utrzymanie
- BUG-018: klasyfikacja source/evidence/generated/backup; usuwanie dopiero po zgodzie.
- BUG-021: corrupt help przenieść do evidence/backup albo usunąć po osobnej decyzji.
- BUG-022: refreshSkills event-driven zamiast pollingu 1 s.
- BUG-023/024: QML style debt i font — jedno źródło prawdy.
- BUG-028: etapowa dekompozycja bridge po characterization tests.
- BUG-029: keyboard/focus/accessibility/scaling audit.
- BUG-035: opcjonalna warstwa live integration Cloud; nie zastępować nią unit tests.

## Problemy już skorygowane według dokumentacji
- BUG-031 — test Apertium nazwany E2E skorygowany; produktowy runtime nadal niesprawny.
- BUG-032 — dodano target-language regression.
- BUG-033 — clean-wheel verification dodane.
- BUG-034 — lifecycle test opisany jako dodany.
- BUG-036 — test QML przepisany do aktualnego kontraktu.

Przed formalnym zamknięciem tych pozycji należy ponownie zweryfikować kod i aktualny wynik testów.

## Krytyczna kolejność
1. BUG-006 + BUG-013
2. BUG-007 + BUG-008 + BUG-009 + BUG-001
3. BUG-014
4. BUG-005
5. BUG-010 + BUG-011
6. BUG-012
7. BUG-025
8. BUG-027
9. BUG-026
10. BUG-015
11. BUG-016 + BUG-017 + BUG-018 + BUG-021
12. BUG-019 + BUG-020
13. BUG-022..030

## Finalny warunek
Nie oznaczać final release, dopóki P0 = 0, P1 release blockers = 0, canonical wheel pochodzi z aktualnego source, Apertium działa z relokowanego runtime, GUI nie deklaruje nieobsługiwanych funkcji, lifecycle jest czysty, a CI potrafi odtworzyć gate.