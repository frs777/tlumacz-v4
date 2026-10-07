---
id: plan-00-baseline-mapa-parytetu-v3-v4
status: plan
meta:
  contentType: ImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-06
owner: project-maintenance
source: docs/Audyt/AUDYT_FORENSICZNY_V3_V4_2026-10-01.md
depends_on: [docs/AGENTS.md, docs/INDEX.md, docs/archive/migration/MIGRATION_INVENTORY.md, docs/STATUS.md]
expires_when: wykonanie planu i utworzenie kanonicznej macierzy parytetu
last_validation: "rewalidacja read-only SentinelX + Apertium docs 2026-10-06"
---

# PLAN 00 — zamrożenie baseline i kanoniczna mapa V3 → V4

## Cel

Utworzyć odtwarzalny materiał referencyjny opisujący funkcjonalność istniejącą w V3 oraz jej status w aktualnym V4. Plan nie zmienia kodu.

## Krytyczne rozstrzygnięcie baseline

Repozytorium V3 posiada tag v0.31.2 (bfcb0fa), ale audyt wykazał również istotne pliki robocze nieobecne w tym tagu, m.in. tlumacz/cloud_providers.py oraz część materiałów filtrów. Nie wolno więc utożsamiać tagu z całym stanem roboczym użytym przy migracji.

Baseline budować z trzech warstw:
1. tag/commit V3 v0.31.2;
2. zachowany stan roboczy V3;
3. dokumentacja i audyty V3 opisujące funkcje obecne przed migracją.

Każdą rozbieżność między tymi warstwami zapisać jako fakt. Nie zgadywać, który wariant był źródłem migracji.

## Działania

1. Ustalić commit, tag, tracked/untracked i zmodyfikowane pliki V3.
2. Zbudować listę modułów Python, QML/Qt, konfiguracji, zasobów i testów V3.
3. Zbudować analogiczną listę V4.
4. Dla każdego modułu V3 wskazać odpowiednik V4, brak odpowiednika albo świadome zastąpienie.
5. Dla każdej funkcji GUI porównać kontrolkę, akcję, zapis stanu i efekt runtime.
6. Dla każdego providera Cloud porównać provider, transport, endpoint, model, klucz, timeout, limity, błędy i testy.
7. Dla każdego formatu dokumentu porównać extract, units, ochronę markerów, translate, reconstruct i validation.
8. Dla llama.cpp porównać start/stop/restart, port, model, compute, parallel, chat template, autostart, cache clear i restart po tłumaczeniu.
9. Dla konfiguracji wykonać porównanie round-trip i profili.
10. Dla testów wskazać, które kontrakty V3 zostały zastąpione kontraktami V4.
11. Oznaczyć funkcje już odtworzone w obecnym V4, aby nie planować ich ponownie.
12. Utworzyć listę niejednoznaczności. Każda pozycja bez dowodu otrzymuje VERIFY-FIRST.

## Klasyfikacja

Każdy element otrzymuje dokładnie jedną etykietę:
RESTORE, REBUILD, REPLACE, KEEP, RETIRED, DEAD albo VERIFY-FIRST.

DEAD wymaga dowodu braku callerów. RETIRED wymaga potwierdzenia w aktualnej dokumentacji V4.

## Kryterium wyjścia

Macierz musi zawierać:
V3 evidence → V4 location → status → required action → test proving parity → source documentation.

Plan 01 nie może uznać funkcji za brakującą wyłącznie na podstawie różnicy nazw plików.

## Bramy

V3 pozostaje nietknięty. Nie instalować ani nie usuwać zależności. Nie zmieniać zachowania V4.
## Raport wykonania — 2026-10-04

**Stan:** ZAKOŃCZONY — baseline zamrożony.

### Wykonane
- ustalono V3 tag v0.31.2; obiekt taga 060471a52ec9b213591ee54923f1de5996c14607 wskazuje na commit bfcb0facbe13f46e7e0cd72ee9dd66e70d11dc93;
- potwierdzono, że working tree V3 jest v0.31.2-dirty i zawiera 128 zmian/plików;
- wykonano inwentaryzację 57 aktywnych plików Python V3 oraz 70 plików Python V4;
- porównano moduły, backendy, GUI, Filter Engine, konfigurację i testowe kontrakty;
- rozdzielono funkcje zachowane, zastąpione, wycofane oraz niejednoznaczne;
- utworzono kanoniczną macierz docs/Audyt/PARYTET_V3_V4_MATRIX_2026-10-04.md;
- dodano osobną macierz pipeline'u dokumentowego;
- dodano macierz kontraktu providerów Cloud;
- wykazano, że V3 working tree zawiera detektor Lingua nieobecny w tagu i V4;
- wykazano, że TXT/PDF nie są obecnie aktywnie rejestrowane przez V4 FilterRegistry;
- wykazano, że DLXProvider istnieje w V4, ale profil DLX nie występuje w cloud_models.json;
- potwierdzono, że migracja Widgets → QML jest zastąpieniem architektury, a nie funkcją do ponownego odtwarzania.

### Brak zmian kodu
Zgodnie z planem 00 nie zmieniono kodu V3 ani V4. Nie instalowano ani nie usuwano zależności.

### Wynik dla planu 01
Plan 01 musi korzystać z macierzy jako źródła decyzji. Pozycje VERIFY-FIRST wymagają dowodu przed zmianą kodu. W szczególności: detekcja języka, TXT/PDF, DLX oraz pełny E2E formatów dokumentowych.


## Rewalidacja baseline — 2026-10-06

Wykonano ponowną walidację planu 00 na aktualnym stanie roboczym, bez zmian w kodzie V3 ani V4.

### Stan V3 potwierdzony bez modyfikacji

- tag v0.31.2 jest tagiem wskazującym commit bfcb0facbe13f46e7e0cd72ee9dd66e70d11dc93;
- obiekt taga 060471a52ec9b213591ee54923f1de5996c14607 jest obiektem typu tag, a nie committem; wcześniejsze sformułowanie „commit 060471...” było nieprecyzyjne i zostało skorygowane w tej rewalidacji;
- git status --porcelain=v1: 128 pozycji, w tym 62 zmiany śledzonych plików i 66 pozycji nieśledzonych;
- bieżący V3 pozostaje nietknięty przez tę pracę.

### Inwentaryzacja aktualnego V4

Ponowna inwentaryzacja źródła wykazała 66 plików Python pod src/tlumacz/, 6 plików QML, 61 plików testowych test_*.py, 14 plików Python Filter Engine i 20 plików Python backendów. Wartości te opisują stan bieżący; wcześniejsze 70 plików Python V4 pozostaje historycznym wynikiem inwentaryzacji wykonanej przy zamrożeniu baseline'u.

### Weryfikacja źródeł

Wnioski dotyczące Apertium zostały dodatkowo skonfrontowane z dokumentacją Apertium: para językowa jest kierunkowa na poziomie dostępnych trybów i nie wszystkie pary są rozwijane w obu kierunkach. Tryby są prekonfigurowanymi łańcuchami narzędzi dla konkretnej pary/kierunku. Nie zmienia to klasyfikacji V4; stan runtime/data pozostaje rozstrzygany przez rzeczywiste artefakty i testy projektu.

### Wynik

Plan 00 pozostaje wykonany jako faza baseline/parity. Nie wykonano zmian funkcjonalnych ani zmian w V3. Wykryto i skorygowano wyłącznie nieprecyzyjne oznaczenie identyfikatora taga V3 oraz dopisano aktualną rewalidację stanu.
