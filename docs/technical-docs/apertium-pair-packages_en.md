## Current package repository model — TAR-only

The user's `$HOME/.config/tlumacz/apertium/` repository stores only `.tar` packages and their external `.tar.sha256` files. The application does not create a persistent unpacked copy. During runtime initialization, the archives are verified and their contents are materialized in a temporary working directory outside the repository; the path of that directory is passed to Apertium as `APERTIUM_DATADIR/-d`.

# Apertium Language-Pair Packages

**Status:** authoritative format and pipeline contract  
**Audit date:** 2026-10-06  
**Distribution format:** uncompressed `.tar`  
**Runtime repository:** `$HOME/.config/tlumacz/apertium/`

## 1. Distribution model
## 1.1. User repository and application usage

The target repository for distribution artifacts is:

    $HOME/.config/tlumacz/apertium/
    ├── apertium-eng-pol-1.0.0.tar
    ├── apertium-eng-pol-1.0.0.tar.sha256
    ├── apertium-eng-pol/
    └── ...

The `.tar` archives are the actual distribution format. The application does not execute TAR directly: before discovery it verifies the SHA-256 of the complete archive and then extracts missing packages into the same repository. The unpacked directories are an internal working representation used by ApertiumRuntime; they do not replace the `.tar` artifacts.

The old `$HOME/.config/tlumacz/apertium/` directory is not used; the correct repository is `$HOME/.config/tlumacz/apertium/`.

**One package = one translation direction.**

If the source Apertium project supports two directions, for example `eng-spa` and `spa-eng`, two independent artifacts are produced:

```text
apertium-eng-spa-1.0.0.tar
apertium-spa-eng-1.0.0.tar
```

We do not create a shared package containing multiple directions.

Tar is a transport container, not a compression mechanism. Packages are created as ordinary, uncompressed tar archives.

## 2. Package contents

The package contains only data required by the selected mode:

```text
apertium-eng-spa-1.0.0.tar
└── apertium-eng-spa/
    ├── manifest.json
    ├── checksums.json
    ├── COPYING
    ├── modes.xml
    ├── modes/
    │   └── eng-spa.mode
    ├── eng-spa.automorf.bin
    ├── eng-spa.prob
    ├── eng-spa.autobil.bin
    ├── eng-spa.t1x.bin
    ├── ...
    └── transfer source files required by the mode
```

The builder **filters `modes.xml` to one selected mode**. Definitions of the remaining directions are not copied.

The package does not contain:

- `.git/`;
- `dev/`;
- `test/`;
- `eval/`;
- compilation cache;
- `Makefile`, `configure`, `autom4te.cache`;
- source dictionaries and other files not referenced by the selected mode;
- data for another direction.

Source files `.t1x`, `.t2x`, `.t3x` are retained **only when the selected mode directly references them**. This is not accidental retention of sources: Apertium runtime uses these files together with the corresponding binaries.

## 3. Manifest and checksum

`manifest.json` identifies exactly one direction:

```json
{
  "format": "apertium-pair",
  "format_version": 1,
  "id": "apertium-eng-spa",
  "name": "apertium-eng-spa",
  "version": "1.0.0",
  "pair": "eng-spa",
  "source": "eng",
  "target": "spa"
}
```

`checksums.json` contains SHA-256 values for all package files except `checksums.json` itself.

The installer also checks:

- one root directory;
- directory consistency with the manifest;
- absence of absolute paths and `..`;
- absence of symlinks and hardlinks;
- checksum completeness;
- presence of `modes.xml` and the correct `.mode`.

## 4. Code

Format and installer:

```text
src/tlumacz/backends/apertium/packages.py
```

Pipeline:

```text
tools/apertium/package_pipeline.py
```

CLI:

```text
tools/apertium/package_pairs.py
```

Tests:

```text
tests/test_apertium_packages.py
tests/test_apertium_package_pipeline.py
```

## 5. Automatic package preparation

### From a local checkout

```bash
python3 tools/apertium/package_pairs.py   --source /path/to/apertium-eng-spa   --output $HOME/.config/tlumacz/apertium   --version 1.0.0
```

If the source contains two complete directions, two files are produced.

### Download from the Internet and compile

```bash
python3 tools/apertium/package_pairs.py   eng-spa   --download   --compile   --output $HOME/.config/tlumacz/apertium   --version 1.0.0
```

Pipeline:

