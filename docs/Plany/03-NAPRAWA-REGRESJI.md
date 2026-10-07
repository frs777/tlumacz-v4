---
id: plan-03-naprawa-regresji
status: closed
meta:
  contentType: ImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-06
owner: project-maintenance
source: docs/BUG.md
depends_on: [docs/Plany/00-BASELINE-MAPA-PARYTETU-V3-V4.md, docs/Plany/01-RESTORE-BRAKUJACE-FUNKCJE.md, docs/Plany/02-REDUKCJA-NADMIAROWEGO-KODU.md]
expires_when: każda potwierdzona regresja ma test reprodukujący i poprawkę
last_validation: "ponowna walidacja Planu 03 2026-10-06; 367 passed, 0 failed"
---

# PLAN 03 — naprawa regresji

## Metoda obowiązkowa

Dla każdej regresji:
1. reprodukcja V4;
2. obserwacja V3;
3. ustalenie kontraktu;
4. lokalizacja pierwszej warstwy rozjazdu;
5. test czerwony;
6. minimalna poprawka;
7. test jednostkowy/kontraktowy;
8. E2E dla granic;
9. pełna regresja;
10. aktualizacja BUG/STATUS/CHANGELOG.

## P1 — launcher i środowisko

Potwierdzić interpreter, tlumacz.__file__, launcher i QML entrypoint. Nie usuwać globalnego V3. Jeśli problem jest wyłącznie środowiskowy, nie zmieniać funkcji aplikacji.

## P1 — Apertium

Oddzielić brak w GUI od blokera eng-pol/cas_sp. Najpierw sprawdzić launcher, bridge, registry i QML. Nie naprawiać cas_sp domysłem.

## P1 — DLX

Sprawdzić registry, GUI, konfigurację, request contract, error mapping, timeout i brak niejawnego fallbacku.

## P1 — Własny

Zweryfikować pełny przepływ:
selector → editable endpoint → model/key → BackendRequest → provider → result.

## P1 — TranslateGemma

Zweryfikować selector → chat template → kod językowy → PromptBuilder → runtime. Nie traktować jako osobnego backendu.

## P1 — dynamiczny Cloud

Dla każdego aktywnego profilu sprawdzić selector, konfigurację, persystencję, routing, provider, wynik, błąd i timeout. Rozdzielić provider, protocol, model i endpoint.

## P1 — ustawienia pozorne

Dla server_chat_template, auto_start_server, cache_clear_after_translation, restart_after_translation, server_port, server_parallel, server_gguf_path, profili Cloud, glossary i skills wykonać test:
ustawienie → zapis → reload → consumer runtime → obserwowalny efekt.

## P2 — dokumenty

Dla DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF:
extract → units → translate stub → validate → reconstruct → structural compare.
Dodatkowo Unicode, inline markers, cancellation, empty result i invalid input.

## P2 — błędy Cloud

Zweryfikować authentication, rate limit, timeout, network, invalid response i empty result. Nie naprawiać retry na podstawie starego openai.RateLimitError bez potwierdzenia aktywnego V4.

## Kryterium wyjścia

Każda potwierdzona regresja ma test przed poprawką, root cause, poprawkę, test po poprawce i dowód braku regresji ubocznej.
## Raport wstępny — 2026-10-04

Audyt regresji po Planie 01/02 nie wykazał nowego błędu wymagającego poprawki kodu.

Wykonano:
- launcher/bootstrap, Cloud, DLX, Własny, TranslateGemma, llama.cpp runtime, GUI;
- filtry dokumentowe DOCX/ODT/Markdown/HTML/EPUB/XLIFF;
- Apertium document E2E;
- timeout/error contract Cloud;
- SecretStore i persystencję GUI.

Wynik skoncentrowanego suite'u: **81 passed**. Dodatkowy suite GUI/i18n/core/Cloud secrets: **62 passed**.

Backup przed audytem: `backups/plan-03-20261004-pre-regression-audit.tar.gz`, SHA-256 `2ab2be2d63153cde01c4fd701c9195d96bc4a103c39e2b02ef700477a4a0d038`.

Otwarte kwestie nie są automatycznie klasyfikowane jako regresje: Apertium eng-pol/cas_sp, Windows runtime, dependency/licencje oraz E2E rzeczywistego modelu TranslateGemma.


## Raport walidacyjny — 2026-10-06

Ponowiono realizację i walidację Planu 03 na aktualnym drzewie V4.

### Weryfikacja środowiska i P1
- /usr/bin/python oraz tlumacz.__file__ wskazują aktualne źródło V4: /home/frs/Projekty/tlumacz-v4/src/tlumacz/__init__.py.
- Launcher źródłowy i kontrakt bootstrapu są objęte testami; V3 nie był usuwany ani modyfikowany.
- Apertium, własny backend, Cloud, llama.cpp/TranslateGemma oraz konfiguracja GUI mają przechodzące testy kontraktowe/regresyjne.
- Focused suite obejmujący te obszary i aktywne formaty dokumentowe: 128 passed.
- Pełny suite V4: 367 passed, 0 failed.

### Weryfikacja jakości
- compileall: PASS.
- qmllint src/tlumacz/qml_gui/*.qml: PASS.
- ruff check src tests: 4 istniejące problemy statyczne (2× I001 oraz 2× E501); nie były zmieniane w ramach Planu 03.
- mypy src/tlumacz: 4 istniejące problemy typowania w translation_orchestrator.py i translation_app.py; poza zakresem Planu 03.

### Wniosek
Nie potwierdzono nowej regresji wymagającej poprawki kodu podczas tej walidacji. Jedyny wcześniejszy czerwony wynik TranslateGemma został ponowiony osobno i przechodzi: 1 passed; pełny suite następnie również przechodzi 367/367.

Backup dokumentacji przed synchronizacją: backups/plan-03-20261006-pre-doc-sync/.
