---
id: historical-windows-exe-build
status: historical
meta:
  category: historical
  updated: 2026-10-01
  source: V3 research/build documentation
expires_when: Ersetzung durch aktuelle V4-Dokumentation
---

# DOKUMENTSTATUS: HISTORISCH / V3-RESEARCH

> Dieses Dokument ist keine Quelle der aktuellen V4-Funktionalität. Es beschreibt historische Forschung sowie FastAPI/OpenVINO/TranslateGemma- oder Build-Verhalten von V3. Es bleibt als Referenz erhalten. Für den aktuellen Stand siehe `docs/STATUS.md`, `docs/technical-docs/index.md` und `docs/RETIRED_FUNCTIONALITY.md`.

# Tlumacz V3 — Bau des Windows-EXE-Pakets

## Stand 2026-09-10

Anwendungsversion: **0.31.1**.
Repository: `frs777/tlumacz`, Branch `main`.

Der aktuelle Windows-Build wird nativ durch GitHub Actions auf `windows-latest` ausgeführt.
Zum Paketieren der Python/PySide6-Anwendung wird **PyInstaller 6.22.2** verwendet.
In CI verwendetes Python: **3.12**.

## Aktueller Workflow

Datei: `.github/workflows/build-windows.yml`

Der Workflow startet:
- manuell über `workflow_dispatch`,
- automatisch für `v*`-Tags.

Schritte:
1. Repository-Checkout,
2. Python 3.12 + pip-Cache,
3. Installation des Projekts und der Testabhängigkeiten,
4. vollständiges `pytest` mit `QT_QPA_PLATFORM=offscreen`,
5. PyInstaller mit `build/windows/tlumacz.spec`,
6. EXE-Smoke-Test,
7. SHA256,
8. Artifact-Upload zu GitHub Actions.

CI-Test-/Build-Abhängigkeiten: `pyinstaller`, `pytest`, `fastapi`, `uvicorn`.
FastAPI und Uvicorn werden für Tests installiert, aber nicht in das Basis-EXE gepackt.

## PyInstaller-Datei

Datei: `build/windows/tlumacz.spec`

Anwendungseinstiegspunkt: `tlumacz/qt_gui/app.py`.
Das EXE enthält Qt-Ressourcen (`*.qss`, `*.svg`) sowie integrierte Markdown-Skills aus `tlumacz.skills`.

Der Basis-Build schließt optionale Backends aus:
- `fastapi`, `uvicorn`,
- `transformers`, `torch`, `accelerate`, `safetensors`,
- `openvino`, `openvino_genai`.

Das EXE läuft als GUI-Anwendung ohne Konsole (`console=False`).

## Letzter verifizierter Build

Der Workflow wurde erfolgreich abgeschlossen:
`https://github.com/frs777/tlumacz/actions/runs/34456326653`

Datei: `Tlumacz-0.31.1-windows-x86_64.exe`
Größe: 48 906 171 B (~46,6 MiB)
SHA256: `ca0334bbee4eb8ddc0961e977fc8adff12dfd1a04c911dac421a6c6b718ccca3`

Release:
`v0.31.1`

Das EXE wurde als Asset zum GitHub-Release hinzugefügt.

## Wichtige Einschränkung des aktuellen EXE

Das aktuelle Paket ist ein **Basis-Windows-Build**, keine vollständige Runtime für alle Backends.
Optionale KI-Komponenten sind nicht enthalten.

Die Distributionsarchitektur soll entsprechend der Entscheidung vom 2026-09-10 später geändert werden.

## Zielkonzept für die Windows-Distribution

Die Anwendung basiert auf lokaler Übersetzung. Daher **sollte llama-server Bestandteil der Basisinstallation von Windows sein**, nicht ein optionales Add-on.

Das Modell sollte nicht in das EXE eingebettet werden. Der Benutzer soll ein mit llama.cpp kompatibles Modell auswählen können, z. B. TranslateGemma 4B/12B, Qwen oder ein anderes geeignetes Modell.

Die GUI nicht auf ein einzelnes Feld `C:\AI\Models\model.gguf` reduzieren. Der bestehende Mechanismus `model_profiles` soll erhalten und für Auswahl/Profilierung von Modellen erweitert werden.

Vorgeschlagene Aufteilung:
1. Tlumacz GUI + llama-server — immer.
2. Basis-Dokumentbibliotheken und Core — immer.
3. FastAPI + Uvicorn — optional.
4. Transformers + PyTorch — optional.
5. OpenVINO — optional.
6. Benutzerübersetzungs-Skills — optional, mit dem GitHub-Repository synchronisiert.
7. Glossar/Wörterbücher — optional, mit dem GitHub-Repository synchronisiert.
8. Modelle — separat vom Benutzer heruntergeladen, außerhalb des Installers.

Bevorzugtes Zielprodukt für Windows: Installer `Tlumacz-Setup.exe` mit Checkboxen für optionale Komponenten sowie ein separates portables Basis-EXE.

Optionale Python-Abhängigkeiten sollten in der privaten Runtime/venv der Anwendung installiert werden, damit der System-Python nicht geändert werden muss.

Der Installer sollte klar darauf hinweisen, dass Modelle nicht Teil des Installers sind und passend zur Hardware des Benutzers ausgewählt werden müssen.

## Skill für den EXE-Build

Eine vollständige Kopie des verwendeten Skills befindet sich neben diesem Dokument:
`docs/technical-docs/windows-compiler-skill.md`

Quelle:
`SKILL.md`, das im historischen Windows-Build-Prozess verwendet wurde

Wichtige Regeln:
- nativen Build auf `windows-latest` bevorzugen,
- PyInstaller für Python-Anwendungen verwenden,
- für GUI-Anwendungen `--windowed` / `console=False` verwenden,
- bei komplexerem Bundling eine `.spec`-Datei verwenden,
- Daten, Ressourcen und Hidden Imports explizit hinzufügen,
- unnötige Module zur Größenreduzierung ausschließen,
- Anwendung vor dem Build testen,
- fertiges EXE einem Smoke-Test unterziehen,
- Artefakte mit `actions/upload-artifact` veröffentlichen,
- Git-Tags für Releases verwenden,
- Code-Signing für die finale Distribution erwägen,
- Installer mit NSIS, Inno Setup oder WiX bauen.

## Nächste Stufe nach der GUI-Prüfung

Nach Bereitstellung von GUI-Screenshots zuerst die aktuelle Oberfläche mit dem obigen Konzept vergleichen.
Danach `model_profiles`, Serverkonfiguration und vorhandene Einstellungsfelder prüfen.
Erst anschließend Änderungen an Installer, Modellauswahl und optionalen Komponenten entwerfen.

GUI oder Modellmechanismus nicht blind ändern.
