# Faza 6 — Apertium: dependency inventory i licencje

Data: 2026-09-30

## Dependency inventory

Warstwa Python Apertium korzysta z biblioteki standardowej Python oraz własnych modułów V4. Nie dodano nowej zależności PyPI dla backendu Apertium.

Runtime natywny:
- rozmiar: 68 MB;
- binarium uruchamia się z katalogu aplikacji;
- `ldd` wskazuje bundled `libc.so.6` oraz systemowy loader `ld-linux-x86-64.so.2`;
- runtime nie jest instalowany podczas działania programu.

## Licencje

W artefakcie znajduje się `LICENSES/apertium-eng-spa-COPYING` zawierający GNU General Public License.

Wniosek migracyjny: artefakt nie może być traktowany jako bezlicencyjny asset aplikacji. Dokumentacja dystrybucyjna V4 musi zachować właściwe notices/licencje. Niniejszy raport nie stanowi opinii prawnej.

## Ograniczenie

Bundled native runtime nie zawiera kompletnego zestawu paczek językowych; są one obsługiwane przez osobny mechanizm language plugins.

Weryfikacja:
- inwentaryzacja importów — PASS;
- inspekcja natywnych zależności — PASS;
- obecność notice/licencji — PASS;
- pełny pytest po zmianach — 117 passed.
