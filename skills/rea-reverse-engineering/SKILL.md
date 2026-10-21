---
name: rea-reverse-engineering
description: "Dual-mode reverse engineering: heavy REA MCP Server (115K stars) OR zero-dependency lean mode using native shell commands. Analyze binaries, APKs, Electron apps, .NET assemblies, websites, and firmware to produce evidence-based analysis and functional-equivalent reimplementation. Lean mode needs no MCP/install — routes by file type to strings/otool/objdump/jadx/asar/rg. Use when: reverse engineer app, analyze binary, understand closed-source software, audit legacy code, reconstruct behavior, 逆向工程, 二进制分析, APK反编译, 无源码分析, Electron逆向. Not for cracking, unpacking, or bypassing licensing/DRM."
license: MIT
compatibility: "Heavy mode: Node.js >= 22.19 + REA MCP (npx rea-agents@latest setup). Lean mode: zero install, uses native shell tools (file/strings/otool/objdump/rg/asar/jadx when present). Windows/macOS/Linux."
metadata:
  author: morluto + leanrea (curated by AthenDrakomin-hub)
  version: "3.0.0"
  category: development
  source: "https://github.com/morluto/rea + https://github.com/aicodeking/leanrea"
  stars: "115K+"
---

# rea-reverse-engineering v3.0（双模式）

## 任务

将用户指定的逆向目标完成端到端分析与复刻：环境检测 → 目标类型识别 → 选择分析引擎 → 执行反编译/跟踪 → 整理带证据的分析报告 → 模块拆解 → 技术栈映射 → 逐模块代码复刻 → 对照验证。

最终交付物是**一套可运行的复刻源代码**，而非仅分析报告。

## 双模式

| 模式 | 触发条件 | 依赖 | 适合场景 |
|---|---|---|---|
| **Heavy（REA MCP）** | REA 已安装且 MCP 可用 | Node 22.19+、REA MCP、Ghidra/IDA/Hopper/JADX | 深度反编译、运行时跟踪、大二进制 |
| **Lean（原生工具）** | REA 未安装 / 用户不想装 / 快速扫描 | 零安装，用系统原生命令 | 快速理解、Electron/APK/Web、字符串和导入分析 |

**模式选择规则**：先检测 REA 是否可用（`rea --version` 或 MCP 工具列表）。可用则默认 Heavy；不可用或用户说"快速看一下"则自动降级 Lean，**不要因为缺 MCP 就拒绝任务**。

## 不变量（安全与边界）

1. **合法用途**：仅用于合法逆向研究、自有代码审计、功能理解与行为重建。
2. **不做破解**：禁止输出脱壳、绕过授权/付费/DRM、移除许可证校验等步骤或代码。
3. **不编造结果**：每个结论必须附带工具输出的证据，标注 `confirmed` / `inferred` / `unknown`。
4. **不承诺源码恢复**：反编译输出是伪代码/汇编，不等于原始源码。
5. **本地执行**：二进制在用户本机分析，不上传云端。
6. **需要人工审查**：关键结论提示用户复核反编译输出。
7. **复刻的法律边界**：复刻是基于逆向理解的**独立重实现**，不得直接复制原始代码/资源。
8. **复刻不等于原样复制**：目标是**功能等价**，UI 风格和品牌素材不得直接复制。

## 输入要求

| 输入项 | 说明 | 缺失时处理 |
|---|---|---|
| 目标路径或 URL | 本地文件绝对路径、目录，或网站 URL | 必须询问 |
| 分析目标 | 想搞懂什么功能（如"分析登录加密"） | 必须询问，无目标则整体扫描 |
| 分析深度 | quick / deep | 默认 quick，大文件强制 quick |
| 模式偏好 | heavy / lean / auto | 默认 auto |

## 核心工作流

### STEP 1 → 环境检测与模式选择

**Heavy 模式检测**：
```powershell
rea --version
# 或检查 MCP 工具列表中是否有 rea_* 工具
```

