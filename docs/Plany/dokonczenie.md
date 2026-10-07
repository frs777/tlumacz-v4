---
id: dokonczenie-v4
status: active
meta:
  contentType: Reference
  category: governance
version: 0.40.0
updated: 2026-10-04
owner: project-engineering
source: docs/Audyt/AUDYT_FINALNY_GATE_2026-10-04.md
depends_on: [docs/STATUS.md, docs/TODO.md, docs/BUG.md, docs/Audyt/AUDYT_FINALNY_GATE_2026-10-04.md, docs/Audyt/PARYTET_V3_V4_MATRIX_2026-10-04.md]
expires_when: zamknięcie wszystkich blockerów Release Candidate 0.40.0 lub formalna zmiana zakresu wydania
last_validation: "korelacja z finalnym gate'em Plan 05 i stanem V4 2026-10-04"
---

# Dokończenie Tłumacza V4

## Cel

Ten dokument rekomenduje kolejność dalszych prac po zamknięciu Planów 00–05. Projekt jest obecnie **Release Candidate 0.40.0**, a nie finalnym wydaniem.

Nie rekomenduje się kolejnego ogólnego audytu. Następny cykl powinien być prowadzony jako **domykanie konkretnych blockerów i braków odbiorowych**.

## Stan wyjściowy

Na zakończenie Planu 05 potwierdzono:

- pełny suite: **268 passed**;
- macierz backendów: **205 passed**;
- macierz formatów: **28 passed**;
- Filter Host/Engine: **26 passed**;
- compileall, Ruff, mypy i qmllint: **PASS**;
- clean install z wheel 0.40.0: **PASS**;
- rzeczywisty start głównego QML: **PASS**;
- integralność `docs/INDEX.yml`: **444/444** ścieżek, 0 duplikatów;
- Cloud SecretStore: `/home/frs/.config/tlumacz/.key`, prawa `0600`.

Pozostają trzy blokery wydaniowe:

1. **Apertium eng-pol / `cas_sp`;**
2. **Windows runtime;**
3. **dependency closure i audyt licencyjny.**

Dodatkowo pozostają dwa zadania ważne dla kompletności odbioru:

4. **pełne E2E TranslateGemma przez rzeczywistą aplikację;**
5. **osobna decyzja dotycząca globalnego `/usr/bin/tlumacz`, który nadal wskazuje V3.**

## Rekomendowana kolejność

### 1. Apertium eng-pol / `cas_sp` — P0

To jest pierwszy ruch, ponieważ problem dotyczy kompletności jednego z aktywnych backendów i jest znanym blockerem migracji.

#### Zakres

- odtworzyć minimalny przypadek problemu dla pary eng-pol;
- ustalić, z którego źródła pochodzi wymagany transfer `eng-pol.t1x.bin`;
- porównać źródło V3, artefakty V4 i aktywną wersję Apertium;
- zidentyfikować przyczynę `Undefined attr-item cas_sp`;
- nie maskować problemu przez wyłączenie reguły lub zmianę kontraktu bez dowodu;
- po uzyskaniu poprawnego artefaktu zweryfikować go w czystej instalacji wheel.

#### Kryterium zamknięcia

- `eng-pol.t1x.bin` jest poprawnie generowany lub pozyskany z udokumentowanego źródła;
- para eng-pol przechodzi test runtime;
- istnieje regresja testująca `cas_sp`;
- wheel zawiera wymagany artefakt;
- dokumentacja Apertium opisuje źródło artefaktu i ograniczenia licencyjne;
- blocker BUG-001 zostaje zamknięty dopiero po przejściu tych punktów.

**Nie rekomenduje się przechodzenia do finalnego release przed zamknięciem tego punktu.**

### 2. Dependency closure i licencje — P0

Ten etap powinien zostać wykonany przed finalnym pakietowaniem, ponieważ jego wynik wpływa na zawartość release'u.

#### Zakres

- sporządzić pełny inventory zależności Python, Java, Apertium/lingua-rs i innych runtime'ów dostarczanych w wheel;
- rozdzielić zależności uruchomieniowe od narzędzi developerskich/testowych;
- ustalić źródło, wersję i licencję każdego komponentu bundlowanego w artefakcie;
- sprawdzić kompletność NOTICE/licencji;
- potwierdzić, że sposób dystrybucji każdego komponentu jest zgodny z jego licencją;
- przygotować SBOM lub równoważny maszynowy rejestr komponentów.

#### Kryterium zamknięcia

- brak nieznanych zależności runtime;
- brak nieudokumentowanych komponentów bundlowanych;
- kompletna lista licencji i NOTICE;
- wynik zapisany w dokumentacji release;
- ewentualne wyjątki są jawnie zaakceptowane przed wydaniem.

**Nie instalować nowych zależności tylko po to, aby zamknąć audyt. Najpierw wykorzystać istniejące źródła i artefakty projektu.**

### 3. Windows runtime — P0 dla deklarowanego wsparcia Windows

Nie należy deklarować pełnego wsparcia Windows, dopóki runtime natywny nie jest dostępny i przetestowany.

#### Zakres

- określić minimalny wymagany zakres Windows dla 0.40.0;
- ustalić komplet natywnych artefaktów potrzebnych przez Apertium i pozostałe komponenty;
- przygotować sposób ich dostarczenia w pakiecie;
- wykonać clean install na Windows;
- uruchomić co najmniej smoke test aplikacji, backendów i filtrów wymagających runtime;
- sprawdzić ścieżki plików, procesów, kodowania i zakończenia procesu.

