# Ręczne tworzenie paczek językowych Apertium

## Cel

Ten dokument opisuje ręczne przygotowanie pojedynczej paczki Apertium dla Tłumacza. Paczka jest osobnym pluginem jednego kierunku tłumaczenia i ma postać niekompresowanego POSIX TAR.

Pełny kontrakt paczki znajduje się w `paczki-jezykowe-specyfikacja.md`.

## 1. Przygotuj kompletne artefakty pary

Potrzebne są artefakty wynikowe jednego kierunku, właściwy `modes.xml`, właściwy plik `.mode` oraz rzeczywisty plik licencyjny.

Przykładowy układ roboczy:

```text
apertium-eng-pol/
├── manifest.json
├── checksums.json
├── COPYING
├── modes.xml
├── modes/
│   └── eng-pol.mode
└── eng-pol.*
```

Nie należy dodawać artefaktów drugiego kierunku ani nieużywanych plików.

## 2. Przygotuj manifest

Dla `eng-pol`:

```json
{
  "schema_version": 1,
  "package_id": "apertium-eng-pol",
  "version": "1.0.0",
  "source_language": "en",
  "target_language": "pl",
  "apertium_source": "eng",
  "apertium_target": "pol",
  "pair": "eng-pol",
  "backend": "apertium",
  "format": "tar",
  "compression": "none"
}
```

Identyfikatory muszą odpowiadać rzeczywistej parze.

## 3. Ogranicz modes.xml do jednej pary

`modes.xml` musi opisywać wyłącznie `eng-pol`. Sprawdź również, czy mode odwołuje się wyłącznie do plików obecnych w paczce.

## 4. Usuń ścieżki absolutne

Plik `modes/eng-pol.mode` nie może zawierać ścieżek zależnych od maszyny budującej. Wszystkie odwołania powinny być przenośne i zgodne z docelowym układem instalacji.

Kontrola:

```bash
grep -R -nE '(^|[ =])/(home|tmp|opt|usr|var)/' apertium-eng-pol/
```

Brak wyniku jest oczekiwany dla ścieżek absolutnych tego typu.

## 5. Wygeneruj checksumy wewnętrzne

Po ostatecznym przygotowaniu zawartości wygeneruj SHA-256 dla każdego pliku wymienionego w `checksums.json`. Nie uwzględniaj samego `checksums.json` przed jego zapisaniem; po wygenerowaniu checksumów nie zmieniaj już plików objętych sumami.

## 6. Zbuduj TAR

Z katalogu roboczego:

```bash
tar -cf apertium-eng-pol-1.0.0.tar apertium-eng-pol/
```

Paczka nie jest kompresowana.

## 7. Wygeneruj sumę całego TAR

```bash
sha256sum apertium-eng-pol-1.0.0.tar > apertium-eng-pol-1.0.0.tar.sha256
```

## 8. Kontrola zawartości

```bash
tar -tf apertium-eng-pol-1.0.0.tar
sha256sum -c apertium-eng-pol-1.0.0.tar.sha256
```

Następnie rozpakuj paczkę do pustego katalogu i zweryfikuj `manifest.json`, `checksums.json`, licencję, `modes.xml` oraz `.mode`.

## 9. Instalacja testowa

Paczka musi zostać przetestowana przez rzeczywisty instalator Tłumacza w czystym magazynie, a następnie przez discovery. Sam poprawny wynik `tar` lub `sha256sum` nie dowodzi poprawności instalacji.

Minimalny przepływ kontroli:

```text
TAR
 ↓
SHA-256 całego TAR
 ↓
walidacja manifestu i struktury
 ↓
walidacja checksum wewnętrznych
 ↓
instalacja do pustego magazynu
 ↓
discovery
 ↓
oczekiwana para dostępna
```

## 10. Automatyczne narzędzia a ręczne tworzenie

W projekcie istnieje narzędzie pomocnicze `tools/apertium/package_pairs.py`, które automatyzuje pobieranie źródeł, kompilację, wykrywanie kompletnych kierunków i tworzenie paczek.

`tools/apertium/package_pipeline.py` zawiera współdzieloną logikę tego procesu.

Oba pliki są narzędziami wewnętrznymi i **nie należą do runtime aplikacji**. Nie powinny być importowane przez kod `src/tlumacz/`.

Ręczne tworzenie jest procedurą awaryjną, kontrolną lub przydatną przy przygotowywaniu pojedynczego artefaktu; preferowaną metodą seryjnego budowania jest narzędzie z `tools/apertium/`.
