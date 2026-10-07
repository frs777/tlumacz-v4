---
id: server-management-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: runtime-maintenance
source: src/tlumacz/qml_gui/, src/tlumacz/backends/llama_cpp/
depends_on: [docs/ARCHITECTURE.md, docs/RETIRED_FUNCTIONALITY.md]
expires_when: Änderung des llama.cpp-Lifecycle
last_validation: "inspekcja dokumentacji SentinelX 2026-10-04"
---

## 2026-10-05 — aktueller llama.cpp-Lebenszyklus

`TranslationApp` verwaltet einen optionalen `LlamaCppRuntimeManager` mit Start, Stop und Neustart. Der Neustart übernimmt Modellpfad, Port, Berechnungsmodus, Parallelität und Chat-Vorlage. Cloud und Apertium verwenden diesen Lebenszyklus nicht.

# Runtime-Verwaltung — Tlumacz V4

## Umfang

Die aktuelle lokale Runtime betrifft **llama.cpp / llama-server**. Cloud benötigt keinen lokalen Prozess. Apertium besitzt eine eigene Runtime und einen eigenen Lifecycle, der in der Apertium-Dokumentation beschrieben wird.

## Aktive Architektur

```text
Qt GUI / application
    ↓
LlamaCpp backend
    ↓
runtime manager
    ↓
llama-server
```

Implementierungsdetails sind in `src/tlumacz/backends/llama_cpp/` und im aktuellen GUI-Code zu lesen.

## Zurückgezogene Runtimes

FastAPI/Transformers und der alte OpenVINO-Pfad mit TranslateGemma INT8 werden von V4 nicht gestartet. Ihre Einträge dürfen nicht wieder in den aktiven Backend-Selektor aufgenommen oder als erforderliche Runtime-Komponenten dokumentiert werden.

## Diagnoseregel

Wenn das Programmverhalten auf FastAPI, OpenVINO oder andere V3-Elemente hinweist, zuerst Interpreter, `tlumacz.__file__`, Runtime-Umgebung und Launcher prüfen. Das Audit vom 2026-10-01 identifizierte die globale Tlumacz-0.31.2-Installation als Quelle solcher Abweichungen.

## Verifikation

Runtime-Tests müssen in einer Umgebung ausgeführt werden, die aus dem aktuellen V4-Wheel/Checkout aufgebaut wurde. Das Ergebnis muss Datum und exakten Befehl enthalten.
