# Rekonstrukcja i walidacja

## 1. Rekonstrukcja

Writer konkretnego filtra odpowiada za zapis dokumentu wynikowego. Warstwa aplikacyjna nie powinna znać szczegółów XML, HTML, części ZIP/XML ani innej reprezentacji formatu.

## 2. Model końcowy

wyniki backendu → mapowanie unit/chunk → targety → walidacja → write()

Jednostki KEEP wracają z tekstem źródłowym 1:1.

## 3. Markery

Dla formatów ze strukturą inline walidacja musi potwierdzić, że markery nie zostały zgubione, zduplikowane ani nieprawidłowo zmienione.

## 4. Round-trip

Test E2E powinien sprawdzić: otwarcie wejścia, ekstrakcję, jednostki/markery, klasyfikację, chunkowanie, tłumaczenie, rekonstrukcję i poprawność pliku wynikowego.

## 5. PDF

PDF nie powinien być przedstawiany jako writer Okapi. Jego ścieżka ekstrakcji jest odrębna od aktywnego FilterRegistry.

## 6. Kryterium jakości

Poprawne tłumaczenie tekstu bez zachowania struktury dokumentu nie jest poprawnym E2E dla filtra strukturalnego.
