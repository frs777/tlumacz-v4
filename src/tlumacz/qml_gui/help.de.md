# Hilfe

> **Stand der Hilfe: 2026-10-05.** Diese Hilfe beschreibt die aktuellen Bereiche **Übersetzen**, **API und Server**, **Schalter** und **Hilfe**. Wenn ältere Projektdokumente vom laufenden Programm abweichen, gilt die aktuelle Oberfläche.

## Erste Schritte

Tłumacz V4 übersetzt Dokumente ohne manuelles Kopieren und Einfügen.

### Der kurze Weg

1. Öffne **Übersetzen**.
2. Wähle die **Eingabedatei**.
3. Wähle die **Ausgabedatei** oder übernimm den vorgeschlagenen Namen.
4. Wähle die **Zielsprache**.
5. Öffne **API und Server** und wähle die Übersetzungsmethode.
6. Konfiguriere bei Bedarf **Schalter**.
7. Klicke auf **Übersetzen**.
8. Beobachte **Fortschritt**, **Zeit**, **Geschwindigkeit**, **Log** und **Übersetzungsvorschau**.

Mit **Abbrechen** kannst du die laufende Übersetzung stoppen. Ein Abbruch ist kein Programmfehler.

### Unterstützte Dokumentformate

Der aktive Filterbereich enthält derzeit Filter für DOCX, ODT, HTML/XHTML, Markdown, EPUB und XLIFF.

**TXT und PDF sind derzeit nicht im Haupt-Filterbereich registriert.** Vorhandene Skill-Dateien für TXT oder PDF bedeuten nicht, dass diese Formate im Hauptprozess unterstützt werden.

### Was nach „Übersetzen“ passiert

Die Anwendung liest das Dokument, wählt übersetzbaren Inhalt aus, teilt ihn in kontrollierte Abschnitte, bereitet Übersetzungsanfragen vor, führt das gewählte Backend aus, prüft die Ergebnisse, setzt das Dokument wieder zusammen und speichert die Ausgabedatei.

## Dokument übersetzen

### Eingabe und Ausgabe

Die **Eingabedatei** ist das zu übersetzende Dokument.

Die **Ausgabedatei** ist der Speicherort des Ergebnisses. Nach der Auswahl der Eingabedatei kann die Anwendung einen Namen mit dem Code der Zielsprache vorschlagen.

Mit **Durchsuchen...** wählst du eine Datei.

### Zielsprache

Für normale Backends wählst du die Sprache über **Zielsprache**.

Bei Apertium zeigt die Registerkarte **Übersetzen** Quell- und Zielsprache in schreibgeschützten Feldern. Die aktuelle Oberfläche bietet dort keine eigene Auswahl der Quellsprache.

### Fortschritt und Abbruch

**Fortschritt** zeigt den Fertigstellungsgrad.

**Zeit** zeigt die Dauer des aktuellen Vorgangs.

**Geschwindigkeit** zeigt die aktuelle und durchschnittliche Zeichenrate pro Sekunde.

Nach einem Abbruch solltest du das **Log** prüfen.

## Übersetzungsmethode wählen

In **API und Server** wählst du aus, wie die Übersetzung ausgeführt wird.

### llama.cpp

**llama.cpp** führt die Übersetzung lokal mit einem Modell über den von der Anwendung verwalteten llama.cpp-Server aus.

Die Oberfläche kann unter anderem enthalten:

- Server-URL;
- API-Schlüssel, falls erforderlich;
- Port;
- CPU- oder GPU-Berechnung;
- parallele Aufgaben;
- GGUF-Modell;
- Chat-Vorlage;
- automatischer Serverstart;
- Cache-Löschung nach der Übersetzung;
- Neustart nach der Übersetzung.

Verfügbare Chat-Vorlagen sind **jinja**, **chatml** und **TranslateGemma**.

**TranslateGemma ist kein eigenes Backend.** Es ist ein spezieller Chat-Vorlagenmodus für llama.cpp.

**Server neu starten** betrifft den von der Anwendung verwalteten llama.cpp-Server. Die aktuelle Runtime-Konfiguration bleibt erhalten.

### Cloud

**Cloud** verwendet einen externen Dienst über das Netzwerk.

Die aktuelle Oberfläche kann unter anderem Profile für ChatGPT, Codex, Gemini Flash, Gemini Flash Lite, DeepSeek, Cohere, DeepL API Free, MyMemory, Microsoft Translator, DLX und Mozhi anzeigen.

Nicht jedes Profil benötigt einen API-Schlüssel. Verwende niemals den Schlüssel eines anderen Dienstes.

Text, der über Cloud gesendet wird, verlässt den Computer und wird vom gewählten Dienst verarbeitet.

### Mozhi

Mozhi ist ein eigener Pfad innerhalb von Cloud.

Du kannst eine bestimmte Instanz oder die automatische Auswahl verwenden. Außerdem kannst du eine verfügbare Übersetzungs-Engine wählen.

### Apertium

**Apertium** ist ein lokales regelbasiertes Übersetzungssystem. Es ist kein LLM.

