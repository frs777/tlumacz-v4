# STATUS DOKUMENTU: HISTORYCZNY / V3

> Ten dokument opisuje historyczny proces budowania Tłumacza V3. Nie jest instrukcją aktywnego V4. Aktualny stan Windows V4: brak kompletnego natywnego runtime'u; obecny artefakt 0.40.0 jest RC dla Linux x86-64. Nie reaktywować FastAPI/OpenVINO na podstawie tego dokumentu.

# Raport: Budowanie wersji Windows dla Agent Translator V3

**Data:** 2026-09-10  
**Zakres:** Wersja Python (obecna) + wersja C++ (hipotetyczna)  
**Cel:** Analiza możliwości budowania dystrybucji Windows z Linux i GitHub Actions

---

## Streszczenie

**Wersja Python:** Budowanie dla Windows z Linux jest **wykonalne** przez cross-compile (PyInstaller, cx_Freeze) lub native build w GitHub Actions (windows-latest runner). Stopień trudności: **średni**.

**Wersja C++:** Budowanie dla Windows z Linux jest **bardzo trudne** (MinGW cross-compile). Zalecane: native build w GitHub Actions (windows-latest z MSVC). Stopień trudności: **wysoki**.

**GitHub Actions:** Darmowy tier oferuje **2000 minut/miesiąc** dla prywatnych repozytoriów — wystarczające dla buildów Windows.

---

## 1. Wersja Python (obecna) — budowanie dla Windows

### 1.1 Opcje budowania

#### Opcja A: PyInstaller (zalecana)

**Opis:** Pakuje aplikację Python + zależności do pojedynczego pliku .exe

**Narzędzia:**
```bash
pip install pyinstaller
```

**Komenda build:**
```bash
pyinstaller --onefile --windowed \
  --name "Tlumacz" \
  --icon=tlumacz/qt_gui/resources/icon.ico \
  --add-data "tlumacz/skills:tlumacz/skills" \
  --add-data "tlumacz/qt_gui/resources:tlumacz/qt_gui/resources" \
  --hidden-import PySide6.QtCore \
  --hidden-import PySide6.QtGui \
  --hidden-import PySide6.QtWidgets \
  tlumacz/qt_gui/app.py
```

**Wynik:** `dist/Tlumacz.exe` (~150-200MB)

**Zalety:**
- Single file executable
- Brak konieczności instalacji Pythona
- Automatyczne wykrywanie zależności

**Wady:**
- Duży rozmiar (bundluje cały interpreter + Qt)
- Wolny start (~2-3s)
- Antivirus może flagować jako false positive

#### Opcja B: cx_Freeze

**Opis:** Alternatywa dla PyInstaller, pakuje do katalogu z plikami

**Narzędzia:**
```bash
pip install cx_Freeze
```

**setup.py:**
```python
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["PySide6", "openai", "sqlite3"],
    "include_files": [
        ("tlumacz/skills/", "skills/"),
        ("tlumacz/qt_gui/resources/", "resources/"),
    ],
}

setup(
    name="Tlumacz",
    version="0.30.0",
    description="AI-powered document translator",
    options={"build_exe": build_exe_options},
    executables=[Executable("tlumacz/qt_gui/app.py", base="Win32GUI")],
)
```

**Komenda:**
```bash
python setup.py build
```

**Wynik:** Katalog `build/` z plikami (~200-250MB)

#### Opcja C: wheel + pip (dla developerów)

**Opis:** Standardowy pakiet Python do instalacji przez pip

**Komenda:**
```bash
python -m build --wheel
```

**Wynik:** `dist/tlumacz-0.30.0-py3-none-any.whl`

**Instalacja na Windows:**
```bash
pip install tlumacz-0.30.0-py3-none-any.whl
```

### 1.2 Cross-compile z Linux → Windows

**Problem:** PyInstaller i cx_Freeze **nie obsługują cross-compile**. Musisz budować na Windows (lub użyć Wine z ograniczeniami).

