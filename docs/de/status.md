---
id: status-v4-de
status: active
meta:
  contentType: Status
  category: governance
version: 0.40.0
updated: 2026-10-04
owner: project-documentation
source: src/tlumacz/
depends_on: [docs/STATUS.md]
expires_when: Änderung des aktuellen Projektstatus
last_validation: "Code- und Dokumentationsprüfung durch SentinelX 04.10.2026"
---

## 2026-10-04 — Dokumentation mit dem aktuellen Code synchronisiert

Die aktuelle Code-/Dokumentationskorrelation bestätigt `TranslationApp.restart_llama()`, den isolierten TranslateGemma/Lingua-Pfad, die SecretStore-Migration alter Cloud-API-Schlüssel und die Entfernung ungenutzter GUI-Controller. `BackendController` bleibt aktiv. Verifikation: **268 passed**, compileall PASS, qmllint PASS.

# V4 STATUS

## 2026-09-30

### Migrationsstatus

- Phase 0 — Baseline: ABGESCHLOSSEN.
- Phase 1 — V4-Bootstrap: ABGESCHLOSSEN.
- Phase 2 — Verträge: ABGESCHLOSSEN.
- Phase 3 — Filter Engine: Komponenten und Filter umgesetzt; das vollständige Phasenkriterium muss noch separat durch einen DOCX-Round-Trip verifiziert werden.
- Phase 4 — LlamaCppBackend: ABGESCHLOSSEN.
- Phase 5 — Cloud: ABGESCHLOSSEN.
- Phase 6 — Apertium: gemäß der bisherigen Verifikation von Adapter/Backend/Runtime/Language-Plugins ABGESCHLOSSEN.
- Phase 7 — Document Services: ABGESCHLOSSEN; DOCX, ODT, HTML/XHTML, Markdown, EPUB und XLIFF sind verifiziert.
- Phase 8 — Translator: ABGESCHLOSSEN; ChunkPlanner, PromptBuilder, TranslationExecutor, TranslationCache, ResultValidator, TranslationOrchestrator und DocumentTranslationService sind verifiziert.
- Phase 9 — GUI: ABGESCHLOSSEN; Anwendungskontroller und Vertragstests sind verifiziert.
- Phase 10 — Legacy-Entfernung: ABGESCHLOSSEN nach dem Zero-Reference-Audit.

### Phase-10-Verifikation — Legacy-Entfernung

Das V4-Audit ergab:
- keine Referenzen auf `fastapi`, `FastAPIServerManager`, `fastapi_server`, `openvino`, `openvino_backend` oder `TranslateGemma INT8` in aktivem Code und Tests;
- keine FastAPI/OpenVINO-Dateien in `src/`, `tests/` oder der aktiven technischen Dokumentation;
- keine dieser Abhängigkeiten in `pyproject.toml`;
- keine Konfiguration dieser Technologien in V4-Konfigurationsdateien;
- keine Feature-Flags für diese Technologien;
- keine ersetzten Dokumentpfade, die auf diese Komponenten verweisen.

Verbleibende FastAPI/OpenVINO-Nennungen befinden sich in Migrationsdokumentation und im V3-Baseline-Material als Beschreibung der Quelle und der Migrationsentscheidungen; sie sind keine aktiven Runtime-Referenzen.

Verifikation:
- Zero-Reference-Scan von aktivem Code/Tests/Konfiguration — PASS;
- Struktur des Phasen-9/10/11-Plans — PASS;
- vollständiges pytest — 180 passed;
- Ruff — PASS;
- mypy — PASS, 60 Quelldateien.

### Nächste Stufe

Phase 11 — Packaging.

### Phase 11 — Packaging — gestartet, BLOCKIERT

Vor den Änderungen wurden Dependency-Closure-Audit und Backup durchgeführt:
- Backup: `.migration-backups/pre-packaging-phase11-20260930.tar.gz`;
- kontrollierte Okapi-Runtime aus V3 nach `filtry/runtime` kopiert (42 Dateien, 22 MiB);
- die zuvor deklarierte `filtry/runtime` fehlte, wodurch der Java-Launcher keine vollständige Runtime hatte;
- der Wheel-Bau im Checkout ist wegen der Eigentümerschaft des übergeordneten Repositorys blockiert (`setuptools`/Git meldet `dubious ownership`);
- der Bau der Apertium-Daten aus der Arbeitskopie scheiterte beim Bereinigen des Stagings in `/tmp` mit einem Berechtigungsfehler; die Phase wurde angehalten;
- V3 wurde nicht absichtlich verändert.

