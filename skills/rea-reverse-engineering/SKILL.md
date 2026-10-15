---
name: rea-reverse-engineering
description: "AI-assisted reverse engineering via REA (Reverse Engineer Anything) MCP Server + CLI (115K+ GitHub stars). Analyze binaries, APKs, Electron apps, .NET assemblies, websites, and network captures to produce evidence-based analysis and functional-equivalent reimplementation. REA orchestrates Hopper/Ghidra/JADX/Binwalk and exposes them to Claude Code, Codex, Cursor, and 17+ AI agents. Use when: reverse engineer app, analyze binary, understand closed-source software, audit legacy code, reconstruct behavior, 逆向工程, 二进制分析, APK反编译, 无源码分析. Not for cracking, unpacking, or bypassing licensing/DRM."
license: MIT
compatibility: "Requires Node.js >= 22.19, REA MCP server (npx rea-agents@latest setup). Optional: Hopper (macOS), Ghidra (cross-platform), JADX (Android), Binwalk (firmware)."
metadata:
  author: morluto (curated by AthenDrakomin-hub)
  version: "2.0.0"
  category: development
  source: "https://github.com/morluto/rea"
  stars: "115K+"
---

# rea-reverse-engineering

## 任务

将用户指定的逆向目标通过 REA 工具链完成端到端分析与复刻：环境检测 → 目标类型识别 → 选择分析引擎 → 执行反编译/跟踪 → 整理带证据的分析报告 → 模块拆解 → 技术栈映射 → 逐模块代码复刻 → 对照验证。

最终交付物是**一套可运行的复刻源代码**，而非仅分析报告。分析报告是中间产物，复刻代码才是终点。

REA 本身不是反汇编器，它是 MCP Server + CLI，把专业逆向工具的能力暴露给 AI 代理。本 Skill 封装 REA 的调用编排、目标路由、复刻工作流和验证规范，使 Agent 可以稳定地完成"逆向→理解→复刻"全流程。

## 不变量（安全与边界）

1. **合法用途**：仅用于合法的逆向工程研究、自有代码审计、功能理解与行为重建。用户须对目标拥有分析授权或符合适用法律的例外情形。
2. **不做破解**：禁止输出脱壳、绕过授权/付费/DRM、移除许可证校验、破解序列号等步骤或代码。
3. **不编造结果**：每个结论必须附带 REA 工具输出的证据。未执行分析不得声称"已分析"。
4. **不承诺源码恢复**：REA 返回的是伪代码/汇编/模块关系，不等于原始源码。报告中必须明确标注这一点。
5. **本地执行**：二进制文件在用户本机分析，不上传云端。但 AI 代理会收到工具输出，数据是否离开本机取决于所用模型提供商的数据政策——需在报告中提醒。
6. **需要人工审查**：完全自动化做不到。关键结论应提示用户人工复核反编译输出和重定位信息。
7. **复刻的法律边界**：复刻代码必须是基于逆向理解的**独立重实现**，不得直接复制原始代码、资源文件或受版权保护的素材。用户须确认复刻行为符合适用法律（包括但不限于版权法、专利法、商业秘密保护和反向工程例外条款）。涉及第三方商业软件的完整复刻时，须提醒用户咨询法律意见。
8. **复刻不等于原样复制**：复刻目标是**功能等价**，不是字节级或代码级一致。UI 风格、品牌标识、专有素材不得直接复制，应重新设计或使用替代资源。

## 输入要求

执行分析前必须确认：

| 输入项 | 说明 | 缺失时处理 |
|--------|------|-----------|
| 目标路径或 URL | 本地文件绝对路径、目录路径，或网站 URL | 必须询问，不得猜测 |
| 分析目标 | 用户想搞懂什么功能/行为（如"分析登录加密逻辑"） | 必须询问，无目标则做整体扫描 |
| 分析深度 | quick（快速扫描）/ deep（深度反编译+跟踪） | 默认 quick，大文件强制 quick |

