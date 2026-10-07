---
id: opis-programu-dla-agentow-root-history
status: superseded
meta:
  contentType: Reference
  category: archive
version: 1.0.0
updated: 2026-10-05
owner: project-documentation
source: root/OPIS_PROGRAMU_DLA_AGENTOW.md
depends_on: [docs/OPIS_PROGRAMU_DLA_AGENTOW.md]
expires_when: pełne usunięcie historycznej wersji opisu agentowego
last_validation: "wersja root przeniesiona jako materiał historyczny; źródłem aktualnym jest docs/OPIS_PROGRAMU_DLA_AGENTOW.md"
---

# Tłumacz V4 — opis programu dla agentów

## 1. Cel programu

**Tłumacz V4** jest aplikacją przeznaczoną do wykonywania i organizowania tłumaczeń tekstów oraz dokumentów.

Program został zaprojektowany tak, aby proces tłumaczenia był niezależny od konkretnego sposobu wykonywania tłumaczenia. Dokument jest przygotowywany, dzielony na odpowiednie fragmenty i kontrolowany niezależnie od tego, jaki mechanizm tłumaczący zostanie wykorzystany.

Najważniejszą zasadą programu jest rozdzielenie:
- dokumentu i jego struktury,
- procesu tłumaczenia,
- sposobu wykonywania tłumaczenia,
- kontroli poprawności wyniku,
- interfejsu użytkownika.

Dzięki temu agent pracujący z programem powinien myśleć przede wszystkim o **zadaniu tłumaczeniowym**, a nie o szczegółach jego technicznej realizacji.

**Szczegóły architektury:** `docs/ARCHITECTURE.md`  
**Historia i zakres migracji:** `docs/Raport_koncowy_migracji_v3-v4.md`

## 2. Główne zadanie programu

Typowy proces wygląda logicznie następująco:

**użytkownik wybiera dokument → program rozpoznaje dokument → przygotowuje jego treść do tłumaczenia → wykonuje tłumaczenie → kontroluje wynik → składa dokument ponownie → użytkownik otrzymuje przetłumaczony dokument.**

Program ma przy tym zachować elementy dokumentu, które nie powinny być tłumaczone, oraz strukturę dokumentu.

Agent nie powinien traktować tłumaczenia jako prostego:

> tekst wejściowy → tekst wyjściowy.

W przypadku dokumentów jest to proces:

> dokument → treść przeznaczona do tłumaczenia → tłumaczenie → ponowne umieszczenie treści w dokumencie.

## 3. Obsługa dokumentów

Jedną z podstawowych funkcji Tłumacza jest praca z dokumentami.

Program może pracować m.in. z:
- DOCX,
- ODT,
- HTML/XHTML,
- Markdown,
- EPUB,
- XLIFF.

Dokument jest traktowany jako całość, a nie tylko jako zwykły plik tekstowy.

Program musi zachować możliwie dużo informacji o strukturze dokumentu podczas procesu tłumaczenia.

Dotyczy to w szczególności:
- kolejności treści,
- struktury dokumentu,
- elementów, których nie należy tłumaczyć,
- znaczników i elementów specjalnych,
- poprawnego odtworzenia dokumentu po tłumaczeniu.

Agent powinien więc rozróżniać **treść przeznaczoną do tłumaczenia** od **struktury dokumentu**.

**Szczegółowe opisy obsługi dokumentów:**  
`docs/reports/FAZA_7_DOCUMENT_SERVICES_COMPLETE_2026-09-30.md`

## 4. Przygotowanie treści do tłumaczenia

Dokument może zawierać bardzo dużą ilość tekstu. Nie jest więc konieczne ani właściwe traktowanie całego dokumentu jako jednego zadania.

Program przygotowuje treść do tłumaczenia w postaci mniejszych jednostek.

Logika jest następująca:
1. program otrzymuje materiał do tłumaczenia,
2. określa jego jednostki,
3. grupuje je w odpowiednie fragmenty,
4. zachowuje kolejność,
5. przekazuje przygotowane fragmenty do procesu tłumaczenia.

