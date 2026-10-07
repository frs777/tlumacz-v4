---
id: plan-04-apertium-2026-10-05
status: active
meta:
  contentType: ModuleImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-05
owner: platform-architecture
priority: P0
depends_on: [docs/Plany/PLAN-2026-10-05.md]
last_validation: "audyt 2026-10-05"
---
# PLAN-03 — Apertium runtime i backend

## 1. Oczekiwany rezultat
Zbudować samodzielny, relokowalny runtime Apertium z rzeczywistymi danymi językowymi i podłączyć go przez wspólny kontrakt backendu.

## 2. Zakres odpowiedzialności
apertium adapter/runtime/discovery; modes.xml/mode files; monolingual data; bilingual pair data; cg-proc i inne zewnętrzne binaria, jeśli para ich wymaga; ISO mapping; packaging/licensing.

## 3. Schemat budowy
```text
```text
ApertiumBackend
  ├─ Config
  ├─ Runtime discovery
  ├─ Language-pair registry
  └─ Adapter → apertium/cg-proc/etc.
              ↓
        TranslationUnit[]
```
```

## 4. Połączenia z innymi modułami
Core przekazuje jednostki. Packaging dostarcza runtime. GUI pokazuje tylko pary faktycznie gotowe. Nie importować Apertium do main/QML.

## 5. Szczegółowy plan wdrożenia
1. Zmapować brakujące artefakty i zależności.
2. Ustalić minimalny release scope par.
3. Odtworzyć dane z właściwych źródeł.
4. Usunąć ścieżki V3.
5. Naprawić cas_sp i wygenerować transfer binaries.
6. Zweryfikować discovery.
7. Uruchomić każdą deklarowaną parę z clean workspace.
8. Wykonać relokację całego runtime.
9. Dopiero potem zamknąć packaging.

## 6. Wymagania i zależności
Research Apertium potwierdza, że para jest zbiorem danych instalowanych pod share/apertium, a artefakty t1x/t2x/t3x są generowane z reguł transferu. Nie traktować samego modes jako dowodu gotowości.

## 7. Szczegóły integracji
GUI ma otrzymywać tylko gotowe pary. Core dostaje tekstowe units. Apertium nie modyfikuje dokumentu ani markerów poza uzgodnionym kontraktem.

## 8. Exit gate
Discovery > 0; deklarowane pary przechodzą smoke; eng→pol działa; brak ścieżek V3; brak zależności od starego drzewa; runtime działa po przeniesieniu; wheel zawiera wymagane dane.

## 9. Zasady
Nie zmieniać innych modułów tylko po to, aby uprościć implementację tego modułu. Każda zmiana kontraktu wymaga aktualizacji testów, dokumentacji i głównego PLAN-2026-10-05.md.