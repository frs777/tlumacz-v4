# STATUS DOKUMENTU: HISTORYCZNY / EVIDENCE

> Ścieżki `/home/frs/Projekty/agent-translator-v4` występują tu jako historyczne ślady wykonania. Oficjalny katalog V4 to `/home/frs/Projekty/tlumacz-v4/`. Nie traktować starej ścieżki jako aktywnego repozytorium.

# Faza 11 — packaging — stan zablokowany

Data: 2026-09-30

## Zakres wykonanej pracy

Rozpoczęto Fazę 11 zgodnie z planem migracji V4. Przed zmianami wykonano backup:

/home/frs/Projekty/agent-translator-v4/.migration-backups/pre-packaging-phase11-20260930.tar.gz

## Dependency closure

W V4 istniał launcher Java Filter Host, ale brakowało katalogu filtry/runtime, do którego launcher odwołuje się jako do kontrolowanego runtime'u Okapi.

Skopiowano runtime z V3:

/home/frs/Projekty/agent-translator-v4/filtry/runtime

Stan po kopiowaniu: 42 pliki, około 22 MiB.

Źródłowy artefakt V3 pozostaje nietknięty.

## Python package

Próba budowy wheel przez python -m build --wheel --no-isolation zakończyła się błędem przed utworzeniem artefaktu. setuptools podczas generowania metadanych próbuje wykonać introspekcję Git i trafia na:

fatal: detected dubious ownership in repository at '/home/frs/Projekty'

Nie zmieniano globalnej konfiguracji Git.

## Apertium

Audyt wykazał, że prywatny runtime Apertium 3.9.12 zawiera silnik, ale nie zawiera skompilowanej pary eng-pol. Dostępny katalog danych Apertium w środowisku użytkownika zawiera źródła i pliki konfiguracji, lecz brak wymaganych artefaktów .bin dla pary.

Rozpoczęto próbę zbudowania danych Apertium z kopii źródeł V3 do stagingu /tmp. Operacja została zatrzymana z powodu błędu uprawnień przy czyszczeniu kopii roboczej. V3 nie był modyfikowany.

## Stan kryterium

Kryterium Fazy 11:

artefakt V4 działa bez drzewa źródłowego V3 i bez lokalnych zasobów deweloperskich.

NIESPEŁNIONE.

Nie oznaczono punktów Fazy 11 jako zakończonych bez końcowej weryfikacji.

## Następny krok

Po usunięciu blokady środowiska budowania należy wznowić od dependency closure, następnie domknąć licencje/NOTICE, Python package, Linux/Windows, clean environment i smoke test artefaktu.


## Wynik ponowienia z `./temp`

Staging przeniesiono do lokalnego `./temp`, ponieważ środowisko użytkownika nie pozwala na zapis poza drzewem `Projekty`.

### Artefakt Linux

Zbudowano:

`temp/wheel/tlumacz-0.40.0-py3-none-any.whl`

Rozmiar: około 43 MiB.

Wheel zawiera:
- kod Python V4;
- Okapi runtime;
- Java Filter Host;
- prywatny runtime Apertium;
- NOTICE i 7 plików licencyjnych w metadanych dystrybucji.

### Weryfikacja

- pełny pytest: **182 passed**;
- Ruff: **PASS**;
- mypy: **PASS**, 60 plików;
- clean install z wheel: **PASS**;
- `tlumacz --version`: **0.40.0**;
- Java Filter Host z wheel: **PASS**;
- Apertium engine: **3.9.12**, **PASS**;
- Apertium language pairs w bundlowanym runtime: **brak**.

### Apertium blocker

Para `eng-pol` ma część skompilowanych artefaktów, ale brakuje `eng-pol.t1x.bin`. Próba przebudowania z materiałów V3 kończy się:

`Undefined attr-item cas_sp.`

Nie zmieniano V3 i nie wygenerowano sztucznego binarium.

### Windows blocker

Bundlowany runtime Apertium jest ELF x86-64. W V4 nie znaleziono odpowiadających natywnych artefaktów Windows (`.exe`/`.dll`) dla tego runtime'u.

### Stan końcowy

Faza 11 jest **częściowo wykonana, ale niezamknięta**. Kryterium release bez zależności od lokalnych zasobów deweloperskich nie jest jeszcze spełnione dla kompletnego Apertium i Windows.
