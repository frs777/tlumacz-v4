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
expires_when: Änderungen an Paketen, der Laufzeit oder den Apertium-Discovery-Regeln
last_validation: "ordnungsgemäßer Smoke-Test über den Apertium-Treiber: 27 READY + 0 FAIL + 0 TIMEOUT + 1 EXCLUDED; vollständiges pytest 477 passed; 2026-10-06"
---

# Audit der Apertium-Paare — 2026-10-06

## Ergebnis des Artefakt-Audits

In `Aperitium/` wurden 14 Pair-Repositorys mit kompilierten Richtungen sowie zusätzliche Quellen gefunden, die noch nicht zur Veröffentlichung bereit sind.

Das Verzeichnis `pary/` enthält **28 separate Richtungs-Pakete**. Die erfolgreiche Installation eines Pakets allein ist kein Nachweis der Ausführungsbereitschaft: Die Laufzeit muss alle in `modes.xml` genannten Pipeline-Programme enthalten, und der Smoke-Test muss die tatsächliche Ausführung bestätigen.

## 28 vorbereitete Richtungen

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

## Aktuelle Bereitschaft der privaten Laufzeit

Nach Ergänzung der bereits lokal verfügbaren, fehlenden Pipeline-Programme in der privaten Laufzeit:

**READY — 27 Richtungen**

- bn-en, en-bn
- cat-eng, csb-pl, deu-eng, eng-cat, eng-deu, eng-ita, eng-pol, eng-spa
- en-pt, ita-eng, pl-csb, pl-sk, pol-ces, pol-eng, pol-rus, pol-szl, pol-spa
- pol-ukr, pt-en, rus-pol, sk-pl, spa-eng, spa-pol, szl-pol, ukr-pol

**EXCLUDED — 1 Richtung**

- `ces-pol`

`ces-pol` wird nicht als bereit deklariert. Die tatsächliche Pipeline mit dem mitgelieferten `ces-pol.prob` löst bei normalen tschechischen Eingaben eine interne Assertion von `apertium-tagger` (`PerceptronSpec::StackValue`) aus und kann den Prozess mit SIGABRT beenden. Ein Retraining des Modells mit dem bereitgestellten Korpus beseitigte das Symptom nicht. Das Paar bleibt bis zur Verfügbarkeit eines kompatiblen Tagger-Modells außerhalb des aktiven Release-Scopes.

## Ergänzte Werkzeuge der privaten Laufzeit

Folgende Dateien wurden ohne Systeminstallation nach `src/tlumacz/backends/apertium/native_runtime/` übernommen:

- `bin/cg-proc` + `lib/libcg3.so.1` — erforderlich für Paare mit Constraint Grammar;
- `bin/lsx-proc` — vorhandenes lokales Artefakt aus `Aperitium/.prefix/bin/`;
- `bin/apertium-anaphora` — erforderlich für `cat-eng` und `eng-cat`;
- `lib/libsqlite3.so.0` — dynamische Abhängigkeit von `cg-proc`.

GPL-3-Lizenzen für CG-3 und Apertium Anaphora wurden in `LICENSES/` aufgenommen. Details zur Herkunft der Relokationen stehen in `TOOLS-ADDITIONS.md`.

Es wurden keine Systempakete installiert oder entfernt.

## Bidirektionalität

Das Quell-Repository kann zwei Richtungen bereitstellen. Jede Richtung wird separat veröffentlicht. Es gibt kein Artefakt wie `eng-spa+spa-eng.tar`.

## Artefakte

Das Verzeichnis `pary/` enthält 28 unkomprimierte Tars, die zugehörigen SHA-256-Dateien und `SHA256SUMS`.

## Verifizierung

- Apertium-Tests: **48 passed**;
- GUI-Tests, die von der aktuellen Regression betroffen sind: **2 passed**;
- Runtime-Smoke nach der Relokation der Werkzeuge: **27 READY / 1 EXCLUDED**;
- Benutzer-Runtime `$HOME/.config/tlumacz/apertium/`: **6 tatsächliche Paare**;
- `ApertiumRuntime.language_pairs()` gibt Hilfsmodi nicht als Paare zurück;
- in einem sauberen Staging-Tree gebautes Wheel: **OK**; es enthält `cg-proc`, `lsx-proc`, `apertium-anaphora`, `libcg3.so.1` und `libsqlite3.so.0`.

## Grundsatz

**Die Apertium-Quelle dient der Kompilierung. Das Tłumacz-Paket dient der Distribution der Laufzeit. Veröffentlichungsbereitschaft erfordert sowohl vollständige Daten als auch eine vollständige ausführbare Pipeline. `ces-pol` bleibt ausdrücklich ausgeschlossen, statt fälschlich als READY markiert zu werden.**