可选输入：关注的函数名/字符串、已知的入口点、输出格式偏好。

## 核心工作流

### STEP 1 → 环境检测

运行 `scripts/check-env.ps1`，检查：
- Node.js 版本（需 >= 22.19）
- REA 是否已安装（`rea --version` 或 npm 全局包）
- 可用的逆向引擎（Ghidra / IDA / Hopper / JADX / Binwalk）

**未安装 REA 时**：输出安装命令并等待用户确认后执行：
```powershell
npx rea-agents@latest setup
```
setup 是交互式的，需要用户在终端中选择代理并批准配置变更。

**Node 版本不满足时**：提示用户升级 Node.js，不得继续。

工具：PowerShell

### STEP 2 → 目标类型识别

根据文件扩展名和文件头判断目标类型，路由到对应分析路径。详细映射见 `references/target-matrix.md`。

| 目标类型 | 识别特征 | 所需引擎 |
|---------|---------|---------|
| 原生二进制 | .exe/.dll/.so/.dylib/.elf，PE/Mach-O/ELF 头 | Ghidra 或 IDA 或 Hopper |
| JavaScript/Electron | .asar、包含 package.json 的目录、Electron 结构 | 无需额外引擎 |
| .NET 程序集 | .exe/.dll 含 CLR 头 | 无需额外引擎（静态） |
| Android APK | .apk | JADX + JDK |
| 固件 | .bin/.img/.fw | Binwalk/Unblob（仅 Linux） |
| 网站 | http(s):// URL | Chrome 浏览器 |
| 网络抓包 | .har | 无需额外引擎 |

识别不确定时，用 `file` 命令（Linux/macOS）或检查文件头魔数确认。

工具：PowerShell / 系统命令

### STEP 3 → 执行分析

根据目标类型选择 REA CLI 命令。完整命令清单见 `references/rea-cli-reference.md`。

**通用原则**：
- 首次分析加 `--json` 输出结构化结果，便于解析
- 大二进制（>50MB）先做字符串和导入表扫描，不做全量反编译
- 原生二进制需先选择 provider：`--provider ghidra`（免费）或 `--provider ida` / `--provider hopper`
- 分析超时：Ghidra 大文件可设 `$env:REA_GHIDRA_STARTUP_TIMEOUT_MS = "300000"`

**JavaScript/Electron 示例**：
```powershell
npx -y rea-agents@latest analyze-javascript-application "D:\path\to\app" --json
```

**原生二进制示例**（需先配置 provider）：
```powershell
rea analyze-native "C:\path\to\binary.exe" --provider ghidra --json
```

> 注意：REA 版本迭代快，命令可能变化。执行前先跑 `rea --help` 确认当前版本支持的子命令。

工具：PowerShell（调用 rea / npx rea-agents）

### STEP 4 → 结果整理与报告

将 REA 输出整理为结构化报告，使用 `references/report-template.md` 模板。

报告必须包含：
1. **目标信息**：文件路径、大小、类型、识别到的编译器/打包器
2. **分析方法**：使用的 REA 命令、provider、分析深度
3. **关键发现**：每个发现附带 REA 输出的原始证据（伪代码片段、字符串、调用关系）
4. **功能重建**：如用户要求，基于证据重建逻辑（标注为"重建版本，非原始源码"）
5. **局限性**：哪些部分未分析、哪些结论不确定、需要人工复核的点
6. **数据安全提醒**：工具输出已发送给 AI 模型提供商

工具：文本整理（无外部工具）

### STEP 5 → 复刻执行

基于 STEP 4 的分析报告，将逆向理解转化为可运行的源代码。详细指南见 `references/replication-guide.md`，模块拆解模板见 `references/module-breakdown-template.md`。

**5.1 模块拆解**

将目标软件的功能拆分为独立可复刻的模块清单，每个模块标注：

