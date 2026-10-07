# Notatki migracyjne V3 → V4

## Cel
Dokument opisuje stan migracji aplikacji Tłumacz z V3 do V4 oraz sposób przejścia na artefakt 0.40.0.

## Najważniejsze zmiany
- V4 jest modularnym monolitem z warstwą aplikacyjną, backendami, Filter Engine i usługami dokumentowymi.
- Kontrakty backendów i filtrów zostały wydzielone do jawnych portów.
- LlamaCpp, Cloud/Mozhi i Apertium mają niezależne adaptery.
- FastAPI i OpenVINO nie występują w aktywnym runtime V4.
- Filter Engine korzysta z izolowanego Java Filter Host i bundlowanego Okapi runtime.
- Tłumaczenie dokumentów jest obsługiwane przez DocumentTranslationService i TranslationOrchestrator.
- GUI jest odseparowane od warstwy aplikacyjnej przez kontrolery bez importów Qt.
- V3 pozostaje osobnym, nienaruszonym drzewem źródłowym.

## Packaging
Artefakt Linux jest budowany jako wheel tlumacz-0.40.0-py3-none-any.whl i zawiera wymagane zasoby runtime V4. Instalacja testowa jest wykonywana w czystym środowisku bez zależności zewnętrznych.

Aktualny artefakt nie zawiera kompletnej pary Apertium eng-pol i nie jest artefaktem Windows.

## Konfiguracja i dane użytkownika
Migracja nie kopiuje sekretów API do repozytorium ani do artefaktu. Konfiguracja użytkownika ma własny mechanizm migracji i backup.

## Słownik
Słownik jest zasobem niezależnym od binarnego/runtime packagingu V4. Nie jest wkompilowany do artefaktu i może zostać dodany w dowolnym późniejszym momencie.

## Procedura przejścia
1. Zachować istniejącą instalację V3 jako rollback.
2. Zainstalować wheel V4 w osobnym środowisku.
3. Zweryfikować tlumacz --version i test clean-install.
4. Zweryfikować wymagane runtime'y dokumentowe.
5. Dopiero po spełnieniu kryteriów release przełączyć użytkownika na V4.

Nie należy kopiować części drzewa V4 z powrotem do V3.

## Aktualizacja po audycie GUI/Cloud — 2026-10-01

Wcześniejszy stan dokumentu opisywał izolację kontrolerów GUI, ale nie odzwierciedlał braku faktycznej warstwy Qt. Po audycie odtworzono Qt GUI V4 jako adapter nad warstwą aplikacyjną. Aktywne backendy GUI to llama.cpp, Apertium i Cloud. FastAPI/OpenVINO pozostają wycofane.

Cloud V4 zawiera 8 adapterów providerów oraz 12 profili Cloud odzyskanych funkcjonalnie z V3. Szczegóły i dowody: docs/Audyt/AUDYT_REGRESJI_GUI_CLOUD_V3_V4_2026-10-01.md oraz docs/Audyt/RAPORT_NAPRAWY_GUI_CLOUD_2026-10-01.md.
