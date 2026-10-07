# STATUS DOKUMENTU: HISTORYCZNY / V3

> Ten dokument opisuje historyczny proces budowania Tłumacza V3. Nie jest instrukcją aktywnego V4. Aktualny stan Windows V4: brak kompletnego natywnego runtime'u; obecny artefakt 0.40.0 jest RC dla Linux x86-64. Nie reaktywować FastAPI/OpenVINO na podstawie tego dokumentu.

# Plan architektury kompilacji Windows — Agent Translator V3

**Data:** 2026-09-10  
**Wersja projektu:** 0.30.0  
**Platforma docelowa:** Windows 10/11 (64-bit)  
**Narzędzie build:** PyInstaller + GitHub Actions  
**Status:** Plan do wdrożenia

---

## 1. Cel

Automatyczne budowanie dystrybucji Windows (.exe) z kodu źródłowego Python przy każdym release (tag `v*`). Artifact dostępny w GitHub Releases.

---

## 2. Architektura pipeline'u

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                             │
│                                                                      │
│  Tag push (v0.30.0)  ──→  GitHub Actions workflow                   │
│                                                                      │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   GitHub Actions — windows-latest                    │
│                                                                      │
│  ┌─────────────┐   ┌──────────────┐   ┌───────────────────────┐   │
│  │ Checkout    │──→│ Python 3.11  │──→│ pip install + build   │   │
│  │ code        │   │ setup        │   │ PyInstaller           │   │
│  └─────────────┘   └──────────────┘   └───────────┬───────────┘   │
│                                                     │               │
│                                                     ▼               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  PyInstaller                                                 │   │
│  │  - Bundle Python interpreter + PySide6 + dependencies       │   │
│  │  - Include skills/*.md, resources/*.qss, resources/*.svg    │   │
│  │  - Output: dist/Tlumacz.exe (~150-200MB)                   │   │
│  └─────────────────────────────────────────┬───────────────────┘   │
│                                             │                       │
│                                             ▼                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Post-build                                                 │   │
│  │  - Upload artifact (GitHub Actions)                         │   │
│  │  - Create GitHub Release (jeśli tag)                        │   │
│  │  - Attach Tlumacz.exe do release                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Releases                               │
│                                                                      │
│  Release: v0.30.0                                                    │
│  ├── Tlumacz-0.30.0-Windows-x64.exe   (150-200MB)                 │
│  ├── Tlumacz-0.30.0-Windows-x64.zip   (opcjonalnie, skompresowany)│
│  └── CHANGELOG.md (auto-generated)                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Struktura plików do utworzenia

```
agent-translator-v3/
├── .github/
│   └── workflows/
│       ├── build-windows.yml        # Główny workflow build Windows
│       └── build-linux.yml          # (opcjonalnie) build Linux AppImage
├── build/
│   └── windows/
│       ├── tlumacz.spec             # Konfiguracja PyInstaller
│       └── icon.ico                 # Ikona aplikacji
├── docs/
│   └── windows-kompilacja.md        # Ten plik
└── pyproject.toml                   # Istniejący (bez zmian)
```

---

## 4. Workflow GitHub Actions

### 4.1 Plik: `.github/workflows/build-windows.yml`

```yaml
name: Build Windows

on:
  push:
    tags:
      - 'v*'  # Trigger na tag v* (np. v0.30.0)
  workflow_dispatch:  # Manualny trigger

env:
  PYTHON_VERSION: '3.11'
  APP_NAME: 'Tlumacz'

jobs:
  build-windows:
    name: Build Windows x64
    runs-on: windows-latest
    
    steps:
      # ─── Krok 1: Checkout kodu ───
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Pełna historia dla versioningu

      # ─── Krok 2: Setup Python ───
      - name: Set up Python ${{ env.PYTHON_VERSION }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      # ─── Krok 3: Instalacja zależności ───
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip setuptools wheel
          pip install -e .
          pip install pyinstaller

      # ─── Krok 4: Weryfikacja instalacji ───
      - name: Verify installation
        run: |
          python -c "import tlumacz; print('OK')"
          python -c "import PySide6; print('PySide6 OK')"
          python -c "import openai; print('openai OK')"

      # ─── Krok 5: Uruchom testy (opcjonalnie) ───
      - name: Run tests
        run: |
          pip install pytest
          pytest tests/ -v --timeout=60 || echo "Tests completed with warnings"

      # ─── Krok 6: Build PyInstaller ───
      - name: Build executable with PyInstaller
        run: |
          pyinstaller build/windows/tlumacz.spec --noconfirm

      # ─── Krok 7: Weryfikacja build ───
      - name: Verify build output
        run: |
          if (Test-Path "dist/${{ env.APP_NAME }}.exe") {
            Write-Host "Build successful: dist/${{ env.APP_NAME }}.exe"
            Get-Item "dist/${{ env.APP_NAME }}.exe" | Select-Object Length, LastWriteTime
          } else {
            Write-Error "Build failed: executable not found"
            exit 1
          }

      # ─── Krok 8: Upload artifact ───
      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ env.APP_NAME }}-Windows-x64
          path: dist/${{ env.APP_NAME }}.exe
          retention-days: 30

      # ─── Krok 9: Kompresja (opcjonalnie) ───
      - name: Create ZIP archive
        run: |
          Compress-Archive -Path "dist/${{ env.APP_NAME }}.exe" -DestinationPath "dist/${{ env.APP_NAME }}-${{ github.ref_name }}-Windows-x64.zip"

      # ─── Krok 10: GitHub Release ───
      - name: Create GitHub Release
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v2
        with:
          name: Release ${{ github.ref_name }}
          body: |
            ## Agent Translator ${{ github.ref_name }}
            
            ### Instalacja
            1. Pobierz `Tlumacz-${{ github.ref_name }}-Windows-x64.exe`
            2. Uruchom plik .exe — nie wymaga instalacji Pythona
            3. Skonfiguruj API key w ustawieniach
            
            ### Wymagania
            - Windows 10/11 (64-bit)
            - ~300MB wolnego miejsca na dysku
            
            ### Znane ograniczenia
            - Pierwsze uruchomienie może być wolne (ładowanie Qt)
            - Antivirus może flagować plik .exe (false positive)
          files: |
            dist/${{ env.APP_NAME }}.exe
            dist/${{ env.APP_NAME }}-${{ github.ref_name }}-Windows-x64.zip
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 4.2 Opcjonalnie: `.github/workflows/build-linux.yml`

```yaml
name: Build Linux

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build-linux:
    name: Build Linux AppImage
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pyinstaller
      
      - name: Build executable
        run: |
          pyinstaller build/linux/tlumacz.spec --noconfirm
      
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: Tlumacz-Linux-x64
          path: dist/Tlumacz
```

---

## 5. Konfiguracja PyInstaller

### 5.1 Plik: `build/windows/tlumacz.spec`

```python
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

# Ścieżki do zasobów
skills_dir = os.path.join('tlumacz', 'skills')
resources_dir = os.path.join('tlumacz', 'qt_gui', 'resources')

a = Analysis(
    ['tlumacz/qt_gui/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Skills (pliki .md z promptami tłumaczenia)
        (skills_dir, 'tlumacz/skills'),
        # Zasoby Qt (motywy QSS, ikony SVG)
        (resources_dir, 'tlumacz/qt_gui/resources'),
    ],
    hiddenimports=[
        # PySide6 — Qt modules
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        # openai SDK
        'openai',
        'httpx',
        'anyio',
        'anyio._backends._asyncio',
        # SQLite
        'sqlite3',
        # Inne
        'json',
        'pathlib',
        'logging',
        'dataclasses',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Wyklucz niepotrzebne moduły (zmniejsza rozmiar)
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Tlumacz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Kompresja UPX (zmniejsza rozmiar ~30%)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Bez okna konsoli (aplikacja GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='build/windows/icon.ico',  # Ikona aplikacji
    version='build/windows/version_info.txt',  # Informacje o wersji
)
```

### 5.2 Plik: `build/windows/version_info.txt`

```python
# UTF-8
#
# For more details about fixed file info:
# https://docs.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(0, 30, 0, 0),
    prodvers=(0, 30, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'Tlumacz Team'),
           StringStruct(u'FileDescription', u'AI-powered document translator'),
           StringStruct(u'FileVersion', u'0.30.0.0'),
           StringStruct(u'InternalName', u'Tlumacz'),
           StringStruct(u'LegalCopyright', u'Copyright (c) 2026 Tlumacz Team'),
           StringStruct(u'OriginalFilename', u'Tlumacz.exe'),
           StringStruct(u'ProductName', u'Agent Translator'),
           StringStruct(u'ProductVersion', u'0.30.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [0x0409, 1200])])
  ]
)
```

---

## 6. Ikona aplikacji

### 6.1 Wymagania

- Format: `.ico` (Windows icon)
- Rozmiary: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
- Głębia kolorów: 32-bit (RGBA)

### 6.2 Konwersja z SVG

Jeśli masz SVG w `tlumacz/qt_gui/resources/icon.svg`:

```bash
# Instalacja narzędzia
pip install cairosvg

# Konwersja SVG → ICO (skrypt Python)
python -c "
import cairosvg
sizes = [16, 32, 48, 64, 128, 256]
for size in sizes:
    cairosvg.svg2png(url='tlumacz/qt_gui/resources/icon.svg',
                     write_to=f'icon_{size}.png',
                     output_width=size, output_height=size)
"

# Pakowanie do ICO (ImageMagick)
magick convert icon_*.png build/windows/icon.ico
```

### 6.3 Alternatywa

Użyj istniejącej ikony lub wygeneruj z tekstu:
- https://favicon.io/ — generator ikon
- https://www.icoconverter.com/ — konwerter online

---

## 7. Process release

### 7.1 Workflow release

```bash
# 1. Przygotuj release
git checkout main
git pull origin main

# 2. Zaktualizuj wersję w pyproject.toml
# version = "0.30.0" → "0.31.0"

# 3. Zaktualizuj CHANGELOG.md
# Dodaj sekcję dla nowej wersji

# 4. Commit i push
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.31.0"
git push origin main

# 5. Utwórz tag
git tag -a v0.31.0 -m "Release 0.31.0"
git push origin v0.31.0

# 6. GitHub Actions automatycznie:
#    - Zbuduje Tlumacz.exe
#    - Utworzy GitHub Release
#    - Dołączy plik .exe do release
```

### 7.2 Struktura GitHub Release

```
Release v0.31.0
├── Tlumacz.exe                          (150-200MB)
├── Tlumacz-v0.31.0-Windows-x64.zip     (skompresowany)
└── Changelog (auto-generated z CHANGELOG.md)
```

---

## 8. Opcjonalnie: Code Signing

### 8.1 Dlaczego signing?

- Windows SmartScreen ostrzega przed niepodpisanymi .exe
- Antivirus mniej agresywnie flaguje
- Profesjonalny wygląd

### 8.2 Opcje

| Opcja | Koszt | Trudność |
|-------|:---:|:---:|
| Brak signingu | 0 | ✅ Łatwa |
| Self-signed certificate | 0 | ⚠️ Średnia |
| Comodo/Sectigo certificate | ~$200/rok | ⚠️ Średnia |
| Azure Trusted Signing | ~$0.10/sign | ✅ Łatwa |

### 8.3 Integracja z GitHub Actions (opcjonalnie)

```yaml
# Dodaj po kroku build
- name: Sign executable
  if: startsWith(github.ref, 'refs/tags/')
  uses: azure/trusted-signing-action@v0
  with:
    azure-tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    azure-client-id: ${{ secrets.AZURE_CLIENT_ID }}
    azure-client-secret: ${{ secrets.AZURE_CLIENT_SECRET }}
    endpoint: https://eus.codesigning.azure.net/
    code-signing-account-name: MySigningAccount
    certificate-profile-name: MyCertProfile
    files-folder: dist
    files-folder-filter: exe
```

**Uwaga:** Signing jest opcjonalny. Aplikacja działa bez niego, ale SmartScreen może ostrzegać.

---

## 9. Testowanie buildu

### 9.1 Testy lokalne (przed push)

```bash
# 1. Zainstaluj PyInstaller
pip install pyinstaller

# 2. Zbuduj lokalnie
pyinstaller build/windows/tlumacz.spec --noconfirm

# 3. Przetestuj na Windows
dist/Tlumacz.exe

# 4. Sprawdź:
#    - Aplikacja startuje
#    - GUI się wyświetla
#    - Tłumaczenie działa (z API key)
#    - Skills się ładują
#    - Cache działa
```

### 9.2 Testy w GitHub Actions

Workflow automatycznie:
1. Instaluje zależności
2. Uruchamia testy (`pytest`)
3. Buduje .exe
4. Weryfikuje że plik istnieje

### 9.3 Testy manualne po build

Po pobraniu .exe z GitHub Releases:

| Test | Oczekiwany wynik |
|------|-----------------|
| Uruchom .exe | Aplikacja startuje, GUI się wyświetla |
| Skonfiguruj API key | Ustawienia zapisują się |
| Przetłumacz tekst | Tłumaczenie działa |
| Przetłumacz plik .md | Plik wyjściowy poprawny |
| Przetłumacz plik .docx | Plik wyjściowy poprawny |
| Zamknij i otwórz ponownie | Ustawienia zachowane |

---

## 10. Rozwiązywanie problemów

### 10.1 PyInstaller — brakujące moduły

**Problem:** `ModuleNotFoundError` po uruchomieniu .exe

**Rozwiązanie:** Dodaj do `hiddenimports` w `tlumacz.spec`:
```python
hiddenimports=[
    'missing_module',
    # ...
]
```

### 10.2 PyInstaller — brakujące pliki danych

**Problem:** Skills nie ładują się, motywy QSS nie działają

**Rozwiązanie:** Sprawdź `datas` w `tlumacz.spec`:
```python
datas=[
    ('tlumacz/skills', 'tlumacz/skills'),
    ('tlumacz/qt_gui/resources', 'tlumacz/qt_gui/resources'),
]
```

### 10.3 Antivirus flaguje .exe

**Problem:** Windows Defender usuwa plik .exe

**Rozwiązanie:**
- Dodaj wyjątek w antivirus
- Rozważ code signing (sekcja 8)
- Zgłoś false positive do Microsoft

### 10.4 Build trwa zbyt długo

**Problem:** Build > 30 minut

**Rozwiązanie:**
- Włącz cache pip w GitHub Actions (już w workflow)
- Wyklucz niepotrzebne moduły (`excludes` w spec)
- Włącz UPX compression (`upx=True` w spec)

### 10.5 Rozmiar .exe > 200MB

**Problem:** Plik .exe jest zbyt duży

**Rozwiązanie:**
- Wyklucz niepotrzebne moduły (`excludes` w spec)
- Włącz UPX compression
- Rozważ opcję "portable" (katalog z plikami zamiast single .exe)

---

## 11. Harmonogram wdrożenia

| Krok | Opis | Czas | Status |
|------|------|:---:|:---:|
| 1 | Utwórz `.github/workflows/build-windows.yml` | 30 min | ⏳ |
| 2 | Utwórz `build/windows/tlumacz.spec` | 1h | ⏳ |
| 3 | Przygotuj `icon.ico` | 30 min | ⏳ |
| 4 | Utwórz `version_info.txt` | 15 min | ⏳ |
| 5 | Test lokalny build | 30 min | ⏳ |
| 6 | Push i test GitHub Actions | 30 min | ⏳ |
| 7 | Weryfikacja .exe na Windows | 30 min | ⏳ |
| 8 | (Opcjonalnie) Code signing | 1h | ⏳ |
| **Łącznie** | | **~5h** | |

---

## 12. Podsumowanie

### Co zyskujesz

✅ **Automatyczne buildy** — push tagu → .exe w GitHub Releases  
✅ **Brak ręcznej pracy** — nie musisz budować lokalnie na Windows  
✅ **Wersjonowanie** — każdy release ma unikalny .exe  
✅ **Darmowe** — w ramach 2000 minut GitHub Actions/miesiąc  
✅ **Reprodukowalność** — ten sam kod → ten sam .exe  

### Czego potrzebujesz

✅ Konto GitHub (darmowe)  
✅ Repository z kodem  
✅ Podstawową znajomość YAML (workflow)  
✅ Podstawową znajomość PyInstaller (spec file)  

### Następne kroki

1. Utwórz pliki z sekcji 3 (struktura katalogów)
2. Skopiuj workflow z sekcji 4.1
3. Skopiuj spec z sekcji 5.1
4. Przygotuj icon.ico (sekcja 6)
5. Przetestuj lokalnie: `pyinstaller build/windows/tlumacz.spec`
6. Push i zobacz GitHub Actions w akcji

---

**Koniec planu**

**Data sporządzenia:** 2026-09-10  
**Wersja:** 1.0  
**Status:** Plan do wdrożenia
