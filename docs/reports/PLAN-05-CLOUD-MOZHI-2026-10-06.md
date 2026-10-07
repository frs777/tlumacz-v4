# PLAN-05 — Cloud i Mozhi — raport realizacji

Data: 2026-10-06
Plan: docs/Plany/PLAN-05-CLOUD-MOZHI-2026-10-05.md

## Wynik

PLAN-05 został zweryfikowany i oznaczony jako `completed`. Zmiany ograniczono do aktywnej ścieżki Cloud/Mozhi oraz testów zabezpieczających jej kontrakty.

## Zrealizowane i zweryfikowane

1. **Provider contract / router** — `CloudRouter` pozostaje jedynym punktem wyboru providera; test potwierdza brak automatycznego fallbacku do innego providera.
2. **Profile isolation / secrets** — test potwierdza, że `api_key` nie trafia do `settings-v4.json`, a sekret jest przechowywany przez `SecretStore`.
3. **DLX** — istniejący adapter i profil przechodzą test kontraktowy; transport pozostaje w warstwie Cloud.
4. **Custom** — test integracyjny potwierdza, że backend `custom` korzysta z `CloudRouter` i OpenAI-compatible providera bez osobnego runtime.
5. **Mozhi discovery** — autodiscovery sprawdza obecność wybranego silnika oraz niepuste listy `source_languages` i `target_languages`.
6. **Mozhi live E2E** — 2026-10-06 wykonano rzeczywiste żądanie przez `MozhiProvider(base_url="auto", engine="duckduckgo")`; wynik `Hello world` → `Witaj świat`, wybrana instancja `https://mozhi.aryak.me`.
7. **Timeout / errors** — istniejące testy potwierdzają klasyfikację timeoutów, błędów HTTP, sieci i niepoprawnych odpowiedzi. Cancellation pozostaje kooperacyjne na granicy orkiestratora; brak ukrytego retry/fallbacku.

## Testy

- Baseline przed zmianami: **31 testów Cloud — PASS**.
- Po zmianach: **34 testy Cloud/Custom — PASS**.
- Ruff: dostępny w `.venv`; wykazuje istniejące błędy poza zakresem PLAN-05, m.in. w `filter_engine`, QML bridge i testach tplugin.
- mypy: **8 istniejących błędów** w `backends/llama_cpp/runtime.py`, `backends/apertium/packages.py` i `backends/apertium/runtime.py`; brak związku z PLAN-05.
- Pełna suite `tests/`: uruchomiona w osobnym zadaniu; wynik końcowy jest częścią końcowej weryfikacji sesji.

## Backupy

- `backups/plan-05-cloud-mozhi-20261006-pre/` — stan kodu Cloud i głównych testów przed zmianą.
- `backups/plan-05-cloud-mozhi-20261006-docs-pre/` — stan planu i dokumentacji Cloud przed zamknięciem planu.
- SentinelX wykonał również automatyczne backupy przy każdej edycji pliku.

## Zmienione pliki

- `src/tlumacz/backends/cloud/mozhi.py` — discovery wymaga source + target languages.
- `tests/test_cloud_providers_v3_compat.py` — regresja discovery.
- `tests/test_cloud_profile_isolation.py` — nowy test izolacji sekretów profili Cloud.
- `tests/test_backend_registry_custom.py` — test Custom → CloudRouter.
- `docs/technical-docs/cloud-translation.md` — evidence i aktualny stan.
- `docs/Plany/PLAN-05-CLOUD-MOZHI-2026-10-05.md` — status `completed` i aktualizacja walidacji.

## Pozostaje poza PLAN-05

Globalne błędy Ruff/mypy oraz pełny release gate V4 pozostają zadaniami innych planów. Nie instalowano ani nie usuwano żadnego oprogramowania.

### Korekta po unifikacji konfiguracji — 2026-10-07

Trwała konfiguracja GUI została scalona do `$HOME/.config/tlumacz/config.json`. Od tej zmiany zapis ustawień nie używa `settings-v4.json`; sekrety pozostają w `SecretStore` (`$HOME/.config/tlumacz/.key`) i nie są zapisywane w `config.json`.
