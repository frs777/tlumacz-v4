# Dodatkowe narzędzia runtime — 2026-10-06

- `bin/cg-proc` — VISL CG-3, GPL-3.0-or-later; wymagany przez pary z Constraint Grammar.
- `lib/libcg3.so.1` — biblioteka VISL CG-3, GPL-3.0-or-later.
- `bin/apertium-anaphora` — Apertium Anaphora Resolution, GPL-3.0-or-later; wymagany przez `cat-eng` i `eng-cat`.
- `bin/lsx-proc` — Apertium Lexical Selection/Separable Processor z lokalnego prefixu projektu; wymagany przez `cat-eng`, `deu-eng`, `eng-cat`, `eng-deu`.
- `lib/libsqlite3.so.0` — SQLite, domena publiczna; zależność dynamiczna `cg-proc`.

Źródła binariów zostały zidentyfikowane lokalnie przed relokacją; nie wykonano instalacji systemowej.