**Das Kriterium für Phase 11 ist nicht erfüllt.** Kein Packaging-Punkt wurde ohne vollständige Verifikation als abgeschlossen markiert.

### Phase 11 — Packaging — teilweise umgesetzt, weiterhin OFFEN

Nach einem erneuten Versuch mit Staging unter `./temp`:
- `tlumacz-0.40.0-py3-none-any.whl` wurde gebaut (~43 MiB);
- das Wheel enthält Okapi-Runtime, Java Filter Host, private Apertium-Runtime und NOTICE/Lizenzen;
- Clean-Installation aus dem Wheel: PASS;
- `tlumacz --version`: `0.40.0`;
- Java Filter Host aus Ressourcen der installierten Wheel-Installation: PASS;
- Apertium Engine 3.9.12 aus Ressourcen der installierten Wheel-Installation: PASS;
- vollständiges pytest: 182 passed;
- Ruff: PASS;
- mypy: PASS, 60 Dateien.

Verbleibende Blocker:
- vollständiges `eng-pol.t1x.bin` fehlt; Wiederherstellung aus V3 scheitert mit `Undefined attr-item cas_sp`;
- Windows-Apertium-Runtime und weitere native Ressourcen fehlen — das aktuelle Artefakt ist Linux x86-64;
- vollständige Dependency-Closure und komponentenweise Lizenzprüfung erfordern weitere Verifikation.

Das Phase-11-Kriterium bleibt **NICHT ERFÜLLT**.

### Phase 12 — Release 0.40.0 — RELEASE CANDIDATE

Verifiziert:
- vollständiges pytest: **182 passed**;
- compileall: **PASS**;
- Ruff: **PASS**;
- mypy: **PASS**, 60 Dateien;
- Integration/E2E: **19 passed**;
- Clean-Linux-Installation aus dem Wheel ohne Abhängigkeiten: **PASS**;
- Artefaktversion: **0.40.0**;
- Java Filter Host aus dem Wheel: **PASS**;
- Apertium Engine 3.9.12 startet aus dem Wheel.

Artefakt: `temp/wheel/tlumacz-0.40.0-py3-none-any.whl`

SHA-256: `161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835`

Dokumentation zu Phase 12:
- `docs/release/RELEASE_NOTES_0.40.0.md`;
- `docs/archive/migration/MIGRATION_NOTES_V3_TO_V4.md`;
- `docs/release/ROLLBACK_0.40.0.md`;
- `docs/reports/FAZA_12_RELEASE_2026-09-30.md`.

Phase 12 ist nicht abgeschlossen. Windows sowie Packaging-/Dependency-/Lizenzblocker aus Phase 11 bleiben bestehen.

Das Glossar ist kein Blocker: Es bleibt eine separate Ressource und kann später hinzugefügt werden.

### Phase 13 — finaler Handoff und Freeze

Phase 13 wurde als lokaler Handoff-Freeze abgeschlossen. Der aktuelle Stand des Release Candidate 0.40.0, das Artefakt, SHA-256, das Dokumentationsbackup und die aus Phase 11/12 verbleibenden Blocker wurden dokumentiert. Es erfolgt kein Push zu GitHub.

Bericht: `docs/reports/FAZA_13_FINAL_HANDOFF_2026-09-30.md`.

Das finale Release 0.40.0 bleibt wegen Apertium eng-pol, Windows und Dependency/Lizenzarbeit offen.

## Offizielles V4-Projektverzeichnis und Bereinigung temporärer Dateien — 2026-10-01

Das offizielle V4-Projektverzeichnis ist jetzt:

`/home/frs/Projekty/tlumacz-v4/`

Das frühere Verzeichnis `/home/frs/Projekty/agent-translator-v4/` gilt nicht mehr als aktuelles Projektverzeichnis.

Im neuen Verzeichnis wurde eine vollständige rekursive Prüfung durchgeführt. Vor der Bereinigung wurden 513 Dateien mit dem Muster `*.bak*` gefunden, insgesamt etwa 2,9 MiB.