Celem jest uzyskanie fragmentów, które można bezpiecznie i przewidywalnie przetłumaczyć.

Duża jednostka może pozostać większa od standardowego rozmiaru, jeżeli jej podział mógłby naruszyć sens lub strukturę materiału.

**Szczegóły:** `docs/reports/FAZA_8_CHUNK_PLANNER_2026-09-30.md`

## 5. Przygotowanie polecenia tłumaczeniowego

Przed wykonaniem tłumaczenia program przygotowuje instrukcję dla mechanizmu tłumaczącego.

Instrukcja określa m.in.:
- czego dotyczy zadanie,
- jaki jest język źródłowy,
- jaki jest język docelowy,
- jaki fragment należy przetłumaczyć,
- jakie zasady powinny być zachowane,
- jakie elementy wymagają szczególnego traktowania.

Ważne jest zachowanie kontekstu oraz kolejności informacji.

Dzięki temu mechanizm tłumaczący otrzymuje **jednoznaczne zadanie**, zamiast przypadkowego fragmentu tekstu pozbawionego informacji potrzebnych do prawidłowego tłumaczenia.

**Szczegóły:** `docs/reports/FAZA_8_PROMPT_BUILDER_2026-09-30.md`

## 6. Wykonywanie tłumaczenia

Za samo wykonanie tłumaczenia odpowiada wybrany backend.

Backend jest dla programu **wykonawcą tłumaczenia**.

Program nie powinien zakładać, że istnieje tylko jeden backend.

Obecny model logiczny przewiduje trzy główne rodzaje backendów:

### LlamaCpp

Backend przeznaczony do lokalnego wykonywania tłumaczeń przy wykorzystaniu lokalnego modelu.

### Cloud

Backend wykorzystujący zewnętrzne usługi tłumaczeniowe lub modele dostępne przez usługi sieciowe.

### Apertium

Backend oparty na regułowym systemie tłumaczenia maszynowego.

Istotne jest to, że wszystkie te mechanizmy wykonują **to samo zadanie logiczne**:

> otrzymać materiał do tłumaczenia i zwrócić wynik tłumaczenia.

Różnica polega na sposobie wykonania zadania.

**Szczegóły backendów:**  
`docs/MIGRATION_NOTES_V3_TO_V4.md`  
`docs/reports/FAZA_4_*`  
`docs/reports/FAZA_5_*`  
`docs/reports/FAZA_6_APERTIUM_ADAPTER_2026-09-30.md`

## 7. Wybór backendu

Agent nie powinien zakładać, że konkretny backend jest zawsze właściwy.

Wybór zależy od sytuacji, m.in.:
- dostępności backendu,
- obsługiwanej pary językowej,
- rodzaju zadania,
- wymagań dotyczących lokalnego lub zewnętrznego wykonania,
- dostępności odpowiednich zasobów.

Backend jest więc **wymiennym wykonawcą**, a nie częścią logiki dokumentu.

Przykładowo:

> dokument DOCX nie jest „dokumentem dla Apertium”.

Ten sam dokument może zostać przygotowany przez warstwę dokumentową, a następnie przekazany do różnych backendów.

## 8. Wykonywanie wielu fragmentów

Proces tłumaczenia może obejmować wiele fragmentów.

Program zarządza ich wykonaniem tak, aby:
- zachować kolejność wyników,
- umożliwić wykonywanie wielu zadań,
- reagować na anulowanie procesu,
- przekazywać błędy dalej,
- nie gubić pojedynczych fragmentów.

Dla agenta oznacza to, że pojedynczy dokument należy traktować jako **jedno zadanie składające się z wielu kontrolowanych operacji**, a nie jako serię niezależnych tłumaczeń.

**Szczegóły:** `docs/reports/FAZA_8_TRANSLATION_EXECUTOR_2026-09-30.md`

## 9. Pamięć wyników tłumaczenia

Program posiada mechanizm pamiętania wcześniejszych wyników tłumaczenia.

