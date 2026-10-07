# Raport naprawy regresji GUI i Cloud V3 → V4 — 2026-10-01

## Stan przed naprawą

Audyt wykazał niekompletną migrację GUI/Cloud: V4 nie posiadał src/tlumacz/qt_gui, CloudRouter miał kontrakt i Mozhi, ale brakowało większości providerów V3 oraz 12 profili Cloud. FastAPI/OpenVINO były prawidłowo wycofane.

## Naprawy

### R-01 GUI — NAPRAWIONE
Dodano warstwę Qt V4: main_window.py, app.py, config.py, help_texts.py i theme.py. GUI korzysta z warstwy aplikacyjnej V4 i nie importuje V3. Aktywne backendy: llama.cpp, Apertium, Chmura.

### R-02 Cloud — NAPRAWIONE
Dodano adaptery: OpenAI-compatible, DeepL, Microsoft Translator, MyMemory, LibreTranslate, SimplyTranslate, Mozhi i DLX.

### R-03 Profile Cloud — NAPRAWIONE
Dodano src/tlumacz/resources/cloud_models.json z 12 profilami: Cohere, ChatGPT, Codex, Gemini Flash, Gemini Flash Lite, DeepSeek, DeepL API Free, LibreTranslate, SimplyTranslate, MyMemory, Microsoft Translator i Mozhi. Sekrety nie są umieszczane w repozytorium.

### R-04 Mozhi GUI — NAPRAWIONE
Odtworzono Model Cloud, Serwer Mozhi, wybór instancji Automatyczny/ręczny, silniki Mozhi, SimplyTranslate i restart procesu po tłumaczeniu.

### R-05 wycofane backendy — ZACHOWANE POZA V4
FastAPI i OpenVINO nie zostały przywrócone.

### R-06 dokumentacja — NAPRAWIONE
Uzupełniono raport niezgodności, plan naprawczy, raport naprawy, STATUS, TODO, CHANGELOG, indeks oraz dokument wdrożeniowy Cloud.

## Weryfikacja

- pytest: 195 passed;
- Ruff: PASS;
- mypy: PASS — 68 plików;
- compileall: PASS;
- test GUI offscreen: 3 passed;
- test kompatybilności providerów V3: 21 passed;
- wheel V4: zbudowany poprawnie;
- wheel zawiera qt_gui, backends/cloud/providers.py i resources/cloud_models.json.

## Wniosek

Regresja GUI/Cloud została naprawiona w aktualnym drzewie V4 bez przywracania FastAPI/OpenVINO. Pozostałe blokery release 0.40.0 są niezależne: Apertium eng-pol, Windows oraz pełne dependency/licence closure.

## Uzupełnienie audytu powierzchni UI — 2026-10-01

Dodatkowe porównanie setu objectName V3/V4 wykazało utracone elementy Dodatki/Pomoc. Zostały odtworzone: glosariusz z wpisem, licznik, akcje umiejętności, język pomocy, O programie, output splitter, czas/spinner oraz pozostałe elementy aktywnego GUI. Kontrole specyficzne dla wycofanych FastAPI/OpenVINO pozostają celowo pominięte.

Regresja powierzchni: tests/test_gui_surface_parity.py — PASS.
Końcowa liczba testów: 196 passed.
Ruff: PASS; mypy: PASS; compileall: PASS; wheel: PASS.

## Quality gate

Ruff został ograniczony do aktywnego kodu src/tests; archiwalne .backup i źródła Apertium nie są częścią quality gate aplikacji. Limit linii ustawiono na 120, a aktywny kod przechodzi Ruff bez błędów. Mypy obejmuje 68 plików źródłowych; PySide6 jest traktowany jako biblioteka bez stubów.
