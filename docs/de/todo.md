---
id: todo-v4-de
status: active
meta:
  contentType: TaskList
  category: governance
version: 0.40.0
updated: 2026-10-04
owner: project-documentation
source: src/tlumacz/
depends_on: [docs/STATUS.md]
expires_when: Abschluss der aktuellen Release-Candidate-Aufgaben
last_validation: "Code- und Dokumentationsprüfung durch SentinelX 04.10.2026"
---

# TODO V4

## Phase 13 — FINALER HANDOFF UND FREEZE — ABGESCHLOSSEN
- [x] Migrationsstatus dokumentiert;
- [x] aktuelles Artefakt und SHA-256 erfasst;
- [x] F11/F12-Blocker ausdrücklich erfasst;
- [x] keine Veröffentlichung auf GitHub;
- [x] Dokumentationsbackup;
- [x] Handoff-Bericht.

Das finale Release 0.40.0 bleibt wegen Apertium eng-pol, Windows und Dependency/Lizenzarbeit offen.

# TODO V4

## Nächste Stufe

### Phase 12 — Release 0.40.0 — RELEASE CANDIDATE, OFFEN

- [x] vollständige Suite — 182 passed;
- [x] Compile;
- [x] statische Analyse — Ruff + mypy;
- [x] Contract-Suite;
- [x] Integration/E2E — 19 passed;
- [ ] Windows;
- [ ] Packaging — abhängig vom Abschluss von Phase 11;
- [x] Dokumentation;
- [x] CHANGELOG;
- [x] Migrationsnotizen;
- [x] Clean-Installation Linux;
- [x] Rollback-Verfahren.

Artefakt: `temp/wheel/tlumacz-0.40.0-py3-none-any.whl`. SHA-256: `161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835`.

Das Glossar bleibt außerhalb des blockierenden Umfangs: Es ist eine separate Ressource und wird nicht in das Artefakt einkompiliert.

### Phase 11 — Packaging — OFFEN, TEILWEISE UMGESETZT

- [ ] Dependency Closure;
- [ ] Lizenzen;
- [x] NOTICE;
- [x] Java-Runtime;
- [x] Okapi;
- [ ] Apertium — vollständiges `eng-pol.t1x.bin` fehlt;
- [x] Python-Paket — Wheel 0.40.0 gebaut;
- [x] Linux — Clean-Installation und Smoke PASS;
- [ ] Windows — native Windows-Runtime fehlt;
- [x] Clean-Umgebung — in sauberer venv verifiziert;
- [x] Artefakt-Smoke-Test — PASS für Python/Java/Apertium-Engine;
- [x] Clean-Installation — Linux PASS;
- [x] Rollback-Verfahren.

Status: Phase 11 bleibt wegen Apertium, Windows, Dependency Closure und der vollständigen Lizenzprüfung offen.

- [x] kein FastAPI;
- [x] kein OpenVINO;
- [x] keine Konfiguration dafür;
- [x] keine Tests dafür;
- [x] keine Imports;
- [x] keine Abhängigkeiten;
- [x] keine Feature-Flags;
- [x] keine ersetzten Dokumentpfade.

### Phase 9 — GUI — ABGESCHLOSSEN / Stand nach dem Cleanup
- [x] BackendController — aktiver Controller für die Backendauswahl;
- [x] Entfernung von TranslationController, SettingsController, DocumentController, ProgressController und DiagnosticsController;
- [x] Entfernung ihrer privaten Abhängigkeiten und Instanzen aus TranslationApp;
- [x] Vertragstests der GUI-Schicht.

### Phase 8 — Translator — ABGESCHLOSSEN
- [x] ChunkPlanner;
- [x] PromptBuilder;
- [x] TranslationExecutor;
- [x] TranslationCache;
- [x] ResultValidator;
- [x] TranslationOrchestrator;
- [x] DocumentTranslationService.

### Phase 7 — Document Services — ABGESCHLOSSEN
- [x] DOCX;
- [x] ODT;
- [x] HTML/XHTML;
- [x] Markdown;
- [x] EPUB;
- [x] XLIFF;
- [x] weitere Formate nur bei nachgewiesenem Bedarf.

### Abgeschlossen
- Phase 0 — Baseline;
- Phase 1 — Bootstrap;
- Phase 2 — Verträge;
- Phase 3 — Filter Engine;
- Phase 4 — LlamaCppBackend;
- Phase 5 — Cloud;
- Phase 6 — Apertium.

Weitere Phasen gemäß `docs/archive/migration/PLAN_MIGRACJI-v4.md`.

## Audit 2026-10-01 — Aktualisierung

