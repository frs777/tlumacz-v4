# Tłumacz V4 — docelowa struktura dokumentacji

Status: USTALONA STRUKTURA LOGICZNA — MIGRACJA FIZYCZNA JESZCZE NIE WYKONANA
Data audytu: 2026-09-30

## Zasada nadrzędna
Do czasu akceptacji raportu i indeksów nie wolno przenosić, usuwać ani archiwizować żadnego dokumentu z V3.

## Struktura
- docs/Archiwum/ — materiały historyczne i zastąpione.
- docs/Zrzuty/ — zrzuty ekranu.
- docs/Testy/ — wyniki, benchmarki, logi i dowody testów.
- docs/Wdrożenia/ — wdrożenia, release, packaging i procedury operacyjne.
- docs/Audyt/ — audyty, raporty i rejestry ryzyka.
- docs/Plany/ — aktywne plany, migracje i przyszłe prace.

Nie tworzymy docelowo równoległych stref research, technical-docs, audits, wdrozenia ani TESTY. Ich zawartość zostanie sklasyfikowana semantycznie do sześciu stref.

## Bramka migracji
1. audyt; 2. raport; 3. indeksy; 4. AGENTS.md; 5. akceptacja użytkownika; 6. dopiero potem migracja fizyczna.
