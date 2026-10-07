# Faza 6 — Apertium: adapter

Data: 2026-09-30

Uzupełniono brakujący w V4 adapter CLI:
- implementuje wspólny TranslationBackend;
- korzysta wyłącznie z ApertiumRuntime;
- buduje jawny pair językowy;
- waliduje dostępność pary;
- respektuje limity wejścia/wyjścia/stderr;
- mapuje timeout i niedostępność runtime na błędy domeny;
- zwraca BackendResult bez zależności od GUI.

Weryfikacja:
- 3 testy adaptera — PASS;
- Ruff — PASS;
- mypy — PASS, 41 plików źródłowych;
- pełny pytest V4 — 111 passed.
