---
id: build-v4
status: active
meta:
  contentType: BuildGuide
  category: release
version: 0.40.0
updated: 2026-10-07
owner: project-maintenance
depends_on: [docs/BUG.md, docs/STATUS.md]
---

# V4 — canonical build i release smoke

## Dlaczego build odbywa się poza nadrzędnym checkoutem

tlumacz-v4 znajduje się obecnie wewnątrz /home/frs/Projekty, który ma problem z Git ownership w środowisku wykonawczym. Nie należy zmieniać globalnego safe.directory jako części builda V4.

Canonical build tworzy czystą kopię aktualnego source poza nadrzędnym checkoutem, a następnie buduje wheel z tej kopii.

## Canonical wheel

Wymagania: Python zgodny z pyproject.toml, zależności projektu, pakiet build.

    tmp="$(mktemp -d)"
    mkdir -p "$tmp/src" "$tmp/licenses" "$tmp/dist"

    cp -a src/. "$tmp/src/"
    cp pyproject.toml README.md LICENSE NOTICE "$tmp/"
    cp -a licenses/. "$tmp/licenses/"

    python -m build --wheel --no-isolation --outdir "$tmp/dist" "$tmp"

Wynik należy audytować przed publikacją. Minimalny audit musi potwierdzić obecność:
- tlumacz/frsststems_logo_full.svg
- tlumacz/tlumacz-dark.svg
- tlumacz/tlumacz-light.svg
- tlumacz/backends/apertium/native_runtime/VERSION
- tlumacz/backends/apertium/native_runtime/bin/apertium
- tlumacz/backends/apertium/native_runtime/libexec/apertium-real
- brak danych językowych w `native_runtime/share/apertium/`
- brak archiwów par językowych `.tar` w wheel
- brak wycofanych kontrolerów GUI

Dane językowe Apertium nie są częścią wheel. Są dostarczane jako osobne paczki `.tar` + `.sha256` w magazynie użytkownika (`$HOME/.config/tlumacz/apertium`). Clean-install smoke musi skopiować reprezentatywną paczkę, np. `tests/fixtures/apertium/apertium-eng-pol-1.0.0.tar` wraz z checksumem, do izolowanego magazynu przed uruchomieniem rzeczywistego tłumaczenia. Testy lokalne domyślnie korzystają z magazynu użytkownika `$HOME/.config/tlumacz/apertium`; źródło testowe można nadpisać przez `TLUMACZ_APERTIUM_PACKAGE_SOURCE`.

## Clean install smoke

Wheel instaluje się do czystego katalogu bez modyfikowania środowiska systemowego:

    install_root="$(mktemp -d)"
    python -m pip install --no-deps --target "$install_root" dist/*.whl
    PYTHONPATH="$install_root" python -m tlumacz --help

Release smoke musi dodatkowo:
1. wykryć parę Apertium eng-pol;
2. wykonać rzeczywiste eng → pol;
3. załadować qml_gui/Main.qml w QT_QPA_PLATFORM=offscreen;
4. potwierdzić obecność wszystkich assetów SVG.

## CI

Canonical pipeline znajduje się w .github/workflows/quality-gate.yml i obejmuje Ruff, mypy, pytest, compileall, qmllint, clean-source wheel build, wheel audit oraz clean-install/product smoke.


## Inicjalizacja katalogu użytkownika przy instalacji ze źródeł

Kanoniczna instalacja ze źródeł odbywa się przez ./instaluj-zrodla.sh. Po instalacji skrypt wywołuje initialize_user_config(), która tworzy $HOME/.config/tlumacz/ oraz puste katalogi skills/, filters/, apertium/ i logs/.

Wzorce config.json, llama.json i cloud_models.json pochodzą z repozytoryjnego config/. Są dołączane do pakietu jako resources/default-config/*.json. Mechanizm nigdy nie kopiuje plików z istniejącego $HOME/.config/tlumacz/ do nowej instalacji.

Istniejące pliki konfiguracji użytkownika nie są nadpisywane podczas ponownej instalacji.
