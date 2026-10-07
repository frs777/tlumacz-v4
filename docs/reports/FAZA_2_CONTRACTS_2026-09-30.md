# Raport Fazy 2 — kontrakty

Data: 2026-09-30

## Zakres

Zaimplementowano kontrakty domenowe V4:

- TranslationBackend;
- BackendResult;
- FilterContract;
- DocumentContract;
- InlineCode;
- błędy domenowe;
- kooperacyjne cancellation;
- HealthCheckResult;
- Workspace i Session.

## Architektura

Kontrakty znajdują się w src/tlumacz/domain/ i nie importują Qt, konkretnych providerów ani V3. Integracja aplikacyjna cancellation znajduje się w src/tlumacz/application/.

## TDD

Najpierw dodano testy kontraktów i potwierdzono RED przez brak implementacji. Następnie dodano minimalną implementację i doprowadzono zestaw do GREEN.

## Weryfikacja

- pytest -q → 11 passed
- ruff check . → All checks passed
- mypy src → Success: no issues found in 13 source files

## Kryterium Fazy 2

Spełnione: kontrakty mają testy i nie zależą od Qt ani konkretnego providera.

## Decyzja Lingua

lingua-language-detector pozostaje zewnętrzną zależnością i nie był instalowany podczas tej fazy.
