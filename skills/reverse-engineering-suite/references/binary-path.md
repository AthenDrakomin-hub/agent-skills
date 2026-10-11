# Binary Reverse-Engineering Path (Path B)

Detailed workflow for analyzing compiled binaries and producing analysis reports + reimplementation plans.

## Prerequisites

Run `scripts/check-env.ps1` (Windows) or equivalent to verify:
- Node.js >= 22.19
- REA CLI (`rea --version` or `npx rea-agents@latest`)
- Available engines: Ghidra / IDA / JADX / Binwalk / Apktool

If REA is not installed:
```powershell
npx rea-agents@latest setup
```
Setup is interactive — the user must approve configuration changes.

## Step 1 — Target Identification

Use `references/target-routing.md` to classify the binary subtype. Record:
- File type (PE/ELF/Mach-O/APK/.NET/JAR/WASM/firmware)
- Architecture (x86/x64/ARM/ARM64)
- Stripped or not (symbols present?)
- Packed/obfuscated? (UPX, VMProtect, Themida, ProGuard)

If packed, note it in the report. Do not attempt automatic unpacking of commercial protectors — flag as `[packed, manual unpacking required]`.

## Step 2 — Surface Analysis

Before deep disassembly, gather surface intelligence:

```bash
# Strings (all platforms)
strings <target> > strings.txt

# Imports/exports
# Windows: dumpbin /imports <target>  (or Ghidra)
# Linux:   readelf -d <target> | grep NEEDED
# macOS:   otool -L <target>

# File metadata
# Windows: powershell: (Get-Item <target>).VersionInfo
# Linux:   file <target>
```

Catalog:
- All human-readable strings (URLs, error messages, config keys, API endpoints)
- Imported libraries and functions
- Exported functions (if a library/DLL)
- Embedded resources (images, configs, certificates)

## Step 3 — Deep Analysis by Subtype

### APK
```bash
jadx -d output/ <target>.apk    # Decompile to Java
apktool d <target>.apk -o apk/   # Extract resources + smali
aapt dump badging <target>.apk   # Package info, permissions
```
Analyze: `AndroidManifest.xml` (permissions, activities, services, receivers), decompiled Java, native libs in `lib/`.

### Electron
```bash
npx asar extract resources/app.asar extracted/
```
Analyze: `package.json` (main entry, dependencies), main process code, preload scripts, renderer JS bundles, native modules.

### .NET
Use ILSpy or dnSpy to decompile. Analyze: namespaces, classes, methods, attributes, embedded resources, P/Invoke calls.

### Native PE/ELF/Mach-O
Use Ghidra or IDA:
1. Auto-analyze the binary
2. Identify `main` / entry point
3. Trace cross-references to strings (strings → functions → call graph)
4. Analyze import table usage (which libraries, which functions)
5. Decompile key functions to pseudo-C

### WebAssembly
```bash
wasm2wat <target>.wasm -o output.wat
wasm-decompile <target>.wasm -o output.decomp
```
Analyze: exported functions, memory layout, imported functions (JS bridge), linear memory segments.

### Firmware
```bash
binwalk -e <target>.bin    # Extract filesystem
strings <target>.bin | head -100
```
Analyze: extracted filesystem, kernel config, bootloader, embedded scripts, hardcoded credentials (flag but do not exploit).

## Step 4 — Module Breakdown

For each identified module, fill `references/module-breakdown-template.md`:
- Module name and purpose
- Inputs/outputs
- Dependencies (internal + external libraries)
- Key algorithms (describe, don't copy verbatim)
- Data structures
- Confidence level (high/medium/low based on evidence quality)

## Step 5 — Analysis Report

Use `references/report-template.md`. Every finding must cite evidence:
- `strings.txt:42` — a string reference
- `Ghidra: FUN_00401000` — a decompiled function
- `AndroidManifest.xml:15` — a manifest entry
- `JADX: com.app.Auth.login()` — a decompiled method

## Step 6 — Reimplementation Plan

Use `references/replication-guide.md`:
- Map each module to a target tech stack
- Estimate complexity (S/M/L/XL)
- Identify which modules can be clean-room reimplemented
- Flag modules that depend on proprietary algorithms or trade secrets
- Provide module-by-module implementation order

## Safety Reminders (embedded in every Path B output)
- State the legal-use assumption in the report header
- Never include deobfuscation, license bypass, or DRM removal steps
- Reimplementation is independent rewrite, not copy-paste of decompiled code
- Do not reproduce copyrighted assets, branding, or UI verbatim
- Mark all findings with confidence levels
