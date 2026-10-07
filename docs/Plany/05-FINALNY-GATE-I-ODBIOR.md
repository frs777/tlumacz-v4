## 2026-10-06 — świeży gate po dalszych zmianach V4

Wykonano ponowny finalny gate na aktualnym stanie projektu.

### Wyniki

- pełny pytest: **373 passed, 1 failed**;
- jedyna porażka: `tests/test_apertium_runtime.py::test_bundled_runtime_programs_are_owner_executable` — 34 pliki bundlowanego runtime Apertium mają tryb `674` zamiast bitu `u+x`;
- próba korekty `chmod u+x` z bieżącej sesji została odrzucona przez ACL, ponieważ pliki należą do użytkownika `frs`, a sesja działa jako `sentinelx`; nie zmieniano właściciela plików ani nie obchodzono ACL;
- Ruff: **PASS**;
- mypy: **PASS**, 67 plików źródłowych;
- compileall: **PASS**;
- qmllint: **PASS** dla wszystkich 6 plików QML;
- macierz backendów, dokumentów, GUI i packagingu: **181 passed**;
- launcher `uruchom-tlumacz-v4.sh`: składnia i bit wykonywania **PASS**;
- `python -m tlumacz --version`: **FAIL**, brak `tlumacz.__main__`;
- `/usr/bin/tlumacz --version`: nie jest wiarygodnym testem V4 — wskazuje globalną instalację V3 i kończy się przerwaniem procesu;
- clean-wheel build nie zakończył się, ponieważ backend builda został zatrzymany przez ochronę Git `dubious ownership` dla `/home/frs/Projekty`.

### Decyzja

**Plan 05 pozostaje zamknięty jako Release Candidate, nie final release.** Świeży gate nie daje podstaw do oznaczenia projektu jako finalnego wydania.

Niezależne blokery wymagają osobnej operacji wykonywanej jako właściciel plików/repozytorium: przywrócenie `u+x` dla prywatnego runtime Apertium oraz ustalenie właściwego kontraktu entrypointu V4/clean-wheel bez używania globalnego V3.

---

---
id: plan-05-finalny-gate-i-odbior
status: closed
meta:
  contentType: ImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-04
owner: project-maintenance
source: docs/AGENTS.md
depends_on: [docs/Plany/01-RESTORE-BRAKUJACE-FUNKCJE.md, docs/Plany/02-REDUKCJA-NADMIAROWEGO-KODU.md, docs/Plany/03-NAPRAWA-REGRESJI.md, docs/Plany/04-OPTYMALIZACJA.md]
expires_when: końcowy zestaw testów, audyt diffu i dokumentacja są aktualne
last_validation: "finalny gate 2026-10-04 — 268 passed; backend/doc/gui matrix PASS; RC z 3 blockerami release"
---

# PLAN 05 — końcowy gate jakości i odbiór

## Cel

Potwierdzić spójność V4 po odzyskaniu funkcji, redukcji kodu, naprawie regresji i optymalizacji.

## 1. Zakres

Sprawdzić wszystkie zmodyfikowane pliki, brak zmian V3, brak zmian poza zakresem, brak sekretów i brak nowych zależności bez decyzji.

## 2. Static checks

Uruchomić świeżo:
- pełny pytest;
- Ruff;
- mypy;
- compileall;
- qmllint dla QML, jeżeli dostępny;
- packaging tests, jeżeli dotknięto packagingu.

Nie wpisywać wyniku bez świeżego uruchomienia.

## 3. Backend matrix

Dla llama.cpp, Cloud, Apertium i Własny sprawdzić:
selection, configuration, persistence, execution, cancellation, error i result validation.

FastAPI/OpenVINO pozostają poza aktywnym runtime.

## 4. Document matrix

Dla DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF wykonać round-trip oraz test Unicode/markerów.

## 5. GUI matrix

Sprawdzić Tłumaczenie, API i serwer, Przełączniki, Pomoc, motywy, geometrię, skills, glossary, progress, log i preview na rzeczywistym uruchomieniu QML.

## 6. Environment matrix

Sprawdzić:
python -m tlumacz --version,
tlumacz.__file__,
launcher,
clean venv/wheel,
brak zależności od V3.

Nie usuwać globalnego V3.

## 7. Dokumentacja

Po zmianach zaktualizować STATUS, TODO, BUG, CHANGELOG, właściwe technical-docs, INDEX.md, INDEX.yml i DOCUMENTATION_CHANGELOG.md. Każdy nowy dokument musi mieć front matter zgodny z docs/AGENTS.md.

## 8. Review

Wykonać niezależny przegląd architektury, bezpieczeństwa, workflow, GUI, regresji i packagingu. Wynik ma rozdzielać blocker, important i suggestion.

## Definition of Done

- RESTORE ma dowód;
- DEAD ma zero-reference evidence;
- każda regresja ma test;
- każda optymalizacja ma pomiar;
- testy są zielone;
- dokumentacja odpowiada kodowi;
- V3 pozostaje nienaruszony;
- hipotezy nie są prezentowane jako fakty.

## Niezależne blokery release

Pozostają osobno: Apertium eng-pol/cas_sp, Windows runtime, dependency closure i audyt licencji. Ich otwarcie oznacza RC, nie final release.

## Wynik końcowy — 2026-10-04

Plan 05 wykonano jako finalny gate jakości i Release Candidate.

### Zweryfikowane

- pełny pytest: **268 passed**;
- backend/cloud/llama.cpp/Apertium/TranslateGemma: **205 passed**;
- DOCX/ODT/HTML/Markdown/EPUB/XLIFF: **28 passed**;
- Filter Host/Engine: **26 passed**;
- clean install wheel bez zależności: **PASS**;
- wheel `tlumacz-0.40.0-py3-none-any.whl`: wersja **0.40.0**;
- QML `Main.qml`: rzeczywisty engine załadował root;
- Ruff, mypy, compileall, qmllint: **PASS**;
- `docs/INDEX.yml`: parser YAML PASS, **444/444** ścieżek istnieje, 0 duplikatów;
- V3: bieżący stan nadal **128 zmian**, bez zapisu do V3 podczas tej sesji;
- Cloud SecretStore: `/home/frs/.config/tlumacz/.key`, `0600`.

### Rozbieżność / luka

Plan odwołuje się do `tests/test_e2e_documents.py`, którego nie ma w V4. Komunikat `no tests ran` nie został zaliczony jako sukces. Zamiast tego wykonano istniejącą macierz testów formatów i potwierdzono 28 testów round-trip/Unicode/markerów. Dedykowane E2E pozostaje TODO.

### Blockery niezależne od gate'u

- Apertium eng-pol / `cas_sp`;
- Windows runtime;
- dependency closure i pełny inventory licencji runtime'u.

### Ważne ograniczenie środowiskowe

`/usr/bin/tlumacz` nadal wskazuje globalną instalację V3. Nie zmieniano jej bez osobnej decyzji. V4 działa i jest weryfikowane przez `python -m tlumacz` z projektu oraz przez clean wheel target.

Katalog V4 nie zawiera `.git`, dlatego `git diff --check` pozostaje niedostępny; nie jest raportowany jako PASS.

### Decyzja

**Plan 05 — ZAMKNIĘTY. Status projektu: RELEASE CANDIDATE, nie final release.**
