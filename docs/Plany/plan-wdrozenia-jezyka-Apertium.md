---
id: plan-wdrozenia-jezyka-apertium
status: implemented
version: 1.1
updated: 2026-10-06
scope: Apertium / wybór języka źródłowego i docelowego
---

# Plan wdrożenia wyboru języka Apertium

## 1. Cel

Wdrożyć mechanizm zgodny z dokumentem wyboru języka Apertium. Zakres obejmuje discovery par, indeks dwukierunkowy, Lingua, resolver targetów, ręczny wybór źródła, BRAK, unieważnianie starego targetu, testy i konfigurację katalogu danych.

## 2. Zasady

- Nie instalować ani usuwać żadnego oprogramowania.
- Nie przenosić obecnych danych poza uzgodniony zakres.
- Nie hardcodować ścieżki projektu.
- Logikę domenową umieścić poza QML.
- Zachować kontrakt QmlApplicationBridge.
- Przed zmianą kodu wykonać backup modyfikowanych artefaktów.
- Po każdej zmianie wykonać weryfikację.

## 3. Etap 0 — inwentaryzacja

Aktualny kod potwierdza:
- ApertiumConfig.data_dir;
- domyślne $HOME/.config/tlumacz/apertium;
- discover_language_plugins();
- discover_supported_pairs();
- apertium_pair_to_iso();
- supported_targets_for_source();
- QmlApplicationBridge.source_language;
- ApiPage.qml z apertiumSourceLanguage i apertiumTargetLanguage.

Problem: supported_targets_for_source() rozpoznaje tylko pary rozpoczynające się od źródła. Dla pol-eng nie daje automatycznie eng → pol.

## 4. Etap 1 — katalog danych

Ustalić jeden konfigurowalny katalog danych Apertium. Obecny punkt abstrakcji ApertiumConfig.data_dir należy zachować.

Dane pozostają obecnie w projekcie zgodnie z wymaganiem użytkownika. Implementacja ma umożliwiać wskazanie tego katalogu przez konfigurację bez zmiany resolvera.

Kryterium: zmiana katalogu danych nie wymaga zmiany logiki par.

## 5. Etap 2 — discovery

Discovery ma zwracać tylko używalne pary.

Każda para musi:
1. mieć format xxx-yyy;
2. mieć różne kody;
3. być możliwa do zmapowania;
4. pochodzić z aktywnego runtime.

Sam katalog pakietu nie jest wystarczającym dowodem dostępności.

## 6. Etap 3 — normalizacja

Utrzymać jedno miejsce mapowania ISO 639-1 ↔ Apertium 639-3 w languages.py.

Nie powielać mapowania w QML, bridge ani testach.

## 7. Etap 4 — indeks

Dodać funkcję w rodzaju:

build_language_pair_index(supported_pairs)

Dla:
pol-eng
pol-deu

wynik logiczny:

pol → eng, deu
eng → pol
deu → pol

Usuwać duplikaty. Kolejność ma być deterministyczna. Niepoprawne pary nie mogą trafić do indeksu.

## 8. Etap 5 — resolver

Resolver przyjmuje selected_source i pair_index, a zwraca available_targets.

Reguła:
available_targets = pair_index[selected_source] lub pusty zbiór.

Resolver nie może zależeć od QML.

## 9. Etap 6 — Lingua

Przepływ:

tekst dokumentu
→ Lingua
→ ISO source
→ normalizacja
→ resolver Apertium
→ target model

Nie tworzyć drugiego detektora tylko dla GUI. Jeżeli obecny detektor Lingua jest związany z innym backendem, wydzielić wspólną usługę detekcji bez przenoszenia logiki par do detektora.

## 10. Etap 7 — bridge

Bridge powinien rozdzielać:
- detectedSourceLanguage;
- selectedSourceLanguage;
- availableTargetLanguages;
- selectedTargetLanguage;
- targetSelectionEnabled.

Źródło jest ręczne albo wykryte. W obu przypadkach targety oblicza ten sam resolver.

## 11. Etap 8 — zmiana źródła

Algorytm:

on_source_changed(source):
1. normalize(source);
2. targets = resolver.targets(source);
3. jeżeli selected_target nie należy do targets, wyzeruj go;
4. target_enabled = bool(targets);
5. odśwież QML.

## 12. Etap 9 — BRAK

Przy pustej liście targetów bridge udostępnia stan pozwalający QML pokazać BRAK i wyłączyć selector.

BRAK nie może być elementem wartości backendowej.

## 13. Etap 10 — QML

ApiPage.qml powinien otrzymać gotowy model. QML ma jedynie:
- prezentować source;
- prezentować targety;
- pokazywać BRAK;
- ustawiać enabled;
- przekazywać wybory.

Nie implementować w QML skanowania, parsowania modes.xml, odwracania par ani mapowania ISO.

