# Audyt dokumentacji — 2026-10-01

## Zakres
Audyt obejmuje dokumentację projektu Tłumacz V4 w `/home/frs/Projekty/tlumacz-v4`, ze szczególnym uwzględnieniem źródeł prawdy, zgodności ścieżek, statusów faz, instrukcji agentowych, planu migracji i raportów wydaniowych.

## Ustalenia

### D1 — rozbieżna ścieżka projektu
`docs/STATUS.md` ustanawia `/home/frs/Projekty/tlumacz-v4/` jako oficjalny katalog projektu. Jednocześnie `docs/MIGRATION_INVENTORY.md` oraz `docs/PLAN_MIGRACJI-v4.md` nadal zawierają `/home/frs/Projekty/agent-translator-v4/`.

**Ryzyko:** agent może pracować na nieaktualnej ścieżce lub uznać historyczne drzewo za aktywne.

### D2 — status release jest opisany poprawnie, ale niespójnie z aktualną weryfikacją
Dokumentacja deklaruje dla RC 0.40.0: pełny pytest PASS, Ruff PASS, mypy PASS i działające `python -m tlumacz --version`. Bieżąca weryfikacja wykazała:
- pytest: 182 passed;
- mypy: PASS;
- compileall: PASS;
- Ruff: FAIL — 6 błędów;
- `python -m tlumacz --version`: FAIL w bieżącym interpreterze, ponieważ importuje zainstalowany pakiet `/usr/lib/python3.14/site-packages/tlumacz`, a nie kod repozytorium, i ten pakiet nie posiada `__main__.py`.

Wniosek: wcześniejsze PASS-y są historycznym dowodem, ale nie są aktualnym dowodem stanu checkoutu.

### D3 — brak `docs/BUG.md`
Plan migracji wymienia `docs/BUG.md` jako źródło, lecz plik nie istnieje w aktualnym katalogu.

### D4 — dokumentacja deklaruje zamknięcie faz, mimo że aktualne bramki jakościowe nie są zielone
STATUS opisuje Fazy 10–13 jako zamknięte/freeze, lecz aktualny Ruff jest czerwony, a CLI wymaga rozstrzygnięcia ścieżki instalacji.

### D5 — artefakty build/package pozostają w drzewie roboczym
`temp/` zawiera staging Apertium i inne artefakty. Nie jest to samo w sobie błąd, ale powinno być jednoznacznie sklasyfikowane jako regenerowalne artefakty robocze, a nie część źródła prawdy.

## Pozytywne ustalenia
- `AGENTS.md` zawiera jasne zasady: brak instalacji/usuwania bez zgody, backup przed dużą zmianą, aktualizacja dokumentacji i faktyczna weryfikacja.
- Istnieją backupy migracyjne.
- Istnieją osobne katalogi `docs/Audyt`, `docs/Plany`, `docs/Testy`, `docs/Wdrożenia`, `docs/reports`.
- Dokumentacja rozróżnia Release Candidate od finalnego wydania.
- Blokery Apertium/Windows/dependency closure są jawnie opisane.

## Ocena
Dokumentacja jest obszerna i ma strukturę potrzebną do dalszej pracy, ale nie jest obecnie w pełni synchronizowana ze stanem wykonawczym. Najważniejsze są: ujednolicenie ścieżki, rozdzielenie dowodów historycznych od bieżących oraz aktualizacja bramek jakościowych.

## Zalecenia
1. Ujednolicić aktywną ścieżkę na `/home/frs/Projekty/tlumacz-v4/`.
2. Oznaczyć historyczne wyniki jako historyczne i dodać aktualny snapshot jakości.
3. Naprawić lub jednoznacznie udokumentować model uruchamiania CLI.
4. Dodać raport audytu kodu i raport planu naprawy.
5. Po każdej zmianie kodu aktualizować STATUS/CHANGELOG/odpowiedni raport testowy.



## Weryfikacja po naprawie
Po P0/P1/P2 aktywna dokumentacja została zsynchronizowana: ścieżki w planie i inventory wskazują `/home/frs/Projekty/tlumacz-v4/`. Aktualne quality gates: pytest 182 passed, Ruff PASS, mypy PASS, compileall PASS, CLI na świeżym wheel PASS. Historyczne raporty zachowują historyczne ścieżki jako dowód przeszłych operacji.
