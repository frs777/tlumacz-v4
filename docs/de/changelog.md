# CHANGELOG V4

## 2026-10-01 — P1 — MainWindow-Dekomposition und Persistenz von Pfaden

- `BackendPresenter`, `SettingsPresenter`, `DocumentPresenter`, `ProgressPresenter` und `TranslationWorker` ausgelagert;
- `MainWindow` von 819 auf 579 Zeilen reduziert;
- `TranslationApp` besitzt nun Controller für Backend, Einstellungen, Dokument, Fortschritt und Diagnostik;
- `last_input_path` und `last_output_path` zu `AppSettings` hinzugefügt;
- Round-Trip-Persistenz von Eingabe-, Ausgabe- und GGUF-Pfaden bestätigt;
- vollständige Suite: 205 passed; Ruff und compileall: PASS.

## 2026-10-01 — P0 V4-Launcher

- Mehrdeutigkeit beim Start von V4 aus dem Source-Baum durch den Repository-Shim `tlumacz -> src/tlumacz` beseitigt;
- `python -m tlumacz --version` aus dem Projektverzeichnis löst V4 `0.40.0` ohne `PYTHONPATH` auf;
- V3/V4-Bootstrap-Regressionstests hinzugefügt;
- vollständige Suite bestätigt: 201 passed, Ruff PASS, compileall PASS;
- das globale V3-Paket `0.31.2` wurde nicht verändert.

## 2026-10-01 — Abschlussbericht der Migration V3 → V4

- `docs/Raport_koncowy_migracji_v3-v4.md` hinzugefügt;
- Phasen 0–13, Erfolge, Probleme und behobene Blocker zusammengefasst;
- verbleibende Blocker für das finale Release dokumentiert: Apertium `eng-pol`, Windows-Runtime, Dependency Closure und Lizenzprüfung;
- lokalen Handoff-Freeze und Linux Release Candidate 0.40.0 bestätigt;
- V3 bleibt als Referenzquelle unverändert und es wurde nichts auf GitHub veröffentlicht.

## 2026-09-30 — Phase 13 — finaler Handoff und Freeze

- lokalen Handoff-Freeze für Release Candidate 0.40.0 abgeschlossen;
- Artefakt, SHA-256, F11/F12-Blocker und weiteres Vorgehen dokumentiert;
- Dokumentationsbackup vor Änderungen erstellt;
- kein GitHub-Push und keine Artefaktveröffentlichung;
- finales Release 0.40.0 bleibt wegen Apertium `eng-pol`, Windows sowie Lizenz-/Dependency-Arbeiten offen.

## 2026-09-30 — Phase 12 — Release 0.40.0 — Release Candidate

- Linux Release Candidate für 0.40.0 vorbereitet;
- vollständige Suite: 182 passed;
- compileall, Ruff und mypy: PASS;
- Integration/E2E: 19 passed;
- Clean-Installation des Wheels ohne Abhängigkeiten: PASS;
- `RELEASE_NOTES_0.40.0.md`, `MIGRATION_NOTES_V3_TO_V4.md` und `ROLLBACK_0.40.0.md` hinzugefügt;
- SHA-256 des Artefakts: `161d5667442b7dc9f1d90f85ed1e371ca57ca79530d690dfdd5d5e6914000835`;
- Phase 12 bleibt wegen Windows und Packaging-Blockern aus Phase 11 offen;
- das separate Glossar ist kein Blocker und kein Bestandteil des gebündelten Artefakts.

## 2026-09-30 — Phase 11 — Packaging fortgesetzt

- Staging nach `./temp` verschoben, ohne außerhalb des V4-Baums zu schreiben;
- Okapi-Ressourcen und Java Filter Host zum Python-Paket hinzugefügt;
- gebündelte Apertium-Runtime zum Wheel hinzugefügt und Engine 3.9.12 verifiziert;
- `LICENSE`, `NOTICE` und Lizenztexte zur Distribution hinzugefügt;
- Wheel `tlumacz-0.40.0-py3-none-any.whl` in einer sauberen venv gebaut und verifiziert;
- Java Filter Host aus dem Wheel bestand den Smoke-Test;
- vollständige Suite: 182 passed, Ruff PASS, mypy PASS;
- Phase 11 bleibt offen: unvollständiges `eng-pol.t1x.bin`, fehlende Windows-Runtime und unvollständige Dependency-/Lizenzprüfung.

## 2026-09-30 — Phase 11 — Packaging gestartet

