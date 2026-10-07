# Faza 8 — ChunkPlanner

Data: 2026-09-30

Wydzielono deterministyczne planowanie chunków z V3 `core.py`.

Zakres:
- budżet znaków;
- separator overhead;
- zachowanie kolejności;
- oversized unit jako pojedynczy chunk;
- normalizacja tuple/object.

Weryfikacja: 5 testów; pełny pytest 149 passed.