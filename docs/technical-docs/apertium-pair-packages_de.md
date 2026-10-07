## Aktuelles Modell des Paket-Speichers — TAR-only

Der Benutzerspeicher `$HOME/.config/tlumacz/apertium/` enthält ausschließlich `.tar`-Pakete und deren externe `.tar.sha256`-Dateien. Die Anwendung erstellt keine dauerhafte entpackte Kopie. Während der Initialisierung der Laufzeit werden die Archive geprüft und ihr Inhalt in einem temporären Arbeitsverzeichnis außerhalb des Speichers materialisiert; der Pfad dieses Verzeichnisses wird als `APERTIUM_DATADIR/-d` an Apertium übergeben.

# Apertium-Sprachpaarpakete

**Status:** verbindlicher Format- und Pipeline-Vertrag  
**Auditdatum:** 2026-10-06  
**Distributionsformat:** unkomprimiertes `.tar`  
**Laufzeitspeicher:** `$HOME/.config/tlumacz/apertium/`

## 1. Distributionsmodell
## 1.1. Benutzerspeicher und Verwendung durch die Anwendung

Der vorgesehene Speicher für Distributionsartefakte ist:

    $HOME/.config/tlumacz/apertium/
    ├── apertium-eng-pol-1.0.0.tar
    ├── apertium-eng-pol-1.0.0.tar.sha256
    ├── apertium-eng-pol/
    └── ...

Die `.tar`-Archive sind das eigentliche Distributionsformat. Die Anwendung führt TAR nicht direkt aus: Vor der Erkennung prüft sie den SHA-256-Hash des vollständigen Archivs und entpackt anschließend fehlende Pakete in denselben Speicher. Die entpackten Verzeichnisse sind eine interne Arbeitsdarstellung für ApertiumRuntime; sie ersetzen die `.tar`-Artefakte nicht.

Das alte Verzeichnis `$HOME/.config/tlumacz/apertium/` wird nicht verwendet; der korrekte Speicher ist `$HOME/.config/tlumacz/apertium/`.

**Ein Paket = eine Übersetzungsrichtung.**

Wenn das Apertium-Quellprojekt zwei Richtungen unterstützt, beispielsweise `eng-spa` und `spa-eng`, werden zwei unabhängige Artefakte erzeugt:

```text
apertium-eng-spa-1.0.0.tar
apertium-spa-eng-1.0.0.tar
```

Wir erstellen kein gemeinsames Paket, das mehrere Richtungen enthält.

Tar ist ein Transportcontainer und kein Kompressionsmechanismus. Die Pakete werden als gewöhnliche, unkomprimierte Tar-Archive erstellt.

## 2. Paketinhalt

Das Paket enthält ausschließlich die vom ausgewählten Modus benötigten Daten:

```text
apertium-eng-spa-1.0.0.tar
└── apertium-eng-spa/
    ├── manifest.json
    ├── checksums.json
    ├── COPYING
    ├── modes.xml
    ├── modes/
    │   └── eng-spa.mode
    ├── eng-spa.automorf.bin
    ├── eng-spa.prob
    ├── eng-spa.autobil.bin
    ├── eng-spa.t1x.bin
    ├── ...
    └── vom Mode benötigte Transfer-Quelldateien
```

Der Builder **filtert `modes.xml` auf genau einen ausgewählten Modus**. Definitionen der übrigen Richtungen werden nicht übernommen.

Nicht im Paket enthalten sind:

- `.git/`;
- `dev/`;
- `test/`;
- `eval/`;
- Kompilierungs-Cache;
- `Makefile`, `configure`, `autom4te.cache`;
- Quelldictionaries und andere Dateien, auf die der ausgewählte Modus nicht verweist;
- Daten einer anderen Richtung.

Quelldateien `.t1x`, `.t2x`, `.t3x` werden **nur dann** beibehalten, wenn der ausgewählte Modus direkt auf sie verweist. Dies ist kein zufälliges Zurücklassen von Quellen: Die Apertium-Laufzeit verwendet diese Dateien zusammen mit den entsprechenden Binärdateien.

## 3. Manifest und Prüfsumme

`manifest.json` identifiziert genau eine Richtung:

```json
{
  "format": "apertium-pair",
  "format_version": 1,
  "id": "apertium-eng-spa",
  "name": "apertium-eng-spa",
  "version": "1.0.0",
  "pair": "eng-spa",
  "source": "eng",
  "target": "spa"
}
```