- Dependency Closure für das V4-Artefakt begonnen;
- Backup vor Änderungen: `.migration-backups/pre-packaging-phase11-20260930.tar.gz`;
- kontrollierte Okapi-Runtime aus V3 (`filtry/runtime`, 42 Dateien, 22 MiB) hinzugefügt;
- Wheel-Bau durch `setuptools`/Git und Eigentümerschaft des übergeordneten Repositorys blockiert;
- zusätzlicher Blocker beim Bau der Apertium-Daten in `/tmp` wegen Berechtigungen erkannt;
- Phase 11 bleibt offen und blockiert; das Abschlusskriterium wurde nicht als erfüllt markiert.

## 2026-09-30 — Phase 10

- Phase 10 — Legacy-Entfernung nach dem Zero-Reference-Audit abgeschlossen;
- kein FastAPI/OpenVINO in aktivem V4-Code, Tests oder Konfiguration bestätigt;
- Inkonsistenzen in der Dokumentation der Phasen 9–10 beseitigt;
- STATUS und TODO aktualisiert;
- Verifikation: 180 Tests, Ruff und mypy — PASS.

# Frühere V4-Meilensteine

## Phase 4 — LlamaCppBackend

- llama.cpp OpenAI-kompatiblen Adapter hinzugefügt;
- Health-Check-Endpunkt `/v1/models` hinzugefügt;
- vollständige V4-Suite: 61 passed;
- Runtime Manager und Prozessbesitzvalidierung hinzugefügt;
- explizite Startup-/Shutdown-Timeouts und Readiness Probe hinzugefügt;
- Health-Check, Contract Suite und E2E abgeschlossen;
- echter llama-server mit Jan-v3.5-4B-Q4_K_XL bestand die Smoke-Übersetzung;
- vollständige V4-Suite: 77 passed;
- Cancellation über V4 CancellationToken abgeschlossen.

## Phase 5 — Cloud

- CloudRouter und CloudRoute hinzugefügt;
- runtime-prüfbaren CloudProvider hinzugefügt;
- Migration von Cloud-Profilen V3 → V4 ohne Übernahme von API-Keys hinzugefügt;
- MozhiProvider und automatische Instanzauswahl hinzugefügt;
- HTTP-Request-Timeouts hinzugefügt und durchgesetzt;
- Fehlerklassifikation, Secret-Isolation und Contract Tests abgeschlossen.

## Phase 6 — Apertium

- private Apertium-3.9.12-Runtime und Discovery ohne Systeminstallation hinzugefügt;
- Apertium-Adapter gemäß TranslationBackend-Vertrag abgeschlossen.

## Phase 3 — Filter Engine

- isolierten Java Filter Host hinzugefügt;
- versionierten JSON-Lines-Client hinzugefügt;
- DOCX/OpenXML-Filter hinzugefügt;
- DOCX-Round-Trip über die Filter Engine hinzugefügt;
- alle Punkte von Phase 3 abgeschlossen;
- vollständige V4-Suite: 58 passed.

## 2026-10-01 — Engineering-Audit und Qualitätsreparatur

- Dokumentationsaudit `docs/Audyt/AUDYT_DOKUMENTACJI_2026-10-01.md` hinzugefügt;
- Codeaudit `docs/Audyt/AUDYT_KODU_2026-10-01.md` hinzugefügt;
- Reparaturplan `docs/Plany/PLAN_NAPRAWCZY_AUDYT_2026-10-01.md` hinzugefügt;
- aktueller Verifikationsbericht `docs/Testy/AUDYT_TESTY_2026-10-01.md` hinzugefügt;
- Backup `.migration-backups/pre-audit-repair-20261001.tar.gz` erstellt;
- Ruff-Probleme behoben;
- regenerierbare Artefakte aus Ruff ausgeschlossen;
- aktive V4-Pfade vereinheitlicht;
- CLI in frischer Wheel-Umgebung verifiziert;
- Apertium-`eng-pol`-Blocker durch `cas_sp` bestätigt.

## 2026-10-01 — Reparatur der GUI/Cloud-Regression V3 → V4

