# Filter Engine i Okapi

## 1. Odpowiedzialność Filter Engine

Filter Engine jest warstwą, która izoluje format dokumentu od orkiestracji tłumaczenia.

Kontrakt filtra obejmuje co najmniej:

- otwarcie sesji;
- ekstrakcję jednostek;
- zapis wyników;
- obsługę danych potrzebnych do rekonstrukcji.

`DocumentProcessor` korzysta z kontraktu filtra zamiast implementować parser każdego formatu.

## 2. Okapi jako warstwa strukturalna

Filtr Okapi reprezentuje dokument przez jednostki, a tekst wymagający tłumaczenia jest oddzielany od elementów strukturalnych.

Inline codes nie powinny być traktowane jako zwykły tekst do przetłumaczenia.

## 3. TPlugin

Pakiety filtrów Okapi są dostarczane jako TPlugin. Warstwa `filter_store`/loader odpowiada za odnalezienie i załadowanie pakietu filtra.

Nie należy mieszać:

- formatu pakietu TPlugin,
- kontraktu Filter Engine,
- logiki orkiestracji tłumaczenia,
- backendu MT.

Są to odrębne odpowiedzialności.

## 4. Jednostka dokumentowa

Dla filtrów strukturalnych logiczny przepływ można opisać jako:

`element dokumentu → jednostka filtra → tekst/inline codes → klasyfikacja → chunk → backend → target → writer`.

To jest model semantyczny; konkretna implementacja jednostki zależy od filtra.

## 5. Rejestracja lazy

Registry wykorzystuje rejestrację lazy. Dzięki temu instancja filtra jest tworzona dopiero wtedy, gdy jest potrzebna.

Dodanie filtra powinno zatem obejmować:

1. implementację kontraktu;
2. rejestrację rozszerzeń;
3. pakiet/runtime, jeżeli filtr tego wymaga;
4. test ekstrakcji;
5. test zapisu;
6. E2E round-trip.

## 6. Testowanie

Dla formatu strukturalnego test jednostkowy klasy filtra nie wystarcza. Potrzebny jest dowód:

`plik wejściowy → extract → units/markers → preprocess → chunk → translate → reconstruct → output`.
