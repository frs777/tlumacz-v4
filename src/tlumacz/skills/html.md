---
name: HTML
formats: html, htm
---
Tłumaczysz dokument HTML. Przestrzegaj tych zasad ŚCIŚLE:
- Zachowaj WSZYSTKIE tagi HTML i ich atrybuty dokładnie tak jak są.
- Tłumacz TYLKO widoczną treść tekstową między tagami.
- NIE tłumacz: wartości CSS, liczb, wymiarów (cm, px, pt, %), kolorów (#fff), URL-i.
- NIE tłumacz zawartości w blokach <script>, <style>, <code>, <pre>.
- NIE dodawaj formatowania Markdown (bez ```, bez #, bez **).
- NIE zmieniaj interpunkcji w CSS (zachowaj kropki w liczbach: 21cm nie 21 cm).
- Zachowaj id, class, href (linki), src, data-*, lang, charset i wszystkie wartości atrybutów bez zmian.
- Zachowaj strukturę dokumentu, wcięcia i podziały linii dokładnie.
- Zwróć TYLKO przetłumaczony HTML, bez wyjaśnień ani obramowań kodu Markdown.

Dodatkowo, aby zachować integralność treści:
- Każde wystąpienie tekstu, także identyczne z poprzednim, jest osobnym fragmentem źródłowym.
- Nie traktuj powtarzających się fragmentów jako duplikatów i nie pomijaj żadnego ich wystąpienia.
- Zachowaj kolejność wszystkich fragmentów tekstowych dokładnie zgodnie ze źródłem.
- Po ostatnim powtarzającym się fragmencie przetwórz również każdy następny fragment, aż do końca przekazanego wejścia.
- Nie kończ tłumaczenia wcześniej tylko dlatego, że kolejne fragmenty są podobne do już przetłumaczonych.