```text
GitHub
  ↓
git clone apertium-<pair>
  ↓
existing apertium-get.py
  ↓
dependency download
  ↓
autoreconf/configure/make
  ↓
detection of complete modes
  ↓
selection of each direction separately
  ↓
manifest + SHA-256
  ↓
uncompressed .tar
  ↓
SHA256SUMS
```

The original `Apertium/apertium-get.py` was not changed. An orchestration layer was added above it so that the upstream download/compilation mechanism is not mixed with our distribution format.

### Cleanup after packaging

```bash
python3 tools/apertium/package_pairs.py   --source /path/to/apertium-eng-spa   --output $HOME/.config/tlumacz/apertium   --version 1.0.0   --clean-runtime
```

The option removes from the source materials that are not required by the runtime of the retained, complete directions.

**Note:** `--clean-runtime` is destructive for the specified directory. A backup must be made before using it on a source repository. In practice, for Tłumacz distribution we use it on the runtime repository `$HOME/.config/tlumacz/apertium/`, while source repositories under `Apertium/` are retained for subsequent compilations.

## 6.1. Portability of `modes/<pair>.mode`

The package must not persist absolute paths from the build environment. The builder normalizes path arguments in the generated `.mode` to file names located inside the package directory. This allows a package built on one host to be installed on another.

The regression is in `tests/test_apertium_packages.py` and checks that the absolute source directory does not enter the artifact.

## 6. Detecting ready directions

`discover_packagable_pairs()` considers a direction ready when:

1. the mode has the standard name `source-target`;
2. the mode has `install="yes"`;
3. all `<file>` entries from the mode exist;
4. the corresponding `modes/<pair>.mode` exists.

Helper modes such as `eng-spa-chunker` are not treated as separate pairs.

For exceptions where upstream does not set `install="yes"`, `include_unmarked=True` is available. We use it only after manual verification. It is not currently used for a published pair.

## 7. Bidirectional pairs

If both modes are complete, the builder creates two artifacts. It does not matter whether they originate from one repository.

Example:

```text
apertium-eng-cat/
    eng-cat  -> apertium-eng-cat-1.0.0.tar
    cat-eng  -> apertium-cat-eng-1.0.0.tar
```

The same applies to all other bidirectional pairs.

## 8. Current audit 2026-10-06

The local `Apertium/` checkouts contain the following complete, already compiled directions:

| Family | Directions |
|---|---|
| Bengali ↔ English | `bn-en`, `en-bn` |
| English ↔ Catalan | `eng-cat`, `cat-eng` |
| English ↔ German | `eng-deu`, `deu-eng` |
| English ↔ Italian | `eng-ita`, `ita-eng` |
| English ↔ Spanish | `eng-spa`, `spa-eng` |
| English ↔ Portuguese | `en-pt`, `pt-en` |
| Polish ↔ Kashubian | `pl-csb`, `csb-pl` |
| Polish ↔ Slovak | `pl-sk`, `sk-pl` |
| Polish ↔ Czech | `pol-ces`, `ces-pol` |
| Polish ↔ Russian | `pol-rus`, `rus-pol` |
| Polish ↔ Silesian | `pol-szl`, `szl-pol` |
| Polish ↔ Ukrainian | `pol-ukr`, `ukr-pol` |
| Polish ↔ Spanish | `pol-spa`, `spa-pol` |
| English → Polish | `eng-pol` |

A total of **28 publishable directions** have been prepared.

## 9. Ready artifacts

The directory:

```text
pary/
```

contains 28 uncompressed archives:

```text
apertium-bn-en-1.0.0.tar
apertium-en-bn-1.0.0.tar
apertium-cat-eng-1.0.0.tar
apertium-eng-cat-1.0.0.tar
apertium-ces-pol-1.0.0.tar
apertium-pol-ces-1.0.0.tar
apertium-csb-pl-1.0.0.tar
apertium-pl-csb-1.0.0.tar
apertium-deu-eng-1.0.0.tar
apertium-eng-deu-1.0.0.tar
apertium-eng-ita-1.0.0.tar
apertium-ita-eng-1.0.0.tar
apertium-eng-pol-1.0.0.tar
apertium-eng-spa-1.0.0.tar
apertium-spa-eng-1.0.0.tar
apertium-en-pt-1.0.0.tar
apertium-pt-en-1.0.0.tar
apertium-pl-sk-1.0.0.tar
apertium-sk-pl-1.0.0.tar
apertium-pol-rus-1.0.0.tar
apertium-rus-pol-1.0.0.tar
apertium-pol-spa-1.0.0.tar
apertium-spa-pol-1.0.0.tar
apertium-pol-szl-1.0.0.tar
apertium-szl-pol-1.0.0.tar
apertium-pol-ukr-1.0.0.tar
apertium-ukr-pol-1.0.0.tar
```

