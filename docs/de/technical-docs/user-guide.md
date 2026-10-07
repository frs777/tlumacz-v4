---
id: user-guide-v4
status: active
meta:
  contentType: Guide
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: project-documentation
source: src/tlumacz/qml_gui/, src/tlumacz/cli.py
depends_on: [docs/STATUS.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: Änderung der aktiven GUI/CLI-Oberfläche
last_validation: "Code- und Dokumentationsprüfung durch SentinelX 04.10.2026; pytest 268 passed, compileall PASS, qmllint PASS"
---

# Benutzerhandbuch — Tlumacz V4

## Aktive Übersetzungs-Backends

- **llama.cpp** — lokale Runtime.
- **Cloud** — Cloud-Service-Provider.
- **Apertium** — lokales Backend über die Filter Engine.

## Grundablauf

1. Aktuelles V4 aus der korrekten Umgebung starten.
2. Ein Backend auswählen.
3. Ein Eingabedokument in einem unterstützten Format auswählen.
4. Quell- und Zielsprache sowie Backend-Parameter festlegen.
5. Übersetzung starten.

Die aktive Dokumentoberfläche umfasst gemäß der aktuellen FilterRegistry DOCX, ODT, HTML/XHTML, Markdown, EPUB und XLIFF. TXT und PDF sind in der Haupt-Pipeline von V4 nicht registriert.

Für den TranslateGemma-Chat-Template-Modus verwendet der llama.cpp-Adapter den Lingua-basierten LanguageDetector und wandelt die erkannte Quellsprache in ISO 639-1 um. Standard-llama.cpp, Cloud und Apertium verwenden diesen Detektor nicht global.

## Wichtig

Die Anwendung darf nicht über historische Umgebungen gestartet werden, die auf `/home/frs/Projekty/agent-translator-v4` verweisen, und nicht über das globale V3-Paket. Das Audit vom 2026-10-01 zeigte, dass eine solche Umgebung statt V4 die Version 0.31.2 starten kann.

## Zurückgezogen

FastAPI + Transformers und der alte OpenVINO-Pfad mit dem TranslateGemma-INT8-Modell sind keine aktiven V4-Pfade. Siehe `docs/RETIRED_FUNCTIONALITY.md`.