`checksums.json` enthält SHA-256-Werte für alle Paketdateien außer `checksums.json` selbst.

Der Installer prüft außerdem:

- ein einziges Stammverzeichnis;
- Übereinstimmung des Verzeichnisses mit dem Manifest;
- keine absoluten Pfade und kein `..`;
- keine Symlinks und Hardlinks;
- Vollständigkeit der Prüfsummen;
- Vorhandensein von `modes.xml` und der richtigen `.mode`-Datei.

## 4. Code

Format und Installer:

```text
src/tlumacz/backends/apertium/packages.py
```

Pipeline:

```text
tools/apertium/package_pipeline.py
```

CLI:

```text
tools/apertium/package_pairs.py
```

Tests:

```text
tests/test_apertium_packages.py
tests/test_apertium_package_pipeline.py
```

## 5. Automatische Paketvorbereitung

### Aus einem lokalen Checkout

```bash
python3 tools/apertium/package_pairs.py   --source /pfad/zu/apertium-eng-spa   --output $HOME/.config/tlumacz/apertium   --version 1.0.0
```

Wenn die Quelle zwei vollständige Richtungen enthält, werden zwei Dateien erzeugt.

### Aus dem Internet herunterladen und kompilieren

```bash
python3 tools/apertium/package_pairs.py   eng-spa   --download   --compile   --output $HOME/.config/tlumacz/apertium   --version 1.0.0
```

Pipeline:

```text
GitHub
  ↓
git clone apertium-<pair>
  ↓
vorhandenes apertium-get.py
  ↓
Herunterladen der Abhängigkeiten
  ↓
autoreconf/configure/make
  ↓
Erkennung vollständiger Modi
  ↓
Auswahl jeder Richtung einzeln
  ↓
Manifest + SHA-256
  ↓
unkomprimiertes .tar
  ↓
SHA256SUMS
```

Das ursprüngliche `Apertium/apertium-get.py` wurde nicht geändert. Darüber wurde eine Orchestrierungsschicht ergänzt, damit der Upstream-Mechanismus zum Herunterladen/Kompilieren nicht mit unserem Distributionsformat vermischt wird.

### Bereinigung nach dem Packen

```bash
python3 tools/apertium/package_pairs.py   --source /pfad/zu/apertium-eng-spa   --output $HOME/.config/tlumacz/apertium   --version 1.0.0   --clean-runtime
```

Die Option entfernt aus der Quelle Materialien, die für die Laufzeit der erhaltenen vollständigen Richtungen nicht benötigt werden.

**Hinweis:** `--clean-runtime` ist für das angegebene Verzeichnis eine destruktive Operation. Vor der Verwendung auf einem Quell-Repository muss ein Backup erstellt werden. Für die Tłumacz-Distribution verwenden wir sie praktisch auf dem Laufzeitspeicher `$HOME/.config/tlumacz/apertium/`, während die Quell-Repositorys unter `Apertium/` für spätere Kompilierungen erhalten bleiben.

## 6.1. Portabilität von `modes/<pair>.mode`

Das Paket darf keine absoluten Pfade der Build-Umgebung dauerhaft speichern. Der Builder normalisiert Pfadargumente der erzeugten `.mode`-Datei auf Dateinamen innerhalb des Paketverzeichnisses. Dadurch kann ein auf einem Host erstelltes Paket auf einem anderen Host installiert werden.

Die Regression befindet sich in `tests/test_apertium_packages.py` und prüft, dass das absolute Quellverzeichnis nicht in das Artefakt gelangt.

## 6. Erkennung fertiger Richtungen

`discover_packagable_pairs()` betrachtet eine Richtung als bereit, wenn:

1. der Modus den Standardnamen `source-target` hat;
2. der Modus `install="yes"` besitzt;
3. alle `<file>`-Einträge des Modus vorhanden sind;
4. die zugehörige `modes/<pair>.mode` vorhanden ist.

Hilfsmodi wie `eng-spa-chunker` werden nicht als eigene Paare behandelt.

Für Ausnahmen, bei denen Upstream `install="yes"` nicht setzt, steht `include_unmarked=True` zur Verfügung. Wir verwenden dies nur nach manueller Prüfung. Für ein veröffentlichtes Paar wird es derzeit nicht verwendet.

## 7. Bidirektionale Paare

Wenn beide Modi vollständig sind, erstellt der Builder zwei Artefakte. Es spielt keine Rolle, ob sie aus einem Repository stammen.