**Rozwiązania:**

#### Rozwiązanie 1: GitHub Actions (zalecane)

Buduj na windows-latest runner:

```yaml
# .github/workflows/build-windows.yml
name: Build Windows

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pyinstaller
    
    - name: Build executable
      run: |
        pyinstaller --onefile --windowed \
          --name "Tlumacz" \
          --icon=tlumacz/qt_gui/resources/icon.ico \
          --add-data "tlumacz/skills;tlumacz/skills" \
          --add-data "tlumacz/qt_gui/resources;tlumacz/qt_gui/resources" \
          tlumacz/qt_gui/app.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: Tlumacz-Windows
        path: dist/Tlumacz.exe
    
    - name: Create Release
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v2
      with:
        files: dist/Tlumacz.exe
```

**Koszt:** ~10-15 minut build, w ramach darmowych 2000 minut/miesiąc

#### Rozwiązanie 2: Wine + PyInstaller (eksperymentalne)

```bash
# Instalacja Wine
sudo apt install wine64

# Instalacja Pythona w Wine
wine python-3.11.0-amd64.exe /S

# Budowanie (niestabilne)
wine pyinstaller --onefile app.py
```

**Uwaga:** Niezalecane — problemy z PySide6/Qt, niestabilne.

### 1.3 Zależności dla Windows build

| Zależność | Wersja | Rozmiar | Uwagi |
|-----------|:---:|:---:|-------|
| Python | 3.10+ | ~30MB | Bundlowany w .exe |
| PySide6 | 6.5+ | ~80MB | Qt 6 dla Pythona |
| openai | 1.0+ | ~2MB | SDK dla API |
| PyMuPDF | 1.24+ | ~15MB | Parsowanie PDF |
| PyInstaller | 6.0+ | ~10MB | Tool do budowania |

**Łączny rozmiar dystrybucji:** ~150-200MB (spakowany)

### 1.4 Stopień trudności

| Aspekt | Trudność | Komentarz |
|--------|:---:|-----------|
| Konfiguracja PyInstaller | ⚠️ Średnia | Wymaga testowania hidden-imports |
| GitHub Actions setup | ✅ Łatwa | Gotowe szablony |
| Cross-compile z Linux | ❌ Trudna | Nie wspierane oficjalnie |
| Debugowanie na Windows | ⚠️ Średnia | Brak lokalnego środowiska |
| Signing .exe (opcjonalne) | ⚠️ Średnia | Wymaga certyfikatu code signing |

**Ogólna ocena:** ⚠️ **Średni** — wykonalne z GitHub Actions

---

## 2. Wersja C++ (hipotetyczna) — budowanie dla Windows

**Zakres:** Tylko backendy llama.cpp i Cloud API. FastAPI (TranslateGemma) i OpenVINO NIE są objęte.

### 2.1 Opcje budowania

#### Opcja A: MSVC (Microsoft Visual C++) — zalecana

**Narzędzia:**
- Visual Studio 2022 Community (darmowe)
- Qt 6.x dla Windows (MSVC 2022 64-bit)
- CMake 3.21+

**Setup na Windows:**
```powershell
# 1. Instalacja Visual Studio Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools

# 2. Instalacja Qt
# Pobierz z: https://www.qt.io/download
# Wybierz: Qt 6.x → MSVC 2022 64-bit

# 3. Instalacja CMake
winget install Kitware.CMake
```

**Komenda build:**
```powershell
# Konfiguracja
cmake -B build -G "Visual Studio 17 2022" -A x64 ^
  -DCMAKE_PREFIX_PATH="C:/Qt/6.7.0/msvc2022_64"

# Kompilacja
cmake --build build --config Release
```

**Wynik:** `build/release/Tlumacz.exe` (~20-30MB)

#### Opcja B: MinGW-w64 (cross-compile z Linux)

