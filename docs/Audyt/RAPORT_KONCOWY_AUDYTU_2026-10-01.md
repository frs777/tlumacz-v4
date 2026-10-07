
# Raport końcowy audytu inżynierskiego — Tłumacz V4

Data: 2026-10-01
Katalog: `/home/frs/Projekty/tlumacz-v4/`

## 1. Zakres

Wykonano audyt dokumentacji, architektury, kodu, testów, jakości statycznej, uruchamiania CLI, packagingu oraz wybranych problemów runtime. Wykorzystano także zewnętrzny research dotyczący setuptools i Apertium.

## 2. Najważniejsze ustalenia

1. Właściwy katalog projektu to `/home/frs/Projekty/tlumacz-v4/`.
2. Wcześniejsza ścieżka `opencode-plugin-builder` nie była projektem audytu.
3. Aktywna dokumentacja zawierała nieaktualne ścieżki V4; poprawiono je w planie i inventory.
4. Kod przechodzi 182 testy, mypy i compileall.
5. Ruff początkowo wykazał 6 błędów; po korekcie importów i wyłączeniu regenerowalnego stagingu `temp/` oraz backupów z lintowania przechodzi.
6. `python -m tlumacz --version` z systemowego interpretera używał globalnego pakietu, a stare środowiska miały nieaktualne shebangi. Świeży venv z wheel przechodzi zarówno moduł CLI, jak i console script.
7. Apertium `eng-pol` pozostaje realnym blockerem packagingu: compiler zgłasza `Undefined attr-item cas_sp` dla `cas_sp`.
8. Ten sam problem występuje w lokalnym źródle V3 oraz w aktualnym pliku upstream `apertium-eng-pol`. Nie wykonano arbitralnej poprawki semantycznej.
9. Dependency closure i pełny audyt licencji pozostają otwarte.

## 3. Zmiany wykonane

- backup: `.migration-backups/pre-audit-repair-20261001.tar.gz`;
- poprawa importów w `processor.py`;
- poprawa importów w `test_docx_filter.py`;
- konfiguracja Ruff tak, aby nie analizował regenerowalnych artefaktów;
- korekta aktywnych ścieżek dokumentacyjnych;
- utworzenie raportów audytowych, planu naprawczego i raportu testów;
- weryfikacja wheel w świeżym środowisku.

## 4. Wyniki końcowej weryfikacji

| Kontrola | Wynik |
|---|---|
| pytest | PASS — 182 passed |
| Ruff | PASS |
| mypy | PASS — 60 plików |
| compileall | PASS |
| `python -m tlumacz --version` w świeżym venv | PASS — 0.40.0 |
| `tlumacz --version` w świeżym venv | PASS — 0.40.0 |
| Apertium runtime/E2E | PASS — 6 passed |
| `eng-pol.t1x.bin` | BLOCKED — `cas_sp` |

## 5. Research zewnętrzny

Dokumentacja Apertium opisuje `def-attr` jako deklarację zbioru atrybutów wykorzystywanych przez transfer i wskazuje kompilator transferu jako miejsce wykrywania niezdefiniowanych atrybutów. Upstream `apertium-eng-pol` zawiera `part="cas_sp"` w transferze, ale wyszukiwanie w aktualnym pliku nie wykazało deklaracji `def-attr n="cas_sp"`. Jest to wystarczający dowód, aby nie uznawać ręcznego dopisania atrybutu za bezpieczną naprawę.

Dokumentacja setuptools potwierdza używany przez projekt model `src` layout oraz `[project.scripts]`; świeży wheel zweryfikował oba entrypointy.

## 6. Ocena architektoniczna

Architektura V4 jest modularnym monolitem z rozdzielonymi warstwami domain/application/backends/filter_engine/infrastructure/interfaces. Filter Engine jest odseparowany od backendów, a Java Filter Host komunikuje się przez wersjonowany JSON Lines. Testy obejmują kontrakty, filtry, backendy i E2E.

Najważniejsze ryzyka pozostałe po audycie są wydaniowe, nie dotyczą podstawowej spójności warstw: Apertium `eng-pol`, dependency closure/licencje oraz brak kompletnego Windows runtime.

## 7. Status

Audyt i pierwsza fala napraw są zakończone. Projekt **nie powinien być oznaczany jako finalny release 0.40.0**, dopóki P3/P4 nie zostaną zamknięte i nie zostanie wykonana końcowa weryfikacja całego artefaktu.

## 8. Następny punkt pracy

P3: pozyskać i zweryfikować poprawną wersję/źródło pary Apertium English→Polish albo ustalić na podstawie historii upstream dokładną semantykę `cas_sp`; następnie zbudować binaria w kontrolowanym środowisku i dopiero wtedy kontynuować dependency/licence closure.
