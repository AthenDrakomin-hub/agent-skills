# REA 目标类型矩阵

执行逆向分析前，根据目标特征路由到正确的分析路径。

## 完整目标矩阵

| 目标类型 | 识别特征 | 扩展名/标识 | 所需引擎 | 平台支持 | REA 返回内容 |
|---------|---------|------------|---------|---------|-------------|
| **原生二进制** | PE/Mach-O/ELF 头 | .exe .dll .so .dylib .elf .o | Ghidra（免费）/ IDA Pro / Hopper | macOS / Linux / Windows（x64 PE 实验性） | 伪代码、汇编、字符串、符号、调用关系、引用 |
| **ELF 离线布局** | ELF 格式 | .elf .so .o | pwntools（调用方提供） | Linux x64 | 节区、段、原始符号/重定位、静态缓解候选 |
| **EVM 字节码** | 以太坊智能合约 | .bin .hex 原始字节 | 无需额外引擎 | 全平台 | dispatch selectors、字节偏移、推断参数、可变性 |
| **Linux Crash 记录** | core dump / 崩溃日志 | core 文件、coredump | pwntools；可选 GDB/pwndbg | Linux | 原始笔记、线程寄存器/信号、映射候选 |
| **JavaScript/Electron** | package.json、ASAR、Electron 结构 | .asar、应用目录、.js | 无需额外引擎 | 全平台 | 模块、导入、source map、路由、IPC、原生插件关系 |
| **网站** | HTTP(S) URL | http:// https:// | Chrome 系浏览器 | 全平台 | 页面结构、脚本、网络观察、截图 |
| **网络抓包** | HAR / mitmproxy | .har .pcap | HAR 解析；mitmdump（Linux） | 全平台（mitm 仅 Linux） | 请求/响应、暴露的 payload、源码位置 |
| **.NET 程序集** | CLR 头、CIL | .exe .dll（含 .NET 元数据） | 无需额外引擎（静态） | 全平台 | 元数据、CIL 指令、原生依赖声明、构建对比 |
| **Android APK** | ZIP 包 + AndroidManifest.xml | .apk .aab | JADX（headless）+ JDK | Linux / macOS / Windows x64 | Manifest 声明、类、反编译方法、引用 |
| **固件** | 原始镜像 | .bin .img .fw | Binwalk / Unblob | Linux 仅 | 区域、提取结果、原生分析交接 |
| **包/资源** | Apple bundle、IPA、资源文件 | .ipa .app .plist .car | 无需额外引擎 | 全平台 | 文件清单、digest、plist、Apple bundle 解剖、提取资源 |
| **进程行为** | 可执行程序运行时 | 任意可执行文件 | PTY | Linux / macOS | 终端输出、交互、退出码、文件系统观察、运行对比 |

## 识别决策树

```
输入是 URL (http/https)？
├─ 是 → 网站分析（需 Chrome）
└─ 否 → 是本地文件/目录
    ├─ 扩展名 .har → 网络抓包分析
    ├─ 扩展名 .apk/.aab → Android APK 分析（需 JADX+JDK）
    ├─ 扩展名 .asar 或目录含 package.json →
    │   ├─ 含 Electron 依赖 → Electron 应用分析
    │   └─ 纯 JS → JavaScript 应用分析
    ├─ 扩展名 .bin/.img/.fw → 固件分析（需 Linux + Binwalk）
    ├─ 扩展名 .exe/.dll →
    │   ├─ 文件头含 CLR → .NET 程序集分析
    │   └─ PE 头 → 原生二进制（Windows，需 Ghidra/IDA/Hopper）
    ├─ 扩展名 .so/.elf/.o → 原生二进制（Linux ELF）
    ├─ 扩展名 .dylib → 原生二进制（macOS Mach-O）
    ├─ 扩展名 .ipa/.app → Apple 包/资源分析
    └─ 无法识别 → 用 file 命令或检查文件头魔数，再归类
```

## 引擎选择优先级

原生二进制分析时，按以下优先级选择 provider：

1. **IDA Pro** — 反编译质量最高，但商业付费
2. **Hopper** — macOS 原生，REA setup 可自动安装（需用户批准）
3. **Ghidra** — NSA 开源免费，跨平台，功能最全但速度较慢

Windows 用户推荐 Ghidra（免费且跨平台）。macOS 用户可让 REA setup 自动安装 Hopper。

## 平台限制速查

| 能力 | Windows | macOS | Linux |
|------|---------|-------|-------|
| JavaScript/Electron 静态分析 | ✅ | ✅ | ✅ |
| .NET 静态分析 | ✅ | ✅ | ✅ |
| 网站分析 | ✅（需 Chrome） | ✅ | ✅ |
| 原生二进制（Ghidra） | ⚠️ x64 PE 实验性 | ✅ | ✅ |
| 原生二进制（Hopper） | ❌ | ✅ | ❌ |
| 原生二进制（IDA） | ✅ | ✅ | ✅ |
| Android APK | ✅ x64 | ✅ | ✅ |
| 固件（Binwalk） | ❌ | ❌ | ✅ |
| ELF 离线布局（pwntools） | ❌ | ❌ | ✅ x64 |
| 进程行为捕获 | ❌ | ✅ | ✅ |
| Crash 记录分析 | ❌ | ❌ | ✅ |

Windows 用户做固件/ELF/进程分析需用 WSL2 或 Linux 服务器。
