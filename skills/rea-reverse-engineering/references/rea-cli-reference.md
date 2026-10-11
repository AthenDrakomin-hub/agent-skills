# REA CLI 命令速查

> REA 版本迭代快，命令可能变化。执行前先跑 `rea --help` 或 `npx -y rea-agents@latest --help` 确认当前版本支持的子命令。
> 本文基于 v6.3.0（2026-10-10）。

## 安装与配置

```powershell
# 一键 setup（检测已安装的 AI 代理并注册 REA MCP）
npx rea-agents@latest setup

# 全局安装 CLI（安装后可用 rea 命令）
npm install --global rea-agents

# 查看版本
rea --version

# 查看所有命令
rea --help

# 更新 REA
rea update
# 或 npx 方式：
npx rea-agents@latest setup
```

## 通用参数

| 参数 | 说明 |
|------|------|
| `--json` | 输出 JSON 格式（推荐，便于解析） |
| `--provider <name>` | 原生分析引擎：`ghidra` / `ida` / `hopper` |
| `--output <path>` | 结果输出到文件 |
| `--verbose` | 详细日志 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `REA_GHIDRA_STARTUP_TIMEOUT_MS` | Ghidra 启动超时（毫秒） | 按需调大，大文件设 300000 |
| `REA_PROVIDER` | 默认原生分析 provider | 自动检测 |

## 按目标类型的命令

### JavaScript / Electron 应用

```powershell
# 分析 JS/Electron 应用目录或 ASAR
npx -y rea-agents@latest analyze-javascript-application "D:\path\to\app" --json

# 分析 ASAR 文件（先解压再分析，或 REA 可能直接支持）
npx -y asar extract app.asar .\extracted
npx -y rea-agents@latest analyze-javascript-application ".\extracted" --json
```

返回：模块列表、导入关系、Electron 主/渲染进程边界、IPC 通道、source map 信息、原生插件引用。

### 原生二进制

```powershell
# 分析原生二进制（需先配置 provider）
rea analyze-native "C:\path\to\binary.exe" --provider ghidra --json

# 仅扫描字符串（快速，无需完整反编译）
rea analyze-native "C:\path\to\binary.exe" --provider ghidra --strings --json

# 查看导入表
rea analyze-native "C:\path\to\binary.exe" --provider ghidra --imports --json

# 反编译指定函数（需函数地址或名称）
rea analyze-native "C:\path\to\binary.exe" --provider ghidra --decompile "0x180124945" --json
```

> Windows 下 Ghidra 对 x86-64 PE 是实验性支持。如分析不完整，尝试 Hopper（macOS）或 IDA。

### .NET 程序集

```powershell
# 静态分析 .NET 程序集（无需额外引擎）
rea analyze-dotnet "C:\path\to\assembly.dll" --json
```

返回：程序集元数据、CIL 指令、类型/方法列表、P/Invoke 原生依赖声明。

### Android APK

```powershell
# 分析 APK（需 JDK + JADX，REA setup 会自动配置 JADX）
rea analyze-apk "C:\path\to\app.apk" --json

# 仅分析 Manifest
rea analyze-apk "C:\path\to\app.apk" --manifest --json
```

返回：AndroidManifest.xml（权限、组件、intent-filter）、类结构、反编译方法、资源引用。

### 网站

```powershell
# 分析网站（需 Chrome 浏览器，REA 通过 CDP 连接）
rea analyze-website "https://example.com" --json

# 包含网络请求捕获
rea analyze-website "https://example.com" --capture-network --json
```

返回：页面 DOM 结构、加载的脚本、网络请求、可选截图。

### 网络抓包（HAR）

```powershell
# 分析 HAR 文件
rea analyze-har "C:\path\to\capture.har" --json
```

返回：API 端点、请求/响应 payload、敏感信息暴露、前端源码引用。

### 固件（Linux 仅）

```bash
# 分析固件镜像（需 Binwalk/Unblob）
rea analyze-firmware /path/to/firmware.bin --json

# 仅提取文件系统
rea analyze-firmware /path/to/firmware.bin --extract --output ./extracted
```

返回：固件区域识别、提取的文件系统、可进一步分析的二进制文件列表。

### ELF 离线布局（Linux x64）

```bash
# 分析 ELF 结构（需 pwntools）
rea analyze-elf-layout /path/to/binary --json
```

返回：节区/段信息、符号表、重定位、安全缓解机制（NX/ASLR/RELRO/Stack Canary）。

### EVM 字节码

```powershell
# 分析以太坊智能合约字节码
rea analyze-evm "C:\path\to\contract.bin" --json
```

返回：函数选择器（dispatch）、字节偏移、推断的函数参数、状态可变性（view/pure/payable）。

### 包/资源

```powershell
# 分析 Apple 应用包
rea analyze-package "C:\path\to\app.ipa" --json

# 分析目录中的资源文件
rea analyze-package "C:\path\to\resources" --inventory --json
```

返回：文件清单、哈希 digest、plist 解析、Apple bundle 结构、资源提取。

## MCP 配置（手动）

如果 `npx rea-agents setup` 不支持你的代理，手动在 MCP 配置中添加：

```json
{
  "mcpServers": {
    "rea": {
      "command": "npx",
      "args": ["-y", "rea-agents@latest", "mcp"]
    }
  }
}
```

支持的代理：Claude Code、Cursor、Codex、Gemini CLI、Windsurf、GitHub Copilot CLI、Grok Build 等。

## 退出状态码

| 码 | 含义 |
|----|------|
| 0 | 成功 |
| 1 | 通用错误 |
| 2 | 目标文件不存在或不可读 |
| 3 | 所需引擎未安装 |
| 4 | 分析超时 |
| 5 | 不支持的目标类型 |

## 常用组合命令

```powershell
# 快速扫描一个未知二进制（字符串+导入+文件信息）
rea analyze-native "target.exe" --provider ghidra --strings --imports --info --json

# Electron 应用完整分析（ASAR 解压 + 模块分析 + IPC 映射）
npx asar extract app.asar .\extracted
rea analyze-javascript-application ".\extracted" --json --ipc --routes

# APK 权限审计
rea analyze-apk "app.apk" --manifest --json | ConvertFrom-Json | Select-Object permissions
```
