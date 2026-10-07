# Paczki par językowych Apertium — plan wdrożenia

**Cel:** wprowadzić pojedynczy, niekompresowany artefakt `.tar` dla każdego kierunku Apertium oraz bezpieczny builder i instalator.

## Zakres

- format `apertium-<pair>-<version>.tar`;
- manifest i SHA-256;
- selekcja wyłącznie skompilowanych plików wymaganych przez wybrany tryb;
- bezpieczne rozpakowanie do magazynu użytkownika;
- synchronizacja pliku `modes/<pair>.mode`;
- testy TDD;
- gotowe artefakty w `pary/`;
- dokumentacja dla twórców paczek.

## Kontrakt

Jedna paczka zawiera jeden kierunek. Tar jest niekompresowany. Paczka nie zawiera runtime'u Apertium ani Javy.

## Weryfikacja

- testy pakietów;
- testy istniejącego wykrywania pluginów Apertium;
- kompilacja modułów Python;
- pełny `pytest`;
- kontrola rzeczywistych artefaktów w `pary/`.

## Wynik

Po naprawie `pol-eng` gotowych do publikacji jest 28 kierunków. `hye-eng` został usunięty z lokalnego magazynu runtime i nie jest częścią bieżącego zestawu artefaktów.
