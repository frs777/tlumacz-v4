---
id: plan-10-testy-ci-2026-10-05
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
# PLAN-09 — Testy, wiarygodność testów i CI

## 1. Oczekiwany rezultat
Zamienić istniejący silny suite testowy w automatyczny, warstwowy release gate.

## 2. Zakres odpowiedzialności
57 modułów testowych, kontrakty, mutation sampling, unit/integration/E2E/release smoke, coverage, Ruff, mypy, qmllint, packaging, CI.

## 3. Schemat budowy
```text
```text
Unit → Contract → Integration → E2E → Release Smoke
                         ↓
                 package/clean install
                         ↓
                    CI gate
```
```

## 4. Połączenia z innymi modułami
Testy każdego modułu pozostają blisko odpowiedzialności. CI jest cross-cutting i nie przenosi logiki aplikacji.

## 5. Szczegółowy plan wdrożenia
1. Zweryfikować baseline aktualnych testów.
2. Utrzymać mutation sampling krytycznych kontraktów.
3. Każdy E2E musi używać realnego runtime/artefaktu.
4. Dodać reprezentatywny final-state document test.
5. Utrzymać clean-wheel test.
6. Utrzymać lifecycle test.
7. Dodać format matrix.
8. Zbudować repo CI.
9. Zapisać release manifest/checksum.
10. Wymusić fail-fast dla P0 gate.

## 6. Wymagania i zależności
Nie używać realnej sieci w domyślnych unit tests. Test doubles muszą być nazwane zgodnie z rzeczywistą granicą.

## 7. Szczegóły integracji
CI uruchamia dokładnie te same komendy, które są wymagane ręcznie. Wynik ma być artefaktem release evidence.

## 8. Exit gate
Green pytest/Ruff/mypy/compileall/qmllint/build/clean install/QML smoke; brak testu udającego E2E; krytyczne mutacje są wykrywalne.

## 9. Zasady
Nie zmieniać innych modułów tylko po to, aby uprościć implementację tego modułu. Każda zmiana kontraktu wymaga aktualizacji testów, dokumentacji i głównego PLAN-2026-10-05.md.
## 10. Walidacja wykonana 2026-10-07

Lokalny release gate został wykonany na aktualnym drzewie projektu.

| Gate | Wynik | Dowód |
|---|---|---|
| pytest | PASS | 595 passed |
| Ruff | PASS | `All checks passed!` |
| mypy | PASS | 79 source files, no issues |
| compileall | PASS | exit 0 |
| qmllint | PASS | exit 0 |
| mutation sampling | PASS | 3/3 critical mutations killed |
| format matrix | PASS | 13 production suffixes covered |
| real-runtime E2E | PASS | bundled Apertium + final DOCX state |
| clean wheel | PASS | wheel audit: 239 entries |
| clean install | PASS | installed `tlumacz-0.40.0` |
| QML smoke | PASS | `Main.qml` created root object |
| CLI smoke | PASS | `python -m tlumacz --help` |
| release evidence | PASS | `dist-ci/SHA256SUMS` + `release-manifest.json` |
| workflow YAML | PASS | parsed locally |

### Ustalenia i korekty

1. Usunięto przyczynę czerwonego testu persystencji hosta: test nie może oczekiwać zdalnego adresu dla lokalnego serwera llama.
2. Naprawiono błędy Ruff/mypy ujawnione przez pełny gate; zmiany są bezpieczne semantycznie (typowanie/importy) poza testowym uszczelnieniem kontraktu hosta.
3. Wykryto błąd w istniejącym CI: wheel był kopiowany do nazwy `dist-ci.whl`, której pip nie akceptuje jako nazwy wheel. Workflow używa teraz rzeczywistej nazwy `tlumacz-*.whl` w katalogu `dist-ci/`.
4. Dodano jawny fail-fast przez `defaults.run.shell: bash` oraz deterministyczny mutation sampling.
5. Dodano final-state E2E dla rzeczywistego bundled Apertium i poprawnego artefaktu DOCX oraz format matrix dla 13 aktywnych rozszerzeń.

### Status

Plan pozostaje `active` do czasu wykonania rzeczywistego workflow na runnerze CI. Lokalny odpowiednik wszystkich gate'ów zakończył się pozytywnie.
