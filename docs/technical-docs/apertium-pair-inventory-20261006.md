---
id: apertium-pair-inventory-20261006
status: evidence
meta:
  contentType: Audit
  category: evidence
version: 1.2.0
updated: 2026-10-06
owner: translation-backend
source:
  - Aperitium/
  - pary/
  - src/tlumacz/backends/apertium/
depends_on:
  - docs/technical-docs/apertium-pair-packages.md
  - docs/technical-docs/apertium-backend-integration.md
expires_when: zmiana paczek, runtime'u albo reguł discovery Apertium
last_validation: "właściwy smoke przez driver apertium: 27 READY + 0 FAIL + 0 TIMEOUT + 1 EXCLUDED; pełny pytest 477 passed; 2026-10-06"
---

# Audyt par Apertium — 2026-10-06

## Wynik audytu artefaktów

W `Aperitium/` znaleziono 14 repozytoriów par zawierających skompilowane kierunki oraz dodatkowe źródła niegotowe do publikacji.

Katalog `pary/` zawiera **28 osobnych paczek kierunkowych**. Sam fakt poprawnej instalacji paczki nie jest dowodem gotowości wykonawczej: runtime musi posiadać wszystkie programy pipeline'u wymienione przez `modes.xml`, a smoke musi potwierdzić rzeczywiste wykonanie.

## 28 przygotowanych kierunków

- bn-en, en-bn
- eng-cat, cat-eng
- eng-deu, deu-eng
- eng-ita, ita-eng
- eng-spa, spa-eng
- en-pt, pt-en
- pl-csb, csb-pl
- pl-sk, sk-pl
- pol-ces, ces-pol
- pol-rus, rus-pol
- pol-szl, szl-pol
- pol-ukr, ukr-pol
- pol-spa, spa-pol
- eng-pol, pol-eng

## Aktualna gotowość prywatnego runtime'u

Po uzupełnieniu prywatnego runtime'u o brakujące, już dostępne lokalnie programy pipeline'u:

**READY — 27 kierunków**

- bn-en, en-bn
- cat-eng, csb-pl, deu-eng, eng-cat, eng-deu, eng-ita, eng-pol, eng-spa
- en-pt, ita-eng, pl-csb, pl-sk, pol-ces, pol-eng, pol-rus, pol-szl, pol-spa
- pol-ukr, pt-en, rus-pol, sk-pl, spa-eng, spa-pol, szl-pol, ukr-pol

**EXCLUDED — 1 kierunek**

- `ces-pol`

`ces-pol` nie jest deklarowany jako gotowy. Rzeczywisty pipeline z dostarczonym `ces-pol.prob` powoduje wewnętrzną asercję `apertium-tagger` (`PerceptronSpec::StackValue`) dla zwykłych czeskich wejść i może zakończyć proces SIGABRT. Próba retrainingu modelu na dostarczonym korpusie nie usunęła objawu. Para pozostaje poza aktywnym scope release do czasu uzyskania zgodnego modelu taggera.

## Uzupełnione narzędzia prywatnego runtime'u

Do `src/tlumacz/backends/apertium/native_runtime/` dołączono bez instalacji systemowej:

- `bin/cg-proc` + `lib/libcg3.so.1` — wymagane przez pary z Constraint Grammar;
- `bin/lsx-proc` — istniejący lokalny artefakt z `Aperitium/.prefix/bin/`;
- `bin/apertium-anaphora` — wymagany przez `cat-eng` i `eng-cat`;
- `lib/libsqlite3.so.0` — zależność dynamiczna `cg-proc`.

Licencje GPL-3 dla CG-3 i Apertium Anaphora zostały dołączone do katalogu `LICENSES/`. Szczegóły źródeł relokacji znajdują się w `TOOLS-ADDITIONS.md`.

Nie wykonano instalacji ani usuwania pakietów systemowych.

## Dwukierunkowość

Źródłowe repozytorium może dostarczać dwa kierunki. Każdy kierunek jest publikowany osobno. Nie ma artefaktu typu `eng-spa+spa-eng.tar`.

## Artefakty

Katalog `pary/` zawiera 28 niekompresowanych tarów, odpowiadające pliki SHA-256 i `SHA256SUMS`.

## Weryfikacja

- testy Apertium: **48 passed**;
- testy GUI dotknięte bieżącą regresją: **2 passed**;
- smoke runtime po relokacji narzędzi: **27 READY / 1 EXCLUDED**;
- runtime użytkownika `$HOME/.config/tlumacz/apertium/`: **6 rzeczywistych par**;
- `ApertiumRuntime.language_pairs()` nie zwraca trybów pomocniczych jako par;
- wheel zbudowany w czystym staging-tree: **OK**; zawiera `cg-proc`, `lsx-proc`, `apertium-anaphora`, `libcg3.so.1` i `libsqlite3.so.0`.

## Zasada

**Źródło Apertium służy do kompilacji. Paczka Tłumacza służy do dystrybucji runtime. Gotowość publikacyjna wymaga zarówno kompletnych danych, jak i kompletnego pipeline'u wykonywalnego. `ces-pol` pozostaje jawnie wyłączone zamiast być fałszywie oznaczone jako READY.**
