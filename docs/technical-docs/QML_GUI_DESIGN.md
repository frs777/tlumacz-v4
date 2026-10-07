## 2026-10-07 — PLAN-14: fallback Fusion po weryfikacji skuteczności Qt

Aktualny launcher nadal preferuje natywny QStyleHints.setColorScheme() / unsetColorScheme(). Diagnostyka Qt wykazała jednak, że w środowisku bez wsparcia platformowego setColorScheme() nie zmienia palety QGuiApplication, więc jawny Ciemny / Jasny otrzymuje ograniczony fallback pełnej palety Fusion.

Fallback jest wykonywany wyłącznie dla dark / light i tylko wtedy, gdy po przetworzeniu zdarzeń paleta aplikacji nadal nie odpowiada żądanemu schematowi. Systemowy nie korzysta z fallbacku: unsetColorScheme() oraz QPalette() przywracają natywną paletę stylu/platformy.

Main.qml nadal nie definiuje lokalnej pełnej palety. Standardowe kontrolki Qt Quick Controls pozostają przy Fusion.

Weryfikacja kodowa: regresje motywu 4 passed, tests/test_qml_gui.py 157 passed, pełny suite 573 passed, compileall — PASS, qmllint — PASS.

Weryfikacja rzeczywistej sesji KDE pozostaje ograniczona przez SentinelX: agent działa jako sentinelx i nie może użyć ciasteczka X ani magistrali DBus sesji UID 1000. Nie zmieniano uprawnień sesji ani nie obchodzono tego ograniczenia.

Backup: backups/20261007-theme-regression-pre-fix/theme-regression-pre-fix.tar.gz, SHA-256 a1193162b417d8567dcd15eb3edebcc9e93ef9ce026f23a950744d8c50f16c3b.

---

## 2026-10-07 — motyw Fusion przez natywny mechanizm Qt

Bieżący mechanizm wyboru `Systemowy` / `Ciemny` / `Jasny` nie buduje własnej palety `QPalette`. `src/tlumacz/qml_gui/app.py` przekazuje wybór bezpośrednio do `QGuiApplication.styleHints().setColorScheme()` albo `unsetColorScheme()`. `Main.qml` nie definiuje już ról `palette.*`; tło korzysta z `palette.window`, a standardowe kontrolki Fusion dziedziczą domyślną paletę dostarczaną przez Qt.

Kolejność inicjalizacji pozostaje krytyczna: schemat jest ustawiany przed utworzeniem `QQmlApplicationEngine`. Dla `Systemowy` wykonywane jest `unsetColorScheme()`, więc Qt wraca do rzeczywistego schematu platformy. Dla `Ciemny` / `Jasny` aplikacja prosi platform theme o odpowiedni schemat. Jest to dokładnie natywny mechanizm przewidziany przez Qt, ale dokumentacja Qt zastrzega, że jawne wymuszenie schematu jest zależne od wsparcia platformy.

Weryfikacja: `qmllint` — PASS; ukierunkowane testy GUI — **12 passed**. W trybie `offscreen` oraz w izolowanym Xvfb mechanizm platformowy zwraca `Unknown` / nie zmienia palety, co jest zgodne z ograniczeniem wsparcia platformy; nie traktujemy tego jako dowodu poprawnego runtime na rzeczywistej sesji KDE.

Backup przed zmianą: `backups/20261007-122616-theme-qstylehints/`.

---

### Historia poprzedniej implementacji

## 2026-10-07 — motyw Fusion i paleta Qt

`Ciemny` / `Jasny` korzystają z pełnej palety Qt przekazywanej do Fusion, natomiast `Systemowy` zachowuje rzeczywistą paletę dostarczaną przez platformę (`QPalette`). Próba wymuszenia `Qt::ColorScheme` przez `QStyleHints` została wycofana: w środowisku projektu zmiana schematu nie aktualizowała palety używanej przez Fusion/Qt Quick Controls, więc nie dawała zmiany wizualnej. Qt dokumentuje `QStyleHints::setColorScheme()` jako mechanizm zależny od wsparcia platformy, a Fusion opiera się na standardowej palecie systemowej.

Backup przed zmianą: `backups/20261007-theme-system-fallback/`.

## 2026-10-07 — obramowania kart

Jawne obramowania kart w `HelpPage.qml` oraz powierzchni tekstowej `ApiPage.qml` mają szerokość `0.5`, zamiast domyślnego/efektywnie stosowanego `1 px`. Zmiana dotyczy wyłącznie wizualnej grubości obramowania i nie zmienia geometrii kart ani stylu Qt Quick Controls.

**Uwaga historyczna:** wcześniejsza implementacja ręcznej palety została zastąpiona natywnym mechanizmem `QStyleHints`; aktualny kontrakt opisuje sekcja „motyw Fusion przez natywny mechanizm Qt”.

Weryfikacja 2026-10-07: `qmllint` — PASS; `tests/test_qml_gui.py` — **153 passed**.

## 2026-10-07 — powierzchnia treści Pomocy bez ramki

`HelpMarkdownView.qml` nie stosuje widocznego obramowania powierzchni tekstu. `Rectangle#surface` ma `border.width: 0`; kolor obramowania pozostaje zdefiniowany wyłącznie jako wartość nieaktywna, aby nie wprowadzać ramki do widoku Pomocy.

## 2026-10-07 — kontrakt inicjalizacji motywu

Schemat kolorów Qt musi zostać ustawiony na `QGuiApplication` **przed utworzeniem `QQmlApplicationEngine`**. Projekt pozostawia systemowy styl Qt Quick Controls bez wymuszania `Material`/`Basic`; na Linuksie działa `Fusion`, który korzysta ze standardowej palety systemowej.

Kontrakt launcher'a `src/tlumacz/qml_gui/app.py`:
1. utworzyć `QGuiApplication`;
2. utworzyć `QmlApplicationBridge` i odczytać motyw;
3. dla `system` wykonać `unsetColorScheme()`;
4. dla `dark` / `light` wykonać `setColorScheme()`;
5. dopiero potem utworzyć `QQmlApplicationEngine` i ładować `Main.qml`.

Nie wolno wymuszać innego stylu tylko po to, aby naprawić motyw ani wpisywać ręcznie ról `palette.*` w `Main.qml`.

---




## 2026-10-07 — motyw systemowy jako jedyna opcja GUI

Na podstawie decyzji użytkowej z 2026-10-07 karta **Pomoc** nie udostępnia obecnie wyboru motywu. Aplikacja uruchamia się i pozostaje przy motywie systemowym KDE/Qt.

Kod obsługujący system / dark / light, `QStyleHints`, fallback Fusion oraz sygnał `themeChanged` pozostaje w projekcie. Jest celowo zachowany z komentarzem w `bridge.py`, aby można było przywrócić wybór motywu po rozwiązaniu problemu z rzeczywistym przełączaniem schematu.

Dialog **O programie** zawiera klikalny odnośnik do strony projektu: https://frs777.github.io/tlumacz-v4/zrzuty.html.


### Umiejętności użytkownika — usuwanie

W sekcji **Skille** każda umiejętność użytkownika jest prezentowana jako wiersz z przełącznikiem oraz przyciskiem usuwania na jego prawym końcu. Przycisk korzysta z ikony systemowej `window-close`, ma nazwę dostępnościową i tooltip `ui.delete_skill`, a kliknięcie wywołuje `bridge.deleteSkill(modelData)`.
