---
id: audyt-ponytail-2026-10-03
status: evidence
meta:
  contentType: Audit
  category: audit
version: 1.0.0
updated: 2026-10-05
owner: project-maintenance
source: src/tlumacz/, tests/
depends_on: [docs/AGENTS.md, docs/STATUS.md]
expires_when: ponowny audyt nadmiarowego kodu po kolejnej większej zmianie strukturalnej
last_validation: "przeniesienie i klasyfikacja dokumentacji SentinelX 2026-10-05"
---

# Audyt kodu — Tłumacz V4

**Data:** 2026-10-03
**Zakres:** całe drzewo `src/` (70 plików .py + 6 .qml, 8961 linii) oraz `tests/` (64 pliki, 4931 linii).
**Typ audytu:** ponytail-audit — nadmiarowa złożoność i over-engineering.
**Poza zakresem:** poprawność, bezpieczeństwo, wydajność (do osobnego przeglądu).

Legenda: `delete:` martwy kod / spekulacja · `stdlib:` ręcznie pisane to, co daje biblioteka standardowa · `native:` zależność robiąca to, co robi platforma · `yagni:` abstrakcja z jednym użyciem, konfig nikt nie ustawia, warstwa z jednym wywołaniem · `shrink:` ta sama logika, mniej linii.

Uwaga: to raport jednorazowy — **nic nie zostało zmienione**.

---

## Znaleziska (od największej redukcji)

1. `delete:` 42 pliki kopii zapasowych `.bak.*` / `.pre-*` w `src/` i `tests/` — **13 432 linie** (więcej niż cały kod źródłowy). Kopią zapasową jest git, nie pliki w drzewie. Usunąć wszystkie; wyjątkiem objąć `resources/cloud_models.json.bak.*`. [src, tests]

2. `shrink:` `bridge.py` — 1569 linii, **122 `@Property` i 85 `@Slot`**, przy czym 103 definicje są w `camelCase`, a 91 w `snake_case`; każda własność i metoda istnieje dwa razy (`backend_type`/`backendType`, `backend_types`/`backendTypes`, …). QML i tak woła tylko jedną konwencję — zostawić `camelCase`, usunąć lustrzane `snake_case`. ~450 linii mniej. [src/tlumacz/qml_gui/bridge.py]

3. `delete:` 88 kluczy i18n nieużywanych w żadnym pliku `.py`/`.qml`/`.md` × 3 języki (PL/EN/DE) = **264 martwe wpisy, ~264 linie**. W tym resztki usuniętych funkcji (`settings.simplytranslate_engine`, `button.start_server`, `settings.auto_start`, `help.polish`). Wygenerować listę i wyciąć z `PL`/`EN`/`DE`. [src/tlumacz/i18n.py]

4. `delete:` duplikaty kluczy w każdym ze słowników: `glossary.count`, `glossary.translation`, `settings.skills_group` występują dwukrotnie (drugi cicho nadpisuje pierwszy). [src/tlumacz/i18n.py]

5. `delete:` `TranslationController` + `TranslationOperation` — klasa 92 linii, używana wyłącznie we własnym `__all__` i we własnych testach. Zero wywołań w kodzie produkcyjnym. [src/tlumacz/application/translation_controller.py]

6. `yagni:` 4 kontrolery tworzone w `TranslationApp.__init__` i **nigdy nieużywane**: `ProgressController`, `SettingsController`, `DocumentController`, `DiagnosticsController` (linie 57–60). Konstrukcja bez konsumenta. [src/tlumacz/application/translation_app.py]

7. `yagni:` `BackendController` — trzecia warstwa wyboru backendu obok `BackendRegistry` i `BackendService`; z całego API wołane jest tylko `.select()`. `supported`/`set_health`/`is_healthy` bez konsumenta. [src/tlumacz/application/backend_controller.py]

8. `yagni:` `BackendRequest` ≡ `BackendSelection` — identyczne `dataclass(frozen, slots)` o tych samych 10 polach; `BackendService.selection()` przepisuje pole po polu. Zostawić jeden typ. [application/backend_service.py, application/backend_registry.py]

9. `delete:` `DocumentProcessor._unit_parts` — statyczna metoda, zero wywołań (pętla i tak ma logikę inline). [src/tlumacz/filter_engine/processor.py]

10. `delete:` `CloudProviderRegistry.get()` i `.names()` — zero wywołań. [src/tlumacz/backends/cloud/providers.py]

11. `delete:` `profile_migration.py` + `migrate_cloud_profiles` — plik 52 linii istnieje tylko po to, by być re-eksportowanym w `__init__`; żaden moduł go nie woła. [src/tlumacz/backends/cloud/profile_migration.py]

12. `delete:` `CLOUD_PROVIDER_NAMES` — zero użycia poza re-eksportem w `__init__`. [src/tlumacz/backends/cloud/providers.py]

13. `delete:` `_split_utf8` wystawiony w `__all__` — wewnętrzny helper (jedno wywołanie lokalne), nie część API. [src/tlumacz/backends/cloud/providers.py]

14. `delete:` puste pakiety `tlumacz/filters/` i `tlumacz/interfaces/` — każdy zawiera wyłącznie `__init__.py` z `"""V4 package."""`; nikt ich nie importuje. (Realny kod filtrów jest w `filter_engine/filters/`.) [src/tlumacz/filters, src/tlumacz/interfaces]

15. `shrink:` `MarkerValidator.validate()` zwraca `text`, którego **żaden wywołujący nie używa** — to walidator, nie transformacja; zwracać `None`. [src/tlumacz/filter_engine/marker_validator.py]

16. `delete:` testy utrwalające martwy kod — `tests/test_translation_controller.py`, `tests/test_gui_controllers_contract.py` trzymają przy życiu `TranslationController` i kontrolery z pkt 6–7. Usunąć razem z kodem. [tests]

17. `stdlib:` własny system lokalizacji (ręczne słowniki `PL`/`EN`/`DE` + `set_language`/`t`) zamiast `gettext`/`QLocale`. Do rozważenia przy okazji sprzątania i18n — nie blokuje reszty. [src/tlumacz/i18n.py]

---

## Podsumowanie

- **Największa redukcja:** pliki `.bak` (13 432 linie) — zero ryzyka, usunąć w pierwszej kolejności.
- **Największa redukcja w kodzie produkcyjnym:** deduplikacja `bridge.py` (~450 linii) i czyszczenie i18n (~264 linie).
- **Martwy kod do wycięcia w całości:** `TranslationController`, `profile_migration`, 4 nieużywane kontrolery, 2 puste pakiety, 3 martwe metody/stałe.
- **Wszystkie znaleziska są bezpieczne do usunięcia** (brak wywołań), ale wymagają zielonych testów po zmianie.

`net: -14500 linii, -0 zależności możliwych.`

---

*Raport wygenerowany przez ponytail-audit. Nie zastosowano żadnych poprawek.*