Jeżeli identyczne zadanie pojawi się ponownie i wynik nadal jest ważny, program może wykorzystać wcześniej uzyskany rezultat zamiast wykonywać tłumaczenie ponownie.

Daje to dwie podstawowe korzyści:
- ograniczenie niepotrzebnego wykonywania tłumaczeń,
- przyspieszenie powtarzalnych operacji.

Pamięć wyników jest elementem pomocniczym. Nie zmienia podstawowej logiki procesu tłumaczenia.

**Szczegóły:** `docs/reports/FAZA_8_TRANSLATION_CACHE_2026-09-30.md`

## 10. Kontrola wyniku

Program nie powinien traktować każdego zwróconego tekstu jako automatycznie poprawnego.

Po wykonaniu tłumaczenia wynik jest kontrolowany.

Sprawdzane są m.in.:
- czy wynik faktycznie istnieje,
- czy nie jest pusty w sytuacji, w której powinien zawierać treść,
- czy odpowiada oczekiwaniom dotyczącym języka,
- czy nie zostały uszkodzone specjalne elementy tekstu.

Jest to ważna zasada programu:

> wykonanie tłumaczenia i zaakceptowanie wyniku są dwoma różnymi etapami.

**Szczegóły:** `docs/reports/FAZA_8_RESULT_VALIDATOR_2026-09-30.md`

## 11. Ochrona struktury dokumentu

Podczas pracy z dokumentami mogą występować elementy, których nie wolno przypadkowo zmienić.

Program posiada mechanizmy kontroli specjalnych znaczników i elementów strukturalnych.

Ich zadaniem jest wykrywanie sytuacji, w których wynik tłumaczenia mógłby uszkodzić strukturę dokumentu.

Agent powinien więc zawsze zakładać, że:

> nie każdy znak znajdujący się w materiale przekazywanym do tłumaczenia jest zwykłym tekstem.

**Szczegóły:** `docs/reports/REGRESJA_MARKER_UNICODE_2026-09-30.md`

## 12. Złożenie dokumentu po tłumaczeniu

Po zakończeniu tłumaczenia poszczególnych fragmentów program składa wynik z powrotem w strukturę dokumentu.

Logiczny proces jest następujący:
1. dokument zostaje rozłożony na elementy przeznaczone do przetwarzania,
2. elementy tekstowe są tłumaczone,
3. wyniki są sprawdzane,
4. elementy zostają umieszczone z powrotem w odpowiednich miejscach,
5. wynikowy dokument jest sprawdzany pod względem strukturalnym.

Dlatego agent nie powinien samodzielnie traktować wyniku tłumaczenia jako gotowego dokumentu.

Gotowym rezultatem jest **dokument po ponownym złożeniu i kontroli**.

**Szczegóły:** `docs/reports/FAZA_8_DOCUMENT_TRANSLATION_SERVICE_2026-09-30.md`

## 13. Główny przepływ programu

Cały program można rozumieć jako następujący łańcuch:

**Użytkownik**

↓

**wybór dokumentu i parametrów tłumaczenia**

↓

**przygotowanie dokumentu**

↓

**wydzielenie treści do tłumaczenia**

↓

**podział na fragmenty**

↓

**przygotowanie instrukcji**

↓

**wybór backendu**

↓

**wykonanie tłumaczenia**

↓

**kontrola wyników**

↓

**ponowne złożenie dokumentu**

↓

**kontrola dokumentu wynikowego**

↓

**gotowy rezultat**

Najważniejszy punkt dla nowego agenta:

> backend wykonuje tłumaczenie, ale nie zarządza całym procesem tłumaczenia dokumentu.

## 14. Warstwa zarządzająca tłumaczeniem

Program posiada logiczny element odpowiedzialny za koordynowanie całego procesu tłumaczenia.

Jego zadaniem jest połączenie:
- przygotowania fragmentów,
- wykonania tłumaczeń,
- pamięci wcześniejszych wyników,
- kontroli rezultatów,
- obsługi anulowania.

