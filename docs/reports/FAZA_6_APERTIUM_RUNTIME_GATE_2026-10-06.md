---
id: faza-6-apertium-runtime-gate-2026-10-06
status: evidence
meta:
  contentType: VerificationReport
  category: evidence
version: 1.1.0
updated: 2026-10-06
owner: translation-backend
source:
  - src/tlumacz/backends/apertium/language_plugins.py
  - src/tlumacz/backends/apertium/runtime.py
  - src/tlumacz/backends/apertium/native_runtime/
  - tests/test_apertium_language_plugins.py
  - tests/test_apertium_runtime.py
  - tests/test_qml_gui.py
depends_on:
  - docs/Plany/PLAN-04-APERTIUM-2026-10-05.md
expires_when: kolejna zmiana kontraktu discovery/runtime Apertium
last_validation: "właściwy smoke drivera Apertium 27 READY/0 FAIL/0 TIMEOUT/1 EXCLUDED; pełny pytest 477 passed; wheel staging OK; 2026-10-06"
---

# FAZA 6 — Apertium runtime gate — 2026-10-06

## Cel

Domknięcie części planu dotyczącej rzeczywistego runtime'u Apertium, discovery, relokowalności, kompletności pipeline'u oraz publikowania wyłącznie par faktycznie wykonywalnych.

## Wykonane

1. Zmapowano aktywny backend, runtime, discovery, GUI bridge i testy.
2. Zweryfikowano prywatny runtime Apertium 3.9.12.
3. Wykonano relokowany test runtime.
4. Wykonano smoke wszystkich 28 przygotowanych paczek.
5. Dodano do discovery kontrolę programów wymienionych w `modes.xml`.
6. Ograniczono `ApertiumRuntime.language_pairs()` do rzeczywistych kierunków `source-target`.
7. Dodano testy regresyjne dla brakujących i dostępnych programów runtime.
8. Dołączono do prywatnego runtime istniejące lokalnie: `cg-proc`, `libcg3.so.1`, `lsx-proc`, `apertium-anaphora` i `libsqlite3.so.0`.
9. Uzupełniono dokumentację licencyjną i manifest runtime.
10. Zweryfikowano wheel w czystym staging-tree; artefakt zawiera nowe narzędzia runtime.
11. Naprawiono deterministyczność testu GUI, który wcześniej zależał od języka zapisanego w prywatnej konfiguracji użytkownika.

## Wyniki

- pełny suite projektu: **477 passed**;
- właściwy smoke drivera Apertium: **27 READY / 0 FAIL / 0 TIMEOUT / 1 EXCLUDED**;
- testy Apertium: **48 passed**;
- regresje GUI: **2 passed**;
- prywatny runtime: **Apertium 3.9.12**;
- relokacja runtime: **OK**;
- 28 paczek: **27 READY / 1 EXCLUDED**;
- aktywny katalog użytkownika `/home/frs/.config/tlumacz/Apertium/`: **6 rzeczywistych par**;
- wheel staging: **OK**;
- wheel: `dist/tlumacz-0.40.0-py3-none-any.whl`, SHA-256 `f8e9a9ab4b5924cb93708e7dbaed25a76a6c2ed173c6338f071b135ccb321028`.

## Jedyna wyłączona para

`ces-pol` pozostaje poza release scope. Dostarczony `ces-pol.prob` powoduje wewnętrzną asercję `apertium-tagger` (`PerceptronSpec::StackValue`) dla części zwykłych czeskich wejść i może zakończyć proces SIGABRT. Próba retrainingu modelu na dostarczonym korpusie nie usunęła objawu. Nie oznaczono pary jako READY tylko dlatego, że proces dla pojedynczego wejścia może zakończyć się kodem 0.

## Narzędzia runtime

Do prywatnego runtime dołączono wyłącznie istniejące lokalnie binaria/biblioteki, bez instalowania pakietów systemowych. `TOOLS-ADDITIONS.md` opisuje pochodzenie i rolę narzędzi. Licencje GPL-3 dla CG-3 i Apertium Anaphora zostały skopiowane do `LICENSES/`.

## Backup

Przed zmianą discovery/runtime wykonano backup:

- `backups/plan-04-apertium-before-discovery-fix-20261006-221425.tar`
- SHA-256: `351f979bbddcf50c60cfab92007bcc4b48b2af05803bab8990d5515f5db4e1`

Przed dokumentacją wykonano backup:

- `backups/plan-04-apertium-before-docs-20261006-221901.tar`
- SHA-256: `6766a85f5148e6df929d168aefb16763fdff8027e2fdd927ad8366224bc37bbc`

Przed uzupełnieniem runtime narzędziami wykonano backup:

- `backups/plan-04-apertium-before-runtime-tools-20261006-223408.tar`
- SHA-256: `f2abbdb360bc7362a100bcd7dd7b8d9c5bfa329473533da66e07c666081f139a`

Backupy pozostawiono; niczego nie usuwano.

## Packaging / Okapi

Bezpośredni `python3 -m build --wheel` w istniejącym drzewie nadal kończy się `Operation not permitted` na starym artefakcie Okapi, ponieważ proces budujący nie jest właścicielem tego pliku i setuptools próbuje zmienić jego metadane w `build/lib`. Nie zmieniano właściciela ani uprawnień pliku.

Czysty staging-tree, z którego pliki zostały odtworzone jako użytkownik wykonujący build, przechodzi budowę wheel. To zamyka gate artefaktu bez naruszania uprawnień istniejącego Okapi.

## Status planu

**Runtime/discovery Apertium: DOMKNIĘTY.**

**Packaging wheel: ZWERYFIKOWANY przez staging-tree.**

**`ces-pol`: jawnie wyłączone z release scope z powodu potwierdzonej awarii taggera.**

Nie ma podstaw do oznaczania `ces-pol` jako gotowego. Pozostałe 27 paczek spełnia kontrakt runtime gate.
