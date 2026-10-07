## 2026-10-07 — pełne wydanie Word kompendium wiedzy projektu

- Przebudowano `tlumacz-v4-kompendium-wiedzy (1).docx` na podstawie całej treści `docs/technical-docs/kompendium-wiedzy-projektu-v4.md` (610 linii), zamiast wcześniejszej wersji skróconej.
- Wydanie Word zawiera wielopoziomową strukturę nagłówków, spis treści Word, listę schematów, tabele oraz wszystkie schematy przepływu obecne w kompendium.
- Zweryfikowano integralność OOXML, 64 nagłówki, obecność pola TOC oraz etapów P0 i P15.
- Przed zmianą wykonano backup `backups/20261007-kompendium-docx-full/pre-change.tar.gz` (SHA-256: `81e677cce203964af7f488e5cefde8696cdffd9ba9defe062ec31739b26614f2`).

## 2026-10-07 — rozszerzone kompendium wiedzy projektu

- Dodano docs/technical-docs/kompendium-wiedzy-projektu-v4.md.
- Kompendium konsoliduje aktualny kod V4, dokumentację V4 oraz doświadczenia V3, ograniczając opis funkcjonalny do rozwiązań potwierdzonych w bieżącym kodzie.
- Dodano praktyczne zalecenia konfiguracji i strojenia llama.cpp, Cloud, Apertium, Filter Engine, GUI i glosariuszy.
- Zweryfikowano pełny suite: 599 passed; compileall, mypy i qmllint: PASS. Ruff pozostawia 2 istniejące błędy importów w tests/test_tplugin_create.py.

## 2026-10-07 — publikacja zakresu repozytorium GitHub

- Przygotowano publikację wyłącznie zakresu: `src/`, `docs/`, `config/`, `instaluj-zrodla.sh` oraz wszystkie `README.md`.
- W ramach `src/` zastosowano aktualny uniwersalny `llama-server` w `src/tlumacz/backends/llama_cpp/native/linux-x86_64/`.
- Docelowe repozytorium: `frs777/tlumacz-v4`.
## 2026-10-07 — runtime llama.cpp: uniwersalny artefakt publikacyjny

- Zastąpiono dotychczasowy zestaw `llama-server` + `libllama*` + `libggml*` + `libmtmd*` w `src/tlumacz/backends/llama_cpp/native/linux-x86_64/` pojedynczą uniwersalną binarką `llama-server` z `llama.cpp/`.
- Artefakt został przygotowany bez `-march=native` i bez specjalizacji instrukcji CPU; docelowa platforma publikacji to Linux x86_64.
- Dodano test kontraktu pakietu wymagający, aby katalog bundled runtime zawierał wyłącznie `llama-server`.
- Zaktualizowano granicę publicznego repozytorium w `.gitignore`; lokalne konfiguracje, sekrety, cache, backupy, legacy oraz `java/filter-host/` pozostają wykluczone.
- Backup przed zmianą zapisano w `.backup/publikacja-github-20261007/` oraz w backupach tworzonych przez SentinelX.

## 2026-10-07 — korekta lokalizacji dwóch nowych dokumentów Apertium

- przerwano niepełne tłumaczenie wykonywane przez lokalny model;
- ręcznie uzupełniono i zweryfikowano EN/DE dla `apertium-pair-inventory-20261006.md` oraz `apertium-pair-packages.md`;
- nie zmieniano pozostałej dokumentacji `docs/technical-docs/`.

## 2026-10-07 — lokalizacja dwóch nowych dokumentów Apertium

- dodano angielską i niemiecką wersję `docs/technical-docs/apertium-pair-inventory-20261006.md`;
- dodano angielską i niemiecką wersję `docs/technical-docs/apertium-pair-packages.md`;
- zachowano strukturę Markdown, kod, ścieżki, identyfikatory, liczby, wyniki testów i znaczenie techniczne;
- zweryfikowano zgodność liczby nagłówków i bloków kodu oraz brak polskich znaków w wersjach EN/DE.