Es wurden ausschließlich diese `*.bak*`-Dateien entfernt. Projektverzeichnisse, Dokumentation, Code, Tests und andere temporäre Dateien mit anderen Namen wurden nicht entfernt.

Nach der Bereinigung:
- verbleibende `*.bak*`-Dateien: 0;
- Verzeichnisse im Projektbaum: 970;
- verbleibende reguläre Dateien: 6449.

Die Bereinigung umfasste auch Archiv- und Berichtsunterverzeichnisse. Im alten Verzeichnis `/home/frs/Projekty/agent-translator-v4/` wurde nichts gelöscht.

Hinweis: `/home/frs/Projekty/tlumacz-v4/` enthält derzeit kein `.git`-Verzeichnis. Der Git-Zustand wurde durch diese Operation nicht verändert.

## Engineering-Audit und Qualitätsreparatur — 2026-10-01

Nach der Festlegung des korrekten Projektverzeichnisses wurden Dokumentation, Code, Tests, statische Analyse und Packaging vollständig geprüft.

### Aktuelle Verifikation
- pytest: **182 passed**;
- Ruff: **PASS**;
- mypy: **PASS**, 60 Dateien;
- compileall: **PASS**;
- `PYTHONPATH=src python3 -m tlumacz --version`: **PASS**, 0.40.0;
- frische venv aus dem Wheel: `python -m tlumacz --version` **PASS**;
- frische venv aus dem Wheel: `tlumacz --version` **PASS**;
- Apertium Runtime/E2E: **6 passed**;
- Bau von `eng-pol.t1x.bin`: **BLOCKIERT** durch `Undefined attr-item cas_sp`.

### Behoben
- Import-Reihenfolge in `processor.py` und `test_docx_filter.py`;
- Ruff analysiert keine regenerierbaren `temp/`-Stagingdaten oder Migrationsbackups mehr;
- aktive Migrationsdokumente verweisen nun auf `/home/frs/Projekty/tlumacz-v4/`.

### CLI
Der Fehler des Systeminterpreters wurde durch den Import des globalen V3-Pakets `/usr/lib/python3.14/site-packages/tlumacz` verursacht. Alte Umgebungen hatten Shebangs mit Verweisen auf das historische `/home/frs/Projekty/agent-translator-v4`. Eine frische venv aus dem aktuellen Wheel funktioniert korrekt.

### Apertium
Es wurde keine unbestätigte `cas_sp`-Korrektur eingeführt. Die lokale Transferdatei und die Upstream-Version von apertium-eng-pol verwenden `cas_sp` ohne Deklaration des Attributs; der aktuelle Compiler lehnt die Datei ab. Der Blocker bleibt Bestandteil von Phase 11.

## GUI/Cloud-V3 → V4-Regression — Audit und Reparatur — 2026-10-01

Eine Regression bei der GUI/Cloud-Migration wurde gefunden und behoben. V4 besaß zuvor keine Qt-Schicht und die meisten V3-Cloud-Provider fehlten.

### Stand nach der Reparatur
- V4-Qt-GUI: als Adapter über der Anwendungsschicht WIEDERHERGESTELLT;
- aktive GUI-Backends: llama.cpp, Apertium, Cloud;
- FastAPI/OpenVINO: NICHT WIEDERHERGESTELLT;
- Cloud-Provider: 8 Adapter;
- Cloud-Profile: 12;
- Mozhi-GUI: WIEDERHERGESTELLT;
- Offscreen-GUI-Test: 3 passed;
- V3-Provider-Kompatibilitätstest: 21 passed;
- vollständige Suite: 195 passed;
- Ruff: PASS;
- mypy: PASS — 68 Dateien;
- compileall: PASS;
- Wheel 0.40.0: BUILD PASS.

Regressionsbericht: `docs/Audyt/AUDYT_REGRESJI_GUI_CLOUD_V3_V4_2026-10-01.md`.
Reparaturbericht: `docs/Audyt/RAPORT_NAPRAWY_GUI_CLOUD_2026-10-01.md`.
Plan: `docs/archive/plans/PLAN_NAPRAWCZY_GUI_CLOUD_2026-10-01.md`.
Backup: `.migration-backups/pre-gui-cloud-repair-20261001.tar.gz`.

## UI-Oberfläche — Abschluss — 2026-10-01