Nie powinien on wiedzieć, czy pracuje z DOCX, EPUB czy Markdown.

Nie powinien również być zależny od konkretnego backendu.

Jego zadanie można streścić jako:

> „doprowadź zadanie tłumaczeniowe od przygotowanego materiału do zweryfikowanego wyniku”.

**Szczegóły:** `docs/reports/FAZA_8_TRANSLATION_ORCHESTRATOR_2026-09-30.md`

## 15. Interfejs użytkownika

Interfejs użytkownika jest warstwą służącą do obsługi programu przez człowieka.

Logicznie odpowiada za takie obszary jak:
- uruchamianie tłumaczenia,
- wybór dokumentu,
- wybór ustawień,
- wybór backendu,
- prezentowanie postępu,
- prezentowanie diagnostyki,
- reagowanie na działania użytkownika.

Interfejs nie powinien samodzielnie wykonywać logiki tłumaczenia.

Jego rolą jest **sterowanie procesem i przedstawianie jego stanu**.

**Szczegóły:** `docs/reports/FAZA_9_GUI_COMPLETE_2026-09-30.md`

## 16. Diagnostyka

Program posiada również obszar odpowiedzialny za informowanie o stanie procesu.

Agent powinien odróżniać:
- błąd dokumentu,
- błąd procesu tłumaczenia,
- niedostępność backendu,
- błąd komunikacji z usługą,
- niepoprawny wynik,
- anulowanie operacji.

Nie każdy problem oznacza błąd całego programu.

W szczególności niedostępność jednego backendu nie oznacza automatycznie, że cały system tłumaczenia jest niedostępny.

## 17. Obsługa błędów

Błędy są traktowane jako część normalnego procesu działania programu.

Program rozróżnia m.in. problemy związane z:
- konfiguracją,
- uwierzytelnieniem,
- ograniczeniem liczby żądań,
- przekroczeniem czasu,
- siecią,
- odpowiedzią usługi,
- backendem,
- nieprawidłowym wynikiem.

Dla agenta najważniejsza zasada brzmi:

> najpierw ustal, w której części procesu wystąpił problem, a dopiero potem podejmuj działania naprawcze.

## 18. Anulowanie operacji

Tłumaczenie może być procesem długotrwałym.

Dlatego program umożliwia logiczne anulowanie operacji.

Anulowanie oznacza:

> użytkownik lub nadrzędny proces nie chce już kontynuować bieżącego zadania.

Agent powinien respektować ten stan i nie traktować anulowania jako błędu systemowego.

## 19. Bezpieczeństwo informacji

Program oddziela informacje wymagane do korzystania z usług od właściwej logiki tłumaczenia.

Dane uwierzytelniające i sekrety nie powinny być traktowane jako zwykłe dane konfiguracyjne ani przekazywane pomiędzy elementami programu bez potrzeby.

**Szczegóły:** `docs/reports/FAZA_5_CLOUD_SECRET_ISOLATION_2026-09-30.md`

## 20. Rola agenta w programie

Nowy agent powinien przede wszystkim rozumieć **cel zadania i granice odpowiedzialności poszczególnych obszarów**.

Agent powinien umieć odpowiedzieć na pytania:
1. Jaki dokument przetwarzamy?
2. Jaki fragment dokumentu wymaga tłumaczenia?
3. Jaki jest język źródłowy?
4. Jaki jest język docelowy?
5. Jaki backend może wykonać zadanie?
6. Czy backend jest dostępny?
7. Czy wynik tłumaczenia jest poprawny?
8. Czy struktura dokumentu została zachowana?
9. Czy zadanie zakończyło się sukcesem, błędem czy anulowaniem?
10. Czy problem dotyczy dokumentu, procesu czy backendu?

Agent nie powinien automatycznie ingerować w niższe warstwy programu tylko dlatego, że napotkał problem.

## 21. Zasada rozdzielenia komponentów

Najważniejszą zasadą organizacji V4 jest rozdzielenie odpowiedzialności.

