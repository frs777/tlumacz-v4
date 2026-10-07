---
id: plan-11-dokumentacja-repo-2026-10-05
status: active
meta:
  contentType: ModuleImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-05
owner: platform-architecture
priority: P1/P2
depends_on: [docs/Plany/PLAN-2026-10-05.md]
last_validation: "audyt 2026-10-05"
---
# PLAN-10 — Dokumentacja i higiena repozytorium

## 1. Oczekiwany rezultat
Utrzymać dokumentację jako aktualne źródło prawdy oraz uporządkować granicę source/evidence/generated/backup bez utraty historii.

## 2. Zakres odpowiedzialności
STATUS; BUG; TODO; ARCHITECTURE; CHANGELOG; INDEX.md/yml; plans; audits; source/evidence/generated/backup; repo boundary.

## 3. Schemat budowy
```text
```text
Kod + testy + audyty
        ↓
źródła prawdy docs/
        ↓
INDEX.yml → INDEX.md
        ↓
release evidence
```
```

## 4. Połączenia z innymi modułami
Każdy moduł po zmianie aktualizuje właściwe źródła prawdy. Main PLAN agreguje status integracji.

## 5. Szczegółowy plan wdrożenia
1. Dodać wszystkie nowe plany do INDEX.
2. Uaktualniać STATUS po każdym milestone.
3. Rozdzielać historyczne wyniki od current state.
4. Usunąć sprzeczność 445/457.
5. Zaktualizować BUG po każdej weryfikacji.
6. Dopisać CHANGELOG.
7. Klasyfikować 70 MB corrupt help jako evidence albo usuwać tylko po zgodzie.
8. Ustalić repo boundary i .gitignore.
9. Po final gate wykonać pełną korelację kod↔test↔docs.

## 6. Wymagania i zależności
Nie usuwać dokumentacji historycznej tylko dlatego, że jest nieaktualna. Historyczne raporty pozostają historyczne.

## 7. Szczegóły integracji
INDEX.md i INDEX.yml muszą odzwierciedlać filesystem. STATUS nie może prezentować historycznego PASS jako bieżącego.

## 8. Exit gate
Brak sprzecznych bieżących wyników; indeks zgodny z filesystem; wszystkie plany są indeksowane; changelog zawiera zmiany; finalny audit ma jedno źródło prawdy.

## 9. Zasady
Nie zmieniać innych modułów tylko po to, aby uprościć implementację tego modułu. Każda zmiana kontraktu wymaga aktualizacji testów, dokumentacji i głównego PLAN-2026-10-05.md.