Beispiel:

```text
apertium-eng-cat/
    eng-cat  -> apertium-eng-cat-1.0.0.tar
    cat-eng  -> apertium-cat-eng-1.0.0.tar
```

Dasselbe gilt für alle anderen bidirektionalen Paare.

## 8. Aktuelles Audit 2026-10-06

In den lokalen `Apertium/`-Checkouts wurden die folgenden vollständigen, bereits kompilierten Richtungen gefunden:

| Familie | Richtungen |
|---|---|
| Bengali ↔ Englisch | `bn-en`, `en-bn` |
| Englisch ↔ Katalanisch | `eng-cat`, `cat-eng` |
| Englisch ↔ Deutsch | `eng-deu`, `deu-eng` |
| Englisch ↔ Italienisch | `eng-ita`, `ita-eng` |
| Englisch ↔ Spanisch | `eng-spa`, `spa-eng` |
| Englisch ↔ Portugiesisch | `en-pt`, `pt-en` |
| Polnisch ↔ Kaschubisch | `pl-csb`, `csb-pl` |
| Polnisch ↔ Slowakisch | `pl-sk`, `sk-pl` |
| Polnisch ↔ Tschechisch | `pol-ces`, `ces-pol` |
| Polnisch ↔ Russisch | `pol-rus`, `rus-pol` |
| Polnisch ↔ Schlesisch | `pol-szl`, `szl-pol` |
| Polnisch ↔ Ukrainisch | `pol-ukr`, `ukr-pol` |
| Polnisch ↔ Spanisch | `pol-spa`, `spa-pol` |
| Englisch → Polnisch | `eng-pol` |

Insgesamt wurden **28 veröffentlichbare Richtungen** vorbereitet.

## 9. Fertige Artefakte

Das Verzeichnis:

```text
pary/
```

enthält 28 unkomprimierte Archive:

```text
apertium-bn-en-1.0.0.tar
apertium-en-bn-1.0.0.tar
apertium-cat-eng-1.0.0.tar
apertium-eng-cat-1.0.0.tar
apertium-ces-pol-1.0.0.tar
apertium-pol-ces-1.0.0.tar
apertium-csb-pl-1.0.0.tar
apertium-pl-csb-1.0.0.tar
apertium-deu-eng-1.0.0.tar
apertium-eng-deu-1.0.0.tar
apertium-eng-ita-1.0.0.tar
apertium-ita-eng-1.0.0.tar
apertium-eng-pol-1.0.0.tar
apertium-eng-spa-1.0.0.tar
apertium-spa-eng-1.0.0.tar
apertium-en-pt-1.0.0.tar
apertium-pt-en-1.0.0.tar
apertium-pl-sk-1.0.0.tar
apertium-sk-pl-1.0.0.tar
apertium-pol-rus-1.0.0.tar
apertium-rus-pol-1.0.0.tar
apertium-pol-spa-1.0.0.tar
apertium-spa-pol-1.0.0.tar
apertium-pol-szl-1.0.0.tar
apertium-szl-pol-1.0.0.tar
apertium-pol-ukr-1.0.0.tar
apertium-ukr-pol-1.0.0.tar
```

Jedes besitzt eine zugehörige `.sha256`-Datei; `SHA256SUMS` enthält die Prüfsummen des gesamten Satzes.

## 10. Noch nicht fertige Richtungen

### `pol-eng`

Das Paar wurde repariert und als `apertium-pol-eng-1.0.0.tar` veröffentlicht.

Die erste Blockade war eine Referenz auf `a_SN` in `apertium-eng-pol.pol-eng.t3x` ohne Deklaration dieses Attributs. `a_SN` mit dem Wert `PDET` wurde hinzugefügt. Eine anschließende vollständige Kompilierung zeigte das Fehlen der erzeugten Datei `pol-eng.autogen.bin`; ein direktes `lt-comp rl` erzeugte dieses Artefakt korrekt, trotz Validator-Warnungen über doppelte `pardef`-Einträge im polnischen Wörterbuch.

Die abschließende Prüfung ergab: `pol-eng.t1x.bin`, `pol-eng.t2x.bin`, `pol-eng.t3x.bin`, `pol-eng.autogen.bin` und die übrigen vom Modus benötigten Dateien sind vorhanden. Das Paket wurde in einem sauberen Speicher installiert, als `pol-eng` erkannt, und die tatsächliche Apertium-Laufzeit führte eine Testübersetzung `pl → en` aus.

