# Audyt inżynierski kodu — 2026-10-01

## Cel
Ocena aktualnego drzewa V4 pod kątem poprawności, architektury, testów, jakości statycznej, uruchamiania i packagingu.

## Dowody wykonane na Bmax
- `python -m pytest -q` → **182 passed in 6.56s**.
- `ruff check .` → **FAIL, 6 błędów**.
- `mypy src` → **PASS, 60 plików źródłowych**.
- `python -m compileall -q src` → **PASS**.
- `python -m tlumacz --version` → **FAIL**.
- `tlumacz --version` nie był używany jako dowód końcowy w tej fazie.
- Snapshot projektu: 187 pozycji na głębokości audytowej, pełne drzewo zawiera źródła, testy, dokumentację i runtime.

## Ustalenia

### K1 — krytyczna niespójność uruchamiania modułowego
Repo zawiera `src/tlumacz/__main__.py`, ale bieżący interpreter importuje `tlumacz` z `/usr/lib/python3.14/site-packages/tlumacz`. Następnie `python -m tlumacz --version` kończy się brakiem `tlumacz.__main__`.

**Znaczenie:** komenda z README nie jest reprodukowalna z bieżącego checkoutu bez właściwego środowiska instalacyjnego/path.

### K2 — Ruff FAIL
Błędy:
- sortowanie importów w `src/tlumacz/filter_engine/processor.py`;
- ten sam problem w dwóch kopiach pod `temp/package`;
- trzy E402 w `tests/test_docx_filter.py`.

**Znaczenie:** quality gate dokumentowany jako PASS nie jest obecnie zielony.

### K3 — testy nie wykrywają problemu CLI
182 testy przechodzą, ale brak testu smoke dla `python -m tlumacz --version` w środowisku instalacyjnym. To luka w coverage kontraktu uruchomieniowego.

### K4 — testy i kod są obecne, architektura jest rozdzielona
Kod posiada warstwy `domain`, `application`, `backends`, `filter_engine`, `documents`, `infrastructure`, `interfaces`. Filter Engine korzysta z izolowanego Java Filter Host i JSON Lines. To jest zgodne z deklarowanym kierunkiem architektonicznym.

### K5 — Apertium pozostaje ryzykiem packagingowym
W `temp/apertium-build/apertium-en-pl` istnieją pliki źródłowe `*.t1x` i część binariów, ale dokumentacja deklaruje brak kompletnego `eng-pol.t1x.bin`. Ten obszar wymaga osobnego, reprodukowalnego build/validation flow, a nie ręcznego kopiowania binariów.

## Ocena
Kod ma wysoki poziom pokrycia testami i przechodzi pytest/mypy/compileall, ale nie spełnia obecnie wszystkich bramek jakościowych. Najważniejszy problem funkcjonalny dotyczy reprodukowalnego uruchamiania CLI, a jakościowy — Ruff.

## Zalecenia
1. Dodać test uruchomieniowy CLI.
2. Ustalić jednoznaczny sposób uruchamiania: clean venv/install lub kontrolowany `PYTHONPATH`; nie mieszać systemowego pakietu z checkoutem.
3. Naprawić Ruff w źródłach i testach; kopie w `temp/` traktować jako regenerowalne.
4. Zweryfikować wheel w czystym środowisku, uruchamiając zarówno console script, jak i `python -m tlumacz`.
5. Osobno zweryfikować Apertium eng-pol i dependency/licencje.



## Weryfikacja po naprawie
Po poprawkach końcowy stan: pytest 182 passed, Ruff PASS, mypy PASS, compileall PASS. Świeże środowisko z wheel uruchamia `python -m tlumacz --version` i `tlumacz --version`, oba zwracają 0.40.0. Nie zmieniano semantyki Apertium; blokada `cas_sp` pozostaje otwarta.