Ein Vergleich der V3/V4-objectNames bestätigte fehlende Elemente in den Tabs Extras/Hilfe. Die aktive UI-Oberfläche wurde wiederhergestellt, mit Ausnahme der FastAPI/OpenVINO-Elemente. Oberflächentest: 1 passed; GUI-Tests zusammen: 4 passed.

Endverifikation dieser Stufe: **196 passed**, Ruff PASS, mypy PASS (68 Dateien), compileall PASS, Wheel PASS.

## 2026-10-01 — Meldung: llama.cpp-Server startet nicht

- **Status:** gemeldet, Ursache unbekannt.
- **Komponente:** llama.cpp-Server/Runtime.
- **Symptom:** Der llama.cpp-Server startet nicht.
- **Klassifikation:** funktionaler Fehler, der reproduziert und diagnostiziert werden muss.
- **Priorität:** P1 — blockiert das lokale llama.cpp-Backend.
- **Ursache:** noch nicht bestimmt; es wird derzeit kein Fehler in Konfiguration, Modell, Prozessparametern oder Umgebung angenommen.
- **Nächster Schritt:** exakte Startmeldung bzw. Log erfassen und feststellen, welches Executable, Modell und welche Konfiguration tatsächlich verwendet werden.

## Dokumentationsbereinigung nach der Migration — 2026-10-01

Die erste strukturierte Bereinigungswelle der Dokumentation nach der V3 → V4-Migration wurde abgeschlossen.

- V3 wurde als historische Quelle behandelt; seine Dokumente wurden weder verschoben noch gelöscht.
- Ein vollständiges Register aller Dateien unter docs/ wurde erstellt: docs/INDEX.yml und docs/INDEX.md.
- docs/DOCUMENTATION_CHANGELOG.md wurde als Änderungsjournal der Dokumentation erstellt.
- docs/RETIRED_FUNCTIONALITY.md wurde als eindeutiges Register zurückgezogener Funktionen erstellt.
- FastAPI + Transformers und der alte OpenVINO-Pfad mit TranslateGemma INT8 sind als ZURÜCKGEZOGEN markiert.
- Das alte V3-Modell von BackendManager/MainWindow gilt nicht als aktive V4-Architektur.
- Der technische Dokumentationsindex sowie die Dokumentation zu Modellen/Runtime wurden aktualisiert.
- Das veraltete V3 BUG.md wurde durch eine Liste aktueller V4-Risiken und Blocker ersetzt.
- Historische Windows-Dokumente und Berichte mit alten Pfaden wurden ausdrücklich als historisch markiert.
- Es wurden keine Funktionen entfernt, keine Software installiert und keine physische Migration der vollständigen Dokumentation durchgeführt.

### Aktuelle Wartungsregel

Nach jeder Dokumentationsänderung müssen INDEX.yml aktualisiert und ein Eintrag in DOCUMENTATION_CHANGELOG.md ergänzt werden. Vor einer Statusänderung eines Dokuments sind Code, Tests und das neueste Audit zu prüfen.

## 2026-10-01 — GUI: falsche Tabs / Backends

Es wurde ein falsches Tab-Layout und ein fehlendes modernes Backend bei gleichzeitigem Vorhandensein zweier älterer Backends gemeldet. Das funktionierende V3.2-GUI dient als UX-Referenz; die V4-Backends bleiben llama.cpp, Apertium und Cloud. Zuerst muss ermittelt werden, welcher GUI-Code tatsächlich ausgeführt wird.

## Update 2026-10-01 — Korrektur der GUI/Cloud-Matrix

- SimplyTranslate wurde aus dem aktiven V4 entfernt, nachdem entschieden wurde, die Integration wegen fehlender effektiver Verbindung zurückzuziehen.
- DLX bleibt ein erforderlicher Cloud-Provider.
- Ein benutzerdefinierter Endpoint bleibt eine Anforderung der Funktionsparität: Der Zielselektor soll eine Kategorie **Custom** besitzen und nach der Auswahl eine editierbare Adresskonfiguration anbieten.
- TranslateGemma ist als spezielle Funktion/Vorlage für Sprachcodes zu behandeln, nicht als automatischer llama.cpp-Start.

## 2026-10-01 — Start der MainWindow-Kernrefaktorierung

Die Auslagerung von Verantwortlichkeiten aus der Qt-Schicht in die Anwendungsschicht wurde begonnen.

