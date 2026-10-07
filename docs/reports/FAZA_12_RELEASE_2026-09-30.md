# Faza 12 — Release 0.40.0 — raport

## Wynik
**RELEASE CANDIDATE — częściowo zweryfikowany. Finalny release pozostaje otwarty.**

## Weryfikacja
| Bramka | Wynik | Dowód |
|---|---|---|
| pełny suite | PASS | 182 passed |
| compile | PASS | compileall |
| static analysis | PASS | Ruff + mypy |
| contract suite | PASS | pełny suite |
| integration | PASS | 19 testów |
| E2E | PASS | testy dokumentowe/Apertium/Filter Host |
| clean install | PASS | wheel w clean venv, bez deps |
| dokumentacja | PASS | release notes + migration notes + rollback |
| CHANGELOG | PASS | wpis Fazy 12 |
| migration notes | PASS | dokument utworzony |
| rollback procedure | PASS | dokument utworzony |
| packaging | OTWARTE | blokady Fazy 11 |
| Windows | OTWARTE | brak runtime'u natywnego |

## Artefakt
tlumacz-0.40.0-py3-none-any.whl

SHA-256: 161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835

## Blokady
- Apertium nie udostępnia kompletnej pary eng-pol w aktualnym bundlowanym runtime.
- Próba odtworzenia brakującego artefaktu z materiałów V3 kończy się Undefined attr-item cas_sp podczas apertium-preprocess-transfer.
- Brak Windowsowego runtime'u natywnego.
- Dependency closure i audyt licencji komponent-po-komponencie nie są jeszcze zamknięte.

## Decyzja zakresowa
Osobny słownik nie jest blockerem. Nie jest częścią wbudowanego artefaktu i może zostać dodany niezależnie po wydaniu.

## Rollback
Rollback pozostaje oparty o nienaruszony V3 oraz osobny backup konfiguracji użytkownika. Szczegóły: docs/release/ROLLBACK_0.40.0.md.

## Kryterium ukończenia
Faza 12 nie jest oznaczona jako zakończona, dopóki nie zostaną zamknięte wymagania Windows i packaging z Fazy 11.
