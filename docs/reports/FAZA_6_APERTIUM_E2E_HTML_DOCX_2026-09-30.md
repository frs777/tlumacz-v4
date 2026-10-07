# Faza 6 — Apertium: E2E HTML/DOCX

Data: 2026-09-30

E2E obejmuje rzeczywisty pipeline V4:
DocumentProcessor → Filter → ApertiumBackend → output.

DOCX:
- wynik DOCX jest poprawnym archiwum;
- tekst został przetłumaczony przez backend;
- zasób binarny został zachowany.

HTML:
- tekst został przetłumaczony przez backend;
- DOCTYPE i markup zostały zachowane;
- skrypty/style nie są jednostkami tłumaczeniowymi.

Weryfikacja: 2 testy E2E; Ruff PASS; mypy PASS; pełny pytest 122 passed.