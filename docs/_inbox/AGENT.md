# AGENT.md — zasady pracy w `docs/_inbox/`

## Cel

`docs/_inbox/` jest tymczasową strefą przyjmowania nowych materiałów dokumentacyjnych projektu Tłumacz.

Materiały znajdujące się tutaj **nie są dokumentacją kanoniczną** do czasu ich przeglądu i segregacji.

## Zasady

1. Nowe raporty, notatki, wyniki audytów, materiały diagnostyczne i inne dokumenty robocze można umieszczać w tym katalogu.
2. Przy porządkowaniu każdego materiału należy:
   - przeczytać jego treść,
   - określić jego zakres i znaczenie dla V4,
   - sprawdzić duplikaty i nakładanie się treści z istniejącą dokumentacją,
   - określić właściwy status dokumentu,
   - zdecydować, czy dokument należy przenieść do właściwej części `docs/`, pozostawić jako materiał badawczy, czy wykorzystać jego informacje do aktualizacji istniejącej dokumentacji.
3. Po segregacji należy odpowiednio zaktualizować:
   - `docs/INDEX.yml`,
   - `docs/INDEX.md`,
   - `docs/DOCUMENTATION_CHANGELOG.md`.
4. Nie kopiować dokumentacji z V3 do V4. V3 może być używany wyłącznie jako źródło porównawcze lub historyczne.
5. Przed usunięciem dokumentu należy potwierdzić, że jest duplikatem, materiałem zbędnym albo że jego treść została bezpiecznie zachowana w dokumentacji kanonicznej. Nie usuwać materiałów bez podstawy.
6. Pliki `.bak.*` są kopiami bezpieczeństwa i nie powinny być traktowane jako normalne dokumenty inboxu.
7. Materiał dotyczący wycofanej funkcjonalności należy oznaczyć jako historyczny lub superseded zgodnie z rzeczywistym stanem projektu.
8. Nie należy uznawać hipotez diagnostycznych za potwierdzone fakty. Raporty powinny zachować rozróżnienie między obserwacją, dowodem, hipotezą i wnioskiem.
9. Dokumentacja musi używać aktualnej terminologii projektu. W szczególności **TranslateGemma INT8 jest modelem/wariantem modelu, a nie backendem**.
10. Po zmianach w kodzie lub zachowaniu aplikacji należy odpowiednio zaktualizować dokumentację.
11. Po każdym zapisie dokumentacji należy sprawdzić rekursywnie docs/ pod kątem nowych plików .bak.*, .bak, ~ i .backup*. Nie wolno pozostawić takich artefaktów bez świadomej decyzji.

## Docelowy przepływ

```
docs/_inbox/
      ↓
przegląd i deduplikacja
      ↓
klasyfikacja
      ↓
integracja / przeniesienie / archiwizacja
      ↓
aktualizacja INDEX.yml + INDEX.md + DOCUMENTATION_CHANGELOG.md
```

## Zasada nadrzędna

Inbox jest miejscem roboczym. **Nie należy traktować znajdujących się w nim dokumentów jako źródła prawdy bez wcześniejszego przeglądu i klasyfikacji.**