#### Kryterium zamknięcia

Albo:

- Windows runtime jest kompletny i przechodzi ustalony zestaw testów,

albo:

- Windows zostaje jawnie wyłączony z zakresu wydania 0.40.0, a release notes i dokumentacja użytkownika są odpowiednio skorygowane.

**Nie należy utrzymywać niezweryfikowanej obietnicy „Windows support”.**

### 4. Pełne E2E TranslateGemma — P1

Ten punkt nie jest obecnie blockerem architektury, ale jest wymagany do uznania ścieżki TranslateGemma za rzeczywiście odbiorową.

#### Zakres

Test powinien przejść przez rzeczywistą ścieżkę aplikacji:

**GUI/TranslationApp → przygotowanie dokumentu → wykrycie języka → TranslateGemma prompt → llama.cpp → walidacja → rekonstrukcja → wynik.**

Należy użyć rzeczywistego modelu GGUF z `/home/frs/Modele/`.

#### Kryterium zamknięcia

- test wykonuje pełny przepływ aplikacji, nie tylko adapter;
- źródło i język docelowy są poprawnie przekazywane jako kody ISO 639-1;
- wynik przechodzi ResultValidator;
- istnieje regresja automatyczna;
- test jest powtarzalny albo ma udokumentowane wymagania sprzętowe.

### 5. Globalny launcher `/usr/bin/tlumacz` — P1 / decyzja operacyjna

Obecnie globalne polecenie nadal wskazuje instalację V3. Nie należy zmieniać tego automatycznie, ponieważ V3 ma własny, niezależny stan roboczy.

#### Rekomendacja

Najpierw podjąć decyzję, czy:

- `/usr/bin/tlumacz` ma zostać przełączony na V4,
- ma pozostać launcherem V3,
- czy należy wprowadzić osobne, jawne launchery V3/V4.

Dopiero po decyzji wykonać zmianę i pełny smoke test.

**Nie wykonywać tej zmiany jako części naprawy blockerów bez osobnej akceptacji.**

## 6. Finalny gate po zamknięciu blockerów

Dopiero po punktach P0 należy wykonać jeden końcowy gate, zamiast kolejnego szerokiego audytu.

### Wymagane dowody

- pełny pytest;
- compileall;
- Ruff;
- mypy;
- qmllint;
- clean install z finalnego wheel;
- test wszystkich aktywnych backendów;
- test aktywnych formatów dokumentów;
- Apertium eng-pol;
- TranslateGemma E2E;
- test Windows, jeśli Windows pozostaje w zakresie;
- walidacja dependency/licencji/SBOM;
- kontrola sekretów i praw `0600`;
- kontrola `docs/INDEX.yml`;
- potwierdzenie wersji artefaktu i SHA-256;
- aktualizacja `STATUS.md`, `TODO.md`, `BUG.md`, `CHANGELOG.md` i dokumentacji release.

## 7. Warunek przejścia do final release

Rekomenduję przyjąć prostą zasadę:

> **0 otwartych blockerów P0 + komplet dowodów finalnego gate'u = możliwość oznaczenia 0.40.0 jako final release.**

Jeżeli Windows nie zostanie domknięty, ale zostanie formalnie wyłączony z zakresu wydania, nie powinien być traktowany jako ukryty blocker. Zakres wydania musi wtedy jasno wskazywać platformy i ograniczenia.

## 8. Czego teraz nie robić

- nie rozpoczynać kolejnego generalnego refaktoru;
- nie wykonywać kolejnego ogólnego audytu V3 → V4 bez nowej przesłanki;
- nie zmieniać globalnego `/usr/bin/tlumacz` bez osobnej decyzji;
- nie usuwać ani nie modyfikować V3 jako sposobu naprawy V4;
- nie instalować nowych pakietów bez uzasadnienia i zgody;
- nie oznaczać projektu jako final release tylko dlatego, że pełny pytest przechodzi;
- nie uznawać braku testu za PASS.

## 9. Proponowana kolejność wykonawcza

| Priorytet | Zadanie | Status | Wynik wymagany |
|---|---|---|---|
| P0 | Apertium eng-pol / `cas_sp` | blocker | działający artefakt + runtime + regresja |
| P0 | dependency closure + licencje | blocker | inventory + licencje + SBOM/NOTICE |
| P0 | Windows runtime | blocker* | działający runtime albo formalne wyłączenie z zakresu |
| P1 | TranslateGemma full E2E | TODO | pełny przepływ aplikacji |
| P1 | decyzja o `/usr/bin/tlumacz` | otwarte | świadoma decyzja operacyjna |
| P1 | finalny gate | oczekuje | komplet dowodów i 0 blockerów |

* Windows jest blockerem tylko wtedy, gdy Windows ma pozostać deklarowaną platformą wydania 0.40.0.

## 10. Rekomendacja końcowa

**Następnym ruchem powinno być domknięcie Apertium eng-pol / `cas_sp`.**

Po nim należy wykonać dependency/licensing closure oraz równolegle zamknąć decyzję o zakresie Windows. TranslateGemma E2E powinno zostać wykonane przed finalnym gate'em, ale nie powinno blokować prac nad Apertium ani audytem zależności.

Po zamknięciu tych punktów należy wykonać jeden, świeży finalny gate i dopiero na jego podstawie zmienić status projektu z **Release Candidate** na **final release**.