## 2026-10-07 — ikona usuwania umiejętności użytkownika

- Udokumentowano zmianę widoku `ExtrasPage.qml`: przy każdej umiejętności użytkownika wyświetlana jest na końcu ikona zamknięcia `window-close`.
- Akcja ikony usuwa wybrany skill przez `bridge.deleteSkill(modelData)`.
- Zweryfikowano testami QML oraz `qmllint`.

## 2026-10-07 — PLAN-14: dokumentacja regresji motywu QML

- zaktualizowano bieżący kontrakt motywu w QML_GUI_DESIGN.md: natywny QStyleHints + ograniczony fallback Fusion;
- ujednolicono status BUG-041 w BUG.md i wskazano, że gate KDE pozostaje niepotwierdzony;
- dodano stan PLAN-14 do STATUS.md i pozostały gate do TODO.md;
- dodano wynik testów i backup do CHANGELOG.md;
- odnotowano ograniczenie SentinelX dotyczące dostępu do aktywnej sesji X11/DBus bez obchodzenia mechanizmów bezpieczeństwa.

## 2026-10-06 — Apertium: `pol-eng`, przenośność paczek i usunięcie `hye-eng`

- zaktualizowano dokumentację paczek do 28 kierunków;
- opisano naprawę `a_SN` w `pol-eng.t3x` i wygenerowanie `pol-eng.autogen.bin`;
- dodano zasadę, że pliki `.mode` w paczkach nie mogą zawierać absolutnych ścieżek hosta;
- zaktualizowano inventory, STATUS i plan paczkowania;
- odnotowano backupy wykonane przed naprawą i usunięciem `hye-eng`.


- 2026-10-06: PLAN-08 QML GUI — watcher event-driven dla skilli użytkownika, korekta layoutu Apertium do 120 px, aktualizacja testów i kontraktu TXT/PDF.
- 2026-10-06: PLAN-08 QML GUI — tokeny typografii/geometrii, accessibility metadata, keyboard/focus audit i aktualizacja statusu planu.

- 2026-10-06: QML GUI — przywrócenie skilli TXT/PDF, osobny URL Własnego serwera, jawny lifecycle llama.cpp przy przełączaniu backendu, dynamiczny URL po `/health`, profilowe wyłączanie klucza Cloud, natychmiastowa zmiana motywu, tooltipy Pomocy oraz większe Log/Podgląd.

- 2026-10-07: QML GUI — korekta stopki ustawień, TranslateGemma, tooltipów Pomocy i reaktywnej palety motywu po ponownej weryfikacji źródeł.


## 2026-10-07 — PLAN-13 remediacja dokumentacji

- Etap 1: zsynchronizowano `INDEX.yml`/`INDEX.md` z żywym `docs/`; aktualny baseline po dodaniu kontraktów pipeline to **495 plików / 495 wpisów**.
- Etap 2: PLAN-12 otrzymał status `active`, ponieważ jego exit gate wymaga dodatkowego E2E i zgodności liczby requestów z liczbą chunków.
- Etap 3: utworzono `TODO-PLAN12-001` dla nierozstrzygniętego testu batch/E2E.
- Etap 4: dodano dokument kontraktów pipeline i jawnie oznaczono brak wspólnego kontraktu nested/complex fields.
- Etap 5: ustalono granicę `docs/` oraz pozostawiono rootowe materiały audytowe na miejscu.
- Etap 6: wykonano cleanup `*.bak*`; wynik końcowy **0**.


## 2026-10-07 — GUI: decyzja o motywie systemowym

- Udokumentowano wycofanie selektora motywu z GUI przy zachowaniu mechanizmu technicznego do przyszłego przywrócenia.
- Udokumentowano link do strony projektu w dialogu **O programie**.
- Dodano informację o backupie `20261007-theme-system-only-project-link`.


