---
id: docs-policy
status: active
meta:
  contentType: Reference
  category: governance
version: 0.31.2
updated: 2026-09-26
owner: project-documentation
source: AGENTS.md
depends_on: [docs/INDEX.yml]
expires_when: zmiana polityki dokumentacji projektu
last_validation: "przegląd raportu audytowego 2026-09-26"
---

# Polityka dokumentacji projektu

Ten katalog jest kontrolowanym źródłem dokumentacji projektu Tłumacz V4. Reguły z tego pliku są bardziej restrykcyjne niż ogólne reguły repozytorium.

## Podział dokumentacji

Używaj następujących kategorii logicznych:

- `governance`: `STATUS.md`, `TODO.md`, `BUG.md` i dokumenty zarządzające
- `technical`: dokumentacja rzeczywistej implementacji w `technical-docs/`
- `plans`: plany wdrożeń i decyzje jeszcze niewdrożone
- `research`: badania, porównania i hipotezy
- `release`: budowanie, pakietowanie i instrukcje wydaniowe
- `audit`: audyty i ich wyniki
- `evidence`: wyniki testów, benchmarki i dowody wykonania
- `archive`: dokumenty historyczne lub zastąpione

Istniejących plików nie przenoś masowo tylko w celu uporządkowania nazw. Nowy dokument zapisuj w docelowej kategorii. Migrację starszego pliku wykonuj przy jego najbliższej istotnej edycji.

## Obowiązkowe metadane

Każdy nowy dokument oraz każdy istotnie zmieniany dokument Markdown musi mieć YAML front matter:

```yaml
---
id: unikalny-slug
status: active
meta:
  contentType: Reference
  category: technical
version: 0.31.2
updated: 2026-09-26
owner: module-or-role
source: tlumacz/path.py
depends_on: []
expires_when: opis-warunku
last_validation: "komenda + wynik + data"
---
```

Dozwolone wartości `status`:

- `active`
- `plan`
- `research`
- `historical`
- `superseded`
- `evidence` — materiał testowy lub dowodowy
- `backup` — kopia techniczna, nie źródło prawdy

Dla dokumentów historycznych nie zmieniaj treści tylko po to, aby spełnić nowe metadane. Zarejestruj ich status w `INDEX.yml` i dodaj metadane przy następnej merytorycznej migracji.

## Polityka zapisu

Przed zapisem sprawdź:

1. czy dokument ma jednoznaczny zakres i właściciela;
2. czy istnieje już dokument pełniący tę samą funkcję;
3. czy informacja nie należy do `STATUS.md`, `TODO.md`, `BUG.md` albo `CHANGELOG.md`;
4. czy dokument ma poprawny status i datę aktualizacji;
5. czy opis implementacji wskazuje rzeczywisty kod lub test;
6. czy wynik testu zawiera datę i dokładną komendę;
7. czy dokument nie zawiera sekretów, kluczy API, tokenów ani pełnych danych użytkownika;
8. czy dokument nie zapisuje treści tłumaczonych dokumentów, jeżeli wystarczy metadana diagnostyczna;
9. czy dokument nie kopiuje istniejącego planu lub audytu.

Nie zapisuj automatycznie logów, benchmarków, dumpów, kopii dokumentów ani artefaktów build do kontrolowanej dokumentacji. Takie materiały trafiają do wydzielonego obszaru roboczego lub artefaktów lokalnych.

## Źródła prawdy

- `README.md`: wejście użytkownika i opis produktu
- `docs/STATUS.md`: wyłącznie stan bieżący
- `docs/TODO.md`: wyłącznie aktywne zadania
- `docs/BUG.md`: wyłącznie aktywne defekty i ryzyka
- `CHANGELOG.md`: historia zmian
- `docs/technical-docs/`: aktualny opis implementacji
- `docs/INDEX.md`: indeks dla człowieka
- `docs/INDEX.yml`: indeks maszynowy i rejestr statusów
- `docs/archive/`: materiał historyczny i zastąpiony

Jeżeli źródło kodu, test lub dokument nadrzędny przeczy starszemu dokumentowi, starszy dokument nie jest źródłem prawdy.

## Aktualizacja dokumentacji po zmianie kodu

Zmiana kodu nie jest zakończona bez aktualizacji właściwej dokumentacji. Aktualizacja musi obejmować:

- opis zmiany w dokumentacji technicznej, jeśli zmienił się kontrakt;
- `STATUS.md`, jeśli zmienił się stan projektu;
- `TODO.md` lub `BUG.md`, jeśli zmienił się status zadania albo defektu;
- `CHANGELOG.md`, jeśli zmiana jest istotna dla wydania;
- `INDEX.yml`, jeśli zmieniono status, zakres lub źródło dokumentu.

## Polecenia do wykonania

- zawsze sparawdzaj folder _index i rozmieść jego zawartość w odpowiednich folderach oraz wprowadź zapis do indeksów.
- zawsze kasuj pliki .bak 
- po każdej operacji, która mogła wygenerować `*.bak*`, uruchamiaj `./tools/cleanup-bak.sh .`; skrypt usuwa wyłącznie regenerowalne pliki `*.bak*` i nie narusza archiwów `backups/` ani `.migration-backups/`.
- sparawdzaj aktualnosść dokumentacji 

Przed zamknięciem pracy wykonaj kontrolę linków, sprawdź metadane i uruchom właściwe testy dokumentacyjne, jeżeli istnieją.
