# Specyfikacja paczki językowej Apertium

## 1. Format pliku

Pojedyncza paczka językowa:

```text
apertium-<source>-<target>-<version>.tar
```

Przykład:

```text
apertium-eng-pol-1.0.0.tar
```

Wymagania:
- format POSIX TAR,
- bez kompresji,
- jedna paczka = dokładnie jeden kierunek tłumaczenia,
- paczka jest samowystarczalnym artefaktem instalacyjnym,
- rozszerzenie `.tar` jest częścią kontraktu.

## 2. Struktura archiwum

```text
apertium-eng-pol-1.0.0.tar
└── apertium-eng-pol/
    ├── manifest.json
    ├── checksums.json
    ├── COPYING
    ├── modes.xml
    ├── modes/
    │   └── eng-pol.mode
    ├── eng-pol.automorf.bin
    ├── eng-pol.autobil.bin
    ├── eng-pol.autogen.bin
    ├── eng-pol.prob
    ├── eng-pol.t1x.bin
    ├── eng-pol.t2x.bin
    ├── eng-pol.t3x.bin
    └── ...
```

Katalog główny musi odpowiadać identyfikatorowi pakietu.

## 3. manifest.json

Minimalny kontrakt:

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

`source_language` i `target_language` to identyfikatory używane przez Tłumacza. `apertium_source` i `apertium_target` to identyfikatory Apertium.

Przykład:

```text
Tłumacz:   en → pl
Apertium:  eng → pol
```

## 4. checksums.json

Kontrola integralności plików wewnątrz paczki:

```json
{
  "algorithm": "sha256",
  "files": {
    "COPYING": "...",
    "modes.xml": "...",
    "modes/eng-pol.mode": "...",
    "eng-pol.automorf.bin": "...",
    "eng-pol.autobil.bin": "...",
    "eng-pol.autogen.bin": "...",
    "eng-pol.t1x.bin": "...",
    "eng-pol.t2x.bin": "...",
    "eng-pol.t3x.bin": "..."
  }
}
```

## 5. Licencja

Każda paczka musi zawierać `COPYING` albo odpowiedni plik licencyjny wynikający z rzeczywistej licencji danych.

**Licencji nie wolno zgadywać.**

Jeżeli licencji nie można jednoznacznie ustalić, paczka nie powinna zostać oznaczona jako publikowalna.

## 6. modes.xml

Paczka zawiera tylko mode dotyczący własnej pary. Nie może przypadkowo zawierać innych kierunków.

Przykład:

```xml
<mode name="eng-pol">
    ...
</mode>
```

## 7. modes/eng-pol.mode

Mode musi być przenośny. Nie może zawierać ścieżek absolutnych z maszyny budującej, np. `/home/frs/Projekty/tlumacz-v4/...`.

Ścieżki powinny być względne i zgodne z układem instalowanego runtime.

Paczka:

```text
pobierz → zweryfikuj → przygotuj do użycia
```

musi działać na innym komputerze.

## Aktualne zasady przechowywania

Artefakt .tar jest właściwą i jedyną trwałą postacią paczki w magazynie użytkownika. Paczka nie jest przechowywana jako rozpakowany katalog. Jeżeli runtime Apertium wymaga fizycznych plików, aplikacja materializuje zawartość TAR wyłącznie w tymczasowym katalogu roboczym poza magazynem.

## 8. Instalacja

Po pobraniu programu paczka jest obsługiwana w kolejności:

```text
1. odczyt paczki
2. sprawdzenie manifest.json
3. sprawdzenie struktury
4. sprawdzenie SHA-256
5. sprawdzenie licencji
6. pozostawienie TAR jako artefaktu magazynu
7. tymczasowa materializacja do katalogu roboczego runtime'u, jeżeli wymaga tego Apertium
8. discovery
9. rejestracja pary
```

Docelowy magazyn:

```text
$HOME/.config/tlumacz/apertium/
├── apertium-eng-pol-1.0.0.tar
├── apertium-eng-pol-1.0.0.tar.sha256
└── ...
```

Rozpakowana postać nie jest częścią trwałego magazynu. Jest tworzona w katalogu tymczasowym poza magazynem, wyłącznie na potrzeby procesu Apertium.

## 9. Walidacja przed instalacją

Paczka jest odrzucana, jeżeli:
- archiwum jest uszkodzone,
- manifest jest niepoprawny,
- brakuje wymaganych plików,
- checksum się nie zgadza,
- mode wskazuje nieistniejące pliki,
- mode zawiera niedozwolone ścieżki absolutne,
- identyfikator pary nie zgadza się z nazwą paczki,
- paczka zawiera więcej niż jedną parę,
- brakuje wymaganej licencji.

## 10. Zewnętrzny plik .tar.sha256

Obok paczki:

```text
apertium-eng-pol-1.0.0.tar
apertium-eng-pol-1.0.0.tar.sha256
```

Plik zawiera SHA-256 całego artefaktu TAR.

Dostępne są dwa poziomy kontroli:

```text
TAR
 │
 ├── SHA-256 całego TAR
 │
 └── checksums.json
       └── SHA-256 poszczególnych plików
```

## 11. Wersjonowanie

Nazwa:

```text
apertium-eng-pol-1.0.0.tar
```

oznacza:
- `apertium-eng-pol` — identyfikator paczki,
- `1.0.0` — wersja paczki,
- `.tar` — format.

Zmiana danych lub binariów może powodować zmianę wersji, np. `1.0.0 → 1.0.1`.

Zmiana kontraktu paczki:

```text
1.x → 2.x
```

## 12. Model architektoniczny

Paczka nie jest archiwum całego Apertium. Jest pojedynczym pluginem kierunku tłumaczenia:

```text
                    TŁUMACZ
                       │
                    Apertium
                       │
          ┌────────────┼────────────┐
          │            │            │
      eng-pol       eng-spa      pol-eng
       plugin        plugin       plugin
          │            │            │
       1 TAR          1 TAR        1 TAR
```

Każdy kierunek można niezależnie:

```text
pobrać
  ↓
zweryfikować
  ↓
zainstalować
  ↓
wykryć przez discovery
  ↓
użyć
```

## 13. Docelowy mechanizm dystrybucji

```text
brak wymaganej pary
        │
        ▼
znajdź paczkę
        │
        ▼
pobierz pojedynczy TAR
        │
        ▼
zweryfikuj SHA-256 TAR
        │
        ▼
zweryfikuj zawartość paczki
        │
        ▼
zainstaluj plugin
        │
        ▼
discovery
        │
        ▼
para dostępna dla Tłumacza
```

Paczki są niezależnymi artefaktami i nie powinny wymagać pobierania całego zestawu Apertium.

## 14. Status specyfikacji

Dokument definiuje docelowy kontrakt pojedynczej paczki językowej Apertium dla projektu Tłumacz.

Implementacja automatycznego pobierania paczek przez aplikację jest odrębnym zadaniem i nie wynika automatycznie z samego istnienia paczek TAR.
