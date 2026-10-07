---
title: "Audyt licencyjny Okapi, lingua-rs i Apertium"
status: evidence
zone: audit
kind: audit
created: 2026-09-28
---

# Audyt licencyjny: Okapi, lingua-rs i Apertium

**Data audytu:** 2026-09-28  
**Projekt:** Tłumacz V3 0.31.2  
**Zakres:** licencje upstream oraz sposób wykorzystania tych projektów w Tłumaczu.

> To jest audyt techniczno-licencyjny projektu, a nie indywidualna opinia prawna. W przypadku komercyjnej dystrybucji o istotnym znaczeniu prawnym końcową interpretację powinien potwierdzić prawnik.

## 1. Źródła i stan faktyczny

Audyt oparto na bieżących źródłach upstream oraz na stanie repozytorium Tłumacz:

- Okapi Framework: https://gitlab.com/okapiframework/Okapi — README i `LICENSE` wskazują Apache License 2.0.
- Okapi FAQ: https://okapiframework.org/wiki/index.php?title=FAQ — projekt wskazuje Apache 2.0 dla kodu i CC BY-SA dla dokumentacji.
- lingua-rs: https://github.com/pemistahl/lingua-rs — repozytorium wskazuje Apache-2.0 i zawiera plik `LICENSE`.
- Apertium core: https://github.com/apertium/apertium — README wskazuje GNU GPL v2.0 i odsyła do `COPYING`.
- Apertium: https://github.com/apertium — organizacja zawiera wiele repozytoriów o różnych oznaczeniach licencyjnych.
- Apertium Wiki, użycie danych językowych: https://www.wiki.apertium.org/wiki/Using_linguistic_resources — dane używane do tworzenia par muszą być własne albo dostępne na licencji kompatybilnej z GPL.
- GNU GPL 2.0: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
- Apache License 2.0: https://www.apache.org/licenses/LICENSE-2.0.html

Stan lokalny Tłumacza:

- `lingua-language-detector>=2.1.1` jest bezpośrednią zależnością Pythonową; kod Tłumacza importuje `lingua` w `tlumacz/language_detector.py`.
- Okapi jest uruchamiane jako zewnętrzny program/bridge (`Tikal` i Java bridge), a nie jako kod scalony z modułami Python Tłumacza.
- Apertium jest uruchamiane jako osobny proces przez backend; projekt zawiera prywatny runtime Apertium 3.9.12 dla Linux x86_64.
- W konfiguracji użytkownika znajduje się 57 repozytoriów Apertium zawierających język polski i/lub angielski.

## 2. Okapi Framework — Apache License 2.0

### Upstream

Okapi deklaruje Apache License 2.0 dla kodu. Licencja zezwala na używanie, kopiowanie, modyfikowanie i rozpowszechnianie kodu, również w projektach komercyjnych i zamkniętych, przy zachowaniu warunków licencji.

Najważniejsze obowiązki przy redystrybucji kodu Okapi:

1. dołączyć kopię Apache License 2.0;
2. zachować odpowiednie informacje copyright, patentowe i atrybucyjne;
3. jeżeli upstream dostarcza plik `NOTICE` dotyczący dystrybuowanej części, zachować wymagane informacje z tego pliku;
4. przy modyfikacji plików zaznaczyć fakt modyfikacji;
5. nie używać znaków towarowych Okapi w sposób sugerujący poparcie lub endorsement.

Apache 2.0 zawiera także grant patentowy dla objętych nim wkładów, z mechanizmem wygaśnięcia w przypadku określonego postępowania patentowego.

### Wykorzystanie w Tłumaczu

Obecny model jest korzystny licencyjnie: Tłumacz uruchamia Okapi/Tikal jako osobny komponent do ekstrakcji i scalania dokumentów. Nie ma potrzeby licencjonowania kodu Tłumacza jako Apache 2.0 tylko dlatego, że korzysta z Okapi.

**Zakres dozwolony:**

