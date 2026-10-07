# Apertium, Filter Engine i inline codes

## 1. Apertium jako osobna ścieżka

Apertium posiada własny adapter/backend, runtime oraz zarządzanie parami językowymi. Nie jest backendem zarządzanym identycznie jak llama.cpp czy Cloud.

## 2. Granica Filter Engine

Dla dokumentów obsługiwanych przez Filter Engine logiczny przepływ do Apertium jest następujący:

dokument → filtr → jednostka → tekst + inline codes → ochrona → Apertium → target → przywrócenie kodów → writer

Konkretna reprezentacja jednostki zależy od filtra.

## 3. Inline codes

Okapi reprezentuje strukturę dokumentu za pomocą kodów inline. Backend MT nie powinien otrzymywać ich jako przypadkowego tekstu. Warstwa integracyjna chroni markery i waliduje odpowiedź backendu.

## 4. PUA i markery transportowe

Integracja wykorzystuje mapowanie pomiędzy reprezentacją Okapi PUA a markerami transportowymi __OKAPI_CODE_N__. Jest to mechanizm Tłumacza na granicy backendu, a nie funkcja Apertium.

## 5. Walidacja

Utrata, duplikacja lub nieprawidłowa modyfikacja markerów jest błędem granicy Filter Engine → backend.

## 6. E2E

Minimalny dowód poprawności obejmuje rzeczywisty dokument, rzeczywistą parę Apertium i rekonstrukcję dokumentu wynikowego.
