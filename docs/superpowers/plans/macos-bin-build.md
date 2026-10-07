# Skrócony audyt: binarna dystrybucja macOS

**Data audytu:** 2026-09-20  
**Charakter dokumentu:** historyczny audyt procesu build; wynik testów w tym dokumencie nie jest bieżącym wynikiem projektu.  
**Zakres:** gotowość kodu do zbudowania aplikacji `.app` na macOS oraz sensowność automatyzacji w GitHub Actions.  
**Wynik:** **wykonalne, bez blokera w kodzie aplikacji**, lecz przed pierwszym wydaniem potrzebne są osobna specyfikacja PyInstaller dla macOS, wybór architektur oraz test rzeczywistego buildu na runnerze macOS.

## Stan obecny

Projekt jest aplikacją Python/PySide6 z punktem wejścia `tlumacz.qt_gui.app:main`. Bazowe zależności (`PySide6`, `PyMuPDF`, `openai` i `markdown-it-py`) są opisane w `pyproject.toml`, a zasoby GUI i wbudowane skille są zadeklarowane jako dane pakietu.

Istnieje działający wzorzec dla Windows:

- `.github/workflows/build-windows.yml` buduje aplikację przez PyInstaller;
- `build/windows/tlumacz.spec` dołącza pliki QSS, SVG i Markdown;
- opcjonalne backendy FastAPI, Transformers, Torch i OpenVINO są wykluczone z lekkiego artefaktu, a GUI obsługuje ich brak.