**Narzędzia na Linux:**
```bash
sudo apt install mingw-w64 cmake qt6-base-dev

# Lub cross-compile toolchain
sudo apt install gcc-mingw-w64 g++-mingw-w64
```

**Problem:** Qt 6 dla MinGW jest **słabo wspierany** — wiele modułów nie działa lub wymaga patchy.

**Komenda cross-compile:**
```bash
# Toolchain file: mingw-w64-toolchain.cmake
set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_C_COMPILER x86_64-w64-mingw32-gcc)
set(CMAKE_CXX_COMPILER x86_64-w64-mingw32-g++)

# Konfiguracja
cmake -B build-mingw \
  -DCMAKE_TOOLCHAIN_FILE=mingw-w64-toolchain.cmake \
  -DCMAKE_PREFIX_PATH="/usr/x86_64-w64-mingw32/qt6"

# Kompilacja
cmake --build build-mingw
```

**Uwaga:** Niezalecane — problemy z Qt6, PyMuPDF, openai SDK.

#### Opcja C: GitHub Actions (zalecane dla C++)

```yaml
# .github/workflows/build-windows-cpp.yml
name: Build Windows (C++)

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows-cpp:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install Qt
      uses: jurplel/install-qt-action@v4
      with:
        version: '6.7.0'
        host: 'windows'
        target: 'desktop'
        arch: 'win64_msvc2022_64'
    
    - name: Configure CMake
      run: |
        cmake -B build -G "Visual Studio 17 2022" -A x64
    
    - name: Build
      run: |
        cmake --build build --config Release
    
    - name: Deploy Qt DLLs
      run: |
        windeployqt build/release/Tlumacz.exe
    
    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: Tlumacz-Windows-CPP
        path: build/release/
```

### 2.2 Zależności dla Windows build (C++ — tylko llama.cpp + Cloud API)

| Zależność | Wersja | Rozmiar | Uwagi |
|-----------|:---:|:---:|-------|
| Visual Studio Build Tools | 2022 | ~8GB | MSVC compiler |
| Qt 6.x | 6.5+ | ~2GB | Framework GUI |
| CMake | 3.21+ | ~50MB | Build system |
| MuPDF | 1.24+ | ~10MB | Parsowanie PDF |
| libcurl | 8.0+ | ~2MB | HTTP client (Cloud API) |
| SQLite | 3.40+ | ~2MB | Cache (wbudowane w Qt) |

**Uwaga:** Brak zależności FastAPI/Transformers/Torch/OpenVINO — tylko llama.cpp (subprocess) i Cloud API (libcurl).

**Łączny rozmiar środowiska build:** ~10GB  
**Łączny rozmiar dystrybucji:** ~50-80MB (z Qt DLLs)

### 2.3 Cross-compile z Linux → Windows (C++)

**Status:** ❌ **Odradzane**

**Problemy:**
1. Qt 6 dla MinGW jest niestabilny
2. Brak gotowych bindingów dla MuPDF
3. Konieczność cross-compile wszystkich zależności
4. Debugowanie jest ekstremalnie trudne

**Alternatywa:** Użyj GitHub Actions z windows-latest runner.

### 2.4 Stopień trudności (tylko llama.cpp + Cloud API)

| Aspekt | Trudność | Komentarz |
|--------|:---:|-----------|
| Konfiguracja CMake | ⚠️ Średnia | Wymaga znajomości CMake |
| Qt 6 setup | ⚠️ Średnia | Instalacja + konfiguracja |
| MSVC compilation | ✅ Łatwa | Standardowy workflow |
| Cross-compile z Linux | ❌ Bardzo trudna | Nie wspierane |
| GitHub Actions setup | ⚠️ Średnia | Wymaga konfiguracji Qt |
| Debugowanie na Windows | ⚠️ Średnia | Visual Studio Debugger |
| Backend llama.cpp (subprocess) | ✅ Łatwa | QProcess — prosta integracja |
| Backend Cloud API (libcurl) | ⚠️ Średnia | Wymaga wrapperów HTTP |
| Integracja MuPDF | ⚠️ Średnia | C API dostępne, ale wymaga wrapperów |

