---
id: wybor-jezyka-apertium
status: implemented
version: 1.1
updated: 2026-10-06
scope: Apertium / wybór języka źródłowego i docelowego
---

# Wybór języka Apertium

## 1. Cel

Mechanizm ma automatycznie wykrywać język źródłowy dokumentu, ustalać dostępne dla niego pary Apertium i ograniczać listę języków docelowych wyłącznie do języków, dla których w aktualnym runtime istnieje używalna para.

Pary Apertium należy traktować jako relację logicznie dwukierunkową. Para pol-eng daje więc możliwość wyboru zarówno pl → eng, jak i eng → pl. Nie oznacza to, że oba kierunki muszą być zapisane jako dwa niezależne pakiety runtime.

## 2. Stan obecny

Kod V4 posiada:
- ApertiumConfig.data_dir;
- domyślny katalog danych $HOME/.config/tlumacz/apertium;
- discovery pakietów przez language_plugins.py;
- mapowanie ISO 639-1 ↔ Apertium 639-3 w languages.py;
- ApiPage.qml z polami apertiumSourceLanguage i apertiumTargetLanguage;
- QmlApplicationBridge jako kontrakt GUI.

Aktualne supported_targets_for_source() jest kierunkowe i nie odwraca par. To jest główny punkt wymagający zmiany.

## 3. Źródło prawdy

Źródłem dostępności par są rzeczywiście wykryte i używalne tryby runtime Apertium. Nie wolno budować targetów wyłącznie z pełnej listy języków, nazw katalogów ani danych historycznych.

Do indeksu trafiają tylko poprawne pary dostępne w skonfigurowanym katalogu danych.

## 4. Normalizacja

Kod z Lingua należy normalizować do wewnętrznego identyfikatora Apertium.

Przykłady:
- en → eng
- pl → pol
- de → deu
- uk → ukr

QML nie wykonuje własnego mapowania.

## 5. Indeks dwukierunkowy

Dla każdej pary A-B należy dodać dwa wpisy logiczne:

A → B
B → A

Przykład:

pol-eng
pol-deu
pol-ukr

daje:

pol → [eng, deu, ukr]
eng → [pol]
deu → [pol]
ukr → [pol]

Duplikaty są usuwane, a kolejność musi być deterministyczna.

## 6. Automatyczne wykrycie źródła

1. Po wczytaniu tekstu dokumentu używany jest istniejący mechanizm Lingua.
2. Wynik jest normalizowany.
3. Wykryty język staje się selectedSourceLanguage.
4. Resolver wylicza availableTargetLanguages.
5. QML otrzymuje już przefiltrowany model.

Jeżeli Lingua nie wykryje języka, nie wolno udawać poprawnego wykrycia. Stan powinien pozostać nierozstrzygnięty i umożliwiać ręczny wybór źródła, jeżeli GUI go przewiduje.

## 7. Ręczny wybór źródła

Użytkownik może wymusić source language. Po zmianie:
1. ustawiany jest selectedSourceLanguage;
2. targety są przeliczane od zera;
3. niekompatybilny stary target jest usuwany;
4. model targetów jest aktualizowany;
5. stan enabled/disabled jest aktualizowany.

Automatyczne i ręczne źródło korzystają z tego samego resolvera.

## 8. Filtrowanie targetów

Jedyną poprawną regułą jest:

availableTargets = wszystkie języki połączone z selectedSourceLanguage w indeksie zbudowanym z aktualnych par Apertium.

Nie wolno pokazywać języka, dla którego nie istnieje relacja z wybranym źródłem.

## 9. Brak par

Jeżeli selectedSourceLanguage nie ma żadnej kompatybilnej pary:

- source pokazuje wykryty lub wymuszony język;
- target pokazuje BRAK;
- target selector jest disabled;
- BRAK jest stanem prezentacyjnym, a nie kodem Apertium.

BRAK nigdy nie może zostać przekazany do backendu.

## 10. Jeden lub wiele targetów

Jedna para:
source = pl
target = en

Wiele:
source = pl
targets = en, de, uk

Target zawiera wyłącznie wartości z indeksu dla źródła.

## 11. Invariant

Po każdej zmianie źródła musi być spełnione:

selectedTargetLanguage == null
albo
selectedTargetLanguage należy do availableTargets(selectedSourceLanguage)

Przykład:
przed: pl → eng
po zmianie: de → pl

eng musi zostać usunięty.

## 12. Kontrakt warstwy aplikacyjnej

Resolver powinien zapewniać co najmniej:
- discover_pairs();
- build_pair_index();
- available_targets(source_language).

Bridge może udostępniać:
- detectedSourceLanguage;
- selectedSourceLanguage;
- availableTargetLanguages;
- selectedTargetLanguage;
- hasAvailableTargets;
- targetSelectionEnabled.

QML pozostaje warstwą prezentacji.

## 13. QML

ApiPage.qml ma:
- wyświetlać źródło;
- wyświetlać przefiltrowany model targetów;
- pokazywać BRAK;
- wyłączać selector przy braku targetów;
- przekazywać ręczne wybory do bridge.

QML nie skanuje katalogów, nie parsuje modes.xml i nie odwraca par.

## 14. Katalog danych

Dane par pozostają obecnie w projekcie zgodnie z wymaganiem wdrożeniowym. Mechanizm nie może jednak hardcodować ścieżki projektu.

Zmiana punktu montowania lub katalogu ma wymagać wyłącznie zmiany konfiguracji. Kod nie może zawierać ścieżki zależnej od środowiska, np. /home/frs/Projekty/tlumacz-v4/Aperitium.

## 15. Kryteria akceptacji

1. Lingua poprawnie ustala źródło.
2. Każda para jest indeksowana w obu kierunkach logicznych.
3. pol-eng daje pl → en oraz en → pl.
4. Target zawiera tylko kompatybilne języki.
5. Brak par daje BRAK i disabled target.
6. Ręczna zmiana źródła ponownie filtruje targety.
7. Stary niekompatybilny target jest usuwany.
8. BRAK nigdy nie trafia do backendu jako kod języka.
9. Zmiana katalogu danych wymaga tylko zmiany konfiguracji.
10. Istnieją testy jednostkowe, bridge/QML i integracyjne.

## 16. Macierz zachowania

| Źródło | Pary | Target |
|---|---|---|
| pl | pl-eng | eng |
| eng | pl-eng | pl |
| pl | pl-eng, pl-de | eng, de |
| de | pl-de | pl |
| fr | brak | BRAK, disabled |
| wymuszone de | pl-de | pl |
| wymuszone fr | brak | BRAK, disabled |


## 17. Stan wdrożenia — 2026-10-06

Specyfikacja została wdrożona. Discovery korzysta z faktycznie skompilowanych trybów, indeks par jest logicznie dwukierunkowy, targety są filtrowane względem źródła, a niezgodny target jest zerowany. Przy braku pary GUI pokazuje `brak pary` i blokuje selektor.

Dla tekstowych plików przy źródle automatycznym bridge korzysta z istniejącego `LanguageDetector`/Lingua. Katalog danych jest pobierany z `default_data_dir()`; docelowo jest to `$HOME/.config/tlumacz/apertium/`.

Weryfikacja:
- 12 focused testów wyboru języka;
- 12 testów adapter/backend/runtime;
- 2 testy E2E dokumentowego Apertium;
- 87 testów QML;
- discovery rzeczywistego katalogu użytkownika: 8 gotowych kierunków.
