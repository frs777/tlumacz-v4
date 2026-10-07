# Faza 5 — Cloud: izolacja sekretów

Data: 2026-09-30

Dodano SecretStore zgodny z V3:
- sekrety są poza profilem/config;
- klucz usługi jest identyfikowany przez SERVICE/<id>;
- plik jest tworzony z prawami 0600;
- pusty sekret usuwa wpis.

Migracja profili usuwa api_key przed zapisaniem profilu V4.

Weryfikacja:
- 3 testy SecretStore — PASS;
- pełny suite po zmianie — 102 passed.
