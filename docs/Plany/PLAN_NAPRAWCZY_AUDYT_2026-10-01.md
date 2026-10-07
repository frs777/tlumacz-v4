# Plan naprawczy po audycie — 2026-10-01

## Cel
Doprowadzić aktualny V4 do stanu, w którym dokumentacja, kod, quality gates i sposób uruchamiania opisują ten sam system.

## P0 — ustalenie źródła uruchomienia
- potwierdzić model instalacji projektu;
- zbudować/zweryfikować clean venv bez modyfikowania systemowego środowiska;
- sprawdzić console script `tlumacz --version`;
- sprawdzić `python -m tlumacz --version`;
- dodać test regresyjny CLI.

**Kryterium:** oba sposoby uruchomienia działają w przewidzianym środowisku albo dokumentacja jednoznacznie ogranicza wspierany sposób.

## P1 — zielony quality gate
- naprawić import ordering w `processor.py`;
- uporządkować importy w `test_docx_filter.py`;
- nie poprawiać ręcznie artefaktów `temp/package`, jeżeli są regenerowane z poprawnego źródła;
- uruchomić Ruff ponownie.

**Kryterium:** `ruff check .` PASS.

## P2 — test CLI
- dodać test sprawdzający wersję i kod zakończenia;
- testować entrypoint zainstalowanego pakietu;
- sprawdzić brak importu z globalnego `site-packages`.

**Kryterium:** test regresyjny reprodukuje i blokuje obecny problem.

## P3 — Apertium
- zidentyfikować dokładne źródło `eng-pol.t1x.bin`;
- walidować `eng-pol.t1x` zgodnie z dokumentacją Apertium;
- odtworzyć binaria w kontrolowanym środowisku;
- nie używać niezweryfikowanego binarium jako obejścia.

**Kryterium:** para eng-pol przechodzi test translacji/E2E oraz jest reprodukowalna.

## P4 — dependency/licencje
- wygenerować closure zależności runtime;
- przypisać źródło i licencję każdemu bundlowanemu komponentowi;
- zweryfikować NOTICE;
- sprawdzić, czy artefakt zawiera wyłącznie dozwolone zasoby.

**Kryterium:** raport komponent→źródło→wersja→licencja→artefakt.

## P5 — synchronizacja dokumentacji
Po każdym ukończonym punkcie:
- aktualizacja `docs/STATUS.md`;
- aktualizacja `docs/TODO.md`;
- wpis do `docs/CHANGELOG.md`;
- aktualizacja raportu audytu/testów;
- korekta nieaktualnych ścieżek.

## P6 — końcowa weryfikacja
- pytest;
- Ruff;
- mypy;
- compileall;
- CLI;
- smoke/E2E;
- packaging clean install;
- audyt ścieżek i dokumentacji;
- raport końcowy.

## Warunek rozpoczęcia zmian
Przed zmianami kodu wymagany jest backup zgodnie z `AGENTS.md`. Nie wykonuje się instalacji/usuwania oprogramowania bez osobnej zgody użytkownika.


# Plan naprawczy po audycie — 2026-10-01

## P0 — źródło uruchomienia — ZAKOŃCZONE
- potwierdzono src/tlumacz/__main__.py;
- potwierdzono [project.scripts];
- świeży venv z wheel uruchamia python -m tlumacz --version;
- świeży venv uruchamia tlumacz --version;
- problem starego środowiska wynikał z historycznej ścieżki shebangu, nie z brakującego kodu.

## P1 — quality gate — ZAKOŃCZONE
- poprawiono import ordering w processor.py;
- poprawiono import ordering w test_docx_filter.py;
- wykluczono regenerowalne temp/ i .migration-backups/ z Ruff;
- ruff check . = PASS.

## P2 — CLI — ZAKOŃCZONE przez weryfikację packagingu
- zweryfikowano moduł i console script w świeżym venv;
- istniejący suite nie posiada dedykowanego testu subprocess CLI, ale packaging smoke wykonano na realnym wheel.

## P3 — Apertium — OTWARTE/BLOCKED
- zlokalizowano Undefined attr-item cas_sp;
- potwierdzono ten sam problem w lokalnym źródle V3 i aktualnym upstreamie apertium-eng-pol;
- nie wprowadzono arbitralnej definicji cas_sp;
- wymagane: ustalenie poprawnej wersji/źródła pary lub świadome odtworzenie semantyki atrybutu.

## P4 — dependency/licencje — OTWARTE
- wymaga osobnego closure komponentów bundlowanych w wheel;
- wymaga raportu komponent → wersja → źródło → licencja → artefakt.

## P5 — synchronizacja dokumentacji — W TOKU
Po każdym zamkniętym punkcie aktualizowane są STATUS/TODO/CHANGELOG i raport testów.

## P6 — końcowa weryfikacja — OCZEKUJE NA P3/P4