### Dokument
Odpowiada za to, **co jest tłumaczone i jak zachować strukturę dokumentu**.

### Proces tłumaczenia
Odpowiada za to, **jak przeprowadzić zadanie tłumaczeniowe od początku do końca**.

### Backend
Odpowiada za to, **jak faktycznie uzyskać tłumaczenie**.

### Walidacja
Odpowiada za to, **czy uzyskany rezultat można zaakceptować**.

### Interfejs
Odpowiada za to, **jak człowiek steruje procesem i obserwuje jego stan**.

Takie rozdzielenie umożliwia rozwijanie poszczególnych części niezależnie.

## 22. Co agent powinien wiedzieć o backendach

Backendy są wymienne.

Nie należy zakładać:
- że istnieje tylko jeden backend,
- że każdy backend obsługuje wszystkie języki,
- że każdy backend jest zawsze dostępny,
- że backend odpowiada za obsługę dokumentów.

W szczególności Apertium jest obecnie traktowane jako backend, który musi mieć **co najmniej jedną kompletną, działającą parę językową do rzeczywistych testów**.

Nie jest wymagane, aby była to konkretnie para `eng-pol`.

## 23. Stan projektu

Aktualny stan należy rozumieć jako:

**Tłumacz V4 0.40.0 — lokalny Release Candidate.**

Migracja V3 → V4 została wykonana na poziomie głównych założeń architektonicznych, implementacji i lokalnego handoffu.

V3 pozostaje oddzielnym, zachowanym projektem.

V4 nie powinna być traktowana jako finalne wydanie produkcyjne do czasu zamknięcia pozostałych kwestii release.

Aktualny opis stanu znajduje się w:
- `docs/Raport_koncowy_migracji_v3-v4.md`
- `docs/STATUS.md`

## 24. Dokumentacja szczegółowa

Ten dokument jest **mapą logiczną programu**, a nie zastępstwem dokumentacji technicznej.

Agent powinien korzystać z dokumentacji szczegółowej wtedy, gdy musi:
- zmienić zachowanie programu,
- rozwiązać konkretny błąd,
- zmienić backend,
- zmienić obsługę dokumentu,
- zmienić sposób pakowania,
- wykonać test,
- zrozumieć decyzję migracyjną.

Najważniejsze punkty wejścia:
- **Stan projektu:** `docs/STATUS.md`
- **Plan migracji:** `docs/PLAN_MIGRACJI-v4.md`
- **Indeks dokumentacji:** `docs/INDEX.md`
- **Historia zmian:** `docs/CHANGELOG.md`
- **Architektura:** `docs/ARCHITECTURE.md`
- **Migracja V3 → V4:** `docs/MIGRATION_NOTES_V3_TO_V4.md`
- **Raport końcowy:** `docs/Raport_koncowy_migracji_v3-v4.md`
- **Release notes:** `docs/release/RELEASE_NOTES_0.40.0.md`
- **Procedura rollbacku:** `docs/release/ROLLBACK_0.40.0.md`
- **Raporty poszczególnych faz:** `docs/reports/`

## 25. Minimalny model mentalny dla nowego agenta

Nowy agent powinien zapamiętać przede wszystkim:

> **Tłumacz V4 przyjmuje dokument, przygotowuje jego treść do tłumaczenia, przekazuje ją do odpowiedniego wykonawcy, kontroluje wynik i składa poprawny dokument wynikowy.**

Backend jest tylko wykonawcą tłumaczenia.

Format dokumentu nie powinien determinować backendu.

Backend nie powinien determinować formatu dokumentu.

Interfejs użytkownika nie powinien zawierać zasad samego tłumaczenia.

Walidacja jest osobnym etapem procesu.

Problemy należy diagnozować według miejsca ich wystąpienia, a nie traktować całego programu jako jednego komponentu.

To jest podstawowy model, który agent powinien posiadać przed rozpoczęciem pracy z kodem i szczegółową dokumentacją projektu.
