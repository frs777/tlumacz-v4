---
id: development-v4-de
status: active
meta:
  contentType: Guide
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: project-documentation
source: src/tlumacz/qml_gui/, pyproject.toml
depends_on: [docs/ARCHITECTURE.md, docs/STATUS.md]
expires_when: Änderung des Source-Bootstraps oder Entwickler-Workflows
last_validation: "Code- und Dokumentationsprüfung durch SentinelX 04.10.2026"
---

# Entwicklung V4

## Tests

Verhaltensänderungen werden im Zyklus RED → GREEN → REFACTOR umgesetzt.

Basistest:

    python -m pytest -q

Quality Gates:

    ruff check .
    mypy src
    python -m pytest -q

Die Installation von Abhängigkeiten ist nicht Teil des Bootstraps. Die Abhängigkeitsumgebung wird in der dafür vorgesehenen Migrationsphase vorbereitet.

## V4 aus dem Quellbaum ausführen

Das Repository verwendet eine `src/`-Struktur. Im Projektverzeichnis kann V4 ohne manuelles Setzen von `PYTHONPATH` gestartet werden:

```bash
cd /home/frs/Projekty/tlumacz-v4
python -m tlumacz.qml_gui.app
```

Der Repository-Eintrag `tlumacz -> src/tlumacz` ist ein lokaler Shim für diesen Modus. Er ersetzt keine Distributionsinstallation und ist nicht Bestandteil des Wheels.
