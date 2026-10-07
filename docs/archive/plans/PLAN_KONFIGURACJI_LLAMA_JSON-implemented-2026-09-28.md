---
meta:
  contentType: Plan
  category: configuration
status: historical
date: 2026-09-27
---

# Plan przebudowy konfiguracji llama.cpp i config.json

## Cel

Rozdzielić ustawienia użytkowe aplikacji od ukrytego tuningu llama.cpp.
Program ma działać na różnych CPU, GPU i ilościach pamięci bez przenoszenia
wartości zmierzonych na jednym komputerze do wszystkich instalacji.

## Artefakty przygotowane przed zmianą kodu

- `config/llama.json` — tymczasowy projekt konfiguracji backendu.
- `config/config.proposed.json` — propozycja uporządkowanego config.json.
- Kanoniczna lokalizacja docelowa llama: `$HOME/.config/tlumacz/llama.json`.
- Obecny `config/config.json` pozostaje nietknięty, ponieważ zawiera dane
  użytkownika, w tym klucze API.

## Podział odpowiedzialności

### config.json

Przechowuje ustawienia użytkownika i GUI:
- język docelowy, temperatura i rozmiar bloku,
- aktywne skille i wzorce pomijania,
- ścieżkę glosariusza,
- wybrany backend,
- model GGUF,
- tryb CPU/GPU,
- liczbę równoległych zadań,
- port lokalnego serwera,
- profile usług chmurowych,
- ostatnie pliki.

Nie przechowuje technicznego tuningu llama.cpp.

### llama.json

Przechowuje ukryte parametry backendu:
- threads i threads-batch,
- batch i ubatch,
- ctx-size,
- KV cache,
- prompt cache,
- Flash Attention,
- repack,
- mmap/mlock,
- affinity CPU,
- polling i priority,
- NUMA,
- GPU layers, offload i split mode,
- reguły automatycznego doboru.

## Reguły automatycznego doboru

### Parallel

GUI zachowuje zakres ręczny 1–8 oraz wartość Auto.
Auto może dobrać wartość powyżej 8, jeśli sprzęt i pamięć na to pozwalają.
Nie zakładamy z góry, że 32 jest właściwe dla każdego GPU.

### Threads

`threads=auto` i `threads-batch=auto`.
Dobór wynika z topologii CPU i trybu obliczeń, a nie z ustawionej wartości
parallel.

### Context

Podstawowy model obliczeń:

`slot = blok + prompt + instrukcje + słownik + generacja + skill + margines`

`ctx = zaokrąglony slot`

`parallel` zwiększa liczbę slotów i zużycie pamięci KV, ale nie mnoży budżetu kontekstu pojedynczego slotu.

Koszt promptu i słownika jest obecnie szacowany z liczby znaków Unicode
przy współczynniku 4 znaki/token. Jest to heurystyka bez dodatkowej zależności
tokenizera i może zostać zastąpiona kalibracją modelową po T13–T15.
Block size jest wejściem do obliczenia, ale nie jest jedynym składnikiem ctx-size.

### Słownik

Pojemność słownika jest dynamiczna. Program powinien policzyć tokeny faktycznie
wysłane do modelu, zamiast używać stałej liczby tokenów.

### Bezpieczeństwo

Auto startuje od konserwatywnego profilu i nie wykonuje agresywnego zwiększania
kontekstu ani równoległości bez danych o pamięci. Walidacja limitu kontekstu
modelu i dokładniejszy budżet pamięci pozostają elementem dalszej kalibracji.

## Podstawa techniczna

Dokumentacja llama.cpp potwierdza, że serwer rozdziela m.in. `--ctx-size`,
`--parallel`, `--threads`, `--threads-batch`, `--batch-size`,
`--ubatch-size`, KV cache, prompt cache i parametry CPU. `--parallel`
oznacza liczbę slotów serwera, a nie liczbę wątków CPU.

