## 2026-10-05 — aktueller Cloud- und SecretStore-Stand

Cloud ist aktiv. Die Standard-Providerregistrierung enthält OpenAI-kompatibel, DeepL, Microsoft, MyMemory, LibreTranslate, Mozhi und DLX. Die QML-Bridge verwendet `SecretStore` und migriert alte `api_key`-Werte aus normalen JSON-Einstellungen.

---
id: cloud-translation-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-01
owner: cloud-runtime
source: src/tlumacz/backends/cloud/
depends_on: [docs/ARCHITECTURE.md, docs/STATUS.md]
expires_when: Änderung des CloudRouter-/Provider-Vertrags
last_validation: "GUI/Cloud-Audit V3 → V4 2026-10-01"
---

# Cloud-Übersetzung — Tlumacz V4

Cloud ist ein aktives V4-Backend. Die Orchestrierung erfolgt über CloudRouter und die Provider-Registry; die Dokumentation basiert nicht auf dem historischen V3-`BackendManager`.

## Aktive Adapter

Der aktuelle Code enthält Adapter für:

- OpenAI-kompatibel
- DeepL
- Microsoft Translator
- MyMemory
- LibreTranslate
- DLX
- Mozhi als separater Adapter/Provider

Die konkreten Klassen und Verträge befinden sich in `src/tlumacz/backends/cloud/`.

## Konfiguration

Die Konfiguration der Cloud-Profile ist Teil des V4-Mechanismus. Geheimnisse dürfen weder in der Dokumentation noch im Repository gespeichert werden.

## Zurückgezogene Pfade

FastAPI/Transformers und OpenVINO gehören weder zu Cloud noch zur aktiven V4-Architektur. Ältere Dokumente über `BackendManager` oder historische V3-Server sind Migrationsmaterial.

## Verifikation

Provider besitzen Vertrags-/Kompatibilitätstests. Bei Änderungen an einem Adapter müssen der zugehörige Test und die Dokumentation aktualisiert werden.

## Aktualisierung 2026-10-01

SimplyTranslate wurde aus der aktiven V4-Matrix zurückgezogen. Eine Verbindung konnte nicht erfolgreich hergestellt werden; Provider, Cloud-Profil, Engine-Einstellung und Vertragstest wurden entfernt. Historische SimplyTranslate-Beschreibungen bleiben Archivmaterial und beschreiben nicht die aktive V4-Konfiguration.
