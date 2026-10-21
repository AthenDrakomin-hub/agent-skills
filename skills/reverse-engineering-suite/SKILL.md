---
name: reverse-engineering-suite
description: "Unified reverse-engineering suite (v2.0 dual-mode) covering three target types: source code (reverse into PRD), binaries (Heavy REA MCP OR zero-dependency Lean native tools), and websites (traffic + frontend + behavior reconstruction). Auto-detects target type, routes to correct pipeline, auto-falls back to Lean mode when REA MCP unavailable. Every conclusion labeled confirmed/inferred/unknown. Use when: reverse-engineer, decompile, analyze codebase, extract product specs, understand binary/APK/Electron app, reconstruct website, clone functionality, 逆向, 反编译, 代码转PRD, 分析程序, 复刻功能, 二进制分析."
license: MIT
metadata:
  author: AthenDrakomin-hub
  version: "2.0.0"
  category: reverse-engineering
  sources: "merged from code-to-prd + rea-reverse-engineering v3.0 + leanrea methodology"
---

# Reverse Engineering Suite v2.0

## Role

Senior reverse-engineering analyst handling the full spectrum: source code, compiled binaries, and live websites. Auto-detect target type, select the correct pipeline, deliver evidence-based outputs — never guesses. Every conclusion cites a file, line, tool output, or network capture as proof, labeled `confirmed` / `inferred` / `unknown`.

## Dual-Mode Binary Analysis (Path B)

| Mode | Trigger | Dependencies | Best for |
|---|---|---|---|
| **Heavy** | REA MCP available | Node 22.19+, REA MCP, Ghidra/JADX/Binwalk | Deep decompilation, runtime tracing, large binaries |
| **Lean** | REA unavailable / user says "quick scan" | Zero install — native shell tools | Fast understanding, Electron/APK/Web, string & import analysis |

**Rule:** Detect REA first (`rea --version` or MCP tool list). Available → Heavy default. Unavailable → **auto-fallback to Lean, never refuse the task.**

## Auto-Detection (No User Confirmation Needed)

| Input signal | Target type | Pipeline | Primary output |
|---|---|---|---|
| Directory with `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `src/`, `app/`, `pages/` | **Source code** | Path A | PRD + functional inventory |
| File `.apk`, `.exe`, `.dll`, `.so`, `.dylib`, `.app`, `.bin`, `.elf`, `.class`, `.jar`, `.wasm`, `.asar` | **Binary** | Path B | Analysis report + reimplementation scaffold |
| `http://` / `https://` URL, or "clone / reconstruct / understand this website" | **Website** | Path C | Behavior spec + frontend/backend reconstruction |
| Ambiguous | Ask for path/URL once, then auto-detect | — | — |

If target spans two types (e.g. Electron = binary + website), run Path B first for the shell, then Path C for embedded web content, merge outputs.

## Universal 5-Step Workflow

### Step 1 — Inventory & Scope
List what was provided, what's missing, what analysis covers. State limitations upfront.

### Step 2 — Acquisition (Lean principle: batch probe in one call)
Gather raw evidence with **merged shell calls** to minimize round-trips:
- **Source:** `scripts/codebase_analyzer.py <dir> -o analysis.json`
- **Binary (Lean):** `file target; ls -lh target; strings target | wc -l; objdump -p target 2>/dev/null | grep NEEDED` — one call gets type + size + string count + imports
- **Binary (Heavy):** `scripts/check-env.ps1` then REA CLI per `references/target-routing.md`
- **Website:** capture HAR, download frontend assets, map API endpoints

### Step 3 — Structured Analysis
Decompose into modules. For each: purpose, inputs, outputs, dependencies, data models, key algorithms. Use `references/module-breakdown-template.md`.

### Step 4 — Output Generation
- **Path A:** full PRD via `scripts/prd_scaffolder.py analysis.json -o prd/`
- **Path B:** analysis report + reimplementation plan
- **Path C:** behavior spec + API inventory + frontend component tree

### Step 5 — Verification
Every claimed feature traces to evidence. No fabricated endpoints/functions. Output detailed enough for reconstruction. Safety boundaries respected.

---

## Path A — Source Code → PRD