| 字段 | 说明 |
|------|------|
| 模块名 | 功能描述性命名 |
| 职责 | 一句话说明做什么 |
| 输入/输出 | 接口契约 |
| 依赖 | 依赖的其他模块 |
| 逆向证据 | 对应分析报告中的发现编号 |
| 优先级 | P0（核心路径）/ P1（重要功能）/ P2（边缘功能） |

拆解原则：
- P0 模块必须先复刻，构成最小可运行版本
- 每个模块的代码量控制在可单测验证的范围
- 模块间通过明确接口通信，避免隐式依赖

**5.2 技术栈映射**

将逆向出来的实现映射到用户指定的技术栈：

- 原生二进制（C/C++/汇编伪代码）→ 用户后端语言（PHP/Go/Node/Python/Java）
- JavaScript/Electron → 可直接参考逻辑，按用户前端框架重构
- .NET CIL → 映射到对应语言的等价实现
- Android (Java/Kotlin/Smali) → 映射到用户技术栈
- 数据结构和算法逻辑保持不变，仅做语法转换

映射时必须：
- 保留原始逻辑的边界条件和异常处理
- 标注每个函数对应的逆向证据地址
- 不直接复制原始代码，必须重写为目标语言的地道写法

**5.3 逐模块实现**

按 P0 → P1 → P2 顺序实现：

1. 先定义模块的接口/类型/数据结构
2. 实现核心逻辑（基于逆向伪代码翻译）
3. 每个函数头部注释标注：`// 复刻自: <原始函数地址或模块名>，证据: 分析报告发现 #N`
4. 完善参数校验和异常捕获
5. 代码组织遵循用户现有项目的目录规范和编码风格

**5.4 资源处理**

- 配置文件、常量、枚举值：从逆向结果中提取，转为目标语言的配置格式
- UI 布局/样式：不得直接复制，按功能等价重新实现
- 图片/音频/字体等素材：不得直接复制，使用替代资源或重新制作
- 第三方依赖：识别原始软件使用的库，在用户技术栈中选择等价替代

工具：代码编写（Write/Edit），遵循用户项目技术栈规范

### STEP 6 → 对照验证

验证复刻代码的功能正确性。验证清单见 `references/verification-checklist.md`。

**6.1 单元测试**

- 为每个 P0/P1 模块编写单元测试
- 测试用例来自：逆向分析中观察到的输入输出、边界条件、异常路径
- 测试断言基于原始软件的行为，而非复刻代码的内部实现

**6.2 行为对照**

对核心功能执行输入输出对照：

| 测试项 | 原始软件输出 | 复刻版本输出 | 是否一致 |
|--------|------------|------------|---------|
| <用例1> | <值> | <值> | ✅/❌ |

不一致时：
1. 检查复刻代码的逻辑翻译是否有偏差
2. 回到 STEP 3 对相关函数做更深入的逆向分析
3. 修正复刻代码后重新测试
4. 记录修正原因和证据

**6.3 边界与异常测试**

- 空输入、null、极值、超长输入
- 非法格式、权限不足、网络异常
- 并发/竞态条件（如原始软件涉及）

**6.4 验收标准**

复刻完成的判定条件：
- P0 模块全部实现且单元测试通过
- 核心路径行为对照一致率 ≥ 95%
- 代码可编译/可运行，无未处理异常
- 每个模块有对应的逆向证据标注
- 明确列出未复刻的 P1/P2 模块及原因

工具：测试运行（按用户技术栈选择测试框架）

## 目标类型深度指引

### 原生二进制（最复杂）

1. 先跑字符串扫描和导入表，建立全局认知
2. 根据用户关注的功能，用字符串/导入函数定位相关代码区域
3. 对目标函数做反编译，阅读伪代码
4. 跟踪调用链，理解数据流向
5. 必要时用 Frida/LLDB 做运行时跟踪（REA v6+ 支持）

