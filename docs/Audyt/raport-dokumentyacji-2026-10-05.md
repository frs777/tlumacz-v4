---
id: raport-dokumentyacji-2026-10-05
status: evidence
meta:
  contentType: Documentation Report
  category: audit
version: 1.0.0
updated: 2026-10-05
owner: project-documentation
source: [src/tlumacz/, tests/, docs/]
depends_on: [docs/AGENTS.md, docs/INDEX.yml, docs/STATUS.md]
expires_when: kolejna pełna synchronizacja dokumentacji po zmianie architektury, GUI lub backendów
last_validation: "SentinelX 2026-10-05; pytest 297 passed; compileall PASS; qmllint PASS"
---

# Raport dokumentacji — 2026-10-05

## Cel

Przeprowadzono pełną synchronizację dokumentacji technicznej i pomocy użytkownika z aktualnym kodem Tłumacz V4. Założono, że część wcześniejszych dokumentów może zawierać nieaktualne fragmenty.

Przegląd objął Python/QML, testy, aktywną dokumentację, materiały historyczne, dokumenty z katalogu głównego oraz pomoc zaszytą w GUI.

## Stan ustalony z kodu

- aktywne GUI: `src/tlumacz/qml_gui/`; zakładki: Tłumaczenie, API i serwer, Przełączniki, Pomoc;
- aktywne kierunki: llama.cpp, Cloud, Apertium, custom/Własny;
- `TranslateGemma` jest specjalnym `chat_template` dla llama.cpp, nie backendem;
- tryb TranslateGemma korzysta z `LanguageDetector` i kodów ISO 639-1;
- `TranslationApp` posiada `LlamaCppRuntimeManager` z operacjami start/stop/restart;
- Cloud korzysta z `CloudProviderRegistry`, a bridge posiada `SecretStore` z migracją starszego `api_key`;
- główny Filter Engine rejestruje DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF;
- TXT i PDF nie są obecnie rejestrowane w głównym `FilterRegistry`.

## Dokumentacja techniczna

Zaktualizowano: `ARCHITECTURE.md`, `STATUS.md`, `TODO.md`, `CHANGELOG.md`, `DOCUMENTATION_CHANGELOG.md`, `technical-docs/index.md`, `models.md`, `server-management.md`, `cloud-translation.md`, `user-guide.md`, `functional-capabilities.md`, dokumentację EN/DE oraz `QML_GUI_DESIGN.md`, `QML_GUI_LAYOUT.md` i `QML_GUI_TRANSLATION_CARD_SPEC.md`.

Dokumenty rozdzielają stan aktualny, wymagania docelowe i historię zmian. Źródłem prawdy dla zachowania jest kod i testy, a dokumenty historyczne są dowodem przebiegu prac.

## Pomoc użytkownika

Przebudowano `help.pl.md`, `help.en.md` i `help.de.md`. Każdy plik ma dokładnie pięć tematów `##`. Pomoc obejmuje cały przepływ przez Tłumaczenie, API i serwer, Przełączniki oraz Pomoc, w tym llama.cpp, TranslateGemma, Cloud, Mozhi, Apertium, Własny, glosariusz, skille, ustawienia LLM, Log, Podgląd, anulowanie i diagnostykę.

`HelpMarkdownView.qml` używa `TextEdit.MarkdownText`, `readOnly` i `ScrollView`; treść została ograniczona do Markdown obsługiwanego przez Qt.

## Najważniejsza rozbieżność — Apertium

`TranslationPage.qml` nadal umieszcza pola Język źródłowy i Język docelowy w tym samym `RowLayout` co Tłumacz i Anuluj. Pola są tylko do odczytu.

Wcześniejsze wpisy changelogu twierdziły, że blok został wydzielony do osobnego wiersza. Korelacja z aktualnym kodem wykazała, że był to stan pośredni albo opis niezgodny z końcowym plikiem.

Problem wpisano do `STATUS.md`, `TODO.md`, `QML_GUI_LAYOUT.md` i `QML_GUI_TRANSLATION_CARD_SPEC.md`. Dokumentacja opisuje stan rzeczywisty zamiast maskować rozbieżność.

Bridge wykrywa potencjalne źródła Apertium, ale aktualna powierzchnia GUI nie daje użytkownikowi osobnego wyboru źródła. Pozostaje decyzja projektowa i TODO dotyczące detektora par jedno- i dwukierunkowych.

## Porządkowanie dokumentacji

Z katalogu głównego przeniesiono dokumenty do `docs/`, między innymi audyty, diagnostykę GUI, `AGENTS-v3.md`, starszy `OPIS_PROGRAMU_DLA_AGENTOW.md` oraz bieżący `CHANGELOG.md`. Starszy changelog zachowano jako `docs/archive/reference/CHANGELOG_LEGACY_V4_2026-10-04.md`. README pozostały w root; `AGENTS.md` i `ADMINS.md` pozostają jako pliki sterujące projektu.

Odświeżono `docs/INDEX.yml` i `docs/INDEX.md`. Stan indeksu: 457 plików i 457 wpisów, 0 missing, 0 orphan.

## Backupy

Przed pracami utworzono `backups/documentation-maintenance-20261005/pre-documentation-update.tar.gz`. SHA-256: `1f441563b2141c095f239bc48b1602cff23efcb212b4b7d4b4947c62ff91700a`.

Usunięto 184 pliki `*.bak`, `*.bak.*`, `*.backup`, `*.backup.*` i `*~`. Końcowo takich plików jest 0. Pozostawiono osobne archiwa `.tar.gz` bezpieczeństwa.

## Testy i walidacja

- pytest: **297 passed**;
- compileall: **PASS**;
- qmllint zmienionych stron QML: **PASS**;
- pomoc PL/EN/DE: dokładnie 5 tematów `##`, bez `####` — **PASS**;
- runtime QML przez Xvfb z `QML_DISABLE_DISK_CACHE=1`: uruchomienie bez błędów, kontrolowany timeout 8 s.

Podczas walidacji poprawiono cztery nieaktualne kontrakty testów GUI oraz rzeczywisty duplikat klucza i18n. `ui.user_skills` rozdzielono na `ui.user_skills` i `ui.user_skills_directory` dla PL/EN/DE.

## Pozostaje do wykonania

1. zdecydować i wdrożyć docelową geometrię wiersza Apertium;
2. zdecydować, czy GUI ma udostępniać wybór źródłowego języka Apertium;
3. domknąć detektor par jedno- i dwukierunkowych Apertium;
4. wykonać pełne E2E TranslateGemma przez rzeczywistą aplikację;
5. przed wydaniem wykonać smoke wszystkich głównych stron QML;
6. kontynuować synchronizację EN/DE i przegląd dokumentów historycznych przy kolejnych edycjach.

## Wniosek

Dokumentacja jest po tej operacji istotnie bliższa aktualnemu kodowi. Pomoc użytkownika obejmuje rzeczywisty przepływ przez wszystkie główne zakładki. Najważniejszy problem Apertium został jawnie udokumentowany jako rozbieżność kodu i wymaganie dalszej decyzji, a nie jako funkcja zakończona.

## 14. Pozostała długoterminowa praca porządkowa

Końcowa kontrola wykazała **94 starsze pliki Markdown bez front matter**. Nie wykonano masowej migracji tych plików, ponieważ polityka `docs/AGENTS.md` przewiduje uzupełnianie metadanych przy kolejnej istotnej edycji, a nie bezwarunkową migrację całego archiwum. Nowe i merytorycznie zmienione dokumenty objęte tym audytem mają metadane.
