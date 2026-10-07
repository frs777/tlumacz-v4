---
id: i18n-status-v4
status: active
meta:
  contentType: Reference
  category: governance
version: 1.0.0
updated: 2026-10-07
owner: project-documentation
source: docs/
depends_on: [docs/I18N.md, docs/INDEX.md, docs/INDEX.yml, docs/DOCUMENTATION_CHANGELOG.md]
expires_when: zmiana zakresu lokalizacji lub struktury GUI/dokumentacji
last_validation: "pytest tests/test_qml_gui.py — 39 passed; 2026-10-03"
---

# Stan lokalizacji — Tłumacz V4

## Języki

- PL — źródło kanoniczne.
- EN — lokalizacja użytkowa.
- DE — lokalizacja użytkowa.

## Lokalizacja GUI

| Obszar | PL | EN | DE | Stan |
|---|---:|---:|---:|---|
| Zakładki główne | ✓ | ✓ | ✓ | gotowe |
| Karta Tłumaczenie | ✓ | ✓ | ✓ | gotowe |
| Karta API i serwer | ✓ | ✓ | ✓ | gotowe |
| Karta Przełączniki | ✓ | ✓ | ✓ | gotowe |
| Karta Pomoc | ✓ | ✓ | ✓ | gotowe |
| Dialogi wyboru plików | ✓ | ✓ | ✓ | gotowe |
| Etykiety backendów | ✓ | ✓ | ✓ | gotowe |
| Log użytkownika | ✓ | ✓ | ✓ | gotowe |
| Pomoc podręczna | ✓ | ✓ | ✓ | gotowe |

## Pliki źródłowe lokalizacji GUI

- src/tlumacz/i18n.py
- src/tlumacz/qml_gui/bridge.py
- src/tlumacz/qml_gui/Main.qml
- src/tlumacz/qml_gui/TranslationPage.qml
- src/tlumacz/qml_gui/ApiPage.qml
- src/tlumacz/qml_gui/ExtrasPage.qml
- src/tlumacz/qml_gui/HelpPage.qml
- src/tlumacz/qml_gui/help.pl.md
- src/tlumacz/qml_gui/help.en.md
- src/tlumacz/qml_gui/help.de.md

## Strona WWW

- EN — strona główna dostępna pod `en/index.html`; strona PL zawiera przełącznik PL → EN.
- Zakres tej fali obejmuje anglojęzyczną stronę główną; pozostałe podstrony pozostają w wersji PL do czasu ich osobnej lokalizacji.

## Dokumentacja

Gotowe lokalizacje:
- README EN/DE;
- STATUS EN/DE;
- TODO EN/DE;
- CHANGELOG EN/DE;
- DEVELOPMENT EN/DE;
- ARCHITECTURE EN/DE;
- aktywna dokumentacja techniczna EN/DE;
- historyczny windows-exe-build.md EN/DE;
- dokumentacja i18n EN/DE.

Dokumenty historyczne, raporty dowodowe, artefakty testowe i część planów nie są automatycznie deklarowane jako przetłumaczone. Ich status należy utrzymywać w tym rejestrze i w docs/INDEX.yml.

## Reguły synchronizacji

1. Zmiana w PL jest źródłem dla EN i DE.
2. Kod, identyfikatory, ścieżki, komendy, nazwy klas i wartości konfiguracji pozostają niezmienione.
3. Pomoc EN/DE musi zachować tę samą strukturę tematów co PL.
4. Każdy nowy klucz i18n musi występować w PL, EN i DE.
5. Po zmianie dokumentacji aktualizuje się INDEX.md, INDEX.yml i DOCUMENTATION_CHANGELOG.md.
6. Nie wolno oznaczać historycznego researchu jako aktualnej funkcjonalności tylko dlatego, że został przetłumaczony.

## Walidacja tej fali

- pytest -q → 272 passed; compileall → PASS; QML smoke → 124.
- Backup przed falą: .migration-backups/pre-localization-wave2-20261003.tar.gz.
- SHA-256 backupu: e515a074a291dc4d2ca2aae105e3b15e6a14517d51bee79555aa3b10e778b7ec.
