---
id: user-guide-v4
status: active
meta:
  contentType: Guide
  category: technical
version: 0.40.0
updated: 2026-10-04
owner: project-documentation
source: src/tlumacz/qml_gui/, src/tlumacz/application/, src/tlumacz/filter_engine/
depends_on: [docs/STATUS.md, docs/RETIRED_FUNCTIONALITY.md, docs/technical-docs/functional-capabilities.md]
expires_when: zmiana aktywnej powierzchni GUI lub pipeline'u dokumentowego
last_validation: "inspekcja kodu SentinelX 2026-10-04; pytest 268 passed, compileall PASS, qmllint PASS"
---

## 2026-10-05 — aktualizacja zgodna z bieżącym GUI

Aktywna powierzchnia QML ma cztery zakładki: **Tłumaczenie**, **API i serwer**, **Przełączniki**, **Pomoc**. Karta **API i serwer** jest miejscem wyboru backendu i jego ustawień. Karta **Przełączniki** zawiera glosariusz, skille i ustawienia LLM.

Główny Filter Engine obsługuje DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF. TXT i PDF nie są obecnie zarejestrowane w `build_filter_registry()`.

Dla Apertium GUI pokazuje źródło i cel w polach tylko do odczytu. W karcie Tłumaczenie pola te pozostają w tym samym wierszu sterowania co przyciski Tłumacz/Anuluj. Jest to stan rzeczywisty, nie docelowa specyfikacja układu.

Pomoc użytkownika jest ładowana z `src/tlumacz/qml_gui/help.pl.md`, `help.en.md` i `help.de.md`. Każdy plik musi zawierać pięć nagłówków `##`, ponieważ bridge dzieli plik na tematy właśnie po tych nagłówkach.

# Podręcznik użytkownika — Tłumacz V4

## Co robi program

Tłumacz służy do tłumaczenia obsługiwanych dokumentów. Program przygotowuje jednostki dokumentu, przekazuje tekst do wybranego backendu, waliduje wynik i zapisuje dokument wynikowy.

## Podstawowy przepływ

1. Otwórz kartę **Tłumaczenie**.
2. Wybierz **Plik wejściowy**.
3. Wybierz **Plik wyjściowy**.
4. Wybierz **Język docelowy**.
5. Ustaw backend w karcie **API i serwer**.
6. Kliknij **Tłumacz**.
7. Obserwuj **Postęp**, **Log** i **Podgląd tłumaczenia**.
8. W Logu kolejno pojawiają się m.in. wybór skilla, gotowość, start tłumaczenia, informacja o typie dokumentu, liczba pominiętych fragmentów, liczba bloków oraz komunikaty `Tłumaczenie bloku X z Y...`. Nad Logiem podczas pracy działa animowany wskaźnik aktywnego tłumaczenia.
9. Jeżeli blok zakończy się błędem, Log pokazuje `Błąd bloku X z Y: ...`, a wskaźnik pracy zatrzymuje się; komunikat podsumowujący sukces nie jest generowany.
10. Po zakończeniu Log pokazuje liczbę przetłumaczonych bloków, czas, szybkość w znakach/s i ścieżkę zapisanego dokumentu.
11. W razie potrzeby użyj **Anuluj**.

## Aktywnie zarejestrowane formaty dokumentów

Aktualny `FilterRegistry` V4 rejestruje:

- DOCX;
- ODT;
- HTML;
- XHTML;
- Markdown;
- EPUB;
- XLIFF 2.0.

**TXT i PDF nie są obecnie zarejestrowane w aktywnym głównym pipeline V4.** Pliki skilli opisujące TXT/PDF są zasobami instrukcji i nie oznaczają obsługi tych formatów przez `DocumentProcessor`.

## Sposoby tłumaczenia

### llama.cpp

Lokalny backend korzystający z zarządzanego llama-server. Konfiguracja obejmuje m.in. model GGUF, port, tryb obliczeń, równoległość, temperaturę i szablon czatu.

Szablon `TranslateGemma` jest formatem promptu llama.cpp, a nie osobnym backendem.

### Chmura

Router Cloud wybiera aktywny provider. V4 zawiera adaptery OpenAI-compatible, DeepL, Microsoft, MyMemory, LibreTranslate i DLX. Mozhi jest osobnym providerem Cloud z wyborem instancji i silnika.

### Apertium

Apertium jest lokalnym backendem korzystającym z prywatnego runtime'u. Dostępne pary zależą od danych językowych obecnych w instalacji.

### Własny

Backend **Własny** korzysta z CloudRouter z parametrami własnego endpointu. Nie jest osobnym lokalnym silnikiem.

## Język źródłowy

GUI może przechowywać wartość źródła jako `auto`. Dla szablonu `TranslateGemma` adapter llama.cpp używa `LanguageDetector` opartego na Lingua i zamienia wykryty język na kod ISO 639-1. Standardowy llama.cpp, Cloud i Apertium nie korzystają z tego globalnie; `auto` nie oznacza automatycznej detekcji przez każdy backend.

## Glosariusz i skille

Karta **Przełączniki** udostępnia glosariusz oraz skille systemowe i użytkownika. Bridge obsługuje dodawanie wpisów, odświeżanie, import, usuwanie i zapis szablonu skilla.

## Ustawienia

Aplikacja zapisuje m.in. backend, profile Cloud, parametry llama.cpp, rozmiar fragmentu, temperaturę, wzorce pomijania, glosariusz, motyw, język aplikacji oraz ustawienia lifecycle serwera.

## Pomoc i lokalizacja

GUI QML korzysta z lokalizacji PL/EN/DE. Pomoc jest renderowana z plików Markdown dla odpowiedniego języka, z fallbackiem do PL.

## Anulowanie i diagnostyka

Anulowanie zatrzymuje dalsze przetwarzanie jednostek. GUI pokazuje postęp, czas, prędkość, log i podgląd.

Szczegółowa macierz implementacji znajduje się w `functional-capabilities.md`.
