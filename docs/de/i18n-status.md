---
id: i18n-status-v4-de
status: active
meta:
  contentType: Reference
  category: governance
version: 1.0.0
updated: 2026-10-03
owner: project-documentation
source: docs/I18N_STATUS.md
depends_on: [docs/de/i18n.md, docs/INDEX.md, docs/INDEX.yml]
expires_when: Änderung des Lokalisierungsumfangs oder der GUI-/Dokumentationsstruktur
last_validation: "pytest -q — 272 passed; compileall PASS; QML smoke 124; 2026-10-03"
---

# Lokalisierungsstatus — Tłumacz V4

## Sprachen

- **PL** — kanonische Quelle.
- **EN** — Benutzerlokalisierung.
- **DE** — Benutzerlokalisierung.

## GUI-Lokalisierung

| Bereich | PL | EN | DE | Status |
|---|---:|---:|---:|---|
| Haupttabs | ✓ | ✓ | ✓ | fertig |
| Tab Übersetzung | ✓ | ✓ | ✓ | fertig |
| Tab API & Server | ✓ | ✓ | ✓ | fertig |
| Tab Schalter | ✓ | ✓ | ✓ | fertig |
| Tab Hilfe | ✓ | ✓ | ✓ | fertig |
| Dateiauswahldialoge | ✓ | ✓ | ✓ | fertig |
| Backend-Bezeichnungen | ✓ | ✓ | ✓ | fertig |
| Benutzerprotokoll | ✓ | ✓ | ✓ | fertig |
| Benutzerhilfe | ✓ | ✓ | ✓ | fertig |

## Quelldateien der GUI-Lokalisierung

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

## Dokumentation

Lokalisierte Dokumentation:
- README EN/DE;
- STATUS EN/DE;
- TODO EN/DE;
- CHANGELOG EN/DE;
- DEVELOPMENT EN/DE;
- ARCHITECTURE EN/DE;
- aktive technische Dokumentation EN/DE;
- historische windows-exe-build.md EN/DE;
- i18n-Dokumentation EN/DE.

Historische Dokumente, Nachweisberichte, Testartefakte und einige Pläne werden nicht automatisch als übersetzt deklariert. Ihr Status wird in diesem Register und in docs/INDEX.yml geführt.

## Synchronisierungsregeln

1. Änderungen in PL sind die Quelle für EN und DE.
2. Code, Bezeichner, Pfade, Befehle, Klassennamen und Konfigurationswerte bleiben unverändert.
3. Die EN/DE-Hilfe muss dieselbe Themenstruktur wie PL behalten.
4. Jeder neue i18n-Schlüssel muss in PL, EN und DE vorhanden sein.
5. Änderungen an der Dokumentation erfordern die Aktualisierung von INDEX.md, INDEX.yml und DOCUMENTATION_CHANGELOG.md.
6. Historische Forschung darf nicht allein deshalb als aktive Funktion dargestellt werden, weil sie übersetzt wurde.

## Validierung dieser Welle

- pytest -q → 272 passed; compileall → PASS; QML smoke → 124.
- Backup vor der Welle: .migration-backups/pre-localization-wave2-20261003.tar.gz.
- SHA-256 des Backups: e515a074a291dc4d2ca2aae105e3b15e6a14517d51bee79555aa3b10e778b7ec.