**Ogólna ocena:** ⚠️ **Średni-Wysoki** — bez FastAPI jest łatwiej, ale nadal wymaga doświadczenia z C++/Qt

---

## 3. GitHub Actions — darmowa przestrzeń

### 3.1 Limity darmowego tieru

| Zasób | Limit | Komentarz |
|-------|:---:|-----------|
| Minuty build/miesiąc | **2000** | Wystarczające dla 50-100 buildów |
| Storage (artifacts) | **500MB** | Wystarczające dla 2-3 wersji |
| Concurrent jobs | **20** | Więcej niż wystarczy |
| Runner types | linux, windows, macos | Wszystkie dostępne |

### 3.2 Koszt buildu Windows

| Wersja | Czas build | Koszt minut | Uwagi |
|--------|:---:|:---:|-------|
| Python (PyInstaller) | ~10-15 min | 10-15 min | Szybki |
| C++ (MSVC + Qt) | ~20-30 min | 20-30 min | Wolniejszy (kompilacja Qt) |

**Miesięczny budżet:**
- 2000 minut / 15 minut = **~133 buildy Python**
- 2000 minut / 30 minut = **~66 buildów C++**

### 3.3 Rekomendacja

**Tak, da się zbudować w darmowej przestrzeni GitHub Actions.**

Przykład workflow dla obu wersji:

```yaml
# .github/workflows/build-all.yml
name: Build All Platforms

on:
  push:
    tags:
      - 'v*'

jobs:
  # Python version
  build-windows-python:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e . pyinstaller
      - run: pyinstaller --onefile --windowed tlumacz/qt_gui/app.py
      - uses: actions/upload-artifact@v4
        with:
          name: Tlumacz-Windows-Python
          path: dist/

  # C++ version (jeśli istnieje)
  build-windows-cpp:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jurplel/install-qt-action@v4
        with:
          version: '6.7.0'
      - run: cmake -B build -G "Visual Studio 17 2022"
      - run: cmake --build build --config Release
      - uses: actions/upload-artifact@v4
        with:
          name: Tlumacz-Windows-CPP
          path: build/release/
```

---

## 4. Porównanie wersji Python vs C++ dla Windows

| Kryterium | Python (PyInstaller) | C++ (MSVC) |
|-----------|:---:|:---:|
| **Rozmiar dystrybucji** | ~150-200MB | ~50-80MB |
| **Czas startu** | ~2-3s | ~0.5-1s |
| **Zużycie RAM** | ~200MB | ~80MB |
| **Czas build** | ~10-15 min | ~20-30 min |
| **Trudność build** | ⚠️ Średnia | ❌ Wysoka |
| **Cross-compile z Linux** | ❌ Nie | ❌ Nie (odradzane) |
| **GitHub Actions** | ✅ Tak | ✅ Tak |
| **Zależności build** | ~100MB | ~10GB |
| **Debugowanie** | ⚠️ Średnie | ⚠️ Średnie |
| **Signing .exe** | ⚠️ Opcjonalne | ⚠️ Opcjonalne |

---

## 5. Rekomendacje

### 5.1 Krótkoterminowe (Python)

**Użyj GitHub Actions z PyInstaller:**

1. Utwórz `.github/workflows/build-windows.yml`
2. Build na windows-latest runner
3. Upload artifact do GitHub Releases
4. Czas build: ~15 minut
5. Rozmiar: ~150-200MB

**Przykład minimalnego workflow:**
```yaml
name: Build Windows

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e . pyinstaller
      - run: pyinstaller --onefile --windowed tlumacz/qt_gui/app.py
      - uses: actions/upload-artifact@v4
        with:
          name: Tlumacz-Windows
          path: dist/Tlumacz.exe
```

### 5.2 Długoterminowe (C++)

**Tylko jeśli zdecydujesz się na migrację C++:**

