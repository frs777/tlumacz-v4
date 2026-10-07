---
id: xliff-pipeline-v4
status: active
meta:
  contentType: Reference
  category: technical
version: 0.40.0
updated: 2026-10-01
owner: document-runtime
source: src/tlumacz/documents/xliff.py
depends_on: [docs/ARCHITECTURE.md]
expires_when: change to XLIFF Filter Engine contract
last_validation: "V4 Filter Engine verification 2026-10-01"
---

# XLIFF 2.0 Filter — Tlumacz V4

XLIFF 2.0 is an internal V4 document layer, not an active input filter. The implementation is in `src/tlumacz/documents/xliff.py`.

## Flow

```text
XLIFF 2.0
  ↓
XliffFilter
  ↓
Filter Engine units
  ↓
Translation Port / backend
  ↓
target
  ↓
XLIFF write
```

The filter validates the document version, preserves unit identifiers and checks that the source has not changed before writing targets.

## Registration

The current GUI registers `XliffFilter` for the `.xlf` and `.xliff` extensions.

## Migration note

Older V3 documents described XLIFF as the central pipeline for the whole application. In V4, XLIFF is one active filter among other formats; the old architectural model must not be carried over.
