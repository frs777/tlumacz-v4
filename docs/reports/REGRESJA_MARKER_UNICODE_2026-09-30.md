# Regresja MarkerValidator — Unicode

Data: 2026-09-30

Problem: walidator używał warunku `ord(marker) >= U+E110`, przez co zwykłe znaki Unicode, np. emoji, były traktowane jak indeksy markerów Okapi.

Naprawa: kontrola dotyczy wyłącznie zakresu Private Use Area U+E000–U+F8FF poza rozpoznaną parą markera.

Dodano test regresyjny z emoji.

Weryfikacja: 13 testów marker + EPUB PASS; pełny suite 141 passed.