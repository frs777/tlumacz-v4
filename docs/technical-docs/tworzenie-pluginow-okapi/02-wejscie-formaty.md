# Format wejściowy i wybór ścieżki

## 1. Aktywny FilterRegistry

Aktualny kod `src/tlumacz/filter_engine/registry.py` rejestruje m.in.:

- Markdown;
- Plain Text;
- filtry dokumentowe dla formatów Okapi;
- XLIFF.

W kodzie istnieje `PlainTextFilter` i jest on rejestrowany przez `register_lazy(PlainTextFilter._SUFFIXES, PlainTextFilter)`.

Dlatego wcześniejsze zdanie dokumentacji mówiące, że TXT nie jest w aktywnym rejestrze, jest nieaktualne względem kodu.

## 2. Formaty strukturalne

Dla formatów takich jak HTML/XHTML, DOCX, ODT, EPUB i XLIFF filtr dostarcza model jednostek dokumentowych i mechanizm writer/reconstruction.

Okapi jest używany tam, gdzie potrzebna jest reprezentacja struktury dokumentu i inline codes.

## 3. Markdown

Markdown ma aktywny `MarkdownFilter` w Filter Engine. Nie należy dokumentować starego `MarkdownPipeline` jako aktywnej ścieżki — audyt parytetu oznacza starą ścieżkę jako RETIRED.

## 4. TXT

TXT ma `PlainTextFilter`. To ścieżka tekstowa, bez potrzeby modelowania znaczników strukturalnych Okapi.

## 5. PDF

PDF nie jest zarejestrowany w aktywnym FilterRegistry. Kod GUI i skill PDF opisują osobną obsługę bloków tekstowych. Nie należy więc rysować PDF jako kolejnego filtra Okapi.

W dokumentacji pomocniczej znajduje się wprost informacja, że PDF korzysta z własnej ścieżki ekstrakcji bloków tekstowych.

## 6. Ważna korekta dokumentacyjna

Starsza dokumentacja łączyła TXT i PDF w jedną kategorię poza głównym rejestrem. Aktualny kod rozdziela te przypadki: TXT ma `PlainTextFilter`, natomiast PDF pozostaje poza aktywnym `FilterRegistry`.

Diagram ścieżek musi zatem rozdzielać:

- strukturalne filtry Filter Engine/Okapi,
- natywną ścieżkę Plain Text,
- Markdown Filter,
- osobną obsługę PDF.
