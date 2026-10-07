---
id: development-v4-en
status: active
meta:
  contentType: Guide
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: project-documentation
source: src/tlumacz/qml_gui/, pyproject.toml
depends_on: [docs/ARCHITECTURE.md, docs/STATUS.md]
expires_when: change to source bootstrap or developer workflow
last_validation: "code and documentation inspection by SentinelX 2026-10-04"
---

# Development V4

## Testing

Behavior changes are implemented using the RED → GREEN → REFACTOR cycle.

Basic test:

    python -m pytest -q

Quality gates:

    ruff check .
    mypy src
    python -m pytest -q

Installing dependencies is not part of bootstrap. The dependency environment will be prepared in the appropriate migration stage.

## Running V4 from source

The repository uses a `src/` layout. From the project directory, V4 can be run without manually setting `PYTHONPATH`:

```bash
cd /home/frs/Projekty/tlumacz-v4
python -m tlumacz.qml_gui.app
```

The repository entry `tlumacz -> src/tlumacz` is a local shim for this mode. It does not replace a distribution installation and is not part of the wheel.
