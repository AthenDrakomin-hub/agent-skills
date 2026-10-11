# Target Routing Matrix

How to classify a reverse-engineering target and select the correct analysis engine.

## Top-Level Classification

| Signal | Type | Pipeline |
|---|---|---|
| Directory with `package.json`, `src/`, `app/`, `pages/`, `pom.xml`, `requirements.txt`, `go.mod`, `Cargo.toml` | Source code | Path A |
| File extension `.apk`, `.aab`, `.exe`, `.dll`, `.so`, `.dylib`, `.app`, `.bin`, `.elf`, `.class`, `.jar`, `.war`, `.wasm`, `.pyc` | Binary | Path B |
| `http://` or `https://` URL, or "clone/reconstruct this website" | Website | Path C |

## Binary Subtype Routing (Path B)

| Subtype | Extensions | Primary tools | Key artifacts |
|---|---|---|---|
| Android APK | `.apk`, `.aab` | JADX, Apktool, aapt, uber-apk-signer | `AndroidManifest.xml`, smali, resources, native libs |
| Electron app | `.exe` (with `resources/app.asar`), `.app`, `.AppImage` | asar extract, Node module analysis, strings | `app.asar` contents, `package.json`, main/preload/renderer JS |
| .NET assembly | `.exe`, `.dll` (PE with CLR header) | ILSpy, dnSpy, `monodis` | CIL decompiled classes, attributes, embedded resources |
| Windows PE | `.exe`, `.dll` (native) | Ghidra, IDA Free, x64dbg, `strings`, Dependency Walker | Imports/exports, control flow, strings |
| Linux ELF | `.elf`, `.so`, no extension binary | Ghidra, IDA, `readelf`, `objdump`, `strings` | Symbols (if not stripped), PLT/GOT, sections |
| macOS Mach-O | `.dylib`, `.app/Contents/MacOS/*` | Ghidra, Hopper, `otool`, `class-dump` | ObjC classes, dyld info, code signatures |
| Java bytecode | `.jar`, `.class`, `.war` | JADX, CFR, Procyon, `javap` | Decompiled `.java`, constant pool |
| WebAssembly | `.wasm` | wasm2wat, wasm-decompile, Ghidra (wasm plugin) | WAT text, exported functions, memory layout |
| Firmware | `.bin`, `.img`, `.hex` | Binwalk, `strings`, `dd`, firmware-mod-kit | Extracted filesystems, kernel, bootloader |
| Python bytecode | `.pyc`, `.pyo` | `decompyle3`, `uncompyle6`, `pycdc` | Decompiled `.py` source |

## Detection Commands

```bash
# File type detection (cross-platform)
file <target>                    # Linux/macOS
Get-Item <target> | Select-Object Extension, Length  # PowerShell

# PE/ELF/Mach-O header check
xxd <target> | head -1           # MZ (PE), 7f454c46 (ELF), cffaedfe (Mach-O)

# APK check
unzip -l <target>.apk | head -20 # Should show AndroidManifest.xml, classes.dex

# Electron check
7z l <target>.exe | findstr asar  # or: ls resources/app.asar

# .NET check
monodis <target>.dll 2>/dev/null || echo "not .NET"
```

## Framework Detection (Path A & C)

| Signal | Framework |
|---|---|
| `package.json` with `"react"` | React |
| `package.json` with `"vue"` | Vue |
| `package.json` with `"@angular/core"` | Angular |
| `package.json` with `"svelte"` | Svelte |
| `next.config.js` / `next.config.ts` | Next.js |
| `nuxt.config.js` / `nuxt.config.ts` | Nuxt |
| `remix.config.js` | Remix |
| `pom.xml` | Java/Maven |
| `build.gradle` | Java/Gradle |
| `requirements.txt` / `pyproject.toml` | Python |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `composer.json` | PHP |
| `Gemfile` | Ruby |

## Mixed Targets

When a target spans multiple types:
- **Electron app** = Path B (binary shell) + Path C (embedded web content). Run B first to extract `app.asar`, then C on the extracted JS.
- **React Native APK** = Path B (APK) + Path A (JS bundle in `assets/index.android.bundle`). Decompile APK, then analyze the JS bundle as source.
- **Website with downloadable desktop client** = run Path C on the site and Path B on the client separately, then cross-reference API contracts.
