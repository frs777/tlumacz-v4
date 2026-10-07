# STATUS DOKUMENTU: HISTORYCZNY / EVIDENCE

> Ścieżki `/home/frs/Projekty/agent-translator-v4` występują tu jako historyczne ślady wykonania. Oficjalny katalog V4 to `/home/frs/Projekty/tlumacz-v4/`. Nie traktować starej ścieżki jako aktywnego repozytorium.

# FAZA 13 — FINALNY HANDOFF I FREEZE — 2026-09-30

## Cel
Faza 13 zamyka bieżący cykl prac migracyjnych jako lokalny Release Candidate / handoff freeze. Nie oznacza publikacji do GitHub ani finalnego wydania 0.40.0.

## Stan zweryfikowany
- V4 pozostaje w /home/frs/Projekty/agent-translator-v4.
- V3 pozostaje osobnym drzewem i nie jest celem migracji in-place.
- Ostatni zweryfikowany pełny suite V4: 182 passed.
- Ostatni zweryfikowany wheel: temp/wheel/tlumacz-0.40.0-py3-none-any.whl.
- SHA-256 wheel: 161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835.
- Linux clean install oraz smoke test artefaktu zostały zweryfikowane.
- Apertium engine: 3.9.12.
- Aktualnie wykrywane pary językowe Apertium: pusta lista; kompletna para eng-pol nie jest dostępna.
- W V4 nie znaleziono natywnych artefaktów Windows .exe/.dll dla bundlowanego runtime'u Apertium.
- Słownik pozostaje poza zakresem blokującym release.

## Otwarte blokery
1. kompletna para Apertium eng-pol, w szczególności brak eng-pol.t1x.bin;
2. Windowsowy runtime natywny;
3. pełne zamknięcie dependency closure;
4. pełny komponentowy audyt licencji.

Próba regeneracji danych Apertium z materiałów V3 kończyła się błędem Undefined attr-item cas_sp podczas apertium-preprocess-transfer. Nie wygenerowano sztucznego binarium.

## Zasady handoff
- brak push do GitHub;
- brak publikacji wheel poza lokalnym drzewem V4;
- V3 pozostaje nietkniętym źródłem referencyjnym;
- dalsze prace należy prowadzić wyłącznie po zamknięciu powyższych blockerów albo po zaakceptowaniu jawnej zmiany zakresu;
- nie należy oznaczać 0.40.0 jako final release przed ponownym przejściem bramek F11/F12.

## Backup
Przed aktualizacją dokumentacji wykonano:

.migration-backups/pre-phase13-documentation-20260930.tar.gz

## Kryterium Fazy 13
Spełnione jako lokalny handoff freeze: stan, artefakt, blokery, zasady publikacji i rollback są udokumentowane.

Finalny release 0.40.0 pozostaje zależny od zamknięcia blockerów F11/F12.