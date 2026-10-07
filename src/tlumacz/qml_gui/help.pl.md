# Pomoc podręczna

> **Stan pomocy: 2026-10-05.** Ta pomoc opisuje aktualne karty **Tłumaczenie**, **API i serwer**, **Przełączniki** oraz **Pomoc**. Jeśli opis w starszej dokumentacji projektu różni się od programu, pierwszeństwo ma aktualny interfejs.

## Na początek

Tłumacz służy do tłumaczenia plików bez ręcznego kopiowania tekstu między programami. Wybierasz dokument, język docelowy i sposób tłumaczenia. Program przygotowuje dokument, tłumaczy jego treść i zapisuje wynik.

### Najkrótsza droga

1. Otwórz kartę **Tłumaczenie**.
2. Wybierz **Plik wejściowy**.
3. Wybierz **Plik wyjściowy** albo użyj podpowiadanej nazwy.
4. Wybierz **Język docelowy**.
5. Ustaw sposób tłumaczenia w karcie **API i serwer**.
6. Kliknij **Tłumacz**.

Podczas pracy możesz obserwować postęp, czas, szybkość, log i podgląd wyniku.

### Jakie pliki możesz tłumaczyć

Główny Filter Engine ma obecnie filtry dla:

- DOCX,
- ODT,
- HTML i XHTML,
- Markdown,
- EPUB,
- XLIFF.

Dostępne są również skille dla **TXT** (`plaintext.md`) i **PDF** (`pdf.md`). Są one dobierane automatycznie po rozszerzeniu pliku i przekazywane do aktywnej ścieżki tłumaczenia odpowiedniej dla danego formatu.

PDF korzysta z własnej ścieżki ekstrakcji bloków tekstowych; skill `pdf.md` opisuje zasady tłumaczenia tych bloków.

## Tłumacz dokument

Karta **Tłumaczenie** prowadzi przez cały proces.

### Plik wejściowy i wyjściowy

**Plik wejściowy** to dokument, który chcesz przetłumaczyć.

**Plik wyjściowy** to miejsce, w którym program zapisze wynik. Jeśli nie wskażesz własnej nazwy, program może zaproponować nazwę opartą na nazwie pliku wejściowego i języku docelowym.

### Język

Dla zwykłych backendów wybierz język z pola **Język docelowy**. Dla Apertium karta pokazuje język źródłowy i docelowy w polach tylko do odczytu. W aktualnym GUI nie ma osobnego wyboru źródła na tej karcie.

### Co dzieje się po kliknięciu „Tłumacz”

Program:

1. odczytuje dokument;
2. wydziela treść przeznaczoną do tłumaczenia;
3. dzieli ją na fragmenty;
4. przygotowuje instrukcję dla wybranego sposobu tłumaczenia;
5. wykonuje tłumaczenie;
6. sprawdza wynik;
7. umieszcza przetłumaczony tekst z powrotem w dokumencie;
8. zapisuje plik wynikowy.

Program pilnuje przy tym elementów dokumentu, których nie należy tłumaczyć, oraz jego struktury.

### Postęp i anulowanie

Pasek **Postęp** pokazuje bieżący stan pracy. Obok niego widzisz procent wykonania.

**Czas** pokazuje czas trwania operacji. **Szybkość** pokazuje bieżącą i średnią liczbę znaków przetwarzanych na sekundę.

Przycisk **Anuluj** zatrzymuje dalszą pracę tłumaczenia. Anulowanie nie oznacza awarii programu.

## Wybierz sposób tłumaczenia

W karcie **API i serwer** wybierasz sposób wykonania tłumaczenia.

### llama.cpp

llama.cpp wykonuje tłumaczenie lokalnie, z użyciem uruchamianego przez aplikację serwera i lokalnego modelu.

Ustawienia, które możesz tu spotkać:

- adres URL serwera;
- klucz API, jeśli wymaga go używany serwer;
- port;
- sposób obliczeń;
- temperaturę;
- liczbę równoległych zadań;
- plik modelu GGUF;
- szablon czatu;
- automatyczny start serwera;
- czyszczenie pamięci podręcznej po tłumaczeniu;
- restart serwera po tłumaczeniu.

**Model nie jest backendem.** Model to zasób używany przez llama.cpp.

### Chmura

**Chmura** korzysta z zewnętrznej usługi tłumaczeniowej lub modelu dostępnego przez sieć.

Konfiguracja jest zapisywana osobno dla wybranej usługi. Dzięki temu różne usługi mogą mieć własne adresy, modele i klucze.

Profile widoczne w aktualnym interfejsie obejmują między innymi ChatGPT, Codex, Gemini Flash, Gemini Flash Lite, DeepSeek, Cohere, DeepL API Free, MyMemory, Microsoft Translator, DLX i Mozhi.

Jeśli korzystasz z usługi chmurowej, tekst dokumentu opuszcza komputer zgodnie z zasadami wybranej usługi.

### Apertium

**Apertium** to lokalny system tłumaczenia oparty na regułach i pakietach językowych. Nie jest modelem LLM.

Aplikacja korzysta z dostępnych par językowych. Jeżeli potrzebna para nie jest dostępna, tłumaczenie nie może zostać wykonane tą metodą.

Apertium działa jako osobna ścieżka procesu. Przycisk restartu serwera nie zarządza nim tak samo jak zarządzany serwer llama.cpp.

