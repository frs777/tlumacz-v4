# Izolacja sekretów profili Cloud — plan naprawy

> **Dla agentów wykonawczych:** plan należy realizować zadanie po zadaniu w trybie TDD. Nie zmieniać kodu przed wykonaniem testu regresyjnego.

**Cel:** usunąć regresję, w której ponownie utworzony `QmlApplicationBridge` nie korzysta z tego samego `SecretStore`, którego użyto podczas migracji/zapisu profili Cloud, przez co po przełączeniu Codex → ChatGPT może odczytać sekret `local` albo pusty zamiast sekretu profilu.

**Architektura:** `QmlApplicationBridge` przechowuje sekrety wyłącznie w `SecretStore`, indeksując je jako `SERVICE/<nazwa_usługi>`. Konfiguracja JSON przechowuje dane profilu bez `api_key`. Wykryta regresja wynika z rozdzielenia ścieżki konfiguracji i ścieżki magazynu sekretów w teście: pierwszy bridge otrzymuje jawne `secret_path=tmp_path / ".key"`, natomiast `restored` jest tworzony bez `secret_path` i zgodnie z implementacją używa domyślnego `$HOME/.config/tlumacz/.key`.

**Technologie:** Python, PySide6/QML bridge, `SecretStore`, pytest.

**Spec:** regresja `tests/test_gui_i18n.py::test_qml_bridge_switches_cloud_profiles_without_secret_leakage` oraz aktualny kontrakt izolacji sekretów opisany w `docs/STATUS.md`, `docs/TODO.md` i `CHANGELOG.md`.

## Globalne ograniczenia

- `api_key` nie może wrócić do trwałego JSON profilu Cloud.
- Sekrety Cloud pozostają rozdzielone per usługa/profil, także gdy profile mają wspólny `provider` i `base_url`.
- Sekret `local` dla llama.cpp nie może być używany jako fallback dla profilu Cloud.
- Nie zmieniać mechanizmu wyboru providera ani endpointów Cloud w ramach tej naprawy.
- Nie instalować ani usuwać zależności systemowych.
- Po zmianie kodu zaktualizować dokumentację projektu.
- Przed większą zmianą wykonać backup.

## Ustalenie przyczyny

Potwierdzona przyczyna bieżącego FAIL nie leży w samym indeksowaniu `SERVICE/<profil>`.

Ścieżka reprodukcji jest następująca:

1. Pierwszy `QmlApplicationBridge` jest tworzony z `secret_path=tmp_path / ".key"`.
2. `_migrate_legacy_secrets()` zapisuje `ChatGPT` i `Codex` do tego magazynu.
3. `set_api_key()` i `set_cloud_profile()` poprawnie zapisują sekret aktywnego profilu.
4. `save_settings()` zapisuje JSON bez sekretów.
5. `restored = QmlApplicationBridge(settings_path=config)` **nie dostaje `secret_path`**.
6. Konstruktor wybiera wtedy domyślne `Path.home() / ".config" / "tlumacz" / ".key"`.
7. `_load_cloud_profile("Codex")` nie znajduje `codex-secret-updated` w magazynie użytym przez pierwszy bridge.
8. Po `set_cloud_profile("ChatGPT")` również nie ma dostępu do `chat-secret-updated` z testowego magazynu; w środowisku testowym zostaje odczytana wartość z domyślnego magazynu, w tym przypadku `local`.

To dokładnie wyjaśnia obserwowany wynik:

```text
Expected: chat-secret-updated
Actual:   local
```

Nie ma obecnie dowodu, że `SecretStore` miesza klucze ChatGPT/Codex. Wręcz przeciwnie: implementacja używa nazwy usługi jako części klucza `SERVICE/<service_id>`.

## Zakres plików

- **Modyfikacja:** `tests/test_gui_i18n.py` — testy muszą jednoznacznie kontrolować magazyn sekretów przy rekonstrukcji bridge'a.
- **Ewentualna modyfikacja:** `src/tlumacz/qml_gui/bridge.py` — tylko jeśli dodatkowy test ujawni, że produkcyjna ścieżka tworzenia bridge'a nie przekazuje konsekwentnie magazynu sekretów albo że kontrakt konstrukcji wymaga jawnego rozdzielenia ścieżek.
- **Weryfikacja:** `tests/test_cloud_secrets.py` — potwierdzenie izolacji `SERVICE/ChatGPT`, `SERVICE/Codex` i `SERVICE/local`.
- **Dokumentacja:** `docs/STATUS.md`, `docs/TODO.md`, `docs/CHANGELOG.md` oraz raport/plan, jeśli wymaga tego indeks dokumentacji.

