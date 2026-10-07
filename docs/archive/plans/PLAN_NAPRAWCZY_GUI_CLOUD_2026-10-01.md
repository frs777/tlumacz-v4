# Plan naprawczy GUI i Cloud V3 → V4 — 2026-10-01

## P0 — zachowanie referencyjne

- [x] porównać V3/V4;
- [x] sprawdzić dokumentację obu drzew;
- [x] sprawdzić indeks;
- [x] porównać zrzuty GUI;
- [x] wykonać backup.

## P1 — odtworzenie GUI

1. Przywrócić warstwę Qt w V4 jako nowy adapter UI.
2. Nie kopiować FastAPI/OpenVINO.
3. Zachować elementy interfejsu dla llama.cpp, Cloud i Apertium.
4. Odtworzyć zakładki i formularze zgodne z referencyjnym GUI.
5. Odtworzyć pola Mozhi i ich health-check.
6. Oprzeć UI na V4 controllers zamiast przywracać bezpośrednie zależności V3.

## P2 — CloudBackend

1. Zachować obecny kontrakt/router V4.
2. Przenieść zachowanie providerów V3 do osobnych adapterów V4.
3. Zachować timeouty, limity, walidację odpowiedzi i podział UTF-8.
4. Zachować DLX jako osobny provider.
5. Zachować SimplyTranslate i Mozhi jako providerów Cloud.
6. Zachować migrację profili V3 → V4.
7. Dodać test kontraktowy dla każdego aktywnego providera.

## P3 — konfiguracja GUI

Odtworzyć profilowy model Cloud z V3, bez sekretów w repozytorium. Zachować niezależne profile i klucze.

## P4 — regresja UI

Zweryfikować:
- wybór llama.cpp;
- wybór Cloud;
- wybór Apertium;
- wybór profilu Cloud;
- Mozhi instance/engine;
- SimplyTranslate engine;
- start/stop/restart llama.cpp;
- brak operacji FastAPI/OpenVINO;
- zapisywanie ustawień;
- odtwarzanie ustawień po restarcie;
- tłumaczenie dokumentu przez aktywny backend.

## P5 — dokumentacja

Po każdym zamkniętym punkcie aktualizować:
- STATUS;
- TODO;
- CHANGELOG;
- dokument techniczny Cloud;
- dokument techniczny GUI;
- INDEX.md;
- INDEX.yml.

## P6 — końcowa weryfikacja

Dopiero po przejściu P1–P5:
- pełny pytest;
- Ruff;
- mypy;
- compileall;
- smoke test GUI offscreen;
- testy kontraktowe Cloud;
- testy E2E dokumentu;
- porównanie z zachowaniem V3.

## Wynik realizacji — 2026-10-01

P1 GUI: ZAMKNIĘTE.
P2 CloudBackend: ZAMKNIĘTE.
P3 konfiguracja GUI: ZAMKNIĘTE.
P4 regresja UI: ZAMKNIĘTE dla testów automatycznych i smoke offscreen.
P5 dokumentacja: ZAMKNIĘTE dla tego etapu.
P6 końcowa weryfikacja tego etapu: ZAMKNIĘTE — 195 passed, Ruff PASS, mypy PASS, compileall PASS, wheel PASS.

Nie oznacza to zamknięcia release 0.40.0. Pozostają niezależne blokery Apertium eng-pol, Windows i dependency/licence closure.