- BackendService wurde als Fassade über den aktiven V4-Backends hinzugefügt;
- TranslationApp wurde als anwendungsorientierter Kern ohne Qt-Abhängigkeit hinzugefügt;
- die llama.cpp-Runtime wurde aus der direkten MainWindow-Verwaltung in TranslationApp verschoben;
- qt_gui/app.py ist jetzt der Composition Root und übergibt den Kern an MainWindow;
- MainWindow importiert BackendRegistry, BackendSelection und LlamaCppRuntimeManager nicht mehr direkt;
- vollständiges pytest: **199 passed**;
- Ruff: **PASS**;
- compileall: **PASS**.

Die weitere Auslagerung von Einstellungen, Dokumenten, Diagnostik, Fortschritt und verbleibender GUI-Logik ist noch erforderlich. BUG-007 bleibt bis zum Abschluss dieser Refaktorierung offen.

## P0 — V4-Launcher — für Quellausführung geschlossen

Am 2026-10-01 wurde der V3/V4-Runtime-Konflikt beim Start aus `/home/frs/Projekty/tlumacz-v4` behoben.

- lokaler Symlink `tlumacz -> src/tlumacz` wurde hinzugefügt, sodass `python -m tlumacz...` aus dem Projektverzeichnis V4 ohne `PYTHONPATH=src` auflöst;
- globales V3-Paket `0.31.2` wurde weder geändert noch entfernt;
- Bootstrap-Regression ohne `PYTHONPATH` wurde hinzugefügt;
- `python -m tlumacz --version` liefert `0.40.0`;
- Import `tlumacz.qt_gui.app` zeigt auf V4;
- vollständige Suite mit `QT_QPA_PLATFORM=offscreen`: **201 passed**;
- Ruff: **PASS**;
- compileall: **PASS**.

Wheel-Builds besitzen weiterhin einen unabhängigen Blocker durch die Eigentümerschaft des übergeordneten Git-Baums (`/home/frs/Projekty`); dieser wurde nicht durch eine Änderung von globalem `safe.directory` behoben.

## 2026-10-01 — P1 — GUI-Dekomposition und Konfigurationspersistenz — Fortschritt

Im nächsten Refaktorierungsschritt wurden Verantwortlichkeiten aus `MainWindow` ausgelagert:
- `BackendPresenter` — Backendauswahl, Sichtbarkeitskonfiguration und Aufbau der Auswahl;
- `SettingsPresenter` — GUI-Einstellungs-Mapping und Konfigurationspersistenz;
- `DocumentPresenter` — Auswahl und Validierung von Dokumentpfaden;
- `ProgressPresenter` — Abbildung des Fortschrittszustands auf Qt;
- `TranslationWorker` — Ausführung der Dokumentübersetzung in einem `QObject`-Worker.

`MainWindow` wurde von 819 auf **579 Zeilen** reduziert.

Die Persistenz von `last_input_path` und `last_output_path` wurde hinzugefügt; `server_gguf_path` behält das Round-Trip-Verhalten. GUI-Tests decken die Persistenz dieser drei Pfade ab.

Verifikation: **205 passed**, Ruff PASS, compileall PASS.

Weitere Dekomposition der GUI-Tab-Builder und Integration der Diagnostik bleiben offen.

## 2026-10-01 — P1 — GUI-View-Builder

- Aufbau von vier Tabs aus `MainWindow` nach `qt_gui/view_builders.py` ausgelagert;
- `MainWindow` von 579 auf **253 Zeilen** reduziert;
- bestehende Control- und Qt-Callback-Oberfläche erhalten;
- GUI-Paritätstest auf `main_window.py` und `view_builders.py` als neue Grenze angepasst, ohne die erforderliche Control-Liste zu ändern;
- Vertragstest für View-Builder hinzugefügt;
- vollständige Regression: **206 passed**;
- Ruff: **PASS**;
- compileall: **PASS**;
- Backup vor der Änderung: `/home/frs/Projekty/agent-translator-v3/backups/tlumacz-v4-tab-builders-20261001/pre-tab-builders.tar.gz`.

Der historische Controller-Plan wurde mit dem Cleanup vom 04.10.2026 abgeschlossen: `DiagnosticsController` und die übrigen ungenutzten GUI-Controller wurden nach Zero-Reference-Prüfung entfernt. Offen bleiben nur der dokumentierte Paritätsaudit und das TranslateGemma-E2E.