Windows 下 Ghidra 对 x86-64 PE 是实验性支持，可能出现分析不完整。

### JavaScript/Electron（最容易）

1. ASAR 文件需先解压：`npx asar extract app.asar ./extracted`
2. REA 直接分析目录，返回模块、导入、路由、IPC 关系
3. Electron 应用重点关注 preload 脚本和 IPC 通道

### Android APK

1. 需要 JDK 和 headless JADX
2. REA 返回 Manifest、类结构、反编译方法
3. 重点关注 AndroidManifest.xml 的权限和组件声明

### 固件

1. 仅 Linux 支持（Binwalk/Unblob）
2. 先提取文件系统，再对提取出的二进制做原生分析
3. Windows 用户需用 WSL 或 Linux 服务器

## 完成条件

- REA 命令实际执行并返回分析输出，报告中每个结论附带工具输出证据
- 模块拆解清单完成，P0 模块全部实现为可运行代码
- 核心路径行为对照测试通过（一致率 ≥ 95%）
- 复刻代码中每个函数标注了对应的逆向证据来源
- 明确标注了未复刻的 P1/P2 功能及原因
- 明确标注分析局限性和复刻的法律合规提醒

## 停止条件

出现以下情况时停止并向用户说明：
- 用户未提供目标路径且无法推断
- Node.js 版本不满足且用户不打算升级
- REA setup 交互需要用户操作（等待用户完成后继续）
- 目标类型需要的引擎未安装且用户不打算安装（如固件分析需要 Linux）
- 分析任务涉及破解/脱壳/绕过授权（拒绝并说明原因）
- REA 命令连续两次报错且换命令后仍失败（报告错误，建议升级 REA 或提 issue）
- 复刻涉及直接复制受版权保护的代码/资源（拒绝并说明独立重实现要求）
- 用户未确认复刻目标的法律授权（暂停并提醒合规风险）
- 行为对照测试连续3轮修正后仍有核心路径不一致（报告差异，建议人工复核逆向分析）
- 用户明确要求停止

## references 读取条件

- `references/target-matrix.md`：STEP 2 目标识别时读取，获取完整的目标类型→引擎→命令映射
- `references/rea-cli-reference.md`：STEP 3 执行分析前读取，确认当前版本的 CLI 命令和参数
- `references/report-template.md`：STEP 4 写分析报告时读取，使用标准模板
- `references/replication-guide.md`：STEP 5 复刻执行时读取，获取模块拆解、技术栈映射、逐模块实现的完整指南
- `references/module-breakdown-template.md`：STEP 5.1 模块拆解时读取，使用标准拆解模板
- `references/verification-checklist.md`：STEP 6 对照验证时读取，使用验证清单和测试规范

## scripts 运行条件

- `scripts/check-env.ps1`：STEP 1 必须运行，输出环境检测结果

## 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `rea: command not found` | 未全局安装 | 用 `npx -y rea-agents@latest <command>` 替代 |
| Ghidra 启动超时 | 大二进制或首次启动慢 | 设 `REA_GHIDRA_STARTUP_TIMEOUT_MS` 为 300000+ |
| MCP 工具不出现 | 代理未重启 | setup 后重启 AI 代理 |
| APK 分析失败 | 缺 JDK 或 JADX | 安装 JDK 17+，REA setup 会自动拉 JADX |
| 固件分析不可用 | Windows 不支持 Binwalk | 用 WSL2 或 Linux 服务器 |
| 结果不准确 | REA 版本旧 | `rea update` 或 `npx rea-agents@latest setup` 升级 |

## 版本信息

- REA npm 包：`rea-agents`（写作时最新 v6.3.0，2026-10-10）
- GitHub：github.com/morluto/rea
- 官网：rea.tools
- License：MIT
- Node 要求：>= 22.19（22.x）、>= 24.11（24.x）或 26+