**Lean 模式工具探测**（一次调用合并检测，减少轮次）：
```bash
which file strings rg objdump otool jadx asar npx python3 2>/dev/null || echo "missing-some"
```
Windows PowerShell：
```powershell
Get-Command file,strings,rg,objdump,jadx,npx,python -ErrorAction SilentlyContinue | Select-Object Name,Source
```

工具：PowerShell / Bash

### STEP 2 → 目标类型识别（Lean 模式核心：按 magic bytes 路由）

**不要盲目分析**，先用文件头和扩展名判断类型，路由到对应命令。

| 目标类型 | 识别特征 | Lean 模式首选命令 |
|---|---|---|
| Electron/asar | `.asar`、Electron 目录结构、`package.json` | `npx asar extract` → `rg -uu` |
| Web 打包文件 | 压缩 `.js`、source map | `head -c 200` 切片 → `rg` |
| Mach-O（macOS） | magic `CF FA ED FE` / `FE ED FA CF` | `otool -l`、`strings`、`otool -ov` |
| ELF（Linux） | magic `7F 45 4C 46` | `objdump -p`、`strings`、`readelf` |
| PE（Windows） | magic `4D 5A`（MZ） | `strings`、`dumpbin /imports` |
| Go 二进制 | 含 `runtime.`、`go.buildinfo` | `go version -m`、`strings \| grep runtime` |
| Rust 二进制 | 含 `rust_`、`cargo auditable` | `strings`、`cargo auditable` |
| .NET 程序集 | 含 CLR 头、`_CorExeMain` | `ilspycmd`、`monodis` |
| Android APK | `.apk`（zip 格式） | `jadx` 或 `apktool d` |
| Flutter | `libflutter.so`、snapshot hash | `strings` 搜 snapshot |
| WASM | magic `00 61 73 6D` | `wasm-objdump`、`strings` |
| SQLite | magic `53 51 4C 69` | `sqlite3 .dump` |
| 固件 | `.bin`/`.img`/`.fw` | `binwalk`、`file` |
| 网站 | `http(s)://` | `curl` + 浏览器 DevTools |
| HAR/PCAP | `.har`/`.pcap` | `jq`、`tshark` |

**识别不确定时**，用 `file` 命令或检查前 4 字节魔数：
```bash
xxd -l 4 target.bin   # Linux/macOS
# 或 Python: python3 -c "print(open('target','rb').read(4).hex())"
```

工具：PowerShell / Bash / Python

### STEP 3 → 执行分析

#### Heavy 模式（REA MCP）

完整命令清单见 `references/rea-cli-reference.md`。通用原则：
- 首次分析加 `--json`
- 大二进制（>50MB）先做字符串和导入表扫描
- 原生二进制选 provider：`--provider ghidra`（免费）

```powershell
# JavaScript/Electron
npx -y rea-agents@latest analyze-javascript-application "D:\path\to\app" --json
# 原生二进制
rea analyze-native "C:\path\to\binary.exe" --provider ghidra --json
```

#### Lean 模式（零依赖，核心技巧）

**技巧 1：压缩文件切片读取，不整文件读入上下文**
```bash
# 只看文件头 200 字节判断类型
head -c 200 target.js
# 大文件用 rg 搜索关键词，不 Read 整个文件
rg -n "login|password|encrypt|token" target.js | head -50
```

**技巧 2：批量探测合并为一次 shell 调用**
```bash
# 一次调用拿到：类型、大小、字符串数、导入表
file target; ls -lh target; strings target | wc -l; objdump -p target | grep NEEDED
```

**技巧 3：用 rg -uu 搜索解压后的目录**（打包器会把代码藏在 `.webpack/` 等点开头目录，普通搜索会跳过）
```bash
npx asar extract app.asar ./extracted
rg -uu "ipcMain|contextBridge|preload" ./extracted/
```

**技巧 4：从字符串和导入入手定位函数**
```bash
# Mach-O：用 otool 看字面量池，通过字符串注释定位引用它的函数
otool -v -s __TEXT __cstring target | head -100
otool -ov target | grep -A5 "感兴趣的字符串"
```

