---
id: i18n-status-v4-en
status: active
meta:
  contentType: Reference
  category: governance
version: 1.0.0
updated: 2026-10-03
owner: project-documentation
source: docs/I18N_STATUS.md
depends_on: [docs/en/i18n.md, docs/INDEX.md, docs/INDEX.yml]
expires_when: change to localization scope or GUI/documentation structure
last_validation: "pytest -q — 272 passed; compileall PASS; QML smoke 124; 2026-10-03"
---

# Localization status — Tłumacz V4

## Languages

- **PL** — canonical source.
- **EN** — user-facing localization.
- **DE** — user-facing localization.

## GUI localization

| Area | PL | EN | DE | Status |
|---|---:|---:|---:|---|
| Main tabs | ✓ | ✓ | ✓ | complete |
| Translation page | ✓ | ✓ | ✓ | complete |
| API & Server page | ✓ | ✓ | ✓ | complete |
| Switches page | ✓ | ✓ | ✓ | complete |
| Help page | ✓ | ✓ | ✓ | complete |
| File-selection dialogs | ✓ | ✓ | ✓ | complete |
| Backend labels | ✓ | ✓ | ✓ | complete |
| User log | ✓ | ✓ | ✓ | complete |
| User help | ✓ | ✓ | ✓ | complete |

## GUI localization source files

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

## Documentation

Localized documentation:
- README EN/DE;
- STATUS EN/DE;
- TODO EN/DE;
- CHANGELOG EN/DE;
- DEVELOPMENT EN/DE;
- ARCHITECTURE EN/DE;
- active technical documentation EN/DE;
- historical windows-exe-build.md EN/DE;
- i18n documentation EN/DE.

Historical documents, evidence reports, test artifacts and some plans are not automatically declared translated. Their status is maintained in this register and in docs/INDEX.yml.

## Synchronization rules

1. Changes in PL are the source for EN and DE.
2. Code, identifiers, paths, commands, class names and configuration values remain unchanged.
3. EN/DE help must preserve the same topic structure as PL.
4. Every new i18n key must exist in PL, EN and DE.
5. Documentation changes require updates to INDEX.md, INDEX.yml and DOCUMENTATION_CHANGELOG.md.
6. Historical research must not be presented as active functionality merely because it was translated.

## Validation for this wave

- pytest -q → 272 passed; compileall → PASS; QML smoke → 124.
- Backup before wave: .migration-backups/pre-localization-wave2-20261003.tar.gz.
- Backup SHA-256: e515a074a291dc4d2ca2aae105e3b15e6a14517d51bee79555aa3b10e778b7ec.
