# Faza 7 — HTML/XHTML

Data: 2026-09-30

HTML Filter zweryfikowany:
- probe HTML/HTM/XHTML;
- deterministyczne text slots;
- wykluczenie tagów technicznych;
- fingerprint źródła;
- round-trip przez DocumentProcessor;
- błędny input;
- cancellation;
- Unicode.

Weryfikacja: 4 testy HTML + E2E Apertium; pełny pytest 132 passed; Ruff PASS; mypy PASS.