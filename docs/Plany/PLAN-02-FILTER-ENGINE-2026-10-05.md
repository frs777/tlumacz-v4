---
id: plan-02-filter-engine-2026-10-05
status: active
meta:
  contentType: ModuleImplementationPlan
  category: plans
version: 1.0.0
updated: 2026-10-05
owner: platform-architecture
priority: P0
depends_on: [docs/Plany/PLAN-2026-10-05.md]
last_validation: "audyt 2026-10-05"
---
# PLAN-02 — Filter Engine i dokumenty

## 1. Oczekiwany rezultat
Zapewnić niezawodne extract → translate → merge dla DOCX, ODT, HTML/XHTML, Markdown, EPUB i XLIFF oraz jasny status TXT/PDF.

## 2. Zakres odpowiedzialności
FilterRegistry; FilterSession; FilterHost; format-specific filters; inline codes; marker protection; round-trip/fingerprint; Java runtime Okapi; workspace/timeout/cancel.

## 3. Schemat budowy
```text
```text
Input file
  ↓
FilterRegistry
  ↓
FilterSession / workspace
  ↓
Filter / FilterHost
  ↓
TranslationUnit[] + inline codes
  ↓
backend
  ↓
validated targets
  ↓
merge/write
```
```

## 4. Połączenia z innymi modułami
Rdzeń konsumuje TranslationUnit. Backend nie dotyka dokumentu. Packaging dostarcza FilterHost/runtime.

## 5. Szczegółowy plan wdrożenia
1. Zachować charakterystykę markerów.
2. Zweryfikować protection/restore na każdym aktywnym filtrze.
3. Dodać realne round-trip corpus.
4. Zweryfikować timeout/cancel hosta.
5. Zdefiniować fingerprint struktury.
6. Zamknąć licencje minimalnego runtime Okapi.
7. Ustalić status TXT/PDF.
8. Dodać release smoke każdego aktywnego formatu.

## 6. Wymagania i zależności
Dokument jest niezaufanym wejściem. Workspace musi być izolowany. Nie wykonywać makr/aktywnej zawartości. Nie dodawać ZIP extraction poza odpowiedzialnością właściwego filtra.

## 7. Szczegóły integracji
Protocol FilterHost ↔ Python pozostaje wersjonowany JSON Lines. Engine jest jedynym właścicielem lifecycle sesji. Warstwa Java udostępnia minimalne operacje hello, version, health, capabilities, extract, merge oraz lifecycle diagnostyczny. Parametry operacji są transportowane w polu payload; kompatybilność legacy pozostaje po stronie hosta. extract i merge są rozdzielone, aby Python mógł wykonać translację pomiędzy etapami bez przetrzymywania zdarzeń Okapi w JVM. W przypadku błędu markerów lub niespójności targetów pipeline ma zakończyć się błędem, nie cichym uszkodzeniem. XLIFF automatycznie wybiera XLIFFFilter dla 1.2 i XLIFF2Filter dla 2.x. Powtarzające się ID TextUnit otrzymują stabilne ID sesyjne (id::N) z zachowaniem mapowania podczas merge.

## 8. Exit gate
Każdy aktywny format ma corpus, extract/merge/round-trip, Unicode i inline-code tests; host nie zostawia procesu; marker counts przed/po są zgodne.

## 9. Zasady
Nie zmieniać innych modułów tylko po to, aby uprościć implementację tego modułu. Każda zmiana kontraktu wymaga aktualizacji testów, dokumentacji i głównego PLAN-2026-10-05.md.