### What you do
1. Run `codebase_analyzer.py` → routes, components, models, API calls, state, enums.
2. Detect framework from config files (`references/framework-patterns.md`).
3. Distinguish real API integrations from mock/fixture data — flag mocks explicitly.
4. Generate per-page docs: purpose, fields, interactions, navigation, API calls, state dependencies.
5. Extract all enums, status codes, type mappings into a dictionary.
6. Run `prd_scaffolder.py` to build PRD directory structure.
7. Fill business-readable descriptions.

### Output structure
```
prd/
├── README.md          # Executive summary, tech stack, feature matrix
├── pages/             # One doc per page/route
├── api/               # One doc per endpoint (request/response/errors)
├── models/            # Data model schemas
├── enums.md           # All status codes, type mappings, constants
└── state.md           # State management map
```

### Quality bar
Page doc: every field with type, validation rules, source (API/computed/hardcoded), interaction behavior. Endpoint doc: method, path, auth, request schema, response schema, error codes. Unknown → mark `[undetermined]`, never invent.

---

## Path B — Binary → Analysis + Reimplementation (Dual-Mode)

### Safety invariants (non-negotiable)
1. **Legal use only:** user must own or be authorized. State this assumption.
2. **No cracking:** no deobfuscation, license bypass, DRM removal, serial-key generation.
3. **No fabrication:** every finding cites tool output. If tool didn't run, say so.
4. **Functional equivalence only:** independent rewrite, not byte-level copy. No copyrighted assets/branding/UI.
5. **Local execution:** binaries analyzed on user's machine. Remind user tool outputs may go to AI provider.

### Step B1 — Mode detection
```powershell
rea --version  # Heavy available?
# If not found → Lean mode auto-engaged
```

### Step B2 — Target subtype routing (Lean: by magic bytes, not just extension)

| Subtype | Magic bytes / signal | Lean commands | Heavy engine |
|---|---|---|---|
| Electron/asar | `.asar`, `package.json` with `main` | `npx asar extract` → `rg -uu` | REA JS analyzer |
| Mach-O | `CF FA ED FE` / `FE ED FA CF` | `otool -l`, `strings`, `otool -ov` | Hopper/Ghidra |
| ELF | `7F 45 4C 46` | `readelf`, `objdump -p`, `strings` | Ghidra/IDA |
| PE | `4D 5A` (MZ) | `strings`, `dumpbin /imports` | Ghidra/IDA |
| Go binary | `runtime.`, `go.buildinfo` in strings | `go version -m`, `strings \| grep runtime` | Ghidra |
| Rust binary | `rust_`, `cargo auditable` | `strings`, `cargo auditable` | Ghidra |
| .NET | CLR header, `_CorExeMain` | `ilspycmd`, `monodis` | ILSpy/dnSpy |
| Android APK | `.apk` (ZIP `50 4B`) | `jadx --no-res`, `apktool d` | JADX + REA |
| Flutter | `libflutter.so`, snapshot hash | `strings` search snapshot | Ghidra |
| WASM | `00 61 73 6D` | `wasm-objdump`, `strings` | — |
| SQLite | `53 51 4C 69` | `sqlite3 .dump` | — |
| Firmware | `.bin`/`.img`/`.fw` | `binwalk -e`, `file` | Binwalk + Ghidra |

**Unsure?** Check first 4 bytes:
```bash
python3 -c "print(open('target','rb').read(4).hex())"
```

### Step B3 — Lean mode core techniques

**1. Slice reading, never load whole file into context**
```bash
head -c 200 target.js          # header only
rg -n "login|encrypt|token" target.js | head -50  # search, don't read
```

**2. Batch probe in one shell call**
```bash
file target; ls -lh target; strings target | wc -l; objdump -p target | grep NEEDED
```

**3. `rg -uu` for extracted dirs** (packers hide code in dot-directories like `.webpack/`)
```bash
npx asar extract app.asar ./extracted
rg -uu "ipcMain|preload|contextBridge" ./extracted/
```

**4. Start from strings & imports, locate functions via literal pools**
```bash
# Mach-O: string in __cstring → find function referencing it
otool -v -s __TEXT __cstring target | head -100
```

**5. Read call sequences, not every instruction**
```bash
objdump -d target | grep "^[0-9a-f]* <" > functions.txt  # inventory first
objdump -d target --start-address=0x1000 --stop-address=0x2000  # then target function
```

**6. Electron focus:** IPC channels (`ipcMain.handle`), preload scripts, `contextBridge`, fuses config.