### `pol-src`

Dies ist ein lokales Sprach-/Quellmodul mit morphologischen Modi und keine vollständige Übersetzungsrichtung. Daraus wird kein Paarpaket erstellt.

## 11. Bereinigung des Laufzeitspeichers

Nach der Vorbereitung der Pakete wurde der Speicher:

```text
$HOME/.config/tlumacz/apertium/
```

von Entwicklungsmaterialien bereinigt.

Unter anderem wurden entfernt:

- `.git/`;
- `dev/`;
- `test/`;
- `eval/`;
- Autotools-Cache;
- `Makefile*`;
- `configure*`;
- nicht verwendete Wörterbuchquellen;
- nicht verwendete Hilfsmodi.

Beibehalten wurden nur die von den verfügbaren Modi benötigten Artefakte, Lizenzen und `modes.xml`.

Backup vor der Operation:

```text
backups/apertium-package-pipeline-20261006-205830/Apertium-data.tar
SHA-256:
1d9e77ffe9eaa363d13f6e25ff02958818a1e54bbffb95baa39a6f8d6d898aec
```

## 12. Verifizierung aller Pakete

Alle 27 Archive wurden:

1. durch den echten `ApertiumPairPackageInstaller` entpackt;
2. anhand von Manifest und Prüfsummen verifiziert;
3. in einem sauberen temporären Speicher installiert;
4. erneut durch `discover_supported_pairs()` erkannt.

Ergebnis:

```text
ARCHIVES 27
PAIRS 27
INSTALLATION ALLER PAKETE: OK
```

Zusätzlich ist jedes Paket ein unkomprimiertes Tar.

## 13. Lizenzen

Der Builder benötigt `COPYING`, `LICENSE` oder `LICENSE.txt`.

Wir raten Lizenzen nicht. Wenn Upstream keine eindeutige Information liefert, wird das Paket für die Veröffentlichung gesperrt.

Beispielsweise bestätigen offizielle Apertium-Repositorys die Lizenzen für einige der vorbereiteten Familien; `apertium-bn-en` ist beispielsweise als GPL-2.0 gekennzeichnet und `apertium-eng-pol` ebenfalls als GPL-2.0. Diese Informationen wurden ausschließlich zur Überprüfung der Quellen verwendet; das Paket selbst muss weiterhin die entsprechende Lizenzdatei enthalten. citeturn3search0turn1search3

## 14. Hinzufügen eines neuen Paars

```bash
python3 tools/apertium/package_pairs.py   <pair>   --download   --compile   --output $HOME/.config/tlumacz/apertium   --version 1.0.0
```

Nach erfolgreicher Kompilierung findet das Werkzeug automatisch alle vollständigen Richtungen aus diesem Repository. Wenn das Paar bidirektional ist, werden zwei separate Dateien erzeugt.

Für die Veröffentlichung prüfen:

```bash
tar -tf pary/apertium-<pair>-1.0.0.tar
sha256sum pary/apertium-<pair>-1.0.0.tar
```

## 15. Designprinzip

**Apertium-Quellen dienen der Kompilierung. Das Tłumacz-Paket dient der Distribution der Laufzeit.**

Wir vermischen diese Rollen nicht:

```text
Apertium/
  vollständige Quell-Repositorys
  ↓
  Kompilierung
  ↓
  package_pipeline
  ↓
pary/
  einzelne .tar-Artefakte
  ↓
Internet
  ↓
Tłumacz
  ↓
$HOME/.config/tlumacz/apertium/
```

Dadurch können regelmäßig neuere Apertium-Repositorys abgerufen, kompiliert, beide Richtungen automatisch erkannt und nur vollständige, verifizierte Pakete veröffentlicht werden.

## 16. Build-Werkzeuge außerhalb der Laufzeit

Die Logik zur Paketvorbereitung befindet sich ausschließlich im Verzeichnis `tools/apertium/`. `package_pipeline.py` und `package_pairs.py` sind Hilfswerkzeuge für den Build-Prozess und gehören nicht zur Tłumacz-Laufzeit.

Die manuelle Vorgehensweise zur Vorbereitung eines einzelnen Pakets ist in `docs/technical-docs/apertium-paczki-reczne-tworzenie.md` beschrieben; der vollständige Vertrag befindet sich in `docs/technical-docs/paczki-jezykowe-specyfikacja.md`.