**技巧 5：读调用序列而非每条指令**
```bash
# 先 diff 函数清单，再 diff 感兴趣的函数
objdump -d target | grep "^[0-9a-f]* <" > functions.txt
# 找到目标函数后只反汇编那一段
objdump -d target --start-address=0x1000 --stop-address=0x2000
```

**技巧 6：Electron 重点关注**
- IPC 通道：`ipcMain.handle(`、`ipcRenderer.invoke(`
- preload 脚本：`webPreferences.preload`
- contextBridge：`contextBridge.exposeInMainWorld`
- fuses 安全配置：`asar`、`onlyLoadAppFromAsar`

**技巧 7：APK 重点关注**
```bash
jadx --no-res --output-dir ./jadx-out target.apk
# 先看 Manifest
cat ./jadx-out/resources/AndroidManifest.xml | head -80
# 再搜关键词
rg -uu "login|api|http|secret|key" ./jadx-out/sources/ | head -30
```

工具：PowerShell / Bash（直接调用原生命令，不需要 MCP）

### STEP 4 → 结果整理与报告

报告模板见 `references/report-template.md`。每个发现必须标注证据等级：

| 等级 | 含义 | 示例 |
|---|---|---|
| `confirmed` | 工具输出直接证明 | "strings 输出包含 API_URL=https://api.example.com" |
| `inferred` | 基于证据的合理推断 | "导入了 libcrypto.so，推断使用 OpenSSL（未确认具体算法）" |
| `unknown` | 无法确定 | "该函数逻辑复杂，反编译伪代码不完整，需人工复核" |

报告必须包含：
1. 目标信息（路径、大小、类型、识别到的编译器/打包器）
2. 分析方法（模式、使用的命令、分析深度）
3. 关键发现（每个附带原始证据片段 + 证据等级）
4. 功能重建（标注"重建版本，非原始源码"）
5. 局限性（未分析部分、不确定结论、需人工复核点）
6. 数据安全提醒

### STEP 5 → 复刻执行

基于分析报告，将逆向理解转化为可运行源代码。详细指南见 `references/replication-guide.md`。

**5.1 模块拆解**：拆为 P0（核心路径）/ P1（重要）/ P2（边缘），每个模块标注逆向证据编号。

**5.2 技术栈映射**：原生伪代码 → 用户后端语言；JS/Electron → 按用户前端框架重构。保留边界条件和异常处理，标注每个函数对应的证据地址，**不直接复制原始代码**。

**5.3 逐模块实现**：按 P0→P1→P2 顺序，每个函数头部注释 `// 复刻自: <地址/模块>，证据: 发现 #N`。

**5.4 资源处理**：配置/常量提取后转目标语言格式；UI/图片/音频不得直接复制，使用替代资源。

### STEP 6 → 对照验证

验证清单见 `references/verification-checklist.md`。

- 为每个 P0/P1 模块写单元测试，用例来自逆向观察到的输入输出
- 核心功能执行输入输出对照表（原始 vs 复刻，一致率 ≥ 95%）
- 边界与异常测试：空输入、null、极值、非法格式、网络异常
- 不一致时回到 STEP 3 深入分析相关函数，修正后重测

## 目标类型深度指引

### 原生二进制

1. 先跑字符串扫描和导入表，建立全局认知（Lean：`strings` + `objdump -p` / `otool -l`）
2. 用字符串/导入函数定位相关代码区域
3. 对目标函数反编译（Heavy：Ghidra/IDA；Lean：`objdump -d` 指定地址范围）
4. 跟踪调用链，理解数据流向
5. Heavy 模式可用 Frida/LLDB 做运行时跟踪

### JavaScript/Electron

1. ASAR 解压：`npx asar extract app.asar ./extracted`
2. Heavy：REA 直接分析目录返回模块/导入/路由/IPC 关系
3. Lean：`rg -uu "ipcMain|preload|contextBridge" ./extracted/`
4. 重点关注 preload 脚本和 IPC 通道

### Android APK

