---
id: migration-inventory-v3-v4
status: historical
meta:
  contentType: MigrationInventory
  category: migration
version: 0.40.0
updated: 2026-09-30
owner: platform-architecture
source: /home/frs/Projekty/agent-translator-v3
depends_on:
  - docs/PLAN_MIGRACJI-v4.md
expires_when: zakończenie migracji V3 → V4
---

# STATUS DOKUMENTU: HISTORYCZNY

> Ten inventory jest zapisem decyzji migracyjnych V3 → V4. Nie jest źródłem bieżącej architektury. Aktywny stan znajduje się w `docs/STATUS.md`, `docs/ARCHITECTURE.md` i dokumentacji technicznej. FastAPI/OpenVINO są wycofane z aktywnego runtime V4.

# V3 → V4 — inventory baseline

## Referencja

- V3: `/home/frs/Projekty/agent-translator-v3`
- V4: `/home/frs/Projekty/tlumacz-v4`
- Plan SHA-256: `537fce739d9c0ffc375fc01940201b1e8cd8fb43211c71aa4c0e445134d6c41d`

## Integralność V3

V3 jest traktowany wyłącznie jako źródło referencyjne. W Fazie 0 nie wykonano zmian w V3. Stan `git status --porcelain=v1` przed i po inwentaryzacji pozostał identyczny.

Do operacji odczytu Git użyto jednorazowego `git -c safe.directory=/home/frs/Projekty/agent-translator-v3`. Globalna konfiguracja Git nie została zmieniona.

## Stan Git V3

- tracked files: 181
- untracked entries: 75
- modified/deleted tracked entries: 62
- Python files in working tree: 799
- test files matching `tests/**/test_*.py`: 37

## Źródła V3 → decyzja V4

| Obszar V3 | Stan baseline | Decyzja V4 |
|---|---|---|
| `tlumacz.qt_gui.app:main` / entrypoint | obecny entrypoint GUI; brak docelowego composition root | odbudować jako composition root |
| `tlumacz/core.py` / `Translator` | duży rdzeń aplikacyjny | rozbić na application services zgodnie z planem |
| `tlumacz/qt_gui/main_window.py` | duża granica UI | rozbić na kontrolery |
| `tlumacz/qt_gui/backend_manager.py` | backend management sprzężony z GUI | zastąpić registry + backend modules |
| `tlumacz/backends/` | lokalny, nieśledzony przez Git | zweryfikować i selektywnie odtworzyć w V4 |
| `tlumacz/filter_engine/` | lokalny, nieśledzony przez Git | odbudować/zweryfikować według kontraktu V4 |
| `java/` | lokalny, nieśledzony przez Git | migrować po ustaleniu Java Filter Host contract |
| `filtry/` | lokalny, nieśledzony przez Git | migrować selektywnie + dependency closure |
| Apertium runtime | lokalne artefakty/runtime obecne | zweryfikować runtime, ABI, dane i licencje; następnie bundlować |
| Cloud/Mozhi | istnieją stare i nowe ścieżki | CloudRouter + provider interface; Mozhi jako provider |
| FastAPI | kod/testy/dependencies obecne | nie migrować; usunąć dopiero po przejęciu wymaganych funkcji |
| OpenVINO | kod/testy/dependencies obecne | nie migrować; usunąć dopiero po przejęciu wymaganych funkcji |
| Markdown/HTML/DOCX/ODT/EPUB/XLIFF | częściowo rozproszone implementacje | przepisać pod Document/Filter contracts i round-trip tests |
| PDF | osobny pipeline | zachować jako niezależny pipeline |
| testy | 37 nazwanych plików testowych + lokalne dodatki | selektywnie migrować, rozszerzyć contract/regression/E2E |
| packaging | V3 metadata + lokalne runtime'y | zaprojektować od zera dla V4 |
| konfiguracja | kilka lokalnych ścieżek konfiguracji | V3 → ConfigMigration → V4; backup + idempotencja |
| dokumentacja | rozbudowana, częściowo zmodyfikowana/untracked | przepisać tylko aktualne źródła prawdy; archiwum nie jest wymaganiem |

## Krytyczny wynik baseline testów

Komenda:

`python -m pytest -q`

Wynik: **FAIL podczas collection**.

- 16 modułów testowych zakończyło collection błędem.
- Bezpośrednią przyczyną jest `ModuleNotFoundError: No module named 'lingua'`.
- Pełny suite nie doszedł do wykonania testów.
- Nie instalowano żadnej zależności podczas baseline.

Ten wynik jest baseline V3, a nie defektem wprowadzonym przez migrację.

## Zasada dalszej migracji

Nie kopiować całego V3. Każdy element otrzymuje decyzję: `migrate`, `rebuild`, `replace`, `drop` albo `verify-first`, wraz z testem/kontraktem.

## Istniejący stan V4 przed tą sesją

Katalog `/home/frs/Projekty/tlumacz-v4/` istniał już przed rozpoczęciem bieżącej sesji i zawierał cztery pliki backup planu. Nie zostały usunięte ani uznane za źródło prawdy. Aktywny `docs/PLAN_MIGRACJI-v4.md` został zweryfikowany jako dokładna kopia planu V3 na podstawie SHA-256.
