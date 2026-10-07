---
id: i18n-scope-v4
status: active
meta:
  contentType: Reference
  category: governance
version: 1.0.0
updated: 2026-10-07
owner: project-documentation
source: docs/I18N_SCOPE.md
depends_on: [docs/I18N.md, docs/INDEX.md, docs/INDEX.yml]
expires_when: zmiana zakresu dokumentacji produktu lub polityki lokalizacji
last_validation: "audyt zakresu lokalizacji i wyjątku Apertium 2026-10-07"
---

# Zakres lokalizacji — Tłumacz V4

## Cel

Ten plik jest **kanoniczną listą zakresu tłumaczeń dokumentacji**. Ma zapobiegać tłumaczeniu plików roboczych, raportów, logów, artefaktów testowych i innych materiałów, które nie są dokumentacją produktu.

Zasada nadrzędna:

> **Jeżeli dokument nie jest wymieniony w sekcji „Tłumaczyć”, nie tłumaczyć go bez osobnej decyzji.**

Językiem źródłowym projektu pozostaje **PL**. Lokalizacje dokumentacji użytkowej i technicznej są prowadzone w **EN** i **DE**.

## 1. Tłumaczyć — dokumentacja podstawowa projektu

### Pliki główne projektu

| Dokument źródłowy | EN | DE | Zakres |
|---|---|---|---|
| README.md | README_en.md | README_de.md | opis projektu, uruchomienie, podstawowe informacje |
| docs/STATUS.md | docs/en/status.md | docs/de/status.md | aktualny stan projektu |
| docs/CHANGELOG.md | docs/en/changelog.md | docs/de/changelog.md | publiczna historia zmian |
| docs/DEVELOPMENT.md | docs/en/development.md | docs/de/development.md | zasady i informacje dla dewelopera |
| docs/ARCHITECTURE.md | docs/en/architecture.md | docs/de/architecture.md | architektura aktywnego V4 |
| docs/RELEASE_NOTES_*.md | odpowiednik EN | odpowiednik DE | informacje o wydaniach przeznaczone dla użytkownika |

### Rejestry funkcjonalne przydatne użytkownikowi/deweloperowi

Tłumaczyć tylko wtedy, gdy dokument opisuje **aktualną funkcjonalność V4**, a nie historię migracji:

- docs/RETIRED_FUNCTIONALITY.md
- docs/archive/reference/STRUKTURA_V4.md
- docs/archive/legacy/windows/windows.md
- docs/archive/legacy/windows/windows-kompilacja.md
- inne aktualne dokumenty instruktażowe wskazane później jako kanoniczne.

## 2. Tłumaczyć — aktywna dokumentacja techniczna

Cały katalog docs/technical-docs/ podlega lokalizacji **EN + DE**, jeżeli dokument opisuje aktualną implementację V4.

Dotyczy to w szczególności:

- index.md
- user-guide.md
- models.md
- server-management.md
- cloud-translation.md
- xliff-pipeline.md
- apertium-backend-integration.md
- windows-exe-build.md

### Wyjątek: dokumentacja historyczna/research

Pliki techniczne oznaczone jako historyczne, research lub dotyczące nieaktywnej architektury nie są automatycznie tłumaczone.

Obecnie poza zakresem pozostają:

- docs/technical-docs/TRANSLATEGEMMA_GOOGLE_CLOUD.md
- docs/technical-docs/TRANSLATEGEMMA_ONNX_DESKTOP_GUIDE.md
- docs/technical-docs/TRANSLATEGEMMA_OPENVINO_AMD_GUIDE.md

Jeżeli taki dokument stanie się ponownie obowiązującą dokumentacją V4, zakres należy zmienić tutaj przed rozpoczęciem tłumaczenia.

## 3. Tłumaczyć — pomoc użytkownika i interfejs

Lokalizacji podlegają wszystkie teksty widoczne bezpośrednio dla użytkownika:

- GUI QML;
- etykiety, przyciski i zakładki;
- komunikaty statusu;
- skrócone logi użytkownika;
- dialogi wyboru plików;
- pomoc użytkownika;
- teksty wyjaśniające funkcje dostępne w GUI.

Źródła lokalizacji:

- src/tlumacz/i18n.py
- src/tlumacz/qml_gui/
- src/tlumacz/qml_gui/help.pl.md
- src/tlumacz/qml_gui/help.en.md
- src/tlumacz/qml_gui/help.de.md

Języki GUI: **PL / EN / DE**.

Surowe komunikaty techniczne wyjątków backendów nie są automatycznie tłumaczone tylko dlatego, że są wyświetlane jako szczegóły błędu.

## 4. Nie tłumaczyć — pliki robocze

Następujące materiały **nie podlegają automatycznej lokalizacji**:

### Raporty i audyty robocze

- docs/Audyt/
- docs/reports/
- docs/Testy/
- docs/_inbox/
- docs/reserge/
- docs/superpowers/
- docs/Plany/

