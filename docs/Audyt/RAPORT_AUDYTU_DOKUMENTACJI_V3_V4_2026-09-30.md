# Raport końcowego audytu dokumentacji V3 → V4

Data: 2026-09-30
Źródło: /home/frs/Projekty/agent-translator-v3
Cel: /home/frs/Projekty/tlumacz-v4
Status: DO AKCEPTACJI
Migracja fizyczna: NIE WYKONANA

## 1. Inwentaryzacja
Katalog docs V3 zawiera 410 plików: 113 Markdownów, 100 JSON, 5 JSONL, 152 logi, 7 PNG, 8 TXT, 2 PDF, 2 XML, 1 YAML, 1 ODT, 1 PY, 2 pliki Okular oraz kopie/backupy. Strefa docs/TESTY zawiera 288 plików, w tym 152 logi i 100 JSON. Archiwum V3 zawiera 45 plików.

## 2. Dokumenty potrzebne TERAZ
Aktywne źródła V4: AGENTS.md, STATUS.md, TODO.md, BUG.md, CHANGELOG.md, README.md, pomoc.md po weryfikacji; dokumentacja architektury Filter Engine; PROTOKOL_MOSTU_OKAPI_V1; PLAN_MIGRACJI-v4; plany modularizacji, MainWindow i Okapi; mechanizm Okapi; zależności i budowa Apertium.

## 3. Dokumenty potrzebne W PRZYSZŁOŚCI
Aktywne plany, audyty otwartych ryzyk, badania wymagane do decyzji architektonicznych, baseline testów, benchmarki przeznaczone do powtórzenia, materiały packaging/runtime/licensing, migracja konfiguracji V3→V4, E2E formatów, clean-install i Windows.

## 4. Kandydaci do ARCHIWUM
Zakończone lub zastąpione plany; research wykorzystany do decyzji; stare audyty zastąpione nowszymi; dokumenty usuniętych/niewybranych rozwiązań; duplikaty; stare instrukcje; backupy; historyczne benchmarki bez wartości baseline; stare materiały FastAPI/OpenVINO, jeżeli nie są potrzebne jako dowód decyzji migracyjnej.

## 5. TESTY
Aktywnie zachować baseline V4, kontrakty, integrację, E2E aktywnych backendów, Apertium, Filter Engine i benchmarki używane jako punkt odniesienia. Historycznie zachować powtórzenia i eksperymenty, jeżeli mają wartość porównawczą. Nie migrować jako aktywne: surowych logów bez wartości diagnostycznej, duplikatów JSON/JSONL, tymczasowych stdout/stderr i plików .bak.

## 6. Zrzuty
7 PNG należy zachować tylko, jeśli dokumentują aktualny interfejs lub są wymagane jako dowód historyczny. Zrzuty FastAPI/OpenVINO nie powinny być aktywną dokumentacją V4, jeśli te ścieżki pozostają poza V4.

## 7. Wdrożenia
Procedury build/release, packaging, deployment, runtime discovery, instalacja, migracja konfiguracji, rollback, Windows/Linux oraz wymagania runtime Apertium/Okapi.

## 8. Audyt
Audyty dokumentacji, inżynierskie, licencyjne, regresji, bezpieczeństwa i raporty migracyjne. Audyty historyczne mogą później przejść do Archiwum.

## 9. Plany
Tylko aktywne lub przyszłe plany. Plan migracji V3→V4 pozostaje aktywny do zakończenia migracji.

## 10. Dokumenty do AKTUALIZACJI zamiast prostego przeniesienia
QWEN.md, AGENTS.md, INDEX.md, INDEX.yml, STATUS.md, TODO.md, BUG.md, dokumentacja architektury, backendów, Filter Engine, packagingu i pomoc użytkownika.

## 11. Najważniejsze konflikty
QWEN.md V3 opisuje FastAPI/OpenVINO i starszy model architektury. Nie wolno kopiować go mechanicznie. V4 powinien mieć jeden indeks człowieka i jeden indeks maszynowy. docs/TESTY miesza dokumentację, logi, JSON, JSONL, backupy i dane surowe. Nie przenosić dokumentów tylko na podstawie nazw.

## 12. Bramka
V3 pozostaje nietknięty. V4 otrzymał wyłącznie nową strukturę docs oraz dokumenty audytowe/indeksowe. Przenoszenie dokumentów nastąpi dopiero po akceptacji raportu i indeksów.
