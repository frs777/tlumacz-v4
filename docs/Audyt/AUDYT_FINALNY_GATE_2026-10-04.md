---
id: audyt-finalny-gate-2026-10-04
status: evidence
meta:
  contentType: Audit
  category: governance
version: 1.0.0
updated: 2026-10-04
owner: project-maintenance
source: docs/Plany/05-FINALNY-GATE-I-ODBIOR.md
depends_on: [docs/STATUS.md, docs/BUG.md, docs/TODO.md, docs/INDEX.yml]
expires_when: zmiana zakresu release candidate lub wykonanie niezależnych blockerów
last_validation: "2026-10-04 — finalny gate wykonany świeżo"
---

# Audyt finalnego gate'u V4 — 2026-10-04

## Wynik ogólny

**RELEASE CANDIDATE / brak podstaw do oznaczenia jako final release.**

Kod V4 przechodzi bieżący zestaw testów i statycznych kontroli, a macierze backendów, dokumentów i GUI zostały sprawdzone. Pozostają jednak trzy niezależne blokery wydaniowe zapisane w `docs/BUG.md`: Apertium eng-pol/cas_sp, natywny Windows runtime oraz dependency closure/audyt licencji komponent-po-komponencie.

## Dowody

### Testy i static checks

- pełny pytest: **268 passed**;
- macierz backendów/cloud/Apertium/llama.cpp/TranslateGemma: **205 passed**;
- macierz formatów dokumentów: **28 passed**;
- Filter Host/Engine: **26 passed**;
- clean wheel install bez zależności: **PASS**;
- `python -m tlumacz --version` z wheel: **0.40.0**;
- import `tlumacz` z clean target wskazuje instalację wheel;
- rzeczywisty QML `Main.qml`: root załadowany poprawnie;
- compileall: **PASS**;
- Ruff: **PASS**;
- mypy: **PASS**;
- qmllint: **PASS**;
- kontrola sekretów w aktywnym kodzie/konfiguracji: brak znalezionych jawnych kluczy w skanowanym wzorcu;
- Cloud SecretStore: `/home/frs/.config/tlumacz/.key`, prawa `0600`.

### Dokumenty

Round-trip/Unicode/marker coverage istnieje w aktywnych testach DOCX, ODT, HTML, Markdown, EPUB i XLIFF. Łącznie macierz formatów dała 28 passed.

### V3

V3 pozostaje osobnym katalogiem roboczym. Stan przed i po bieżącej sesji ma 128 zmian względem `main`; bieżąca sesja nie wykonywała żadnej operacji zapisu w V3. Wersja bazowa V3 to `v0.31.2-dirty`.

### Indeks dokumentacji

`docs/INDEX.yml` został naprawiony: usunięto znaki sterujące i niepoprawne niecytowane wartości `title`. Parser YAML przechodzi, indeks zawiera **443/443** istniejących plików, bez duplikatów i brakujących ścieżek.

## Klasyfikacja

### BLOCKER

1. **BUG-001 — Apertium eng-pol/cas_sp.** Brak kompletnego artefaktu `eng-pol.t1x.bin`; kompilacja kończy się na `Undefined attr-item cas_sp`.
2. **BUG-002 — Windows runtime.** Brak kompletnego natywnego runtime Windows.
3. **BUG-003 — dependency closure/licencje.** Brak zamkniętego inventory całego redystrybuowanego runtime'u i obowiązków licencyjnych komponent-po-komponencie.

### IMPORTANT

1. **BUG-004 — ryzyko uruchomienia V3 zamiast V4.** `/usr/bin/tlumacz` nadal wskazuje globalną instalację V3. Nie zmieniano jej, zgodnie z zasadą braku destrukcyjnych zmian bez osobnej decyzji.
2. E2E TranslateGemma pełnym przepływem aplikacji pozostaje TODO; obecny dowód obejmuje benchmark rzeczywistego `translategemma-4b-it.Q5_K_M.gguf`, nie pełne E2E aplikacji.
3. V4 nie posiada własnego `.git`, dlatego `git diff --check` nie jest dostępny w katalogu projektu.

### SUGGESTION

1. Przed finalnym wydaniem wygenerować SBOM/third-party inventory dla całego wheel/runtime'u.
2. Dodać jawny test smoke dla wszystkich stron QML na rzeczywistym engine, nie tylko testy kontraktowe bridge.
3. Utrzymać osobny audit globalnego launchera, aby nie mieszać diagnostyki V3 i V4.

## Uwagi o brakującym E2E

Plan 05 odwołuje się do `tests/test_e2e_documents.py`, ale taki plik nie istnieje w V4. Nie potraktowano komunikatu `no tests ran` jako sukcesu. Zamiast tego uruchomiono wszystkie istniejące testy formatów i potwierdzono 28 testów round-trip/Unicode/markerów. Brakujący dedykowany suite E2E pozostaje jawnie oznaczony jako luka/TODO.

## Konkluzja

**Plan 05 może zostać zamknięty jako finalny quality/release-candidate gate, ale artefakt nie może zostać uczciwie oznaczony jako final release 0.40.0.** Niezależne blokery release pozostają otwarte i są zgodne z `docs/BUG.md` oraz `docs/release/RELEASE_NOTES_0.40.0.md`.
