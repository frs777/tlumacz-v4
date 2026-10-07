# Faza 6 — Apertium: runtime

Data: 2026-09-30

Przeniesiono:
- konfigurację runtime;
- discovery bundled runtime;
- diagnostykę wersji;
- discovery par językowych;
- obsługę per-user data directory;
- prywatny artefakt native runtime 68 MB.

Dodano regresję: pusty katalog użytkownika nie może zasłonić danych bundled.

Smoke:
- executable: V4 `src/tlumacz/backends/apertium/native_runtime/bin/apertium`;
- wersja: Apertium 3.9.12;
- runtime uruchamia się poprawnie.

Ograniczenie artefaktu V3:
`native_runtime/share/apertium` nie zawiera paczek językowych. W środowisku istnieje osobno źródłowe `apertium-en-pl`, ale nie jest ono częścią tego runtime'u. Integracja danych językowych pozostaje punktem language plugins.

Weryfikacja:
- 4 testy runtime — PASS;
- Ruff — PASS;
- mypy — PASS, 39 plików źródłowych;
- pełny pytest V4 — 108 passed.