- festgestellt, dass V4 trotz GUI-Controllern keine tatsächliche Qt-Schicht besaß;
- Verlust der meisten V3-Cloud-Provider festgestellt;
- unvollständige Konfiguration von 12 Cloud-Profilen festgestellt;
- Backup `.migration-backups/pre-gui-cloud-repair-20261001.tar.gz` erstellt;
- Qt-GUI als V4-Adapter wiederhergestellt;
- aktive GUI-Backends llama.cpp, Apertium und Cloud wiederhergestellt;
- Cloud-Provider OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate, SimplyTranslate, Mozhi und DLX wiederhergestellt;
- 12 Cloud-Profile wiederhergestellt;
- Mozhi-/SimplyTranslate-Felder wiederhergestellt;
- FastAPI/OpenVINO blieben zurückgezogen;
- GUI-Regression und Cloud-Kompatibilitätstests hinzugefügt;
- vollständige Suite: 195 passed;
- Ruff: PASS;
- mypy: PASS;
- Wheel 0.40.0 erfolgreich gebaut.

Regressionsbericht: `docs/Audyt/AUDYT_REGRESJI_GUI_CLOUD_V3_V4_2026-10-01.md`.
Reparaturbericht: `docs/Audyt/RAPORT_NAPRAWY_GUI_CLOUD_2026-10-01.md`.

## 2026-10-01 — Abschluss der UI-Oberfläche

- vollständige V3/V4-objectName-Menge verglichen;
- aktive Elemente der Tabs Extras/Hilfe wiederhergestellt;
- Glossar, Skill-Verwaltung, Sprache der Hilfe, Über-Dialog und Output-Splitter hinzugefügt;
- `tests/test_gui_surface_parity.py` hinzugefügt;
- finale Suite dieser Stufe: **196 passed**;
- Ruff, mypy, compileall und Wheel: PASS.

## 2026-10-01 — Meldung zum llama.cpp-Server

- **Status:** gemeldet, Ursache unbekannt.
- **Komponente:** llama.cpp-Server/Runtime.
- **Symptom:** Der llama.cpp-Server startet nicht.
- **Klassifikation:** funktionaler Fehler zur Reproduktion und Diagnose.
- **Priorität:** P1 — blockiert das lokale llama.cpp-Backend.
- **Ursache:** noch unbekannt; es wird kein Fehler bei Konfiguration, Modell, Prozessparametern oder Umgebung angenommen.
- **Nächster Schritt:** exakte Startmeldung bzw. Log erfassen und tatsächliches Executable, Modell und Konfiguration bestimmen.

## 2026-10-01 — Korrektur der GUI/Cloud-Matrix

- SimplyTranslate aus V4 zurückgezogen, da keine wirksame Verbindung hergestellt werden konnte;
- DLX bleibt erforderlicher Cloud-Provider;
- Kategorie **Custom** mit editierbarer Adresse für externe API-Endpunkte bleibt eine Anforderung der Funktionsparität;
- TranslateGemma ist eine spezielle Sprachcode-Funktion/Vorlage und kein automatischer llama.cpp-Start.

## 2026-10-01 — Auslagerung des GUI-Anwendungskerns

- BackendService als Fassade über aktive Backends hinzugefügt;
- TranslationApp als Anwendungskern ohne Qt-Abhängigkeit hinzugefügt;
- llama.cpp-Runtime-Verwaltung von MainWindow nach TranslationApp verschoben;
- qt_gui/app.py zum Composition Root gemacht;
- MainWindow importiert Backend-Registry/-Auswahl und LlamaCppRuntimeManager nicht mehr direkt;
- vollständige Suite: **199 passed**;
- Ruff: PASS;
- compileall: PASS.

## 2026-10-01 — P1 — GUI-View-Builder

- vier Tab-Builder nach `src/tlumacz/qt_gui/view_builders.py` ausgelagert;
- MainWindow von 579 auf 253 Zeilen reduziert, ohne den GUI-Oberflächenvertrag zu ändern;
- Paritätstest an die neue Modulgrenze angepasst;
- `test_gui_view_builders.py` hinzugefügt;
- vollständige Suite: **206 passed**; Ruff und compileall: PASS;
- Backup: `/home/frs/Projekty/agent-translator-v3/backups/tlumacz-v4-tab-builders-20261001/pre-tab-builders.tar.gz`.


## 2026-10-03 — Lokalisierung der QML-Oberfläche und Hilfe

- Lokalisierung der aktiven QML-Oberfläche in PL/EN/DE abgeschlossen;
- Dateidialoge, Backend-Bezeichnungen, Glossar, Einstellungen und Laufzeitmeldungen lokalisiert;
- Benutzerhilfe PL/EN/DE synchronisiert;
- docs/I18N_STATUS.md als Übersetzungsstatusregister hinzugefügt;
- vollständige Regression: 272 passed, compileall PASS, QML-Offscreen-Smoke mit kontrolliertem Code 124 beendet.
