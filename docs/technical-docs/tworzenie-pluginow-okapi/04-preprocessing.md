# Preprocessing i klasyfikacja jednostek

## 1. Umiejscowienie

Aktualny kod pokazuje, że preprocessing jest wykonywany przez `Preprocessor` po uzyskaniu jednostek z filtra.

`DocumentProcessor` wywołuje:

1. `preflight(source)`;
2. `filter_contract.extract(session)`;
3. walidację jednostek;
4. `preprocessor.classify_units(...)`.

Nie należy więc rysować preprocessingu jako zamiennika ekstrakcji formatu.

## 2. Preflight

`preflight()` wybiera wysokopoziomową ścieżkę przygotowania wejścia. Jest to decyzja przygotowawcza, a nie tłumaczenie.

Dokładna semantyka preflightu powinna być utrzymywana razem z kodem `preprocessor.py`; diagram nie powinien przypisywać mu odpowiedzialności parsera formatu.

## 3. TRANSLATE / KEEP

Klasyfikacja jest istotnym punktem granicznym:

- `TRANSLATE` — jednostka może zostać skierowana do tłumaczenia;
- `KEEP` — jednostka pozostaje w tekście źródłowym.

KEEP nie jest wysyłane do backendu. Oryginał pozostaje dostępny dla rekonstrukcji.

## 4. Ochrona treści

Ochrona treści wymagających zachowania 1:1 jest odpowiedzialnością preprocessingu/filtra zależnie od rodzaju danych. Inline codes strukturalne mają dodatkowo własny kontrakt walidacyjny Filter Engine.

Nie wolno łączyć tych mechanizmów w jeden ogólny „placeholder”.

## 5. Źródło semantyki

Historyczny V3 `preprocess.py` jest używany w planach migracyjnych jako źródło zachowania, ale aktywny V4 należy opisywać na podstawie `src/tlumacz/preprocessing/`.

To rozróżnienie jest istotne, ponieważ nazwy modułów V3 i V4 nie są już tożsame.