**7. APK focus:** Manifest permissions/components first, then `rg -uu` for API/secret/key in sources.

### Step B4 — Heavy mode (when available)
Full REA CLI commands in `references/target-routing.md`. Use `--json` for structured output. Large binaries (>50MB): string+import scan first, then targeted decompile.

### Step B5 — Report with evidence levels

Every finding must carry one of:

| Level | Meaning | Example |
|---|---|---|
| `confirmed` | Tool output directly proves | "strings output line 1234: API_URL=https://api.example.com" |
| `inferred` | Reasonable inference from evidence | "Imports libcrypto.so → likely uses OpenSSL (algorithm unconfirmed)" |
| `unknown` | Cannot determine | "Function logic too complex for pseudocode, needs manual review" |

### Output structure
```
reverse-report/
├── report.md              # Full analysis with evidence citations + levels
├── modules/               # One doc per identified module
├── strings/               # Extracted string catalog (if relevant)
├── reimplementation-plan.md
└── scaffolds/             # Generated code scaffolds (per module, on request)
```

---

## Path C — Website → Behavior Reconstruction

### What you do
1. **Frontend mapping:** download page, extract component tree from bundled JS, identify framework, list routes. Use `rg -n "api|fetch|token"` on downloaded JS instead of reading whole files.
2. **API discovery:** capture network (HAR/DevTools). For each endpoint: method, path, payload, response shape, auth, pagination.
3. **Behavior spec:** document user flows step by step — clicks, inputs, navigation, loading/error/empty states.
4. **Data model inference:** derive entities and relationships from API responses + frontend state.
5. **Reconstruction output:** behavior spec + API inventory + frontend component map. Code → clean-room scaffold (your own implementation, not asset copy).

### Output structure
```
website-report/
├── behavior-spec.md       # User flows, states, interactions
├── api-inventory.md       # All endpoints with request/response schemas
├── frontend-map.md        # Component tree, routes, state management
├── data-model.md          # Inferred entities and relationships
└── scaffolds/             # Clean-room code scaffolds (on request)
```

### Ethics
No proprietary branding/copy/visual assets verbatim. Reconstruct behavior and API contracts, redesign UI independently. Only analyze what user's own account can access.

---

## Cross-Path Rules

1. **Evidence first:** every claim cites `file:line`, tool output, or captured request. Uncited → `[unverified]`.
2. **Evidence levels:** binary findings labeled `confirmed`/`inferred`/`unknown`.
3. **No silent assumptions:** obfuscated/minified/no-debug-symbols → say so, reduce confidence.
4. **Batch calls:** merge detection commands into one shell invocation to minimize round-trips.
5. **Slice reading:** never Read whole large files; use `rg`/`head`/address-range disassembly.
6. **Output language:** match user's language. Code/identifiers stay English.
7. **Line discipline:** this file is the orchestrator. Deep per-path instructions in `references/`, loaded on demand.
8. **Tool preference:** bundled scripts first (`codebase_analyzer.py`, `prd_scaffolder.py`, `check-env.ps1`), then native tools, then custom one-offs.

## Quick Start

```bash
# Source → PRD
python3 scripts/codebase_analyzer.py ./my-app -o analysis.json
python3 scripts/prd_scaffolder.py analysis.json -o prd/ -n "My App"

# Binary → Lean mode (no install needed)
file target; strings target | head -50; objdump -p target | grep NEEDED
# Electron: npx asar extract app.asar ./out && rg -uu "ipcMain" ./out/
# APK: jadx --no-res --output-dir ./out app.apk && rg -uu "api" ./out/sources/

# Binary → Heavy mode (REA available)
powershell -ExecutionPolicy Bypass -File scripts/check-env.ps1

# Website → provide URL; agent handles capture and mapping
```

## References
- `references/target-routing.md` — Binary subtype detection and engine selection matrix (Heavy mode)
- `references/lean-command-cheatsheet.md` — Complete native command reference per target type (Lean mode)
- `references/framework-patterns.md` — Frontend/backend framework detection rules
- `references/module-breakdown-template.md` — Standard module analysis template
- `references/report-template.md` — Binary analysis report structure
- `references/replication-guide.md` — Reimplementation planning methodology
- `references/verification-checklist.md` — Pre-delivery quality gate for all three paths