To podejście można przenieść na macOS. PyInstaller nie jest cross-kompilatorem, więc artefakt macOS musi powstawać na macOS — GitHub Actions z runnerem macOS spełnia ten warunek. [Dokumentacja PyInstaller](https://www.pyinstaller.org/en/stable/)  

## Ustalenia audytu

| Obszar | Ocena | Uzasadnienie |
|---|---|---|
| Kod Python i GUI | Gotowy do walidacji na macOS | Kod nie ma zależności wymagającej Windows lub Linuksa; ścieżki do czcionek obejmują macOS. |
| Zasoby aplikacji | Gotowe | Obecny spec już jawnie pakuje `tlumacz.qt_gui.resources` i `tlumacz.skills`; tę samą listę trzeba zachować w specyfikacji macOS. |
| Aktualny spec PyInstaller | Nie nadaje się bezpośrednio | Jest specem Windows: tworzy `Tlumacz.exe` i wskazuje `tlumacz.ico`. W macOS należy utworzyć pakiet `.app` z `BUNDLE`, identyfikatorem bundle oraz ikoną `.icns`. [Opcje speca macOS](https://pyinstaller.org/en/stable/spec-files.html) |
| Testy | Gotowe po zawężeniu ścieżki | W czasie audytu z 2026-09-20 `python -m pytest tests -q` zakończyło się wynikiem **278 passed**. Jest to wynik historyczny; bieżący wynik projektu znajduje się w `docs/STATUS.md`. Nie używać samego `pytest -q` bez uwzględnienia konfiguracji `testpaths` i stanu working tree. |
| Architektura | Wymaga decyzji wydaniowej | Najprostsze i najbardziej przewidywalne są dwa artefakty: `arm64` dla Apple Silicon oraz `x86_64` dla starszych Maców Intel. Nie należy zakładać, że `macos-latest` jest Intelem — aktualnie jest runnerem arm64; GitHub udostępnia osobne etykiety Intel. [Lista runnerów GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job) |
| Podpis i Gatekeeper | Niezbędne do publicznej dystrybucji, nie do testowego artefaktu | Testowe `.app` można wytworzyć bez konta Apple. Publiczny pakiet pobierany spoza App Store powinien być podpisany certyfikatem Developer ID, z hardened runtime i notarized. [Wymagania Apple dla notarization](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution) |

## Ryzyka nieblokujące

1. `tlumacz/server.py` używa narzędzia `ss`, typowego dla Linuksa, do sprawdzania zajętego portu. Na macOS zwykle go nie ma. Kod ma częściowy fallback do `lsof`, ale `_is_port_busy()` bez `ss` zwraca `False`. Budowanie nie ucierpi, natomiast automatyczne zarządzanie `llama-server` może gorzej obsłużyć port zajęty przez osierocony proces.
2. Katalog konfiguracji domyślnie jest `$HOME/.config/tlumacz`; działa na macOS, ale nie stosuje konwencji `$HOME/Library/Application Support`. To decyzja UX, nie warunek wydania.
3. Aplikacja odczytuje awaryjnie `HF_TOKEN` z `$HOME/.bashrc`, a domyślną powłoką macOS jest zwykle zsh. Preferowanym sposobem przekazania klucza powinno być środowisko procesu lub konfiguracja użytkownika.
4. Backend OpenVINO pozostaje poza podstawową paczką, tak jak w Windows. Artefakt macOS powinien jasno komunikować, że obsługuje backend chmurowy lub zewnętrzny `llama-server`; rozszerzenia opcjonalne należy testować i pakować osobno.

## Rekomendowany pierwszy workflow GitHub Actions

Najpierw należy dodać workflow budujący **niepodpisane artefakty testowe**, a podpis i notarization wprowadzić dopiero po potwierdzeniu poprawności `.app`. Szkielet powinien:

1. uruchamiać się ręcznie i po tagach `v*`;
2. budować macOS osobno dla `arm64` i `x86_64` (`macos-15` oraz `macos-15-intel`, z przypiętymi etykietami zamiast dryfującego `macos-latest`);
3. instalować `pip install -e . pyinstaller pytest fastapi uvicorn`;
4. uruchamiać **dokładnie** `python -m pytest tests -q` z `QT_QPA_PLATFORM=offscreen`;
5. uruchamiać nowy `build/macos/tlumacz.spec`, który tworzy `dist/Tlumacz.app` i zawiera zasoby znane ze specyfikacji Windows;
6. wykonywać smoke test struktury (`test -d dist/Tlumacz.app`, `test -x dist/Tlumacz.app/Contents/MacOS/Tlumacz`) i pakować `.app` do ZIP przed uploadem artefaktu;
7. na etapie wydaniowym podpisywać każdy binarny składnik pakietu, a następnie przesyłać ZIP lub DMG do notaryzacji przez `notarytool` i dołączać ticket przez `stapler`.

PyInstaller dla aplikacji okienkowej na macOS tworzy bundle `.app`; spec może ustawić `BUNDLE`, ikonę, `Info.plist`, `CFBundleIdentifier` i wersję. [Dokumentacja speców PyInstaller](https://pyinstaller.org/en/stable/spec-files.html)  

## Proponowana kolejność wdrożenia

1. Dodać `build/macos/tlumacz.spec` oraz ikonę `.icns`, bez naruszania speca Windows.
2. Dodać testowy workflow i potwierdzić po jednym buildzie `arm64` oraz `x86_64`.
3. Przetestować pobrany `.app` na prawdziwym Macu dla obu architektur — CI potwierdza utworzenie pakietu, ale nie zastępuje ręcznego startu GUI i otwierania dokumentów.
4. Dopiero następnie dodać sekrety Apple i etap podpisu/notaryzacji do wydań tagowanych.

## Konkluzja

Nie ma przesłanki, że aplikacji nie da się zbudować dla macOS. Największa praca to **pakowanie i wydawanie**, a nie przenoszenie logiki biznesowej: osobny `.app`/`.icns`, świadome rozdzielenie `arm64` i `x86_64`, doprecyzowany test CI oraz później podpis Apple. Jedyny problem w samej automatyzacji, który należy naprawić od razu, to wywoływanie testów jako `pytest tests -q` zamiast globalnego zbierania całego katalogu roboczego.
