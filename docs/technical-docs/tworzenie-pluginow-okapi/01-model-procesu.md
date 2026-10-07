# Model procesu tłumaczenia

## 1. Granica dokumentowa

Aktywna ścieżka dokumentowa zaczyna się od wyboru obsługi formatu. Dla formatów zarejestrowanych w FilterRegistry filtr otwiera sesję, wykonuje ekstrakcję jednostek i udostępnia writerowi mechanizm rekonstrukcji.

Kod pokazuje następujący szkielet:

`FilterRegistry → FilterSession → extract() → walidacja jednostek → preprocessing → planowanie chunków → wykonanie tłumaczenia → zastosowanie targetów → write()`.

Jest to model logiczny. Poszczególne formaty różnią się reprezentacją jednostki i sposobem zachowania struktury.

## 2. Preprocessing nie zastępuje filtra

`Preprocessor` znajduje się w warstwie `src/tlumacz/preprocessing/`, natomiast ekstrakcję i zapis realizuje konkretny filtr. Oznacza to, że preprocessing nie jest parserem DOCX/HTML/EPUB itd.

W aktualnym kodzie `DocumentProcessor`:

1. wykonuje `preflight()`;
2. otwiera sesję filtra;
3. wywołuje `extract()`;
4. waliduje jednostki;
5. przekazuje je do `classify_units()`;
6. dopiero dalej jednostki są planowane do tłumaczenia.

To jest ważne dla diagramu: preprocessing należy pokazywać **po ekstrakcji jednostek**, a nie jako parser poprzedzający Filter Engine.

## 3. Klasyfikacja

`Preprocessor.classify_units()` przypisuje jednostkom status `TRANSLATE` albo `KEEP`.

`KEEP`:

- nie jest wysyłane do backendu;
- zachowuje tekst źródłowy;
- wraca do procesu rekonstrukcji 1:1.

`TRANSLATE` trafia do planowania i tłumaczenia.

## 4. Chunk i jednostka

Chunk jest jednostką transportową dla tłumaczenia. Nie należy utożsamiać go z jednostką dokumentową filtra.

Model:

`dokument → jednostki filtra → klasyfikacja → chunk → backend → wyniki przypisane do jednostek → writer`.

## 5. Równoległość

`TranslationExecutor` korzysta z `ThreadPoolExecutor` i parametr `max_workers`. `TranslationApp` przekazuje wartość równoległości do warstwy usługi.

Równoległość dotyczy wykonywania pracy tłumaczeniowej; nie zmienia odpowiedzialności filtra za ekstrakcję i zapis.

## 6. Diagram

Diagram główny znajduje się w `latex/main.tex`. Numery etapów diagramu odpowiadają sekcjom tego katalogu, aby można było przejść od grafu do dokładnego opisu odpowiedzialności.