- Dodano wynik weryfikacji zmiany: 158 testów QML GUI oraz `compileall`/`qmllint` bez błędów; odnotowano niezależny problem brakującego `filter_engine.preprocessor` w pełnym suite.


## 2026-10-07 — wydzielenie pipeline'u paczek Apertium

- `src/tlumacz/backends/apertium/package_pipeline.py` przeniesiono do `tools/apertium/package_pipeline.py`, ponieważ jest to narzędzie pomocnicze używane podczas budowania paczek, a nie kod runtime aplikacji.
- Zaktualizowano testy i importy narzędzia.
- Dodano `docs/technical-docs/apertium-paczki-reczne-tworzenie.md` z procedurą ręcznego tworzenia i weryfikacji paczek.
- Zaktualizowano dokumentację techniczną i indeksy.
- Pełny kontrakt paczki pozostaje w `paczki-jezykowe-specyfikacja.md`.


## 2026-10-07 — specyfikacja i tworzenie paczek językowych Apertium

- Dodano `tworzenie-paczek-jezykowych.md` jako kanoniczną instrukcję specyfikacji i przygotowania paczek przy użyciu `tools/apertium/package_pairs.py` oraz `tools/apertium/package_pipeline.py`.
- Dokument opisuje rzeczywisty kontrakt implementowany przez `src/tlumacz/backends/apertium/packages.py`, w tym manifest, checksumy, licencję, strukturę TAR, kryteria kompletności kierunku i walidację instalatora.
- Uzupełniono indeks dokumentacji technicznej i indeks główny.

## 2026-10-07 — inwentaryzacja i segregacja dokumentacji
- Przeprowadzono pełną inwentaryzację `docs/`.
- Dokumenty rozproszone w katalogu głównym przeniesiono do właściwych stref: `Audyt/`, `Plany/`, `technical-docs/`, `wdrozenia/`, `release/`, `research/`, `reports/` oraz `archive/`.
- Opróżniono strefę `docs/_inbox/` z materiałów roboczych; pozostał wyłącznie jej plik sterujący `AGENT.md`.
- Zaktualizowano odwołania do przeniesionych dokumentów.
- Przebudowano `docs/INDEX.yml` na podstawie aktualnego filesystemu i zsynchronizowano `docs/INDEX.md`.
- Usunięto regenerowalne `*.bak*` zgodnie z polityką dokumentacji.


## 2026-10-07 — analiza testów V4/V3 przez Paper Close Reading
- Rozszerzono `docs/technical-docs/kompendium-wiedzy-projektu-v4.md` o §29A z wnioskami z analizy katalogów `docs/Testy` V4 i `docs/TESTY` V3.
- Oddzielono aktualny materiał dowodowy V4 od historycznych doświadczeń V3.
- Ujęto zasady kwalifikacji wyników: rozstrzygający, screeningowy, niekompletny/anomalny oraz plan.
- Dodano wspólną kartę oceny testów dokumentowych: kompletność, semantyka, język, struktura, integralność techniczna, wydajność i powtarzalność.
- Dodano do kompendium wniosek metodologiczny z testów `parallel`/kontekstu: czas bez kontroli kompletności nie jest wystarczającym kryterium wyboru konfiguracji.
- Backup przed zmianą: `backups/20261007-paper-close-reading-tests/pre-change.tar.gz` (SHA-256: `854d30ee6cb429d2341f2699616acc36f06df95e35008d5cd7841dc14304cc55`).

## 2026-10-08 — właściwe repozytorium Git V4

- Udokumentowano utworzenie własnego `.git` bezpośrednio w katalogu źródłowym V4.
- Usunięto konflikt wynikający z dziedziczenia nadrzędnego repozytorium `$HOME/Projekty`.
- Skorygowano granicę publikacji: `config/` oraz `licenses/` mogą być śledzone przez właściwe repozytorium V4.
- Backup wykonano przed zmianą w katalogu `backups/git-repo-<znacznik-czasu>/`.