- użycie lokalne — tak;
- użycie komercyjne — tak;
- redystrybucja Okapi razem z Tłumaczem — tak, przy spełnieniu obowiązków Apache 2.0 i obowiązków licencyjnych zależności Okapi;
- modyfikacja Okapi — tak, z zachowaniem oznaczeń zmian i pozostałych warunków Apache 2.0;
- pozostawienie własnego kodu Tłumacza na MIT — tak, przy zachowaniu rozdzielenia i wymaganych notice dla Okapi.

### Uwaga o dokumentacji

FAQ Okapi rozróżnia kod (Apache 2.0) od dokumentacji (CC BY-SA). Nie należy automatycznie kopiować dokumentacji Okapi do Tłumacza pod MIT. Ten audyt dotyczy wykorzystania kodu/runtime'u, nie redystrybucji treści dokumentacyjnych upstream.

## 3. lingua-rs — Apache License 2.0

### Upstream

`pemistahl/lingua-rs` deklaruje Apache-2.0. Repozytorium pokazuje również pliki źródłowe z nagłówkami Apache 2.0.

Licencja pozwala na używanie, modyfikowanie i redystrybucję, także w produkcie komercyjnym, pod warunkiem spełnienia wymogów Apache 2.0. W szczególności przy redystrybucji należy zachować odpowiednie informacje copyright/attribution, kopię licencji i wymagane informacje z `NOTICE`, jeśli dotyczą dystrybuowanej wersji.

### Wykorzystanie w Tłumaczu

Tłumacz używa pakietu `lingua-language-detector` jako zależności Pythonowej. Jest to bezpośrednie użycie biblioteki, a nie tylko uruchamianie osobnego programu.

**Zakres dozwolony:**

- użycie jako zależności aplikacji MIT — tak;
- użycie komercyjne — tak;
- redystrybucja wheel/biblioteki razem z Tłumaczem — tak, przy spełnieniu Apache 2.0;
- modyfikacja biblioteki i dystrybucja zmodyfikowanej wersji — tak, przy zachowaniu notice o zmianach i warunków Apache 2.0;
- pozostawienie Tłumacza na MIT — tak.

Nie stwierdzono na podstawie źródeł upstream obowiązku przeniesienia licencji Apache 2.0 na cały kod aplikacji Tłumacz.

## 4. Apertium — GPL-2.0 dla rdzenia, ale ekosystem wymaga audytu per komponent

### Rdzeń

Repozytorium `apertium/apertium` jednoznacznie wskazuje GNU General Public License v2.0. GPLv2 zezwala na używanie programu, także komercyjne. Przy redystrybucji binariów obowiązują jednak wymagania GPL, w szczególności dotyczące licencji, informacji copyright oraz zapewnienia odpowiadającego kodu źródłowego na zasadach GPL.

### Ważne rozróżnienie

Nie należy wpisywać do polityki projektu uproszczenia „całe Apertium = GPL-2.0”. Organizacja Apertium zawiera wiele repozytoriów, a aktualne repozytorium core samo wskazuje również zależności/komponenty, dla których widoczne są inne licencje (m.in. LGPL-2.1). Dodatkowo lokalny katalog Tłumacza zawiera 57 repozytoriów par językowych, a część z nich ma własne pliki `COPYING`/`LICENSE`, podczas gdy w innych repozytoriach oznaczenie nie występuje w katalogu głównym.

Dlatego **licencję każdej redystrybuowanej pary językowej oraz każdego elementu runtime należy ustalić z jej własnego repozytorium i wersji**, a nie z samej nazwy „Apertium”.

### Obecny runtime Tłumacza

`tlumacz/backends/apertium/native_runtime/` zawiera 65 plików i m.in.:

- narzędzia Apertium;
- `libapertium`, `libapertium-lex-tools`, `liblttoolbox`;
- ICU, libxml2, zlib, bzip2, xz/lzma, GMP, MPFR, PCRE2, libmagic, libseccomp, readline/ncurses i inne biblioteki;
- prywatny `bash`, `gawk`, `grep`, `file` i inne narzędzia pomocnicze;
- dane/artefakty runtime.

