# STATUS DOKUMENTU: HISTORYCZNY / EVIDENCE

> Ścieżki `/home/frs/Projekty/agent-translator-v4` występują tu jako historyczne ślady wykonania. Oficjalny katalog V4 to `/home/frs/Projekty/tlumacz-v4/`. Nie traktować starej ścieżki jako aktywnego repozytorium.


# Raport weryfikacji po audycie — 2026-10-01

## Aktualny wynik

| Bramka | Wynik |
|---|---|
| pytest | PASS — 182 passed |
| Ruff | PASS |
| mypy | PASS — 60 plików |
| compileall | PASS |
| PYTHONPATH=src python3 -m tlumacz --version | PASS — 0.40.0 |
| świeży venv + wheel + python -m tlumacz --version | PASS — 0.40.0 |
| świeży venv + wheel + tlumacz --version | PASS — 0.40.0 |
| Apertium runtime/E2E | PASS — 6 passed |
| kompilacja eng-pol.t1x.bin | BLOCKED — Undefined attr-item cas_sp |

## Zmiany

- uporządkowano importy w src/tlumacz/filter_engine/processor.py;
- uporządkowano importy w tests/test_docx_filter.py;
- Ruff wyklucza regenerowalne temp/ i .migration-backups/;
- aktywny plan/inventory używa oficjalnej ścieżki /home/frs/Projekty/tlumacz-v4/;
- wykonano backup: .migration-backups/pre-audit-repair-20261001.tar.gz.

## CLI

Początkowa próba z systemowym interpreterem importowała tlumacz z /usr/lib/python3.14/site-packages, dlatego python -m tlumacz nie odzwierciedlało checkoutu. Świeże środowisko z wheel potwierdziło poprawność zarówno entrypointu modułowego, jak i console script.

Istniejące środowiska w temp/ mają shebangi wskazujące na historyczną ścieżkę /home/frs/Projekty/agent-translator-v4; nie są dowodem aktualnego packagingu.

## Apertium

Lokalny plik apertium-eng-pol.eng-pol.t1x oraz upstreamowy plik tej samej pary zawierają użycie part=cas_sp bez odpowiadającej deklaracji def-attr. Bieżący compiler odrzuca plik. Nie wykonano arbitralnego dopisania atrybutu.