## 14. Etap 11 — zachowanie GUI

Nie zmieniać układu ani kolejności pól, innych backendów i niepowiązanych ustawień. Zmiana ma dotyczyć zachowania list językowych i zależnych stanów.

## 15. Etap 12 — testy indeksu

Wymagane przypadki:

A. jedna para:
pol-eng
→ pol: eng
→ eng: pol

B. wiele:
pol-eng, pol-deu
→ pol: eng, deu
→ eng: pol
→ deu: pol

C. brak:
[]
→ brak targetów

D. duplikat:
pol-eng, pol-eng
→ eng tylko raz

E. niepoprawna para:
invalid
→ brak wpisu

## 16. Etap 13 — testy resolvera

| Source | Index | Expected |
|---|---|---|
| pl | pl→eng | eng |
| eng | pl→eng | pl |
| de | pl→de | pl |
| fr | brak | pusty |

## 17. Etap 14 — testy bridge

Zweryfikować:
1. automatyczne źródło;
2. ręczne źródło;
3. ręczne źródło bez par;
4. zmianę pl → de;
5. unieważnienie starego targetu;
6. BRAK;
7. disabled target;
8. ponowne włączenie targetu po wyborze źródła z parami.

## 18. Etap 15 — testy QML

Sprawdzić kontrakt:
- source model jest widoczny;
- target model jest przefiltrowany;
- enabled odpowiada dostępności;
- BRAK jest pokazywany przy pustym modelu;
- stary target nie pozostaje po zmianie źródła.

## 19. Etap 16 — test integracyjny

Scenariusz 1:
tekst polski → Lingua = pl → runtime ma pol-eng i pol-deu → targety en/de → użytkownik wybiera de → backend otrzymuje pl → de.

Scenariusz 2:
tekst angielski → Lingua = en → runtime ma tylko pol-eng → target = pl.

Scenariusz 3:
tekst francuski → Lingua = fr → brak pary → target = BRAK → selector disabled.

## 20. Etap 17 — test konfiguracji

Zmienić wyłącznie katalog danych w konfiguracji i ponowić discovery.

Oczekiwane:
- resolver bez zmian;
- QML bez zmian;
- discovery czyta nowy katalog.

Nie wpisywać do kodu /home/frs/Projekty/tlumacz-v4/Aperitium ani innej ścieżki środowiskowej.

## 21. Etap 18 — weryfikacja końcowa

Uruchomić:
1. testy Apertium;
2. testy resolvera;
3. testy bridge;
4. testy QML;
5. test integracyjny;
6. kontrolę konfiguracji;
7. kontrolę braku hardcoded path;
8. kontrolę diff;
9. kontrolę dokumentacji.

Sprawdzić także, że zmieniono tylko pliki objęte zakresem.

## 22. Kolejność zmian

1. languages.py;
2. language_plugins.py, tylko jeśli konieczne;
3. resolver;
4. bridge.py;
5. ApiPage.qml;
6. testy jednostkowe;
7. testy bridge/QML;
8. test integracyjny;
9. dokumentacja i changelog.

## 23. Ryzyka

### Kierunek par
pol-eng musi tworzyć także relację eng → pol.

### Nieużywalne dane
Katalog pakietu nie gwarantuje gotowego trybu runtime.

### Kody ISO
pl i pol muszą być konsekwentnie normalizowane.

### Logika w QML
Odwracanie par w QML tworzyłoby drugi resolver i utrudniało testowanie.

### Stale target
Po zmianie źródła niekompatybilny target musi zostać usunięty.

## 24. Kryterium zakończenia

Gotowy przepływ:

Lingua
→ normalized source
→ pair index
↕
bidirectional relations
→ filtered target model
→ QML

musi działać dla jednej pary, wielu par, kierunku odwrotnego, braku par, źródła automatycznego, źródła ręcznego, zmiany źródła, unieważnienia targetu, BRAK oraz zmiany katalogu wyłącznie przez konfigurację.

## 25. Ostateczny kontrakt

Dla każdej pary A-B:
- dodaj A → B;
- dodaj B → A.

Dla selected_source:
- targets = pair_index[selected_source] albo pusty zbiór.

Jeżeli targets jest pusty:
- pokaż BRAK;
- wyłącz target.

BRAK jest stanem UI, nigdy kodem języka Apertium.


## 26. Stan wdrożenia — 2026-10-06

Plan dla zakresu wyboru języka został wykonany. Etapy discovery, indeksu, resolvera, bridge, BRAK, QML, testów indeksu/bridge/QML i konfiguracji katalogu danych są zamknięte. Etap integracyjny jest zweryfikowany dla rzeczywistych E2E dokumentowych Apertium, natomiast pełna macierz wszystkich dostępnych par pozostaje osobnym zadaniem jakościowym.

Backup zmian: `backups/apertium-language-selection-20261006/`.
