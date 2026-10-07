---
id: audyt-dokumentacji-2026-10-04
status: evidence
meta:
  contentType: Audit
  category: audit
version: 1.0.0
updated: 2026-10-04
owner: project-documentation
source: docs/AGENTS.md, docs/INDEX.yml, docs/INDEX.md
depends_on: [docs/AGENTS.md, docs/_inbox/AGENT.md]
expires_when: kolejny pełny audyt dokumentacji albo zmiana polityki dokumentacji
last_validation: "inspekcja SentinelX 2026-10-04"
---

# Audyt dokumentacji — 2026-10-04

## Zakres

Inspekcja wykonana według docs/AGENTS.md oraz docs/_inbox/AGENT.md. Sprawdzono strukturę docs/, segregację _inbox, synchronizację INDEX.yml, metadane, artefakty .bak*, lokalne linki Markdown, zgodność ścieżek źródłowych oraz oczywiste duplikaty treści.

## Wykonane porządki

- sześć planów z _inbox/ przeniesiono do docs/Plany/;
- materiał badawczy o Tailscale/MCP przeniesiono do docs/reserge/;
- _inbox/ pozostawiono wyłącznie z AGENT.md;
- usunięto artefakty .bak.*, .bak, ~ i .backup* z docs/;
- dodano wymagane metadane do nowego checkpointu GUI i dwóch materiałów badawczych;
- poprawiono nieaktualne ścieżki src/tlumacz/qt_gui/ w aktywnej dokumentacji QML;
- poprawiono nieistniejące odwołania planów w dokumentacji Apertium;
- odświeżono indeks maszynowy i indeks dla człowieka.

## Wyniki kontroli

### PASS

- brak artefaktów .bak*, .bak, ~, .backup* pod docs/;
- brak osieroconych wpisów w INDEX.yml;
- brak brakujących wpisów po pełnej synchronizacji indeksu;
- brak nieistniejących lokalnych celów w składni linków Markdown;
- aktywne dokumenty zmienione podczas tego audytu mają wymagane metadane i aktualną datę;
- docs/INDEX.yml ma status active i pozostaje rejestrem maszynowym.

### Ustalenia do dalszej migracji

1. Część starszych dokumentów nie ma YAML front matter. Nie dodawano go masowo do dokumentów historycznych ani niezmienianych dokumentów, zgodnie z zasadą migracji przy najbliższej istotnej edycji.
2. W repozytorium pozostają trzy grupy identycznych plików tekstowych: OPIS_PROGRAMU_DLA_AGENTOW.md/.txt, windows.md/windows-build-report-2026-09-10.md oraz windows-kompilacja.md/windows-kompilacja-plan-2026-09-10.md. Nie usuwano ich bez dodatkowego potwierdzenia celu każdego pliku.
3. docs/BUG.md zawiera nadal starsze, datowane sekcje opisujące poprzedni stan GUI. Nie zostały usunięte w ramach tego audytu, ponieważ stanowią historię diagnostyczną; przy następnej merytorycznej edycji należy rozdzielić bieżące otwarte BUG-i od zamkniętej historii.
4. Starsze raporty i audyty mogą zawierać historyczne ścieżki src/tlumacz/qt_gui/; nie są one traktowane jako opis aktywnej implementacji, jeżeli dokument ma charakter dowodowy lub historyczny.

## Weryfikacja

- inspekcja wykonana przez SentinelX na hoście Bmax;
- data: 2026-10-04;
- zakres: cały docs/, z pominięciem kopii .bak* przy kontroli kanonicznej;
- testów stricte dokumentacyjnych w tests/ nie znaleziono;
- po zakończeniu ponownie wykonano kontrolę artefaktów backupowych i spójności indeksu.
