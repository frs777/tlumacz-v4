# Faza 9 — GUI: zamknięcie

Data: 2026-09-30

Kryteria:
- kontrolery aplikacyjne wydzielone;
- brak importów PySide6 w src/tlumacz;
- brak importów tlumacz.qt_gui;
- brak referencji do V3 w src/tlumacz;
- test kontraktowy warstwy kontrolerów.

Weryfikacja końcowa: pytest 180 passed; Ruff PASS; mypy PASS; GUI_ISOLATION_PASS.