Die Oberfläche zeigt Quell- und Zielsprache sowie Informationen zur lokalen Apertium-Konfiguration.

Eine deklarierte Sprachpaarung beweist nicht, dass die vollständige Laufzeit für diese Paarung bereit ist. Bei Problemen solltest du das **Log** prüfen.

Apertium verwendet nicht den Lebenszyklus des llama.cpp-Servers.

### Eigener Server

**Eigener Server** bedeutet einen außerhalb der Anwendung gestarteten Server.

Tłumacz kann einen kompatiblen Server verwenden, verwaltet aber dessen Prozess und Modell nicht.

## Einstellungen und Werkzeuge

Die Registerkarte **Schalter** enthält Glossar, Skills und LLM-Einstellungen. Backend-spezifische Verhaltenseinstellungen befinden sich beim jeweiligen Backend unter **API und Server**.

### Glossar

Ein Glossar speichert Quell- und Zielbegriffe.

1. Wähle die Glossardatei mit **Durchsuchen...**.
2. Gib den Quellbegriff ein.
3. Gib die Zielübersetzung ein.
4. Klicke auf **Hinzufügen**.

Die Oberfläche zeigt auch die Anzahl der gespeicherten Begriffspaare.

### Skills

Skills liefern zusätzliche Übersetzungsanweisungen.

Die Anwendung unterscheidet **System-Skills** und **Benutzer-Skills**.

Du kannst Skills aktivieren oder deaktivieren. Verfügbare Aktionen sind **Skill importieren**, **Neuer Skill**, **Aktualisieren** und das Löschen eines Benutzer-Skills.

**Neuer Skill** öffnet eine Vorlage, die du bearbeiten und speichern kannst.

Die Anwendung kann anhand der Dateiendung automatisch einen passenden Grund-Skill auswählen.

### LLM-Einstellungen

Dieser Bereich ist für modellbasierte Übersetzungspfade verfügbar und bei Apertium ausgeblendet.

**Blockgröße** bestimmt die maximale Größe des an die Übersetzung übergebenen Textabschnitts.

**Temperatur** beeinflusst die Freiheit der Modellantwort. Niedrigere Werte liefern stärker wiederholbare Ergebnisse.

**Eigene Modellanweisungen** fügen eigene Regeln zur Übersetzungsaufgabe hinzu.

**Überspringmuster** bestimmen Textmuster, die nicht übersetzt werden sollen.

### Einstellungen speichern

Mit **Einstellungen speichern** speicherst du die aktuellen Werte.

Mit **Standardwerte wiederherstellen** stellst du die Standardwerte wieder her.

Die Auswahl des Backends unter **API und Server** wird über den aktiven QML-Pfad gespeichert. Ein Neustart der Anwendung ist dafür nicht erforderlich.

## Ergebnisse und Probleme

### Log

**Log** enthält Meldungen über den aktuellen Vorgang.

Wenn eine Übersetzung fehlschlägt, beginne mit dem Log. Prüfe Backend, Fehlermeldung und den Schritt, an dem die Verarbeitung gestoppt hat.

### Übersetzungsvorschau

**Übersetzungsvorschau** zeigt das verfügbare Ergebnis nach der Übersetzung.

Die Vorschau muss nicht exakt so aussehen wie das Dokument in einem externen Editor. Das gilt besonders für Formate mit komplexem Layout.

### Übersetzung startet nicht

Prüfe:

1. ob die Eingabedatei existiert;
2. ob der Ausgabeort beschreibbar ist;
3. ob das richtige Backend ausgewählt ist;
4. ob die erforderlichen Backend-Einstellungen vorhanden sind;
5. ob das Log eine konkrete Fehlermeldung enthält.

### llama.cpp funktioniert nicht

Prüfe GGUF-Datei, Adresse, Port, Berechnungsmodus und Chat-Vorlage.

Wenn die Anwendung den Server verwaltet, verwende **Server neu starten**.

### Cloud funktioniert nicht

Prüfe Profil, Dienstadresse, API-Schlüssel, falls erforderlich, Netzwerkzugang und Log.

### Apertium funktioniert nicht

Prüfe Backend, angezeigte Sprachen, verfügbare Apertium-Daten und Log.

Gehe nicht davon aus, dass der Name eines Sprachpaares in der Konfiguration eine einsatzbereite Laufzeit garantiert.

### Das Ergebnis ist falsch

Starte nicht sofort einen weiteren Versuch.

Prüfe zuerst Log, Backend-Einstellungen, Glossar, aktive Skills und eigene Modellanweisungen.

Wenn die Dokumentstruktur betroffen ist, teste ein anderes unterstütztes Format.

### Technische Details

Die Hilfe in der Anwendung beantwortet **„Wie benutze ich das Programm?“**.

Die technische Dokumentation beschreibt die Implementierung und den Projektstatus.

Version **0.40.0** ist derzeit ein lokaler Release Candidate. Offen sind unter anderem Apertium, Windows, Abhängigkeiten/Lizenzen und der vollständige End-to-End-Test von TranslateGemma.