Wyniki T4–T12 pozostają materiałem referencyjnym do inicjalnych wartości,
ale nie są traktowane jako uniwersalny profil sprzętowy.

## Integracja z programem

### Ścieżka pliku

[x] Dodać stałą ścieżki config_dir() / "llama.json".
[x] Obsłużyć $HOME/.config/tlumacz/llama.json.
[x] Nie czytać config/config.json jako źródła tuningu llama.cpp.
[x] Nie wprowadzać drugiego równorzędnego źródła .llama.json.

### Przebudowa konfiguracji

[x] Przebudować zapis config.json do uporządkowanych sekcji.
[x] Usunąć FastAPI/OpenVINO z zapisywanego schematu config.json.
[x] Zachować profile chmurowe i dane użytkownika.
[x] Nie zapisywać globalnego klucza API; klucze pozostają w profilach usług.
[x] Zachować migrację starego płaskiego config.json.

### Integracja llama.cpp

[x] Dodać loader llama.json z wartościami auto.
[x] Dodać detekcję CPU i dostępnej pamięci GPU.
[x] Dodać szacowanie tokenów promptu i słownika.
[x] Dodać dynamiczny kalkulator ctx-size.
[x] Rozdzielić parallel GUI od threads CPU.
[x] Zbudować komendę llama-server z wyliczonych parametrów.
[x] Zachować istniejące ustawienia GUI bez dodawania przełączników.
[ ] Rozszerzyć automatyczną detekcję VRAM na wszystkie wspierane backendy.
[ ] Dodać walidację limitu kontekstu z metadanych modelu.

## Pakietowanie

[x] Zaktualizować packages/0.31.2/PKGBUILD.
[x] Zaktualizować packaging/release-0.31.2/arch/PKGBUILD i .SRCINFO.
[x] Zaktualizować spec RPM w packaging/release-0.31.2/rpm/SPECS/.
[x] Zaktualizować kontrolę zależności DEB.
[x] Dodać config/llama.json jako data-file do wheel.
[x] Zweryfikować wheel: zawiera tlumacz-0.31.2.data/data/share/tlumacz/config/llama.json.
[ ] Wykonać końcowy clean build AUR, RPM, DEB i AppImage z aktualnego źródła.
[ ] Sprawdzić zawartość końcowych paczek i brak danych osobistych.

## TDD i walidacja

[x] Backup przed rozpoczęciem większej zmiany kodu: /tmp/tlumacz-backup-20260927-065844.
[x] Testy loadera llama.json.
[x] Testy walidacji wartości auto.
[x] Testy migracji starego config.json.
[x] Testy kalkulatora ctx-size.
[x] Testy szacowania glosariusza.
[x] Testy budowania komendy llama-server.
[x] Pełny zestaw testów projektu: 372 passed, 2 skipped.
[x] Kontrola wheel: szablon llama.json obecny.
[x] Aktualizacja dokumentacji i indeksu.

## Stan wykonania

1. Pliki konfiguracyjne przygotowane i wdrożone.
2. Backup wykonany przed zmianami.
3. Loader, migracja i profiler wdrożone przez TDD.
4. Integracja z ServerConfig i komendą llama-server wdrożona.
5. FastAPI/OpenVINO usunięte z zapisywanego schematu config.json.
6. Testy regresji GUI/backendów przechodzą.
7. Specyfikacje AUR/RPM/DEB zaktualizowane.
8. Wheel sprawdzony; szablon llama.json jest pakowany.
9. Pozostaje końcowy clean build AUR/RPM/DEB/AppImage.
10. Pozostają T13–T15 i T16.

## Kryterium akceptacji

Konfiguracja jest gotowa do dalszej kalibracji, gdy użytkownik ustawia model,
tryb obliczeń, block size i parallel w istniejącym GUI, a techniczne parametry
llama.cpp są wyliczane z llama.json, sprzętu i workloadu.
