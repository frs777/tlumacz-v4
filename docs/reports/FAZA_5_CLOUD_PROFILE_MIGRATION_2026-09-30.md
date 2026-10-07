# Faza 5 — Cloud: profile migration

Data: 2026-09-30

Dodano `migrate_cloud_profiles()`.

Reguły:
- istniejące V4 `cloud_profiles` ma pierwszeństwo;
- z V3 `model_profiles["cloud:<aktywny model>"]` migrowany jest tylko aktywny profil;
- `api_key` nie trafia do zmigrowanego profilu;
- brak aktywnego profilu nie powoduje zgadywania providera ani kopiowania innych sekretów.

Weryfikacja:
- 4 testy migracji — PASS;
- Ruff — PASS;
- mypy — PASS, 29 plików źródłowych;
- pełny pytest V4 — 90 passed.