Aktualnie w `native_runtime/LICENSES/` znajduje się tylko `apertium-eng-spa-COPYING`. To **nie jest wystarczający dowód kompletnego spełnienia obowiązków notice/source dla całego redystrybuowanego runtime**. Przed wydaniem Tłumacza z bundlowanym runtime należy wykonać SBOM/licence inventory całego artefaktu i dołączyć komplet wymaganych licencji, notice oraz źródeł/źródeł odpowiadających binariom.

### Model integracji a GPL

Tłumacz uruchamia Apertium jako osobny proces i komunikuje się z nim przez standardowy interfejs procesu. GNU FAQ wskazuje, że osobne programy mogą być dystrybuowane obok siebie, a granica procesu może wspierać traktowanie ich jako osobnych programów; ostateczna kwalifikacja zależy od sposobu i semantyki komunikacji.

W obecnym modelu:

`Tłumacz (MIT) -> subprocess -> Apertium (GPL)`

jest znacznie bezpieczniejszy licencyjnie niż włączenie kodu Apertium do tego samego modułu/obrazu wykonywalnego lub bezpośrednie linkowanie kodu GPL z kodem Tłumacza.

**Nie należy jednak na tej podstawie twierdzić, że dystrybucja całego instalatora jest „wyłącznie MIT”.** Bundlowany komponent GPL zachowuje własną licencję i musi być oznaczony oraz dystrybuowany zgodnie z GPL. Dodatkowe biblioteki runtime zachowują własne licencje.

### Dane językowe

Apertium opisuje dane językowe jako zasoby wymagające licencji kompatybilnej z GPL. Dla 57 pobranych repozytoriów nie wolno więc przyjmować jednej licencji zbiorczej bez sprawdzenia każdego konkretnego repozytorium i wersji.

Szczególnie istotne jest to dla planowanego bundlowania wszystkich par językowych. Każda para, którą chcemy dostarczać użytkownikowi, powinna mieć w rejestrze:

- repozytorium;
- commit/tag/release;
- dokładną licencję;
- pliki `COPYING`/`LICENSE`;
- ewentualne dodatkowe notice/licencje danych;
- informację, czy zawiera komponenty na innych licencjach.

## 5. Wnioski dla Tłumacza V3

| Projekt | Licencja upstream | Użycie w Tłumaczu | Komercyjne użycie | Redystrybucja | Ryzyko licencyjne |
|---|---|---|---|---|---|
| Okapi | Apache-2.0 | osobny runtime/proces | dozwolone | dozwolona po spełnieniu Apache-2.0 | niskie/zarządzalne |
| lingua-rs | Apache-2.0 | bezpośrednia zależność Python | dozwolone | dozwolona po spełnieniu Apache-2.0 | niskie/zarządzalne |
| Apertium core | GPL-2.0 | osobny proces + bundlowany runtime | dozwolone | dozwolona, ale z obowiązkami GPL | podwyższone |
| Apertium language pairs | per repozytorium | osobne dane/wtyczki | zależne od konkretnej licencji | zależne od konkretnej licencji i GPL/source obligations | podwyższone |

### Zalecany model licencyjny projektu

1. **Kod Tłumacza pozostaje MIT.**
2. **lingua-rs pozostaje zależnością Apache-2.0** i otrzymuje wymagane attribution/license notice.
3. **Okapi pozostaje osobnym komponentem Apache-2.0**; przy dystrybucji należy zachować jego licencję i wymagane notice oraz zinwentaryzować licencje zależności Okapi.
4. **Apertium pozostaje osobnym komponentem GPL**, uruchamianym przez granicę procesu. Nie należy linkować kodu GPL bezpośrednio z kodem MIT Tłumacza bez osobnej analizy prawnej.
5. **Runtime Apertium nie powinien zostać uznany za gotowy do redystrybucji** dopóki nie powstanie kompletna lista licencji/NOTICE/source dla wszystkich 65 dołączonych plików/binariow i ich zależności.
6. **57 repozytoriów par językowych należy traktować jako 57+ osobnych pozycji licencyjnych**, a nie jako jedną licencję „Apertium”.
7. W paczce wydaniowej należy rozdzielić logicznie:
   - `Tłumacz` — MIT;
   - `Okapi` — Apache-2.0;
   - `lingua` — Apache-2.0;
   - `Apertium runtime` — właściwe GPL/pozostałe licencje;
   - poszczególne pakiety językowe — licencja właściwa dla konkretnego repozytorium.