- [x] Dokumentationsaudit;
- [x] Codeaudit;
- [x] aktuelles pytest — 182 passed;
- [x] Ruff — PASS;
- [x] mypy — PASS;
- [x] compileall — PASS;
- [x] CLI in frischer Umgebung aus dem Wheel — PASS;
- [ ] Apertium eng-pol — durch `cas_sp` blockiert;
- [ ] Dependency Closure/Lizenzen;
- [ ] finale Release-Verifikation.

## GUI/Cloud — 2026-10-01

- [x] V3/V4-GUI-Vergleich;
- [x] V3/V4-Cloud-Vergleich;
- [x] Analyse der Referenz-Screenshots;
- [x] Backup vor größerer Änderung;
- [x] Wiederherstellung der Qt-GUI;
- [x] Wiederherstellung aktiver Cloud-Provider;
- [x] Wiederherstellung der Cloud-Profile;
- [x] Mozhi-GUI;
- [x] Entfernung von FastAPI/OpenVINO aus der aktiven GUI;
- [x] Offscreen-GUI-Tests;
- [x] vollständige Suite 195 passed;
- [x] Ruff;
- [x] mypy;
- [x] compileall;
- [ ] Apertium eng-pol / cas_sp;
- [ ] Dependency Closure/Lizenzen;
- [ ] Windows;
- [ ] finale Release-Verifikation.

## Abschluss der UI-Oberfläche — 2026-10-01

- [x] V3/V4-objectName-Vergleich;
- [x] aktive Oberfläche Übersetzung/API/Extras/Hilfe;
- [x] UI-Glossar;
- [x] UI für Skill-Verwaltung;
- [x] PL/EN-Hilfe und Über-Dialog;
- [x] Output-Splitter, elapsed/spinner;
- [x] GUI-Oberflächen-Paritätstest.

Aktuelle vollständige Suite: 196 passed.

## Korrektur der GUI/Cloud-Anforderungen — 2026-10-01

- [ ] Kategorie **Custom** für externe API-Endpunkte hinzufügen und nach Auswahl eine editierbare Adresskonfiguration bereitstellen;
- [ ] Verhalten des speziellen **TranslateGemma**-Templates für Sprachcodes verifizieren;
- [x] SimplyTranslate aus dem aktiven V4 zurückziehen;
- [ ] Verfügbarkeit von DLX in der tatsächlich laufenden GUI bestätigen;
- [ ] Verfügbarkeit von Apertium in der tatsächlich laufenden GUI bestätigen.

## Zeitplan — Stand nach P0-Launcher — 2026-10-01

- [x] P0: V4-Start von globalem V3 für `python -m tlumacz...` aus dem Projektverzeichnis trennen;
- [x] P0: Bootstrap-Test ohne `PYTHONPATH`;
- [x] P0: vollständige Offscreen-Regression — 201 passed;
- [ ] P1: weitere `MainWindow`-Dekomposition;
- [ ] P1: Persistenz von `last_input_path`, `last_output_path`, `server_gguf_path`;
- [ ] P1: Paritätsfunktionen für Custom, DLX, Apertium und TranslateGemma;
- [ ] P2: Aufräumen von V3-bezogenen Relikten und Tests.

## Verifikationsupdate — 2026-10-01

- [x] P1: Backendauswahl, Einstellungen, Dokumente, Fortschritt und Worker aus `MainWindow` ausgelagert;
- [x] P1: Persistenz von `last_input_path`, `last_output_path`, `server_gguf_path`;
- [x] GUI-Offscreen-Regression — 205 passed;
- [ ] weitere Auslagerung des GUI-Tab-Aufbaus;
- [ ] Diagnostikintegration in den GUI-Ablauf.

## 2026-10-01 — P1 — Stand nach GUI-Dekomposition

- [x] Aufbau des Tabs Übersetzung ausgelagert;
- [x] Aufbau des API- und Server-Tabs ausgelagert;
- [x] Aufbau des Extras-Tabs ausgelagert;
- [x] Aufbau des Hilfe-Tabs ausgelagert;
- [x] erforderliche Qt-Objektnamen für Paritätstests erhalten;
- [x] Paritätstest an die neue Modulgrenze angepasst;
- [x] vollständige Regression — 206 Tests;
- [x] Ruff;
- [x] compileall;
- [x] Backup vor größerer Änderung.

### Nächste Schritte

- [ ] Paritätsfunktionen prüfen: Custom, DLX, Apertium in der tatsächlichen GUI-Oberfläche und TranslateGemma;
- [ ] vollständiges TranslateGemma-E2E über die reale Anwendung und das GGUF-Modell ausführen;
- [ ] Round-Trip aller `AppSettings` gegen die aktuelle QML-Integration verifizieren;
- [ ] `*.bak.*`-Backuprelikte erst nach separatem Audit entfernen und dabei erforderliche Historie erhalten.
