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
expires_when: changes to packages, the runtime, or Apertium discovery rules
last_validation: "proper smoke via Apertium driver: 27 READY + 0 FAIL + 0 TIMEOUT + 1 EXCLUDED; full pytest 477 passed; 2026-10-06"
---

# Apertium Pair Audit — 2026-10-06

## Artifact audit result

The `Aperitium/` directory contains 14 pair repositories with compiled directions, plus additional sources that are not ready for publication.

The `pary/` directory contains **28 separate directional packages**. Successful package installation alone is not evidence of execution readiness: the runtime must contain all pipeline programs listed by `modes.xml`, and the smoke test must confirm actual execution.

## 28 prepared directions

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

## Current readiness of the private runtime

After adding the missing pipeline programs already available locally to the private runtime:

**READY — 27 directions**

- bn-en, en-bn
- cat-eng, csb-pl, deu-eng, eng-cat, eng-deu, eng-ita, eng-pol, eng-spa
- en-pt, ita-eng, pl-csb, pl-sk, pol-ces, pol-eng, pol-rus, pol-szl, pol-spa
- pol-ukr, pt-en, rus-pol, sk-pl, spa-eng, spa-pol, szl-pol, ukr-pol

**EXCLUDED — 1 direction**

- `ces-pol`

`ces-pol` is not declared ready. The actual pipeline with the supplied `ces-pol.prob` triggers an internal `apertium-tagger` assertion (`PerceptronSpec::StackValue`) for ordinary Czech input and may terminate the process with SIGABRT. Retraining the model on the supplied corpus did not remove the symptom. The pair remains outside the active release scope until a compatible tagger model is obtained.

## Added private-runtime tools

The following were added to `src/tlumacz/backends/apertium/native_runtime/` without system installation:

- `bin/cg-proc` + `lib/libcg3.so.1` — required by Constraint Grammar pairs;
- `bin/lsx-proc` — existing local artifact from `Aperitium/.prefix/bin/`;
- `bin/apertium-anaphora` — required by `cat-eng` and `eng-cat`;
- `lib/libsqlite3.so.0` — dynamic dependency of `cg-proc`.

GPL-3 licenses for CG-3 and Apertium Anaphora were added to `LICENSES/`. Source relocation details are in `TOOLS-ADDITIONS.md`.

No system packages were installed or removed.

## Bidirectionality

The source repository may provide two directions. Each direction is published separately. There is no artifact such as `eng-spa+spa-eng.tar`.

## Artifacts

The `pary/` directory contains 28 uncompressed tars, corresponding SHA-256 files, and `SHA256SUMS`.

## Verification

- Apertium tests: **48 passed**;
- GUI tests affected by the current regression: **2 passed**;
- runtime smoke after tool relocation: **27 READY / 1 EXCLUDED**;
- user runtime `$HOME/.config/tlumacz/apertium/`: **6 actual pairs**;
- `ApertiumRuntime.language_pairs()` does not return helper modes as pairs;
- wheel built in a clean staging tree: **OK**; it contains `cg-proc`, `lsx-proc`, `apertium-anaphora`, `libcg3.so.1`, and `libsqlite3.so.0`.

## Principle

**Apertium source is used for compilation. The Tłumacz package is used for runtime distribution. Publication readiness requires both complete data and a complete executable pipeline. `ces-pol` remains explicitly excluded instead of being falsely marked READY.**