8. Przed publicznym wydaniem bundlowanego runtime'u należy dodać stronę/plik `THIRD-PARTY-NOTICES` lub równoważny rejestr oraz mechanizm udostępniania odpowiadających źródeł GPL dla dokładnie tych binariów, które są dystrybuowane.

## 6. Odpowiedź na pytanie „w jakim zakresie możemy używać?”

### Okapi

Możemy używać, modyfikować i redystrybuować Okapi w Tłumaczu, także komercyjnie. Apache-2.0 nie wymusza zmiany licencji własnego kodu Tłumacza na Apache-2.0. Musimy zachować wymagane informacje licencyjne, copyright, attribution i NOTICE.

### lingua-rs

Możemy używać `lingua-language-detector` jako zależności Tłumacza, także w wydaniu komercyjnym i binarnym. Możemy utrzymać własny kod Tłumacza na MIT. Przy redystrybucji musimy spełnić Apache-2.0 dla biblioteki i jej wymaganych notice.

### Apertium

Możemy używać Apertium do tłumaczenia oraz redystrybuować je komercyjnie. Warunkiem jest zachowanie GPL dla redystrybuowanego komponentu GPL i spełnienie wymagań dotyczących źródeł, licencji i informacji copyright. Obecna architektura osobnego procesu jest właściwym kierunkiem dla utrzymania rozdzielenia Tłumacza MIT od Apertium GPL.

Nie możemy natomiast bez dodatkowej analizy traktować całego bundlowanego runtime'u i wszystkich 57 par jako jednego komponentu GPL-2.0. Wymagana jest inwentaryzacja per artefakt.

## 7. Status audytu

**AUDYT ZAKOŃCZONY — 2026-09-28.**

Zakres audytu został wykonany: potwierdzono licencje upstream Okapi, lingua-rs i Apertium oraz opisano sposób wykorzystania tych komponentów w Tłumaczu. Zidentyfikowane obowiązki redystrybucyjne zostały zapisane jako wymagania dla procesu wydania.

- **Okapi:** licencja upstream Apache-2.0 — potwierdzona.
- **lingua-rs:** licencja upstream Apache-2.0 — potwierdzona.
- **Apertium core:** licencja GPL-2.0 — potwierdzona.
- **Apertium runtime 3.9.12:** wymagany przyszły inventory licencji/NOTICE/source dla artefaktu release — pozostaje zadaniem wydaniowym, nie otwartym audytem niniejszego dokumentu.
- **Pakiety językowe:** wymagany przyszły rejestr licencji per repozytorium/wersję dla konkretnych pakietów przeznaczonych do dystrybucji — pozostaje zadaniem wydaniowym.

Zamknięcie audytu oznacza zakończenie analizy licencyjnej i zapisanie wymagań. Nie oznacza automatycznego zamknięcia prac przygotowujących konkretny artefakt dystrybucyjny.

## 8. Źródła

- Okapi: https://gitlab.com/okapiframework/Okapi
- Okapi LICENSE: https://gitlab.com/okapiframework/Okapi/-/blob/main/LICENSE
- Okapi FAQ: https://okapiframework.org/wiki/index.php?title=FAQ
- lingua-rs: https://github.com/pemistahl/lingua-rs
- Apertium core: https://github.com/apertium/apertium
- Apertium organization: https://github.com/apertium
- Apertium — using linguistic resources: https://www.wiki.apertium.org/wiki/Using_linguistic_resources
- Apache License 2.0: https://www.apache.org/licenses/LICENSE-2.0.html
- GNU GPL v2.0: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
- GNU GPL FAQ: https://www.gnu.org/licenses/gpl-faq.en.html
