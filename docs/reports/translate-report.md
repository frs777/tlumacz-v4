# Raport lokalizacji dokumentacji — Tłumacz V4

**Data:** 2026-10-01  
**Projekt:** `/home/frs/Projekty/tlumacz-v4/`  
**Źródło:** dokumentacja V4 w języku polskim  
**Języki docelowe:** English (`en`), Deutsch (`de`)

## 1. Stan wyjściowy

Projekt V4 jest natywnie polski. Nie znaleziono osobnego stosu MkDocs/i18n ani struktury `docs/docs/en`; zastosowanie gotowego skilla MkDocs wprost nie odpowiada rzeczywistej strukturze repozytorium.

Ustalono więc lokalizację zgodną z aktualnym V4:
- `docs/en/`
- `docs/de/`
- `README_en.md`
- `README_de.md`

Polskie dokumenty pozostają kanonicznym źródłem prawdy.

## 2. Wykonane tłumaczenia

### Dokumenty główne

| Źródło PL | EN | DE |
|---|---|---|
| `README.md` | `README_en.md` | `README_de.md` |
| `docs/STATUS.md` | `docs/en/status.md` | `docs/de/status.md` |
| `docs/TODO.md` | `docs/en/todo.md` | `docs/de/todo.md` |
| `docs/CHANGELOG.md` | `docs/en/changelog.md` | `docs/de/changelog.md` |
| `docs/DEVELOPMENT.md` | `docs/en/development.md` | `docs/de/development.md` |
| `docs/ARCHITECTURE.md` | `docs/en/architecture.md` | `docs/de/architecture.md` |

### Dokumentacja techniczna

Przetłumaczono aktywne dokumenty:
- `technical-docs/index.md`
- `technical-docs/user-guide.md`
- `technical-docs/models.md`
- `technical-docs/server-management.md`
- `technical-docs/cloud-translation.md`
- `technical-docs/xliff-pipeline.md`

oraz historyczny:
- `technical-docs/windows-exe-build.md`

Odpowiedniki znajdują się w `docs/en/technical-docs/` i `docs/de/technical-docs/`.

## 3. Dokumenty pozostawione poza pierwszą falą

Następujące dokumenty są dużymi materiałami historycznego researchu, a nie źródłem aktywnej architektury V4:

- `docs/technical-docs/TRANSLATEGEMMA_GOOGLE_CLOUD.md`
- `docs/technical-docs/TRANSLATEGEMMA_ONNX_DESKTOP_GUIDE.md`
- `docs/technical-docs/TRANSLATEGEMMA_OPENVINO_AMD_GUIDE.md`

Nie zostały przedstawione jako przetłumaczone. Ich status historyczny jest zachowany, aby lokalizacja nie sugerowała, że FastAPI/OpenVINO/TranslateGemma są aktywnymi backendami V4.

## 4. Dokumentacja i18n

Dodano:
- `docs/I18N.md` — zasady lokalizacji, struktura języków i synchronizacja;
- `docs/_inbox/translate-report.md` — niniejszy raport.

## 5. Backup

Przed rozpoczęciem większej zmiany wykonano backup:

`/home/frs/Projekty/tlumacz-v4/.migration-backups/pre-i18n-localization-20261001.tar.gz`

SHA-256:

`f0e0cf5afa699c27e562925c86c0c9d3fb62ca0c9d785634cd7775862a50d702`

## 6. Accurate Translation / Yaps

Skill `yaps-translation` został załadowany i sprawdzono jego kontrakt. W tej sesji nie był dostępny osobny lokalny runner Yaps jako narzędzie wykonawcze; dlatego nie deklaruję, że powyższe pliki zostały wygenerowane przez lokalny silnik Yaps. Tłumaczenia zostały wykonane bezpośrednio na podstawie kanonicznych plików V4 z zachowaniem terminologii technicznej, kodu, ścieżek i wyników testów.

Nie instalowano ani nie usuwano żadnego oprogramowania.

## 7. Walidacja zakresu

Sprawdzono:
- aktualny katalog projektu;
- stan dokumentacji V4;
- aktywną architekturę i status backendów;
- strukturę `docs/technical-docs/`;
- brak dedykowanego stosu MkDocs/i18n;
- wymagane dokumenty EN/DE;
- konieczność aktualizacji `INDEX.yml` i `DOCUMENTATION_CHANGELOG.md`.

## 8. Uwagi techniczne

V4 pozostaje projektem polskojęzycznym. Lokalizacje EN/DE są warstwą prezentacyjną dokumentacji i nie zmieniają kodu, konfiguracji ani aktywnych backendów.

## 9. Lokalizacja aplikacji GUI — wykonana 2026-10-01

Podczas ponownego audytu migracji V3→V4 potwierdzono, że V3 posiadał `tlumacz/i18n.py`. Kontrakt tego modułu został odtworzony w V4 jako:

- `src/tlumacz/i18n.py` — PL/EN/DE;
- `src/tlumacz/qt_gui/help_texts.py` — pomoc PL/EN/DE;
- `src/tlumacz/qt_gui/config.py` — ustawienie `language`;
- `src/tlumacz/qt_gui/settings_presenter.py` — trwałość języka;
- `src/tlumacz/qt_gui/view_builders.py`, `main_window.py`, `backend_presenter.py`, `document_presenter.py` — teksty GUI podpięte do lokalizacji.

Język można zmienić w zakładce Dodatki bez restartu aplikacji. Dodano testy regresyjne dla PL/EN/DE i przełączania w czasie pracy.

### Zakres pozostający

Komunikaty wyjątków z warstw aplikacyjnych i backendów nadal są w kodzie kontraktowym po polsku. Nie zostały automatycznie przeniesione do i18n, ponieważ wymagałoby to osobnej decyzji o kontrakcie błędów i zakresu lokalizacji warstwy domenowej.

## 10. Walidacja implementacji GUI

- testy lokalizacji: **5/5** przed rozszerzeniem testu przełączania;
- pełny zestaw V4 po izolacji konfiguracji testowej: **212 passed**;
- backup przed zmianą: `.migration-backups/pre-i18n-v3-port-20261001.tar.gz`.

### Korekta zakresu — logi użytkownika

Po ponownym przeglądzie powierzchni GUI i zrzutów ekranu uznano skrócone logi prezentowane użytkownikowi za element interfejsu. Dodano ich lokalizację PL/EN/DE: rozpoczęcie tłumaczenia, prefiks błędu oraz etykietę czasu; istniejące komunikaty zakończenia, zapisu, anulowania i stanu llama.cpp były już podpięte do i18n. Surowe komunikaty techniczne wyjątków pozostają danymi warstwy domenowej.
