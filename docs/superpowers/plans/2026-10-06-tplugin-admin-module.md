# Moduł administracyjny TPlugin — plan wdrożenia

**Cel:** Utworzyć niezależne narzędzie administracyjne do przygotowywania, audytowania, walidowania i publikowania paczek TPlugin oraz pełną instrukcję ręcznego tworzenia paczek dla zaawansowanych użytkowników.

**Architektura:** Backend pozostaje poza \`src/tlumacz\` i nie jest ładowany przez aplikację. Korzysta z istniejącego kontraktu \`TPluginBuilder\` i \`TPluginInventory\`, ale dodaje warstwę projektu/manifestu, walidację, raportowanie i workflow paczkowania. Interfejs CLI jest pierwszym interfejsem; później może zostać użyty przez panel administracyjny.

**Tech Stack:** Python 3, argparse, JSON, pathlib, pytest, istniejący TPluginBuilder/TPluginInventory.

**Spec:** \`docs/technical-docs/tplugin-zarzadzanie-zaleznosciami.md\`

## Globalne ograniczenia

- Moduł administracyjny nie może być częścią \`src/tlumacz\`.
- Nie wolno automatycznie instalować zależności systemowych.
- Paczka musi zawierać manifest, inventory i checksumy.
- Walidacja musi blokować path traversal i błędne checksumy.
- Proces produkcyjny musi wspierać A/B/C.
- Ręczne tworzenie paczki pozostaje możliwe bez backendu administracyjnego.
- Dokumentacja projektu jest aktualizowana po zmianach.

## Review Focus

1. Projekt z brakującym entrypointem musi zostać odrzucony.
2. Niebezpieczne ścieżki zależności muszą zostać odrzucone.
3. Paczka z uszkodzonym checksumem musi zostać odrzucona.
4. Projekt z nieznaną klasą zależności musi zostać odrzucony.
5. Backend nie może stać się importem runtime aplikacji.

---

## Zadanie 1 — model projektu administracyjnego

**Pliki:**
- Utworzyć \`tools/tplugin_admin/project.py\`
- Utworzyć \`tests/test_tplugin_admin.py\`

**Interfejs:** \`TPluginProject.load(path) -> TPluginProject\`, \`validate() -> ValidationReport\`.

- [ ] Test odrzucający projekt bez manifestu projektu.
- [ ] Test akceptujący minimalny projekt z entrypointem.
- [ ] Test odrzucający nieznaną klasę A/B/C.
- [ ] Implementacja modelu i walidatora projektu.

## Zadanie 2 — backend budowania

**Pliki:**
- Utworzyć \`tools/tplugin_admin/backend.py\`
- Rozszerzyć \`tests/test_tplugin_admin.py\`

**Interfejs:** \`build(project_path, output_dir) -> BuildReport\`.

- [ ] Test: budowanie tworzy \`.tplugin\`.
- [ ] Test: raport zawiera inventory i checksumy.
- [ ] Test: błędny projekt nie jest budowany.
- [ ] Implementacja delegująca fizyczne pakowanie do istniejącego TPluginBuilder.

## Zadanie 3 — CLI administracyjne

**Pliki:**
- Utworzyć \`tools/tplugin_admin/__main__.py\`
- Utworzyć \`tools/tplugin_admin/cli.py\`
- Rozszerzyć testy.

Polecenia:
- \`init\`
- \`validate\`
- \`build\`
- \`inspect\`
- \`verify\`

- [ ] Test parsera i kodów zakończenia.
- [ ] Implementacja CLI.

## Zadanie 4 — ręczna specyfikacja

**Pliki:**
- Utworzyć \`docs/technical-docs/tplugin-reczne-tworzenie.md\`

Instrukcja ma pokazywać pełny proces:
źródła → manifest → A/B/C → struktura katalogów → inventory → checksums → ZIP → validate → instalacja testowa.

- [ ] Udokumentować minimalny plugin.
- [ ] Udokumentować shared dependency.
- [ ] Udokumentować entrypoint wskazujący shared JAR.
- [ ] Udokumentować testowanie i diagnostykę.

## Zadanie 5 — integracja dokumentacyjna i gate

**Pliki:**
- \`docs/STATUS.md\`
- \`docs/CHANGELOG.md\`
- \`docs/technical-docs/index.md\`
- \`docs/INDEX.yml\`
- \`docs/TODO.md\`

- [ ] Udokumentować moduł administracyjny.
- [ ] Dodać instrukcję ręcznego tworzenia do indeksu.
- [ ] Uruchomić testy modułu.
- [ ] Uruchomić pełny gate TPlugin.
- [ ] Zweryfikować, że \`src/tlumacz\` nie importuje \`tools.tplugin_admin\`.


## Wynik wykonania — 2026-10-06

Zadania 1–4 wykonane. Zadanie 5 wykonane w zakresie dokumentacji i gate; dalsze rozszerzenia workflow administracyjnego pozostają w TODO-TPLUGIN-004.

Weryfikacja:
- tests/test_tplugin_admin.py: 8 passed;
- skoncentrowany gate TPlugin: 43 passed;
- compileall: PASS;
- rzeczywisty CLI init → validate → build → verify → inspect: PASS;
- test wheel importu: PASS;
- pełny pytest: oczekiwane niezależne problemy Apertium/QML pozostają poza zakresem zmiany.
