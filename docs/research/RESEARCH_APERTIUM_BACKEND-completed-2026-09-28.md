---
id: research-apertium-backend
status: research
meta:
  contentType: Research
  category: research
version: 0.1.0
updated: 2026-09-26
owner: translation-backend
source: "https://github.com/apertium/apertium"
depends_on: [docs/AGENTS.md, docs/STATUS.md]
expires_when: zmiana kontraktu Apertium lub decyzji o backendach
last_validation: "przegląd źródeł pierwotnych Apertium 2026-09-26"
---

# Research: Apertium jako backend Tłumacza V3

## Zakres

Ocena Apertium jako lokalnego backendu tłumaczeniowego w dwóch trybach:

1. samodzielny backend regułowy;
2. tryb hybrydowy: Apertium wykonuje tłumaczenie bazowe, a `llama.cpp` wykonuje kontrolowany post-processing i korektę błędów.

Dokument rozdziela fakty potwierdzone w źródłach od decyzji projektowych.

## Fakty potwierdzone w źródłach pierwotnych

- Apertium jest otwartym, regułowym narzędziem MT opartym m.in. na finite-state transducers; dane językowe są rozdzielone na moduły jednojęzyczne i pary tłumaczeniowe. Źródło: [oficjalne README Apertium](https://github.com/apertium/apertium/blob/main/README).
- Główne wywołanie CLI obsługuje potok tekstowy przez stdin/stdout, tryb pary językowej oraz opcjonalne formaty przez `-f`; dostępne tryby można wykrywać przez `-l`. Źródło: [oficjalne README Apertium, Usage](https://github.com/apertium/apertium/blob/main/README#usage).
- Apertium APy udostępnia HTTP API dla tłumaczenia tekstu, dokumentów i stron WWW, a także analizy i generowania morfologicznego. Źródło: [Apertium APy README](https://github.com/apertium/apertium-apy/blob/master/README.md).
- APy może działać jako lokalny serwer na porcie 2737. Dokumentuje timeout, liczbę procesów, liczbę potoków na parę, limit użytkowników na potok, restart potoku oraz limit równoległych potoków dokumentowych. Źródło: [Apertium APy options](https://github.com/apertium/apertium-apy/blob/master/README.md#usage).
- APy używa endpointu `/translate` z parametrami `langpair` i `q`; kod źródłowy waliduje nieprawidłową parę i brak zainstalowanego trybu, a błędy timeoutu zwraca jako błąd usługi. Źródło: [handler tłumaczenia APy](https://github.com/apertium/apertium-apy/blob/master/apertium_apy/handlers/translate.py).
- Oficjalne materiały wskazują, że instalacja składa się z core oraz niezależnie instalowanych danych językowych/par. Dla użytkowników preferowane są paczki lub środowisko wirtualne; kompilowanie core jest przede wszystkim ścieżką dla deweloperów. Źródło: [oficjalny przewodnik instalacji](https://apertium.org/releases/Installation.pdf).
- Pary językowe mają własne wymagania i własne licencje. Przykładowa para `apertium-eng-deu` wymaga `lttoolbox`, `apertium`, `vislcg3` oraz modułów językowych. Źródło: [README apertium-eng-deu](https://github.com/apertium/apertium-eng-deu).
- Oficjalna lista par obejmuje polski z wybranymi językami, ale status par może być `trunk`, `staging` lub `nursery`; nie wolno zakładać, że każda para jest wydana, kompletna ani zainstalowana. Źródło: [oficjalna lista par językowych](https://wiki.apertium.org/wiki/List_of_language_pairs).
- Apertium core jest licencjonowane GPL-2.0, natomiast konkretne paczki językowe/pary mogą mieć inne warianty GPL. Przykładowa para `apertium-eng-deu` deklaruje GPL-3.0. Dystrybucja z aplikacją wymaga osobnego audytu licencji i dependency closure. Źródła: [Apertium README](https://github.com/apertium/apertium/blob/main/README), [apertium-eng-deu license](https://github.com/apertium/apertium-eng-deu).

## Uzupełnienie researchu — 2026-09-27

- Oficjalna wiki opisuje osobno kompilację danych językowych. Para po `./autogen.sh` i `make` może być używana bez instalacji, a test wykonywany jest jako `apertium -d . <tryb>`. Oznacza to, że skompilowane dane pozostają niezależnym artefaktem pakietu językowego, a nie częścią biblioteki core. Źródło: https://wiki.apertium.org/wiki/Install_language_data_by_compiling.
- Oficjalne README core potwierdza `apertium -d <katalog> <tryb>` dla skompilowanych, ale niezainstalowanych danych oraz `-l` do listowania trybów. Źródło: https://github.com/apertium/apertium/blob/main/README.
- `apertium-eng-pol` jest aktualną parą angielski↔polski w GitHubie Apertium. README wymaga `lttoolbox >= 3.5.1` i `apertium >= 3.6.1`; repo opisuje kompilację przez `autoreconf -fvi`, `./configure`, `make` oraz test `apertium -d . eng-pol`. Repo ma licencję GPL-2.0. Źródło: https://github.com/apertium/apertium-eng-pol.
- Lokalny katalog `$HOME/.config/tlumacz/Apertium/apertium-en-pl` zawiera obecnie źródła pary i `modes.xml`, ale nie zawiera kompletu wymaganych plików `.bin`. Traktujemy ten katalog jako docelowy katalog wtyczek danych; kompilacja, jeżeli wymagana, ma wytworzyć artefakty w tym samym pakiecie.
- Lokalny build nie może obecnie wykonać kompilacji core/danych, ponieważ system nie ma `lttoolbox` ani `apertium`. Próba izolowanego builda `lttoolbox` wykazała dodatkowo brak nagłówków `utf8cpp` i konfiguracji Boost. Nie instalowano żadnych zależności systemowych.
- Nie znaleziono gotowego artefaktu `.bin` dla `apertium-eng-pol` w oficjalnym repo GitHub; repo zawiera źródła danych i instrukcję ich kompilacji. Oficjalne pakiety dystrybucyjne zawierają inne wydane pary, ale `eng-pol` jest obecnie oznaczone jako `apertium-incubator`, więc nie należy zakładać dostępności gotowej paczki dla tego konkretnego repo.

## Wnioski techniczne

- Apertium dobrze nadaje się do przewidywalnego tłumaczenia lokalnego, szczególnie gdy ważne są powtarzalność, brak wysyłania danych do chmury i możliwość diagnozowania reguł.
- Apertium nie powinno otrzymywać surowego DOCX/EPUB/ODT z pominięciem istniejącego kontraktu dokumentowego. W Tłumaczu V3 backend powinien dostawać tekstowe jednostki segmentacyjne, a rekonstrukcja dokumentu powinna pozostać odpowiedzialnością XLIFF/V4 Filter Engine.
- Apertium nie zastępuje `llama.cpp`: ma inne właściwości jakościowe, nie zapewnia swobodnej korekty stylistycznej i może pozostawiać nieznane słowa lub błędy leksykalno-składniowe.
- Tryb hybrydowy jest możliwy, ale wymaga traktowania wyniku Apertium jako danych wejściowych do kontrolowanego post-editingu, nie jako luźnej sugestii dla modelu.
- Największym ryzykiem wdrożeniowym nie jest samo wywołanie CLI, tylko dystrybucja core, par językowych, zależności, mapowania kodów językowych, limitów zasobów i zgodności licencyjnej.

## Nieweryfikowane jeszcze lokalnie

- rzeczywista dostępność i jakość wymaganych par dla docelowych języków projektu;
- dokładna wersja Apertium dostępna w repozytoriach Kiro/Arch;
- czas uruchomienia, przepustowość i zużycie RAM na sprzęcie użytkownika;
- pełne dependency closure i możliwość redystrybucji w AppImage, pakiecie Arch, Windows oraz macOS;
- jakość post-editingu `llama.cpp` na reprezentatywnym korpusie dokumentów projektu.

## Decyzja badawcza

Rozpocząć od adaptera Apertium w osobnym module ApertiumBackend za wspólnym
portem backendu, początkowo przez kontrolowany lokalny runtime CLI. Nie budować
nowego mikroserwisu ani nie integrować Apertium bezpośrednio z GUI, main ani
Cloud. Tryb hybrydowy włączyć dopiero po przejściu testów kontraktowych trybu
samodzielnego. Granice i kolejność migracji opisuje
`docs/PLAN_MODULARIZACJI_BACKENDOW_2026-09-26.md`.