Dotyczy to również raportów jednorazowych, raportów faz, wyników audytów, handoffów i planów wykonawczych.

### Artefakty testowe i dane

Nie tłumaczyć:

- plików .log;
- plików .jsonl;
- plików wynikowych testów;
- snapshotów i baseline'ów;
- zrzutów ekranu;
- plików PDF/ODT/XML używanych jako materiały robocze;
- danych benchmarkowych;
- wyników eksperymentów;
- plików generowanych automatycznie.

### Pliki indeksujące i administracyjne

Nie tworzyć automatycznie odpowiedników językowych dla:

- docs/INDEX.md
- docs/INDEX.yml
- docs/DOCUMENTATION_CHANGELOG.md
- docs/I18N.md
- docs/I18N_STATUS.md
- docs/I18N_SCOPE.md
- docs/AGENTS.md

Są to dokumenty zarządzania projektem i pozostają w języku źródłowym.

## 5. Nie tłumaczyć — historia migracji i archiwum

Nie tłumaczyć automatycznie:

- docs/archive/
- dokumentów V3;
- baseline'ów V3;
- raportów migracji;
- dokumentów oznaczonych historical;
- dokumentów oznaczonych superseded;
- dokumentów oznaczonych evidence;
- researchu, który nie jest częścią aktualnej dokumentacji V4.

Przykłady:

- docs/archive/migration/MIGRATION_INVENTORY.md
- docs/archive/migration/MIGRATION_NOTES_V3_TO_V4.md
- docs/archive/migration/Raport_koncowy_migracji_v3-v4.md
- docs/archive/reference/V3_GIT_STATUS_BASELINE.txt
- docs/archive/reference/index-v3.md
- docs/archive/reference/index-v3.tmol

## 6. Nie tłumaczyć — licencje i dokumenty prawne

Nie lokalizować:

- LICENSE
- licenses/
- tekstów licencyjnych zależności;
- oryginalnych dokumentów prawnych.

Oryginał licencji musi pozostać nienaruszony.

## 7. Dokumentacja techniczna a dokumentacja robocza

Przy kwalifikacji nowego pliku stosować tę regułę:

**Tłumaczyć**, jeżeli dokument odpowiada na pytanie:

> „Jak działa, jak używać albo jak rozwijać aktualny Tłumacz V4?”

**Nie tłumaczyć**, jeżeli dokument odpowiada na pytanie:

> „Co wykonaliśmy podczas konkretnego audytu, testu, migracji, eksperymentu albo naprawy?”

Przykład:

- docs/technical-docs/cloud-translation.md → **TAK**
- docs/reports/FAZA_5_CLOUD_ROUTER_2026-09-30.md → **NIE**

## 8. Zasada dla nowych dokumentów

Przed rozpoczęciem tłumaczenia nowego dokumentu:

1. sprawdzić docs/I18N_SCOPE.md;
2. określić, czy dokument jest podstawową dokumentacją produktu, aktywną dokumentacją techniczną czy materiałem roboczym;
3. jeśli nie ma jednoznacznej kwalifikacji — **nie tłumaczyć automatycznie**;
4. w razie potrzeby dodać dokument do tego pliku;
5. dopiero potem utworzyć EN/DE.

## 8a. Jawny wyjątek — 2026-10-07

Na podstawie osobnej decyzji użytkownika zlokalizowano dwa nowe dokumenty Apertium oznaczone `status: evidence`:

- `docs/technical-docs/apertium-pair-inventory-20261006.md`;
- `docs/technical-docs/apertium-pair-packages.md`.

Ten wyjątek dotyczy wyłącznie tych dwóch dokumentów i nie rozszerza automatycznie zakresu na inne materiały `evidence`.


## 9. Zasada synchronizacji

Dla dokumentów objętych zakresem:

1. PL jest źródłem prawdy;
2. EN i DE muszą zachować znaczenie techniczne;
3. nazwy plików, ścieżki, komendy, identyfikatory i nazwy klas pozostają niezmienione;
4. tłumaczenie nie może zmieniać statusu funkcji;
5. po zmianie dokumentacji aktualizuje się docs/INDEX.yml i docs/DOCUMENTATION_CHANGELOG.md;
6. nie tworzy się tłumaczeń plików wyłączonych z zakresu tylko po to, aby zwiększyć parytet liczby plików.

## 10. Stan początkowy — 2026-10-03

Zakres został ustalony po audycie struktury docs/.

Istniejące lokalizacje EN/DE, które wykraczają poza ten zakres, nie są automatycznie usuwane. Od tej chwili **nie należy ich rozszerzać ani tworzyć kolejnych odpowiedników**, chyba że dokument zostanie jawnie zakwalifikowany w tym pliku.

Ten dokument jest nadrzędną instrukcją planowania kolejnych fal lokalizacji.