1. Użyj GitHub Actions z MSVC + Qt
2. Build na windows-latest runner
3. Cross-compile z Linux **odradzane**
4. Czas build: ~30 minut
5. Rozmiar: ~50-80MB

### 5.3 Opcje alternatywne

#### Opcja 1: NSIS Installer (Python)

Stwórz installer zamiast single .exe:

```bash
# Pobierz NSIS
winget install NSIS.NSIS

# Skrypt install.nsi
Name "Tlumacz"
OutFile "Tlumacz-Installer.exe"
InstallDir "$PROGRAMFILES\Tlumacz"

Section "Install"
  SetOutPath $INSTDIR
  File /r "dist\*.*"
  CreateShortcut "$DESKTOP\Tlumacz.lnk" "$INSTDIR\Tlumacz.exe"
SectionEnd
```

**Zaleta:** Mniejszy rozmiar, profesjonalny installer

#### Opcja 2: Portable App (Python)

Stwórz portable wersję bez instalacji:

```bash
# Struktura
Tlumacz-Portable/
├── Tlumacz.exe
├── python311.dll
├── PySide6/
├── skills/
└── config/
```

**Zaleta:** Można uruchamiać z USB

---

## 6. Podsumowanie

### 6.1 Wersja Python

✅ **Wykonalne** — PyInstaller + GitHub Actions  
⚠️ **Średni stopień trudności** — wymaga konfiguracji  
✅ **Darmowe** — w ramach 2000 minut/miesiąc  
❌ **Brak cross-compile** — musisz budować na Windows (GitHub Actions)

### 6.2 Wersja C++ (tylko llama.cpp + Cloud API)

⚠️ **Wykonalne** — MSVC + GitHub Actions  
⚠️ **Średni-Wysoki stopień trudności** — bez FastAPI jest łatwiej  
✅ **Darmowe** — w ramach 2000 minut/miesiąc  
❌ **Cross-compile odradzane** — problemy z Qt/MinGW

**Uproszczenia dzięki wykluczeniu FastAPI/OpenVINO:**
- Brak integracji z Transformers/Torch (oszczędność ~2 miesięcy)
- Brak zależności od Pythona w runtime
- Prostsza architektura (tylko QProcess dla llama.cpp + libcurl dla Cloud)
- Mniejszy rozmiar dystrybucji (~50MB vs ~80MB)

### 6.3 Rekomendacja końcowa

**Dla obecnej wersji Python:**
- Użyj **GitHub Actions + PyInstaller**
- Build na `windows-latest` runner
- Czas: ~15 minut, koszt: 0 (w ramach darmowego tieru)

**Dla hipotetycznej wersji C++:**
- Użyj **GitHub Actions + MSVC + Qt**
- Build na `windows-latest` runner
- Czas: ~30 minut, koszt: 0 (w ramach darmowego tieru)
- Cross-compile z Linux: **odradzane**

---

## 7. Załączniki

### 7.1 Przydatne linki

- PyInstaller: https://pyinstaller.org/
- GitHub Actions: https://docs.github.com/en/actions
- Qt for Windows: https://doc.qt.io/qt-6/windows.html
- Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/

### 7.2 Narzędzia

| Narzędzie | Przeznaczenie | Link |
|-----------|---------------|------|
| PyInstaller | Pakowanie Python → .exe | https://pyinstaller.org/ |
| cx_Freeze | Alternatywa dla PyInstaller | https://cx-freeze.readthedocs.io/ |
| NSIS | Tworzenie installerów | https://nsis.sourceforge.io/ |
| windeployqt | Deploy Qt DLLs | https://doc.qt.io/qt-6/windows-deployment.html |

### 7.3 Szablony GitHub Actions

- Python build: https://github.com/actions/starter-workflows
- Qt build: https://github.com/jurplel/install-qt-action

---

**Koniec raportu**

**Data sporządzenia:** 2026-09-10  
**Wersja:** 1.0  
**Status:** Finalny