### Własny serwer

**Własny** oznacza serwer uruchomiony poza aplikacją.

Tłumacz może się z nim połączyć zgodnie z wymaganym kontraktem, ale nie zarządza jego procesem, modelem ani ustawieniami sprzętowymi.

### Jak wybrać metodę

Wybierz **llama.cpp**, jeśli chcesz korzystać z lokalnego modelu.

Wybierz **Chmurę**, jeśli chcesz użyć zewnętrznej usługi.

Wybierz **Apertium**, jeśli potrzebna para językowa jest dostępna w lokalnych pakietach Apertium.

Wybierz **Własny**, jeśli masz już działający serwer zgodny z wymaganym interfejsem.

## Ustawienia i narzędzia

Karta **Przełączniki** zawiera glosariusz, skille oraz ustawienia LLM. Ustawienia zachowania konkretnego backendu są prezentowane przy właściwym backendzie w karcie **API i serwer**, a nie jako wspólna lista przełączników.

### Glosariusz

Glosariusz przechowuje pary terminów źródłowych i docelowych.

Użyj go, gdy konkretne nazwy lub terminy mają być tłumaczone w ustalony sposób.

### Skille

Skille to dodatkowe instrukcje używane podczas tłumaczenia.

Program rozróżnia:

- **Skille systemowe** — dostarczane razem z programem;
- **Skille użytkownika** — dodane przez użytkownika.

Możesz je włączać i wyłączać. Dostępne są także akcje importowania, odświeżania, usuwania i tworzenia skilla.

### Ustawienia LLM

W tej części znajdziesz parametry używane przez ścieżki oparte na modelach.

**Rozmiar bloku** określa, ile treści program grupuje przed przekazaniem jej do tłumaczenia.

**Temperatura** wpływa na sposób generowania odpowiedzi przez model. Wyższa wartość daje większą swobodę, a niższa bardziej powtarzalne odpowiedzi.

**Własne instrukcje modelu** pozwalają dodać własne zasady do zadania tłumaczeniowego.

**Pomijane linie** pozwalają określić wzorce, których program nie powinien wysyłać do tłumaczenia.

## Wynik i problemy

### Log

Sekcja **Log** pokazuje komunikaty programu dotyczące bieżącej pracy.

Jeśli tłumaczenie zakończy się błędem, sprawdź log przed ponownym uruchomieniem.

### Podgląd

Sekcja **Podgląd tłumaczenia** pokazuje dostępny wynik tłumaczenia.

W przypadku formatów tekstowych może pokazać zawartość pliku wynikowego. Nie każdy format dokumentu ma podgląd identyczny z wyglądem pliku otwartego w zewnętrznym programie.

### Po zakończeniu

Sprawdź:

- czy plik wynikowy został zapisany;
- czy dokument otwiera się poprawnie;
- czy zachował oczekiwaną strukturę;
- czy nazwy, adresy, kod i inne elementy, których nie chcesz tłumaczyć, pozostały poprawne.

### Gdy coś nie działa

Najpierw sprawdź, **gdzie** wystąpił problem.

### Program nie może rozpocząć tłumaczenia

Sprawdź plik wejściowy, plik wyjściowy i wybrany sposób tłumaczenia.

Jeśli używasz llama.cpp, sprawdź adres, port i plik GGUF. Jeśli używasz Chmury, sprawdź usługę, adres i klucz. Jeśli używasz Apertium, sprawdź dostępność wymaganej pary językowej.

### Nie działa połączenie z Chmurą

Sprawdź, czy usługa jest dostępna.

Sprawdź adres usługi i klucz zapisany dla wybranego profilu.

Nie używaj klucza z innej usługi jako zamiennika.

### Nie działa llama.cpp

Sprawdź, czy wskazany plik GGUF istnieje.

Sprawdź port i adres serwera.

Jeśli aplikacja zarządza serwerem, użyj **Restartuj serwer** po sprawdzeniu ustawień.

### Brakuje pary Apertium

Sprawdź listę dostępnych pakietów językowych. Apertium może tłumaczyć tylko za pomocą par, które są dostępne w aktualnym środowisku.

### Wynik wygląda źle

Nie uruchamiaj od razu kolejnej próby.

Najpierw sprawdź log, plik wejściowy, wybraną metodę tłumaczenia i ustawienia dodatkowych instrukcji.

Jeśli problem dotyczy struktury dokumentu, sprawdź także, czy ten sam problem występuje w innym obsługiwanym formacie.

### Co warto wiedzieć o programie

Tłumacz nie traktuje dokumentu jako zwykłego ciągu znaków. Najpierw przygotowuje jego treść, tłumaczy odpowiednie fragmenty, a następnie składa wynik.

To pozwala oddzielić treść od struktury dokumentu.

W wersji **0.40.0** główne elementy V4 są już po migracji do nowej architektury. Program jest obecnie kandydatem do wydania. Finalne wydanie pozostaje zależne między innymi od domknięcia kwestii wydania Apertium, Windows oraz kompletności zależności i licencji.

### Gdzie szukać szczegółów

Jeśli potrzebujesz informacji technicznych, pełne opisy znajdują się w dokumentacji projektu. Pomoc w aplikacji ma odpowiadać na pytanie **„jak użyć programu?”**, a nie zastępować dokumentację developerską.