## Review Focus

1. Rekonstrukcja bridge'a z tym samym `settings_path`, ale innym/nieprzekazanym `secret_path` — test musi jednoznacznie określać kontrakt magazynu sekretów.
2. Profile ChatGPT i Codex ze wspólnym `provider=openai` i `base_url` — sekret musi pozostać niezależny.
3. Sekret `local` — nigdy nie może być fallbackiem dla Cloud.
4. Migracja legacy `api_key` z JSON — po migracji klucz musi trafić do właściwego profilu, a JSON nie może go zachować.
5. Zmiana profilu po ponownym utworzeniu bridge'a — odczyt musi nastąpić z właściwego magazynu i zwrócić sekret właściwego profilu.

## Zadanie 1: Test reprodukcyjny i jednoznaczny kontrakt testowego SecretStore

**Pliki:**
- Modyfikacja: `tests/test_gui_i18n.py`
- Weryfikacja: `tests/test_cloud_secrets.py`

- [x] **Krok 1: Zachować obecny FAIL jako punkt odniesienia.**

Uruchomić:

```bash
python3 -m pytest -q tests/test_gui_i18n.py::test_qml_bridge_switches_cloud_profiles_without_secret_leakage -vv
```

Oczekiwany stan przed naprawą: FAIL z `assert 'local' == 'chat-secret-updated'`.

- [x] **Krok 2: Zmienić test rekonstrukcji tak, aby `restored` korzystał z tego samego jawnie przekazanego `secret_path` co pierwszy bridge.**

Kontrakt testu:

```python
secret_path = tmp_path / ".key"
bridge = QmlApplicationBridge(settings_path=config, secret_path=secret_path)
...
restored = QmlApplicationBridge(settings_path=config, secret_path=secret_path)
```

Nie dopuszczać do odczytu realnego `$HOME/.config/tlumacz/.key` podczas testu.

- [x] **Krok 3: Uruchomić regresję.**

Oczekiwany wynik: PASS; po rekonstrukcji `Codex` ma `codex-secret-updated`, a po przełączeniu na `ChatGPT` ma `chat-secret-updated`.

- [x] **Krok 4: Rozszerzyć regresję o rozdzielenie `local`.**

Test zapisuje osobny lokalny sekret i potwierdza, że przełączenie Cloud nigdy nie zwraca wartości `local`.

- [x] **Krok 5: Uruchomić testy sekretów.**

```bash
python3 -m pytest -q tests/test_cloud_secrets.py tests/test_gui_i18n.py
```

Oczekiwany wynik: wszystkie testy PASS.

## Zadanie 2: Sprawdzenie, czy produkcyjny kontrakt wymaga zmiany kodu bridge'a

**Pliki:**
- Inspekcja: `src/tlumacz/qml_gui/bridge.py`
- Test: `tests/test_gui_i18n.py`

- [x] **Krok 1: Zweryfikować, że konstruktor jawnie przyjmuje `secret_path` i że produkcyjny default pozostaje `$HOME/.config/tlumacz/.key`.**

- [x] **Krok 2: Zweryfikować ścieżki `_migrate_legacy_secrets()`, `_load_cloud_profile()`, `_store_active_cloud_profile()` i `_store_local_api_key()`.**

Warunek: żadna ścieżka Cloud nie może wywoływać `get_service_api_key("local")` jako fallbacku.

- [x] **Krok 3: Po poprawieniu `secret_path` testy są zielone; `bridge.py` pozostaje bez zmian.**

Uzasadnienie: aktualny kod ma już poprawny rozdział `SERVICE/<profil>`; zmiana produkcyjna bez dowodu regresji zwiększałaby ryzyko.

- [ ] **Krok 4: Jeżeli pojawi się dodatkowy FAIL niezależny od testowego `secret_path`, najpierw dodać jego osobny test regresyjny, a dopiero potem wykonać minimalną zmianę implementacji.**

## Zadanie 3: Weryfikacja migracji i brak wycieku sekretów do JSON

**Pliki:**
- Test: `tests/test_gui_i18n.py`
- Test: `tests/test_cloud_secrets.py`
- Implementacja tylko w razie dowodu: `src/tlumacz/qml_gui/bridge.py`, `src/tlumacz/qml_gui/config.py`