1. Heavy：REA + JADX 返回 Manifest、类结构、反编译方法
2. Lean：`jadx --no-res --output-dir ./out app.apk`，先看 Manifest 再 `rg -uu` 搜关键词
3. 重点关注权限声明和组件注册

### .NET 程序集

1. Heavy：REA 静态分析
2. Lean：`ilspycmd -p -o ./out assembly.dll`（需安装 ilspycmd）或 `monodis`
3. 重点关注引用的程序集和入口点

### 固件

1. 仅 Linux 支持（Binwalk/Unblob）
2. `binwalk -e firmware.bin` 提取文件系统，再对提取出的二进制做原生分析
3. Windows 用户需 WSL2 或 Linux 服务器

### 网站

1. Heavy：Chrome 浏览器运行时跟踪
2. Lean：`curl -sL https://example.com | rg -n "api|fetch|token"`，配合浏览器 DevTools 看 Network 面板
3. 重点关注 API 端点、请求签名、本地存储

## 完成条件

- 分析命令实际执行并返回输出，报告中每个结论附带证据 + 证据等级
- 模块拆解清单完成，P0 模块全部实现为可运行代码
- 核心路径行为对照一致率 ≥ 95%
- 每个函数标注了逆向证据来源
- 明确标注未复刻的 P1/P2 功能及原因
- 明确标注分析局限性和法律合规提醒

## 停止条件

- 用户未提供目标路径且无法推断
- Heavy 模式 Node 版本不满足且用户不升级 → 自动降级 Lean
- 目标类型需要的引擎未安装且用户不装 → Lean 模式能用就用，不能用则说明
- 涉及破解/脱壳/绕过授权 → 拒绝
- 复刻涉及直接复制受版权保护内容 → 拒绝并说明独立重实现要求
- 行为对照连续 3 轮修正后核心路径仍不一致 → 报告差异，建议人工复核
- 用户明确要求停止

## references 读取条件

- `references/target-matrix.md`：STEP 2 需要完整目标类型→引擎→命令映射时读取
- `references/rea-cli-reference.md`：Heavy 模式 STEP 3 前读取，确认当前 CLI 命令
- `references/lean-command-cheatsheet.md`：Lean 模式 STEP 3 前读取，获取各平台完整命令清单
- `references/report-template.md`：STEP 4 写报告时读取
- `references/replication-guide.md`：STEP 5 复刻时读取
- `references/module-breakdown-template.md`：STEP 5.1 模块拆解时读取
- `references/verification-checklist.md`：STEP 6 验证时读取

## scripts 运行条件

- `scripts/check-env.ps1`：STEP 1 运行，输出 Heavy 模式环境检测结果

## 常见问题排查

| 问题 | 原因 | 解决 |
|---|---|---|
| `rea: command not found` | 未装 REA | 用 `npx -y rea-agents@latest` 或降级 Lean 模式 |
| Ghidra 启动超时 | 大二进制/首次启动 | 设 `REA_GHIDRA_STARTUP_TIMEOUT_MS=300000`，或用 Lean 模式先扫字符串 |
| MCP 工具不出现 | 代理未重启 | setup 后重启 AI 代理，或降级 Lean |
| APK 分析失败 | 缺 JDK/JADX | 装 JDK 17+，REA setup 自动拉 JADX；Lean 模式 jadx 需自行装 |
| 固件分析不可用 | Windows 不支持 Binwalk | WSL2 或 Linux 服务器 |
| Lean 模式结果不够深 | 原生命令只能做表层分析 | 关键函数需 Heavy 模式反编译，或安装 Ghidra/JADX |
| 结果不准确 | REA 版本旧 | `rea update` 升级；Lean 模式升级系统工具 |

## 版本信息

- REA npm 包：`rea-agents`（v6.3.0，2026-10-10）
- leanrea：8KB 纯 SKILL.md，零依赖（v1.0，2026-10）
- GitHub：github.com/morluto/rea + github.com/aicodeking/leanrea
- License：MIT
- Heavy 模式 Node 要求：>= 22.19（22.x）、>= 24.11（24.x）或 26+
- Lean 模式：无 Node 要求，用系统原生工具