Each has a corresponding `.sha256` file; `SHA256SUMS` contains the checksums for the entire set.

## 10. Directions not ready

### `pol-eng`

The pair was fixed and published as `apertium-pol-eng-1.0.0.tar`.

The first blocker was a reference to `a_SN` in `apertium-eng-pol.pol-eng.t3x` without a declaration of that attribute. `a_SN` with the value `PDET` was added. A full compilation then revealed a missing generated `pol-eng.autogen.bin`; direct `lt-comp rl` correctly generated this artifact despite validator warnings about duplicate `pardef` entries in the Polish dictionary.

Final verification: `pol-eng.t1x.bin`, `pol-eng.t2x.bin`, `pol-eng.t3x.bin`, `pol-eng.autogen.bin`, and the other files required by the mode are present. The package was installed into a clean repository, detected as `pol-eng`, and the actual Apertium runtime performed a test `pl → en` translation.

### `pol-src`

This is a local language/source module with morphological modes, not a complete translation direction. We do not create a pair package from it.

## 11. Runtime repository cleanup

After package preparation, the repository:

```text
$HOME/.config/tlumacz/apertium/
```

was cleaned of development materials.

The following were removed, among others:

- `.git/`;
- `dev/`;
- `test/`;
- `eval/`;
- autotools cache;
- `Makefile*`;
- `configure*`;
- unused dictionary sources;
- unused helper modes.

Only artifacts required by the available modes, licenses, and `modes.xml` were retained.

Backup before the operation:

```text
backups/apertium-package-pipeline-20261006-205830/Apertium-data.tar
SHA-256:
1d9e77ffe9eaa363d13f6e25ff02958818a1e54bbffb95baa39a6f8d6d898aec
```

## 12. Verification of all packages

All 27 archives were:

1. unpacked by the real `ApertiumPairPackageInstaller`;
2. verified for manifest and checksums;
3. installed into a clean temporary repository;
4. detected again by `discover_supported_pairs()`.

Result:

```text
ARCHIVES 27
PAIRS 27
INSTALLATION OF ALL PACKAGES: OK
```

In addition, every package is an uncompressed tar.

## 13. Licenses

The builder requires `COPYING`, `LICENSE`, or `LICENSE.txt`.

We do not guess licenses. If upstream does not provide unambiguous information, the package is blocked from publication.

For example, official Apertium repositories confirm licenses for some prepared families; e.g. `apertium-bn-en` is marked GPL-2.0, and `apertium-eng-pol` is also GPL-2.0. This information was used only to verify the sources, while the package itself must still contain the appropriate license file. citeturn3search0turn1search3

## 14. Adding a new pair

```bash
python3 tools/apertium/package_pairs.py   <pair>   --download   --compile   --output $HOME/.config/tlumacz/apertium   --version 1.0.0
```

After successful compilation, the tool automatically finds all complete directions from that repository. If the pair is bidirectional, two separate files are produced.

For publication, check:

```bash
tar -tf pary/apertium-<pair>-1.0.0.tar
sha256sum pary/apertium-<pair>-1.0.0.tar
```

## 15. Design principle

**Apertium source is used for compilation. The Tłumacz package is used for runtime distribution.**

We do not mix these roles:

```text
Apertium/
  complete source repositories
  ↓
  compilation
  ↓
  package_pipeline
  ↓
pary/
  individual .tar artifacts
  ↓
Internet
  ↓
Tłumacz
  ↓
$HOME/.config/tlumacz/apertium/
```

This makes it possible to regularly fetch newer Apertium repositories, compile them, automatically detect both directions, and publish only complete, verified packages.

## 16. Build tools outside the runtime

Package preparation logic is located exclusively in `tools/apertium/`. `package_pipeline.py` and `package_pairs.py` are helper tools used during the build process and are not part of the Tłumacz runtime.

The manual procedure for preparing a single package is described in `docs/technical-docs/apertium-paczki-reczne-tworzenie.md`, while the full contract is in `docs/technical-docs/paczki-jezykowe-specyfikacja.md`.