- [x] **Krok 1: Potwierdzić po `save_settings()`, że `config.json` nie zawiera `chat-secret-updated`, `codex-secret-updated` ani lokalnego sekretu.**
- [x] **Krok 2: Potwierdzić, że magazyn sekretów zawiera trzy niezależne wpisy `SERVICE/ChatGPT`, `SERVICE/Codex`, `SERVICE/local`.**
- [x] **Krok 3: Potwierdzić migrację legacy `api_key` i `cloud_profiles[*].api_key` do właściwych usług bez kolizji.**

## Zadanie 4: Pełna walidacja

- [x] **Krok 1:** uruchomić skoncentrowane testy GUI/sekretów.
- [x] **Krok 2:** uruchomić pełny suite pytest — dwa niezależne przebiegi zakończone **537 passed**.
- [x] **Krok 3:** przeanalizować przejściowe FAIL z pierwszego nakładającego się przebiegu; izolowany `tests/test_qml_gui.py` oraz dwa kolejne pełne przebiegi są zielone, więc nie potwierdzono regresji kodu.
- [x] **Krok 4:** wykonać `python3 -m compileall -q src tests`.
- [x] **Krok 5:** wykonać kontrolę braku sekretów w konfiguracji i `git diff --check` — skan konfiguracji PASS, `git diff --check` PASS.
- [x] **Krok 6:** wykonać świeżą weryfikację wyników przed zamknięciem.

## Zadanie 5: Dokumentacja

- [x] **Krok 1:** zaktualizować `docs/STATUS.md` o potwierdzoną przyczynę regresji i kontrakt testowego `secret_path`.
- [x] **Krok 2:** zaktualizować `docs/CHANGELOG.md` o naprawę/regresję profili Cloud, bez ujawniania żadnych rzeczywistych sekretów.
- [x] **Krok 3:** zaktualizować `docs/TODO.md`, jeżeli istnieje odpowiadające zadanie; nie tworzyć duplikatu zamkniętego zadania.
- [x] **Krok 4:** zachować ten plan jako ślad diagnostyczny i dopisać bieżący wynik wykonania.

## Kryteria akceptacji

- Test `test_qml_bridge_switches_cloud_profiles_without_secret_leakage` przechodzi po rekonstrukcji bridge'a.
- ChatGPT i Codex zachowują niezależne sekrety mimo wspólnego providera/end-pointu.
- `local` nigdy nie jest zwracany jako sekret Cloud.
- JSON konfiguracji nie zawiera kluczy API.
- Migracja legacy nie powoduje kolizji sekretów.
- Skoncentrowane testy oraz pełna suite są wykonane; niepowodzenia nie są ukrywane.
- Dokumentacja odzwierciedla faktyczny stan po naprawie.

## Wynik wykonania — 2026-10-07

- Potwierdzony RED: `test_qml_bridge_switches_cloud_profiles_without_secret_leakage` zwracał `local` zamiast oczekiwanego sekretu ChatGPT.
- Naprawa: test przekazuje ten sam `secret_path` do pierwszego i rekonstruowanego `QmlApplicationBridge`.
- Backup: `backups/SECRET-PROFILE-ISOLATION-BEFORE-2026-10-07.tar.gz` (`0e744e95b0b77498e656ea584cbd690093bfe356ddab97ab896e346311a12818`).
- GREEN: regresja **1 passed**; testy sekretów i GUI **14 passed**.
- Produkcyjnego `bridge.py` nie zmieniano, ponieważ analiza potwierdziła poprawne indeksowanie `SERVICE/<service_id>`.
- Pełna suite została wykonana: dwa niezależne przebiegi zakończyły się **537 passed**.
- Pierwszy przebieg uruchomiony równolegle z innym pełnym przebiegiem zwrócił 4 przejściowe FAIL w testach QML; testy `tests/test_qml_gui.py` uruchomione osobno dały **153 passed**, a dwa kolejne pełne przebiegi dały **537 passed**, więc nie potwierdzono regresji kodu.
- `compileall`: PASS; skan aktywnego `config.json` pod kątem testowych sekretów i pola `api_key`: PASS; `git diff --check`: PASS.
- Dokumentacja: `docs/STATUS.md`, `docs/CHANGELOG.md`, `docs/TODO.md` oraz niniejszy plan zostały zaktualizowane.
